from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import *
from .models import *
from rest_framework.response import Response
# Create your views here.

class CityViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def list(self, request):
        queryset = City.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class CompetitionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # Combine all competitions into a single response
        national_competitions = NationalCompetition.objects.all()
        european_competitions = EuropeanCompetition.objects.all()
        other_competitions = OtherCompetition.objects.all()

        # Serialize each type of competition
        national_serializer = CompetitionSerializer(national_competitions, many=True)
        european_serializer = CompetitionSerializer(european_competitions, many=True)
        other_serializer = CompetitionSerializer(other_competitions, many=True)

        # Combine serialized data
        combined_data = {
            "national_competitions": national_serializer.data,
            "european_competitions": european_serializer.data,
            "other_competitions": other_serializer.data,
        }

        return Response(combined_data)

    def create(self, request):
        # Determine the type of competition from the request data
        competition_type = request.data.get("type")
        serializer = None

        if competition_type == "national":
            serializer = CompetitionSerializer(data=request.data, model=NationalCompetition)
        elif competition_type == "european":
            serializer = CompetitionSerializer(data=request.data, model=EuropeanCompetition)
        elif competition_type == "other":
            serializer = CompetitionSerializer(data=request.data, model=OtherCompetition)

        if serializer and serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        # Retrieve competition by ID from all types
        try:
            instance = NationalCompetition.objects.get(pk=pk)
        except NationalCompetition.DoesNotExist:
            try:
                instance = EuropeanCompetition.objects.get(pk=pk)
            except EuropeanCompetition.DoesNotExist:
                try:
                    instance = OtherCompetition.objects.get(pk=pk)
                except OtherCompetition.DoesNotExist:
                    return Response({"error": "Competition not found"}, status=404)

        serializer = CompetitionSerializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Update competition by ID from all types
        try:
            instance = NationalCompetition.objects.get(pk=pk)
        except NationalCompetition.DoesNotExist:
            try:
                instance = EuropeanCompetition.objects.get(pk=pk)
            except EuropeanCompetition.DoesNotExist:
                try:
                    instance = OtherCompetition.objects.get(pk=pk)
                except OtherCompetition.DoesNotExist:
                    return Response({"error": "Competition not found"}, status=404)

        serializer = CompetitionSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        # Delete competition by ID from all types
        try:
            instance = NationalCompetition.objects.get(pk=pk)
        except NationalCompetition.DoesNotExist:
            try:
                instance = EuropeanCompetition.objects.get(pk=pk)
            except EuropeanCompetition.DoesNotExist:
                try:
                    instance = OtherCompetition.objects.get(pk=pk)
                except OtherCompetition.DoesNotExist:
                    return Response({"error": "Competition not found"}, status=404)

        instance.delete()
        return Response(status=204)
    

class ClubViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def list(self, request):
        queryset = Club.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)

class AthleteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer

    def list(self, request):
        queryset = Athlete.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)
    
class TitleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    def list(self, request):
        queryset = Title.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)
    

class FederationRoleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = FederationRole.objects.all()
    serializer_class = FederationRoleSerializer
    def list(self, request):
        queryset = FederationRole.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)
class GradeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    def list(self, request):
        queryset = Grade.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)
class GradeHistoryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = GradeHistory.objects.all()
    serializer_class = GradeHistorySerializer
    def list(self, request):
        queryset = GradeHistory.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def retrieve(self, request, pk=None):
        queryset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
    def update(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    def destroy(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.delete()
        return Response(status=204)