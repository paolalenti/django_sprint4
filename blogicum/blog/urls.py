from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        'posts/<int:id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path('posts/<int:id>/comment/', views.post_detail, name='add_comment'),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path(
        'profile/<slug:username>/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
]
