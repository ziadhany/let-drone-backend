"""
URL configuration for let_drone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.template.context_processors import static
from django.urls import path
from django.urls import include
from rest_framework import routers

from management import views as management_views, views
from management.views import OCRAPIView

router = routers.DefaultRouter()
router.register("users", management_views.UserViewSet)
router.register("pharmacist", management_views.PharmacistViewSet)
router.register("patients", management_views.PatientViewSet)

router.register("drones", management_views.DroneViewSet)
router.register("gcs", management_views.GCSViewSet)
router.register("comments", management_views.CommentViewSet)

router.register("patients_prescriptions", management_views.PrescriptionPatientViewSet,
                basename="patients_prescriptions")

router.register("pharmacist_prescriptions", management_views.PrescriptionPharmacistViewSet,
                basename="pharmacist_prescriptions")

router.register("delivery", management_views.DeliveryViewSet)
router.register("geolocation", management_views.GeolocationViewSet)

urlpatterns = [
      path("admin/", admin.site.urls),
      path("api/v0/", include(router.urls)),
      path('api/v0/ocr/', OCRAPIView.as_view(), name='ocr'),
      path('register/', views.register),
      path('token/', views.token),
      path('token/refresh/', views.refresh_token),
      path('token/revoke/', views.revoke_token),
      path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
      path("api/v0/", include("rest_framework.urls", namespace="rest_framework")),
]
