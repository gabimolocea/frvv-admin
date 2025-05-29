from django.contrib import admin
from django.utils.html import format_html
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
    AthleteCategory,
    Category,
    Team,
    CategoryTeam,
)

class AthleteInline(admin.TabularInline):
    model = Team.athletes.through
    extra = 0
    verbose_name = "Athlete"
    verbose_name_plural = "Athletes"

    

class TeamInline(admin.TabularInline):
    model = Category.teams.through
    extra = 0
    verbose_name = "Team"
    verbose_name_plural = "Teams"


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


# Inline AthleteCategory for Competition
class AthleteCategoryInline(admin.TabularInline):
    model = AthleteCategory
    extra = 0  # Do not show extra empty rows
    fields = ('athlete', 'current_weight')    
    show_change_link = True  # Allow linking to the related objects
    verbose_name = "Athlete (Fight)"
    verbose_name_plural = "Athletes (Fight)"


# Inline Category for Competition
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1  # Allow adding new categories
    show_change_link = True  # Allow linking to the related objects
    inlines = [AthleteCategoryInline]  # Nested inline for athletes


class CategoryTeamInline(admin.TabularInline):
    model = CategoryTeam  # Use the custom through model
    extra = 0
    verbose_name = "Team in Category"
    verbose_name_plural = "Teams in Category"


# Custom admin view for Competition
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')  # Display competition details
    inlines = []  # Add the inline for categories

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition', 'type', 'gender')
    inlines = [CategoryTeamInline]
    list_filter = ('type', 'gender', 'competition')
    filter_horizontal = ('athletes',)

    def get_inlines(self, request, obj=None):
        """
        Dynamically display inlines based on the category type.
        """
        if obj and obj.type == 'solo':
            return [AthleteInline]
        elif obj and obj.type == 'teams':
            return [TeamInline]
        elif obj and obj.type == 'fight':
            return [AthleteCategoryInline]
        return []

    def get_fields(self, request, obj=None):
        """
        Dynamically display fields based on the category type.
        """
        fields = ['name', 'competition', 'type', 'gender']
        if obj and obj.type == 'fight':
            fields += ['athletes']
        elif obj and obj.type == 'teams':
            fields += ['teams']
        elif obj and obj.type == 'solo':
            fields += ['athletes']
        return fields
    
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [AthleteInline]
    filter_horizontal = ('athletes',)  # Allow assigning athletes to teams
