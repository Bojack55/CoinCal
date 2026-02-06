from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import DailyPrice, EgyptianMeal, Ingredient, MealRecipe
from datetime import date

class Phase1DataLayerTests(APITestCase):
    """Tests for Phase 1: Data Layer (Scraper & Receiver)"""
    
    def setUp(self):
        self.prices_url = reverse('receive-prices')
        self.api_key = 'COINCAL_PRICE_ANCHOR_2026'

    def test_receive_prices_success(self):
        """Test successful price submission from scraper"""
        data = {
            "date": "2026-02-01",
            "source": "carrefour_egypt",
            "items": [
                {"item_id": "rice_1kg", "item_name": "Rice (1kg)", "price_egp": 45.50, "unit": "kg"},
                {"item_id": "sugar_1kg", "item_name": "Sugar (1kg)", "price_egp": 27.00, "unit": "kg"}
            ]
        }
        response = self.client.post(self.prices_url, data, format='json', HTTP_X_API_KEY=self.api_key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyPrice.objects.count(), 2)
        self.assertEqual(DailyPrice.objects.get(item_id='rice_1kg').price_egp, 45.50)

    def test_receive_prices_unauthorized(self):
        """Test price submission with invalid API key"""
        data = {"date": "2026-02-01", "source": "test", "items": []}
        response = self.client.post(self.prices_url, data, format='json', HTTP_X_API_KEY='WRONG_KEY')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receive_prices_negative_validation(self):
        """Test rejection of negative prices"""
        data = {
            "date": "2026-02-01",
            "source": "carrefour_egypt",
            "items": [{"item_id": "bad_item", "item_name": "Bad", "price_egp": -10.00}]
        }
        response = self.client.post(self.prices_url, data, format='json', HTTP_X_API_KEY=self.api_key)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

class Phase2LogicLayerTests(APITestCase):
    """Tests for Phase 2: API & Logic (Nutrition & Retrieval)"""

    def setUp(self):
        # Create test ingredient
        self.rice = Ingredient.objects.create(
            name="Rice",
            calories_per_100g=360,
            protein_per_100g=7.0,
            carbs_per_100g=80.0,
            fat_per_100g=0.5
        )
        
        # Create test meal (100% Rice)
        self.meal = EgyptianMeal.objects.create(
            meal_id="test_rice_meal",
            name_en="Plain Rice",
            default_serving_weight_g=200
        )
        MealRecipe.objects.create(meal=self.meal, ingredient=self.rice, percentage=100)

    def test_meal_list(self):
        """Test retrieval of Egyptian meals"""
        url = reverse('egyptian-meals-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if our test meal is in the list
        meal_names = [m['name_en'] for m in response.data['meals']]
        self.assertIn("Plain Rice", meal_names)

    def test_nutrition_calculation_accuracy(self):
        """Test core math: (Base / 100) * weight"""
        url = reverse('egyptian-meal-calculate', kwargs={'meal_id': 'test_rice_meal'})
        # Test for 200g
        response = self.client.get(url, {'weight_g': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        nutrition = response.data['nutrition']
        # 360 cal/100g -> 720 cal/200g
        self.assertEqual(nutrition['calories'], 720.0)
        # 7.0 p/100g -> 14.0 p/200g
        self.assertEqual(nutrition['protein'], 14.0)

    def test_449_rule_verification(self):
        """Verify result against the '4-4-9 Rule' (Precision Check)"""
        url = reverse('egyptian-meal-calculate', kwargs={'meal_id': 'test_rice_meal'})
        response = self.client.get(url, {'weight_g': 100})
        
        nut = response.data['nutrition']
        calculated_cals = (nut['protein'] * 4) + (nut['carbs'] * 4) + (nut['fat'] * 9)
        
        # Result should be close to stated calories (within 5% due to rounding/database precision)
        diff = abs(nut['calories'] - calculated_cals)
        self.assertLess(diff / nut['calories'], 0.05, f"4-4-9 Rule mismatch too high: {nut['calories']} vs {calculated_cals}")
