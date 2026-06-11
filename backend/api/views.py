from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .badwords import CheckTextOnBadWords


@api_view(['POST'])
@permission_classes([AllowAny])
def check_bad_words(request):
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'Текст не передан'}, status=400)
    
    result = CheckTextOnBadWords(text)
    
    if result:
        return Response({'has_bad_words': True, 'message': result})
    return Response({'has_bad_words': False, 'message': ''})