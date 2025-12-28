### CookingLLM

import re
import json
import os
from typing import Dict, Any

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="GEMINI_API_KEY2")

REQUIRED_FIELDS = [
    "date",
    "user_goal",
    "daily_macros",
    "workout_split",
    "exercises",
    "time_required_minutes",
    "diet_rationale",
    "workout_rationale",
    "current_weight",
    "workout_intensity",
    "calories_burnt"
]



NUTRITION_DB = {
    "chicken breast": {"calories": 1.65, "protein": 0.31, "carbs": 0.0, "fats": 0.036},
    "rice": {"calories": 1.30, "protein": 0.025, "carbs": 0.28, "fats": 0.002},
    "tomato": {"calories": 0.18, "protein": 0.009, "carbs": 0.039, "fats": 0.002},
    "olive oil": {"calories": 8.8, "protein": 0.0, "carbs": 0.0, "fats": 1.0}
}


def validate_workout_output(data: Dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

def extract_number(text: str) -> float:
    match = re.search(r"[\d\.]+", text)
    if not match:
        raise ValueError(f"No numeric value found in: {text}")
    return float(match.group())

def normalize_inputs(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "date": raw["date"],
        "goal_text": raw["user_goal"],
        "nutritional_goal": raw.get("nutritional_goal", raw.get("user_goal")),
        "diet_rationale": raw["diet_rationale"],
        "workout_rationale": raw["workout_rationale"],
        "daily_macros": raw["daily_macros"],
        "current_weight_kg": float(raw["current_weight"]),
        "workout": {
            "split_text": raw["workout_split"],
            "intensity_text": raw["workout_intensity"],
            "duration_min": int(raw["time_required_minutes"]),
            "calories_burned": float(raw["calories_burnt"]),
            "exercises": raw["exercises"]
        }
    }

def build_semantic_prompt(normalized: Dict[str, Any]) -> str:
    return f"""
You are a STRICT classifier.

You MUST return ONLY valid JSON.
Do NOT add explanations.
Do NOT invent data.
Choose the closest option if unsure.

ALLOWED VALUES ONLY.

workout_focus:
  primary:
    - lower_body
    - upper_body
    - full_body
  modality:
    - strength
    - endurance
    - mixed

intensity_level:
- low
- moderate
- high

recovery_priority:
- low
- medium
- high

carb_requirement:
- low
- medium
- high

INPUT:
User goal: {normalized["goal_text"]}
Workout split: {normalized["workout"]["split_text"]}
Exercises: {json.dumps(normalized["workout"]["exercises"])}
Nutritional Goal: {normalized["nutritional_goal"]}
Workout rationale: {normalized["workout_rationale"]}
Workout intensity text: {normalized["workout"]["intensity_text"]}
Workout duration: {normalized["workout"]["duration_min"]} minutes
Calories burned estimate: {normalized["workout"]["calories_burned"]}
"""

# def call_semantic_llm(prompt: str) -> Dict[str, Any]:
#     model = genai.GenerativeModel("gemini-2.5-flash")

#     response = model.generate_content(
#         prompt,
#         generation_config={
#             "temperature": 0.0,
#             "top_p": 1.0,
#             "top_k": 1
#         }
#     )

#     raw_text = response.text.strip()

#     # ---------- CLEANING LAYER ----------
#     # Remove markdown fences if present
#     if raw_text.startswith("```"):
#         raw_text = raw_text.replace("```json", "")
#         raw_text = raw_text.replace("```", "")
#         raw_text = raw_text.strip()

#     # Remove leading "json" token if Gemini adds it
#     if raw_text.lower().startswith("json"):
#         raw_text = raw_text[4:].strip()

#     # Extract JSON object safely
#     start = raw_text.find("{")
#     end = raw_text.rfind("}") + 1

#     if start == -1 or end == -1:
#         raise RuntimeError(f"No JSON object found in Gemini output:\n{raw_text}")

#     json_text = raw_text[start:end]

#     try:
#         return json.loads(json_text)
#     except json.JSONDecodeError as e:
#         raise RuntimeError(
#             f"Failed to parse Gemini JSON.\n"
#             f"Raw response:\n{response.text}\n"
#             f"Extracted JSON:\n{json_text}"
#         ) from e
def call_semantic_llm(prompt: str, max_retries=3) -> Dict[str, Any]:
    model = genai.GenerativeModel("gemini-2.5-flash")

    for attempt in range(1, max_retries + 1):
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,
                "top_p": 1.0,
                "top_k": 1
            }
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1

        if start == -1 or end == -1:
            continue

        json_text = raw_text[start:end]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed after {max_retries} attempts.\n"
                    f"Last raw response:\n{response.text}"
                )


def decide_meal_structure(duration_min: int,
                          calories_burned: float,
                          recovery_priority: str):
    if duration_min >= 60 or calories_burned >= 500 or recovery_priority == "high":
        return ["breakfast", "post_workout", "lunch", "dinner"]
    return ["breakfast", "lunch", "dinner"]

def meal_fractions(meals):
    if "post_workout" in meals:
        return {
            "breakfast": 0.25,
            "post_workout": 0.30,
            "lunch": 0.25,
            "dinner": 0.20
        }
    return {
        "breakfast": 0.30,
        "lunch": 0.35,
        "dinner": 0.35
    }

def compute_meal_macros(daily_macros, fractions):
    meal_macros = {}
    for meal, frac in fractions.items():
        meal_macros[meal] = {
            "calories": daily_macros["calories"] * frac,
            "protein_g": daily_macros["protein_g"] * frac,
            "carbs_g": daily_macros["carbs_g"] * frac,
            "fats_g": daily_macros["fats_g"] * frac
        }
    return meal_macros

def build_pre_cooking_context(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    validate_workout_output(raw_output)
    normalized = normalize_inputs(raw_output)

    semantic_prompt = build_semantic_prompt(normalized)
    semantics = call_semantic_llm(semantic_prompt)

    meals = decide_meal_structure(
        normalized["workout"]["duration_min"],
        normalized["workout"]["calories_burned"],
        semantics["recovery_priority"]
    )

    fractions = meal_fractions(meals)
    meal_macros = compute_meal_macros(
        normalized["daily_macros"],
        fractions
    )

    return {
        "date": normalized["date"],
        "nutrition_goal": normalized["nutritional_goal"],
        "daily_macros": normalized["daily_macros"],
        "meal_macros": meal_macros,
        "meals": meals,
        "workout_semantics": semantics,
        "workout_context": normalized["workout"],
        "current_weight": normalized["current_weight_kg"],
        "diet_rationale": normalized["diet_rationale"]
    }

def build_recipe_prompt(
    meal_name: str,
    meal_macros: dict,
    food_context: dict,
    pre_context: dict
) -> str:

    return f"""
You are a cooking assistant.

STRICT RULES:
- Use ONLY the available ingredients.
- Do NOT exceed target calories by more than 10%.
- Prioritize hitting protein target.
- Return ONLY valid JSON.
- Do NOT add explanations.
- Do NOT provide the same meals everytime
- It is NOT necessary to use the same ingredients everytime, be creative

MEAL TYPE: {meal_name}

TARGET MACROS:
Calories: {meal_macros["calories"]:.0f}
Protein (g): {meal_macros["protein_g"]:.0f}
Carbs (g): {meal_macros["carbs_g"]:.0f}
Fats (g): {meal_macros["fats_g"]:.0f}

USER CONTEXT:
Diet type: {food_context["diet_type"]}
Cooking skill: {food_context["cooking_skill"]}
Allergies: {food_context["allergies"]}

AVAILABLE INGREDIENTS:
{food_context["available_ingredients"]}

WORKOUT CONTEXT:
Intensity: {pre_context["workout_semantics"]["intensity_level"]}
Carb requirement: {pre_context["workout_semantics"]["carb_requirement"]}

OUTPUT JSON SCHEMA:
{{
  "recipe_name": string,
  "ingredients": [
    {{ "item": string, "quantity_g": number }}
  ],
  "steps": [string]
}}
"""

def call_cooking_llm(prompt: str) -> dict:
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.6,  # allow creativity now
            "top_p": 0.9
        }
    )

    raw_text = response.text.strip()

    # --- CLEAN ---
    if raw_text.startswith("```"):
        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "").strip()

    if raw_text.lower().startswith("json"):
        raw_text = raw_text[4:].strip()

    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1

    if start == -1 or end == -1:
        raise RuntimeError(f"No JSON found:\n{raw_text}")

    return json.loads(raw_text[start:end])

# def compute_recipe_macros(recipe: dict):
#     total = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}

#     for ing in recipe["ingredients"]:
#         data = NUTRITION_DB[ing["item"]]
#         qty = ing["quantity_g"]

#         total["calories"] += data["calories"] * qty
#         total["protein"] += data["protein"] * qty
#         total["carbs"] += data["carbs"] * qty
#         total["fats"] += data["fats"] * qty

#     return total

def validate_recipe(actual, target, tolerance=0.10):
    return (
        abs(actual["calories"] - target["calories"]) / target["calories"] <= tolerance
        and actual["protein"] >= target["protein_g"] * 0.9
    )

import requests

def search_open_food_facts(food_name: str):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data.get("products"):
        raise ValueError(f"No Open Food Facts entry found for '{food_name}'")

    return data["products"][0]

def extract_macros_from_off(product: dict):
    nutriments = product.get("nutriments", {})

    def get_value(key):
        val = nutriments.get(key)
        return float(val) if val is not None else None

    macros = {
        "calories": get_value("energy-kcal_100g"),
        "protein": get_value("proteins_100g"),
        "carbs": get_value("carbohydrates_100g"),
        "fats": get_value("fat_100g")
    }

    # Ensure we have all required macros
    if any(v is None for v in macros.values()):
        raise ValueError(
            f"Incomplete nutrition data in Open Food Facts entry: {macros}"
        )

    return macros

import json
from pathlib import Path

NUTRITION_DB_PATH = Path("nutrition_db.json")

def load_nutrition_db():
    if NUTRITION_DB_PATH.exists():
        return json.loads(NUTRITION_DB_PATH.read_text())
    return {}

def save_nutrition_db(db):
    NUTRITION_DB_PATH.write_text(json.dumps(db, indent=2))

def get_food_macros(food_name: str):
    db = load_nutrition_db()

    key = food_name.lower().strip()

    if key in db:
        return db[key]["per_100g"]

    product = search_open_food_facts(food_name)
    macros = extract_macros_from_off(product)

    db[key] = {
        "source": "Open Food Facts",
        "product_name": product.get("product_name"),
        "per_100g": macros
    }

    save_nutrition_db(db)
    return macros


def compute_recipe_macros(recipe: dict):
    total = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}

    for ing in recipe["ingredients"]:
        food = ing["item"]
        grams = ing["quantity_g"]

        macros_100g = get_food_macros(food)

        total["calories"] += macros_100g["calories"] * grams / 100
        total["protein"] += macros_100g["protein"] * grams / 100
        total["carbs"] += macros_100g["carbs"] * grams / 100
        total["fats"] += macros_100g["fats"] * grams / 100

    return total

def sum_daily_macros(all_meals: dict):
    """
    Sums actual macros across all meals in a day.

    Parameters:
        all_meals (dict): final_output["meals"]

    Returns:
        dict: total daily macros
    """
    daily_total = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fats": 0.0
    }

    for meal_name, meal_data in all_meals.items():
        actual = meal_data.get("actual_macros")

        if not actual:
            continue  # safety

        daily_total["calories"] += actual["calories"]
        daily_total["protein"] += actual["protein"]
        daily_total["carbs"] += actual["carbs"]
        daily_total["fats"] += actual["fats"]

    return daily_total

def parse_ingredients2(response_text):
    import json, re
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output JSON error: {e}")

def generate_and_validate_meal(
    meal_name,
    meal_target,
    user_food_context,
    context,
    max_retries=3
):
    prompt = build_recipe_prompt(
            meal_name,
            meal_target,
            user_food_context,
            context
        )

    recipe = call_cooking_llm(prompt)
    actual_macros = compute_recipe_macros(recipe)

    return {
        "recipe": recipe,
        "target_macros": meal_target,
        "actual_macros": actual_macros,
        "status": "success",
        "attempts": 1
    }

def generate_meal_plan(
    workout_plan: Dict[str, Any],
    user_food_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 2 entry point.
    Takes:
      - Stage 1 workout plan JSON
      - User food context JSON
    Returns:
      - Full daily meal plan with macros
    """

    # Build context from Stage 1 output
    context = build_pre_cooking_context(workout_plan)

    all_meal_outputs = {}

    for meal_name in context["meals"]:
        meal_target = context["meal_macros"][meal_name]

        meal_result = generate_and_validate_meal(
            meal_name=meal_name,
            meal_target=meal_target,
            user_food_context=user_food_context,
            context=context
        )

        all_meal_outputs[meal_name] = meal_result

    final_output = {
        "date": context["date"],
        "nutrition_goal": context["nutrition_goal"],
        "meals": all_meal_outputs,
        "daily_actual_macros": sum_daily_macros(all_meal_outputs)
    }

    return final_output

# if __name__ == "__main__":
#     import json

#     import json

#     with open("output.json", "r", encoding="utf-8") as f:
#         workout_llm_output = json.load(f)

    
#     user_food_context = {
#         "available_ingredients": [
#             "chicken breast",
#             "white rice raw",
#             "tomato",
#             "olive oil",
#             "onion",
#             "pasta",
#             "cheese"
#         ],
#         "diet_type": "non_vegetarian",
#         "allergies": [],
#         "cooking_skill": "basic"
#     }

#     # ---------- PRE-COOKING CONTEXT ----------
#     context = build_pre_cooking_context(workout_llm_output)

#     print("\n=== PRE-COOKING CONTEXT ===")
#     print(json.dumps(context, indent=2))

#     # ---------- GENERATE ALL MEALS ----------
#     all_meal_outputs = {}

#     for meal_name in context["meals"]:
#         meal_target = context["meal_macros"][meal_name]

#         print(f"\n--- Generating {meal_name.upper()} ---")

#         meal_result = generate_and_validate_meal(
#             meal_name,
#             meal_target,
#             user_food_context,
#             context
#         )

#         all_meal_outputs[meal_name] = meal_result

#         print(json.dumps(meal_result, indent=2))

#     # ---------- FINAL STRUCTURED OUTPUT ----------
#     final_output = {
#         "date": context["date"],
#         "nutrition_goal": context["nutrition_goal"],
#         "meals": all_meal_outputs
#     }

#     print("\n=== FINAL MEAL PLAN WITH MACROS ===")
#     print(json.dumps(final_output, indent=2))

#     daily_actual_macros = sum_daily_macros(final_output["meals"])

#     print("\n=== DAILY TOTAL MACROS ===")
#     print(json.dumps(daily_actual_macros, indent=2))
