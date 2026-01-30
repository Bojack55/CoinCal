from django.urls import path
from . import views

urlpatterns = [
    path('foods/', views.get_food_list, name='food-list'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('suggest/', views.suggest_meal_plan, name='suggest-meal-plan'),
    path('dashboard/', views.get_dashboard, name='dashboard'),
    path('water/', views.manage_water, name='manage-water'),
    path('log/', views.log_food, name='log-food'),
    path('custom-meal/', views.create_custom_meal, name='create-custom-meal'),
    path('profile/', views.manage_profile, name='manage-profile'),
    path('weight/', views.manage_weight, name='manage-weight'),
    path('search-food/', views.search_food, name='search-food'),
    path('ingredients/', views.search_ingredients, name='search-ingredients'),
    path('recipes/', views.manage_recipes, name='recipe-list'),
    path('recipes/<int:pk>/', views.manage_recipes, name='recipe-detail'),
    path('log-recipe/', views.log_recipe, name='log-recipe'),
    path('generate-plan/', views.generate_plan, name='generate-plan'),
    path('analytics/financial/', views.financial_analytics, name='financial-analytics'),
    
    # Egyptian Meals API (read-only)
    path('egyptian-meals/', views.list_egyptian_meals, name='egyptian-meals-list'),
    path('egyptian-meals/<str:meal_id>/', views.get_egyptian_meal, name='egyptian-meal-detail'),
    path('egyptian-meals/<str:meal_id>/calculate/', views.calculate_meal_nutrition, name='egyptian-meal-calculate'),
    
    # Daily Prices API
    path('prices/', views.receive_daily_prices, name='receive-prices'),
    path('prices/latest/', views.get_daily_prices, name='get-prices'),
]

