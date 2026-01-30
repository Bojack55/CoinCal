from django.core.management.base import BaseCommand
from api.models import BaseMeal, Vendor, MarketPrice

class Command(BaseCommand):
    help = 'Seed core database with Cairo Average vendor and 10 items'

    def handle(self, *args, **options):
        # 1. Vendor
        cairo_vendor, _ = Vendor.objects.get_or_create(
            name="Market Average - Cairo",
            city="Cairo",
            is_national_brand=False
        )

        # 2. Core Items Data
        core_items = [
            {
                "name": "Koshary (Medium Plate)",
                "type": "Lunch",
                "cals": 850,
                "protein": 22,
                "carbs": 160,
                "fats": 12,
                "price": 65.0
            },
            {
                "name": "Foul Sandwich",
                "type": "Breakfast",
                "cals": 320,
                "protein": 14,
                "carbs": 45,
                "fats": 8,
                "price": 12.0
            },
            {
                "name": "Falafel Sandwich",
                "type": "Breakfast",
                "cals": 410,
                "protein": 12,
                "carbs": 55,
                "fats": 18,
                "price": 15.0
            },
            {
                "name": "Chicken Shawerma (Large)",
                "type": "Dinner",
                "cals": 650,
                "protein": 45,
                "carbs": 50,
                "fats": 25,
                "price": 120.0
            },
            {
                "name": "Beef Burger (Standard)",
                "type": "Dinner",
                "cals": 550,
                "protein": 30,
                "carbs": 40,
                "fats": 28,
                "price": 180.0
            },
            {
                "name": "Lentil Soup",
                "type": "Lunch",
                "cals": 250,
                "protein": 15,
                "carbs": 40,
                "fats": 5,
                "price": 45.0
            },
            {
                "name": "Grilled Chicken Breast (200g)",
                "type": "Lunch",
                "cals": 330,
                "protein": 62,
                "carbs": 0,
                "fats": 7,
                "price": 150.0
            },
            {
                "name": "Molokhia (Plain)",
                "type": "Lunch",
                "cals": 120,
                "protein": 5,
                "carbs": 15,
                "fats": 4,
                "price": 40.0
            },
            {
                "name": "Fruit Salad (Bowl)",
                "type": "Snack",
                "cals": 180,
                "protein": 2,
                "carbs": 40,
                "fats": 1,
                "price": 55.0
            },
            {
                "name": "Greek Salad",
                "type": "Dinner",
                "cals": 280,
                "protein": 8,
                "carbs": 12,
                "fats": 22,
                "price": 95.0
            },
        ]

        for item in core_items:
            meal, _ = BaseMeal.objects.get_or_create(
                name=item['name'],
                defaults={
                    'meal_type': item['type'],
                    'calories': item['cals'],
                    'protein_g': item['protein'],
                    'carbs_g': item['carbs'],
                    'fats_g': item['fats'],
                    'min_calories': int(item['cals'] * 0.9),
                    'max_calories': int(item['cals'] * 1.2),
                    'is_standard_portion': True
                }
            )
            
            MarketPrice.objects.get_or_create(
                meal=meal,
                vendor=cairo_vendor,
                defaults={'price_egp': item['price']}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded architect core data.'))
