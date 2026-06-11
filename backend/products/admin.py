from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewImage
from django.contrib import admin
from .models import Brand

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'text', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved')
    search_fields = ('text', 'user__username', 'product__title')
    list_editable = ('is_approved',)

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'image_preview', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.file.url)
        return '-'
    image_preview.short_description = 'Фото'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'shop_url')
    search_fields = ('name',)