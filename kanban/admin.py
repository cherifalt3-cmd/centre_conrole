from django.contrib import admin
from .models import Board, Column, Card


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 1


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ColumnInline]


class CardInline(admin.TabularInline):
    model = Card
    extra = 1


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'order')
    list_filter = ('board',)
    inlines = [CardInline]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'order', 'created_at')
    list_filter = ('column__board', 'column')
