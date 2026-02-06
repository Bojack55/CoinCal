from django.contrib import admin
from .models import (
    BaseMeal, Vendor, MarketPrice, UserProfile, MealLog, UserCustomMeal,
    DailySummary, Ingredient, Recipe, RecipeItem, EgyptianMeal, MealRecipe, DailyPrice,
    WeightLog
)

admin.site.register(BaseMeal)
admin.site.register(Vendor)
admin.site.register(MarketPrice)
admin.site.register(UserProfile)
admin.site.register(MealLog)
admin.site.register(UserCustomMeal)
admin.site.register(DailySummary)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeItem)
admin.site.register(WeightLog)

class MealRecipeInline(admin.TabularInline):
    model = MealRecipe
    extra = 3

@admin.register(EgyptianMeal)
class EgyptianMealAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'meal_id', 'default_serving_weight_g')
    search_fields = ('name_en', 'meal_id')
    inlines = [MealRecipeInline]

admin.site.register(DailyPrice)

