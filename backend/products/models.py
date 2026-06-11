from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet

@register_snippet
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    logo = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Логотип')
    description = models.TextField(blank=True, verbose_name='Описание')
    website = models.URLField(blank=True, verbose_name='Сайт бренда')
    shop_url = models.URLField(blank=True, verbose_name='Ссылка на магазин')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'



@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(Page):
    # ========== ОСНОВНАЯ ИНФОРМАЦИЯ ==========
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products', 
        verbose_name='Бренд'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products', 
        verbose_name='Категория'
    )
    
    # ========== ОПИСАНИЕ ==========
    description = models.TextField(
        blank=True, 
        verbose_name='Описание товара'
    )
    
    # ========== ХАРАКТЕРИСТИКИ ==========
    volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Объем (мл)'
    )
    ingredients = models.TextField(
        blank=True, 
        verbose_name='Состав INCI'
    )
    how_to_use = models.TextField(
        blank=True, 
        verbose_name='Способ применения'
    )
    
    # ========== ПАРАМЕТРЫ ПОДБОРА ==========
    suitable_skin_types = models.CharField(
    max_length=200, 
    blank=True,
    help_text='Типы кожи, для которых подходит (через запятую: dry, oily, combination, normal, sensitive)',
    verbose_name='Подходит для типов кожи'
)
    
    solves_problems = models.CharField(
        max_length=500,
        blank=True,
        help_text='Какие проблемы решает (через запятую: acne, pigmentation, wrinkles, dehydration, redness)',
        verbose_name='Решаемые проблемы'
    )
    
    has_allergens = models.CharField(
        max_length=500,
        blank=True,
        help_text='Содержит аллергены (через запятую: alcohol, fragrance, essential_oils, parabens)',
        verbose_name='Аллергены'
    )
    
    # ========== ИЗОБРАЖЕНИЯ И РЕЙТИНГ ==========
    main_image = models.ForeignKey(
        'wagtailimages.Image', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name='Главное изображение'
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0, 
        verbose_name='Рейтинг'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('ingredients'),
        index.FilterField('brand'),
        index.FilterField('category'),
    ]
    
    content_panels = Page.content_panels + [
        # ГРУППА 1: Основная информация
        MultiFieldPanel([
            FieldPanel('brand'),
            FieldPanel('category'),
        ], heading='Основная информация'),
        
        # ГРУППА 2: Описание
        FieldPanel('description'),
        
        # ГРУППА 3: Характеристики
        MultiFieldPanel([
            FieldPanel('volume'),
            FieldPanel('ingredients'),
            FieldPanel('how_to_use'),
        ], heading='Характеристики'),
        
        # ГРУППА 4: Параметры подбора
        MultiFieldPanel([
            FieldPanel('suitable_skin_types', 
                       help_text='Укажите типы кожи, для которых подходит продукт. Например: dry, oily, sensitive'),
            FieldPanel('solves_problems',
                       help_text='Укажите проблемы, которые решает продукт. Например: acne, dehydration, wrinkles'),
            FieldPanel('has_allergens',
                       help_text='Укажите аллергены в составе. Например: alcohol, fragrance, parabens'),
        ], heading='Параметры подбора'),
        
        # ГРУППА 5: Изображения
        MultiFieldPanel([
            FieldPanel('main_image'),
            InlinePanel('product_images', label='Дополнительные изображения'),
        ], heading='Изображения'),
        
        # ГРУППА 6: Рейтинг
        MultiFieldPanel([
            FieldPanel('rating'),
        ], heading='Рейтинг'),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class ProductImage(models.Model):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(max_length=250, blank=True)
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Оценка')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True, verbose_name='Одобрен')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.rating}⭐"
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for review {self.review.id}"
    
    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'