
# City to Category Mapping
# Keys are lowercased city names (English and Arabic)
CITY_CATEGORIES = {
    # Metro (1.0)
    'cairo': 'metro', 'el qahira': 'metro', 'القاهرة': 'metro',
    'giza': 'metro', 'el giza': 'metro', 'الجيزة': 'metro',
    'new cairo': 'metro', 'القاهرة الجديدة': 'metro',
    '6th of october': 'metro', 'october': 'metro', 'السادس من أكتوبر': 'metro', 'أكتوبر': 'metro',
    'nasr city': 'metro', 'مدينة نصر': 'metro',
    'heliopolis': 'metro', 'masr el gedida': 'metro', 'مصر الجديدة': 'metro',
    'maadi': 'metro', 'el maadi': 'metro', 'المعادي': 'metro',
    'shoubra': 'metro', 'shubra': 'metro', 'شبرا': 'metro',
    'helwan': 'metro', 'حلوان': 'metro',

    # Major City (0.95)
    'alexandria': 'major_city', 'alex': 'major_city', 'الإسكندرية': 'major_city',
    'port said': 'major_city', 'bur said': 'major_city', 'بورسعيد': 'major_city',
    'suez': 'major_city', 'el suez': 'major_city', 'السويس': 'major_city',
    'ismailia': 'major_city', 'el ismailia': 'major_city', 'الإسماعيلية': 'major_city',
    'mansoura': 'major_city', 'el mansoura': 'major_city', 'المنصورة': 'major_city',

    # Regional (0.88)
    'tanta': 'regional', 'el tanta': 'regional', 'طنطا': 'regional',
    'zagazig': 'regional', 'el zagazig': 'regional', 'الزقازيق': 'regional',
    'damanhour': 'regional', 'damanhur': 'regional', 'دمنهور': 'regional',
    'kafr el sheikh': 'regional', 'kafr el-sheikh': 'regional', 'كفر الشيخ': 'regional',
    'shibin el kom': 'regional', 'shebin el kom': 'regional', 'شبين الكوم': 'regional',
    'damietta': 'regional', 'domyat': 'regional', 'دمياط': 'regional',
    'benha': 'regional', 'banha': 'regional', 'بنها': 'regional',

    # Provincial (0.80)
    'aswan': 'provincial', 'أسوان': 'provincial',
    'luxor': 'provincial', 'el luxor': 'provincial', 'الأقصر': 'provincial',
    'sohag': 'provincial', 'suhag': 'provincial', 'سوهاج': 'provincial',
    'qena': 'provincial', 'ena': 'provincial', 'قنا': 'provincial',
    'minya': 'provincial', 'el minya': 'provincial', 'المنيا': 'provincial',
    'beni suef': 'provincial', 'bani sweif': 'provincial', 'بني سويف': 'provincial',
    'fayoum': 'provincial', 'el fayoum': 'provincial', 'الفيوم': 'provincial',
    'asyut': 'provincial', 'assiut': 'provincial', 'أسيوط': 'provincial',
    'marsa matrouh': 'provincial', 'matrouh': 'provincial', 'مرسى مطروح': 'provincial', 'مطروح': 'provincial',
    'el arish': 'provincial', 'arish': 'provincial', 'العريش': 'provincial',
    'hurghada': 'provincial', 'el gouna': 'provincial', 'الغردقة': 'provincial',
    'sharm el sheikh': 'provincial', 'sharm': 'provincial', 'شرم الشيخ': 'provincial',
}

LOCATION_MULTIPLIERS = {
    'metro': 1.0,
    'major_city': 0.95,
    'regional': 0.88,
    'provincial': 0.80,
    'rural': 0.70,
}

LOCATION_CHOICES = [
    ('metro', 'Metropolitan (Cairo/Giza)'),
    ('major_city', 'Major City'),
    ('regional', 'Regional City'),
    ('provincial', 'Provincial City'),
    ('rural', 'Rural Area'),
]

def get_city_category(city_name):
    """
    Get the price category for a given city name.
    Defaults to 'metro' (Cairo prices) if unknown to be safe/standard.
    """
    if not city_name:
        return 'metro'
    
    normalized = city_name.lower().strip()
    return CITY_CATEGORIES.get(normalized, 'metro')

def get_multiplier_for_category(category):
    return LOCATION_MULTIPLIERS.get(category, 1.0)
