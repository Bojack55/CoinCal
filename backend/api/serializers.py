from rest_framework import serializers
from .models import (
    BaseMeal, Vendor, MarketPrice, UserProfile, MealLog, UserCustomMeal,
    Ingredient, Recipe, RecipeItem, EgyptianMeal, MealRecipe, DailyPrice, WeightLog
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

    class Meta:
        model = EgyptianMeal
        fields = ['id', 'meal_id', 'name_en', 'name_ar', 'default_serving_weight_g', 'nutrition']

    def get_nutrition(self, obj):
        return obj.calculate_nutrition()


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
                    'price_egp': item.get('price_egp'),
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
        total_cost = 0.0
        total_cals = 0.0
        
        for item in obj.items.all():
            total_cost += item.amount * item.ingredient.price_per_unit
            total_cals += item.amount * item.ingredient.calories_per_unit
            
        return {
            "total_cost": round(total_cost, 2),
            "total_calories": int(total_cals),
            "cost_per_plate": round(total_cost / obj.servings, 2) if obj.servings > 0 else 0,
            "cals_per_plate": int(total_cals / obj.servings) if obj.servings > 0 else 0
        }


class UserCustomMealSerializer(serializers.ModelSerializer):
    is_custom = serializers.ReadOnlyField(default=True)
    class Meta:
        model = UserCustomMeal
        fields = '__all__'


class BaseMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseMeal
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class MarketPriceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='meal.name', read_only=True)
    calories = serializers.IntegerField(source='meal.calories', read_only=True)
    min_calories = serializers.IntegerField(source='meal.min_calories', read_only=True)
    max_calories = serializers.IntegerField(source='meal.max_calories', read_only=True)
    category = serializers.CharField(source='meal.meal_type', read_only=True)
    restaurant_name = serializers.CharField(source='vendor.name', read_only=True)
    restaurant_location = serializers.CharField(source='vendor.city', read_only=True)
    price = serializers.FloatField(source='price_egp', read_only=True)
    is_custom = serializers.ReadOnlyField(default=False)
    is_estimated = serializers.BooleanField(default=False, read_only=True)
    
    protein = serializers.FloatField(source='meal.protein_g', read_only=True)
    carbs = serializers.FloatField(source='meal.carbs_g', read_only=True)
    fats = serializers.FloatField(source='meal.fats_g', read_only=True)

    class Meta:
        model = MarketPrice
        fields = ['id', 'name', 'calories', 'min_calories', 'max_calories', 'category', 'restaurant_name', 'restaurant_location', 'price', 'is_custom', 'is_estimated', 'protein', 'carbs', 'fats']


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
    serving_unit = serializers.ReadOnlyField(default='Plate')
    category = serializers.SerializerMethodField()
    restaurant_name = serializers.ReadOnlyField(default='Egyptian Street Food')
    restaurant_location = serializers.ReadOnlyField(default='Cairo')
    is_custom = serializers.ReadOnlyField(default=False)
    is_estimated = serializers.ReadOnlyField(default=False)
    min_calories = serializers.SerializerMethodField()
    max_calories = serializers.SerializerMethodField()

    class Meta:
        model = EgyptianMeal
        fields = [
            'id', 'name', 'calories', 'min_calories', 'max_calories', 
            'category', 'restaurant_name', 'restaurant_location', 
            'price', 'is_custom', 'is_estimated', 'protein', 'carbs', 'fats',
            'serving_unit'
        ]

    def get_name(self, obj):
        return obj.name_en

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
        return obj.calculate_nutrition()

    def get_calories(self, obj):
        return int(self._get_nut(obj)['calories'])

    def get_protein(self, obj):
        return self._get_nut(obj)['protein']

    def get_carbs(self, obj):
        return self._get_nut(obj)['carbs']

    def get_fats(self, obj):
        return self._get_nut(obj)['fat']

    def get_price(self, obj):
        return obj.get_price()

    def get_min_calories(self, obj):
        return self.get_calories(obj)

    def get_max_calories(self, obj):
        return self.get_calories(obj)


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

class UnifiedSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    calories = serializers.IntegerField()
    protein = serializers.FloatField()
    carbs = serializers.FloatField()
    fats = serializers.FloatField()
    price = serializers.FloatField()
    type = serializers.CharField() # 'global' or 'custom'
    is_estimated = serializers.BooleanField()
    category = serializers.CharField(required=False)
    restaurant_name = serializers.CharField(required=False)
