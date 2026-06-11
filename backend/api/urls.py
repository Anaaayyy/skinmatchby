from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from products.api import ProductViewSet, BrandViewSet, CategoryViewSet, ReviewViewSet
from users.api import ProfileViewSet
from users.register_api import register
from quiz.api import save_quiz_results
from favorites.api import FavoriteViewSet
from comparison.api import ComparisonViewSet
from routines.api import RoutineViewSet
from .views import check_bad_words

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'comparisons', ComparisonViewSet, basename='comparison')
router.register(r'routines', RoutineViewSet, basename='routine')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register, name='register'),
    path('save-quiz/', save_quiz_results, name='save-quiz'),
    path('check-text/', check_bad_words, name='check-bad-words'),
]