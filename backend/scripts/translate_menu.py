
import json
import os

FIXTURE_PATH = 'fixtures/egyptian_master_menu.json'

TRANSLATIONS = {
    "Foul Plate (Plain)": "طبق فول (سادة)",
    "Foul Plate (Olive Oil)": "طبق فول (زيت زيتون)",
    "Foul Plate (Alexandrian)": "طبق فول (إسكندراني)",
    "Falafel (4 Pieces)": "طعمية (٤ قطع)",
    "Omelette with Pastrami": "أومليت بالبسطرمة",
    "Cheese with Tomato (Feta)": "جبنة بالطماطم (فيتا)",
    "Koshary Plate (Medium)": "طبق كشري (وسط)",
    "Koshary Plate (Big Boss)": "طبق كشري (كبير)",
    "Mahshi Vine Leaves (15 pcs)": "محشي ورق عنب (١٥ قطعة)",
    "Mahshi Cabbage (Plate)": "محشي كرنب (طبق)",
    "Molokhia with White Rice": "ملوخية مع أرز أبيض",
    "Pasta Bechamel (Large)": "مكرونة بشاميل (كبيرة)",
    "Hawawshi (1 Loaf)": "حواوشي (رغيف)",
    "Liver Sandwich (Alexandrian)": "ساندوتش كبدة (إسكندراني)",
    "Beef Shawarma (Kaiser)": "شاورما لحمة (كايزر)",
    "Chicken Shawarma (Saj)": "شاورما فراخ (صاج)",
    "Classic Cheeseburger": "تشيز برجر كلاسيك",
    "Fried Chicken (3 pcs)": "دجاج مقلي (٣ قطع)",
    "Pizza Margherita (Medium)": "بيتزا مارجريتا (وسط)",
    "Seafood Pizza (Medium)": "بيتزا سي فوود (وسط)",
    "Chicken Pane Crepe": "كريب دجاج بانيه",
    "Fiteer Meshaltet (Plain)": "فطير مشلتت (سادة)",
    "Sugarcane Juice (Large)": "عصير قصب (كبير)",
    "Rice Pudding (Roz Bel Laban)": "أرز باللبن",
    "Om Ali (Clay Pot)": "أم علي (طاجن)",
    "Quarter Ribs Chicken": "ربع فرخة (صدر/ورك)",
    "Beef Kofta (1/4 kg)": "كفتة مشوية (ربع كيلو)",
    "Stuffed Pigeon (1 pc)": "حمام محشي (قطعة)",
    "Okra (Bamia) w/ Meat": "بامية باللحمة",
    "Potato Tray w/ Chicken": "صينية بطاطس بالفراخ",
    "Lentil Soup": "شوربة عدس",
    "Orzo Soup (Lisan Asfour)": "شوربة لسان عصفور",
    "Eggplant Moussaka (Plain)": "مسقعة (سادة)",
    "Baladi Bread (Loaf)": "عيش بلدي (رغيف)",
    "Pepsi (Can)": "بيبسي (كانز)",
    "Mineral Water (Small)": "مياه معدنية (صغيرة)",
    "Grilled Tilapia": "سمك بلطي مشوي",
    "Sayadeya Rice (Plate)": "أرز صيادية (طبق)",
    "Baba Ganoush (Side)": "بابا غنوج (جانبي)",
    "Tahini (Side)": "طحينة (جانبي)",
    "Mango Juice (Large)": "عصير مانجو (كبير)",
    "Basbousa (Plate)": "بسبوسة (طبق)",
    "Kunafa with Cream": "كنافة بالقشطة",
    "Goulash with Meat": "جلاش باللحمة",
    "Liver (1/4 kg Bag)": "كبدة (ربع كيلو)",
    "Kebda Sandwich": "ساندوتش كبدة",
    "Sausage (Sogoq) Sandwich": "ساندوتش سجق",
    "French Fries (Small)": "بطاطس محمرة (صغيرة)",
    "Pickled Eggplant (Side)": "باذنجان مخلل",
    "Alexandrian Liver Meal": "وجبة كبدة إسكندراني",
    "Greek Salad (Large)": "سلطة يونانية (كبيرة)",
    "Caesar Salad": "سلطة سيزر",
    "Tabbouleh Salad": "تبولة",
    "Fattoush Salad": "فتوش",
    "Quinoa Buddha Bowl": "طبق كينوا صحي",
    "Grilled Salmon Plate": "سمك سلمون مشوي",
    "Shrimp Pasta": "مكرونة بالجمبري",
    "Fish Tajine": "طاجن سمك",
    "Seafood Rice": "أرز بالسي فوود",
    "Chicken Kebab Plate": "شيش طاووق (طبق)",
    "Lamb Chops (3 pcs)": "ريش ضاني (٣ قطع)",
    "Steak with Mushroom Sauce": "ستيك بصوص المشروم",
    "Mixed Grill Platter": "مشويات مشكل",
    "Chicken Curry with Rice": "دجاج بالكاري والأرز",
    "Vegetable Stir Fry": "خضار سوتيه",
    "Tofu Scramble Bowl": "طبق توفو",
    "Shakshuka": "شكشوكة",
    "Avocado Toast": "توست أفوكادو",
    "Pancakes (3 pcs) with Honey": "بان كيك بالعسل (٣ قطع)",
    "French Toast (3 slices)": "فرنش توست (٣ قطع)",
    "Granola with Yogurt": "جرانولا بالزبادي",
    "Smoothie Bowl (Berry)": "سموزي بيري",
    "Eggs Benedict": "بيض بينديكت",
    "Breakfast Burrito": "بوريتو إفطار",
    "Manakish Zaatar": "منقوشة زعتر",
    "Manakish Cheese": "منقوشة جبنة",
    "Labneh Sandwich": "ساندوتش لبنة",
    "Hummus Plate": "طبق حمص",
    "Falafel Wrap": "رال فلافل",
    "Grilled Chicken Wrap": "راب دجاج مشوي",
    "Tuna Sandwich": "ساندوتش تونة",
    "Club Sandwich": "كلوب ساندوتش",
    "Beef Burger (Homemade)": "برجر لحم (بيتي)",
    "Vegetarian Burger": "برجر نباتي",
    "Spaghetti Bolognese": "سباجيتي بولونيز",
    "Pasta Carbonara": "مكرونة كاربونارا",
    "Penne Arrabiata": "مكرونة أرابياتا",
    "Lasagna": "لازانيا",
    "Macaroni Gratin": "مكرونة فرن",
    "Chicken Alfredo Pasta": "مكرونة ألفريدو بالفراخ",
    "Biryani Rice (Chicken)": "أرز برياني دجاج",
    "Fried Rice (Vegetable)": "أرز مقلي بالخضار",
    "Fried Rice (Shrimp)": "أرز مقلي بالجمبري",
    "Noodle Stir Fry": "نودلز صيني",
    "Pad Thai": "باد تاي",
    "Sushi Platter (12 pcs)": "سوشي (١٢ قطعة)",
    "Spring Rolls (4 pcs)": "سبرينج رولز (٤ قطع)",
    "Samosa (4 pcs)": "سمبوسك (٤ قطع)",
    "Cheese Sticks (6 pcs)": "أصابع جبنة (٦ قطع)",
    "Chicken Wings (6 pcs)": "أجنحة دجاج (٦ قطع)",
    "Onion Rings (Large)": "حلقات بصل (كبير)",
    "Nachos with Cheese": "ناتشوز بالجبنة",
    "Quesadilla (Chicken)": "كساديا دجاج",
    "Tacos (3 pcs)": "تاكو (٣ قطع)",
    "Burrito Bowl": "طبق بوريتو",
    "Fajitas Platter": "فاهيتا دجاج",
    "Chocolate Cake (Slice)": "كيك شيكولاتة (قطعة)",
    "Cheesecake (Slice)": "تشيز كيك (قطعة)",
    "Tiramisu": "تيراميسو",
    "Brownies (2 pcs)": "براونيز (٢ قطعة)",
    "Cookies (4 pcs)": "كوكيز (٤ قطع)",
    "Ice Cream Sundae": "آيس كريم صانداي",
    "Milkshake (Chocolate)": "ميلك شيك شيكولاتة",
    "Milkshake (Vanilla)": "ميلك شيك فانيليا",
    "Milkshake (Strawberry)": "ميلك شيك فراولة",
    "Fresh Orange Juice (Large)": "عصير برتقال فريش (كبير)",
    "Carrot Juice (Large)": "عصير جزر (كبير)",
    "Pomegranate Juice (Large)": "عصير رمان (كبير)",
    "Iced Coffee (Large)": "آيس كوفي (كبير)",
    "Cappuccino": "كابتشينو",
    "Latte": "لاتيه",
    "Hot Chocolate": "هوت شوكليت",
    "Mint Lemonade (Large)": "ليمون بالنعناع (كبير)",
    "Mixed Berry Smoothie": "سموزي بيري مشكل",
    "Green Smoothie": "سموزي أخضر",
    "Protein Shake": "بروتين شيك",
    "Coconut Water (Fresh)": "ماء جوز الهند",
    "Sahlab (Hot)": "سحلب ساخن",
    "Karkade (Hibiscus Tea)": "كركديه",
    "Qamar El Din Juice": "عصير قمر الدين",
    "Tamarind Juice (Tamr Hindi)": "عصير تمر هندي",
    "Licorice Drink (Erq Sous)": "عرقسوس",
    "Aseer Asab (Mixed Juice)": "عصير قصب",
    "Banana Milk": "موز باللبن",
    "Mulakhiya Soup": "شوربة ملوخية",
    "Tomato Soup": "شوربة طماطم",
    "Mushroom Soup": "شوربة مشروم",
    "Chicken Noodle Soup": "شوربة دجاج بالشعيرية",
    "Minestrone Soup": "شوربة خضار",
    "French Onion Soup": "شوربة بصل",
    "Sweet Potato Fries": "بطاطس حلوة محمرة",
    "Roasted Vegetables": "خضار روستو",
    "Stuffed Bell Peppers": "فلفل ألوان محشي",
    "Zucchini Boats": "قوارب كوسة",
    "Eggplant Parm": "باذنجان بانيه",
    "Cauliflower Rice Bowl": "أرز قرنبيط",
    "Lentil Curry": "كاري عدس",
    "Chickpea Curry": "كاري حمص",
    "Black Bean Bowl": "طبق فاصوليا سوداء",
    "Veggie Wrap": "راب خضار",
    "Mediterranean Plate": "طبق متوسطي",
    "Acai Bowl": "طبق آساي",
    "Poke Bowl": "طبق بوكي",
    "Pita Bread (1 piece)": "عيش شامي (رغيف)",
    "Garlic Bread (4 slices)": "خبز بالثوم (٤ قطع)",
    "Grilled Halloumi Cheese": "جبنة حلوم مشوي",
    "Caprese Salad": "سلطة كابريزي",
    "Bruschetta (4 pcs)": "بروشيتا (٤ قطع)"
}

def main():
    print(f"Loading {FIXTURE_PATH}...")
    try:
        with open(FIXTURE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return

    count = 0
    missing = []
    
    for item in data:
        name = item.get('name')
        if name in TRANSLATIONS:
            item['name_ar'] = TRANSLATIONS[name]
            count += 1
        else:
            # Fallback or mark as missing
            item['name_ar'] = name # Default to English if not found, or maybe just leave it? 
            # Better to have some value than null if we enforce non-null in logic, but model allows null.
            # However, for "translate ALL", we should try.
            missing.append(name)

    print(f"Translated {count} items.")
    if missing:
        print(f"Missing translations for {len(missing)} items:")
        for m in missing:
            print(f" - {m}")

    with open(FIXTURE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved.")

if __name__ == "__main__":
    main()
