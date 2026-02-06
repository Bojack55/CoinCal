"""
Utility functions for meal categorization and food-related operations.

This module contains reusable helpers that support the main views,
particularly for Egyptian cuisine detection and categorization.
"""

# Egyptian cuisine keyword database for meal detection
EGYPTIAN_MEAL_KEYWORDS = [
    'koshary', 'koshari', 'foul', 'beans', 'falafel', 'tameya',
    'liver', 'kebda', 'sausage', 'sogoq', 'kofta', 'hawawshi',
    'fiteer', 'mahshi', 'mombar', 'baba gan', 'zalabya', 'om ali',
    'rice pudding', 'roz', 'mesaka', 'macaroni', 'bechamel', 'tarab',
    'shish', 'fattah', 'bolti', 'shrimp', 'calamari',
    'shawerma', 'molokhia', 'lentil', 'soup'
]


def is_egyptian_meal(meal_name):
    """
    Check if a meal name matches Egyptian cuisine keywords.
    
    Args:
        meal_name (str): Name of the meal to check
        
    Returns:
        bool: True if meal matches Egyptian keywords, False otherwise
        
    Example:
        >>> is_egyptian_meal("Koshary Special")
        True
        >>> is_egyptian_meal("Pizza Margherita")
        False
    """
    normalized_name = meal_name.lower()
    return any(keyword in normalized_name for keyword in EGYPTIAN_MEAL_KEYWORDS)


def categorize_egyptian_meal(name, meal_id):
    """
    Categorize an Egyptian meal by type based on name and meal ID.
    
    Determines whether a meal is breakfast, lunch, dinner, snack, or street food
    based on common Egyptian cuisine patterns.
    
    Args:
        name (str): Meal name (English or Arabic)
        meal_id (str): Unique meal identifier
        
    Returns:
        str: Category name - one of: 'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Street Food'
        
    Example:
        >>> categorize_egyptian_meal("Foul Medames", "foul_beans_01")
        'Breakfast'
        >>> categorize_egyptian_meal("Koshary", "koshary_large")
        'Street Food'
    """
    normalized_name = name.lower()
    normalized_id = meal_id.lower()
    
    # Breakfast items
    breakfast_keywords = ['foul', 'tameya', 'beid', 'shakshuka', 'cheese', 'falafel']
    if any(keyword in normalized_id or keyword in normalized_name for keyword in breakfast_keywords):
        return 'Breakfast'
    
    # Lunch mains
    lunch_keywords = ['kebda', 'liver', 'sogoq', 'sausage', 'kofta', 'fattah', 'mahshi']
    if any(keyword in normalized_id or keyword in normalized_name for keyword in lunch_keywords):
        return 'Lunch'
    
    # Dinner/Heavy meals
    dinner_keywords = ['hawawshi', 'bechamel', 'molokhia', 'tarab', 'bolti', 'shrimp', 'calamari']
    if any(keyword in normalized_id or keyword in normalized_name for keyword in dinner_keywords):
        return 'Dinner'
    
    # Desserts/Snacks
    dessert_keywords = ['om ali', 'zalabya', 'rice pudding', 'roz bi laban', 'fiteer']
    if any(keyword in normalized_id or keyword in normalized_name for keyword in dessert_keywords):
        return 'Snack'
    
    # Street food (Koshary, etc.)
    street_food_keywords = ['koshary', 'koshari', 'shawerma']
    if any(keyword in normalized_id or keyword in normalized_name for keyword in street_food_keywords):
        return 'Street Food'
    
    # Default to lunch if no match
    return 'Lunch'


def calculate_meal_efficiency(calories, price_egp):
    """
    Calculate nutritional efficiency (calories per Egyptian Pound).
    
    Args:
        calories (int|float): Total calories in the meal
        price_egp (float): Price in Egyptian Pounds
        
    Returns:
        float: Calories per EGP, or 0 if price is invalid
        
    Example:
        >>> calculate_meal_efficiency(500, 25)
        20.0
    """
    try:
        price = float(price_egp)
        if price > 0:
            return float(calories) / price
        return 9999  # Very high efficiency for free items
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
