from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone


class BaseMeal(models.Model):
    meal_type = models.CharField(max_length=20, choices=[
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
    ])
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    min_calories = models.IntegerField(null=True, blank=True)
    max_calories = models.IntegerField(null=True, blank=True)
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fats_g = models.FloatField()
    image_url = models.URLField(null=True, blank=True)
    is_standard_portion = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100) # e.g., 'Cairo', 'Banha'
    is_national_brand = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.city})"


class MarketPrice(models.Model):
    meal = models.ForeignKey(BaseMeal, on_delete=models.CASCADE, related_name='prices')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='prices')
    price_egp = models.FloatField()

    class Meta:
        unique_together = ('meal', 'vendor')

    def __str__(self):
        return f"{self.meal.name} @ {self.vendor.name}: {self.price_egp} EGP"


class UserProfile(models.Model):
    DIET_CHOICES = [
        ('BALANCED', 'Balanced'),
        ('KETO', 'Keto'),
        ('VEGAN', 'Vegan'),
        ('HIGH_PROTEIN', 'High Protein'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    weight = models.FloatField() # in kg
    height = models.FloatField(default=170.0) # in cm
    goal_weight = models.FloatField()
    daily_budget_limit = models.FloatField(default=50.0)
    calorie_goal = models.IntegerField(editable=False, null=True, blank=True)
    age = models.IntegerField(default=20)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    activity_level = models.CharField(max_length=50, default='Sedentary', choices=[
        ('Sedentary', 'Sedentary'),
        ('Light', 'Light'),
        ('Moderate', 'Moderate'),
        ('Active', 'Active'),
    ])
    preferred_brands = models.TextField(null=True, blank=True)
    current_location = models.CharField(max_length=255, default="Cairo")
    
    # Premium Fields
    is_premium = models.BooleanField(default=False)
    body_fat_percentage = models.FloatField(null=True, blank=True)
    diet_mode = models.CharField(max_length=20, choices=DIET_CHOICES, default='BALANCED')

    def save(self, *args, **kwargs):
        # 1. Calculate BMR
        bmr = 0
        if self.is_premium and self.body_fat_percentage:
            # Katch-McArdle Formula
            lean_mass = self.weight * (1 - (self.body_fat_percentage / 100))
            bmr = 370 + (21.6 * lean_mass)
        else:
            # Mifflin-St Jeor Formula
            if self.gender == 'M':
                bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
            else:
                bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        
        # 2. Apply Activity Multiplier
        multipliers = {
            'Sedentary': 1.2,
            'Light': 1.375,
            'Moderate': 1.55,
            'Active': 1.725
        }
        tdee = bmr * multipliers.get(self.activity_level, 1.2)
        
        # 3. Adjust for Weight Goal (Simple +/- 500 kcal)
        if self.goal_weight < self.weight:
            self.calorie_goal = int(tdee - 500)
        elif self.goal_weight > self.weight:
            self.calorie_goal = int(tdee + 500)
        else:
            self.calorie_goal = int(tdee)
            
        super().save(*args, **kwargs)

    @property
    def ideal_weight(self):
        """Calculates ideal weight based on BMI 22: weight = 22 * (height_m^2)"""
        height_m = self.height / 100
        return round(22 * (height_m ** 2), 1)

    def __str__(self):
        return f"{self.user.username}'s profile ({'PRO' if self.is_premium else 'FREE'})"


class WeightLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.FloatField()
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.user.username}: {self.weight}kg on {self.date}"


class UserCustomMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_meals')
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fats_g = models.FloatField()
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} (Custom by {self.user.username})"


class MealLog(models.Model):
    PREP_CHOICES = [
        ('LIGHT', 'Light'),
        ('STANDARD', 'Standard'),
        ('HEAVY', 'Heavy'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='meal_logs')
    meal = models.ForeignKey(BaseMeal, on_delete=models.SET_NULL, null=True, blank=True, related_name='meal_logs')
    custom_meal = models.ForeignKey(UserCustomMeal, on_delete=models.SET_NULL, null=True, blank=True, related_name='meal_logs')
    egyptian_meal = models.ForeignKey('EgyptianMeal', on_delete=models.SET_NULL, null=True, blank=True, related_name='meal_logs')
    date = models.DateField(default=date.today)
    quantity = models.FloatField(default=1.0)
    prep_style = models.CharField(max_length=10, choices=PREP_CHOICES, default='STANDARD')
    
    final_calories = models.IntegerField(editable=False)
    final_price = models.FloatField(editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # 1. Determine Base Calories
        base_cals = 0
        if self.meal:
            base_cals = self.meal.calories
        elif self.custom_meal:
            base_cals = self.custom_meal.calories
        elif self.egyptian_meal:
            base_cals = self.egyptian_meal.calculate_nutrition()['calories']
        
        # 2. Apply Modifier
        modifiers = {
            'LIGHT': 0.85,
            'STANDARD': 1.0,
            'HEAVY': 1.3
        }
        mod = modifiers.get(self.prep_style, 1.0)
        self.final_calories = int((base_cals * mod) * self.quantity)

        # 3. Determine Final Price
        self.final_price = 0.0
        if self.meal:
            # Look for local price first, then fallback to Cairo/Generic
            prices = MarketPrice.objects.filter(meal=self.meal)
            local_price = prices.filter(vendor__city=self.user.current_location).first()
            if not local_price:
                local_price = prices.filter(vendor__city='Cairo').first() or prices.first()
            
            if local_price:
                self.final_price = local_price.price_egp * self.quantity
        elif self.egyptian_meal:
            # Egyptian meals calculate price dynamically from ingredients + markup
            self.final_price = self.egyptian_meal.get_price() * self.quantity
        
        # Save the log
        is_new = self.pk is None
        old_calories = 0
        old_price = 0
        if not is_new:
            old_instance = MealLog.objects.get(pk=self.pk)
            old_calories = old_instance.final_calories
            old_price = old_instance.final_price

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


class DailySummary(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='summaries')
    date = models.DateField(default=date.today)
    total_calories_consumed = models.IntegerField(default=0)
    total_budget_spent = models.FloatField(default=0.0)
    water_intake_cups = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.user.username} - {self.date}"

class Ingredient(models.Model):
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
    usda_id = models.CharField(max_length=20, null=True, blank=True, help_text="USDA FoodData Central ID")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='GRAM')
    
    # Nutrition per 100g (Ground Truth from USDA)
    calories_per_100g = models.FloatField(default=0, help_text="Calories per 100g")
    protein_per_100g = models.FloatField(default=0, help_text="Protein (g) per 100g")
    carbs_per_100g = models.FloatField(default=0, help_text="Carbohydrates (g) per 100g")
    fat_per_100g = models.FloatField(default=0, help_text="Fat (g) per 100g")
    fiber_per_100g = models.FloatField(default=0, help_text="Fiber (g) per 100g")
    
    # Legacy fields for backward compatibility
    price_per_unit = models.FloatField(default=0, help_text="Price for 1g, 1ml or 1 piece")
    calories_per_unit = models.FloatField(default=0, help_text="Calories for 1g, 1ml or 1 piece")
    is_common = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.usda_id or 'no USDA'})"

    class Meta:
        ordering = ['name']


class EgyptianMeal(models.Model):
    """
    Traditional Egyptian meal - nutrition calculated from ingredients.
    No static calorie count - all values derived from composition.
    """
    meal_id = models.CharField(max_length=50, unique=True)  # e.g., 'koshary'
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, null=True, blank=True)
    default_serving_weight_g = models.IntegerField(default=300)
    image_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name_en} ({self.meal_id})"

    def get_price(self, weight_g=None):
        """
        Calculates realistic price based on ingredient costs and categorical markup.
        Matches the logic in EgyptianMealUnifiedSerializer.
        """
        if weight_g is None:
            weight_g = self.default_serving_weight_g
            
        total_cost = 0.0
        for item in self.recipe_items.all():
            ing_price_per_gram = item.ingredient.price_per_unit
            ingredient_weight = weight_g * (item.percentage / 100.0)
            total_cost += ingredient_weight * ing_price_per_gram
            
        # Categorical Markup (Realism logic)
        # Determine category dynamically for model logic
        is_breakfast_or_snack = any(x in self.name_en.lower() for x in ['sandwich', 'pudding', 'foul', 'tameya', 'basbousa', 'om ali'])
        
        if is_breakfast_or_snack:
            markup = 2.0
        else:
            markup = 3.2
            
        return round(total_cost * markup, 2)

    def calculate_nutrition(self, weight_g=None):
        """
        Calculate total nutrition for this meal at given weight.
        Uses the Lego approach - sum of ingredient contributions.
        """
        if weight_g is None:
            weight_g = self.default_serving_weight_g

        total = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
        }

        for recipe_item in self.recipe_items.all():
            ingredient = recipe_item.ingredient
            ingredient_weight = weight_g * recipe_item.percentage / 100
            scale = ingredient_weight / 100  # nutrition is per 100g

            total['calories'] += ingredient.calories_per_100g * scale
            total['protein'] += ingredient.protein_per_100g * scale
            total['carbs'] += ingredient.carbs_per_100g * scale
            total['fat'] += ingredient.fat_per_100g * scale
            total['fiber'] += ingredient.fiber_per_100g * scale

        result = {k: round(v, 1) for k, v in total.items()}
        result['price'] = self.get_price(weight_g)
        return result

    class Meta:
        verbose_name = "Egyptian Meal"
        verbose_name_plural = "Egyptian Meals"


class MealRecipe(models.Model):
    """
    Junction table connecting EgyptianMeal to Ingredients with percentage.
    This enables the "Lego" calculation approach.
    """
    meal = models.ForeignKey(EgyptianMeal, on_delete=models.CASCADE, related_name='recipe_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='meal_recipes')
    percentage = models.FloatField(help_text="Percentage by weight (0-100)")

    class Meta:
        unique_together = ('meal', 'ingredient')
        ordering = ['-percentage']

    def __str__(self):
        return f"{self.meal.name_en}: {self.percentage}% {self.ingredient.name}"


class DailyPrice(models.Model):
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

    item_id = models.CharField(max_length=50)  # e.g., 'rice_1kg'
    item_name = models.CharField(max_length=100)
    price_egp = models.FloatField()
    unit = models.CharField(max_length=50)
    store_name = models.CharField(max_length=100, default='carrefour_egypt')
    date = models.DateField(default=date.today)
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='medium')
    scraped_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('item_id', 'store_name', 'date')
        ordering = ['-date', 'item_id']

    def __str__(self):
        return f"{self.item_name}: {self.price_egp} EGP ({self.date})"


class Recipe(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=100)
    servings = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} by {self.user.user.username}"


class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.amount}{self.ingredient.unit} of {self.ingredient.name} in {self.recipe.name}"

