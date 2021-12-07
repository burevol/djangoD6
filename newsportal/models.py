from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Author(models.Model):
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')

    def update_rating(self):
        post_rating = Post.objects.filter(author=self).aggregate(models.Sum('rating'))['rating__sum'] * 3
        author_comment_rating = Comment.objects.filter(user=self.user).aggregate(models.Sum('rating'))['rating__sum']
        post_comment_rating = Comment.objects.filter(post__author=self).aggregate(models.Sum('rating'))['rating__sum']
        self.rating = post_rating + author_comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return f'{self.user.username}'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    subscribers = models.ManyToManyField(User)

    def __str__(self):
        return f'{self.name.title()}'


article = 'AR'
news = 'NW'

content_type = [
    (article, "Статья"),
    (news, 'Новость')
]


class Post(models.Model):
    header = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст статьи')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    type = models.CharField(max_length=2, choices=content_type, verbose_name='Тип')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, verbose_name='Автор')
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категории')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:123] + '...'

    def __str__(self):
        return f'{self.text}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Статья')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name='Статья')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.text}'
