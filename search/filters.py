from django_filters import FilterSet, ModelChoiceFilter

from newsportal.models import Post, Author


class PostFilter(FilterSet):
    author = ModelChoiceFilter(queryset=Author.objects.all())

    class Meta:
        model = Post
        fields = {
            'date': ['gt'],
            'header': ['icontains'],
        }
