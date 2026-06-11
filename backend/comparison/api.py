from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from products.models import Product
from .models import Comparison

class ComparisonSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Comparison
        fields = ['id', 'name', 'products', 'created_at']

class ComparisonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComparisonSerializer
    
    def get_queryset(self):
        return Comparison.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        comparison = self.get_object()
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)
        comparison.products.add(product)
        return Response({'status': 'added'})
    
    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        comparison = self.get_object()
        product_id = request.data.get('product_id')
        comparison.products.remove(product_id)
        return Response({'status': 'removed'})