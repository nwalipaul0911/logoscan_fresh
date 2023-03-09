from django.urls import path
from backend.views import index, LogoUploadView,ImageAPIView

urlpatterns = [
    path('', index),
    path('upload-logo/', LogoUploadView.as_view(), name='logo-upload'),
    path('api/image/<str:id>', ImageAPIView.as_view(), name='image_api'),
]