from django.views.generic import DetailView
from django.shortcuts import render
from .models import Page


class PageView(DetailView):
    model = Page
    template_name_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_template_names(self):
        return [f'pages/{self.object.slug}.html']


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
