from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import CategoryViewSet, TopicViewSet, PostViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='forum-categories')
router.register(r'topics', TopicViewSet, basename='forum-topics')
router.register(r'posts', PostViewSet, basename='forum-posts')

urlpatterns = [
    path('', include(router.urls)),
]