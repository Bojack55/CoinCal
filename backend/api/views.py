import random
from datetime import date, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from .models import (
    BaseMeal, Vendor, MarketPrice, UserProfile, MealLog, UserCustomMeal,
    DailySummary, Ingredient, Recipe, RecipeItem, EgyptianMeal, DailyPrice
)
from .serializers import (
    MarketPriceSerializer, UserProfileSerializer, UserCustomMealSerializer, 
    UnifiedSearchSerializer, IngredientSerializer, RecipeSerializer,
    EgyptianMealSerializer, EgyptianMealListSerializer, DailyPriceSerializer,
    DailyPriceCreateSerializer, EgyptianMealUnifiedSerializer, WeightLogSerializer
)
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')
        
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Safe extraction of numeric values (matching new model field names)
        weight = float(request.data.get('current_weight') or request.data.get('weight') or 70)
        height = float(request.data.get('height') or 170)
        age = int(request.data.get('age') or 25)
        gender = request.data.get('gender', 'M')
        daily_budget_limit = float(request.data.get('daily_budget') or request.data.get('daily_budget_limit') or 100)
        current_location = request.data.get('location') or request.data.get('current_location') or 'Cairo'
        preferred_brands = request.data.get('preferred_brands', '')
        activity_level = request.data.get('activity_level', 'Sedentary')
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # The calorie_goal is handled by api.signals
        UserProfile.objects.create(
            user=user,
            weight=weight,
            height=height,
            age=age,
            gender=gender,
            goal_weight=weight, 
            daily_budget_limit=daily_budget_limit,
            current_location=current_location,
            preferred_brands=preferred_brands,
            activity_level=activity_level
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error during registration: {str(e)}")
        traceback.print_exc()
        return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_food_list(request):
    user_location = request.query_params.get('location') or request.user.profile.current_location
    
    # 1. Primary Query: Local Prices
    local_prices = MarketPrice.objects.filter(vendor__city__iexact=user_location)
    
    # 2. Identify missing items for Fallback (Cairo)
    local_meal_ids = local_prices.values_list('meal_id', flat=True)
    other_meals = BaseMeal.objects.exclude(id__in=local_meal_ids)
    
    # Fallback logic: Fetch Cairo prices for meals that don't have local prices
    fallback_prices = MarketPrice.objects.filter(
        meal__in=other_meals,
        vendor__name="Market Average - Cairo"
    )
    
    # Serialize both
    market_data = MarketPriceSerializer(local_prices, many=True).data
    fallback_data = MarketPriceSerializer(fallback_prices, many=True).data
    
    # Flag fallback data as estimated
    for item in fallback_data:
        item['is_estimated'] = True
    
    # User Custom Meals
    custom_meals = UserCustomMeal.objects.filter(user=request.user)
    custom_data = UserCustomMealSerializer(custom_meals, many=True).data
    
    # Egyptian Meals (Ground Truth)
    egyptian_meals = EgyptianMeal.objects.all()
    egyptian_data = EgyptianMealUnifiedSerializer(egyptian_meals, many=True).data

    all_data = market_data + fallback_data + custom_data + egyptian_data

    # Sorting
    sort_mode = request.query_params.get('sort', 'default')
    
    if sort_mode == 'smart':
        # Efficiency Score = Calories / Price. High is better.
        def get_efficiency(item):
            price = item.get('price', 0)
            cals = item.get('calories', 0)
            if price > 0:
                try:
                    return float(cals) / float(price)
                except (ValueError, ZeroDivisionError):
                    return 0
            return 9999 
        all_data.sort(key=get_efficiency, reverse=True)
        
    elif sort_mode == 'price':
        # Sort by price ascending
        all_data.sort(key=lambda x: x.get('price', 0))
        
    elif sort_mode == 'price_desc':
        # Sort by price descending
        all_data.sort(key=lambda x: x.get('price', 0), reverse=True)

    return Response(all_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggest_meal_plan(request):
    mode = request.data.get('mode', 'diet') 
    max_price = float(request.data.get('budget', 1000000))
    calorie_goal = int(request.data.get('calories', 2000))
    
    prices = list(MarketPrice.objects.all())
    if len(prices) < 2:
        return Response({"error": "Not enough items in database"}, status=status.HTTP_400_BAD_REQUEST)
    
    suggestions = []
    
    if mode == 'budget':
        for _ in range(5):
            combo = random.sample(prices, min(2, len(prices)))
            total_price = sum(p.price_egp for p in combo)
            if total_price <= max_price:
                suggestions.append(MarketPriceSerializer(combo, many=True).data)
    else:
        for _ in range(5):
            combo = random.sample(prices, min(3, len(prices)))
            total_calories = sum(p.meal.calories for p in combo)
            if abs(total_calories - calorie_goal) < 500:
                suggestions.append(MarketPriceSerializer(combo, many=True).data)
                
    return Response(suggestions)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_food(request):
    query = request.query_params.get('query', '')
    if not query:
        return Response([])

    user_location = request.user.profile.current_location

    # 1. Search Global Meals (MarketPrice)
    # We search BaseMeal by name, then look up MarketPrice
    market_prices = MarketPrice.objects.filter(meal__name__icontains=query)
    
    # Filter to get best price per meal for the search results
    # Priority: Local -> Cairo -> Any
    global_results = []
    seen_meals = set()
    
    for mp in market_prices:
        if mp.meal_id in seen_meals:
            continue
            
        # For each meal found, get the best price for this user
        best_mp = MarketPrice.objects.filter(meal=mp.meal, vendor__city=user_location).first()
        is_estimated = False
        if not best_mp:
            best_mp = MarketPrice.objects.filter(meal=mp.meal, vendor__city='Cairo').first()
            is_estimated = True
        if not best_mp:
            best_mp = MarketPrice.objects.filter(meal=mp.meal).first()
            is_estimated = True
            
        if best_mp:
            global_results.append({
                'id': best_mp.meal.id,
                'name': best_mp.meal.name,
                'calories': best_mp.meal.calories,
                'protein': best_mp.meal.protein_g,
                'carbs': best_mp.meal.carbs_g,
                'fats': best_mp.meal.fats_g,
                'price': best_mp.price_egp,
                'type': 'global',
                'is_estimated': is_estimated,
                'category': best_mp.meal.meal_type,
                'restaurant_name': best_mp.vendor.name
            })
            seen_meals.add(mp.meal_id)

    # 2. Search Egyptian Meals
    egyptian_meals = EgyptianMeal.objects.filter(name_en__icontains=query)
    egyptian_results = []
    from .serializers import EgyptianMealUnifiedSerializer
    for em in egyptian_meals:
        # Use the unified format for search results
        data = EgyptianMealUnifiedSerializer(em).data
        data['type'] = 'egyptian'
        egyptian_results.append(data)

    # 3. Search Custom Meals
    custom_meals = UserCustomMeal.objects.filter(user=request.user, name__icontains=query)
    custom_results = []
    for cm in custom_meals:
        custom_results.append({
            'id': cm.id,
            'name': cm.name,
            'calories': cm.calories,
            'protein': cm.protein_g,
            'carbs': cm.carbs_g,
            'fats': cm.fats_g,
            'price': 0.0,
            'type': 'custom',
            'is_estimated': False,
            'category': 'Custom'
        })

    all_results = global_results + egyptian_results + custom_results
    serializer = UnifiedSearchSerializer(all_results, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_custom_meal(request):
    serializer = UserCustomMealSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard(request):
    date_str = request.query_params.get('date')
    if date_str:
        query_date = date.fromisoformat(date_str)
    else:
        query_date = date.today()

    profile = request.user.profile
    summary, _ = DailySummary.objects.get_or_create(user=profile, date=query_date)
    
    # Aggregating macros from MealLog for the specific date
    logs = MealLog.objects.filter(user=profile, date=query_date)
    
    total_protein = 0
    total_carbs = 0
    total_fats = 0
    
    for log in logs:
        if log.meal:
            total_protein += log.meal.protein_g * log.quantity
            total_carbs += log.meal.carbs_g * log.quantity
            total_fats += log.meal.fats_g * log.quantity
        elif log.custom_meal:
            total_protein += log.custom_meal.protein_g * log.quantity
            total_carbs += log.custom_meal.carbs_g * log.quantity
            total_fats += log.custom_meal.fats_g * log.quantity
        elif log.egyptian_meal:
            nutrition = log.egyptian_meal.calculate_nutrition()
            total_protein += nutrition['protein'] * log.quantity
            total_carbs += nutrition['carbs'] * log.quantity
            total_fats += nutrition['fat'] * log.quantity

    user = request.user
    full_name = f"{user.first_name} {user.last_name}".strip() if user.first_name else user.username
    
    return Response({
        "date": query_date.isoformat(),
        "budget": {
            "limit": profile.daily_budget_limit,
            "spent": summary.total_budget_spent,
            "remaining": max(0, profile.daily_budget_limit - summary.total_budget_spent)
        },
        "calories": {
            "goal": profile.calorie_goal,
            "eaten": summary.total_calories_consumed,
            "remaining": max(0, (profile.calorie_goal or 0) - summary.total_calories_consumed)
        },
        "macros": {
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fats, 1)
        },
        "water": summary.water_intake_cups,
        "location": profile.current_location,
        # User profile data for profile page
        "full_name": full_name,
        "current_weight": profile.weight,
        "height": profile.height,
        "age": profile.age,
        "gender": profile.gender,
        "goal_weight": profile.goal_weight,
        "ideal_weight": profile.ideal_weight,
        "activity_level": profile.activity_level,
        "preferred_brands": profile.preferred_brands,
        "is_premium": profile.is_premium,
        "body_fat": profile.body_fat_percentage,
        "diet_mode": profile.diet_mode,
        "weight_history": WeightLogSerializer(profile.weight_logs.all().order_by('date'), many=True).data
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_weight(request):
    profile = request.user.profile
    
    if request.method == 'GET':
        logs = WeightLog.objects.filter(user=profile).order_by('date')
        return Response({
            "current_weight": profile.weight,
            "ideal_weight": profile.ideal_weight,
            "history": WeightLogSerializer(logs, many=True).data
        })
        
    if request.method == 'POST':
        weight = float(request.data.get('weight'))
        log_date = request.data.get('date', date.today().isoformat())
        
        # Update current weight if it's the latest
        log, created = WeightLog.objects.update_or_create(
            user=profile,
            date=log_date,
            defaults={'weight': weight}
        )
        
        # If this is the newest entry, update profile weight
        latest_log = WeightLog.objects.filter(user=profile).order_by('-date').first()
        if latest_log and latest_log.date == date.fromisoformat(log_date):
            profile.weight = weight
            profile.save()
            
        return Response(WeightLogSerializer(log).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_water(request):
    action = request.data.get('action') # 'increment' or 'decrement'
    profile = request.user.profile
    summary, _ = DailySummary.objects.get_or_create(user=profile, date=date.today())
    
    if action == 'increment':
        summary.water_intake_cups += 1
    elif action == 'decrement' and summary.water_intake_cups > 0:
        summary.water_intake_cups -= 1
        
    summary.save()
    return Response({"water": summary.water_intake_cups})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_food(request):
    user_profile = request.user.profile
    meal_id = request.data.get('meal_id')
    is_custom = request.data.get('is_custom', False)
    is_egyptian = request.data.get('is_egyptian', False)
    quantity = float(request.data.get('quantity', 1.0))
    prep_style = request.data.get('preparation_style', 'STANDARD').upper()
    log_date = request.data.get('date', date.today().isoformat())

    try:
        if is_custom:
            cm = UserCustomMeal.objects.get(id=meal_id, user=request.user)
            MealLog.objects.create(
                user=user_profile,
                custom_meal=cm,
                quantity=quantity,
                prep_style=prep_style,
                date=log_date
            )
        elif is_egyptian:
            em = EgyptianMeal.objects.get(id=meal_id)
            MealLog.objects.create(
                user=user_profile,
                egyptian_meal=em,
                quantity=quantity,
                prep_style=prep_style,
                date=log_date
            )
        else:
            bm = BaseMeal.objects.get(id=meal_id)
            MealLog.objects.create(
                user=user_profile,
                meal=bm,
                quantity=quantity,
                prep_style=prep_style,
                date=log_date
            )
        return Response({"message": "Food logged successfully"}, status=status.HTTP_201_CREATED)
    except (BaseMeal.DoesNotExist, UserCustomMeal.DoesNotExist):
        return Response({"error": "Meal not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    user = request.user
    profile = user.profile
    
    today_logs = MealLog.objects.filter(user=profile, date=date.today())
    
    spent = 0
    eaten_calories = 0
    
    for log in today_logs:
        spent += log.final_price
        eaten_calories += log.final_calories
            
    return Response({
        "full_name": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
        "daily_budget_used": spent,
        "daily_budget_goal": profile.daily_budget_limit,
        "calories_eaten": eaten_calories,
        "calorie_goal": profile.calorie_goal,
        "remaining_budget": max(0, profile.daily_budget_limit - spent),
        "remaining_calories": max(0, (profile.calorie_goal or 0) - eaten_calories),
        "location": profile.current_location,
        "current_weight": profile.weight,
        "height": profile.height,
        "goal_weight": profile.goal_weight,
        "age": profile.age,
        "gender": profile.gender,
        "activity_level": profile.activity_level,
        "preferred_brands": profile.preferred_brands
    })

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_profile(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
        
    if request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({
        "message": "Welcome to CoinCal API",
        "endpoints": {
            "foods": "/api/foods/",
            "log": "/api/log/",
            "custom-meal": "/api/custom-meal/",
            "dashboard": "/api/dashboard/",
            "profile": "/api/profile/",
            "ingredients": "/api/ingredients/",
            "recipes": "/api/recipes/"
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_ingredients(request):
    query = request.query_params.get('query', '')
    if query:
        ingredients = Ingredient.objects.filter(name__icontains=query)
    else:
        ingredients = Ingredient.objects.all()[:15]
    
    serializer = IngredientSerializer(ingredients, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_recipes(request, pk=None):
    profile = request.user.profile
    
    if request.method == 'GET':
        if pk:
            recipe = get_object_or_404(Recipe, pk=pk, user=profile)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        else:
            recipes = Recipe.objects.filter(user=profile)
            serializer = RecipeSerializer(recipes, many=True)
            return Response(serializer.data)
            
    if request.method == 'POST':
        name = request.data.get('name')
        servings = int(request.data.get('servings', 1))
        items_data = request.data.get('items', [])
        
        recipe = Recipe.objects.create(user=profile, name=name, servings=servings)
        
        for item in items_data:
            ingredient = get_object_or_404(Ingredient, pk=item.get('ingredient_id'))
            RecipeItem.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=float(item.get('amount'))
            )
            
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    if request.method == 'DELETE' and pk:
        recipe = get_object_or_404(Recipe, pk=pk, user=profile)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_recipe(request):
    profile = request.user.profile
    recipe_id = request.data.get('recipe_id')
    date_val = request.data.get('date', date.today().isoformat())
    
    recipe = get_object_or_404(Recipe, pk=recipe_id, user=profile)
    # Re-fetch with prefetching if needed, but metrics logic handles it
    serializer = RecipeSerializer(recipe)
    metrics = serializer.data['metrics']
    
    MealLog.objects.create(
        user=profile,
        date=date_val,
        prep_style='STANDARD',
        final_calories=metrics['cals_per_plate'],
        final_price=metrics['cost_per_plate'],
        quantity=1.0
    )
    
    return Response({"message": "Recipe plate logged successfully!"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_plan(request):
    profile = request.user.profile
    if not profile.is_premium:
        return Response({"error": "Pro subscription required for Auto-Pilot Planner."}, status=status.HTTP_403_FORBIDDEN)
    
    weekly_budget = float(request.data.get('weekly_budget', 1000))
    # goal_calories is taken from profile if not provided
    goal_calories = int(request.data.get('goal_calories', profile.calorie_goal or 2000))
    
    # 1. Gather Candidates
    # Global items (MarketPrice)
    global_items = MarketPrice.objects.all().select_related('meal', 'vendor')
    # Custom items (UserCustomMeal)
    custom_items = UserCustomMeal.objects.filter(user=request.user)
    # Recipe items (Recipe)
    recipe_items = Recipe.objects.filter(user=profile).prefetch_related('items__ingredient')
    
    # Merged list of candidates with standardized fields
    candidates = []
    
    for item in global_items:
        candidates.append({
            'name': item.meal.name,
            'source': item.vendor.name,
            'calories': item.meal.calories,
            'price': item.price_egp,
            'carbs': item.meal.carbs_g,
            'type': 'global'
        })
        
    for item in custom_items:
        candidates.append({
            'name': item.name,
            'source': 'Custom',
            'calories': item.calories,
            'price': 0, # Assuming custom meals are "free" or price not tracked as raw ingredients yet
            'carbs': item.carbs_g,
            'type': 'custom'
        })
        
    for item in recipe_items:
        ser = RecipeSerializer(item)
        metrics = ser.data['metrics']
        candidates.append({
            'name': item.name,
            'source': 'Home',
            'calories': metrics['cals_per_plate'],
            'price': metrics['cost_per_plate'],
            'carbs': 0, # Carbs not tracked directly in Recipe metrics yet, but we could add it
            'type': 'recipe'
        })

    # 2. Filter by Diet Mode
    if profile.diet_mode == 'KETO':
        candidates = [c for c in candidates if c.get('carbs', 0) < 20]
    elif profile.diet_mode == 'VEGAN':
        # Simple heuristic: exclude meat-sounding names
        meat_keywords = ['meat', 'chicken', 'beef', 'lamb', 'fish', 'steak']
        candidates = [c for c in candidates if not any(k in c['name'].lower() for k in meat_keywords)]

    # 3. Greedy Selection Algorithm
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Breakfast", "Lunch", "Dinner"]
    schedule = {}
    
    daily_budget = weekly_budget / 7
    daily_cals = goal_calories
    
    for day in days:
        day_plan = {}
        for meal in meals:
            # Find a meal that fits (randomized greedy)
            valid_candidates = [c for c in candidates if c['price'] <= (daily_budget / 1.5)]
            if valid_candidates:
                selected = random.choice(valid_candidates)
                day_plan[meal] = {
                    "name": selected['name'],
                    "source": selected['source'],
                    "cost": selected['price'],
                    "calories": selected['calories']
                }
            else:
                day_plan[meal] = {"name": "Homemade Lentils", "source": "Staple", "cost": 5.0, "calories": 400}
        schedule[day] = day_plan
        
    return Response({
        "diet_mode": profile.diet_mode,
        "weekly_budget": weekly_budget,
        "schedule": schedule
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_analytics(request):
    profile = request.user.profile
    if not profile.is_premium:
        return Response({"error": "Pro subscription required for CFO Analytics."}, status=status.HTTP_403_FORBIDDEN)
    
    thirty_days_ago = date.today() - timedelta(days=30)
    logs = MealLog.objects.filter(user=profile, date__gte=thirty_days_ago)
    
    total_spent = logs.aggregate(Sum('final_price'))['final_price__sum'] or 0
    total_cals = logs.aggregate(Sum('final_calories'))['final_calories__sum'] or 0
    
    # Cost per Protein Gram (Heuristic calculation)
    # Since we don't track protein in MealLog directly yet, we look at the source
    cost_per_pro = 0
    # In a real app, MealLog would store protein. For this module, we'll return a simulated metric 
    # based on the user's logged items.
    cost_per_pro = (total_spent / 600) if total_spent > 0 else 0 # Mock 600g protein / month average
    
    # Source Breakdown
    home_count = logs.filter(meal__isnull=True).count()
    rest_count = logs.filter(meal__isnull=False).count()
    total_count = home_count + rest_count
    
    source_breakdown = {
        "Home Cooking": round((home_count / total_count * 100), 1) if total_count > 0 else 0,
        "Restaurants": round((rest_count / total_count * 100), 1) if total_count > 0 else 0
    }
    
    return Response({
        "total_spent_30d": round(total_spent, 2),
        "total_calories_30d": total_cals,
        "cost_per_protein_gram": round(cost_per_pro, 2),
        "source_breakdown": source_breakdown,
        "efficiency_score": "High" if cost_per_pro < 0.5 else "Moderate"
    })


# ============ Egyptian Meals API (Read-Only) ============

@api_view(['GET'])
@permission_classes([AllowAny])
def list_egyptian_meals(request):
    """
    List all Egyptian meals with calculated nutrition.
    
    Query params:
    - weight_g: Custom serving weight for nutrition calculation
    """
    meals = EgyptianMeal.objects.all().prefetch_related('recipe_items__ingredient')
    serializer = EgyptianMealListSerializer(meals, many=True)
    return Response({
        'count': meals.count(),
        'meals': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_egyptian_meal(request, meal_id):
    """
    Get detailed info for a specific Egyptian meal.
    
    Query params:
    - weight_g: Custom serving weight for nutrition calculation (default: meal's default)
    """
    try:
        meal = EgyptianMeal.objects.prefetch_related(
            'recipe_items__ingredient'
        ).get(meal_id=meal_id)
    except EgyptianMeal.DoesNotExist:
        return Response(
            {'error': f'Meal not found: {meal_id}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get custom weight if provided
    weight_g = request.query_params.get('weight_g')
    context = {'weight_g': int(weight_g)} if weight_g else {}
    
    serializer = EgyptianMealSerializer(meal, context=context)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def calculate_meal_nutrition(request, meal_id):
    """
    Calculate nutrition for a meal at a specific weight.
    Pure calculation endpoint - no database storage.
    
    Query params:
    - weight_g: Serving weight in grams (required)
    """
    weight_g = request.query_params.get('weight_g')
    if not weight_g:
        return Response(
            {'error': 'weight_g query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        meal = EgyptianMeal.objects.prefetch_related(
            'recipe_items__ingredient'
        ).get(meal_id=meal_id)
        nutrition = meal.calculate_nutrition(int(weight_g))
        
        return Response({
            'meal_id': meal_id,
            'meal_name': meal.name_en,
            'weight_g': int(weight_g),
            'nutrition': nutrition
        })
    except EgyptianMeal.DoesNotExist:
        return Response(
            {'error': f'Meal not found: {meal_id}'},
            status=status.HTTP_404_NOT_FOUND
        )


# ============ Daily Prices API (Secure POST) ============

@api_view(['POST'])
@permission_classes([AllowAny])  # In production, use API key authentication
def receive_daily_prices(request):
    """
    Secure endpoint to receive price data from price_anchor.py scraper.
    
    Expected payload:
    {
        "date": "2026-01-30",
        "source": "carrefour_egypt",
        "items": [
            {"item_id": "rice_1kg", "item_name": "Rice (1kg)", "price_egp": 45.99, ...},
            ...
        ]
    }
    """
    # Validate API key (simple auth - use proper auth in production)
    api_key = request.headers.get('X-API-Key')
    expected_key = 'COINCAL_PRICE_ANCHOR_2026'  # In production, use environment variable
    
    if api_key != expected_key:
        return Response(
            {'error': 'Invalid or missing API key'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = DailyPriceCreateSerializer(data=request.data)
    if serializer.is_valid():
        prices = serializer.save()
        return Response({
            'status': 'success',
            'message': f'Saved {len(prices)} prices',
            'date': request.data.get('date'),
            'source': request.data.get('source')
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_daily_prices(request):
    """
    Get the latest daily prices for validation.
    
    Query params:
    - date: Specific date (default: today)
    - item_id: Filter by item ID
    """
    from datetime import date as dt_date
    
    date_str = request.query_params.get('date')
    if date_str:
        try:
            query_date = dt_date.fromisoformat(date_str)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        query_date = dt_date.today()
    
    prices = DailyPrice.objects.filter(date=query_date)
    
    item_id = request.query_params.get('item_id')
    if item_id:
        prices = prices.filter(item_id=item_id)
    
    serializer = DailyPriceSerializer(prices, many=True)
    return Response({
        'date': query_date.isoformat(),
        'count': prices.count(),
        'prices': serializer.data
    })
