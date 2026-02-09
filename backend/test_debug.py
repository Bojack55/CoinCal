
import os
import django
import sys
import traceback

sys.path.append('d:\\CoinCal_1\\CoinCal\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_nutritionist.settings')
django.setup()

with open('result.txt', 'w', encoding='utf-8') as f:
    f.write("DEBUG START\n")
    try:
        from api.models import BaseMeal
        from api.serializers import LocationAwareBaseMealSerializer
        f.write("Imported.\n")
        
        f.write(f"Declared Fields: {list(LocationAwareBaseMealSerializer._declared_fields.keys())}\n")
        
        meal = BaseMeal.objects.first()
        f.write(f"Meal: {meal}\n")
        
        s = LocationAwareBaseMealSerializer(meal)
        f.write("Instantiated.\n")
        
        f.write(f"Fields: {list(s.fields.keys())}\n")
        f.write("SUCCESS.\n")
        
    except Exception as e:
        f.write(f"EXCEPTION: {e}\n")
        traceback.print_exc(file=f)
