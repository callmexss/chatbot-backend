from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"documents", views.DocumentViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/user-documents/", views.UserDocumentsList.as_view(), name="user-documents"
    ),
]
