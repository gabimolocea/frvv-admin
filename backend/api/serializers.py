from rest_framework import serializers
from .models import *

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class ClubSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())  # Accept city ID only
    coaches = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Athlete.objects.filter(is_coach=True))  # Include coaches

    class Meta:
        model = Club
        fields = ['id', 'name', 'address', 'mobile_number', 'website', 'coaches', 'city']

    def to_representation(self, instance):
        """Customize the output to include the full city object and coaches."""
        representation = super().to_representation(instance)
        if instance.city:
            representation['city'] = {
                'id': instance.city.id,
                'name': instance.city.name
            }
        else:
            representation['city'] = None  # Handle cases where city is None

        # Include full coach details
        representation['coaches'] = [
            {
                'id': coach.id,
                'first_name': coach.first_name,
                'last_name': coach.last_name
            }
            for coach in instance.coaches.all()
        ]
        return representation

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'
        depth = 1  # This will include the related clubs in the output


class AthleteSerializer(serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all(), allow_null=True)  # Accept club ID only
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), allow_null=True)  # Accept city ID only
    current_grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), allow_null=True)  # Accept grade ID only
    federation_role = serializers.PrimaryKeyRelatedField(queryset=FederationRole.objects.all(), allow_null=True)  # Accept role ID only
    title = serializers.PrimaryKeyRelatedField(queryset=Title.objects.all(), allow_null=True)  # Accept title ID only

    class Meta:
        model = Athlete
        fields = '__all__'
        depth = 1  # This will include related objects in the output
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'date_of_birth': {'required': True},
        }

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['id', 'name']

class FederationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederationRole
        fields = ['id', 'name']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']

class GradeHistorySerializer(serializers.ModelSerializer):
    athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())  # Accept athlete ID only
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all())  # Accept grade ID only
    obtained_date = serializers.DateField()
    class Meta:
        model = GradeHistory
        fields = ['id', 'athlete', 'grade', 'obtained_date']
