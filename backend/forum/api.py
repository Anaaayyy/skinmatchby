from rest_framework import serializers, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.utils import timezone
from .models import ForumCategory, ForumTopic, TopicImage, ForumPost, PostImage, PostLike
from users.models import UserProfile


class ForumPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class TopicPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30


class AuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_url']
    
    def get_avatar_url(self, obj):
        try:
            profile = obj.profile
            if profile.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(profile.avatar.url)
                return profile.avatar.url
        except Exception:
            pass
        return None


class TopicImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = TopicImage
        fields = ['id', 'url', 'order']
    
    def get_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.file.url)
            return obj.image.file.url
        return None


class PostImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields = ['id', 'url', 'order']
    
    def get_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.file.url)
            return obj.image.file.url
        return None


class ForumCategorySerializer(serializers.ModelSerializer):
    topics_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    last_post = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 
                  'topics_count', 'posts_count', 'last_post']
    
    def get_last_post(self, obj):
        last = obj.last_post
        if last:
            return {
                'id': last.id,
                'author': last.author.username,
                'created_at': last.created_at.isoformat(),
                'topic_id': last.topic_id,
                'topic_title': last.topic.title,
            }
        return None


class ForumPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=ForumPost.objects.all(), write_only=True, required=False)
    
    class Meta:
        model = ForumPost
        fields = ['id', 'topic', 'author', 'content', 'images', 'is_liked', 'parent', 'parent_id', 
                  'likes_count', 'is_visible', 'created_at', 'updated_at']
        read_only_fields = ['author', 'likes_count', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False


class ForumTopicListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    posts_count = serializers.IntegerField(source='_posts_count', read_only=True, default=0)
    last_post = serializers.SerializerMethodField()
    images = TopicImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ForumTopic
        fields = ['id', 'category', 'author', 'title', 'content', 'images', 'is_pinned', 'is_closed',
                  'posts_count', 'last_post', 'created_at', 'updated_at']
    
    def get_last_post(self, obj):
        last = obj.last_post
        if last:
            return ForumPostSerializer(last, context=self.context).data
        return None


class ForumTopicDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    posts = serializers.SerializerMethodField()
    images = TopicImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ForumTopic
        fields = ['id', 'category', 'author', 'title', 'content', 'images', 'is_pinned',
                  'is_closed', 'posts', 'created_at', 'updated_at']
    
    def get_posts(self, obj):
        posts = obj.posts.filter(is_visible=True).order_by('created_at')
        return ForumPostSerializer(posts, many=True, context=self.context).data


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer


class TopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = TopicPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-is_pinned', '-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ForumTopicListSerializer
        return ForumTopicDetailSerializer
    
    def get_queryset(self):
        if self.action == 'list':
            return ForumTopic.objects.filter(is_visible=True).annotate(
                _posts_count=Count('posts', filter=Q(posts__is_visible=True))
            ).prefetch_related('images')
        return ForumTopic.objects.filter(is_visible=True).prefetch_related('images')
    
    def perform_create(self, serializer):
        image_ids = self.request.data.get('images', [])
        topic = serializer.save(author=self.request.user)
        for i, image_id in enumerate(image_ids):
            from wagtail.images.models import Image
            try:
                img = Image.objects.get(id=image_id)
                TopicImage.objects.create(topic=topic, image=img, order=i)
            except Image.DoesNotExist:
                pass


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return ForumPost.objects.filter(is_visible=True, topic__is_visible=True).prefetch_related('images')
    
    def perform_create(self, serializer):
        topic_id = self.request.data.get('topic')
        topic = ForumTopic.objects.get(id=topic_id)
        image_ids = self.request.data.get('images', [])
        post = serializer.save(author=self.request.user, topic=topic)
        for i, image_id in enumerate(image_ids):
            from wagtail.images.models import Image
            try:
                img = Image.objects.get(id=image_id)
                PostImage.objects.create(post=post, image=img, order=i)
            except Image.DoesNotExist:
                pass
        topic.updated_at = timezone.now()
        topic.save(update_fields=['updated_at'])
    
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({'detail': 'Вы не можете удалить чужое сообщение'}, status=status.HTTP_403_FORBIDDEN)
        self._delete_replies(post)
        post.is_visible = False
        post.save(update_fields=['is_visible'])
        return Response({'status': 'Сообщение удалено'}, status=status.HTTP_200_OK)
    
    def _delete_replies(self, post):
        replies = ForumPost.objects.filter(parent=post, is_visible=True)
        for reply in replies:
            self._delete_replies(reply)
            reply.is_visible = False
            reply.save(update_fields=['is_visible'])
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save(update_fields=['likes_count'])
            return Response({'status': 'unliked', 'likes_count': post.likes_count})
        post.likes_count += 1
        post.save(update_fields=['likes_count'])
        return Response({'status': 'liked', 'likes_count': post.likes_count})
    
    @action(detail=False, methods=['post'], url_path='upload-image')
    def upload_image(self, request):
        from django.core.files.base import ContentFile
        import base64, uuid
        from wagtail.images.models import Image as WagtailImage
        image_data = request.data.get('image')
        if not image_data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f"forum_{request.user.id}_{uuid.uuid4().hex}.{ext}")
        wagtail_image = WagtailImage.objects.create(
            title=f"Forum upload by {request.user.username}", file=image_file
        )
        return Response({'image_id': wagtail_image.id, 'url': wagtail_image.file.url}, status=status.HTTP_201_CREATED)