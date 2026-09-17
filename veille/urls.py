from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SourceViewSet, ArticleViewSet, RefreshFeedsView

router = DefaultRouter()
router.register('sources', SourceViewSet)
router.register('articles', ArticleViewSet)

urlpatterns = router.urls + [
    path('refresh/', RefreshFeedsView.as_view()),
]
