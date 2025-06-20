from django.contrib import admin
from django.utils.html import format_html
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
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
    CategoryAthlete,
    Match,
    RefereeScore,
    CategoryAthleteScore,
    CategoryTeamScore,
    TeamMember,
)


class AthleteInline(admin.TabularInline):
    model = Athlete
    fields = ('first_name', 'last_name', 'club', 'city')
    extra = 0
    verbose_name = "Athlete"
    verbose_name_plural = "Athletes"

class CategoryAthleteInline(admin.TabularInline):
    model = CategoryAthlete
    extra = 0
    autocomplete_fields = ['athlete']  # Enable autocomplete for the athlete field
    verbose_name = "Athlete"
    verbose_name_plural = "Athletes"

    def get_formset(self, request, obj=None, **kwargs):
        """
        Dynamically adjust the inline title and fields based on the parent model.
        """
        if isinstance(obj, Category):
            if obj.type == 'fight':
                self.verbose_name = "Athlete"
                self.verbose_name_plural = "ENROLLED ATHLETES"
                self.fields = ('athlete', 'weight')  # Only include actual fields from the model
                self.readonly_fields = ('category_with_competition', 'category_type')  # Computed fields are read-only
            elif obj.type == 'solo':
                self.verbose_name = "Enrolled Athlete"
                self.verbose_name_plural = "Enrolled Athletes"

            else:
                self.verbose_name = "Competition History"
                self.verbose_name_plural = "Add another Competition History"
                self.fields = ('category_with_competition', 'category_type', 'weight')  # Only include actual fields from the model
                self.readonly_fields = ('athlete_with_club', 'category_with_competition', 'category_type', 'weight')  # Computed fields are read-only
        return super().get_formset(request, obj, **kwargs)

    def athlete_with_club(self, obj):
        """
        Display the athlete's name along with their club.
        """
        if obj.athlete.club:
            return f"{obj.athlete.first_name} {obj.athlete.last_name} ({obj.athlete.club.name})"
        return f"{obj.athlete.first_name} {obj.athlete.last_name}"
    athlete_with_club.short_description = "Athlete (Club)"

    def category_with_competition(self, obj):
        """
        Display the category name along with its competition.
        """
        return f"{obj.category.name} ({obj.category.competition.name})"
    category_with_competition.short_description = "Category (Competition)"

    def category_type(self, obj):
        """
        Display the type of the category.
        """
        return obj.category.type.capitalize()
    category_type.short_description = "Category Type"


class AthleteTeamResultsInline(admin.TabularInline):
    model = TeamMember  # Use the TeamMember model
    extra = 0
    verbose_name = "TEAM RESULTS"
    verbose_name_plural = "TEAM RESULTS"
    can_add = False  # Disable the "Add another TEAM RESULTS" button
    can_delete = False  # Disable the "Delete" button
    show_change_link = False  # Hide the "Change" link
    show_add_link = False

    fields = ('category_name', 'competition_name', 'place_obtained')  # Fields to display
    readonly_fields = ('place_obtained', 'category_name', 'competition_name')  # Make fields read-only

    def category_name(self, obj):
        """
        Display the category name without including the team name.
        """
        categories = obj.team.categories.all()
        return ", ".join([category.name for category in categories]) if categories else "No Categories"
    category_name.short_description = "Category Name"

    def competition_name(self, obj):
        """
        Display the competition name associated with the categories the team is enrolled in.
        """
        competitions = obj.team.categories.values_list('competition__name', flat=True).distinct()
        return ", ".join(competitions) if competitions else "No Competitions"
    competition_name.short_description = "Competition Name"

    

    def place_obtained(self, obj):
        """
        Display the place obtained by the team in the categories it is enrolled in.
        """
        # Check if the team has been awarded a place in any category
        first_place_categories = obj.team.first_place_team_categories.all()
        second_place_categories = obj.team.second_place_team_categories.all()
        third_place_categories = obj.team.third_place_team_categories.all()

        if first_place_categories.exists():
            return "1st Place"
        elif second_place_categories.exists():
            return "2nd Place"
        elif third_place_categories.exists():
            return "3rd Place"
        return "No Placement"
    place_obtained.short_description = "Place Obtained"

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

class MatchInline(admin.TabularInline):
    model = Match
    extra = 0
    autocomplete_fields = ['red_corner', 'blue_corner', 'winner']  # Enable autocomplete for these fields
    fields = ('match_type', 'red_corner', 'blue_corner', 'winner')  # Do not show referees
    readonly_fields = ('winner',)
    verbose_name = "Match"
    verbose_name_plural = "Matches"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restrict athlete selection to those enrolled in the category for red_corner and blue_corner.
        """
        if db_field.name in ['red_corner', 'blue_corner']:
            # Check if the parent object (Category) is available in the request
            if hasattr(request, 'parent_model') and request.parent_model == Category:
                category_id = request.resolver_match.kwargs.get('object_id')  # Get the category ID from the URL
                if category_id:
                    kwargs['queryset'] = Athlete.objects.filter(categories__id=category_id)  # Filter athletes by category
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class RefereeScoreInline(admin.TabularInline):
    model = RefereeScore
    extra = 0
    autocomplete_fields = ['referee']
    fields = ('referee', 'red_corner_score', 'blue_corner_score', 'winner')

class CategoryAthleteScoreInline(admin.TabularInline):
    model = CategoryAthleteScore  # Ensure this model exists in your models.py
    extra = 0
    autocomplete_fields = ['athlete', 'referee']  # Enable autocomplete for athlete and referee fields
    fields = ('athlete', 'referee', 'score')  # Display athlete, referee, and score fields
    verbose_name = "Athlete Score"
    verbose_name_plural = "Athlete Scores"

class CategoryTeamScoreInline(admin.TabularInline):
    model = CategoryTeamScore  # Ensure this model exists in your models.py
    extra = 0
    autocomplete_fields = ['team', 'referee']  # Enable autocomplete for team and referee fields
    fields = ('team', 'referee', 'score')  # Display team, referee, and score fields
    verbose_name = "Team Score"
    verbose_name_plural = "Team Scores"

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1  # Allow adding new athletes to the team
    verbose_name = "Team Member"
    verbose_name_plural = "Team Members"

class EnrolledTeamsInline(admin.TabularInline):
    model = CategoryTeam
    extra = 1  # Allow adding new teams
    fields = ('team', 'place_obtained')
    readonly_fields = ('place_obtained',)
    verbose_name_plural = "TEAMS ENROLLED"  # Rename the section title

    def place_obtained(self, obj):
        """
        Display the place obtained by the team in the category.
        """
        if obj.category.first_place_team == obj.team:
            return "1st Place"
        elif obj.category.second_place_team == obj.team:
            return "2nd Place"
        elif obj.category.third_place_team == obj.team:
            return "3rd Place"
        return "No Placement"
    place_obtained.short_description = "Place Obtained"

class AthleteSoloResultsInline(admin.TabularInline):
    """
    Inline to display results for solo categories.
    """
    model = CategoryAthlete
    extra = 0
    verbose_name = "Solo Results"
    verbose_name_plural = "Solo Results"
    can_add = False  # Disable the "Add another" button
    can_delete = False  # Disable the "Delete" button
    show_change_link = False  # Hide the "Change" link
    fields = ('category_name', 'competition_name', 'results')  # Fields to display
    readonly_fields = ('category_name', 'competition_name', 'results')  # Make fields read-only

    def get_queryset(self, request):
        """
        Filter the queryset to include only results for solo categories.
        """
        qs = super().get_queryset(request)
        return qs.filter(category__type='solo')  # Filter by category type 'solo'

    def category_name(self, obj):
        """
        Display the category name.
        """
        return obj.category.name
    category_name.short_description = "Category Name"

    def competition_name(self, obj):
        """
        Display the competition name.
        """
        return obj.category.competition.name if obj.category.competition else "N/A"
    competition_name.short_description = "Competition Name"

    def results(self, obj):
        """
        Display the results of the athlete for solo categories.
        """
        if obj.category.first_place == obj.athlete:
            return "1st Place"
        elif obj.category.second_place == obj.athlete:
            return "2nd Place"
        elif obj.category.third_place == obj.athlete:
            return "3rd Place"
        return "No Placement"
    results.short_description = "Place Obtained"


class AthleteFightResultsInline(admin.TabularInline):
    """
    Inline to display results for fight categories.
    """
    model = CategoryAthlete
    extra = 0
    verbose_name = "Fight Results"
    verbose_name_plural = "Fight Results"
    can_add = False  # Disable the "Add another" button
    can_delete = False  # Disable the "Delete" button
    show_change_link = False  # Hide the "Change" link
    fields = ('category_name', 'competition_name', 'results')  # Fields to display
    readonly_fields = ('category_name', 'competition_name', 'results')  # Make fields read-only

    def get_queryset(self, request):
        """
        Filter the queryset to include only results for fight categories.
        """
        qs = super().get_queryset(request)
        return qs.filter(category__type='fight')  # Filter by category type 'fight'

    def category_name(self, obj):
        """
        Display the category name.
        """
        return obj.category.name
    category_name.short_description = "Category Name"

    def competition_name(self, obj):
        """
        Display the competition name.
        """
        return obj.category.competition.name if obj.category.competition else "N/A"
    competition_name.short_description = "Competition Name"

    def results(self, obj):
        """
        Display the results of the athlete for fight categories.
        """
        if obj.category.first_place == obj.athlete:
            return "1st Place"
        elif obj.category.second_place == obj.athlete:
            return "2nd Place"
        elif obj.category.third_place == obj.athlete:
            return "3rd Place"
        return "No Placement"
    results.short_description = "Place Obtained"


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
    list_display = ('first_name', 'last_name', 'current_grade', 'club', 'city', 'date_of_birth', 'is_coach', 'is_referee', 'view_team_results')
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

    readonly_fields = ('current_grade',)

    def save_model(self, request, obj, form, change):
        """
        Override save_model to update current_grade after saving the athlete.
        """
        super().save_model(request, obj, form, change)
        obj.update_current_grade()  # Automatically update current_grade

    def view_team_results(self, obj):
        """
        Add a link to view team results for the athlete.
        """
        return format_html('<a href="{}">View Team Results</a>', f'/admin/api/athlete/{obj.id}/')
    view_team_results.short_description = "Team Results"

    def get_urls(self):
        """
        Add a custom URL for the team results view.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<int:athlete_id>/team-results/', self.admin_site.admin_view(self.team_results_view), name='team-results'),
        ]
        return custom_urls + urls

    def team_results_view(self, request, athlete_id):
        """
        Custom view to display team results for the athlete.
        """
        athlete = Athlete.objects.get(id=athlete_id)
        teams = athlete.teams.all()
        team_results = []
        for team in teams:
            first_place_categories = team.first_place_team_categories.all()
            second_place_categories = team.second_place_team_categories.all()
            third_place_categories = team.third_place_team_categories.all()

            if first_place_categories.exists():
                team_results.append(f"{team.name}: 1st Place")
            elif second_place_categories.exists():
                team_results.append(f"{team.name}: 2nd Place")
            elif third_place_categories.exists():
                team_results.append(f"{team.name}: 3rd Place")
            else:
                team_results.append(f"{team.name}: No Placement")

        context = {
            'athlete': athlete,
            'team_results': team_results,
        }
        return render(request, 'admin/team_results.html', context)

    # Add the new inlines for solo and fight results
    inlines = [
        GradeHistoryInline,
        MedicalVisaInline,
        AnnualVisaInline,
        TrainingSeminarInline,
        AthleteSoloResultsInline,  # Inline for solo results
        AthleteFightResultsInline,  # Inline for fight results
        AthleteTeamResultsInline,  # Inline for team results
    ]

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
    model = CategoryTeam
    extra = 0
    fields = ('category', 'place_obtained')
    readonly_fields = ('place_obtained',)
    verbose_name_plural = "TEAM ENROLLED TO FOLLOWING CATEGORIES"  # Rename the section title
    def place_obtained(self, obj):
        """
        Display the place obtained by the team in the category.
        """
        if obj.category.first_place_team == obj.team:
            return "1st Place"
        elif obj.category.second_place_team == obj.team:
            return "2nd Place"
        elif obj.category.third_place_team == obj.team:
            return "3rd Place"
        return "No Placement"
    place_obtained.short_description = "Place Obtained"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition', 'type', 'gender', 'display_winners')
  #  filter_horizontal = ('athletes',)  # Allow assigning athletes directly
    search_fields = ('name', 'competition__name', 'type', 'gender')  # Add search fields
    autocomplete_fields = ['first_place', 'second_place', 'third_place', 'first_place_team', 'second_place_team', 'third_place_team']
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
        
        fieldsets = [
            ('CATEGORY DETAILS', {
                'fields': ('name', 'competition', 'type', 'gender')
            }),
        ]
        if obj and obj.type in ['solo', 'fight']:
            fieldsets.append(('AWARDS - INDIVIDUAL', {
                'fields': ('first_place', 'second_place', 'third_place'),

            }))
        elif obj and obj.type == 'teams':
            fieldsets.append(('AWARDS - TEAMS', {
                'fields': ('first_place_team', 'second_place_team', 'third_place_team'),

            }))
        return fieldsets

    def get_inlines(self, request, obj=None):
        """
        Dynamically include inlines based on category type.
        """
        inlines = []
        if obj:
            if obj.type == 'solo':
                inlines.append(CategoryAthleteInline)
                inlines.append(CategoryAthleteScoreInline)  # Add athlete score inline for solo categories
            elif obj.type == 'teams':
                inlines.append(CategoryTeamScoreInline)  # Add team score inline for teams categories
                inlines.append(EnrolledTeamsInline)  # Add the new EnrolledTeamsInline
            elif obj.type == 'fight':
                inlines.extend([CategoryAthleteInline, MatchInline])  # Add athlete and match inlines for fight categories
        return inlines

    def display_winners(self, obj):
        """
        Display the winners for the category.
        """
        if obj.type in ['solo', 'fight']:
            return f"1st: {obj.first_place}, 2nd: {obj.second_place}, 3rd: {obj.third_place}"
        elif obj.type == 'teams':
            return f"1st: {obj.first_place_team}, 2nd: {obj.second_place_team}, 3rd: {obj.third_place_team}"
        return "No winners assigned"
    display_winners.short_description = "Winners"

    def save_model(self, request, obj, form, change):
        """
        Trigger validation before saving the category.
        """
        obj.clean()  # Trigger validation logic
        super().save_model(request, obj, form, change)

    def enrolled_teams_count(self, obj):
        """
        Display the number of teams enrolled in the category.
        """
        return obj.enrolled_teams.count()
    enrolled_teams_count.short_description = "Enrolled Teams Count"

    def enrolled_individuals_count(self, obj):
        """
        Display the number of individuals enrolled in the category.
        """
        return obj.enrolled_individuals.count()
    enrolled_individuals_count.short_description = "Enrolled Individuals Count"

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_categories')  # Display team name and assigned categories
    readonly_fields = ('name',)
    inlines = [TeamMemberInline, CategoryTeamInline]  # Include both inlines
    search_fields = ('name',)  # Enable search by team name
    def assigned_categories(self, obj):
        """
        Display the categories assigned to the team.
        """
        categories = obj.categories.all()
        return ", ".join([category.name for category in categories]) if categories else "No Categories Assigned"
    assigned_categories.short_description = "Assigned Categories"

    def save_model(self, request, obj, form, change):
        """
        Save the team instance and validate that no duplicate team exists.
        """
        # Save the team instance first to ensure it has a primary key
        super().save_model(request, obj, form, change)

        # Validate that no team with the same set of athletes already exists
        team_members = set(obj.members.values_list('athlete', flat=True))
        existing_teams = Team.objects.exclude(pk=obj.pk)

        for team in existing_teams:
            existing_team_members = set(team.members.values_list('athlete', flat=True))
            if team_members == existing_team_members:
                raise ValueError("A team with the same members already exists.")

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('name_with_corners', 'match_type', 'get_winner', 'category_link', 'competition')
    search_fields = ('name', 'red_corner__first_name', 'red_corner__last_name', 'blue_corner__first_name', 'blue_corner__last_name', 'winner__first_name', 'category__name', 'category__competition__name')
    list_filter = ('match_type', 'category__competition')

    fieldsets = (
        ('MATCH DETAILS', {
            'fields': ('category', 'match_type', 'red_corner', 'blue_corner', 'winner')  # Added winner field
        }),
    )

    autocomplete_fields = ['red_corner', 'blue_corner', 'winner']  # Enable autocomplete for these fields

    inlines = [RefereeScoreInline]

    def name_with_corners(self, obj):
        """
        Display the full names of the athletes with their corner in parentheses.
        """
        return f"{obj.red_corner.first_name} {obj.red_corner.last_name} (Red Corner) vs {obj.blue_corner.first_name} {obj.blue_corner.last_name} (Blue Corner)"
    name_with_corners.short_description = "Match Name"

    def competition(self, obj):
        """
        Display the competition name associated with the match.
        """
        return obj.category.competition.name if obj.category.competition else "N/A"
    competition.short_description = "Competition"

    def category_link(self, obj):
        """
        Display the category name as a clickable link.
        """
        return format_html('<a href="/admin/api/category/{}/change/">{}</a>', obj.category.id, obj.category.name)
    category_link.short_description = "Category"

    def get_winner(self, obj):
        """
        Display the full name of the winner in the admin interface.
        """
        return f"{obj.winner.first_name} {obj.winner.last_name}" if obj.winner else "TBD"
    get_winner.short_description = "Winner"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restrict athlete selection to those within the selected category for red_corner, blue_corner, and winner.
        """
        if db_field.name in ['red_corner', 'blue_corner']:
            if hasattr(request, 'obj') and isinstance(request.obj, Match):
                kwargs['queryset'] = request.obj.category.athletes.all()
        elif db_field.name == 'winner':
            if hasattr(request, 'obj') and isinstance(request.obj, Match):
                kwargs['queryset'] = Athlete.objects.filter(pk__in=[request.obj.red_corner.pk, request.obj.blue_corner.pk])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

