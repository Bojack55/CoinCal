
import os
import django
import sys
import traceback

sys.path.append('d:\\CoinCal_1\\CoinCal\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_nutritionist.settings')
django.setup()

from api.models import BaseMeal, UserProfile
from django.contrib.auth.models import User
from api.serializers import LocationAwareBaseMealSerializer

def verify_price_calculation():
    print("Verifying Pricing Logic...")
    meal = BaseMeal.objects.first()
    if not meal:
        print("No meals found.")
        return

    print(f"Testing Meal: {meal.name}")
    print(f"Base Price: {meal.base_price}")
    
    contexts = [
        {'location_multiplier': 1.0, 'city_name': 'Cairo'},
        {'location_multiplier': 0.80, 'city_name': 'Sohag'},
        {'location_multiplier': 0.95, 'city_name': 'Alexandria'},
    ]
    
    for ctx in contexts:
        try:
            # Emulate the serializer context passed by views
            serializer = LocationAwareBaseMealSerializer(meal, context=ctx)
            price = serializer.data['price']
            print(f"  Price in {ctx['city_name']} (x{ctx['location_multiplier']}): {price}")
            
            expected = float(meal.base_price) * ctx['location_multiplier']
            diff = abs(float(price) - expected)
            if diff > 0.01:
                 print(f"    MISMATCH! Expected {expected}, got {price}")
            else:
                 print(f"    Verified.")
        except Exception as e:
            print(f"EXCEPTION in {ctx['city_name']}: {e}")
            traceback.print_exc()

def verify_profile_logic():
    print("\nVerifying Profile Auto-Categorization...")
    u, _ = User.objects.get_or_create(username='test_pricing_user')
    # Cleanup previous
    UserProfile.objects.filter(user=u).delete()
    
    # Test Cairo (Metro)
    p = UserProfile.objects.create(user=u, current_location='Cairo')
    print(f"  [Cairo] Category: {p.location_category} (Expected: metro)")
    print(f"  [Cairo] Multiplier: {p.get_location_multiplier()} (Expected: 1.0)")
    
    if p.location_category != 'metro':
        print("  FAIL: Cairo should be metro")
    
    # Test Update to Sohag (Provincial)
    p.current_location = 'Sohag'
    p.save()
    p.refresh_from_db()
    print(f"  [Sohag] Category: {p.location_category} (Expected: provincial)")
    print(f"  [Sohag] Multiplier: {p.get_location_multiplier()} (Expected: 0.8)")

    if p.location_category != 'provincial':
        print("  FAIL: Sohag should be provincial")

    # Test Unknown City (Default to Cairo/Metro)
    p.current_location = 'Unknown City 123'
    p.save()
    p.refresh_from_db()
    print(f"  [Unknown] Category: {p.location_category} (Expected: metro)")
    
    if p.location_category != 'metro':
        print("  FAIL: Unknown city should default to metro")

if __name__ == '__main__':
    verify_price_calculation()
    verify_profile_logic()
