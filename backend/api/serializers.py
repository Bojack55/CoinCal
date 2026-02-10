from rest_framework import serializers
from .models import (
    BaseMeal, Vendor, MarketPrice, UserProfile, MealLog, UserCustomMeal,
    DailySummary, Ingredient, Recipe, RecipeItem, EgyptianMeal, MealRecipe, DailyPrice, WeightLog, DayStatus
)


# ============ Egyptian Meals (Lego Engine) Serializers ============


class MealRecipeSerializer(serializers.ModelSerializer):
    """Serializer for meal recipe items (ingredient + percentage)"""
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    usda_id = serializers.CharField(source='ingredient.usda_id', read_only=True)

    class Meta:
        model = MealRecipe
        fields = ['ingredient_name', 'usda_id', 'percentage']


class EgyptianMealSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Egyptian meals.
    Includes calculated nutrition based on ingredients.
    """
    ingredients = MealRecipeSerializer(source='recipe_items', many=True, read_only=True)
    nutrition = serializers.SerializerMethodField()

    class Meta:
        model = EgyptianMeal
        fields = [
            'id', 'meal_id', 'name_en', 'name_ar', 'default_serving_weight_g',
            'image_url', 'description', 'ingredients', 'nutrition'
        ]

    def get_nutrition(self, obj):
        """Calculate nutrition using the Lego approach"""
        weight = self.context.get('weight_g', obj.default_serving_weight_g)
        return obj.calculate_nutrition(weight)


class EgyptianMealListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for meal list view"""
    nutrition = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = EgyptianMeal
        fields = ['id', 'meal_id', 'name_en', 'name_ar', 'default_serving_weight_g', 'nutrition', 'price']

    def get_nutrition(self, obj):
        return obj.calculate_nutrition()

    def get_price(self, obj):
        return obj.get_price()


# ============ Daily Prices Serializers ============

class DailyPriceSerializer(serializers.ModelSerializer):
    """Serializer for daily prices from the price anchor"""
    class Meta:
        model = DailyPrice
        fields = [
            'id', 'item_id', 'item_name', 'price_egp', 'unit',
            'store_name', 'date', 'confidence', 'scraped_at'
        ]
        read_only_fields = ['id', 'scraped_at']


class DailyPriceCreateSerializer(serializers.Serializer):
    """
    Serializer for receiving price data from the price_anchor.py scraper.
    Handles bulk creation of daily prices.
    """
    date = serializers.DateField()
    source = serializers.CharField()
    items = serializers.ListField(child=serializers.DictField())

    def validate_items(self, value):
        for item in value:
            price = item.get('price_egp')
            if price is None:
                raise serializers.ValidationError(f"Item {item.get('item_id')} is missing price_egp")
            try:
                price = float(price)
                if price <= 0:
                    raise serializers.ValidationError(f"Price for {item.get('item_id')} must be positive. Got {price}")
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Invalid price format for {item.get('item_id')}")
        return value

    def create(self, validated_data):
        items = validated_data.get('items', [])
        date = validated_data.get('date')
        source = validated_data.get('source', 'unknown')
        
        created_prices = []
        for item in items:
            price, _ = DailyPrice.objects.update_or_create(
                item_id=item.get('item_id'),
                store_name=source,
                date=date,
                defaults={
                    'item_name': item.get('item_name'),
                    'price_egp': float(item.get('price_egp')),
                    'unit': item.get('unit', 'unit'),
                    'confidence': item.get('confidence', 'medium'),
                }
            )
            created_prices.append(price)
        
        return created_prices


# ============ Existing Serializers ============

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)
    
    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient', 'ingredient_name', 'amount', 'unit']

class RecipeSerializer(serializers.ModelSerializer):
    items = RecipeItemSerializer(many=True, read_only=True)
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'servings', 'created_at', 'items', 'metrics']

    def get_metrics(self, obj):
        # Optimization: Use prefetch_related for ingredients used in loop
        total_cost = 0.0
        total_cals = 0.0
        
        # Accessing obj.items.all() which should be prefetched in the view
        for item in obj.items.all():
            total_cost += float(item.amount) * float(item.ingredient.price_per_unit)
            total_cals += float(item.amount) * float(item.ingredient.calories_per_unit)
            
        return {
            "total_cost": round(total_cost, 2),
            "total_calories": int(total_cals),
            "cost_per_plate": round(total_cost / obj.servings, 2) if obj.servings > 0 else 0,
            "cals_per_plate": int(total_cals / obj.servings) if obj.servings > 0 else 0
        }


class UserCustomMealSerializer(serializers.ModelSerializer):
    is_custom = serializers.ReadOnlyField(default=True)
    price = serializers.ReadOnlyField(default=0.0)
    category = serializers.ReadOnlyField(default='Custom')
    protein = serializers.FloatField(source='protein_g', read_only=True)
    carbs = serializers.FloatField(source='carbs_g', read_only=True)
    fats = serializers.FloatField(source='fats_g', read_only=True)
    
    class Meta:
        model = UserCustomMeal
        fields = [
            'id', 'name', 'name_ar', 'calories', 'protein', 'carbs', 'fats',
            'protein_g', 'carbs_g', 'fats_g', 
            'is_custom', 'price', 'category', 'is_private', 'created_at'
        ]


class BaseMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseMeal
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class MarketPriceSerializer(serializers.ModelSerializer):
    name_ar = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='price_egp', max_digits=10, decimal_places=2, read_only=True)
    name = serializers.ReadOnlyField(source='meal.name')
    calories = serializers.ReadOnlyField(source='meal.calories')
    protein = serializers.ReadOnlyField(source='meal.protein_g')
    carbs = serializers.ReadOnlyField(source='meal.carbs_g')
    fats = serializers.ReadOnlyField(source='meal.fats_g')
    fiber = serializers.ReadOnlyField(source='meal.fiber_g')
    serving_weight = serializers.ReadOnlyField(source='meal.serving_weight')
    is_healthy = serializers.ReadOnlyField(source='meal.is_healthy')
    is_standard_portion = serializers.ReadOnlyField(source='meal.is_standard_portion')
    min_calories = serializers.ReadOnlyField(source='meal.min_calories')
    max_calories = serializers.ReadOnlyField(source='meal.max_calories')
    category = serializers.ReadOnlyField(source='meal.meal_type')
    restaurant_name = serializers.ReadOnlyField(source='vendor.name')
    restaurant_location = serializers.ReadOnlyField(source='vendor.city')
    is_custom = serializers.SerializerMethodField()
    is_estimated = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = MarketPrice
        fields = [
            'id', 'name', 'name_ar', 'calories', 'min_calories', 'max_calories', 
            'category', 'restaurant_name', 'restaurant_location', 
            'price', 'is_custom', 'is_estimated', 'protein', 'carbs', 'fats', 'fiber', 'serving_weight',
            'is_healthy', 'is_standard_portion',
            'description', 'ingredients'
        ]

    def get_name_ar(self, obj):
        try:
            return obj.meal.name_ar
        except AttributeError:
             return None

    def get_description(self, obj):
        return "Legacy Market Item"

    def get_is_custom(self, obj):
        return False
        
    def get_is_estimated(self, obj):
        return False

    def get_ingredients(self, obj):
        return ["Standard Recipe"]


class EgyptianMealUnifiedSerializer(serializers.ModelSerializer):
    """
    Maps EgyptianMeal to the flat FoodItem format used in the frontend.
    """
    name = serializers.SerializerMethodField()
    calories = serializers.SerializerMethodField()
    protein = serializers.SerializerMethodField()
    carbs = serializers.SerializerMethodField()
    fats = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    is_custom = serializers.ReadOnlyField(default=False)
    is_egyptian = serializers.ReadOnlyField(default=True)
    is_estimated = serializers.ReadOnlyField(default=False)
    min_calories = serializers.SerializerMethodField()
    max_calories = serializers.SerializerMethodField()
    serving_unit = serializers.ReadOnlyField(default='Plate')
    category = serializers.SerializerMethodField()
    restaurant_name = serializers.ReadOnlyField(default='Egyptian Street Food')
    restaurant_location = serializers.ReadOnlyField(default='Cairo')
    description = serializers.CharField(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = EgyptianMeal
        fields = [
            'id', 'name', 'name_ar', 'calories', 'min_calories', 'max_calories', 
            'category', 'restaurant_name', 'restaurant_location', 
            'price', 'is_custom', 'is_egyptian', 'is_estimated', 'protein', 'carbs', 'fats',
            'serving_unit', 'description', 'ingredients', 'default_serving_weight_g'
        ]

    def get_name(self, obj):
        return obj.name_en

    def get_ingredients(self, obj):
        # Return list of ingredient names
        return [item.ingredient.name.replace('_', ' ').title() for item in obj.recipe_items.all()]

    def get_category(self, obj):
        mid = obj.meal_id.lower()
        # Breakfast Items
        if any(x in mid for x in ['foul', 'tameya', 'beid', 'shakshuka', 'cheese', 'falafel']):
            # These are also often eaten for dinner in Egypt
            return 'Breakfast'
        # Snack/Dessert
        if any(x in mid for x in ['basbousa', 'zalabya', 'om_ali', 'pudding', 'halawa', 'honey', 'sugar', 'potato']):
            return 'Snack'
        # Dinner specialized (lighter street food)
        if any(x in mid for x in ['sand', 'liver_sand', 'sausage_sand', 'kofta_sand']):
            return 'Dinner'
        # Lunch (Main meals)
        return 'Lunch' 

    def _get_nut(self, obj):
        # Cache nutrition result in the object instance to avoid redundant lookups
        if not hasattr(obj, '_nutrition_memo'):
            obj._nutrition_memo = obj.calculate_nutrition()
        return obj._nutrition_memo

    def get_calories(self, obj):
        return int(self._get_nut(obj)['calories'])

    def get_protein(self, obj):
        return self._get_nut(obj)['protein']

    def get_carbs(self, obj):
        return self._get_nut(obj)['carbs']

    def get_fats(self, obj):
        return self._get_nut(obj)['fat']

    def get_price(self, obj):
        base_price = self._get_nut(obj)['price']
        # Apply location multiplier from context
        multiplier = self.context.get('location_multiplier', 1.0)
        return round(float(base_price) * float(multiplier), 2)

    def get_min_calories(self, obj):
        return self.get_calories(obj)

    def get_max_calories(self, obj):
        return self.get_calories(obj)


class LocationAwareBaseMealSerializer(serializers.ModelSerializer):
    """
    Serializer for BaseMeal that calculates price based on user location.
    Replaces MarketPriceSerializer.
    """
    price = serializers.SerializerMethodField()
    name_ar = serializers.CharField()
    restaurant_name = serializers.SerializerMethodField()
    restaurant_location = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    is_custom = serializers.ReadOnlyField(default=False)
    is_estimated = serializers.ReadOnlyField(default=False)
    category = serializers.CharField(source='meal_type')
    
    class Meta:
        model = BaseMeal
        fields = [
            'id', 'name', 'name_ar', 'calories', 'min_calories', 'max_calories', 
            'category', 'restaurant_name', 'restaurant_location', 
            'price', 'is_custom', 'is_estimated', 'protein', 'carbs', 'fats', 'fiber', 'serving_weight',
            'is_healthy', 'is_standard_portion', 'description'
        ]
        # Map fields to match frontend expectations (frontend expects protein, carbs, fats without _g suffix? 
        # MarketPriceSerializer used source='meal.protein_g' named 'protein'.
        # So I need to alias them.
    
    protein = serializers.DecimalField(source='protein_g', max_digits=8, decimal_places=2, read_only=True)
    carbs = serializers.DecimalField(source='carbs_g', max_digits=8, decimal_places=2, read_only=True)
    fats = serializers.DecimalField(source='fats_g', max_digits=8, decimal_places=2, read_only=True)
    fiber = serializers.DecimalField(source='fiber_g', max_digits=8, decimal_places=2, read_only=True)

    def get_price(self, obj):
        multiplier = self.context.get('location_multiplier', 1.0)
        # obj.base_price is Decimal
        original_price = float(obj.base_price)
        return round(original_price * float(multiplier), 2)

    def get_restaurant_name(self, obj):
        return "Market Average"

    def get_restaurant_location(self, obj):
        return self.context.get('city_name', 'Cairo')
        
    def get_description(self, obj):
        return "Standard Meal Item"



class UserProfileSerializer(serializers.ModelSerializer):
    ideal_weight = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = '__all__'


class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = ['id', 'weight', 'date', 'created_at']

class MealLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealLog
        fields = '__all__'

class MealLogDetailedSerializer(serializers.ModelSerializer):
    meal_name = serializers.SerializerMethodField()
    meal_name_ar = serializers.SerializerMethodField()
    
    class Meta:
        model = MealLog
        fields = [
            'id', 'meal_name', 'meal_name_ar', 'quantity', 'prep_style', 
            'final_calories', 'final_price', 'date'
        ]

    def get_meal_name(self, obj):
        if obj.meal:
            return obj.meal.name
        if obj.egyptian_meal:
            return obj.egyptian_meal.name_en
        if obj.custom_meal:
            return obj.custom_meal.name
        return "Unknown Meal"

    def get_meal_name_ar(self, obj):
        if obj.meal:
            return obj.meal.name_ar
        if obj.egyptian_meal:
            return obj.egyptian_meal.name_ar
        return None

class UnifiedSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_ar = serializers.CharField(required=False, allow_null=True)
    calories = serializers.IntegerField()
    protein = serializers.FloatField()
    carbs = serializers.FloatField()
    fats = serializers.FloatField()
    price = serializers.FloatField()
    type = serializers.CharField() # 'global' or 'custom'
    is_estimated = serializers.BooleanField()
    category = serializers.CharField(required=False)
    restaurant_name = serializers.CharField(required=False)


class DayStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayStatus
        fields = ['date', 'status']

