# CoinCal - Nutrition Budget Tracker

![CoinCal Logo](frontend/coincal_mobile/assets/images/logo.png)

A comprehensive nutrition and budget tracking application that helps you master your plate and budget. Built with Flutter (mobile) and Django (backend).

## Features

### Core Functionality
- 💰 **Budget Tracking**: Monitor daily spending on meals with real-time budget calculations
- 🍎 **Calorie Tracking**: Track calories eaten vs. daily goals with macro breakdowns
- 📊 **Smart Dashboard**: Visual HUD cards showing budget, calories, and progress
- 💧 **Hydration Tracker**: Log water intake with +/- controls
- ⚖️ **Weight Management**: Track weight over time with chart visualization
- 🗓️ **Timeline View**: Last 7 days quick navigation

### Food Management
- 🔍 **Smart Food Database**: Browse Egyptian meals with calculated nutrition
- 🏪 **Restaurant Integration**: Prices and availability by location
- 🏷️ **Smart Badges**: Auto-detect "Best Value" and "High Protein" options
- 📝 **Meal Logging**: One-tap meal logging with preparation styles
- 🔀 **Sort Options**: Default, Smart Efficiency, Price ranges

### Advanced Features
- 🍽️ **Recipe Studio**: Create custom recipes with ingredient calculator
- 📈 **Financial Analytics**: Visualize spending patterns
- 🎯 **Diet Planner**: AI-powered meal suggestions
- ⚡ **Quick Log**: Fast meal entry via calculator
- 📍 **Location-Based Pricing**: Automatic price adjustments

## Tech Stack

### Frontend (Flutter)
- **Framework**: Flutter 3.10.7
- **State Management**: Provider pattern
- **Charts**: fl_chart
- **HTTP**: http package
- **Storage**: shared_preferences

### Backend (Django)
- **Framework**: Django 6.0
- **Database**: SQLite (development)
- **API**: REST endpoints (30+)
- **Authentication**: Token-based auth

## Project Structure

```
CoinCal/
├── backend/                 # Django backend
│   ├── api/                # Main API app
│   │   ├── models.py      # Database models
│   │   ├── views.py       # API endpoints
│   │   ├── serializers.py # Data serialization
│   │   └── urls.py        # URL routing
│   ├── fixtures/          # Data fixtures
│   └── manage.py
│
└── frontend/
    └── coincal_mobile/    # Flutter app
        ├── lib/
        │   ├── models/    # Data models
        │   ├── providers/ # State management
        │   ├── screens/   # UI screens (15 total)
        │   ├── services/  # API & business logic
        │   ├── widgets/   # Reusable components
        │   └── theme/     # App theming
        └── assets/
            └── images/    # Logo and assets
```

## Getting Started

### Prerequisites
- Flutter SDK 3.10.7+
- Python 3.10+
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers

# Run migrations
python manage.py migrate

# Load initial data
python manage.py loaddata fixtures/egyptian_master_menu.json

# Start server
python manage.py runserver 8000
```

### Frontend Setup

```bash
cd frontend/coincal_mobile

# Install dependencies
flutter pub get

# Run on web
flutter run -d chrome

# Or build for production
flutter build web --release
```

## API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login

### Dashboard
- `GET /api/dashboard/` - Get dashboard data
- `GET /api/dashboard/?date=YYYY-MM-DD` - Get data for specific date

### Food Management
- `GET /api/foods/` - List all foods
- `POST /api/log/` - Log a meal
- `GET /api/search-food/?query=<term>` - Search foods
- `POST /api/custom-meal/` - Create custom meal

### Tracking
- `POST /api/water/` - Update water intake
- `GET /api/weight/` - Get weight history
- `POST /api/weight/` - Log weight

### Egyptian Meals
- `GET /api/egyptian-meals/` - List all Egyptian meals
- `GET /api/egyptian-meals/<id>/` - Get meal details
- `GET /api/egyptian-meals/<id>/calculate/?weight_g=<grams>` - Calculate nutrition

## Configuration

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (lib/config/api_config.dart)
```dart
static String get baseUrl => 'http://127.0.0.1:8000/api';
```

## Testing

The project has been professionally tested with:
- ✅ 36 test cases executed
- ✅ Zero bugs found
- ✅ Production build verified
- ✅ Code quality: Excellent

See `test_report.md` for full test documentation.

## Screenshots

_Coming soon_

## License

Private Project

## Author

**Bojack55**

## Acknowledgments

- Built with ❤️ for nutrition tracking
- Logo designed with Golden Ratio principles
- Egyptian meals database curated for local market
