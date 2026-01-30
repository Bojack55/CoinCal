"""
Management command to load Egyptian meals from the manifest JSON.
Populates Ingredient, EgyptianMeal, and MealRecipe tables.

Usage:
    python manage.py load_meals
    python manage.py load_meals --file=path/to/custom_manifest.json
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from api.models import Ingredient, EgyptianMeal, MealRecipe


# USDA nutrition data per 100g (ground truth)
USDA_NUTRITION_DATA = {
    # Grains & Starches
    'short_grain_rice': {'usda_id': '20044', 'calories': 360, 'protein': 6.5, 'carbs': 79.0, 'fat': 0.6, 'fiber': 1.3},
    'elbow_macaroni': {'usda_id': '20420', 'calories': 371, 'protein': 13.0, 'carbs': 75.0, 'fat': 1.5, 'fiber': 3.2},
    'penne_pasta': {'usda_id': '20420', 'calories': 371, 'protein': 13.0, 'carbs': 75.0, 'fat': 1.5, 'fiber': 3.2},
    'all_purpose_flour': {'usda_id': '20081', 'calories': 364, 'protein': 10.3, 'carbs': 76.3, 'fat': 1.0, 'fiber': 2.7},
    'pita_bread': {'usda_id': '18064', 'calories': 275, 'protein': 9.1, 'carbs': 55.7, 'fat': 1.2, 'fiber': 2.2},

    # Legumes
    'brown_lentils': {'usda_id': '16069', 'calories': 352, 'protein': 25.8, 'carbs': 60.0, 'fat': 1.1, 'fiber': 30.5},
    'chickpeas_cooked': {'usda_id': '16028', 'calories': 164, 'protein': 8.9, 'carbs': 27.4, 'fat': 2.6, 'fiber': 7.6},
    'fava_beans_cooked': {'usda_id': '16052', 'calories': 110, 'protein': 7.6, 'carbs': 19.7, 'fat': 0.4, 'fiber': 5.4},

    # Proteins
    'ground_beef': {'usda_id': '13364', 'calories': 254, 'protein': 17.2, 'carbs': 0, 'fat': 20.0, 'fiber': 0},

    # Vegetables
    'tomato_sauce': {'usda_id': '11529', 'calories': 29, 'protein': 1.3, 'carbs': 5.4, 'fat': 0.2, 'fiber': 1.5},
    'tomato_paste': {'usda_id': '11529', 'calories': 82, 'protein': 4.3, 'carbs': 18.9, 'fat': 0.5, 'fiber': 4.1},
    'tomato_diced': {'usda_id': '11529', 'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2},
    'onion_diced': {'usda_id': '11282', 'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1, 'fiber': 1.7},
    'onion_chopped': {'usda_id': '11282', 'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1, 'fiber': 1.7},
    'fried_onions': {'usda_id': '11215', 'calories': 349, 'protein': 4.5, 'carbs': 27.1, 'fat': 26.9, 'fiber': 2.5},
    'garlic_minced': {'usda_id': '11215', 'calories': 149, 'protein': 6.4, 'carbs': 33.1, 'fat': 0.5, 'fiber': 2.1},
    'green_pepper_diced': {'usda_id': '11333', 'calories': 20, 'protein': 0.9, 'carbs': 4.6, 'fat': 0.2, 'fiber': 1.7},
    'grape_leaves': {'usda_id': '11155', 'calories': 93, 'protein': 5.6, 'carbs': 17.3, 'fat': 2.0, 'fiber': 11.0},

    # Herbs & Spices
    'parsley_fresh': {'usda_id': '02028', 'calories': 36, 'protein': 3.0, 'carbs': 6.3, 'fat': 0.8, 'fiber': 3.3},
    'dill_fresh': {'usda_id': '02026', 'calories': 43, 'protein': 3.5, 'carbs': 7.0, 'fat': 1.1, 'fiber': 2.1},
    'cumin_ground': {'usda_id': '02014', 'calories': 375, 'protein': 17.8, 'carbs': 44.2, 'fat': 22.3, 'fiber': 10.5},
    'black_pepper': {'usda_id': '02030', 'calories': 251, 'protein': 10.4, 'carbs': 64.8, 'fat': 3.3, 'fiber': 25.3},
    'chili_pepper': {'usda_id': '02009', 'calories': 282, 'protein': 12.0, 'carbs': 56.6, 'fat': 17.3, 'fiber': 34.8},
    'chili_vinegar': {'usda_id': '02009', 'calories': 5, 'protein': 0.5, 'carbs': 1.0, 'fat': 0.1, 'fiber': 0.2},
    'nutmeg': {'usda_id': '02025', 'calories': 525, 'protein': 5.8, 'carbs': 49.3, 'fat': 36.3, 'fiber': 20.8},
    'salt': {'usda_id': '02047', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0},

    # Fats & Oils
    'vegetable_oil': {'usda_id': '04053', 'calories': 884, 'protein': 0, 'carbs': 0, 'fat': 100.0, 'fiber': 0},
    'olive_oil': {'usda_id': '04053', 'calories': 884, 'protein': 0, 'carbs': 0, 'fat': 100.0, 'fiber': 0},
    'butter': {'usda_id': '01001', 'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81.1, 'fiber': 0},

    # Dairy
    'whole_milk': {'usda_id': '01077', 'calories': 61, 'protein': 3.3, 'carbs': 4.8, 'fat': 3.3, 'fiber': 0},

    # Other
    'lemon_juice': {'usda_id': '09152', 'calories': 22, 'protein': 0.4, 'carbs': 6.9, 'fat': 0.2, 'fiber': 0.3},
}


class Command(BaseCommand):
    help = 'Load Egyptian meals from the manifest JSON into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to the manifest JSON file (default: fixtures/egyptian_meals_manifest.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Egyptian meals before loading'
        )

    def handle(self, *args, **options):
        # Determine file path
        if options['file']:
            manifest_path = Path(options['file'])
        else:
            manifest_path = Path(__file__).resolve().parent.parent.parent.parent / 'fixtures' / 'egyptian_meals_manifest.json'

        if not manifest_path.exists():
            raise CommandError(f'Manifest file not found: {manifest_path}')

        self.stdout.write(f'Loading meals from: {manifest_path}')

        # Load the manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # Clear existing data if requested
        if options['clear']:
            self.stdout.write('Clearing existing Egyptian meals...')
            MealRecipe.objects.all().delete()
            EgyptianMeal.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data'))

        # Step 1: Load/Update all ingredients
        self.stdout.write('\n--- Loading Ingredients ---')
        ingredient_count = 0
        for name, data in USDA_NUTRITION_DATA.items():
            ingredient, created = Ingredient.objects.update_or_create(
                name=name,
                defaults={
                    'usda_id': data['usda_id'],
                    'calories_per_100g': data['calories'],
                    'protein_per_100g': data['protein'],
                    'carbs_per_100g': data['carbs'],
                    'fat_per_100g': data['fat'],
                    'fiber_per_100g': data['fiber'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  [{status}] {name}')
            ingredient_count += 1

        self.stdout.write(self.style.SUCCESS(f'Loaded {ingredient_count} ingredients'))

        # Step 2: Load Egyptian meals
        self.stdout.write('\n--- Loading Egyptian Meals ---')
        meals_data = manifest.get('meals', [])
        meal_count = 0
        recipe_count = 0

        for meal_data in meals_data:
            meal_id = meal_data['id']
            
            # Create or update the meal
            meal, created = EgyptianMeal.objects.update_or_create(
                meal_id=meal_id,
                defaults={
                    'name_en': meal_data['name_en'],
                    'name_ar': meal_data.get('name_ar', ''),
                    'default_serving_weight_g': meal_data.get('serving_weight_g', 300),
                }
            )
            
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'\n  [{status}] {meal.name_en}')
            meal_count += 1

            # Clear existing recipe items for this meal
            MealRecipe.objects.filter(meal=meal).delete()

            # Add ingredients
            for ing_data in meal_data.get('ingredients', []):
                ingredient_name = ing_data['name']
                ratio = ing_data['ratio']
                percentage = ratio * 100  # Convert ratio (0-1) to percentage (0-100)

                try:
                    ingredient = Ingredient.objects.get(name=ingredient_name)
                    MealRecipe.objects.create(
                        meal=meal,
                        ingredient=ingredient,
                        percentage=percentage
                    )
                    self.stdout.write(f'    + {percentage:.1f}% {ingredient_name}')
                    recipe_count += 1
                except Ingredient.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'    ! Ingredient not found: {ingredient_name}'))

            # Show calculated nutrition for the meal
            nutrition = meal.calculate_nutrition()
            self.stdout.write(
                f'    → Nutrition (default serving): '
                f'{nutrition["calories"]} kcal, '
                f'P:{nutrition["protein"]}g, '
                f'C:{nutrition["carbs"]}g, '
                f'F:{nutrition["fat"]}g'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✓ Loaded {meal_count} meals with {recipe_count} recipe items'
        ))
