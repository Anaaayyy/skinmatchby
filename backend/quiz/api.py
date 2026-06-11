from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import UserProfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_quiz_results(request):
    """Сохраняет результаты анкеты в профиль пользователя"""
    user_profile = request.user.profile
    data = request.data

    # Обновляем поля профиля
    skin_type = data.get('skin_type')
    if skin_type:
        user_profile.skin_type = skin_type

    problems = data.get('problems')
    if problems and isinstance(problems, list):
        user_profile.problems = ', '.join(problems)

    age_range = data.get('age_range')
    if age_range:
        user_profile.age_range = age_range

    allergies = data.get('allergies')
    if allergies and isinstance(allergies, list):
        user_profile.allergies = ', '.join(allergies)

    user_profile.save()

    return Response({'status': 'success', 'message': 'Результаты анкеты сохранены'}, 
                    status=status.HTTP_200_OK)