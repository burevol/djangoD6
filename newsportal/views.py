from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.views.generic import ListView, UpdateView, CreateView, DetailView, \
    DeleteView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .forms import NewsForm
from .models import Post, Category

# Create your views here.
class PostCategoryView(ListView):
    model = Post
    template_name = 'posts_category.html'
    context_object_name = 'posts'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        id = self.kwargs.get('pk')
        return Post.objects.filter(postcategory__category_id=id)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(pk=id).name
        context['category_id'] = id
        context['is_subscribed'] = Category.objects.get(pk=id).subscribers.exists()
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-date')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('newsportal.add_post')
    template_name = 'post_create.html'
    form_class = NewsForm


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('newsportal.change_post')
    template_name = 'post_create.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


class PostSearchView(ListView):
    model = Post
    template_name = 'posts_search.html'

@login_required()
def upgrade_me(request):
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(request.user)
    return redirect('/news/')


@login_required()
def subscribe(request, pk):
    if not Category.objects.get(pk=pk).subscribers.filter(id=request.user.id).exists():
        cat = Category.objects.get(pk=pk).subscribers.add(request.user)
    return redirect('/news/')

def article_added(sender, instance, action, **kwargs):
    if action == 'post_add':
        mail_dict = {}
        categories = instance.category.all()
        for category in categories:
            for user in category.subscribers.all():
                mail_dict[user.username] = user.email

        for username, email in mail_dict.items():
            html_content = render_to_string('mail.html', {'header': instance.header, 'username': username, 'text':instance.text, 'id': instance.id})
            msg = EmailMultiAlternatives(
                subject=instance.header,
                from_email='appointment@silicon-chronicles.ru',
                body=instance.text,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


m2m_changed.connect(article_added, sender=Post.category.through)