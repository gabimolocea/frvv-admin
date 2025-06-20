from django.db import models
from django.contrib import admin
from datetime import date, timedelta
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Competition(models.Model):
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100, blank=True, null=True)  # Place of the competition
    
    start_date = models.DateField(blank=True, null=True)  # Start date of the competition
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)  # Optional logo field
    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE, 
        related_name='clubs',
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    coaches = models.ManyToManyField(
        'Athlete', 
        related_name='coached_clubs', 
        blank=True
    )  # Replace coach field with ManyToManyField to Athlete
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Grade(models.Model):
    GRADE_TYPE_CHOICES = [
        ('inferior', 'Inferior Grade'),
        ('superior', 'Superior Grade'),
    ]

    name = models.CharField(max_length=100)
    rank_order = models.IntegerField(default=0)  # Rank order for grades (higher value = higher rank)
    grade_type = models.CharField(max_length=10, choices=GRADE_TYPE_CHOICES, default='inferior')  # Type of grade
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Rank: {self.rank_order}, Type: {self.get_grade_type_display()})"


class Title(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Title name

    def __str__(self):
        return self.name


class FederationRole(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Federation role name

    def __str__(self):
        return self.name


class Athlete(models.Model):
    # Personal Data
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    team_place = models.CharField(max_length=50, blank=True, null=True)  # Place awarded to the athlete in a team competition
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    club = models.ForeignKey(
        'Club',
        on_delete=models.SET_NULL,
        related_name='athletes',
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        related_name='athletes',
        blank=True,
        null=True
    )
    current_grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        related_name='current_athletes',
        blank=True,
        null=True
    )  # Automatically set based on GradeHistory
    federation_role = models.ForeignKey(
        'FederationRole',
        on_delete=models.SET_NULL,
        related_name='athletes',
        blank=True,
        null=True
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.SET_NULL,
        related_name='athletes',
        blank=True,
        null=True
    )
    registered_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    is_coach = models.BooleanField(default=False)
    is_referee = models.BooleanField(default=False)
    profile_image = models.ImageField(
        upload_to='profile_images/', blank=True, null=True, default='profile_images/default.png'
    )  # Optional profile image with default

    def update_current_grade(self):
        """
        Automatically set the current_grade to the grade with the highest rank_order from GradeHistory.
        """
        highest_grade = self.grade_history.order_by('-grade__rank_order').first()
        self.current_grade = highest_grade.grade if highest_grade else None
        self.save()

    def enrolled_competitions_and_categories(self):
        """
        Retrieve the competitions and categories where the athlete has been enrolled.
        """
        enrolled_categories = self.categories.all()  # Categories where the athlete is enrolled
        competitions = {category.competition for category in enrolled_categories}  # Extract competitions from categories

        return {
            "competitions": competitions,
            "categories": enrolled_categories,
        }
    
    def get_teams(self):
        """
        Retrieve the teams the athlete is part of.
        """
        return Team.objects.filter(members__athlete=self)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class GradeHistory(models.Model):
    LEVEL_CHOICES = [
        ('good', 'Good'),
        ('bad', 'Bad'),
    ]

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='grade_history')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    obtained_date = models.DateField(auto_now_add=True)  # Date when the grade was obtained
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='good')  # Dropdown for level
    exam_date = models.DateField(blank=True, null=True)  # Date of the exam
    exam_place = models.CharField(max_length=100, blank=True, null=True)  # Place of the exam
    technical_director = models.CharField(max_length=100, blank=True, null=True)  # Technical director of the exam
    president = models.CharField(max_length=100, blank=True, null=True)  # President of the exam

    def __str__(self):
        return f"{self.grade.name} for {self.athlete.first_name} {self.athlete.last_name} on {self.obtained_date}"


# Yearly Medical Visa
class MedicalVisa(models.Model):
    HEALTH_STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='medical_visas')
    issued_date = models.DateField(blank=True, null=True)  # Renamed from 'date' to 'issued_date'
    health_status = models.CharField(max_length=10, choices=HEALTH_STATUS_CHOICES, default='denied')  # Dropdown for health status
    
    @property
    def is_valid(self):
        """
        Determine if the medical visa is valid (within 6 months of the issued date).
        """
        if self.issued_date is None:  # Handle case where issued_date is None
            return False
        expiration_date = self.issued_date + timedelta(days=180)  # 6 months validity
        return date.today() <= expiration_date

    def __str__(self):
        status = "Available" if self.is_valid else "Expired"
        health_status = dict(self.HEALTH_STATUS_CHOICES).get(self.health_status, "Unknown")
        return f"Medical Visa for {self.athlete.first_name} {self.athlete.last_name} - {status} ({health_status})"


# Annual Visa
class AnnualVisa(models.Model):
    VISA_STATUS_CHOICES = [
        ('available', 'Available'),
        ('expired', 'Expired'),
        ('not_available', 'Not Available'),  # Default status
    ]

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='annual_visas')
    issued_date = models.DateField(blank=True, null=True)  # Date when the visa was issued
    visa_status = models.CharField(max_length=15, choices=VISA_STATUS_CHOICES, default='not_available')  # Default status

    @property
    def is_valid(self):
        """
        Determine if the annual visa is valid (within 12 months of the issued date).
        """
        if self.issued_date is None:  # Handle case where issued_date is None
            return False
        expiration_date = self.issued_date + timedelta(days=365)  # 12 months validity
        return date.today() <= expiration_date

    def update_visa_status(self):
        """
        Automatically update the visa status based on the issued date.
        """
        if self.issued_date:
            self.visa_status = 'available' if self.is_valid else 'expired'
        else:
            self.visa_status = 'not_available'

    def save(self, *args, **kwargs):
        """
        Override save to automatically update the visa status before saving.
        """
        self.update_visa_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Annual Visa for {self.athlete.first_name} {self.athlete.last_name} - {self.visa_status.capitalize()}"


# Training Seminars
class TrainingSeminar(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=100)
    athletes = models.ManyToManyField(Athlete, related_name='training_seminars',blank=True, )  # Many-to-Many relationship with Athlete

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date}) at {self.place}"

class CategoryAthlete(models.Model):
    """
    Through model for the many-to-many relationship between Category and Athlete.
    """
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="enrolled_athletes")
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Weight in kilograms

    class Meta:
        unique_together = ('category', 'athlete')  # Ensure an athlete cannot be added twice to the same category

    def delete(self, *args, **kwargs):
        """
        Override the delete method to remove the result from the database.
        """
        # Perform any additional cleanup if needed
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.athlete.first_name} {self.athlete.last_name} in {self.category.name} (Weight: {self.weight} kg)"
    
           
class CategoryTeam(models.Model):
    """
    Through model for the many-to-many relationship between Category and Team.
    """
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='enrolled_teams')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='enrolled_categories')  # Rename related_name

    class Meta:
        unique_together = ('category', 'team')  # Ensure a team cannot be added twice to the same category

    def __str__(self):
        return f"{self.team.name} in {self.category.name}"


class Team(models.Model):
    """
    Represents a team of athletes.
    """
    name = models.CharField(max_length=255, blank=True)  # Auto-generated name
    categories = models.ManyToManyField(
        'Category',
        through='CategoryTeam',  # Use the existing through model
        related_name='team_categories',
        blank=True,
        limit_choices_to={'type': 'teams'},  # Only allow categories with type 'teams'
    )


    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """
    Represents a member of a team.
    """
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='members')
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='team_members')

    class Meta:
        unique_together = ('team', 'athlete')  # Ensure an athlete cannot be added twice to the same team

    def __str__(self):
        return f"{self.athlete.first_name} {self.athlete.last_name} in {self.team.name}"


class Category(models.Model):
    """
    Represents a competition category.
    """
    CATEGORY_TYPE_CHOICES = [
        ('solo', 'Solo'),
        ('teams', 'Teams'),
        ('fight', 'Fight'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('mixt', 'Mixt'),
    ]

    name = models.CharField(max_length=100)
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, related_name='categories')
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default='solo')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='mixt')
    athletes = models.ManyToManyField('Athlete', through='CategoryAthlete', related_name='categories', blank=True)  # Many-to-Many relationship with Athlete
    teams = models.ManyToManyField('Team', through='CategoryTeam', related_name='category_teams', blank=True)  # Many-to-Many relationship with Team

    first_place = models.ForeignKey('Athlete', on_delete=models.SET_NULL, null=True, blank=True, related_name='first_place_categories')
    second_place = models.ForeignKey('Athlete', on_delete=models.SET_NULL, null=True, blank=True, related_name='second_place_categories')
    third_place = models.ForeignKey('Athlete', on_delete=models.SET_NULL, null=True, blank=True, related_name='third_place_categories')

    first_place_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='first_place_team_categories')
    second_place_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='second_place_team_categories')
    third_place_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='third_place_team_categories')
    
     # Use the existing relationships for enrolled teams and individuals
    
    def clean(self):
        """
        Validate that the awarded individual or team is enrolled in the category and not awarded multiple times.
        """
        if self.type == 'teams':
            # Validate teams
            awarded_teams = [self.first_place_team, self.second_place_team, self.third_place_team]
            # Ensure no duplicate awards for teams
            awarded_teams = list(filter(None, awarded_teams))  # Convert filter result to a list
            if len(set(awarded_teams)) != len(awarded_teams):
                raise ValidationError("The same team cannot be awarded multiple times within the same category.")

            # Ensure teams are enrolled before being awarded
            for team in awarded_teams:
                if team and not self.teams.filter(pk=team.pk).exists():
                    raise ValidationError(f"Team '{team}' must be enrolled in the category to be awarded.")
        elif self.type in ['solo', 'fight']:
            # Validate individuals
            awarded_athletes = [self.first_place, self.second_place, self.third_place]
            # Ensure no duplicate awards for athletes
            awarded_athletes = list(filter(None, awarded_athletes))  # Convert filter result to a list
            if len(set(awarded_athletes)) != len(awarded_athletes):
                raise ValidationError("The same athlete cannot be awarded multiple times within the same category.")

            # Ensure athletes are enrolled before being awarded
            for athlete in awarded_athletes:
                if athlete and not CategoryAthlete.objects.filter(category=self, athlete=athlete).exists():
                    raise ValidationError(f"Athlete '{athlete}' must be enrolled in the category to be awarded.")


    def calculate_athlete_scores(self):
        """
        Calculate total scores for each athlete in the category.
        """
        athlete_scores = {}
        for score in self.athlete_scores.all():
            athlete_scores[score.athlete] = athlete_scores.get(score.athlete, 0) + score.score
        return athlete_scores

    
    

    def save(self, *args, **kwargs):
        # Check if the type has changed
        if self.pk:  # Ensure this is not a new instance
            old_instance = Category.objects.get(pk=self.pk)
            if old_instance.type != self.type:
                # If the type has changed, clear athletes and teams
                self.athletes.clear()
                self.teams.clear()

        # Save the instance
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.competition.name})"


class Match(models.Model):
    MATCH_TYPE_CHOICES = [
        ('qualifications', 'Qualifications'),
        ('semi-finals', 'Semi-Finals'),
        ('finals', 'Finals'),
    ]

    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='matches')
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default='qualifications')
    red_corner = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='red_corner_matches')
    blue_corner = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='blue_corner_matches')
    referees = models.ManyToManyField('Athlete', related_name='refereed_matches', limit_choices_to={'is_referee': True})
    winner = models.ForeignKey('Athlete', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')
    name = models.CharField(max_length=255, blank=True)  # Automatically generated match name

    def calculate_winner(self):
        """
        Determine the winner based on referee votes.
        """
        red_votes = self.referee_scores.filter(winner='red').count()
        blue_votes = self.referee_scores.filter(winner='blue').count()
        if red_votes > blue_votes:
            return self.red_corner
        elif blue_votes > red_votes:
            return self.blue_corner
        return None  # No winner if votes are tied

    def save(self, *args, **kwargs):
        """
        Override save to clear the winner if referee scoring is removed and generate the match name.
        """
        # Save the instance first to ensure it has a primary key
        if not self.pk:
            super().save(*args, **kwargs)
            self.refresh_from_db()  # Reload the instance to ensure it has a primary key

        # Generate the match name
        self.name = f"{self.red_corner.first_name} vs {self.blue_corner.first_name} ({self.match_type}) - {self.category.name}"

        # Check if there are no referee scores
        if self.pk and not self.referee_scores.exists():
            self.winner = None  # Clear the winner

        # Save again to update the winner field and name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RefereeScore(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='referee_scores')
    referee = models.ForeignKey('Athlete', on_delete=models.CASCADE, limit_choices_to={'is_referee': True})
    red_corner_score = models.IntegerField(default=0)
    blue_corner_score = models.IntegerField(default=0)
    winner = models.CharField(max_length=10, choices=[('red', 'Red Corner'), ('blue', 'Blue Corner')], null=True, blank=True)

    def __str__(self):
        return f"Referee: {self.referee.first_name} {self.referee.last_name} - Match: {self.match}"


class CategoryAthleteScore(models.Model):
    """
    Stores referee scores for athletes in a category.
    """
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='athlete_scores')
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='category_scores')
    referee = models.ForeignKey('Athlete', on_delete=models.CASCADE, limit_choices_to={'is_referee': True})
    score = models.IntegerField(default=0)  # Score given by the referee

    class Meta:
        unique_together = ('category', 'athlete', 'referee')  # Ensure unique scores per referee and athlete

    def __str__(self):
        return f"{self.athlete.first_name} {self.athlete.last_name} - {self.category.name} - Referee: {self.referee.first_name} {self.referee.last_name}"


class CategoryTeamScore(models.Model):
    """
    Stores referee scores for teams in a category.
    """
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='team_scores')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='category_scores')
    referee = models.ForeignKey('Athlete', on_delete=models.CASCADE, limit_choices_to={'is_referee': True})
    score = models.IntegerField(default=0)  # Score given by the referee

    class Meta:
        unique_together = ('category', 'team', 'referee')  # Ensure unique scores per referee and team

    def __str__(self):
        return f"{self.team.name} - {self.category.name} - Referee: {self.referee.first_name} {self.referee.last_name}"


