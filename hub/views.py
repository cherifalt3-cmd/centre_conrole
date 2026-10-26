from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Etat reel de l'API pour l'indicateur de la barre superieure.

    La base est interrogee : un serveur qui repond mais dont la base est
    inaccessible n'est pas « en ligne » du point de vue de l'utilisateur.
    """
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return Response({'status': 'ok'})
