from django.core.management.base import BaseCommand
from api.models import Ingredient, BaseMeal, MarketPrice, Vendor, MealLog, EgyptianMeal, RecipeItem
from django.db.models import Avg, Count
import json
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Rebuild CoinCal food database with accurate Egyptian market data (Feb 2026)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️  Starting CoinCal Database Rebuild..."))

        # 1. Backup
        self.backup_data()

        # 2. Clear Data
        self.clear_data()

        # 3. Populate Ingredients
        self.populate_ingredients()

        # 4. Populate Meals
        self.populate_meals()

        # 5. Validation
        self.validate_data()

    def backup_data(self):
        self.stdout.write("📦 Backing up existing data...")
        try:
            meals = list(BaseMeal.objects.all().values())
            ingredients = list(Ingredient.objects.all().values())
            
            with open('coincal_backup_meals.json', 'w', encoding='utf-8') as f:
                json.dump(meals, f, indent=2, default=str)
            with open('coincal_backup_ingredients.json', 'w', encoding='utf-8') as f:
                json.dump(ingredients, f, indent=2, default=str)
                
            self.stdout.write(f"   -> Backed up {len(meals)} meals and {len(ingredients)} ingredients.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   -> Backup failed: {str(e)}"))

    def clear_data(self):
        self.stdout.write("🧹 Clearing existing data...")
        
        # Unlink MealLogs to preserve history but detach from deleted items
        MealLog.objects.all().update(meal=None, egyptian_meal=None)
        
        # Delete dependent data first
        RecipeItem.objects.all().delete()
        # MarketPrice.objects.all().delete() # Deprecated

        
        # Delete main data
        del_counts = {}
        _, del_counts = BaseMeal.objects.all().delete()
        self.stdout.write(f"   -> Deleted BaseMeals: {del_counts.get('api.BaseMeal', 0)}")
        
        _, del_counts = EgyptianMeal.objects.all().delete() # dependent on Ingredients
        self.stdout.write(f"   -> Deleted EgyptianMeals: {del_counts.get('api.EgyptianMeal', 0)}")

        _, del_counts = Ingredient.objects.all().delete()
        self.stdout.write(f"   -> Deleted Ingredients: {del_counts.get('api.Ingredient', 0)}")

    def populate_ingredients(self):
        self.stdout.write("🥬 Creating Ingredients...")
        
        ingredients_data = [
            # GRAINS & STARCHES
            {"name": "White Rice", "name_ar": "أرز أبيض", "price": 35, "unit": "GRAM", "cal": 130, "p": 2.7, "c": 28, "f": 0.3, "fiber": 0.4},
            {"name": "Egyptian Rice", "name_ar": "أرز مصري", "price": 40, "unit": "GRAM", "cal": 135, "p": 2.8, "c": 29, "f": 0.4, "fiber": 0.5},
            {"name": "Pasta", "name_ar": "مكرونة", "price": 45, "unit": "GRAM", "cal": 157, "p": 5.8, "c": 31, "f": 0.9, "fiber": 1.8}, 
            {"name": "Vermicelli", "name_ar": "شعيرية", "price": 50, "unit": "GRAM", "cal": 150, "p": 5, "c": 30, "f": 0.5, "fiber": 1}, 
            {"name": "Bulgur", "name_ar": "برغل", "price": 40, "unit": "GRAM", "cal": 83, "p": 3, "c": 18, "f": 0.2, "fiber": 4.5},
            {"name": "Freekeh", "name_ar": "فريكة", "price": 60, "unit": "GRAM", "cal": 340, "p": 14, "c": 72, "f": 2.5, "fiber": 11}, 
            {"name": "Oats", "name_ar": "شوفان", "price": 90, "unit": "GRAM", "cal": 389, "p": 16.9, "c": 66, "f": 6.9, "fiber": 10.6}, 
            {"name": "Couscous", "name_ar": "كسكسي", "price": 70, "unit": "GRAM", "cal": 112, "p": 3.8, "c": 23, "f": 0.2, "fiber": 1.4}, 
            {"name": "White Flour", "name_ar": "دقيق أبيض", "price": 30, "unit": "GRAM", "cal": 364, "p": 10, "c": 76, "f": 1, "fiber": 2.7},
            {"name": "Corn Flour", "name_ar": "دقيق ذرة", "price": 35, "unit": "GRAM", "cal": 365, "p": 9, "c": 74, "f": 3, "fiber": 7},
            {"name": "Semolina", "name_ar": "سميد", "price": 40, "unit": "GRAM", "cal": 360, "p": 12, "c": 72, "f": 1, "fiber": 3.9},
            {"name": "White Bread (Fino)", "name_ar": "عيش فينو", "price": 5, "unit": "PIECE", "cal": 150, "p": 5, "c": 28, "f": 2, "fiber": 1}, 
            {"name": "Baladi Bread", "name_ar": "عيش بلدي", "price": 3, "unit": "PIECE", "cal": 240, "p": 9, "c": 49, "f": 1.5, "fiber": 4}, 
            {"name": "Shami Bread", "name_ar": "عيش شامي", "price": 4, "unit": "PIECE", "cal": 180, "p": 6, "c": 35, "f": 1.5, "fiber": 1.5},
            {"name": "Plain Crackers", "name_ar": "كراكرز سادة", "price": 50, "unit": "PIECE", "cal": 440, "p": 9, "c": 68, "f": 14, "fiber": 3}, 

            # PROTEINS
            {"name": "Eggs", "name_ar": "بيض", "price": 5, "unit": "PIECE", "cal": 72, "p": 6, "c": 0.4, "f": 5, "fiber": 0}, 
            {"name": "Chicken Breast", "name_ar": "صدور فراخ", "price": 210, "unit": "GRAM", "cal": 165, "p": 31, "c": 0, "f": 3.6, "fiber": 0},
            {"name": "Chicken Thighs", "name_ar": "أفخاد فراخ", "price": 130, "unit": "GRAM", "cal": 209, "p": 26, "c": 0, "f": 10.9, "fiber": 0},
            {"name": "Whole Chicken", "name_ar": "فرخة كاملة", "price": 95, "unit": "GRAM", "cal": 215, "p": 18, "c": 0, "f": 15, "fiber": 0},
            {"name": "Chicken Liver", "name_ar": "كبدة فراخ", "price": 120, "unit": "GRAM", "cal": 167, "p": 24, "c": 0.9, "f": 6.5, "fiber": 0},
            {"name": "Beef Liver", "name_ar": "كبدة بقري", "price": 280, "unit": "GRAM", "cal": 135, "p": 20, "c": 3.9, "f": 3.6, "fiber": 0},
            {"name": "Ground Beef", "name_ar": "لحمة مفرومة", "price": 400, "unit": "GRAM", "cal": 250, "p": 26, "c": 0, "f": 17, "fiber": 0},
            {"name": "Beef Stew Meat", "name_ar": "لحمة للطبخ", "price": 450, "unit": "GRAM", "cal": 250, "p": 26, "c": 0, "f": 15, "fiber": 0},
            {"name": "Canned Tuna", "name_ar": "تونة معلبة", "price": 280, "unit": "GRAM", "cal": 116, "p": 25, "c": 0, "f": 1, "fiber": 0}, 
            {"name": "Canned Sardines", "name_ar": "سردين معلب", "price": 200, "unit": "GRAM", "cal": 208, "p": 24, "c": 0, "f": 11, "fiber": 0}, 
            {"name": "Frozen Fish Fillet", "name_ar": "فيليه سمك", "price": 180, "unit": "GRAM", "cal": 90, "p": 19, "c": 0, "f": 1, "fiber": 0},
            {"name": "Tilapia", "name_ar": "بلطي", "price": 90, "unit": "GRAM", "cal": 96, "p": 20, "c": 0, "f": 1.7, "fiber": 0},
            {"name": "Fava Beans (Dried)", "name_ar": "فول ناشف", "price": 45, "unit": "GRAM", "cal": 341, "p": 26, "c": 58, "f": 1.5, "fiber": 25},
            {"name": "Fava Beans (Canned)", "name_ar": "فول معلب", "price": 60, "unit": "GRAM", "cal": 110, "p": 7.6, "c": 19, "f": 0.4, "fiber": 5}, 
            {"name": "Red Lentils", "name_ar": "عدس أحمر", "price": 65, "unit": "GRAM", "cal": 358, "p": 24, "c": 63, "f": 2, "fiber": 11},
            {"name": "Brown Lentils", "name_ar": "عدس بني", "price": 60, "unit": "GRAM", "cal": 116, "p": 9, "c": 20, "f": 0.4, "fiber": 8},
            {"name": "Chickpeas (Dried)", "name_ar": "حمص ناشف", "price": 80, "unit": "GRAM", "cal": 378, "p": 20, "c": 63, "f": 6, "fiber": 12},
            {"name": "Chickpeas (Canned)", "name_ar": "حمص معلب", "price": 100, "unit": "GRAM", "cal": 119, "p": 7, "c": 27, "f": 2.5, "fiber": 7}, 
            {"name": "White Beans", "name_ar": "فاصوليا بيضا", "price": 70, "unit": "GRAM", "cal": 333, "p": 23, "c": 60, "f": 0.8, "fiber": 15},
            {"name": "Kidney Beans", "name_ar": "فاصوليا حمرا", "price": 85, "unit": "GRAM", "cal": 333, "p": 24, "c": 60, "f": 0.8, "fiber": 15},
            {"name": "Peanuts", "name_ar": "فول سوداني", "price": 120, "unit": "GRAM", "cal": 567, "p": 26, "c": 16, "f": 49, "fiber": 9},

            # DAIRY
            {"name": "Fresh Milk", "name_ar": "لبن طازة", "price": 45, "unit": "ML", "cal": 60, "p": 3.2, "c": 4.5, "f": 3.25, "fiber": 0}, 
            {"name": "Yogurt", "name_ar": "زبادي", "price": 65, "unit": "GRAM", "cal": 61, "p": 3.5, "c": 4.7, "f": 3.3, "fiber": 0}, 
            {"name": "White Cheese", "name_ar": "جبنة بيضا", "price": 160, "unit": "GRAM", "cal": 260, "p": 12, "c": 2, "f": 22, "fiber": 0},
            {"name": "Rumi Cheese", "name_ar": "جبنة رومي", "price": 350, "unit": "GRAM", "cal": 380, "p": 25, "c": 2, "f": 30, "fiber": 0},
            {"name": "Feta Cheese", "name_ar": "جبنة فيتا", "price": 180, "unit": "GRAM", "cal": 264, "p": 14, "c": 4, "f": 21, "fiber": 0},
            {"name": "Butter", "name_ar": "زبدة", "price": 450, "unit": "GRAM", "cal": 717, "p": 0.8, "c": 0.1, "f": 81, "fiber": 0}, 

            # VEGETABLES
            {"name": "Tomatoes", "name_ar": "طماطم", "price": 25, "unit": "GRAM", "cal": 18, "p": 0.9, "c": 3.9, "f": 0.2, "fiber": 1.2},
            {"name": "Cucumbers", "name_ar": "خيار", "price": 20, "unit": "GRAM", "cal": 15, "p": 0.7, "c": 3.6, "f": 0.1, "fiber": 0.5},
            {"name": "Onions", "name_ar": "بصل", "price": 20, "unit": "GRAM", "cal": 40, "p": 1.1, "c": 9.3, "f": 0.1, "fiber": 1.7},
            {"name": "Potatoes", "name_ar": "بطاطس", "price": 25, "unit": "GRAM", "cal": 77, "p": 2, "c": 17, "f": 0.1, "fiber": 2.2},
            {"name": "Sweet Potatoes", "name_ar": "بطاطا", "price": 20, "unit": "GRAM", "cal": 86, "p": 1.6, "c": 20, "f": 0.1, "fiber": 3},
            {"name": "Eggplant", "name_ar": "باذنجان", "price": 15, "unit": "GRAM", "cal": 25, "p": 1, "c": 6, "f": 0.2, "fiber": 3},
            {"name": "Zucchini", "name_ar": "كوسة", "price": 30, "unit": "GRAM", "cal": 17, "p": 1.2, "c": 3, "f": 0.3, "fiber": 1},
            {"name": "Bell Peppers", "name_ar": "فلفل رومي", "price": 40, "unit": "GRAM", "cal": 20, "p": 0.9, "c": 4.6, "f": 0.2, "fiber": 1.7},
            {"name": "Rice (Cooked)", "name_ar": "أرز مطبوخ", "price": 35, "unit": "GRAM", "cal": 130, "p": 2.7, "c": 28, "f": 0.3, "fiber": 0.4},
            {"name": "Molokhia Leaves", "name_ar": "ملوخية", "price": 25, "unit": "GRAM", "cal": 34, "p": 4, "c": 6, "f": 0.3, "fiber": 2.5}, 
            {"name": "Green Beans", "name_ar": "فاصوليا خضرا", "price": 25, "unit": "GRAM", "cal": 31, "p": 1.8, "c": 7, "f": 0.2, "fiber": 2.7},
            {"name": "Peas", "name_ar": "بسلة", "price": 30, "unit": "GRAM", "cal": 81, "p": 5, "c": 14, "f": 0.4, "fiber": 5},
            {"name": "Spinach", "name_ar": "سبانخ", "price": 15, "unit": "GRAM", "cal": 23, "p": 2.9, "c": 3.6, "f": 0.4, "fiber": 2.2},
            {"name": "Cabbage", "name_ar": "كرنب", "price": 10, "unit": "GRAM", "cal": 25, "p": 1.3, "c": 6, "f": 0.1, "fiber": 2.5},
            {"name": "Red Cabbage", "name_ar": "كرنب أحمر", "price": 15, "unit": "GRAM", "cal": 31, "p": 1.4, "c": 7, "f": 0.1, "fiber": 2.1},
            {"name": "Cauliflower", "name_ar": "قرنبيط", "price": 20, "unit": "GRAM", "cal": 25, "p": 1.9, "c": 5, "f": 0.3, "fiber": 2},
            {"name": "Broccoli", "name_ar": "بروكلي", "price": 40, "unit": "GRAM", "cal": 34, "p": 2.8, "c": 7, "f": 0.4, "fiber": 2.6},
            {"name": "Lettuce", "name_ar": "خس", "price": 10, "unit": "GRAM", "cal": 15, "p": 1.4, "c": 2.9, "f": 0.2, "fiber": 1.3},
            {"name": "Garlic", "name_ar": "توم", "price": 40, "unit": "GRAM", "cal": 149, "p": 6.4, "c": 33, "f": 0.5, "fiber": 2.1},
            {"name": "Carrot", "name_ar": "جزر", "price": 15, "unit": "GRAM", "cal": 41, "p": 0.9, "c": 10, "f": 0.2, "fiber": 2.8},
            {"name": "Parsley", "name_ar": "بقدونس", "price": 10, "unit": "GRAM", "cal": 36, "p": 3, "c": 6, "f": 0.8, "fiber": 3.3},
            {"name": "Dill", "name_ar": "شبت", "price": 10, "unit": "GRAM", "cal": 43, "p": 3.5, "c": 7, "f": 1.1, "fiber": 2.1},
            {"name": "Cilantro", "name_ar": "كزبرة خضرا", "price": 10, "unit": "GRAM", "cal": 23, "p": 2.1, "c": 3.7, "f": 0.5, "fiber": 2.8},
            {"name": "Radish", "name_ar": "فجل", "price": 10, "unit": "GRAM", "cal": 16, "p": 0.7, "c": 3.4, "f": 0.1, "fiber": 1.6},
            {"name": "Beetroot", "name_ar": "بنجر", "price": 15, "unit": "GRAM", "cal": 43, "p": 1.6, "c": 10, "f": 0.2, "fiber": 2.8},
            {"name": "Arugula (Rocca)", "name_ar": "جرجير", "price": 10, "unit": "GRAM", "cal": 25, "p": 2.6, "c": 3.7, "f": 0.7, "fiber": 1.6}, 

            # FRUITS
            {"name": "Bananas", "name_ar": "موز", "price": 30, "unit": "GRAM", "cal": 89, "p": 1.1, "c": 23, "f": 0.3, "fiber": 2.6},
            {"name": "Apples", "name_ar": "تفاح", "price": 80, "unit": "GRAM", "cal": 52, "p": 0.3, "c": 14, "f": 0.2, "fiber": 2.4},
            {"name": "Oranges", "name_ar": "برتقان", "price": 20, "unit": "GRAM", "cal": 47, "p": 0.9, "c": 12, "f": 0.1, "fiber": 2.4},
            {"name": "Dates", "name_ar": "تمر", "price": 100, "unit": "GRAM", "cal": 282, "p": 2.5, "c": 75, "f": 0.4, "fiber": 8},
            {"name": "Watermelon", "name_ar": "بطيخ", "price": 15, "unit": "GRAM", "cal": 30, "p": 0.6, "c": 8, "f": 0.2, "fiber": 0.4},
            {"name": "Grapes (Red)", "name_ar": "عنب أحمر", "price": 35, "unit": "GRAM", "cal": 69, "p": 0.7, "c": 18, "f": 0.2, "fiber": 0.9},
            {"name": "Grapes (Green)", "name_ar": "عنب بناتي", "price": 40, "unit": "GRAM", "cal": 69, "p": 0.7, "c": 18, "f": 0.2, "fiber": 0.9},
            {"name": "Grapes", "name_ar": "عنب", "price": 40, "unit": "GRAM", "cal": 69, "p": 0.7, "c": 18, "f": 0.2, "fiber": 0.9},
            {"name": "Strawberry", "name_ar": "فراولة", "price": 25, "unit": "GRAM", "cal": 32, "p": 0.7, "c": 7.7, "f": 0.3, "fiber": 2},
            {"name": "Peach", "name_ar": "خوخ", "price": 30, "unit": "GRAM", "cal": 39, "p": 0.9, "c": 10, "f": 0.3, "fiber": 1.5},
            {"name": "Plum", "name_ar": "برقوق", "price": 35, "unit": "GRAM", "cal": 46, "p": 0.7, "c": 11, "f": 0.3, "fiber": 1.4},
            {"name": "Cantaloupe", "name_ar": "كانتلوب", "price": 15, "unit": "GRAM", "cal": 34, "p": 0.8, "c": 8, "f": 0.2, "fiber": 0.9},
            {"name": "Fig", "name_ar": "تين", "price": 40, "unit": "GRAM", "cal": 74, "p": 0.8, "c": 19, "f": 0.3, "fiber": 2.9},
            {"name": "Guava", "name_ar": "جوافة", "price": 20, "unit": "GRAM", "cal": 68, "p": 2.6, "c": 14, "f": 1, "fiber": 5.4},
            {"name": "Pear", "name_ar": "كمثرى", "price": 40, "unit": "GRAM", "cal": 57, "p": 0.4, "c": 15, "f": 0.1, "fiber": 3.1},
            {"name": "Apricot", "name_ar": "مشمش", "price": 45, "unit": "GRAM", "cal": 48, "p": 1.4, "c": 11, "f": 0.4, "fiber": 2},
            {"name": "Cherry", "name_ar": "كريز", "price": 120, "unit": "GRAM", "cal": 50, "p": 1, "c": 12, "f": 0.3, "fiber": 1.6},
            {"name": "Kiwi", "name_ar": "كيوي", "price": 80, "unit": "GRAM", "cal": 61, "p": 1.1, "c": 15, "f": 0.5, "fiber": 3},
            {"name": "Pomegranate", "name_ar": "رمان", "price": 25, "unit": "GRAM", "cal": 83, "p": 1.7, "c": 19, "f": 1.2, "fiber": 4},
            {"name": "Mandarin", "name_ar": "يوسفي", "price": 15, "unit": "GRAM", "cal": 53, "p": 0.8, "c": 13, "f": 0.3, "fiber": 1.8},
            {"name": "Mango", "name_ar": "مانجو", "price": 35, "unit": "GRAM", "cal": 60, "p": 0.8, "c": 15, "f": 0.4, "fiber": 1.6},

            # CONDIMENTS
            {"name": "Tahini", "name_ar": "طحينة", "price": 180, "unit": "GRAM", "cal": 595, "p": 17, "c": 21, "f": 53, "fiber": 9}, 
            {"name": "Olive Oil", "name_ar": "زيت زيتون", "price": 350, "unit": "ML", "cal": 884, "p": 0, "c": 0, "f": 100, "fiber": 0},
            {"name": "Vegetable Oil", "name_ar": "زيت نباتي", "price": 110, "unit": "ML", "cal": 884, "p": 0, "c": 0, "f": 100, "fiber": 0},
            {"name": "Tomato Paste", "name_ar": "معجون طماطم", "price": 80, "unit": "GRAM", "cal": 82, "p": 4, "c": 19, "f": 0.5, "fiber": 4}, 
            {"name": "Honey", "name_ar": "عسل نحل", "price": 250, "unit": "GRAM", "cal": 304, "p": 0.3, "c": 82, "f": 0, "fiber": 0.2},
            {"name": "Yeast", "name_ar": "خميرة", "price": 60, "unit": "GRAM", "cal": 325, "p": 40, "c": 41, "f": 7.6, "fiber": 27},
            {"name": "Baking Powder", "name_ar": "بيكينج بودر", "price": 100, "unit": "GRAM", "cal": 53, "p": 0, "c": 28, "f": 0, "fiber": 0},
            {"name": "Vanilla", "name_ar": "فانيليا", "price": 300, "unit": "GRAM", "cal": 288, "p": 0.1, "c": 13, "f": 0.1, "fiber": 0},
            {"name": "Vinegar", "name_ar": "خل", "price": 15, "unit": "ML", "cal": 18, "p": 0, "c": 0, "f": 0, "fiber": 0},

            # SUPERMARKET SNACKS
            # Chips
            {"name": "Chipsy (Salt)", "name_ar": "شيبسي ملح", "price": 10, "unit": "PIECE", "cal": 530, "p": 7, "c": 53, "f": 34, "fiber": 4}, # Per 100g, Unit=Bag ~50g usually but price is per piece? Let's assume Unit=PIECE and cal is per 100g.
            {"name": "Chipsy (Chili & Lemon)", "name_ar": "شيبسي شطة وليمون", "price": 10, "unit": "PIECE", "cal": 540, "p": 6, "c": 54, "f": 33, "fiber": 3},
            {"name": "Doritos (Nacho Cheese)", "name_ar": "دوريتوس جبنة", "price": 15, "unit": "PIECE", "cal": 500, "p": 7, "c": 58, "f": 26, "fiber": 5},
            {"name": "Tiger Chips (Kebab)", "name_ar": "تايجر كباب", "price": 10, "unit": "PIECE", "cal": 530, "p": 6.5, "c": 52, "f": 35, "fiber": 3.5},
            
            # Biscuits & Cakes
            {"name": "Oreo (Standard)", "name_ar": "أوريو", "price": 15, "unit": "PIECE", "cal": 480, "p": 5, "c": 68, "f": 20, "fiber": 2}, # Per 100g
            {"name": "Biskrem", "name_ar": "بسكريم", "price": 10, "unit": "PIECE", "cal": 450, "p": 6, "c": 70, "f": 18, "fiber": 2},
            {"name": "Bimbo", "name_ar": "بيمبو", "price": 10, "unit": "PIECE", "cal": 470, "p": 6, "c": 65, "f": 22, "fiber": 2},
            {"name": "Molto (Chocolate)", "name_ar": "مولتو شوكولاتة", "price": 20, "unit": "PIECE", "cal": 400, "p": 7, "c": 45, "f": 20, "fiber": 2},
            {"name": "Molto (Pate Feta)", "name_ar": "مولتو جبنة فيتا", "price": 15, "unit": "PIECE", "cal": 380, "p": 8, "c": 42, "f": 18, "fiber": 2},
            {"name": "HoHos (Twinkies)", "name_ar": "هوهوز", "price": 10, "unit": "PIECE", "cal": 410, "p": 4, "c": 60, "f": 16, "fiber": 0},
            
            # Chocolates
            {"name": "Cadbury Dairy Milk", "name_ar": "كادبوري ديري ميلك", "price": 35, "unit": "PIECE", "cal": 530, "p": 7, "c": 57, "f": 30, "fiber": 2},
            {"name": "KitKat (4 Fingers)", "name_ar": "كيت كات", "price": 25, "unit": "PIECE", "cal": 500, "p": 7, "c": 62, "f": 25, "fiber": 2},
            {"name": "Galaxy (Smooth Milk)", "name_ar": "جالاكسي", "price": 40, "unit": "PIECE", "cal": 540, "p": 6, "c": 56, "f": 32, "fiber": 0},
            
            # Drinks
            {"name": "Pepsi (Can)", "name_ar": "بيبسي كانز", "price": 20, "unit": "PIECE", "cal": 41, "p": 0, "c": 11, "f": 0, "fiber": 0}, # Cal per 100ml
            {"name": "Coca-Cola (Can)", "name_ar": "كوكاكولا كانز", "price": 20, "unit": "PIECE", "cal": 42, "p": 0, "c": 10.6, "f": 0, "fiber": 0},
            {"name": "Juhayna Juice (Box)", "name_ar": "عصير جهينة", "price": 15, "unit": "PIECE", "cal": 45, "p": 0.5, "c": 11, "f": 0, "fiber": 0},
            {"name": "Beyti Juice (Box)", "name_ar": "عصير بيتي", "price": 15, "unit": "PIECE", "cal": 50, "p": 0.5, "c": 12, "f": 0, "fiber": 0},
            
            # Instant Meals
            {"name": "Indomie (Chicken)", "name_ar": "إندومي فراخ", "price": 15, "unit": "PIECE", "cal": 450, "p": 9, "c": 62, "f": 18, "fiber": 2},
            {"name": "Indomie (Vegetables)", "name_ar": "إندومي خضار", "price": 15, "unit": "PIECE", "cal": 440, "p": 8, "c": 63, "f": 17, "fiber": 2},
        ]

        count = 0
        for data in ingredients_data:
            # normalize unit price to per 100g if unit is GRAM/ML
            # The list provided prices per KG or per unit.
            # My logic below assumes input price is PER KG if GRAM/ML
            # Special handling for PIECE
            
            price_per_100g = Decimal(0)
            if data['unit'] in ['GRAM', 'ML']:
                # Input price is EGP/KG so /10 is per 100g
                price_per_100g = Decimal(data['price']) / 10
            else:
                 # Piece price is absolute
                 pass
            
            # Create Ingredient
            ing = Ingredient.objects.create(
                name=data['name'],
                name_ar=data['name_ar'],
                unit=data['unit'],
                calories_per_100g=data['cal'],
                protein_per_100g=data['p'],
                carbs_per_100g=data['c'],
                fat_per_100g=data['f'],
                fiber_per_100g=data['fiber'],
                base_price=data['price'] if data['unit'] == 'PIECE' else price_per_100g,
                # Legacy fields
                calories_per_unit=data['cal'],
                is_common=True
            )
            count += 1
            
        self.stdout.write(f"   -> Created {count} ingredients.")

    def populate_meals(self):
        self.stdout.write("🍽️ Creating Meals (BaseMeal + Prices)...")
        
        # Ensure Vendor exists
        vendor, _ = Vendor.objects.get_or_create(
            name="Market Average - Cairo",
            defaults={'city': 'Cairo', 'is_national_brand': True}
        )

        meals_data = [
            # BREAKFAST (15)
            {"n": "Foul Medames (Plain)", "n_ar": "فول مدمس سادة", "cat": "Breakfast", "p": 25, "g": 250, "c": 280, "pr": 14, "cb": 40, "ft": 5},
            {"n": "Foul with Oil & Lemon", "n_ar": "فول بالزيت والليمون", "cat": "Breakfast", "p": 30, "g": 260, "c": 350, "pr": 14, "cb": 40, "ft": 15},
            {"n": "Foul with Tahini", "n_ar": "فول بالطحينة", "cat": "Breakfast", "p": 35, "g": 270, "c": 400, "pr": 16, "cb": 42, "ft": 20},
            {"n": "Falafel (3 pcs)", "n_ar": "طعمية - 3 قطع", "cat": "Breakfast", "p": 15, "g": 100, "c": 280, "pr": 8, "cb": 30, "ft": 15},
            {"n": "Falafel Sandwich", "n_ar": "ساندوتش طعمية", "cat": "Breakfast", "p": 20, "g": 150, "c": 450, "pr": 12, "cb": 55, "ft": 20},
            {"n": "Foul Sandwich", "n_ar": "ساندوتش فول", "cat": "Breakfast", "p": 20, "g": 200, "c": 400, "pr": 15, "cb": 60, "ft": 10},
            {"n": "Boiled Eggs (2)", "n_ar": "بيض مسلوق - 2", "cat": "Breakfast", "p": 15, "g": 110, "c": 155, "pr": 13, "cb": 1, "ft": 11},
            {"n": "Scrambled Eggs (2)", "n_ar": "بيض مقلي", "cat": "Breakfast", "p": 25, "g": 120, "c": 200, "pr": 13, "cb": 1, "ft": 16},
            {"n": "Egg Sandwich", "n_ar": "ساندوتش بيض", "cat": "Breakfast", "p": 25, "g": 150, "c": 350, "pr": 16, "cb": 30, "ft": 18},
            {"n": "Cheese Sandwich", "n_ar": "ساندوتش جبنة", "cat": "Breakfast", "p": 25, "g": 120, "c": 320, "pr": 10, "cb": 30, "ft": 15},
            {"n": "Labneh with Olive Oil", "n_ar": "لبنة بالزيت", "cat": "Breakfast", "p": 45, "g": 150, "c": 250, "pr": 8, "cb": 5, "ft": 22},
            {"n": "Feteer Meshaltet (Plain)", "n_ar": "فطير مشلتت سادة", "cat": "Breakfast", "p": 60, "g": 200, "c": 650, "pr": 8, "cb": 80, "ft": 35},
            {"n": "Feteer with Cheese", "n_ar": "فطير بالجبنة", "cat": "Breakfast", "p": 85, "g": 250, "c": 750, "pr": 15, "cb": 85, "ft": 40},
            {"n": "Feteer with Honey", "n_ar": "فطير بالعسل", "cat": "Breakfast", "p": 75, "g": 220, "c": 700, "pr": 8, "cb": 95, "ft": 35},
            {"n": "Baladi Omelette", "n_ar": "أومليت بلدي", "cat": "Breakfast", "p": 35, "g": 150, "c": 350, "pr": 18, "cb": 5, "ft": 28},

            # LUNCH (20)
            {"n": "Koshari (Regular)", "n_ar": "كشري عادي", "cat": "Lunch", "p": 45, "g": 350, "c": 550, "pr": 18, "cb": 100, "ft": 10},
            {"n": "Koshari (Large)", "n_ar": "كشري كبير", "cat": "Lunch", "p": 65, "g": 500, "c": 800, "pr": 25, "cb": 140, "ft": 15},
            {"n": "Molokhia with Rice", "n_ar": "ملوخية بالأرز", "cat": "Lunch", "p": 65, "g": 400, "c": 450, "pr": 8, "cb": 80, "ft": 10},
            {"n": "Molokhia with Bread", "n_ar": "ملوخية بالعيش", "cat": "Lunch", "p": 55, "g": 350, "c": 350, "pr": 8, "cb": 60, "ft": 8},
            {"n": "Mahshi (Mix)", "n_ar": "محشي مشكل", "cat": "Lunch", "p": 85, "g": 300, "c": 500, "pr": 6, "cb": 80, "ft": 18},
            {"n": "Okra Stew (Bamia)", "n_ar": "بامية", "cat": "Lunch", "p": 75, "g": 300, "c": 250, "pr": 6, "cb": 20, "ft": 15},
            {"n": "White Bean Stew", "n_ar": "فاصوليا بيضا", "cat": "Lunch", "p": 65, "g": 300, "c": 300, "pr": 12, "cb": 40, "ft": 8},
            {"n": "Green Bean Stew", "n_ar": "فاصوليا خضرا", "cat": "Lunch", "p": 65, "g": 300, "c": 200, "pr": 4, "cb": 20, "ft": 10},
            {"n": "Lentil Soup", "n_ar": "شوربة عدس", "cat": "Lunch", "p": 45, "g": 300, "c": 220, "pr": 12, "cb": 35, "ft": 4},
            {"n": "Grilled Chicken (1/4)", "n_ar": "ربع فراخ مشوية", "cat": "Lunch", "p": 120, "g": 250, "c": 350, "pr": 40, "cb": 0, "ft": 20},
            {"n": "Grilled Chicken (1/2)", "n_ar": "نص فراخ مشوية", "cat": "Lunch", "p": 220, "g": 500, "c": 700, "pr": 80, "cb": 0, "ft": 40},
            {"n": "Fried Chicken (2 pcs)", "n_ar": "فراخ مقلي - قطعتين", "cat": "Lunch", "p": 150, "g": 250, "c": 600, "pr": 35, "cb": 20, "ft": 40},
            {"n": "Kofta (4 pcs)", "n_ar": "كفتة - 4 قطع", "cat": "Lunch", "p": 180, "g": 200, "c": 550, "pr": 30, "cb": 10, "ft": 45},
            {"n": "Hawawshi", "n_ar": "حواوشي", "cat": "Lunch", "p": 65, "g": 200, "c": 600, "pr": 25, "cb": 40, "ft": 35},
            {"n": "Shawarma Sandwich", "n_ar": "ساندوتش شاورما", "cat": "Lunch", "p": 110, "g": 200, "c": 500, "pr": 25, "cb": 40, "ft": 25},
            {"n": "Liver Sandwich", "n_ar": "ساندوتش كبدة", "cat": "Lunch", "p": 55, "g": 150, "c": 400, "pr": 20, "cb": 35, "ft": 18},
            {"n": "Rice with Chicken", "n_ar": "أرز بالفراخ", "cat": "Lunch", "p": 130, "g": 400, "c": 600, "pr": 30, "cb": 80, "ft": 15},
            {"n": "Pasta Bechamel", "n_ar": "مكرونة بشاميل", "cat": "Lunch", "p": 85, "g": 300, "c": 550, "pr": 20, "cb": 60, "ft": 25},
            {"n": "Fattah", "n_ar": "فتة", "cat": "Lunch", "p": 150, "g": 400, "c": 700, "pr": 25, "cb": 90, "ft": 25},
            {"n": "Torly (Mixed Veg)", "n_ar": "طرلي", "cat": "Lunch", "p": 65, "g": 300, "c": 250, "pr": 4, "cb": 30, "ft": 12},

            # DINNER (12)
            {"n": "Grilled Fish (Tilapia)", "n_ar": "سمك بلطي مشوي", "cat": "Dinner", "p": 150, "g": 350, "c": 300, "pr": 40, "cb": 5, "ft": 10},
            {"n": "Fried Fish", "n_ar": "سمك مقلي", "cat": "Dinner", "p": 160, "g": 350, "c": 500, "pr": 35, "cb": 20, "ft": 30},
            {"n": "Besara", "n_ar": "بصارة", "cat": "Dinner", "p": 35, "g": 200, "c": 300, "pr": 15, "cb": 30, "ft": 12},
            {"n": "Shakshuka", "n_ar": "شكشوكة", "cat": "Dinner", "p": 55, "g": 250, "c": 250, "pr": 12, "cb": 15, "ft": 16},
            {"n": "Lentils with Rice", "n_ar": "كشري اسكندراني", "cat": "Dinner", "p": 45, "g": 300, "c": 400, "pr": 12, "cb": 70, "ft": 8},
            {"n": "Mjadara", "n_ar": "مجدرة", "cat": "Dinner", "p": 50, "g": 300, "c": 420, "pr": 14, "cb": 75, "ft": 8},
            {"n": "Stuffed Cabbage", "n_ar": "محشي كرنب", "cat": "Dinner", "p": 85, "g": 300, "c": 400, "pr": 5, "cb": 70, "ft": 10},
            {"n": "Stuffed Grape Leaves", "n_ar": "محشي ورق عنب", "cat": "Dinner", "p": 95, "g": 250, "c": 350, "pr": 5, "cb": 60, "ft": 10},
            {"n": "Eggplant Moussaka", "n_ar": "مسقعة", "cat": "Dinner", "p": 75, "g": 300, "c": 400, "pr": 8, "cb": 25, "ft": 30},
            {"n": "Zucchini Bechamel", "n_ar": "كوسة بالبشاميل", "cat": "Dinner", "p": 85, "g": 300, "c": 350, "pr": 10, "cb": 20, "ft": 25},
            {"n": "Potato Tajine", "n_ar": "طاجن بطاطس", "cat": "Dinner", "p": 65, "g": 300, "c": 300, "pr": 4, "cb": 40, "ft": 14},
            {"n": "Mixed Grill", "n_ar": "مشويات مشكلة", "cat": "Dinner", "p": 350, "g": 300, "c": 600, "pr": 50, "cb": 0, "ft": 40},

            # SNACKS (15)
            {"n": "Semit Bread", "n_ar": "سميط", "cat": "Snack", "p": 10, "g": 80, "c": 250, "pr": 8, "cb": 45, "ft": 4},
            {"n": "Boiled Sweet Potato", "n_ar": "بطاطا مسلوقة", "cat": "Snack", "p": 20, "g": 200, "c": 180, "pr": 4, "cb": 40, "ft": 0},
            {"n": "Roasted Chickpeas", "n_ar": "حمص مقلي", "cat": "Snack", "p": 25, "g": 100, "c": 360, "pr": 19, "cb": 60, "ft": 6},
            {"n": "Peanuts", "n_ar": "فول سوداني", "cat": "Snack", "p": 35, "g": 100, "c": 567, "pr": 26, "cb": 16, "ft": 49},
            {"n": "Sunflower Seeds", "n_ar": "لب سوري", "cat": "Snack", "p": 25, "g": 100, "c": 580, "pr": 21, "cb": 20, "ft": 51},
            {"n": "Popcorn", "n_ar": "فشار", "cat": "Snack", "p": 15, "g": 50, "c": 190, "pr": 3, "cb": 35, "ft": 2},
            {"n": "Fruit Salad", "n_ar": "سلطة فواكه", "cat": "Snack", "p": 50, "g": 250, "c": 150, "pr": 2, "cb": 38, "ft": 0},
            {"n": "Halawa", "n_ar": "حلاوة طحينية", "cat": "Snack", "p": 25, "g": 50, "c": 270, "pr": 6, "cb": 25, "ft": 16},
            {"n": "Basbousa", "n_ar": "بسبوسة", "cat": "Snack", "p": 35, "g": 100, "c": 350, "pr": 4, "cb": 55, "ft": 14},
            {"n": "Konafa", "n_ar": "كنافة", "cat": "Snack", "p": 45, "g": 120, "c": 450, "pr": 6, "cb": 60, "ft": 22},
            {"n": "Qatayef", "n_ar": "قطايف", "cat": "Snack", "p": 30, "g": 80, "c": 200, "pr": 3, "cb": 35, "ft": 6},
            {"n": "Balah El Sham (3)", "n_ar": "بلح الشام", "cat": "Snack", "p": 35, "g": 100, "c": 380, "pr": 4, "cb": 40, "ft": 22},
            {"n": "Yogurt Cup", "n_ar": "كوب زبادي", "cat": "Snack", "p": 15, "g": 170, "c": 110, "pr": 6, "cb": 8, "ft": 6},
            {"n": "Fruit Yogurt", "n_ar": "زبادي فواكه", "cat": "Snack", "p": 25, "g": 170, "c": 160, "pr": 5, "cb": 25, "ft": 4},
            {"n": "Cheese w Tomato", "n_ar": "جبنة بالطماطم", "cat": "Snack", "p": 15, "g": 150, "c": 250, "pr": 12, "cb": 5, "ft": 20},

            # SALADS (12)
            {"n": "Egyptian Salad", "n_ar": "سلطة بلدي", "cat": "Salads", "p": 20, "g": 150, "c": 50, "pr": 1, "cb": 10, "ft": 0},
            {"n": "Tahini Salad", "n_ar": "سلطة طحينة", "cat": "Salads", "p": 25, "g": 100, "c": 250, "pr": 8, "cb": 12, "ft": 20},
            {"n": "Baba Ghanoush", "n_ar": "بابا غنوج", "cat": "Salads", "p": 35, "g": 150, "c": 180, "pr": 4, "cb": 15, "ft": 12},
            {"n": "Hummus", "n_ar": "حمص", "cat": "Salads", "p": 35, "g": 100, "c": 170, "pr": 8, "cb": 14, "ft": 10},
            {"n": "Tabbouleh", "n_ar": "تبولة", "cat": "Salads", "p": 45, "g": 150, "c": 120, "pr": 2, "cb": 10, "ft": 8},
            {"n": "Fattoush", "n_ar": "فتوش", "cat": "Salads", "p": 45, "g": 200, "c": 160, "pr": 3, "cb": 20, "ft": 8},
            {"n": "Green Salad", "n_ar": "سلطة خضرا", "cat": "Salads", "p": 25, "g": 150, "c": 45, "pr": 1, "cb": 8, "ft": 0},
            {"n": "Cucumber Yogurt", "n_ar": "سلطة زبادي", "cat": "Salads", "p": 25, "g": 150, "c": 90, "pr": 4, "cb": 6, "ft": 4},
            {"n": "Pickled Veg", "n_ar": "طرشي", "cat": "Salads", "p": 10, "g": 100, "c": 30, "pr": 1, "cb": 6, "ft": 0},
            {"n": "Olives", "n_ar": "زيتون", "cat": "Salads", "p": 45, "g": 80, "c": 120, "pr": 0, "cb": 2, "ft": 12},
            {"n": "Cheese Platter", "n_ar": "طبق جبنة", "cat": "Salads", "p": 65, "g": 150, "c": 400, "pr": 20, "cb": 2, "ft": 35},
            {"n": "Mixed Mezze", "n_ar": "مقبلات مشكلة", "cat": "Salads", "p": 85, "g": 250, "c": 450, "pr": 12, "cb": 25, "ft": 35},
        ]
        
        count = 0
        for data in meals_data:
            meal = BaseMeal.objects.create(
                name=data['n'],
                name_ar=data['n_ar'],
                meal_type=data['cat'],
                calories=data['c'],
                protein_g=data['pr'],
                carbs_g=data['cb'],
                fats_g=data['ft'],
                serving_weight=data['g'],
                is_standard_portion=True,
                is_healthy=(data['c'] < 600 and data['cat'] != 'Snack') or data['cat'] == 'Salads',
                base_price=data['p']
            )
            count += 1
            
        self.stdout.write(f"   -> Created {count} meals with prices.")

    def validate_data(self):
        self.stdout.write("✅ Validation:")
        
        ing_count = Ingredient.objects.count()
        meal_count = BaseMeal.objects.count()
        
        self.stdout.write(f"   Ingredients: {ing_count}")
        self.stdout.write(f"   Meals: {meal_count}")
        
        if ing_count < 10:
             self.stdout.write(self.style.ERROR("   ⚠️  Warning: Low ingredient count!"))
        
        avg_price = BaseMeal.objects.aggregate(Avg('base_price'))['base_price__avg']
        self.stdout.write(f"   Avg Meal Price: {avg_price:.2f} EGP")
        
        self.stdout.write(self.style.SUCCESS("🎉 Database rebuild complete!"))
