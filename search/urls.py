from django.urls import path
from .views import PostListSearch

urlpatterns = [
    path('', PostListSearch.as_view()),
]