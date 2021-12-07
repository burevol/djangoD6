from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import PostList, PostDetail, PostCreateView, PostUpdateView, PostDeleteView, PostCategoryView, upgrade_me, \
    subscribe

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('add/', PostCreateView.as_view(), name='post_create'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('category/<int:pk>', PostCategoryView.as_view(), name='post_category'),
    path('category/<int:pk>/subscribe', subscribe, name='subscribe'),
]
