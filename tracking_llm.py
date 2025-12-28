import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai


# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY3")
if api_key is None:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=api_key)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Load image
image = Image.open("FoodItem.png").convert("RGB")

# Prompt
prompt = """
Identify all RAW food ingredients visible in this image.
Ignore cooked dishes, utensils, and packaging.
Return ONLY a JSON array of ingredient names.
"""

# Generate response
# response = model.generate_content([prompt, image])

# print(response.text)
def get_weights(ingredients):
    weights = {}
    for item in ingredients:
        w = float(input(f"Enter weight (grams) for {item}: "))
        weights[item] = w
    return weights

def parse_ingredients(response_text):
    import json, re
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output JSON error: {e}")

import json

def load_nutrition_db(path="nutrition_db2.json"):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        print("Nutrition DB loaded successfully")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Nutrition DB JSON error: {e}")

def normalize_name(name):
    return name.lower().replace(" ", "_")

def calculate_nutrition(ingredients, weights, nutrition_db):
    total = {
        "calories": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbs": 0.0
    }

    breakdown = {}

    for item in ingredients:
        if item not in nutrition_db:
            raise ValueError(f"No nutrition data for {item}")

        w = weights[item]
        data = nutrition_db[item]

        calories = w * data["calories_per_gram"]
        protein = w * data["protein_g_per_gram"]
        fat = w * data["fat_g_per_gram"]
        carbs = w * data["carbs_g_per_gram"]

        breakdown[item] = {
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        }

        total["calories"] += calories
        total["protein"] += protein
        total["fat"] += fat
        total["carbs"] += carbs

    return total, breakdown

nutrition_db = load_nutrition_db()

gemini_output_text = """[
  "raw_chicken",
  "rice_raw",
  "onion",
  "tomato",
  "potato",
  "carrot",
  "banana",
  "apple",
  "egg_whole",
  "oil_generic",
  "milk_full_fat",
  "bread_white"
]
"""

ingredients = parse_ingredients(gemini_output_text)
ingredients = [normalize_name(i) for i in ingredients]


nutrition_db = load_nutrition_db()

# weights = get_weights(ingredients)

# total, breakdown = calculate_nutrition(
#     ingredients,
#     weights,
#     nutrition_db
# )


# print("\nNutrition Breakdown (per ingredient):")
# for item, data in breakdown.items():
#     print(
#         f"{item}: "
#         f"{data['calories']:.2f} kcal | "
#         f"Protein {data['protein']:.2f} g | "
#         f"Fat {data['fat']:.2f} g | "
#         f"Carbs {data['carbs']:.2f} g"
#     )

# print("\nTOTALS:")
# print(f"Calories: {total['calories']:.2f} kcal")
# print(f"Protein:  {total['protein']:.2f} g")
# print(f"Fat:      {total['fat']:.2f} g")
# print(f"Carbs:    {total['carbs']:.2f} g")

import sqlite3

def create_database(db_name="fitness.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE,
        user_goal TEXT,
        calories REAL,
        protein_g REAL,
        carbs_g REAL,
        fats_g REAL,
        workout_split TEXT,
        time_required_minutes INTEGER,
        diet_rationale TEXT,
        workout_rationale TEXT,
        current_weight REAL,
        workout_intensity TEXT,
        calories_to_burn REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        daily_plan_id INTEGER,
        name TEXT NOT NULL,
        exercise_type TEXT NOT NULL,   -- 'strength' or 'cardio'

        -- strength fields
        sets INTEGER,
        reps TEXT,

        -- cardio fields
        distance_km REAL,
        time_minutes TEXT,

        FOREIGN KEY (daily_plan_id)
            REFERENCES daily_plans(id)
            ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# create_database()

def insert_daily_plan(plan, db_name="fitness.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
        INSERT INTO daily_plans (
            date, user_goal, calories, protein_g, carbs_g, fats_g,
            workout_split, time_required_minutes,
            diet_rationale, workout_rationale,
            current_weight, workout_intensity, calories_to_burn
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan["date"],
            plan["user_goal"],
            plan["daily_macros"]["calories"],
            plan["daily_macros"]["protein_g"],
            plan["daily_macros"]["carbs_g"],
            plan["daily_macros"]["fats_g"],
            plan["workout_split"],
            plan["time_required_minutes"],
            plan["diet_rationale"],
            plan["workout_rationale"],
            plan["Current_weight"],
            plan["Workout_Intensity"],
            plan["calories_burnt"]
        ))

        daily_plan_id = cursor.lastrowid

        for ex in plan["exercises"]:

            # STRENGTH
            if "sets" in ex and "reps" in ex:
                cursor.execute("""
                INSERT INTO exercises (
                    daily_plan_id, name, exercise_type, sets, reps
                ) VALUES (?, ?, 'strength', ?, ?)
                """, (
                    daily_plan_id,
                    ex["name"],
                    ex["sets"],
                    ex["reps"]
                ))

            # CARDIO
            elif "distance_km" in ex:
                cursor.execute("""
                INSERT INTO exercises (
                    daily_plan_id, name, exercise_type, distance_km, time_minutes
                ) VALUES (?, ?, 'cardio', ?, ?)
                """, (
                    daily_plan_id,
                    ex["name"],
                    ex["distance_km"],
                    ex.get("duration_mins")
                ))

        conn.commit()

    except sqlite3.IntegrityError:
        print(f"⚠️ Workout already exists for date {plan['date']}")

    finally:
        conn.close()

from datetime import date

# today_str = date.today().strftime("%d/%m/%y")
# print(today_str)

# with open("output.json", "r", encoding="utf-8") as f:
#     workout_llm_output = json.load(f)
    
# plan_output = workout_llm_output

FORMAT_NORMALIZATION_SYSTEM_PROMPT = """
You are a Data Normalization Agent.

Your task:
- Convert the provided workout & diet object into a STRICTLY NORMALIZED plan_output JSON.

STRICT RULES:
- Output MUST be valid JSON only.
- Do NOT add explanations, comments, or extra fields.
- Do NOT invent new values.
- Do NOT change numeric values.
- Do NOT infer missing data.
- If information exists in multiple places, choose the MOST DIRECT equivalent.
- Flatten complex nested structures into the required schema.
- Cardio exercises MUST use:
  { "name", "distance_km", "duration_mins" }
- Strength exercises MUST use:
  { "name", "sets", "reps" }
- workout_split MUST be a STRING, not an object.

REQUIRED OUTPUT FORMAT:
{
  "date": string,
  "user_goal": "fat_loss" | "muscle_gain",
  "daily_macros": {
    "calories": number,
    "protein_g": number,
    "carbs_g": number,
    "fats_g": number
  },
  "workout_split": string,
  "exercises": array,
  "time_required_minutes": number,
  "diet_rationale": string,
  "workout_rationale": string,
  "Current_weight": number,
  "Workout_Intensity": string,
  "calories_burnt": number
}
"""

import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

# Configure Gemini (OLD SDK)
genai.configure(api_key=api_key)

MODEL_NAME = "gemma-3-27b-it"
model = genai.GenerativeModel(model_name=MODEL_NAME)

def extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from model output.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    return json.loads(match.group())

def normalize_plan_with_llm(raw_plan: dict) -> dict:
    prompt = f"""
{FORMAT_NORMALIZATION_SYSTEM_PROMPT}

IMPORTANT:
- Output ONLY a JSON object.
- Do not include explanations or markdown.

INPUT DATA:
{json.dumps(raw_plan)}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.0
        }
    )

    return extract_json(response.text)

# normalized_plan = normalize_plan_with_llm(plan_output)

# normalized_plan

# Directly insert into DB
# insert_daily_plan(normalized_plan)

# insert_daily_plan(normalized_plan)

import sqlite3
from datetime import datetime

# def print_todays_plan(db_name="fitness.db"):
#     today = datetime.now().strftime("%d/%m/%y")

#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()

#     # Fetch daily plan
#     cursor.execute("""
#         SELECT id, date, user_goal, calories, protein_g, carbs_g, fats_g,
#                workout_split, time_required_minutes,
#                diet_rationale, workout_rationale,
#                current_weight, workout_intensity, calories_to_burn
#         FROM daily_plans
#         WHERE date = ?
#     """, (today,))

#     plan = cursor.fetchone()

#     if not plan:
#         print(f"❌ No workout plan found for {today}")
#         conn.close()
#         return

#     daily_plan_id = plan[0]

#     # Fetch exercises (NEW SCHEMA)
#     cursor.execute("""
#         SELECT
#             name,
#             exercise_type,
#             sets,
#             reps,
#             distance_km,
#             time_minutes
#         FROM exercises
#         WHERE daily_plan_id = ?
#     """, (daily_plan_id,))

#     exercises = cursor.fetchall()
#     conn.close()

#     # Pretty print
#     print("\n" + "=" * 50)
#     print(f"📅 Date: {plan[1]}")
#     print(f"🎯 Goal: {plan[2]}")

#     print("\n🍽️ Daily Macros:")
#     print(f"   Calories: {plan[3]} kcal")
#     print(f"   Protein: {plan[4]} g")
#     print(f"   Carbs:   {plan[5]} g")
#     print(f"   Fats:    {plan[6]} g")

#     print("\n🏋️ Workout:")
#     print(f"   Split: {plan[7]}")
#     print(f"   Time Required: {plan[8]} minutes")
#     print(f"   Intensity: {plan[12]}")
#     print(f"   Calories to Burn: {plan[13]} kcal")

#     print("\n📋 Exercises:")
#     for i, ex in enumerate(exercises, start=1):
#         name, ex_type, sets, reps, dist, time = ex

#         if ex_type == "strength":
#             print(f"   {i}. {name} — {sets} sets × {reps} reps")

#         elif ex_type == "cardio":
#             line = f"   {i}. {name} — {dist} km"
#             if time:
#                 line += f" in {time} min"
#             print(line)

#     print("\n🧠 Rationale:")
#     print(f"   Diet: {plan[9]}")
#     print(f"   Workout: {plan[10]}")

#     print("\n⚖️ Current Weight:")
#     print(f"   {plan[11]} kg")

#     print("=" * 50 + "\n")

# print_todays_plan()

import sqlite3
from datetime import datetime

def fetch_targets_for_today(db_name="fitness.db"):
    today = datetime.now().strftime("%d/%m/%y")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            calories,
            protein_g,
            carbs_g,
            fats_g,
            calories_to_burn,
            time_required_minutes,
            workout_intensity
        FROM daily_plans
        WHERE date = ?
    """, (today,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "required_macros": {
            "calories": row[0],
            "protein": row[1],
            "carbs": row[2],
            "fat": row[3]
        },
        "workout": {
            "calories_burnt": row[4],
            "time_required_minutes": row[5],
            "intensity": row[6]
        }
    }

def calculate_daily_deficits(required, consumed):
    """
    required -> from DB
    consumed -> your `total` dict from nutrition calculation
    """

    calorie_deficit = (
        required["required_macros"]["calories"]
        - consumed["calories"]
        + required["workout"]["calories_burnt"]
    )

    macro_deficits = {
        "protein": required["required_macros"]["protein"] - consumed["protein"],
        "carbs":   required["required_macros"]["carbs"]   - consumed["carbs"],
        "fat":     required["required_macros"]["fat"]     - consumed["fat"]
    }

    return {
        "calorie_deficit": calorie_deficit,
        "macro_deficits": macro_deficits,
        "workout": required["workout"]
    }

# targets = fetch_targets_for_today()

# if not targets:
#     print("❌ No plan found for today")
# else:
#     deficits = calculate_daily_deficits(targets, total)

    # print("\n🔥 DAILY ENERGY BALANCE")
    # print(f"Calorie Deficit: {deficits['calorie_deficit']:.2f} kcal")

    # print("\n🧬 MACRO DEFICITS")
    # print(f"Protein: {deficits['macro_deficits']['protein']:.2f} g")
    # print(f"Carbs:   {deficits['macro_deficits']['carbs']:.2f} g")
    # print(f"Fat:     {deficits['macro_deficits']['fat']:.2f} g")

    # print("\n🏋️ WORKOUT CONTEXT")
    # print(f"Calories Burnt: {deficits['workout']['calories_burnt']} kcal")
    # print(f"Time Required: {deficits['workout']['time_required_minutes']} min")
    # print(f"Intensity: {deficits['workout']['intensity']}")

import sqlite3
from datetime import datetime

def fetch_workout_for_today(db_name="fitness.db"):
    today = datetime.now().strftime("%d/%m/%y")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch today's plan
    cursor.execute("""
        SELECT id, time_required_minutes, workout_intensity, calories_to_burn
        FROM daily_plans
        WHERE date = ?
    """, (today,))

    plan = cursor.fetchone()
    if not plan:
        conn.close()
        return None

    daily_plan_id, planned_time, intensity, calories_burnt = plan

    # Fetch exercises (NEW SCHEMA)
    cursor.execute("""
        SELECT
            name,
            exercise_type,
            sets,
            reps,
            distance_km,
            time_minutes
        FROM exercises
        WHERE daily_plan_id = ?
    """, (daily_plan_id,))

    rows = cursor.fetchall()
    conn.close()

    exercises = []

    for row in rows:
        name, ex_type, sets, reps, dist, time = row

        if ex_type == "strength":
            exercises.append({
                "name": name,
                "exercise_type": "strength",
                "sets": sets,
                "reps": reps
            })

        elif ex_type == "cardio":
            exercises.append({
                "name": name,
                "exercise_type": "cardio",
                "distance_km": dist,
                "time_minutes": time
            })

    return {
        "planned_time": planned_time,
        "planned_intensity": intensity,
        "calories_burnt": calories_burnt,
        "exercises": exercises
    }

def parse_reps(reps_str):
    if "-" in reps_str:
        low, high = reps_str.split("-")
        return int((int(low) + int(high)) / 2)  # average
    return int(reps_str)

def calculate_planned_reps(exercises):
    total = 0

    for ex in exercises:
        # Only strength exercises have reps
        if ex.get("exercise_type") == "strength":
            reps_per_set = parse_reps(ex["reps"])
            total += ex["sets"] * reps_per_set

    return total

# def get_user_workout_input_per_exercise(exercises, planned_time):
#     if not exercises:
#         raise ValueError("❌ No exercises found for today")

#     # print("\n--- WORKOUT FEEDBACK (PER EXERCISE) ---")

#     total_planned_reps = 0
#     total_completed_reps = 0
#     cardio_data = []

#     for idx, ex in enumerate(exercises, start=1):
#         print(f"\nExercise {idx}: {ex['name']}")

#         # --------------------
#         # STRENGTH
#         # --------------------
#         if ex["exercise_type"] == "strength":
#             reps_per_set = parse_reps(ex["reps"])
#             planned_reps = ex["sets"] * reps_per_set
#             total_planned_reps += planned_reps

#             print(f"Planned: {ex['sets']} × {ex['reps']} → {planned_reps} reps")

#             completed = int(
#                 input(f"How many reps did you complete for {ex['name']}? ")
#             )

#             completed = max(0, completed)
#             total_completed_reps += completed

#         # --------------------
#         # CARDIO
#         # --------------------
#         elif ex["exercise_type"] == "cardio":
#             planned_distance = ex["distance_km"]

#             print(f"Planned distance: {planned_distance} km")

#             if ex.get("time_minutes"):
#                 print(f"Planned time: {ex['time_minutes']} minutes")

#             completed_distance = float(
#                 input(f"How many km did you complete for {ex['name']}? ")
#             )
#             completed_time = float(
#                 input(f"How many minutes did you take for {ex['name']}? ")
#             )

#             cardio_data.append({
#                 "planned_distance": planned_distance,
#                 "completed_distance": completed_distance,
#                 "completed_time": completed_time
#             })

#     # print(f"\nPlanned total workout time: {planned_time} minutes")
#     # actual_time = float(input("Total workout time taken (minutes): "))

#     return {
#         "strength": {
#             "planned_reps": total_planned_reps,
#             "completed_reps": total_completed_reps
#         },
#         "cardio": cardio_data,
#         "actual_time": actual_time
#     }

def calculate_cardio_completion(cardio_data):
    if not cardio_data:
        return 1.0  # no cardio → neutral

    ratios = []
    for c in cardio_data:
        distance_ratio = c["completed_distance"] / c["planned_distance"]
        ratios.append(min(distance_ratio, 1.2))  # small overachievement allowed

    return sum(ratios) / len(ratios)

def calculate_workout_effort_with_cardio(
    strength_planned_reps,
    strength_completed_reps,
    planned_time,
    actual_time,
    cardio_data
):
    # Strength completion
    if strength_planned_reps > 0:
        strength_completion = min(
            strength_completed_reps / strength_planned_reps, 1.0
        )
    else:
        strength_completion = 1.0

    # Cardio completion
    cardio_completion = calculate_cardio_completion(cardio_data)

    # Combine (simple average for now)
    completion_ratio = (strength_completion + cardio_completion) / 2

    # Time-based intensity
    time_ratio = planned_time / actual_time
    intensity_multiplier = max(0, time_ratio)

    effort_score = completion_ratio * intensity_multiplier

    return {
        "strength_completion_pct": round(strength_completion * 100, 2),
        "cardio_completion_pct": round(cardio_completion * 100, 2),
        "intensity_multiplier": round(intensity_multiplier, 2),
        "effort_score": round(effort_score, 3)
    }

workout = fetch_workout_for_today()

if not workout:
    print("❌ No workout found for today")


# print("\n📋 TODAY'S WORKOUT")
# print(f"Planned Time: {workout['planned_time']} min")
# print(f"Planned Intensity: {workout['planned_intensity']}")
# print(f"Calories to Burn: {workout['calories_burnt']} kcal")

# print("\nExercises:")
# for ex in workout["exercises"]:
#     if "sets" in ex:
#         print(f" - {ex['name']}: {ex['sets']} × {ex['reps']}")
#     elif "distance_km" in ex:
#         print(f" - {ex['name']}: {ex['distance_km']} km (time {ex.get('duration_mins', 'N/A')})")


planned_reps = calculate_planned_reps(workout["exercises"])

# user_input = get_user_workout_input_per_exercise(
#     workout["exercises"],
#     workout["planned_time"]
# )

# effort = calculate_workout_effort_with_cardio(
#     strength_planned_reps=user_input["strength"]["planned_reps"],
#     strength_completed_reps=user_input["strength"]["completed_reps"],
#     planned_time=workout["planned_time"],
#     actual_time=user_input["actual_time"],
#     cardio_data=user_input["cardio"]
# )

# print("\n📊 WORKOUT SUMMARY")
# print(f"Strength Completion: {effort['strength_completion_pct']} %")
# print(f"Cardio Completion: {effort['cardio_completion_pct']} %")
# print(f"Intensity Multiplier: {effort['intensity_multiplier']}")
# print(f"Effort Score: {effort['effort_score']}")

# if effort["effort_score"] >= 1.0:
#     print("✅ Workout met or exceeded expectations")
# else:
#     print("⚠️ Workout under-completed")

def evaluate_daily_thresholds(
    user_goal,
    calorie_deficit,
    macro_deficits,
    strength_completion_pct,
    cardio_completion_pct,
    intensity_multiplier,
    effort_score
):
    results = {
        "goal": user_goal,
        "status": "on_track",
        "flags": [],              # things that need attention
        "positives": [],          # things that went well
        "metrics": {}
    }

    # =======================
    # FAT LOSS
    # =======================
    if user_goal == "fat_loss":

        # ---- Calorie deficit ----
        if calorie_deficit <= 200:
            results["flags"].append("calorie_deficit_too_low")
        elif calorie_deficit >= 700:
            results["flags"].append("calorie_deficit_too_high")
        else:
            results["positives"].append("calorie_deficit_in_optimal_range")

        # ---- Protein ----
        if macro_deficits["protein"] < 0:
            results["flags"].append("protein_intake_insufficient")
        else:
            results["positives"].append("protein_intake_adequate")

        # ---- Strength ----
        if strength_completion_pct < 75:
            results["flags"].append("low_strength_completion")
        else:
            results["positives"].append("strength_training_completed_well")

        # ---- Cardio ----
        if cardio_completion_pct < 70:
            results["flags"].append("low_cardio_completion")
        else:
            results["positives"].append("cardio_target_met")

        # ---- Effort ----
        if effort_score < 0.80:
            results["flags"].append("low_overall_effort")
        else:
            results["positives"].append("good_overall_effort")

        # ---- Intensity ----
        if intensity_multiplier < 0.7:
            results["flags"].append("training_intensity_low")
        else:
            results["positives"].append("training_intensity_adequate")

    # =======================
    # MUSCLE GAIN
    # =======================
    elif user_goal == "muscle_gain":

        # ---- Calories ----
        if calorie_deficit > 0:
            results["flags"].append("calorie_deficit_present")
        else:
            results["positives"].append("calorie_intake_supports_growth")

        # ---- Protein ----
        if macro_deficits["protein"] < 10:
            results["flags"].append("insufficient_protein_for_growth")
        else:
            results["positives"].append("protein_target_exceeded")
         # ---- Cardio ----
        if cardio_completion_pct < 70:
            results["flags"].append("low_cardio_completion")
        else:
            results["positives"].append("cardio_target_met")

        # ---- Strength ----
        if strength_completion_pct < 85:
            results["flags"].append("low_strength_completion")
        else:
            results["positives"].append("strength_training_executed_well")

        # ---- Effort ----
        if effort_score < 0.8:
            results["flags"].append("low_training_effort")
        else:
            results["positives"].append("high_training_effort")

        # ---- Intensity ----
        if intensity_multiplier < 1.0:
            results["flags"].append("training_intensity_below_target")
        elif intensity_multiplier > 1.5:
            results["positives"].append("training_intensity_is_too_easy")
        else:
            results["positives"].append("training_intensity_on_point")

    # =======================
    # FINAL STATUS
    # =======================
    if results["flags"]:
        results["status"] = "needs_adjustment"

    # =======================
    # METRICS SNAPSHOT
    # =======================
    results["metrics"] = {
        "calorie_deficit": calorie_deficit,
        "protein_deficit": macro_deficits["protein"],
        "strength_completion_pct": strength_completion_pct,
        "cardio_completion_pct": cardio_completion_pct,
        "intensity_multiplier": intensity_multiplier,
        "effort_score": effort_score
    }

    return results

import sqlite3
from datetime import datetime

def fetch_user_goal_for_today(db_name="fitness.db"):
    today = datetime.now().strftime("%d/%m/%y")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_goal
        FROM daily_plans
        WHERE date = ?
    """, (today,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return row[0]   # 'fat_loss' or 'muscle_gain'

# Fetch goal from DB
user_goal = fetch_user_goal_for_today()

# if not user_goal:
#     print("❌ Could not fetch user goal for today")
# else:
#     threshold_result = evaluate_daily_thresholds(
#         user_goal=user_goal,
#         calorie_deficit=deficits["calorie_deficit"],
#         macro_deficits=deficits["macro_deficits"],
#         strength_completion_pct=effort["strength_completion_pct"],
#         cardio_completion_pct=effort["cardio_completion_pct"],
#         intensity_multiplier=effort["intensity_multiplier"],
#         effort_score=effort["effort_score"]
#     )

    # print("\n🎯 THRESHOLD EVALUATION")
    # print("Goal:", threshold_result["goal"])
    # print("Status:", threshold_result["status"])
    # print("Flags:", threshold_result["flags"])
    # print("Positives:", threshold_result["positives"])
    # print("Metrics ",threshold_result["metrics"])
    
# tracker_decision_output = {
#     "goal": threshold_result["goal"],
#     "status": threshold_result["status"],
#     "Negatives": threshold_result["flags"],
#     "Positives": threshold_result["positives"],
#     "Metrics" : threshold_result["metrics"],
#     "Intensity": workout["planned_intensity"]
# }

import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a fast, reliable model
tracker_model = genai.GenerativeModel("gemma-3-27b-it")

WORKOUT_ADJUSTMENT_SYSTEM_PROMPT = """
You are a Workout Adjustment & Summary Agent in a fitness optimization system.

Your role:
- Convert tracker evaluation results into a comprehensive, structured adjustment report.
- Clearly explain what went well, what needs adjustment, and why.
- Translate high-level tracker flags into concrete, bounded workout-level guidance.
- Keep the user's goal in mind when creating the report

STRICT RULES:
- You may ONLY base your output on the input data provided (negatives, positives, metrics, intensity, goal).
- You may NOT invent new goals, timelines, constraints, or numeric targets.
- You may NOT override tracker decisions or reinterpret thresholds.
- You may NOT generate a full workout plan.
- You may NOT introduce new exercises.


YOU SHOULD:
- Explicitly separate:
  - confirmed strengths (what worked well)
  - required adjustments (what must change)
  - protected elements (what should be maintained)
- Break adjustments into:
  - intensity guidance
  - volume guidance
  - cardio vs strength emphasis
  - recovery considerations
- Explain adjustments causally (i.e., link each adjustment to a specific tracker flag or metric).
- Be precise, non-judgmental, and coach-like.
- Make a field called 'report_id' for unique identification

OUTPUT REQUIREMENTS:
- Output MUST be valid JSON only.
- No markdown, no prose outside JSON.
- The output must be directly consumable by a downstream Workout Planning Agent.

You are NOT a planner.
You are a structured interpreter and adjustment summarizer.
"""


def run_workout_adjustment_llm(tracker_decision_json):
    """
    Converts tracker decisions into workout modification instructions.
    Returns a dict (parsed JSON).
    """

    user_message = json.dumps(tracker_decision_json, indent=2)

    response = tracker_model.generate_content(
        [
            WORKOUT_ADJUSTMENT_SYSTEM_PROMPT,
            user_message
        ]
    )

    raw_text = response.text.strip()

    # Clean any accidental markdown
    cleaned = re.sub(r"```json|```", "", raw_text).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Workout Adjustment LLM output is not valid JSON: {e}")

# workout_adjustments = run_workout_adjustment_llm(tracker_decision_output)
def store_workout_plan(raw_plan: dict) -> dict:
    """
    Normalizes and stores workout plan from Stage 1.
    Returns normalized plan.
    """
    normalized = normalize_plan_with_llm(raw_plan)
    insert_daily_plan(normalized)
    return normalized

# print(json.dumps(workout_adjustments, indent=2))
def generate_workout_adjustments(
    *,
    date_str: str,
    food_consumed: dict,
    workout_feedback: dict,
    db_name="fitness.db"
) -> dict:
    """
    Stage 3 API-safe entry point.
    - Reads today's workout from DB
    - Computes deficits & effort
    - Updates DB if needed
    - Returns workout_adjustments JSON
    """

    # -----------------------------
    # 1️⃣ Fetch plan from DB
    # -----------------------------
    workout = fetch_workout_for_today(db_name)
    if not workout:
        raise ValueError("No workout found for today")

    targets = fetch_targets_for_today(db_name)
    if not targets:
        raise ValueError("No targets found for today")

    user_goal = fetch_user_goal_for_today(db_name)
    if not user_goal:
        raise ValueError("Could not fetch user goal")

    # -----------------------------
    # 2️⃣ Nutrition calculation
    # -----------------------------
    total_nutrition, _ = calculate_nutrition(
        ingredients=list(food_consumed.keys()), 
        # here note that you need to check the top
        weights=food_consumed,
        nutrition_db=load_nutrition_db()
    )

    deficits = calculate_daily_deficits(
        required=targets,
        consumed=total_nutrition
    )

    # -----------------------------
    # 3️⃣ Workout effort
    # -----------------------------
    effort = calculate_workout_effort_with_cardio(
        strength_planned_reps=workout_feedback["planned_reps"],
        strength_completed_reps=workout_feedback["completed_reps"],
        planned_time=workout["planned_time"],
        actual_time=workout_feedback["actual_time"],
        cardio_data=workout_feedback.get("cardio", [])
    )

    # -----------------------------
    # 4️⃣ Threshold evaluation
    # -----------------------------
    threshold_result = evaluate_daily_thresholds(
        user_goal=user_goal,
        calorie_deficit=deficits["calorie_deficit"],
        macro_deficits=deficits["macro_deficits"],
        strength_completion_pct=effort["strength_completion_pct"],
        cardio_completion_pct=effort["cardio_completion_pct"],
        intensity_multiplier=effort["intensity_multiplier"],
        effort_score=effort["effort_score"]
    )

    tracker_decision_output = {
        "goal": threshold_result["goal"],
        "status": threshold_result["status"],
        "Negatives": threshold_result["flags"],
        "Positives": threshold_result["positives"],
        "Metrics": threshold_result["metrics"],
        "Intensity": workout["planned_intensity"]
    }

    # -----------------------------
    # 5️⃣ LLM adjustment generation
    # -----------------------------
    workout_adjustments = run_workout_adjustment_llm(
        tracker_decision_output
    )

    # -----------------------------
    # 6️⃣ (OPTIONAL) Persist adjustments
    # -----------------------------
    # save_adjustments_to_db(workout_adjustments)

    return workout_adjustments
