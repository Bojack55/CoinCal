
from api.models import BaseMeal, EgyptianMeal, Ingredient
from django.db.models import Q

def audit():
    output_path = r'C:/Users/moaza/.gemini/antigravity/brain/73e92531-c5d6-436b-8665-88fcb3f6224c/audit_result.txt'
    print(f"Writing to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("--- Meal Data Audit ---\n")
        
        # BaseMeal
        base_count = BaseMeal.objects.count()
        base_missing = BaseMeal.objects.filter(Q(name_ar__isnull=True) | Q(name_ar='')).count()
        f.write(f"BaseMeal (Legacy): Total={base_count}, Missing AR={base_missing}\n")
        
        # EgyptianMeal
        eg_count = EgyptianMeal.objects.count()
        eg_missing = EgyptianMeal.objects.filter(Q(name_ar__isnull=True) | Q(name_ar='')).count()
        f.write(f"EgyptianMeal: Total={eg_count}, Missing AR={eg_missing}\n")
        
        # Ingredient
        ing_count = Ingredient.objects.count()
        ing_missing = Ingredient.objects.filter(Q(name_ar__isnull=True) | Q(name_ar='')).count()
        f.write(f"Ingredient: Total={ing_count}, Missing AR={ing_missing}\n")

        if base_missing > 0:
            f.write("\nSAMPLE MISSING BaseMeal:\n")
            for m in BaseMeal.objects.filter(Q(name_ar__isnull=True) | Q(name_ar=''))[:5]:
                f.write(f"- {m.name}\n")

        if ing_missing > 0:
            f.write("\nSAMPLE MISSING Ingredient:\n")
            for i in Ingredient.objects.filter(Q(name_ar__isnull=True) | Q(name_ar=''))[:5]:
                f.write(f"- {i.name}\n")
    
    # Print to stdout for agent visibility
    print(f"BaseMeal (Legacy): Total={base_count}, Missing AR={base_missing}")
    print(f"Ingredient: Total={ing_count}, Missing AR={ing_missing}")

if __name__ == r'__main__':
    audit()
