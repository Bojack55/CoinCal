from django.core.management.base import BaseCommand
from api.models import UserProfile
from api.utils.location_helpers import CITY_PRICE_CATEGORIES

class Command(BaseCommand):
    help = 'Populates the UserProfile with location categories for existing users based on their location.'

    def handle(self, *args, **options):
        self.stdout.write("Populating location categories...")
        
        # We don't need a City model anymore, we just need to update user profiles
        # But wait, the user instructions said "Populate Cities"
        # In the original plan, we had a City model.
        # But we pivoted to `location_helpers.py`.
        # So "populate_cities" is a misnomer now, it should probably be `update_user_locations`.
        # HOWEVER, the user is expecting `populate_cities`. 
        # So I will make this command do nothing or just print "Cities are managed dynamically now."
        # OR better yet, I will make it update all existing user profiles to have the correct category.
        
        count = 0
        for profile in UserProfile.objects.all():
            if profile.current_location:
                # Trigger the save method which now has the auto-categorization logic
                profile.save()
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated location categories for {count} user profiles.'))
        self.stdout.write(self.style.SUCCESS('Note: City data is now static in api/utils/location_helpers.py and does not need database population.'))
