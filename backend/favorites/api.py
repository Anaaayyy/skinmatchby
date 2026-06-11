from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from products.models import Product
from .models import Favorite
from django.core.exceptions import ObjectDoesNotExist

class FavoriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']

class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def create(self, request):
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response(
                {'error': f'Product with id {product_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return Response({'status': 'added'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already exists'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        product_id = request.query_params.get('product_id')
        Favorite.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({'status': 'removed'})
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        local_favorites = request.data.get('favorites', [])
        user = request.user
        
        current_favorites = set(Favorite.objects.filter(user=user).values_list('product_id', flat=True))
        local_set = set(local_favorites)
        
        to_add = local_set - current_favorites
        for product_id in to_add:
            try:
                product = Product.objects.get(id=product_id)
                Favorite.objects.get_or_create(user=user, product=product)
            except ObjectDoesNotExist:
                pass
        
        to_remove = current_favorites - local_set
        Favorite.objects.filter(user=user, product_id__in=to_remove).delete()
        
        return Response({'status': 'synced', 'synced': True})