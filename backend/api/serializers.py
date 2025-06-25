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
        fields = ['id', 'name', 'address', 'mobile_number', 'website', 'coaches', 'city', 'logo']

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

    
class TeamSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), allow_null=True)  # Accept category IDs only
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=TeamMember.objects.all(), allow_null=True)  # Accept member IDs only
    class Meta:
        model = Team
        fields = ['id', 'name', 'categories', 'members']
    def to_representation(self, instance):
        """Customize the output to include full category and member details."""
        representation = super().to_representation(instance)
        representation['categories'] = [
            {
                'id': category.id,
                'name': category.name
            }
            for category in instance.categories.all()
        ]
        representation['members'] = [
            {
                'id': member.id,
                'athlete': {
                    'id': member.athlete.id,
                    'first_name': member.athlete.first_name,
                    'last_name': member.athlete.last_name
                }
            }
            for member in instance.members.all()
        ]
        return representation
class TeamMemberSerializer(serializers.ModelSerializer):
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())  # Accept team ID only
    athlete = serializers.PrimaryKeyRelatedField(queryset=Athlete.objects.all())  # Accept athlete ID only
    class Meta:
        model = TeamMember
        fields = ['id', 'team', 'athlete', 'place']
    def to_representation(self, instance):
        """Customize the output to include full athlete details."""
        representation = super().to_representation(instance)
        representation['athlete'] = {
            'id': instance.athlete.id,
            'first_name': instance.athlete.first_name,
            'last_name': instance.athlete.last_name
        }
        return representation


class MatchSerializer(serializers.ModelSerializer):
    # Include related fields for better readability
    category_name = serializers.CharField(source='category.name', read_only=True)
    red_corner_name = serializers.CharField(source='red_corner.first_name', read_only=True)
    blue_corner_name = serializers.CharField(source='blue_corner.first_name', read_only=True)
    winner_name = serializers.CharField(source='winner.first_name', read_only=True, allow_null=True)
    referees = serializers.StringRelatedField(many=True)  # Display referees as strings

    class Meta:
        model = Match
        fields = [
            'id',
            'name',
            'category',
            'category_name',
            'match_type',
            'red_corner',
            'red_corner_name',
            'blue_corner',
            'blue_corner_name',
            'referees',
            'winner',
            'winner_name',
        ]
        read_only_fields = ['name', 'winner_name', 'category_name', 'red_corner_name', 'blue_corner_name']

    def validate(self, data):
        """
        Custom validation to ensure red_corner and blue_corner are enrolled in the category.
        """
        category = data.get('category')
        red_corner = data.get('red_corner')
        blue_corner = data.get('blue_corner')

        if category and red_corner and not category.athletes.filter(pk=red_corner.pk).exists():
            raise serializers.ValidationError(f"Red corner athlete '{red_corner}' must be enrolled in the category.")
        if category and blue_corner and not category.athletes.filter(pk=blue_corner.pk).exists():
            raise serializers.ValidationError(f"Blue corner athlete '{blue_corner}' must be enrolled in the category.")

        return data
    

class AnnualVisaSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()   # Include the computed property

    class Meta:
        model = AnnualVisa
        fields = ['id', 'athlete', 'issued_date', 'visa_status', 'is_valid']
        read_only_fields = ['is_valid']

class CategoryAthleteSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(read_only=True)  # Serialize the related Athlete object

    class Meta:
        model = CategoryAthlete
        fields = ('athlete', 'weight')  # Include the athlete and additional fields like weight

class CategorySerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    enrolled_athletes = CategoryAthleteSerializer(many=True, read_only=True)  # Include enrolled athletes
    teams = TeamSerializer(many=True, read_only=True)  # Use the existing TeamSerializer for teams
    first_place_name = serializers.CharField(source='first_place.first_name', read_only=True, allow_null=True)
    second_place_name = serializers.CharField(source='second_place.first_name', read_only=True, allow_null=True)
    third_place_name = serializers.CharField(source='third_place.first_name', read_only=True, allow_null=True)
    first_place_team = TeamSerializer(read_only=True)  # Include detailed team information
    second_place_team = TeamSerializer(read_only=True)  # Include detailed team information
    third_place_team = TeamSerializer(read_only=True)  # Include detailed team information
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)  # Include group name

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'competition', 'competition_name', 'group', 'group_name', 'type', 'gender',
            'enrolled_athletes', 'teams', 'first_place', 'second_place', 'third_place',
            'first_place_name', 'second_place_name', 'third_place_name',
            'first_place_team', 'second_place_team', 'third_place_team',
        ]

class GradeHistorySerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.first_name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = GradeHistory
        fields = [
            'id', 'athlete', 'athlete_name', 'grade', 'grade_name', 'obtained_date',
            'level', 'exam_date', 'exam_place', 'technical_director', 'president',
        ]

class MedicalVisaSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)  # Include the computed property

    class Meta:
        model = MedicalVisa
        fields = ['id', 'athlete', 'issued_date', 'health_status', 'is_valid']
        read_only_fields = ['is_valid']

class TrainingSeminarSerializer(serializers.ModelSerializer):
    athletes_names = serializers.StringRelatedField(many=True, source='athletes')  # Display athlete names

    class Meta:
        model = TrainingSeminar
        fields = ['id', 'name', 'start_date', 'end_date', 'place', 'athletes', 'athletes_names']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'competition', 'categories']
        read_only_fields = ['id']