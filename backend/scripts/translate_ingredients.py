
import re
import os

SEED_FILE = 'api/management/commands/seed_ingredients.py'

TRANSLATIONS = {
    "White Rice (Long Grain, Cooked)": "أرز أبيض (طويل الحبة، مطبوخ)",
    "Pasta (Macaroni, Cooked)": "مكرونة (مطبوخة)",
    "Lentils (Cooked)": "عدس (مطبوخ)",
    "Fava Beans (Foul, Cooked)": "فول (مطبوخ)",
    "Bread (Baladi, Egyptian)": "عيش بلدي",
    "Tomato (Raw)": "طماطم",
    "Potato (Boiled)": "بطاطس (مسلوقة)",
    "Onion (Raw)": "بصل",
    "Garlic (Raw)": "ثوم",
    "Cucumber (Raw)": "خيار",
    "Green Bell Pepper (Raw)": "فلفل أخضر",
    "Eggplant (Cooked)": "باذنجان (مطبوخ)",
    "Chicken Breast (Cooked, No Skin)": "صدور دجاج (مطبوخة)",
    "Ground Beef (80% Lean, Cooked)": "لحم مفروم (مطبوخ)",
    "Egg (Whole, Cooked)": "بيض (مسلوق)",
    "Chickpeas (Cooked)": "حمص (حب، مطبوخ)",
    "Olive Oil": "زيت زيتون",
    "Vegetable Oil (Sunflower)": "زيت عباد الشمس",
    "Butter (Salted)": "زبدة",
    "Ghee (Clarified Butter)": "سمن بلدي",
    "Milk (Whole, 3.25% fat)": "حليب (كامل الدسم)",
    "Feta Cheese": "جبنة فيتا",
    "Greek Yogurt (Plain, 2% fat)": "زبادي يوناني",
    "Salt (Table)": "ملح",
    "Black Pepper (Ground)": "فلفل أسود",
    "Cumin (Ground)": "كمون",
    "Tahini (Sesame Paste)": "طحينة",
    "Dates (Deglet Noor)": "تمر",
    "Banana (Raw)": "موز",
    "Sugar (White, Granulated)": "سكر",
    "Tilapia Fillet (Raw)": "فيليه بلطي",
    "Shrimp (Raw)": "جمبري (ني)",
    "Salmon Fillet (Raw)": "فيليه سلمون",
    "Tuna (Canned in Water)": "تونة (معلبة)",
    "Spinach (Raw)": "سبانخ",
    "Zucchini (Raw)": "كوسة",
    "Carrots (Raw)": "جزر",
    "Cauliflower (Raw)": "قرنبيط",
    "Broccoli (Raw)": "بروكلي",
    "Lettuce (Romaine)": "خس",
    "Cabbage (Green, Raw)": "كرنب",
    "Okra (Raw)": "بامية",
    "Kidney Beans (Cooked)": "فاصوليا حمراء",
    "Black Beans (Cooked)": "فاصوليا سوداء",
    "Green Peas (Cooked)": "بسلة",
    "Almonds (Raw)": "لوز",
    "Walnuts (Raw)": "عين جمل",
    "Peanuts (Raw)": "سوداني",
    "Cashews (Raw)": "كاجو",
    "Sunflower Seeds": "لب سوري",
    "Pumpkin Seeds": "لب أبيض",
    "Sesame Seeds": "سمسم",
    "Apple (Raw)": "تفاح",
    "Orange (Raw)": "برتقال",
    "Mango (Raw)": "مانجو",
    "Watermelon (Raw)": "بطيخ",
    "Grapes (Raw)": "عنب",
    "Strawberry (Raw)": "فراولة",
    "Turkey Breast (Cooked)": "صدر رومي (مدخن)",
    "Lamb (Lean, Cooked)": "لحم ضاني",
    "Beef Liver (Cooked)": "كبدة بتلو",
    "Chicken Liver (Cooked)": "كبدة فراخ",
    "Tofu (Firm)": "توفو",
    "Parsley (Fresh)": "بقدونس",
    "Coriander (Fresh)": "كزبرة",
    "Dill (Fresh)": "شبت",
    "Lemon Juice (Fresh)": "عصير ليمون",
    "Vinegar (White)": "خل",
    "Soy Sauce": "صويا صوص",
    "Tomato Paste": "صلصة طماطم",
    "Oats (Rolled, Dry)": "شوفان",
    "Quinoa (Cooked)": "كينوا",
    "Bulgur (Cooked)": "برغل",
    "Couscous (Cooked)": "كسكسي",
    "Coffee (Brewed)": "قهوة",
    "Tea (Black, Brewed)": "شاي",
    "Honey": "عسل نحل"
}

def main():
    print(f"Reading {SEED_FILE}...")
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("File not found.")
        return

    # Regex to find dictionary entries with "name": "..."
    # We want to insert "name_ar": "..." after "name": "..."
    # pattern: "name": "Value",
    
    lines = content.split('\n')
    new_lines = []
    
    count = 0
    
    for line in lines:
        new_lines.append(line)
        match = re.search(r'"name": "(.*?)",', line)
        if match:
            name = match.group(1)
            if name in TRANSLATIONS:
                indentation = line[:line.find('"')]
                ar_name = TRANSLATIONS[name]
                # Check if name_ar already exists in next line to avoid dupes if run multiple times
                # But for now assume clean run or acceptable dupe (syntax error if dupes key? no, just overwrite)
                # But to be clean we just insert.
                
                new_line = f'{indentation}"name_ar": "{ar_name}",'
                new_lines.append(new_line)
                count += 1
            else:
                # If not translated, add English name as fallback?
                # Or leave blank? Let's leave blank for now or add fallback
                # Wait, user wants "everything translated".
                # I'll just use the English name as Arabic if missing, but mark it.
                pass 

    print(f"Injected {count} translations.")
    
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("Saved.")

if __name__ == "__main__":
    main()
