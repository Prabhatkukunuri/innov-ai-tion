import os
import json
import re
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


# =========================
# INGREDIENT DETECTION
# =========================
def detect_ingredients_from_image(image: Image.Image) -> list[str]:
    """
    Uses Gemini Vision to detect raw ingredients from an image.
    Returns list of normalized ingredient names.
    """

    prompt = """
    Identify all RAW food ingredients visible in this image.
    Ignore cooked dishes, utensils, and packaging.
    Return ONLY a JSON array of ingredient names.
    """

    response = model.generate_content([prompt, image])
    raw_text = response.text.strip()

    cleaned = re.sub(r"```json|```", "", raw_text).strip()
    ingredients = json.loads(cleaned)

    return [normalize_name(i) for i in ingredients]


# =========================
# NUTRITION CALCULATION
# =========================
def load_nutrition_db(path="nutrition_db2.json"):
    with open(path, "r") as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def calculate_nutrition(food_consumed: dict) -> dict:
    """
    food_consumed:
    {
        "chicken_breast": 200,
        "rice_raw": 150
    }
    """

    nutrition_db = load_nutrition_db()

    total = {
        "calories": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbs": 0.0
    }

    breakdown = {}

    for item, grams in food_consumed.items():
        if item not in nutrition_db:
            raise ValueError(f"No nutrition data for {item}")

        data = nutrition_db[item]

        breakdown[item] = {
            "calories": grams * data["calories_per_gram"],
            "protein": grams * data["protein_g_per_gram"],
            "fat": grams * data["fat_g_per_gram"],
            "carbs": grams * data["carbs_g_per_gram"]
        }

        for k in total:
            total[k] += breakdown[item][k]

    return {
        "total": total,
        "breakdown": breakdown
    }
