from django.core.management.base import BaseCommand
from api.models import Ingredient

class Command(BaseCommand):
    help = 'Seed common Egyptian ingredients with 2026 prices'

    def handle(self, *args, **options):
        ingredients = [
            # Grains & Staple
            {"name": "Egyptian Rice", "unit": "GRAM", "price_per_unit": 0.035, "calories_per_unit": 1.3, "is_common": True},
            {"name": "Pasta (Macarona)", "unit": "GRAM", "price_per_unit": 0.025, "calories_per_unit": 1.5, "is_common": True},
            {"name": "Lentils", "unit": "GRAM", "price_per_unit": 0.045, "calories_per_unit": 1.1, "is_common": True},
            {"name": "Fava Beans (Foul)", "unit": "GRAM", "price_per_unit": 0.030, "calories_per_unit": 1.1, "is_common": True},
            
            # Vegetables
            {"name": "Tomato", "unit": "GRAM", "price_per_unit": 0.015, "calories_per_unit": 0.18, "is_common": True},
            {"name": "Potato", "unit": "GRAM", "price_per_unit": 0.020, "calories_per_unit": 0.77, "is_common": True},
            {"name": "Onion", "unit": "GRAM", "price_per_unit": 0.018, "calories_per_unit": 0.40, "is_common": True},
            {"name": "Garlic", "unit": "GRAM", "price_per_unit": 0.060, "calories_per_unit": 1.49, "is_common": True},
            {"name": "Cucumber", "unit": "GRAM", "price_per_unit": 0.012, "calories_per_unit": 0.15, "is_common": False},
            {"name": "Green Pepper", "unit": "GRAM", "price_per_unit": 0.025, "calories_per_unit": 0.20, "is_common": False},
            
            # Proteins
            {"name": "Minced Meat (Beef)", "unit": "GRAM", "price_per_unit": 0.450, "calories_per_unit": 2.5, "is_common": True},
            {"name": "Chicken Pane (Raw)", "unit": "GRAM", "price_per_unit": 0.220, "calories_per_unit": 1.65, "is_common": True},
            {"name": "Egg", "unit": "PIECE", "price_per_unit": 6.5, "calories_per_unit": 70.0, "is_common": True},
            
            # Fats & Oils
            {"name": "Vegetable Oil", "unit": "ML", "price_per_unit": 0.070, "calories_per_unit": 8.8, "is_common": True},
            {"name": "Ghee (Samma)", "unit": "GRAM", "price_per_unit": 0.120, "calories_per_unit": 9.0, "is_common": True},
            {"name": "Butter", "unit": "GRAM", "price_per_unit": 0.250, "calories_per_unit": 7.17, "is_common": False},
            
            # Others
            {"name": "Salt", "unit": "GRAM", "price_per_unit": 0.005, "calories_per_unit": 0.0, "is_common": True},
            {"name": "Black Pepper", "unit": "GRAM", "price_per_unit": 0.350, "calories_per_unit": 2.5, "is_common": True},
            {"name": "Cumin", "unit": "GRAM", "price_per_unit": 0.280, "calories_per_unit": 3.7, "is_common": True},
            {"name": "Sugar", "unit": "GRAM", "price_per_unit": 0.035, "calories_per_unit": 3.87, "is_common": True},
        ]

        count = 0
        for data in ingredients:
            ingredient, created = Ingredient.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                count += 1
            else:
                # Update existing if needed
                for key, value in data.items():
                    setattr(ingredient, key, value)
                ingredient.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(ingredients)} ingredients ({count} new).'))
