from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from products.models import Product
from products.api import ProductSerializer
from .models import Routine

class RoutineSerializer(serializers.ModelSerializer):
    cleansing_data = ProductSerializer(source='cleansing', read_only=True)
    toner_data = ProductSerializer(source='toner', read_only=True)
    serum_data = ProductSerializer(source='serum', read_only=True)
    cream_data = ProductSerializer(source='cream', read_only=True)
    spf_data = ProductSerializer(source='spf', read_only=True)
    
    class Meta:
        model = Routine
        fields = ['id', 'name', 'goal', 'time_of_day', 
                  'cleansing', 'cleansing_data',
                  'toner', 'toner_data',
                  'serum', 'serum_data',
                  'cream', 'cream_data',
                  'spf', 'spf_data',
                  'created_at']

class RoutineViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoutineSerializer
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)