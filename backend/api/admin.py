from django.contrib import admin
from django.utils.html import format_html
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from .models import (
    City,
    Club,
    Athlete,
    MedicalVisa,
    TrainingSeminar,
    Grade,
    GradeHistory,
    Title,
    FederationRole,
    Competition,
    AnnualVisa,
    Category,
    Team,
    CategoryTeam,
    CategoryAthlete
)

class AthleteInline(admin.TabularInline):
    model = Athlete
    fields = ('first_name', 'last_name', 'club', 'city')
    extra = 0
    verbose_name = "Athlete"
    verbose_name_plural = "Athletes"

class CategoryAthleteInline(admin.TabularInline):
    model = CategoryAthlete
    fields = ('athlete', 'weight')  # Display athlete and weight fields
    readonly_fields = ('athlete_with_club',)
    extra = 0
    autocomplete_fields = ['athlete']  # Enable autocomplete for the athlete field
    verbose_name = "Athlete in Category"
    verbose_name_plural = "Athletes in Category"


# Inline GradeHistory for Athlete
class GradeHistoryInline(admin.TabularInline):
    model = GradeHistory
    extra = 0  # Display only existing entries
    readonly_fields = ('obtained_date',)  # Make obtained_date read-only
    show_change_link = True  # Enable link to open the GradeHistory add/edit page

# Inline MedicalVisa for Athlete
class MedicalVisaInline(admin.TabularInline):
    model = MedicalVisa
    extra = 0  # Display only existing entries
    fields = ('issued_date', 'health_status', 'visa_status')  # Include visa status
    readonly_fields = ('visa_status',)  # Make visa status read-only

    def visa_status(self, obj):
        """
        Display visa status as 'Available' or 'Expired'.
        """
        return "Available" if obj.is_valid else "Expired"
    visa_status.short_description = "Visa Status"

# Inline AnnualVisa for Athlete
class AnnualVisaInline(admin.TabularInline):
    model = AnnualVisa
    extra = 0  # Display only existing entries
    fields = ('issued_date', 'visa_status', 'visa_status_display')  # Include visa status
    readonly_fields = ('visa_status_display',)  # Make visa status read-only

    def visa_status_display(self, obj):
        """
        Display visa status as 'Available' or 'Expired'.
        """
        return "Available" if obj.is_valid else "Expired"
    visa_status_display.short_description = "Visa Status"

# Inline TrainingSeminar for Athlete
class TrainingSeminarInline(admin.TabularInline):
    model = TrainingSeminar.athletes.through  # Use the through table for the Many-to-Many relationship
    extra = 0  # Display only existing entries
    show_change_link = True  # Enable link to open the TrainingSeminar add/edit page
    verbose_name = "TRAINING SEMINAR"
    verbose_name_plural = "TRAINING SEMINARS"


# Register City model
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')
    search_fields = ('name',)

# Register Club model
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'mobile_number', 'website', 'created', 'modified')
    search_fields = ('name', 'city__name')
    filter_horizontal = ('coaches',)  # Add horizontal filter for ManyToManyField

    # Organize fields in the admin form
    fieldsets = (
        ('Club Details', {
            'fields': ('name', 'logo', 'city', 'address', 'mobile_number', 'website')
        }),
        ('Timestamps', {
            'fields': ('modified',)  # Only include editable fields
        }),
    )

    readonly_fields = ('created', 'modified')  # Mark non-editable fields as read-only

# Register Athlete model
@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'current_grade', 'club', 'city', 'date_of_birth', 'is_coach', 'is_referee')
    search_fields = ('first_name', 'last_name', 'current_grade__name', 'club__name', 'city__name')
    list_filter = ('current_grade', 'club', 'city', 'is_coach', 'is_referee')

    # Organize fields in the admin form
    fieldsets = (
        ('PERSONAL INFORMATION', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_image', 'city', 'address', 'mobile_number')
        }),
        ('CLUB INFORMATION', {
            'fields': ('club', 'registered_date', 'expiration_date')
        }),
        ('FEDERATION ROLE AND TITLE', {
            'fields': ('federation_role', 'title', 'current_grade')
        }),
        ('OTHER INFORMATION', {
            'fields': ('is_coach', 'is_referee')
        }),
    )

    readonly_fields = ('current_grade',)  # Make Current Grade read-only

    def save_model(self, request, obj, form, change):
        """
        Override save_model to update current_grade after saving the athlete.
        """
        super().save_model(request, obj, form, change)
        obj.update_current_grade()  # Automatically update current_grade

    inlines = [GradeHistoryInline, MedicalVisaInline, AnnualVisaInline, TrainingSeminarInline]  # Include TrainingSeminarInline

# Register MedicalVisa model
@admin.register(MedicalVisa)
class MedicalVisaAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'issued_date', 'health_status', 'visa_status')  # Display visa status
    search_fields = ('athlete__first_name', 'athlete__last_name')
    list_filter = ('health_status',)  # Add a filter for health status
    readonly_fields = ('visa_status',)  # Make visa status read-only

    def visa_status(self, obj):
        """
        Display visa status as 'Available' or 'Expired'.
        """
        return "Available" if obj.is_valid else "Expired"
    visa_status.short_description = "Visa Status"

# Register AnnualVisa model
@admin.register(AnnualVisa)
class AnnualVisaAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'issued_date', 'visa_status', 'visa_status_display')  # Display visa status
    search_fields = ('athlete__first_name', 'athlete__last_name', 'visa_status')
    list_filter = ('visa_status',)  # Add a filter for visa status
    readonly_fields = ('visa_status_display',)  # Make visa status read-only

    def visa_status_display(self, obj):
        """
        Display visa status as 'Available' or 'Expired'.
        """
        return "Available" if obj.is_valid else "Expired"
    visa_status_display.short_description = "Visa Status"

# Register TrainingSeminar model
@admin.register(TrainingSeminar)
class TrainingSeminarAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'place')  # Display seminar details
    search_fields = ('name', 'place')
    list_filter = ('start_date', 'end_date', 'place')
    filter_horizontal = ('athletes',)  # Allow selecting multiple athletes in the admin panel

# Register Grade model with the new grade_type field
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank_order', 'grade_type', 'created', 'modified')  # Include grade_type in list_display
    search_fields = ('name', 'grade_type')  # Enable search by grade_type
    list_filter = ('grade_type', 'created', 'modified')  # Enable filtering by grade_type

# Updated GradeHistoryAdmin
@admin.register(GradeHistory)
class GradeHistoryAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'grade', 'level', 'exam_date', 'exam_place', 'technical_director', 'president', 'obtained_date')
    search_fields = ('athlete__first_name', 'athlete__last_name', 'grade__name', 'level')
    list_filter = ('level', 'exam_date', 'exam_place', 'obtained_date')
    # Do not use readonly_fields here to allow editing in the standalone GradeHistory admin panel

# Register Title model
@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register FederationRole model
@admin.register(FederationRole)
class FederationRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_associated_athletes')
    search_fields = ('name',)

    def get_associated_athletes(self, obj):
        """
        Custom method to display athletes associated with the federation role.
        """
        athletes = Athlete.objects.filter(federation_role=obj)
        return ", ".join([f"{athlete.first_name} {athlete.last_name}" for athlete in athletes]) if athletes else "None"
    get_associated_athletes.short_description = 'Associated Athletes'


# Custom admin view for Competition
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'place', 'start_date', 'end_date')  # Display competition details
    inlines = []  # Add the inline for categories

class CategoryTeamInline(admin.TabularInline):
    model = CategoryTeam  # Use the custom through model
    #fields = ('team',)  # Display the team field
    autocomplete_fields = ['team', 'category']  # Enable autocomplete for the team field
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        Dynamically set the verbose_name_plural based on the parent model.
        """
        if isinstance(obj, Team):
            self.fields = ('category',)
            self.verbose_name_plural = "TEAM ENROLLED TO CATEGORIES"
        elif isinstance(obj, Category):
            self.fields = ('team',)
            self.verbose_name_plural = "ENROLLED TEAMS"
        return super().get_formset(request, obj, **kwargs)

    def get_queryset(self, request):
        """
        Filter the queryset to display teams only for categories of type 'Teams'.
        """
        qs = super().get_queryset(request)
        # Filter the queryset to include only categories of type 'Teams'
        return qs.filter(category__type='teams')
    def save_new(self, form, commit=True):
        """
        Override save_new to prevent duplicate teams in the same category.
        """
        instance = form.save(commit=False)
        if CategoryTeam.objects.filter(category=instance.category, team=instance.team).exists():
            raise ValidationError(f"The team '{instance.team}' is already assigned to this category.")
        return super().save_new(form, commit)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition', 'type', 'gender')
    inlines = [CategoryTeamInline]  # Add the inline for managing enrolled teams
    filter_horizontal = ('athletes',)  # Allow assigning athletes directly
    search_fields = ('name', 'competition__name', 'type', 'gender')  # Add search fields

    def get_form(self, request, obj=None, **kwargs):
        """
        Dynamically modify the form to hide the 'athletes' field when creating a new category.
        """
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # If creating a new category
            # Remove the 'athletes' field from the form
            if 'athletes' in form.base_fields:
                del form.base_fields['athletes']
            # Add a custom help text message
            form.base_fields['name'].help_text = (
                "Create the category first, then reopen it to add athletes or teams."
            )
        return form

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically modify the fieldsets to hide the 'athletes' field if the category type is 'Teams and Fight'.
        """
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.type in ['teams', 'fight']:
            # Remove the 'athletes' field if the category type is 'Teams'
            return (
                ('CATEGORY DETAILS', {
                    'fields': ('name', 'competition', 'type', 'gender')
                }),
            )
        return fieldsets
    

    def get_inlines(self, request, obj=None):
        """
        Dynamically include the CategoryTeamInline only if the category type is 'Teams',
        and include the CategoryAthleteInline only if the category type is 'Fight'.
        """
        if obj:
            if obj.type == 'teams':
                return [CategoryTeamInline]
            elif obj.type == 'fight':
                return [CategoryAthleteInline]
        return []

class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def clean(self):
        """
        Validate that no team with the same set of athletes already exists.
        """
        cleaned_data = super().clean()
        athletes = self.cleaned_data.get('athletes')

        if self.instance.pk:  # If editing an existing team
            existing_teams = Team.objects.exclude(pk=self.instance.pk)
        else:  # If creating a new team
            existing_teams = Team.objects.all()

        for team in existing_teams:
            if set(team.athletes.all()) == set(athletes):
                raise ValidationError("A team with the same members already exists.")

        return cleaned_data
                
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_display = ('name',)  # Display team name
    filter_horizontal = ('athletes',)  # Allow assigning athletes to the team
    readonly_fields = ('name',)
    search_fields = ('name', 'athletes__first_name', 'athletes__last_name')  # Add search fields
    inlines = [CategoryTeamInline]

