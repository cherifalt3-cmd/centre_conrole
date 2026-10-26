from rest_framework import viewsets
from .models import Target, Tool, CommandPreset
from .serializers import TargetSerializer, ToolSerializer, CommandPresetSerializer


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all().order_by('-date_added')
    serializer_class = TargetSerializer


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    # Le serialiseur descend outil -> options -> choix et options -> catalogue ->
    # entrees : sans prechargement, une requete par niveau et par objet.
    queryset = Tool.objects.prefetch_related(
        'options__choices',
        'options__catalog__entries',
    )
    serializer_class = ToolSerializer


class CommandPresetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommandPreset.objects.all()
    serializer_class = CommandPresetSerializer
