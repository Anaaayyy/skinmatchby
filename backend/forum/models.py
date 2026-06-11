from django.db import models
from django.contrib.auth.models import User
from wagtail.images.models import Image as WagtailImage


class ForumCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=10, blank=True, verbose_name='Иконка')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = "Категория форума"
        verbose_name_plural = "Категории форума"
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def topics_count(self):
        return self.topics.filter(is_visible=True).count()

    @property
    def posts_count(self):
        return ForumPost.objects.filter(
            topic__category=self, topic__is_visible=True, is_visible=True
        ).count()

    @property
    def last_post(self):
        return ForumPost.objects.filter(
            topic__category=self, topic__is_visible=True, is_visible=True
        ).order_by('-created_at').first()


class ForumTopic(models.Model):
    category = models.ForeignKey(
        ForumCategory, on_delete=models.CASCADE, related_name='topics', verbose_name='Категория'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='forum_topics', verbose_name='Автор'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    is_pinned = models.BooleanField(default=False, verbose_name='Закреплено')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')
    is_visible = models.BooleanField(default=True, verbose_name='Видимо')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = "Тема форума"
        verbose_name_plural = "Темы форума"

    def __str__(self):
        return self.title

    @property
    def posts_count(self):
        return self.posts.filter(is_visible=True).count()

    @property
    def last_post(self):
        return self.posts.filter(is_visible=True).order_by('-created_at').first()


class TopicImage(models.Model):
    topic = models.ForeignKey(
        ForumTopic, on_delete=models.CASCADE, related_name='images', verbose_name='Тема'
    )
    image = models.ForeignKey(
        WagtailImage, on_delete=models.CASCADE, related_name='topic_images', verbose_name='Изображение'
    )
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = "Изображение темы"
        verbose_name_plural = "Изображения темы"
        ordering = ['order']


class ForumPost(models.Model):
    topic = models.ForeignKey(
        ForumTopic, on_delete=models.CASCADE, related_name='posts', verbose_name='Тема'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='forum_posts', verbose_name='Автор'
    )
    content = models.TextField(verbose_name='Содержание')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies', verbose_name='Ответ на'
    )
    is_visible = models.BooleanField(default=True, verbose_name='Видимо')
    likes_count = models.IntegerField(default=0, verbose_name='Лайки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = "Сообщение форума"
        verbose_name_plural = "Сообщения форума"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class PostImage(models.Model):
    post = models.ForeignKey(
        ForumPost, on_delete=models.CASCADE, related_name='images', verbose_name='Сообщение'
    )
    image = models.ForeignKey(
        WagtailImage, on_delete=models.CASCADE, related_name='post_images', verbose_name='Изображение'
    )
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = "Изображение сообщения"
        verbose_name_plural = "Изображения сообщений"
        ordering = ['order']


class PostLike(models.Model):
    post = models.ForeignKey(
        ForumPost, on_delete=models.CASCADE, related_name='likes', verbose_name='Сообщение'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='forum_likes', verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        unique_together = ['post', 'user']
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"{self.user.username} лайкнул #{self.post.id}"