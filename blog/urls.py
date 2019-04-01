from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index),
    path('blog/', PostListView.as_view(), name='post-list'),
    path('blog/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('post-create/', post_create, name='post-create'),
    path('user/<username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/favourite-post/', favourite_post, name='favourite_post'),
    path('like/', like_post, name='like_post'),
    path('favourites/', favourite_post_list, name='favouite_post_list'),
    # path('popular_posts/', popular_posts, name = 'popular_posts'),
    path('post/<int:pk>/comment/', add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', comment_remove, name='comment_remove'),
]


