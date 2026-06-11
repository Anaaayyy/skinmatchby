from django.db.models import Q, Case, When, Value, IntegerField
from .models import Product

def get_recommended_products(profile, limit=50):
    products = Product.objects.live().all()
    
    if not profile:
        return products[:limit]
    
    skin_type = profile.get('skin_type')
    problems = profile.get('problems', [])
    allergies = profile.get('allergies', [])
    
    # Исключение аллергенов
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
    
    # Фильтрация по типу кожи
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
    
    # Расчет релевантности
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