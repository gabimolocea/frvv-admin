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
router.register('team', TeamViewSet, basename='team')
router.register('match', MatchViewSet, basename='match')
router.register('annual-visa', AnnualVisaViewSet, basename='annual-visa')
router.register('category', CategoryViewSet, basename='category')
router.register('grade-history', GradeHistoryViewSet, basename='grade-history')
router.register('medical-visa', MedicalVisaViewSet, basename='medical-visa')
router.register('training-seminar', TrainingSeminarViewSet, basename='training-seminar')
router.register('group', GroupViewSet, basename='group')


urlpatterns = router.urls
