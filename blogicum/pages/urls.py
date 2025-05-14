from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.PageView.as_view(), {'slug': 'about'}, name='about'),
    path('rules/', views.PageView.as_view(), {'slug': 'rules'}, name='rules'),
]
