from decimal import Decimal

def calculate_bmr(weight, height, age, gender, body_fat=None, is_premium=False):
    """
    Calculates Basal Metabolic Rate using Mifflin-St Jeor or Katch-McArdle (if BF% provided).
    All inputs should be converted to Decimal internally for precision.
    """
    w = Decimal(str(weight))
    h = Decimal(str(height))
    a = Decimal(str(age))
    
    if is_premium and body_fat:
        bf = Decimal(str(body_fat))
        # Katch-McArdle Formula
        lean_mass = w * (Decimal('1') - (bf / Decimal('100')))
        return Decimal('370') + (Decimal('21.6') * lean_mass)
    else:
        # Mifflin-St Jeor Formula
        if gender == 'M':
            return (Decimal('10') * w) + (Decimal('6.25') * h) - (Decimal('5') * a) + Decimal('5')
        else:
            return (Decimal('10') * w) + (Decimal('6.25') * h) - (Decimal('5') * a) - Decimal('161')

def calculate_tdee(bmr, activity_level):
    """
    Applies activity multiplier to BMR.
    """
    multipliers = {
        'Sedentary': Decimal('1.2'),
        'Light': Decimal('1.375'),
        'Lightly Active': Decimal('1.375'),
        'Moderate': Decimal('1.55'),
        'Moderately Active': Decimal('1.55'),
        'Active': Decimal('1.725'),
        'Very Active': Decimal('1.725'),
        'Extremely Active': Decimal('1.9'),
    }
    return bmr * multipliers.get(activity_level, Decimal('1.2'))

def get_caloric_balance(tdee, current_weight, goal_weight):
    """
    Determines calorie goal based on current vs goal weight (+/- 500 kcal).
    """
    if goal_weight < current_weight:
        return int(tdee - Decimal('500'))
    elif goal_weight > current_weight:
        return int(tdee + Decimal('500'))
    else:
        return int(tdee)

def calculate_macro_calories(protein, carbs, fat):
    """
    Standard 4-4-9 rule for calorie calculation.
    """
    p = Decimal(str(protein))
    c = Decimal(str(carbs))
    f = Decimal(str(fat))
    return (p * Decimal('4')) + (c * Decimal('4')) + (f * Decimal('9'))
