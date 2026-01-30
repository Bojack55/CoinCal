from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=UserProfile)
def calculate_calorie_goal(sender, instance, created, **kwargs):
    # Only calculate if specific fields changed or it's new
    # For simplicity in this Foundation step, we calculate on every save
    
    # Formula factors
    W = instance.weight
    H = instance.height
    A = instance.age
    
    if instance.gender == 'M':
        bmr = (10 * W) + (6.25 * H) - (5 * A) + 5
    else:
        bmr = (10 * W) + (6.25 * H) - (5 * A) - 161
        
    # Activity Multipliers
    multipliers = {
        'Sedentary': 1.2,
        'Light': 1.375,
        'Moderate': 1.55,
        'Active': 1.725
    }
    
    factor = multipliers.get(instance.activity_level, 1.2)
    new_goal = int(bmr * factor)
    
    if instance.calorie_goal != new_goal:
        # Use update() to avoid recursion by post_save signal
        UserProfile.objects.filter(pk=instance.pk).update(calorie_goal=new_goal)
