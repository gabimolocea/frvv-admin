from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'city', CityViewSet, basename='city')
router.register('club', ClubViewSet, basename='club')
router.register('competition', CompetitionViewSet, basename='competition')
router.register('athlete', AthleteViewSet, basename='athlete')
router.register('title', TitleViewSet, basename='title')
router.register('federation-role', FederationRoleViewSet, basename='federation-role')
router.register('grade', GradeViewSet, basename='grade')
urlpatterns = router.urls
