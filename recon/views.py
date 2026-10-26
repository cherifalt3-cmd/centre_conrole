from django.db import IntegrityError, transaction
from rest_framework import serializers, viewsets
from .models import Target, Tool, CommandPreset
from .serializers import (
    DUPLICATE_TARGET_MESSAGE, TargetSerializer, ToolSerializer, CommandPresetSerializer,
)


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all().order_by('-date_added')
    serializer_class = TargetSerializer

    # validate_address ecarte les doublons, mais deux requetes simultanees (un
    # double-clic) passent toutes deux ce controle avant d'ecrire : seule la
    # contrainte en base tranche. On convertit son erreur en 400 lisible.
    def perform_create(self, serializer):
        self._save_or_reject_duplicate(serializer)

    def perform_update(self, serializer):
        self._save_or_reject_duplicate(serializer)

    def _save_or_reject_duplicate(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise serializers.ValidationError({'address': [DUPLICATE_TARGET_MESSAGE]})


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
