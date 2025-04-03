from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('toggle-like/<int:comment_id>/', views.toggle_like_comment, name='toggle_like_comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('get_liked_comments/', views.get_liked_comments, name='get_liked_comments'),
    path('toggle_article_like/<int:article_id>/', views.toggle_article_like, name='toggle_article_like'),
    path('get_article_like_status/<int:article_id>/', views.get_article_like_status, name='get_article_like_status'),
]
