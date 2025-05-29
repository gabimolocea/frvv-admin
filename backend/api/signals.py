from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import *

@receiver(m2m_changed, sender=Club.coaches.through)
def update_is_coach(sender, instance, action, pk_set, **kwargs):
    """
    Signal to update the is_coach field in Athlete when the coaches field in Club is modified.
    """
    if action in ['post_add', 'post_remove']:
        for athlete_id in pk_set:
            athlete = Athlete.objects.get(pk=athlete_id)
            if action == 'post_add':
                if not athlete.is_coach:  # Prevent unnecessary updates
                    athlete.is_coach = True
                    athlete.save()
            elif action == 'post_remove':
                # Check if the athlete is still a coach for other clubs
                if not athlete.coached_clubs.exists() and athlete.is_coach:
                    athlete.is_coach = False
                    athlete.save()

@receiver(post_save, sender=Athlete)
def update_club_coaches(sender, instance, **kwargs):
    """
    Signal to update the coaches field in Club when the is_coach field in Athlete is modified.
    """
    # Prevent recursion by checking if the athlete is already in the club's coaches
    if instance.is_coach:
        if instance.club and not instance.club.coaches.filter(pk=instance.pk).exists():
            instance.club.coaches.add(instance)
    else:
        if instance.club and instance.club.coaches.filter(pk=instance.pk).exists():
            instance.club.coaches.remove(instance)

@receiver(post_save, sender=GradeHistory)
def update_current_grade(sender, instance, **kwargs):
    """
    Signal to update the current_grade field in Athlete when a new GradeHistory is created.
    """
    athlete = instance.athlete
    athlete.current_grade = instance.grade
    athlete.save()

@receiver(m2m_changed, sender=Category.teams.through)
def sync_category_and_team(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Synchronize the relationship between Category and Team.
    """
    if action in ['post_add', 'post_remove']:
        if reverse:
            # If the change is made from the Team side
            teams = Team.objects.filter(pk__in=pk_set)
            for team in teams:
                if action == 'post_add':
                    team.categories.add(instance)
                elif action == 'post_remove':
                    team.categories.remove(instance)
        else:
            # If the change is made from the Category side
            categories = Category.objects.filter(pk__in=pk_set)
            for category in categories:
                if action == 'post_add':
                    category.teams.add(instance)
                elif action == 'post_remove':
                    category.teams.remove(instance)

@receiver(post_save, sender=Team)
def validate_unique_team_members(sender, instance, **kwargs):
    """
    Ensure that no duplicate teams with the same members exist.
    """
    # Check if the team has athletes assigned
    if instance.athletes.exists():
        existing_teams = Team.objects.exclude(pk=instance.pk)
        for team in existing_teams:
            if set(team.athletes.all()) == set(instance.athletes.all()):
                raise ValidationError("A team with the same members already exists.")