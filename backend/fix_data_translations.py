
from api.models import BaseMeal, Ingredient
from django.db.models import Q

# English -> Arabic Dictionary
TRANSLATIONS = {
    # Ingredients
    "rice": "أرز",
    "white rice": "أرز أبيض",
    "brown rice": "أرز بني",
    "pasta": "مكرونة",
    "macaroni": "مكرونة",
    "spaghetti": "مكرونة اسباجيتي",
    "oats": "شوفان",
    "bread": "خبز",
    "baladi bread": "خبز بلدي",
    "flour": "دقيق",
    "potato": "بطاطس",
    "sweet potato": "بطاطا",
    
    # Proteins
    "chicken": "دجاج",
    "chicken breast": "صدور دجاج",
    "chicken thigh": "وراك دجاج",
    "beef": "لحم بقري",
    "ground beef": "لحم مفروم",
    "liver": "كبدة",
    "beef liver": "كبدة بقري",
    "egg": "بيض",
    "eggs": "بيض",
    "tuna": "تونا",
    "fish": "سمك",
    "tilapia": "بلطي",
    "salmon": "سالمون",
    
    # Dairy
    "milk": "حليب",
    "whole milk": "حليب كامل الدسم",
    "skim milk": "حليب خالي الدسم",
    "yogurt": "زبادي",
    "greek yogurt": "زبادي يوناني",
    "cheese": "جبنة",
    "feta cheese": "جبنة فيتا",
    "cottage cheese": "جبنة قريش",
    "cheddar cheese": "جبنة شيدر",
    "butter": "زبدة",
    "ghee": "سمن",
    
    # Veggies
    "tomato": "طماطم",
    "cucumber": "خيار",
    "onion": "بصل",
    "garlic": "ثوم",
    "pepper": "فلفل",
    "carrots": "جزر",
    "lettuce": "خس",
    "spinach": "سبانخ",
    "zucchini": "كوسة",
    "eggplant": "باذنجان",
    
    # Fruits
    "apple": "تفاح",
    "banana": "موز",
    "orange": "برتقال",
    "strawberry": "فراولة",
    "dates": "تمر",
    "watermelon": "بطيخ",
    
    # Pantry / Oils
    "oil": "زيت",
    "olive oil": "زيت زيتون",
    "vegetable oil": "زيت نباتي",
    "sugar": "سكر",
    "honey": "عسل",
    "salt": "ملح",
    "pepper": "فلفل",
    "cumin": "كمون",
    "tahini": "طحينة",
    "vinegar": "خل",
    
    # Specifics
    "foul": "فول",
    "fava beans": "فول",
    "falafel": "طعمية",
    "koshary": "كشري",
    "lentils": "عدس",
    "chickpeas": "حمص",
    "molokhia": "ملوخية",
    "fruit salad": "سلطة فواكه",
    "greek salad": "سلطة يونانية",
    "walnuts": "عين جمل",
    "almonds": "لوز",
    "almonds (handful)": "لوز (حفنة)",
    "walnuts (handful)": "عين جمل (حفنة)",
    "arugula": "جرجير",
    "bundle": "حزمة",
    "salad": "سلطة",
    "soup": "شوربة",
}

def fix_translations():
    count_updated = 0
    
    # Function to apply translation
    def update_item(item):
        nonlocal count_updated
        name_lower = item.name.lower().replace('_', ' ')
        
        # 1. Exact match
        if name_lower in TRANSLATIONS:
            item.name_ar = TRANSLATIONS[name_lower]
            item.save()
            print(f"Updated [Exact]: {item.name} -> {item.name_ar}")
            count_updated += 1
            return

        # 2. Partial match (longest match wins)
        best_match = None
        best_len = 0
        
        for key, val in TRANSLATIONS.items():
            if key in name_lower and len(key) > best_len:
                best_match = val
                best_len = len(key)
        
        if best_match:
            # Simple heuristic: If it's a partial match, we might want to manually verifying
            # But for now, let's use it as a base. 
            # E.g. "Cooked Rice" -> "أرز" (Acceptable fallback)
            item.name_ar = best_match 
            item.save()
            print(f"Updated [Partial]: {item.name} -> {item.name_ar}")
            count_updated += 1

    # Update Ingredients
    print("Scanning Ingredients...")
    for i in Ingredient.objects.filter(Q(name_ar__isnull=True) | Q(name_ar='')):
        update_item(i)

    # Update BaseMeals
    print("Scanning BaseMeals...")
    for m in BaseMeal.objects.filter(Q(name_ar__isnull=True) | Q(name_ar='')):
        update_item(m)

    print(f"Total Updated: {count_updated}")

# Execute immediately
fix_translations()
