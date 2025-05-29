from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
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


