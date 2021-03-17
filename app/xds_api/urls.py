from django.urls import path
from rest_framework.routers import DefaultRouter
from xds_api import views

router = DefaultRouter()

urlpatterns = [
    path('configuration/', views.XDSConfigurationView.as_view()),
]