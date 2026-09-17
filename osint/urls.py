from rest_framework.routers import DefaultRouter
from .views import SearchViewSet

router = DefaultRouter()
router.register('searches', SearchViewSet)

urlpatterns = router.urls
