import math
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models import Sum


from decimal import Decimal


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


from .utils.location_helpers import (
    LOCATION_CHOICES, get_city_category, get_multiplier_for_category
)

class AbstractMeal(TimeStampedModel):
    name = models.CharField(max_length=100, default='Unnamed Meal', db_index=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True, help_text='Arabic meal name', db_index=True)
    calories = models.IntegerField(default=0)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    carbs_g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    fats_g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    fiber_g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'), help_text='Dietary fiber in grams')
    serving_weight = models.IntegerField(default=100, help_text='Serving size in grams')
    image_url = models.URLField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'), help_text="Reference price in EGP")

    def get_price_for_location(self, location_category):
        """Calculate adjusted price based on location"""
        multipliers = {
            'metro': Decimal('1.0'),
            'major_city': Decimal('0.95'),
            'regional': Decimal('0.88'),
            'provincial': Decimal('0.80'),
            'rural': Decimal('0.70'),
        }
        multiplier = multipliers.get(location_category, Decimal('1.0'))
        return self.base_price * multiplier

    class Meta:
        abstract = True


class BaseMeal(AbstractMeal):
    name_ar = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    meal_type = models.CharField(max_length=20, default='Snack', choices=[
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
        ('Salads', 'Salads'),
    ])
    min_calories = models.IntegerField(null=True, blank=True)
    max_calories = models.IntegerField(null=True, blank=True)
    is_standard_portion = models.BooleanField(default=False)
    is_healthy = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100) # e.g., 'Cairo', 'Banha'
    is_national_brand = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.city})"


class MarketPrice(TimeStampedModel):
    meal = models.ForeignKey(BaseMeal, on_delete=models.CASCADE, related_name='prices')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='prices')
    price_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    is_price_verified = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('meal', 'vendor')

    def __str__(self):
        return f"{self.meal.name} @ {self.vendor.name}: {self.price_egp} EGP"


class UserProfile(TimeStampedModel):
    DIET_CHOICES = [
        ('BALANCED', 'Balanced'),
        ('KETO', 'Keto'),
        ('VEGAN', 'Vegan'),
        ('HIGH_PROTEIN', 'High Protein'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('70.0')) # in kg
    height = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('170.0')) # in cm
    goal_weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('70.0'))
    daily_budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.0'))
    calorie_goal = models.IntegerField(editable=False, null=True, blank=True)
    age = models.IntegerField(default=20)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    activity_level = models.CharField(max_length=50, default='Sedentary', choices=[
        ('Sedentary', 'Sedentary'),
        ('Light', 'Light'),
        ('Lightly Active', 'Lightly Active'),
        ('Moderate', 'Moderate'),
        ('Moderately Active', 'Moderately Active'),
        ('Active', 'Active'),
        ('Very Active', 'Very Active'),
        ('Extremely Active', 'Extremely Active'),
    ])
    preferred_brands = models.TextField(null=True, blank=True)
    current_location = models.CharField(max_length=255, default="Cairo")
    
    # Location Based Pricing
    location_category = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default='metro',
        help_text="Price category for user's location (Auto-assigned)"
    )

    # Premium Fields
    is_premium = models.BooleanField(default=False)
    body_fat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    diet_mode = models.CharField(max_length=20, choices=DIET_CHOICES, default='BALANCED')



    def get_location_multiplier(self):
        """Get price multiplier for user's location"""
        return get_multiplier_for_category(self.location_category)
    
    # Hydration Gamification
    hydration_level = models.IntegerField(default=1)
    total_glasses_lifetime = models.IntegerField(default=0)
    current_hydration_streak = models.IntegerField(default=0)
    best_hydration_streak = models.IntegerField(default=0)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Current weight for diet planning')
    
    # Diet Planner V7: Variation Tracking
    last_plan_variant = models.IntegerField(default=0, help_text='Tracks the last used diet plan strategy (0-4) for rotation.')

    def save(self, *args, **kwargs):
        from .utils.nutrition import calculate_bmr, calculate_tdee, get_caloric_balance
        
        # 0. Auto-assign category based on current_location
        if self.current_location:
            self.location_category = get_city_category(self.current_location)
        
        # 1. Calculate BMR
        bmr = calculate_bmr(
            weight=self.weight,
            height=self.height,
            age=self.age,
            gender=self.gender,
            body_fat=self.body_fat_percentage,
            is_premium=self.is_premium
        )
        
        # 2. Apply Activity Multiplier
        tdee = calculate_tdee(bmr, self.activity_level)
        
        # 3. Adjust for Weight Goal
        self.calorie_goal = get_caloric_balance(tdee, self.weight, self.goal_weight)
            
        super().save(*args, **kwargs)

    @property
    def ideal_weight(self):
        """Calculates ideal weight based on BMI 22: weight = 22 * (height_m^2)"""
        height_m = self.height / 100
        return round(22 * (height_m ** 2), 1)

    def __str__(self):
        return f"{self.user.username}'s profile ({'PRO' if self.is_premium else 'FREE'})"


class WeightLog(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    date = models.DateField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.user.username}: {self.weight}kg on {self.date}"


class UserCustomMeal(AbstractMeal):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_meals')
    # already inherits macros and timestamps
    is_private = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Custom by {self.user.username})"


class MealLog(TimeStampedModel):
    PREP_CHOICES = [
        ('LIGHT', 'Light'),
        ('STANDARD', 'Standard'),
        ('HEAVY', 'Heavy'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='meal_logs')
    meal = models.ForeignKey(BaseMeal, on_delete=models.SET_NULL, null=True, blank=True, related_name='standard_meal_logs')
    custom_meal = models.ForeignKey(UserCustomMeal, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_meal_logs')
    egyptian_meal = models.ForeignKey('EgyptianMeal', on_delete=models.SET_NULL, null=True, blank=True, related_name='egyptian_meal_logs')
    date = models.DateField(default=date.today, db_index=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    prep_style = models.CharField(max_length=10, choices=PREP_CHOICES, default='STANDARD')
    
    final_calories = models.IntegerField(editable=False, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'), editable=False)

    def save(self, *args, **kwargs):
        # 0. Location Multipliers for fallback logic
        multipliers = {
            'metro': Decimal('1.0'),
            'major_city': Decimal('0.95'),
            'regional': Decimal('0.88'),
            'provincial': Decimal('0.80'),
            'rural': Decimal('0.70'),
        }
        multiplier = multipliers.get(self.user.location_category, Decimal('1.0'))

        # 1. Determine Base Calories & Price
        # If no meal is attached, we preserve any existing/manually set values
        if self.meal or self.custom_meal or self.egyptian_meal:
            base_cals = 0
            base_price = Decimal('0.0')
            
            if self.meal:
                base_cals = self.meal.calories
                # Price logic: MarketPrice -> BaseMeal Fallback
                mp = MarketPrice.objects.filter(meal=self.meal)
                local_mp = mp.filter(vendor__city=self.user.current_location).first()
                if not local_mp:
                    local_mp = mp.filter(vendor__city='Cairo').first() or mp.first()
                
                if local_mp:
                    base_price = local_mp.price_egp
                else:
                    # Fallback to BaseMeal's reference price with location adjustment
                    base_price = self.meal.base_price * multiplier
            
            elif self.egyptian_meal:
                base_cals = self.egyptian_meal.calculate_nutrition()['calories']
                # Localize the EgyptianMeal recipe price
                base_price = Decimal(self.egyptian_meal.get_price()) * multiplier
            
            elif self.custom_meal:
                base_cals = self.custom_meal.calories
                # Custom meals now inherit base_price from AbstractMeal
                base_price = self.custom_meal.base_price * multiplier

            # 2. Apply Quantity and Prep Modifiers
            prep_mods = {
                'LIGHT': Decimal('0.85'),
                'STANDARD': Decimal('1.0'),
                'HEAVY': Decimal('1.3')
            }
            mod = prep_mods.get(self.prep_style, Decimal('1.0'))
            qt = Decimal(str(self.quantity))
            
            self.final_calories = int(Decimal(base_cals) * mod * qt)
            self.final_price = (base_price * qt).quantize(Decimal('0.01'))
        
        # If we reach here and final_calories/price were set manually (e.g. log_recipe),
        # they are preserved because we only overwrite them if a meal source is present.
        
        # Save the log
        is_new = self.pk is None
        old_calories = 0
        old_price = Decimal('0')
        if not is_new:
            try:
                old_instance = MealLog.objects.get(pk=self.pk)
                old_calories = old_instance.final_calories
                old_price = old_instance.final_price
            except MealLog.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 4. Update DailySummary
        summary, _ = DailySummary.objects.get_or_create(user=self.user, date=self.date)
        summary.total_calories_consumed += (self.final_calories - old_calories)
        summary.total_budget_spent += (self.final_price - old_price)
        summary.save()

    def __str__(self):
        if self.meal:
            name = self.meal.name
        elif self.custom_meal:
            name = self.custom_meal.name
        elif self.egyptian_meal:
            name = self.egyptian_meal.name_en
        else:
            name = "Unknown"
        return f"{self.user.user.username} - {name} ({self.prep_style}) on {self.date}"


class DailySummary(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='summaries')
    date = models.DateField(default=date.today, db_index=True)
    total_calories_consumed = models.IntegerField(default=0)
    total_budget_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    water_intake_cups = models.IntegerField(default=0)
    hydration_goal_met = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.user.username} - {self.date}"

class Ingredient(TimeStampedModel):
    """
    Ground-truth ingredient with USDA reference.
    All nutrition values are per 100g for consistent calculation.
    """
    UNIT_CHOICES = [
        ('GRAM', 'Gram (g)'),
        ('ML', 'Milliliter (ml)'),
        ('PIECE', 'Piece (qty)'),
    ]
    name = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True)
    usda_id = models.CharField(max_length=20, null=True, blank=True, help_text="USDA FoodData Central ID")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='GRAM')
    
    # Nutrition per 100g (Ground Truth from USDA)
    calories_per_100g = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    protein_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    carbs_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    fat_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    fiber_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.0'))
    
    # Price
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'), help_text="Cairo/Giza reference price in EGP")
    
    # Legacy fields
    calories_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    is_common = models.BooleanField(default=False)

    def get_price_for_location(self, location_category):
        """Calculate adjusted price based on location"""
        multipliers = {
            'metro': 1.0,
            'major_city': 0.95,
            'regional': 0.88,
            'provincial': 0.80,
            'rural': 0.70,
        }
        multiplier = multipliers.get(location_category, 1.0)
        return self.base_price * Decimal(str(multiplier))

    def __str__(self):
        return f"{self.name} ({self.usda_id or 'no USDA'})"

    class Meta:
        ordering = ['name']


@receiver(pre_save, sender=Ingredient)
def normalize_ingredient_name(sender, instance, **kwargs):
    """Force lowercase/trimmed names to avoid 'Tomato' vs 'tomato' duplication."""
    if instance.name:
        instance.name = instance.name.strip().lower()


class EgyptianMeal(TimeStampedModel):
    """
    Traditional Egyptian meal - nutrition calculated from ingredients.
    No static calorie count - all values derived from composition.
    """
    meal_id = models.CharField(max_length=50, unique=True)  # e.g., 'koshary'
    name_en = models.CharField(max_length=100, db_index=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    default_serving_weight_g = models.IntegerField(default=300)
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name_en} ({self.meal_id})"

    def get_price(self, weight_g=None):
        """
        Calculates realistic price based on ingredient costs and categorical markup.
        Matches the logic in EgyptianMealUnifiedSerializer.
        """
        if weight_g is None:
            weight_g = self.default_serving_weight_g
            
        total_cost = Decimal('0.0')
        w_decimal = Decimal(str(weight_g))
        
        for item in self.recipe_items.all():
            ing_base_price = item.ingredient.base_price
            ingredient_weight = w_decimal * (item.percentage / Decimal('100.0'))
            
            if item.ingredient.unit in ['GRAM', 'ML']:
                 # base_price is per 100g/ml
                 cost = (ingredient_weight / Decimal('100.0')) * ing_base_price
            else:
                 # base_price is per piece
                 # Assuming ingredient_weight implies number of pieces if unit is PIECE? 
                 # Or percentage of a piece?
                 # Existing logic used weight. Let's assume weight logic applies to grams only for now or 
                 # we need to check how recipe items are defined for pieces. 
                 # For safety, treating piece price as direct multiplier if needed, but recipe percentage is weight based?
                 # Defaulting to 100g normalization for logic consistency with current rebuild script
                 # But technically Piece items shouldn't be weighted in grams usually unless converted.
                 # Let's stick to the 100g normalization if unit is GRAM/ML, else just multiply?
                 # Actually, let's look at how pieces are handled.
                 # In populate_ingredients: unit=PIECE.
                 # If recipe has Eggs (Piece), percentage 100?
                 # EgyptianMeal servings are in Grams.
                 # It's safest to assume standard mass-based calculation.
                 cost = (ingredient_weight / Decimal('100.0')) * ing_base_price
            
            total_cost += cost
            
        # Categorical Markup (Realism logic)
        is_breakfast_or_snack = any(x in self.name_en.lower() for x in ['sandwich', 'pudding', 'foul', 'tameya', 'basbousa', 'om ali', 'baba', 'side', 'salad', 'tahini', 'dip', 'hawawshi', 'koshary', 'fiteer', 'zalabya'])
        
        markup = Decimal('1.6') if is_breakfast_or_snack else Decimal('2.2')
            
        # Return rounded up price (Ceiling)
        final_price = total_cost * markup
        return Decimal(math.ceil(final_price))

    @property
    def nutrition_integrity(self):
        """
        Calculates the discrepancy between summed calories and macro-cals (4-4-9 rule).
        Returns a dictionary with 'discrepancy_kcal' and 'is_precise'.
        """
        from .utils.nutrition import calculate_macro_calories
        nut = self.calculate_nutrition()
        if nut['calories'] == Decimal('0'):
            return {'discrepancy_kcal': Decimal('0'), 'is_precise': True}
            
        macro_cals = calculate_macro_calories(nut['protein'], nut['carbs'], nut['fat'])
        discrepancy = abs(nut['calories'] - macro_cals)
        
        return {
            'discrepancy_kcal': discrepancy.quantize(Decimal('0.1')),
            'is_precise': discrepancy < (nut['calories'] * Decimal('0.1')), # 10% tolerance
            'macro_calories': macro_cals.quantize(Decimal('0.1'))
        }

    def calculate_nutrition(self, weight_g=None):
        """
        Calculate total nutrition for this meal at given weight.
        Uses the Lego approach - sum of ingredient contributions.
        """
        if weight_g is None:
            weight_g = self.default_serving_weight_g

        total = {
            'calories': Decimal('0'),
            'protein': Decimal('0'),
            'carbs': Decimal('0'),
            'fat': Decimal('0'),
            'fiber': Decimal('0'),
        }
        w_decimal = Decimal(str(weight_g))

        for recipe_item in self.recipe_items.all():
            ingredient = recipe_item.ingredient
            ingredient_weight = w_decimal * recipe_item.percentage / Decimal('100')
            scale = ingredient_weight / Decimal('100')  # nutrition is per 100g

            total['calories'] += ingredient.calories_per_100g * scale
            total['protein'] += ingredient.protein_per_100g * scale
            total['carbs'] += ingredient.carbs_per_100g * scale
            total['fat'] += ingredient.fat_per_100g * scale
            total['fiber'] += ingredient.fiber_per_100g * scale

        result = {k: v.quantize(Decimal('0.1')) for k, v in total.items()}
        result['price'] = self.get_price(weight_g)
        return result

    class Meta:
        verbose_name = "Egyptian Meal"
        verbose_name_plural = "Egyptian Meals"


class MealRecipe(TimeStampedModel):
    """
    Junction table connecting EgyptianMeal to Ingredients with percentage.
    This enables the "Lego" calculation approach.
    """
    meal = models.ForeignKey(EgyptianMeal, on_delete=models.CASCADE, related_name='recipe_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='meal_recipes')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.0'), help_text="Percentage by weight (0-100)")

    class Meta:
        unique_together = ('meal', 'ingredient')
        ordering = ['-percentage']

    def __str__(self):
        return f"{self.meal.name_en}: {self.percentage}% {self.ingredient.name}"


class DailyPrice(TimeStampedModel):
    """
    Ground truth price data from the Price Anchor scraper.
    Used for validating user-submitted prices.
    """
    CONFIDENCE_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('mock', 'Mock Data'),
    ]

    item_id = models.CharField(max_length=100, default='generic_item')
    item_name = models.CharField(max_length=100)
    price_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    unit = models.CharField(max_length=50)
    store_name = models.CharField(max_length=100, default='carrefour_egypt')
    date = models.DateField(default=date.today)
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='medium')
    scraped_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', 'item_id']

    def __str__(self):
        return f"{self.item_name}: {self.price_egp} EGP ({self.date})"


class Recipe(TimeStampedModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, null=True, blank=True, help_text='Arabic recipe name')
    servings = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} by {self.user.user.username}"


class RecipeItem(TimeStampedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.amount}{self.ingredient.unit} of {self.ingredient.name} in {self.recipe.name}"


class DayStatus(TimeStampedModel):
    STATUS_CHOICES = [
        ('standard', 'Standard'),
        ('cheat', 'Cheat Day'),
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='day_statuses')
    date = models.DateField(default=date.today, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='standard')

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.user.user.username} - {self.date}: {self.status}"


class HydrationAchievement(TimeStampedModel):
    """
    Tracks unlocked hydration achievements for gamification.
    """
    ACHIEVEMENT_CHOICES = [
        ('FIRST_DROP', 'First Drop - Logged first glass'),
        ('HOT_STREAK', 'Hot Streak - 7 days hitting goal'),
        ('LIGHTNING', 'Lightning - 3 consecutive perfect days'),
        ('HYDRO_HERO', 'Hydro Hero - 30-day streak'),
        ('OCEAN_MASTER', 'Ocean Master - 100 total glasses'),
        ('LEVEL_5', 'Level 5 Unlocked'),
        ('LEVEL_10', 'Level 10 Unlocked'),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='hydration_achievements')
    achievement_id = models.CharField(max_length=50, choices=ACHIEVEMENT_CHOICES)
    unlocked_at = models.DateTimeField(default=timezone.now)
    seen = models.BooleanField(default=False)  # For showing popup once

    class Meta:
        unique_together = ('user', 'achievement_id')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.user.username} unlocked {self.achievement_id}"
