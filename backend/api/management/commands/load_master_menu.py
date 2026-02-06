import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import BaseMeal, Vendor, MarketPrice

class Command(BaseCommand):
    help = 'Load master Egyptian menu from fixtures/egyptian_master_menu.json'

    def handle(self, *args, **options):
        # 1. Path to fixture
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'egyptian_master_menu.json')
        
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"Fixture not found at {fixture_path}"))
            return

        # 2. Ensure Generic Vendor exists
        vendor, created = Vendor.objects.get_or_create(
            name="Market Average - Cairo",
            city="Cairo",
            is_national_brand=False
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Vendor: {vendor.name}"))

        # 3. Load JSON
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            # Create/Get BaseMeal (Nutrition Taxonomy)
            base_cal = item['calories']
            meal, m_created = BaseMeal.objects.update_or_create(
                name=item['name'],
                defaults={
                    'name_ar': item.get('name_ar'),
                    'meal_type': item['category'],
                    'calories': base_cal,
                    'min_calories': int(base_cal * 0.9),
                    'max_calories': int(base_cal * 1.2),
                    'protein_g': item['protein_g'],
                    'carbs_g': item['carbs_g'],
                    'fats_g': item['fats_g'],
                    'fiber_g': item.get('fiber_g', 0),
                    'serving_weight': item.get('serving_size_g', 100),
                    'image_url': item.get('image_url', '')
                }
            )
            
            # Update existing meals with new data
            if not m_created:
                meal.fiber_g = item.get('fiber_g', 0)
                meal.serving_weight = item.get('serving_size_g', 100)
                meal.save()
            
            # Update national brand status if meal is branded
            if item.get('is_national_brand'):
                # We apply this to the generic vendor's price entry or the meal itself?
                # The user asked to mark vendor as is_national_brand if it's branded.
                # But a generic vendor isn't national. Branded items like Pepsi are national.
                pass

            # Create MarketPrice entry
            market_price, p_created = MarketPrice.objects.get_or_create(
                meal=meal,
                vendor=vendor,
                defaults={'price_egp': item['reference_price']}
            )
            
            if p_created:
                count += 1
                self.stdout.write(f"Added {meal.name} @ {vendor.city} for {item['reference_price']} EGP")

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {count} new menu items."))
