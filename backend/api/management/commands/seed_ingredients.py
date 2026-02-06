from django.core.management.base import BaseCommand
from api.models import Ingredient
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed ingredients with USDA-verified nutrition data (per 100g)'

    def handle(self, *args, **options):
        """
        All nutrition values are per 100g for consistency.
        USDA FoodData Central IDs included for traceability.
        Prices are 2026 Egyptian market rates (EGP per 100g).
        """
        ingredients = [
            # === GRAINS & STAPLES ===
            {
                "name": "White Rice (Long Grain, Cooked)",
                "name_ar": "أرز أبيض (طويل الحبة، مطبوخ)",
                "usda_id": "168878",
                "unit": "GRAM",
                "calories_per_100g": Decimal('130'),
                "protein_per_100g": Decimal('2.7'),
                "carbs_per_100g": Decimal('28.2'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('0.4'),
                "price_per_unit": Decimal('3.50'),  # ~35 EGP/kg
                "is_common": True
            },
            {
                "name": "Pasta (Macaroni, Cooked)",
                "name_ar": "مكرونة (مطبوخة)",
                "usda_id": "169736",
                "unit": "GRAM",
                "calories_per_100g": Decimal('157'),
                "protein_per_100g": Decimal('5.8'),
                "carbs_per_100g": Decimal('30.9'),
                "fat_per_100g": Decimal('0.9'),
                "fiber_per_100g": Decimal('1.8'),
                "price_per_unit": Decimal('2.50'),  # ~25 EGP/kg
                "is_common": True
            },
            {
                "name": "Lentils (Cooked)",
                "name_ar": "عدس (مطبوخ)",
                "usda_id": "172420",
                "unit": "GRAM",
                "calories_per_100g": Decimal('116'),
                "protein_per_100g": Decimal('9.0'),
                "carbs_per_100g": Decimal('20.1'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('7.9'),
                "price_per_unit": Decimal('4.50'),  # ~45 EGP/kg
                "is_common": True
            },
            {
                "name": "Fava Beans (Foul, Cooked)",
                "name_ar": "فول (مطبوخ)",
                "usda_id": "175200",
                "unit": "GRAM",
                "calories_per_100g": Decimal('110'),
                "protein_per_100g": Decimal('7.6'),
                "carbs_per_100g": Decimal('19.7'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('5.4'),
                "price_per_unit": Decimal('3.00'),  # ~30 EGP/kg
                "is_common": True
            },
            {
                "name": "Bread (Baladi, Egyptian)",
                "name_ar": "عيش بلدي",
                "usda_id": "172687",  # Generic white bread
                "unit": "GRAM",
                "calories_per_100g": Decimal('265'),
                "protein_per_100g": Decimal('8.9'),
                "carbs_per_100g": Decimal('49.0'),
                "fat_per_100g": Decimal('3.2'),
                "fiber_per_100g": Decimal('2.4'),
                "price_per_unit": Decimal('0.50'),  # ~5 EGP/kg
                "is_common": True
            },

            # === VEGETABLES ===
            {
                "name": "Tomato (Raw)",
                "name_ar": "طماطم",
                "usda_id": "170457",
                "unit": "GRAM",
                "calories_per_100g": Decimal('18'),
                "protein_per_100g": Decimal('0.9'),
                "carbs_per_100g": Decimal('3.9'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('1.2'),
                "price_per_unit": Decimal('1.50'),  # ~15 EGP/kg
                "is_common": True
            },
            {
                "name": "Potato (Boiled)",
                "name_ar": "بطاطس (مسلوقة)",
                "usda_id": "170026",
                "unit": "GRAM",
                "calories_per_100g": Decimal('87'),
                "protein_per_100g": Decimal('1.9'),
                "carbs_per_100g": Decimal('20.1'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('1.8'),
                "price_per_unit": Decimal('2.00'),  # ~20 EGP/kg
                "is_common": True
            },
            {
                "name": "Onion (Raw)",
                "name_ar": "بصل",
                "usda_id": "170000",
                "unit": "GRAM",
                "calories_per_100g": Decimal('40'),
                "protein_per_100g": Decimal('1.1'),
                "carbs_per_100g": Decimal('9.3'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('1.7'),
                "price_per_unit": Decimal('1.80'),  # ~18 EGP/kg
                "is_common": True
            },
            {
                "name": "Garlic (Raw)",
                "name_ar": "ثوم",
                "usda_id": "169230",
                "unit": "GRAM",
                "calories_per_100g": Decimal('149'),
                "protein_per_100g": Decimal('6.4'),
                "carbs_per_100g": Decimal('33.1'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('2.1'),
                "price_per_unit": Decimal('6.00'),  # ~60 EGP/kg
                "is_common": True
            },
            {
                "name": "Cucumber (Raw)",
                "name_ar": "خيار",
                "usda_id": "169225",
                "unit": "GRAM",
                "calories_per_100g": Decimal('15'),
                "protein_per_100g": Decimal('0.7'),
                "carbs_per_100g": Decimal('3.6'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('0.5'),
                "price_per_unit": Decimal('1.20'),  # ~12 EGP/kg
                "is_common": False
            },
            {
                "name": "Green Bell Pepper (Raw)",
                "name_ar": "فلفل أخضر",
                "usda_id": "170108",
                "unit": "GRAM",
                "calories_per_100g": Decimal('20'),
                "protein_per_100g": Decimal('0.9'),
                "carbs_per_100g": Decimal('4.6'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('1.7'),
                "price_per_unit": Decimal('2.50'),  # ~25 EGP/kg
                "is_common": False
            },
            {
                "name": "Eggplant (Cooked)",
                "name_ar": "باذنجان (مطبوخ)",
                "usda_id": "169228",
                "unit": "GRAM",
                "calories_per_100g": Decimal('35'),
                "protein_per_100g": Decimal('0.8'),
                "carbs_per_100g": Decimal('8.7'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('2.5'),
                "price_per_unit": Decimal('2.00'),  # ~20 EGP/kg
                "is_common": True
            },

            # === PROTEINS ===
            {
                "name": "Chicken Breast (Cooked, No Skin)",
                "name_ar": "صدور دجاج (مطبوخة)",
                "usda_id": "171477",
                "unit": "GRAM",
                "calories_per_100g": Decimal('165'),
                "protein_per_100g": Decimal('31.0'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('3.6'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('22.00'),  # ~220 EGP/kg
                "is_common": True
            },
            {
                "name": "Ground Beef (80% Lean, Cooked)",
                "name_ar": "لحم مفروم (مطبوخ)",
                "usda_id": "174032",
                "unit": "GRAM",
                "calories_per_100g": Decimal('254'),
                "protein_per_100g": Decimal('25.9'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('16.4'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('45.00'),  # ~450 EGP/kg
                "is_common": True
            },
            {
                "name": "Egg (Whole, Cooked)",
                "name_ar": "بيض (مسلوق)",
                "usda_id": "173424",
                "unit": "GRAM",
                "calories_per_100g": Decimal('155'),
                "protein_per_100g": Decimal('12.6'),
                "carbs_per_100g": Decimal('1.1'),
                "fat_per_100g": Decimal('10.6'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('13.00'),  # ~6.5 EGP per 50g egg
                "is_common": True
            },
            {
                "name": "Chickpeas (Cooked)",
                "name_ar": "حمص (حب، مطبوخ)",
                "usda_id": "173757",
                "unit": "GRAM",
                "calories_per_100g": Decimal('164'),
                "protein_per_100g": Decimal('8.9'),
                "carbs_per_100g": Decimal('27.4'),
                "fat_per_100g": Decimal('2.6'),
                "fiber_per_100g": Decimal('7.6'),
                "price_per_unit": Decimal('3.50'),  # ~35 EGP/kg
                "is_common": True
            },

            # === FATS & OILS ===
            {
                "name": "Olive Oil",
                "name_ar": "زيت زيتون",
                "usda_id": "171413",
                "unit": "ML",
                "calories_per_100g": Decimal('884'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('100.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('15.00'),  # ~150 EGP/L
                "is_common": True
            },
            {
                "name": "Vegetable Oil (Sunflower)",
                "name_ar": "زيت عباد الشمس",
                "usda_id": "172365",
                "unit": "ML",
                "calories_per_100g": Decimal('884'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('100.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('7.00'),  # ~70 EGP/L
                "is_common": True
            },
            {
                "name": "Butter (Salted)",
                "name_ar": "زبدة",
                "usda_id": "173410",
                "unit": "GRAM",
                "calories_per_100g": Decimal('717'),
                "protein_per_100g": Decimal('0.9'),
                "carbs_per_100g": Decimal('0.1'),
                "fat_per_100g": Decimal('81.1'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('25.00'),  # ~250 EGP/kg
                "is_common": False
            },
            {
                "name": "Ghee (Clarified Butter)",
                "name_ar": "سمن بلدي",
                "usda_id": "173412",
                "unit": "GRAM",
                "calories_per_100g": Decimal('876'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('99.5'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('12.00'),  # ~120 EGP/kg
                "is_common": True
            },

            # === DAIRY ===
            {
                "name": "Milk (Whole, 3.25% fat)",
                "name_ar": "حليب (كامل الدسم)",
                "usda_id": "174844",
                "unit": "ML",
                "calories_per_100g": Decimal('61'),
                "protein_per_100g": Decimal('3.2'),
                "carbs_per_100g": Decimal('4.8'),
                "fat_per_100g": Decimal('3.3'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('2.50'),  # ~25 EGP/L
                "is_common": True
            },
            {
                "name": "Feta Cheese",
                "name_ar": "جبنة فيتا",
                "usda_id": "173420",
                "unit": "GRAM",
                "calories_per_100g": Decimal('264'),
                "protein_per_100g": Decimal('14.2'),
                "carbs_per_100g": Decimal('4.1'),
                "fat_per_100g": Decimal('21.3'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('40.00'),  # ~400 EGP/kg
                "is_common": True
            },
            {
                "name": "Greek Yogurt (Plain, 2% fat)",
                "name_ar": "زبادي يوناني",
                "usda_id": "170903",
                "unit": "GRAM",
                "calories_per_100g": Decimal('73'),
                "protein_per_100g": Decimal('10.0'),
                "carbs_per_100g": Decimal('3.9'),
                "fat_per_100g": Decimal('2.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('5.00'),  # ~50 EGP/kg
                "is_common": False
            },

            # === SPICES & CONDIMENTS ===
            {
                "name": "Salt (Table)",
                "name_ar": "ملح",
                "usda_id": "172587",
                "unit": "GRAM",
                "calories_per_100g": Decimal('0'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('0.50'),  # ~5 EGP/kg
                "is_common": True
            },
            {
                "name": "Black Pepper (Ground)",
                "name_ar": "فلفل أسود",
                "usda_id": "170931",
                "unit": "GRAM",
                "calories_per_100g": Decimal('251'),
                "protein_per_100g": Decimal('10.4'),
                "carbs_per_100g": Decimal('63.9'),
                "fat_per_100g": Decimal('3.3'),
                "fiber_per_100g": Decimal('25.3'),
                "price_per_unit": Decimal('35.00'),  # ~350 EGP/kg
                "is_common": True
            },
            {
                "name": "Cumin (Ground)",
                "name_ar": "كمون",
                "usda_id": "171329",
                "unit": "GRAM",
                "calories_per_100g": Decimal('375'),
                "protein_per_100g": Decimal('17.8'),
                "carbs_per_100g": Decimal('44.2'),
                "fat_per_100g": Decimal('22.3'),
                "fiber_per_100g": Decimal('10.5'),
                "price_per_unit": Decimal('28.00'),  # ~280 EGP/kg
                "is_common": True
            },
            {
                "name": "Tahini (Sesame Paste)",
                "name_ar": "طحينة",
                "usda_id": "172456",
                "unit": "GRAM",
                "calories_per_100g": Decimal('595'),
                "protein_per_100g": Decimal('17.0'),
                "carbs_per_100g": Decimal('21.2'),
                "fat_per_100g": Decimal('53.8'),
                "fiber_per_100g": Decimal('9.3'),
                "price_per_unit": Decimal('8.00'),  # ~80 EGP/kg
                "is_common": True
            },

            # === FRUITS (Common in Egyptian cuisine) ===
            {
                "name": "Dates (Deglet Noor)",
                "name_ar": "تمر",
                "usda_id": "168191",
                "unit": "GRAM",
                "calories_per_100g": Decimal('282'),
                "protein_per_100g": Decimal('2.5'),
                "carbs_per_100g": Decimal('75.0'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('8.0'),
                "price_per_unit": Decimal('10.00'),  # ~100 EGP/kg
                "is_common": True
            },
            {
                "name": "Banana (Raw)",
                "name_ar": "موز",
                "usda_id": "173944",
                "unit": "GRAM",
                "calories_per_100g": Decimal('89'),
                "protein_per_100g": Decimal('1.1'),
                "carbs_per_100g": Decimal('22.8'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('2.6'),
                "price_per_unit": Decimal('3.00'),  # ~30 EGP/kg
                "is_common": True
            },

            # === SUGAR & SWEETENERS ===
            {
                "name": "Sugar (White, Granulated)",
                "name_ar": "سكر",
                "usda_id": "169655",
                "unit": "GRAM",
                "calories_per_100g": Decimal('387'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('100.0'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('3.50'),  # ~35 EGP/kg
                "is_common": True
            },

            # === FISH & SEAFOOD (NEW) ===
            {
                "name": "Tilapia Fillet (Raw)",
                "name_ar": "فيليه بلطي",
                "usda_id": "175168",
                "unit": "GRAM",
                "calories_per_100g": Decimal('96'),
                "protein_per_100g": Decimal('20.1'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('1.7'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('8.00'),
                "is_common": True
            },
            {
                "name": "Shrimp (Raw)",
                "name_ar": "جمبري (ني)",
                "usda_id": "175180",
                "unit": "GRAM",
                "calories_per_100g": Decimal('85'),
                "protein_per_100g": Decimal('20.1'),
                "carbs_per_100g": Decimal('0.2'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('25.00'),
                "is_common": False
            },
            {
                "name": "Salmon Fillet (Raw)",
                "name_ar": "فيليه سلمون",
                "usda_id": "175168",
                "unit": "GRAM",
                "calories_per_100g": Decimal('142'),
                "protein_per_100g": Decimal('19.8'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('6.3'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('40.00'),
                "is_common": False
            },
            {
                "name": "Tuna (Canned in Water)",
                "name_ar": "تونة (معلبة)",
                "usda_id": "175149",
                "unit": "GRAM",
                "calories_per_100g": Decimal('116'),
                "protein_per_100g": Decimal('25.5'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('0.8'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('12.00'),
                "is_common": True
            },

            # === MORE VEGETABLES (NEW) ===
            {
                "name": "Spinach (Raw)",
                "name_ar": "سبانخ",
                "usda_id": "168462",
                "unit": "GRAM",
                "calories_per_100g": Decimal('23'),
                "protein_per_100g": Decimal('2.9'),
                "carbs_per_100g": Decimal('3.6'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('2.2'),
                "price_per_unit": Decimal('2.50'),
                "is_common": True
            },
            {
                "name": "Zucchini (Raw)",
                "name_ar": "كوسة",
                "usda_id": "169291",
                "unit": "GRAM",
                "calories_per_100g": Decimal('17'),
                "protein_per_100g": Decimal('1.2'),
                "carbs_per_100g": Decimal('3.1'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('1.0'),
                "price_per_unit": Decimal('2.00'),
                "is_common": True
            },
            {
                "name": "Carrots (Raw)",
                "name_ar": "جزر",
                "usda_id": "170393",
                "unit": "GRAM",
                "calories_per_100g": Decimal('41'),
                "protein_per_100g": Decimal('0.9'),
                "carbs_per_100g": Decimal('9.6'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('2.8'),
                "price_per_unit": Decimal('1.50'),
                "is_common": True
            },
            {
                "name": "Cauliflower (Raw)",
                "name_ar": "قرنبيط",
                "usda_id": "169986",
                "unit": "GRAM",
                "calories_per_100g": Decimal('25'),
                "protein_per_100g": Decimal('1.9'),
                "carbs_per_100g": Decimal('4.9'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('2.0'),
                "price_per_unit": Decimal('2.00'),
                "is_common": True
            },
            {
                "name": "Broccoli (Raw)",
                "name_ar": "بروكلي",
                "usda_id": "170379",
                "unit": "GRAM",
                "calories_per_100g": Decimal('34'),
                "protein_per_100g": Decimal('2.8'),
                "carbs_per_100g": Decimal('6.6'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('2.6'),
                "price_per_unit": Decimal('3.00'),
                "is_common": False
            },
            {
                "name": "Lettuce (Romaine)",
                "name_ar": "خس",
                "usda_id": "169248",
                "unit": "GRAM",
                "calories_per_100g": Decimal('17'),
                "protein_per_100g": Decimal('1.2'),
                "carbs_per_100g": Decimal('3.3'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('2.1'),
                "price_per_unit": Decimal('2.50'),
                "is_common": True
            },
            {
                "name": "Cabbage (Green, Raw)",
                "name_ar": "كرنب",
                "usda_id": "169975",
                "unit": "GRAM",
                "calories_per_100g": Decimal('25'),
                "protein_per_100g": Decimal('1.3'),
                "carbs_per_100g": Decimal('5.8'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('2.5'),
                "price_per_unit": Decimal('1.50'),
                "is_common": True
            },
            {
                "name": "Okra (Raw)",
                "name_ar": "بامية",
                "usda_id": "169260",
                "unit": "GRAM",
                "calories_per_100g": Decimal('33'),
                "protein_per_100g": Decimal('1.9'),
                "carbs_per_100g": Decimal('7.5'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('3.2'),
                "price_per_unit": Decimal('2.50'),
                "is_common": True
            },

            # === LEGUMES & BEANS (NEW) ===
            {
                "name": "Kidney Beans (Cooked)",
                "name_ar": "فاصوليا حمراء",
                "usda_id": "173735",
                "unit": "GRAM",
                "calories_per_100g": Decimal('127'),
                "protein_per_100g": Decimal('8.7'),
                "carbs_per_100g": Decimal('22.8'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('6.4'),
                "price_per_unit": Decimal('3.00'),
                "is_common": True
            },
            {
                "name": "Black Beans (Cooked)",
                "name_ar": "فاصوليا سوداء",
                "usda_id": "173735",
                "unit": "GRAM",
                "calories_per_100g": Decimal('132'),
                "protein_per_100g": Decimal('8.9'),
                "carbs_per_100g": Decimal('23.7'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('8.7'),
                "price_per_unit": Decimal('3.50'),
                "is_common": False
            },
            {
                "name": "Green Peas (Cooked)",
                "name_ar": "بسلة",
                "usda_id": "170419",
                "unit": "GRAM",
                "calories_per_100g": Decimal('84'),
                "protein_per_100g": Decimal('5.4'),
                "carbs_per_100g": Decimal('15.6'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('5.5'),
                "price_per_unit": Decimal('2.50'),
                "is_common": True
            },

            # === NUTS & SEEDS (NEW) ===
            {
                "name": "Almonds (Raw)",
                "name_ar": "لوز",
                "usda_id": "170567",
                "unit": "GRAM",
                "calories_per_100g": Decimal('579'),
                "protein_per_100g": Decimal('21.2'),
                "carbs_per_100g": Decimal('21.6'),
                "fat_per_100g": Decimal('49.9'),
                "fiber_per_100g": Decimal('12.5'),
                "price_per_unit": Decimal('18.00'),
                "is_common": False
            },
            {
                "name": "Walnuts (Raw)",
                "name_ar": "عين جمل",
                "usda_id": "170187",
                "unit": "GRAM",
                "calories_per_100g": Decimal('654'),
                "protein_per_100g": Decimal('15.2'),
                "carbs_per_100g": Decimal('13.7'),
                "fat_per_100g": Decimal('65.2'),
                "fiber_per_100g": Decimal('6.7'),
                "price_per_unit": Decimal('22.00'),
                "is_common": False
            },
            {
                "name": "Peanuts (Raw)",
                "name_ar": "سوداني",
                "usda_id": "174263",
                "unit": "GRAM",
                "calories_per_100g": Decimal('567'),
                "protein_per_100g": Decimal('25.8'),
                "carbs_per_100g": Decimal('16.1'),
                "fat_per_100g": Decimal('49.2'),
                "fiber_per_100g": Decimal('8.5'),
                "price_per_unit": Decimal('8.00'),
                "is_common": True
            },
            {
                "name": "Cashews (Raw)",
                "name_ar": "كاجو",
                "usda_id": "170162",
                "unit": "GRAM",
                "calories_per_100g": Decimal('553'),
                "protein_per_100g": Decimal('18.2'),
                "carbs_per_100g": Decimal('30.2'),
                "fat_per_100g": Decimal('43.8'),
                "fiber_per_100g": Decimal('3.3'),
                "price_per_unit": Decimal('20.00'),
                "is_common": False
            },
            {
                "name": "Sunflower Seeds",
                "name_ar": "لب سوري",
                "usda_id": "170562",
                "unit": "GRAM",
                "calories_per_100g": Decimal('584'),
                "protein_per_100g": Decimal('20.8'),
                "carbs_per_100g": Decimal('20.0'),
                "fat_per_100g": Decimal('51.5'),
                "fiber_per_100g": Decimal('8.6'),
                "price_per_unit": Decimal('10.00'),
                "is_common": True
            },
            {
                "name": "Pumpkin Seeds",
                "name_ar": "لب أبيض",
                "usda_id": "170556",
                "unit": "GRAM",
                "calories_per_100g": Decimal('559'),
                "protein_per_100g": Decimal('30.2'),
                "carbs_per_100g": Decimal('10.7'),
                "fat_per_100g": Decimal('49.0'),
                "fiber_per_100g": Decimal('6.0'),
                "price_per_unit": Decimal('12.00'),
                "is_common": False
            },
            {
                "name": "Sesame Seeds",
                "name_ar": "سمسم",
                "usda_id": "170554",
                "unit": "GRAM",
                "calories_per_100g": Decimal('573'),
                "protein_per_100g": Decimal('17.7'),
                "carbs_per_100g": Decimal('23.4'),
                "fat_per_100g": Decimal('49.7'),
                "fiber_per_100g": Decimal('11.8'),
                "price_per_unit": Decimal('9.00'),
                "is_common": True
            },

            # === MORE FRUITS (NEW) ===
            {
                "name": "Apple (Raw)",
                "name_ar": "تفاح",
                "usda_id": "171688",
                "unit": "GRAM",
                "calories_per_100g": Decimal('52'),
                "protein_per_100g": Decimal('0.3'),
                "carbs_per_100g": Decimal('13.8'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('2.4'),
                "price_per_unit": Decimal('3.50'),
                "is_common": True
            },
            {
                "name": "Orange (Raw)",
                "name_ar": "برتقال",
                "usda_id": "169097",
                "unit": "GRAM",
                "calories_per_100g": Decimal('47'),
                "protein_per_100g": Decimal('0.9'),
                "carbs_per_100g": Decimal('11.8'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('2.4'),
                "price_per_unit": Decimal('2.50'),
                "is_common": True
            },
            {
                "name": "Mango (Raw)",
                "name_ar": "مانجو",
                "usda_id": "169910",
                "unit": "GRAM",
                "calories_per_100g": Decimal('60'),
                "protein_per_100g": Decimal('0.8'),
                "carbs_per_100g": Decimal('15.0'),
                "fat_per_100g": Decimal('0.4'),
                "fiber_per_100g": Decimal('1.6'),
                "price_per_unit": Decimal('4.00'),
                "is_common": True
            },
            {
                "name": "Watermelon (Raw)",
                "name_ar": "بطيخ",
                "usda_id": "169225",
                "unit": "GRAM",
                "calories_per_100g": Decimal('30'),
                "protein_per_100g": Decimal('0.6'),
                "carbs_per_100g": Decimal('7.5'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('0.4'),
                "price_per_unit": Decimal('1.50'),
                "is_common": True
            },
            {
                "name": "Grapes (Raw)",
                "name_ar": "عنب",
                "usda_id": "174682",
                "unit": "GRAM",
                "calories_per_100g": Decimal('69'),
                "protein_per_100g": Decimal('0.7'),
                "carbs_per_100g": Decimal('18.1'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('0.9'),
                "price_per_unit": Decimal('5.00'),
                "is_common": True
            },
            {
                "name": "Strawberry (Raw)",
                "name_ar": "فراولة",
                "usda_id": "167762",
                "unit": "GRAM",
                "calories_per_100g": Decimal('32'),
                "protein_per_100g": Decimal('0.7'),
                "carbs_per_100g": Decimal('7.7'),
                "fat_per_100g": Decimal('0.3'),
                "fiber_per_100g": Decimal('2.0'),
                "price_per_unit": Decimal('8.00'),
                "is_common": False
            },

            # === ADDITIONAL PROTEINS (NEW) ===
            {
                "name": "Turkey Breast (Cooked)",
                "name_ar": "صدر رومي (مدخن)",
                "usda_id": "171116",
                "unit": "GRAM",
                "calories_per_100g": Decimal('135'),
                "protein_per_100g": Decimal('30.1'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('0.7'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('25.00'),
                "is_common": False
            },
            {
                "name": "Lamb (Lean, Cooked)",
                "name_ar": "لحم ضاني",
                "usda_id": "174318",
                "unit": "GRAM",
                "calories_per_100g": Decimal('258'),
                "protein_per_100g": Decimal('25.6'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('16.5'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('50.00'),
                "is_common": True
            },
            {
                "name": "Beef Liver (Cooked)",
                "name_ar": "كبدة بتلو",
                "usda_id": "174352",
                "unit": "GRAM",
                "calories_per_100g": Decimal('191'),
                "protein_per_100g": Decimal('29.1'),
                "carbs_per_100g": Decimal('5.5'),
                "fat_per_100g": Decimal('5.3'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('15.00'),
                "is_common": True
            },
            {
                "name": "Chicken Liver (Cooked)",
                "name_ar": "كبدة فراخ",
                "usda_id": "171062",
                "unit": "GRAM",
                "calories_per_100g": Decimal('172'),
                "protein_per_100g": Decimal('24.5'),
                "carbs_per_100g": Decimal('0.9'),
                "fat_per_100g": Decimal('7.4'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('12.00'),
                "is_common": True
            },
            {
                "name": "Tofu (Firm)",
                "name_ar": "توفو",
                "usda_id": "174276",
                "unit": "GRAM",
                "calories_per_100g": Decimal('144'),
                "protein_per_100g": Decimal('17.3'),
                "carbs_per_100g": Decimal('2.8'),
                "fat_per_100g": Decimal('8.7'),
                "fiber_per_100g": Decimal('2.3'),
                "price_per_unit": Decimal('6.00'),
                "is_common": False
            },

            # === CONDIMENTS & HERBS (NEW) ===
            {
                "name": "Parsley (Fresh)",
                "name_ar": "بقدونس",
                "usda_id": "170116",
                "unit": "GRAM",
                "calories_per_100g": Decimal('36'),
                "protein_per_100g": Decimal('3.0'),
                "carbs_per_100g": Decimal('6.3'),
                "fat_per_100g": Decimal('0.8'),
                "fiber_per_100g": Decimal('3.3'),
                "price_per_unit": Decimal('3.00'),
                "is_common": True
            },
            {
                "name": "Coriander (Fresh)",
                "name_ar": "كزبرة",
                "usda_id": "170393",
                "unit": "GRAM",
                "calories_per_100g": Decimal('23'),
                "protein_per_100g": Decimal('2.1'),
                "carbs_per_100g": Decimal('3.7'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('2.8'),
                "price_per_unit": Decimal('3.00'),
                "is_common": True
            },
            {
                "name": "Dill (Fresh)",
                "name_ar": "شبت",
                "usda_id": "170393",
                "unit": "GRAM",
                "calories_per_100g": Decimal('43'),
                "protein_per_100g": Decimal('3.5'),
                "carbs_per_100g": Decimal('7.0'),
                "fat_per_100g": Decimal('1.1'),
                "fiber_per_100g": Decimal('2.1'),
                "price_per_unit": Decimal('4.00'),
                "is_common": False
            },
            {
                "name": "Lemon Juice (Fresh)",
                "name_ar": "عصير ليمون",
                "usda_id": "167746",
                "unit": "ML",
                "calories_per_100g": Decimal('22'),
                "protein_per_100g": Decimal('0.4'),
                "carbs_per_100g": Decimal('6.9'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('0.3'),
                "price_per_unit": Decimal('2.00'),
                "is_common": True
            },
            {
                "name": "Vinegar (White)",
                "name_ar": "خل",
                "usda_id": "172587",
                "unit": "ML",
                "calories_per_100g": Decimal('18'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.4'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('1.50'),
                "is_common": True
            },
            {
                "name": "Soy Sauce",
                "name_ar": "صويا صوص",
                "usda_id": "172681",
                "unit": "ML",
                "calories_per_100g": Decimal('53'),
                "protein_per_100g": Decimal('5.6'),
                "carbs_per_100g": Decimal('4.9'),
                "fat_per_100g": Decimal('0.1'),
                "fiber_per_100g": Decimal('0.8'),
                "price_per_unit": Decimal('3.50'),
                "is_common": False
            },
            {
                "name": "Tomato Paste",
                "name_ar": "صلصة طماطم",
                "usda_id": "170562",
                "unit": "GRAM",
                "calories_per_100g": Decimal('82'),
                "protein_per_100g": Decimal('4.3'),
                "carbs_per_100g": Decimal('18.9'),
                "fat_per_100g": Decimal('0.5'),
                "fiber_per_100g": Decimal('4.1'),
                "price_per_unit": Decimal('3.00'),
                "is_common": True
            },

            # === ADDITIONAL GRAINS (NEW) ===
            {
                "name": "Oats (Rolled, Dry)",
                "name_ar": "شوفان",
                "usda_id": "170362",
                "unit": "GRAM",
                "calories_per_100g": Decimal('389'),
                "protein_per_100g": Decimal('16.9'),
                "carbs_per_100g": Decimal('66.3'),
                "fat_per_100g": Decimal('6.9'),
                "fiber_per_100g": Decimal('10.6'),
                "price_per_unit": Decimal('4.00'),
                "is_common": True
            },
            {
                "name": "Quinoa (Cooked)",
                "name_ar": "كينوا",
                "usda_id": "168917",
                "unit": "GRAM",
                "calories_per_100g": Decimal('120'),
                "protein_per_100g": Decimal('4.4'),
                "carbs_per_100g": Decimal('21.3'),
                "fat_per_100g": Decimal('1.9'),
                "fiber_per_100g": Decimal('2.8'),
                "price_per_unit": Decimal('8.00'),
                "is_common": False
            },
            {
                "name": "Bulgur (Cooked)",
                "name_ar": "برغل",
                "usda_id": "168917",
                "unit": "GRAM",
                "calories_per_100g": Decimal('83'),
                "protein_per_100g": Decimal('3.1'),
                "carbs_per_100g": Decimal('18.6'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('4.5'),
                "price_per_unit": Decimal('3.50'),
                "is_common": True
            },
            {
                "name": "Couscous (Cooked)",
                "name_ar": "كسكسي",
                "usda_id": "168918",
                "unit": "GRAM",
                "calories_per_100g": Decimal('112'),
                "protein_per_100g": Decimal('3.8'),
                "carbs_per_100g": Decimal('23.2'),
                "fat_per_100g": Decimal('0.2'),
                "fiber_per_100g": Decimal('1.4'),
                "price_per_unit": Decimal('3.00'),
                "is_common": True
            },

            # === BEVERAGES (NEW) ===
            {
                "name": "Coffee (Brewed)",
                "name_ar": "قهوة",
                "usda_id": "171890",
                "unit": "ML",
                "calories_per_100g": Decimal('1'),
                "protein_per_100g": Decimal('0.1'),
                "carbs_per_100g": Decimal('0.0'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('1.00'),
                "is_common": True
            },
            {
                "name": "Tea (Black, Brewed)",
                "name_ar": "شاي",
                "usda_id": "171899",
                "unit": "ML",
                "calories_per_100g": Decimal('1'),
                "protein_per_100g": Decimal('0.0'),
                "carbs_per_100g": Decimal('0.3'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.0'),
                "price_per_unit": Decimal('0.50'),
                "is_common": True
            },
            {
                "name": "Honey",
                "name_ar": "عسل نحل",
                "usda_id": "169640",
                "unit": "GRAM",
                "calories_per_100g": Decimal('304'),
                "protein_per_100g": Decimal('0.3'),
                "carbs_per_100g": Decimal('82.4'),
                "fat_per_100g": Decimal('0.0'),
                "fiber_per_100g": Decimal('0.2'),
                "price_per_unit": Decimal('15.00'),
                "is_common": True
            },
        ]

        count = 0
        updated = 0
        for data in ingredients:
            defaults = data.copy()
            defaults.pop('name', None)
            
            ingredient, created = Ingredient.objects.update_or_create(
                name=data['name'],
                defaults=defaults
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Created: {ingredient.name}'))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f'🔄 Updated: {ingredient.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully processed {len(ingredients)} ingredients:\n'
            f'   • {count} newly created\n'
            f'   • {updated} updated with USDA data'
        ))
