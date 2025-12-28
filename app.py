from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import json

from workout_llm import generate_workout_plan
from cooking_LLM import generate_meal_plan
from tracking_llm import (
    generate_workout_adjustments,
    create_database,
    store_workout_plan
)
from calorie import detect_ingredients_from_image



# Initialize DB once
create_database()

app = Flask(__name__)
CORS(app)


# =========================
# STAGE 1: WORKOUT PLAN
# =========================
@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_input = payload.get("user_input")
    workout_adjustments = payload.get("workout_adjustments")

    if not user_input and not workout_adjustments:
        return jsonify({"error": "user_input or workout_adjustments required"}), 400

    try:
        plan = generate_workout_plan(
            user_input=user_input,
            workout_adjustments=workout_adjustments
        )

        # ✅ Store AFTER generation
        store_workout_plan(plan)

        return jsonify(plan), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# =========================
# STAGE 2: MEAL PLAN
# =========================
@app.route("/generate-meals", methods=["POST"])
def generate_meals():
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    workout_plan = payload.get("workout_plan")
    user_food_context = payload.get("user_food_context")

    if not workout_plan or not user_food_context:
        return jsonify({"error": "workout_plan and user_food_context required"}), 400

    try:
        meal_plan = generate_meal_plan(
            workout_plan=workout_plan,
            user_food_context=user_food_context
        )
        return jsonify(meal_plan), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detect-ingredients", methods=["POST"])
def detect_ingredients():
    if "image" not in request.files:
        return jsonify({"error": "image file required"}), 400

    try:
        image_file = request.files["image"]
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")

        ingredients = detect_ingredients_from_image(image)

        return jsonify({
            "status": "awaiting_weights",
            "ingredients": ingredients
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# STAGE 3: ADJUSTMENTS
# =========================
@app.route("/generate-adjustments", methods=["POST"])
def generate_adjustments():
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    food_consumed = payload.get("food_consumed")
    workout_feedback = payload.get("workout_feedback")

    if not food_consumed or not workout_feedback:
        return jsonify({
            "error": "food_consumed and workout_feedback required"
        }), 400

    try:
        workout_adjustments = generate_workout_adjustments(
            food_consumed=food_consumed,
            workout_feedback=workout_feedback
        )

        return jsonify(workout_adjustments), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
