from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView


from .forms import PostForm, UserEditForm, CommentForm
from .models import Category, Post, User, Comment


def index(request):
    template = 'blog/index.html'
    post_list = (Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True)
        .select_related('category', 'location', 'author')
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    base_conditions = Q(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )

    # Если пользователь аутентифицирован, добавляем условие проверки авторства
    if request.user.is_authenticated:
        conditions = base_conditions | Q(author=request.user)
    else:
        conditions = base_conditions

    # Получаем пост с учетом условий
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        conditions,
        id=id
    )

    comments = post.comments.select_related('author')
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and request.user.is_authenticated:
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=post.id)

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    post_list = (category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('location', 'author')
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments')))

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        post_list = profile_user.posts.all()
    else:
        post_list = profile_user.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', id=self.kwargs['id'])


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('blog:profile')

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment  # Добавьте явное указание модели
    form_class = CommentForm  # Укажите форму
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['post_id']}
        )

    def get_queryset(self):
        return super().get_queryset().filter(post_id=self.kwargs['post_id'])


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'  # Правильный параметр из URL
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_queryset(self):
        return super().get_queryset().filter(post_id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Явно удаляем форму из контекста для удаления
        context['form'] = None
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['post_id']}
        )
