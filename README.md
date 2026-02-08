# 🪙 CoinCal - Master Your Plate & Budget

**CoinCal** is a smart nutrition and budget tracking application designed specifically for the Egyptian market. It helps users achieve their fitness goals without breaking the bank by balancing calorie targets with daily financial limits.

## 🚀 Key Features

### 🍎 Smart Nutrition & Budgeting
*   **Dual Tracking**: Monitor both your daily calorie intake and food spending in real-time.
*   **Market Integration**: Live prices for local Egyptian ingredients and meals (e.g., Koshary, Foul, Falafel).
*   **Efficiency Score**: "Smart Sort" algorithms to find meals that give you the most protein/calories per EGP.

### 🍽️ Meal Management
*   **Kitchen & Pantry**: Manage your inventory of ingredients.
*   **Recipe Studio**: Create custom recipes from your pantry items and calculate their exact cost and nutrition.
*   **Egyptian Food Database**: comprehensive database of local dishes with accurate macro-nutrient data.
*   **Price Review**: Community-driven price validation system.

### 📅 Planning & Tracking
*   **AI Diet Planner**: Generate weekly diet plans that strictly adhere to your budget and calorie limits.
*   **Cheat Day Mode**: Toggle "Cheat Day" to pause strict tracking while keeping your streaks alive.
*   **Hydration Tracker**: Gamified water tracking with streaks, levels, and achievements (e.g., "Hydro Hero").
*   **Weight Tracker**: Visual charts to monitor your weight progress over time.

### 🌍 Localization
*   **Bilingual Support**: Fully localized for **English** and **Arabic (العربية)**.
*   **Currency**: Optimized for EGP (Egyptian Pound).

---

## 🛠️ Tech Stack

### Frontend (Mobile)
*   **Framework**: [Flutter](https://flutter.dev/)
*   **State Management**: Provider
*   **Charts**: `fl_chart` for visualization
*   **Localization**: `easy_localization`
*   **Navigation**: Custom Bottom Navigation Shell

### Backend (API)
*   **Framework**: [Django](https://www.djangoproject.com/) & Django REST Framework (DRF)
*   **Database**: SQLite (Development)
*   **Authentication**: Token-based Auth

---

## 📂 Project Structure

```
CoinCal/
├── backend/                 # Django API & Admin
│   ├── api/                 # Core Business Logic (Views, Models, Serializers)
│   ├── fixtures/            # Pre-loaded Egyptian Meal Data
│   └── manage.py            # Django Entry Point
│
└── frontend/
    └── coincal_mobile/      # Flutter Mobile App
        ├── lib/
        │   ├── screens/     # UI Screens (Kitchen, Diet Planner, Profile, etc.)
        │   ├── services/    # API Integration Service
        │   ├── models/      # Data Models
        │   └── assets/      # Translations & Images
        └── pubspec.yaml     # Flutter Dependencies
```

---

## ⚡ Getting Started

### Prerequisites
*   Python 3.10+
*   Flutter SDK (Latest Stable)
*   Git

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Migrations
python manage.py migrate

# Load Initial Data (Egyptian Meals)
python manage.py loaddata fixtures/egyptian_master_menu.json

# Start the Server
python manage.py runserver 0.0.0.0:8000
```

### 2. Frontend Setup

```bash
# Navigate to flutter project
cd frontend/coincal_mobile

# Install dependencies
flutter pub get

# Generate Localization Keys (if needed)
flutter pub run easy_localization:generate

# Run on Emulator/Device
flutter run
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/dashboard/` | Get daily summary (calories, budget, macros) |
| **GET** | `/api/foods/` | List all foods with efficiency scores |
| **POST** | `/api/log/` | Log a meal to your daily history |
| **POST** | `/api/custom-meal-from-ingredients/` | Create a custom meal from pantry items |
| **POST** | `/api/generate-plan/` | Generate a budget-friendly diet plan |
| **POST** | `/api/toggle-day-status/` | Switch between Standard and Cheat Day |
| **POST** | `/api/water/` | Increment water intake |
| **GET** | `/api/egyptian-meals/` | Search local Egyptian database |

---

## 🛡️ License

Private Project. All specific food data and pricing algorithms are proprietary.
