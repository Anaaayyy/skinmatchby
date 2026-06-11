from django.contrib import admin
from .models import ForumTopic, ForumPost, PostLike

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_pinned', 'is_closed', 'is_visible', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_closed', 'is_visible']
    search_fields = ['title', 'content']

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'author', 'short_content', 'likes_count', 'is_visible', 'created_at']
    list_filter = ['is_visible']
    search_fields = ['content', 'author__username']
    def short_content(self, obj):
        return obj.content[:80]
    short_content.short_description = 'Текст'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']