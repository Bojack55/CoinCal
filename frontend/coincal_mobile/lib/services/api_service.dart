import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/meal_model.dart';

class ApiService {
  // Environment-based API URL
  // Dev: flutter run (uses default localhost)
  // Prod: flutter build --dart-define=API_URL=http://Moaz55.pythonanywhere.com/api
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://127.0.0.1:8000/api',
  );

  static String? token; // To be set after login

  static Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (token != null) 'Authorization': 'Token $token',
  };

  static Future<List<Meal>> fetchFoodItems() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/foods/'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((item) => Meal.fromJson(item)).toList();
      } else {
        throw Exception('Failed to fetch food items: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection Error: $e');
    }
  }

  static Future<List<Meal>> getEgyptianMeals() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/egyptian-meals/'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List mealsJson = data['meals'];
        return mealsJson.map((json) => Meal.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load meals: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to API: $e');
    }
  }

  static Future<Nutrition> calculateNutrition(String mealId, int weight) async {
    try {
      final response = await http.get(
        Uri.parse(
          '$baseUrl/egyptian-meals/$mealId/calculate/?weight_g=$weight',
        ),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Nutrition.fromJson(data['nutrition']);
      } else {
        throw Exception(
          'Failed to calculate nutrition: ${response.statusCode}',
        );
      }
    } catch (e) {
      throw Exception('Calculation error: $e');
    }
  }

  static Future<List<dynamic>> searchFood(String query) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/search-food/?query=$query'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Search failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Search error: $e');
    }
  }

  static Future<Map<String, dynamic>> updateProfile(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/profile/'),
        headers: _headers,
        body: json.encode(data),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Profile update failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Profile update error: $e');
    }
  }

  static Future<Map<String, dynamic>> getDashboard({String? date}) async {
    try {
      final url = date != null
          ? '$baseUrl/dashboard/?date=$date'
          : '$baseUrl/dashboard/';
      final response = await http.get(Uri.parse(url), headers: _headers);
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Dashboard load failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Dashboard error: $e');
    }
  }

  static Future<void> logFood(int mealId, double quantity, String type) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/log/'),
        headers: _headers,
        body: json.encode({
          'meal_id': mealId,
          'quantity': quantity,
          'is_custom': type == 'custom',
          'is_egyptian': type == 'egyptian',
          'date': DateTime.now().toIso8601String().split('T')[0],
        }),
      );
      if (response.statusCode != 201) {
        final errorData = json.decode(response.body);
        throw Exception(
          '${errorData['error']} \n\n${errorData['traceback'] ?? ''}',
        );
      }
    } catch (e) {
      throw Exception('Log failed: $e');
    }
  }

  static Future<Map<String, dynamic>> updateWater(String action) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/water/'),
        headers: _headers,
        body: json.encode({'action': action}),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Water update failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Water error: $e');
    }
  }

  static Future<void> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'username': username, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        token = data['token'];
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Login error: $e');
    }
  }

  static Future<void> register({
    required String username,
    required String email,
    required String password,
    double weight = 70.0,
    double? targetWeight,
    double height = 170.0,
    int age = 25,
    String gender = 'M',
    double dailyBudget = 100.0,
    String location = 'Cairo',
    String activityLevel = 'Sedentary',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'email': email,
          'password': password,
          'current_weight': weight,
          'goal_weight': targetWeight ?? weight,
          'height': height,
          'age': age,
          'gender': gender,
          'daily_budget': dailyBudget,
          'location': location,
          'activity_level': activityLevel,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        token = data['token'];
      } else {
        final errorData = json.decode(response.body);
        throw Exception(errorData['error'] ?? 'Registration failed');
      }
    } catch (e) {
      throw Exception('Registration error: $e');
    }
  }

  static Future<List<dynamic>> getWeightHistory() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/weight/'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['history'] ?? [];
      } else {
        throw Exception('Failed to fetch weight history');
      }
    } catch (e) {
      throw Exception('Weight history error: $e');
    }
  }

  static Future<void> logWeight(double weight) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/weight/'),
        headers: _headers,
        body: json.encode({'weight': weight}),
      );
      if (response.statusCode != 201) {
        throw Exception('Weight log failed');
      }
    } catch (e) {
      throw Exception('Weight log error: $e');
    }
  }

  static Future<List<dynamic>> searchIngredients(String query) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ingredients/?query=$query'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to search ingredients');
      }
    } catch (e) {
      throw Exception('Ingredient search error: $e');
    }
  }

  static Future<Map<String, dynamic>> createRecipe(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/recipes/'),
        headers: _headers,
        body: json.encode(data),
      );
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to create recipe: ${response.body}');
      }
    } catch (e) {
      throw Exception('Recipe creation error: $e');
    }
  }

  static Future<Meal> createCustomMeal(Map<String, dynamic> mealData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/custom-meal/'),
        headers: _headers,
        body: json.encode(mealData),
      );

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        return Meal.fromJson(data);
      } else {
        throw Exception('Failed to create custom meal: ${response.body}');
      }
    } catch (e) {
      throw Exception('Custom meal creation error: $e');
    }
  }

  static Future<Meal> createCustomMealFromIngredients(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/custom-meal-from-ingredients/'),
        headers: _headers,
        body: json.encode(data),
      );

      if (response.statusCode == 201) {
        final responseData = json.decode(response.body);
        return Meal.fromJson(responseData);
      } else {
        throw Exception(
          'Failed to create custom meal from ingredients: ${response.body}',
        );
      }
    } catch (e) {
      throw Exception('Custom meal from ingredients error: $e');
    }
  }

  static Future<void> logRecipe(int recipeId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/log-recipe/'),
        headers: _headers,
        body: json.encode({'recipe_id': recipeId}),
      );
      if (response.statusCode != 201) {
        throw Exception('Failed to log recipe');
      }
    } catch (e) {
      throw Exception('Recipe logging error: $e');
    }
  }

  static Future<Map<String, dynamic>> generateDietPlan(
    double budget,
    int calories, {
    int mealsCount = 3,
    bool includeCustom = false,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/generate-plan/'),
        headers: _headers,
        body: json.encode({
          'daily_budget': budget,
          'target_calories': calories,
          'meals_count': mealsCount,
          'include_custom': includeCustom,
        }),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to generate diet plan');
      }
    } catch (e) {
      throw Exception('Diet plan generation error: $e');
    }
  }

  static Future<List<dynamic>> getSmartFeed() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/smart-feed/'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to fetch smart feed');
      }
    } catch (e) {
      throw Exception('Smart feed error: $e');
    }
  }

  static Future<List<dynamic>> getMealHistory() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/meal-history/'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to fetch meal history');
      }
    } catch (e) {
      throw Exception('Meal history error: $e');
    }
  }

  static Future<List<dynamic>> getTimeline(DateTime start, DateTime end) async {
    final startStr = start.toIso8601String().split('T')[0];
    final endStr = end.toIso8601String().split('T')[0];
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/timeline/?start=$startStr&end=$endStr'),
        headers: _headers,
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to fetch timeline');
      }
    } catch (e) {
      throw Exception('Timeline error: $e');
    }
  }

  static Future<Map<String, dynamic>> toggleDayStatus(DateTime date) async {
    final dateStr = date.toIso8601String().split('T')[0];
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/toggle-day-status/'),
        headers: _headers,
        body: json.encode({'date': dateStr}),
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to toggle status');
      }
    } catch (e) {
      throw Exception('Toggle status error: $e');
    }
  }
}
