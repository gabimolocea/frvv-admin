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
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='annual_visas')
    issued_date = models.DateField(blank=True, null=True)  # Date when the visa was issued
    visa_status = models.CharField(max_length=10, choices=VISA_STATUS_CHOICES, default='denied')  # Dropdown for visa status
    
    @property
    def is_valid(self):
        """
        Determine if the annual visa is valid (within 12 months of the issued date).
        """
        if self.issued_date is None:  # Handle case where issued_date is None
            return False
        expiration_date = self.issued_date + timedelta(days=365)  # 12 months validity
        return date.today() <= expiration_date

    def __str__(self):
        status = "Available" if self.is_valid else "Expired"
        visa_status = dict(self.VISA_STATUS_CHOICES).get(self.visa_status, "Unknown")
        return f"Annual Visa for {self.athlete.first_name} {self.athlete.last_name} - {status} ({visa_status})"


# Training Seminars
class TrainingSeminar(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=100)
    athletes = models.ManyToManyField(Athlete, related_name='training_seminars',blank=True, )  # Many-to-Many relationship with Athlete

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date}) at {self.place}"



    
class CategoryTeam(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team.name} in {self.category.name}"

class Team(models.Model):
    athletes = models.ManyToManyField(Athlete, related_name='teams')
    name = models.CharField(max_length=255, blank=True)  # Auto-generated name

    def save(self, *args, **kwargs):
        # Automatically generate the team name based on the athletes
        athlete_names = ", ".join([f"{athlete.first_name} {athlete.last_name}" for athlete in self.athletes.all()])
        self.name = f"Team: {athlete_names}"
        super().save(*args, **kwargs)

    def categories_list(self):
        return ", ".join([category.name for category in self.categories.all()])
    def __str__(self):
        return self.name

class CategoryTeam(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team.name} in {self.category.name}"
           
class Category(models.Model):
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
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='categories')
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default='solo')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='mixt')
    athletes = models.ManyToManyField(Athlete, related_name='categories', blank=True)
    teams = models.ManyToManyField(Team, through='CategoryTeam', related_name='new_categories', blank=True)  # New field with through model

    def __str__(self):
        return f"{self.name} ({self.competition.name})"
    

    
class AthleteCategory(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='athlete_categories')  # Link to Athlete
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='athlete_categories')  # Link to Category
    current_weight = models.FloatField(blank=True, null=True)  # Only for Fight type

    def __str__(self):
        return f"{self.athlete} in {self.category} (Weight: {self.current_weight})"