
import json
import os

files = [
    r"d:\CoinCal_1\CoinCal\frontend\coincal_mobile\assets\translations\en.json",
    r"d:\CoinCal_1\CoinCal\frontend\coincal_mobile\assets\translations\ar.json"
]

for f_path in files:
    try:
        with open(f_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ {os.path.basename(f_path)} is VALID")
    except json.JSONDecodeError as e:
        print(f"❌ {os.path.basename(f_path)} is INVALID: {e}")
    except Exception as e:
        print(f"❌ {os.path.basename(f_path)} Error: {e}")
