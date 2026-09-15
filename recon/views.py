from rest_framework import viewsets
from .models import Target
from .serializers import TargetSerializer


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all().order_by('-date_added')
    serializer_class = TargetSerializer
