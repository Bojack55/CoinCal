"""
Translation utility for automatic bilingual meal names.

Uses deep-translator library for Arabic ↔ English translation.
Auto-detects language and translates meal names on creation.
"""
import re
from deep_translator import GoogleTranslator


def contains_arabic(text):
    """Check if text contains Arabic characters."""
    if not text:
        return False
    # Arabic Unicode range
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
    return bool(arabic_pattern.search(text))


def auto_translate_meal_name(name):
    """
    Auto-detect language and translate meal name to the other language.
    
    Args:
        name (str): Meal name in either English or Arabic
        
    Returns:
        tuple: (english_name, arabic_name)
            - If input is Arabic: (translated_to_english, original_arabic)
            - If input is English: (original_english, translated_to_arabic)
            - If translation fails: (name, None) or (None, name) with fallback to input
    
    Examples:
        >>> auto_translate_meal_name("Protein Bowl")
        ("Protein Bowl", "وعاء البروتين")
        
        >>> auto_translate_meal_name("سلطة دجاج")
        ("Chicken Salad", "سلطة دجاج")
    """
    if not name or not name.strip():
        return ("", "")
    
    name = name.strip()
    
    try:
        if contains_arabic(name):
            # Input is Arabic → Translate to English
            translator = GoogleTranslator(source='ar', target='en')
            english_name = translator.translate(name)
            return (english_name, name)
        else:
            # Input is English → Translate to Arabic
            translator = GoogleTranslator(source='en', target='ar')
            arabic_name = translator.translate(name)
            return (name, arabic_name)
            
    except Exception as e:
        # Translation failed - return original with None for the other language
        print(f"Translation error for '{name}': {str(e)}")
        if contains_arabic(name):
            return (None, name)  # Keep Arabic, no English
        else:
            return (name, None)  # Keep English, no Arabic


def translate_text(text, source_lang, target_lang):
    """
    Translate text from source language to target language.
    
    Args:
        text (str): Text to translate
        source_lang (str): Source language code ('en', 'ar')
        target_lang (str): Target language code ('en', 'ar')
        
    Returns:
        str: Translated text, or None if translation fails
    """
    if not text or not text.strip():
        return None
        
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text.strip())
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return None
