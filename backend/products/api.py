from rest_framework import serializers, viewsets, filters, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Q, Sum, Case, When, Value, IntegerField
from .models import Product, Brand, Category, ProductImage, Review, ReviewImage
import base64
import uuid
from django.core.files.base import ContentFile
from wagtail.images.models import Image

class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'caption']
    
    def get_url(self, obj):
        if obj.image:
            return obj.image.file.url
        return None

class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    gallery = ProductImageSerializer(source='product_images', many=True, read_only=True)
    brand_website = serializers.URLField(source='brand.website', read_only=True)
    brand_shop_url = serializers.URLField(source='brand.shop_url', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'brand', 'brand_name', 'category', 'category_name',
            'description', 'volume', 'ingredients', 'how_to_use', 
            'main_image_url', 'gallery', 'rating',
            'suitable_skin_types', 'solves_problems', 'has_allergens','brand_website', 'brand_shop_url'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            return obj.main_image.file.url
        return None

class BrandSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'website', 'shop_url']
    
    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.file.url
        return None
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ReviewImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewImage
        fields = ['id', 'url']
    
    def get_url(self, obj):
        if obj.image:
            return obj.image.file.url
        return None

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(write_only=True, required=False)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'username', 'user_id', 'rating', 'text', 
                  'created_at', 'updated_at', 'images', 'uploaded_images', 'avatar_url']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = Review.objects.create(**validated_data)
        
        for image_id in uploaded_images:
            try:
                image = Image.objects.get(id=image_id)
                ReviewImage.objects.create(review=review, image=image)
            except Image.DoesNotExist:
                pass
        
        product = review.product
        avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            product.rating = round(avg_rating, 2)
            product.save()
        
        return review
    
    def get_avatar_url(self, obj):  # ← добавить метод
        try:
            profile = obj.user.profile
            if profile.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(profile.avatar.url)
                return profile.avatar.url
        except:
            pass
        return None


def get_recommended_products(profile, limit=50):
    products = Product.objects.live().all()
    
    if not profile:
        return products[:limit]
    
    skin_type = profile.get('skin_type')
    problems = profile.get('problems', [])
    allergies = profile.get('allergies', [])
    
    if allergies:
        for allergy in allergies:
            if allergy == 'alcohol':
                products = products.exclude(has_allergens__icontains='alcohol')
            elif allergy == 'fragrance':
                products = products.exclude(has_allergens__icontains='fragrance')
            elif allergy == 'essential_oils':
                products = products.exclude(has_allergens__icontains='essential_oils')
            elif allergy == 'parabens':
                products = products.exclude(has_allergens__icontains='parabens')
    
    if skin_type:
        skin_type_map = {
            'dry': 'dry', 'oily': 'oily', 'combination': 'combination',
            'normal': 'normal', 'sensitive': 'sensitive',
            'Сухая': 'dry', 'Жирная': 'oily', 'Комбинированная': 'combination',
            'Нормальная': 'normal', 'Чувствительная': 'sensitive',
        }
        skin_code = skin_type_map.get(skin_type, skin_type)
        products = products.filter(
            Q(suitable_skin_types__icontains=skin_code) | Q(suitable_skin_types='')
        )
    
    if problems:
        relevance_cases = []
        for i, problem in enumerate(problems):
            problem_weight = 10 - i
            relevance_cases.append(
                When(solves_problems__icontains=problem, then=Value(problem_weight))
            )
        
        from django.db.models import Sum
        products = products.annotate(
            relevance_score=Sum(
                Case(*relevance_cases, default=Value(0), output_field=IntegerField())
            )
        )
        products = products.order_by('-relevance_score', '-rating')
    else:
        products = products.order_by('-rating')
    
    return products[:limit]

def calculate_match_percentage(product, profile):
    if not profile:
        return 0
    
    skin_type = profile.get('skin_type')
    problems = profile.get('problems', [])
    allergies = profile.get('allergies', [])
    
    total_criteria = 0
    matched_criteria = 0
    
    skin_type_map = {
        'dry': 'dry', 'oily': 'oily', 'combination': 'combination',
        'normal': 'normal', 'sensitive': 'sensitive',
        'Сухая': 'dry', 'Жирная': 'oily', 'Комбинированная': 'combination',
        'Нормальная': 'normal', 'Чувствительная': 'sensitive',
    }
    
    if skin_type and product.suitable_skin_types:
        skin_code = skin_type_map.get(skin_type, skin_type)
        total_criteria += 1
        if skin_code in product.suitable_skin_types.lower():
            matched_criteria += 1
    
    if problems and product.solves_problems:
        for problem in problems:
            total_criteria += 1
            if problem in product.solves_problems.lower():
                matched_criteria += 1
    
    if allergies and product.has_allergens:
        has_forbidden = False
        for allergy in allergies:
            if allergy in product.has_allergens.lower():
                has_forbidden = True
                break
        total_criteria += 1
        if not has_forbidden:
            matched_criteria += 1
    
    if total_criteria == 0:
        return 0
    
    return int((matched_criteria / total_criteria) * 100)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.live().all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'category']
    search_fields = ['title', 'brand__name', 'ingredients']
    ordering_fields = ['rating', 'first_published_at']
    ordering = ['-first_published_at']
    
    @action(detail=False, methods=['post'], url_path='recommend')
    def recommend(self, request):
        profile = request.data.get('profile', {})
        
        if not profile:
            products = Product.objects.live().all().order_by('-rating')[:20]
            serializer = self.get_serializer(products, many=True)
            return Response({
                'results': serializer.data,
                'total': len(products)
            })
        
        recommended_products = get_recommended_products(profile)
        
        data = []
        for product in recommended_products:
            product_data = ProductSerializer(product).data
            product_data['match_percentage'] = calculate_match_percentage(product, profile)
            data.append(product_data)
        
        data.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return Response({
            'results': data,
            'total': len(data),
            'profile_used': profile
        })

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'rating']
    
    def get_queryset(self):
        return Review.objects.filter(is_approved=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        image_data = request.data.get('image')
        if not image_data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f"review_image_{request.user.id}_{uuid.uuid4().hex}.{ext}")
        
        wagtail_image = Image.objects.create(
            title=f"Review by {request.user.username}",
            file=image_file
        )
        
        return Response({'image_id': wagtail_image.id, 'url': wagtail_image.file.url}, 
                        status=status.HTTP_201_CREATED)