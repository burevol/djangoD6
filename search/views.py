from django.views.generic import ListView

from newsportal.models import Post
from .filters import PostFilter


# Create your views here.
class PostListSearch(ListView):
    model = Post
    template_name = 'posts_search.html'
    context_object_name = 'posts'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context
