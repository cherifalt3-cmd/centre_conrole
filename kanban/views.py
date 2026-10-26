from rest_framework import viewsets
from .models import Board, Column, Card
from .serializers import BoardSerializer, ColumnSerializer, CardSerializer


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    # Tableau -> colonnes -> cartes : le cout croit avec le nombre de colonnes
    queryset = Board.objects.prefetch_related('columns__cards')
    serializer_class = BoardSerializer


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.prefetch_related('cards')
    serializer_class = ColumnSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
