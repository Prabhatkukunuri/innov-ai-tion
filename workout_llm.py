import os
import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, Optional, List, Any
from tavily import TavilyClient
import google.generativeai as genai


# ============================================================================
# CONFIGURATION
# ============================================================================
class Config:
    """Configuration constants"""
    TAVILY_API_KEY = "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"
    GEMINI_API_KEY = "AIzaSyBzCn9rgf6Ieo_YXBeMcFWqZPKD8BaIYm4"
    MODEL_NAME = "gemini-2.5-flash"
    DEFAULT_DB_NAME = "fitness.db"
    WORKOUT_DURATION_MINUTES = 60
    MAX_RETRIES = 2

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

# Initialize Tavily
tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)


def detect_input_type(user_input: Dict) -> str:
    """
    Detect whether input is a new user registration or adjustment report.

    Args:
        user_input: User input dictionary

    Returns:
        'new_user' or 'adjustment_report'
    """
    # Check for minimal new user fields
    has_minimal_fields = all(k in user_input for k in ['weight', 'experience', 'goal'])

    # Check for adjustment report structure
    has_report_structure = 'report_id' in user_input or 'metrics_reference' in user_input

    if has_report_structure:
        return 'adjustment_report'
    elif has_minimal_fields:
        return 'new_user'
    else:
        # Default to new_user if unclear
        return 'new_user'


def normalize_input_to_report(user_input: Dict) -> Dict:
    """
    Normalize any input format into a standard adjustment report format.

    Args:
        user_input: Raw user input (either new user or adjustment report)

    Returns:
        Normalized adjustment report dictionary
    """
    input_type = detect_input_type(user_input)

    if input_type == 'adjustment_report':
        # Already in correct format, return as-is
        print("  ✓ Detected: Existing user with adjustment report")
        return user_input

    # New user - create conservative first-time workout report
    print("  ✓ Detected: New user registration")
    print(f"  📋 Weight: {user_input.get('weight', 'not provided')} kg")
    print(f"  📋 Experience: {user_input.get('experience', 'not provided')}")
    print(f"  📋 Goal: {user_input.get('goal', 'not provided')}")

    # Extract basic info
    weight = user_input.get('weight', 70.0)
    experience = user_input.get('experience', 'beginner').lower()
    goal = user_input.get('goal', 'maintenance').lower()

    # Map experience to intensity and volume guidance
    experience_mapping = {
        'beginner': {
            'intensity': 'low',
            'volume': 'Start with minimal volume (2-3 exercises per session)',
            'rest': 'Allow 2-3 days rest between similar muscle groups',
            'emphasis': 'Focus on learning proper form and movement patterns'
        },
        'intermediate': {
            'intensity': 'moderate',
            'volume': 'Moderate volume (4-5 exercises per session)',
            'rest': 'Allow 48-72 hours rest between similar muscle groups',
            'emphasis': 'Balance progressive overload with recovery'
        },
        'advanced': {
            'intensity': 'moderate-high',
            'volume': 'Higher volume with periodization (5-7 exercises)',
            'rest': 'Strategic recovery based on training split',
            'emphasis': 'Implement advanced training techniques and periodization'
        }
    }

    exp_data = experience_mapping.get(experience, experience_mapping['beginner'])

    # Create normalized report
    normalized_report = {
        "report_id": f"new_user_{goal}_{experience}",
        "goal": goal,
        "overall_status": "new_user_onboarding",
        "user_type": "new_registration",
        "experience_level": experience,
        "strengths": [
            f"New user with {experience} experience level - starting fresh with proper foundation.",
            "No previous workout history to analyze - blank slate for optimal programming.",
            f"Goal of {goal} is clear and will guide programming decisions."
        ],
        "adjustments": {
            "intensity_guidance": f"{exp_data['intensity'].upper()} intensity is appropriate for {experience} level. {exp_data['emphasis']}",
            "volume_guidance": f"{exp_data['volume']}. Avoid overtraining in early stages.",
            "cardio_vs_strength_emphasis": (
                f"For {goal} goal: " +
                ("Emphasize cardio with moderate strength training." if goal == 'fat_loss' else
                 "Emphasize strength training with minimal cardio." if goal == 'muscle_gain' else
                 "Balance both cardio and strength training equally.")
            ),
            "recovery_considerations": f"{exp_data['rest']}. New users need adequate recovery to adapt.",
            "form_and_technique": "CRITICAL: Prioritize perfect form over weight/intensity. Learn movement patterns first."
        },
        "protected_elements": [
            "Maintain conservative progression to prevent injury",
            "Focus on compound movements to learn fundamental patterns",
            "Ensure adequate rest and recovery between sessions",
            "Build sustainable habits rather than rushing progress"
        ],
        "adjustment_rationale": {
            "conservative_approach": f"As a {experience} user, starting conservatively prevents injury and builds proper foundation.",
            "learning_phase": "Initial weeks focus on motor learning and adaptation rather than maximum intensity.",
            "habit_formation": "Sustainable progression is more important than aggressive initial gains.",
            "injury_prevention": "New users have higher injury risk - proper progression is critical."
        },
        "metrics_reference": {
            "calorie_deficit": 0,  # Will be calculated based on goal
            "protein_deficit": 0,
            "strength_completion_pct": 0,  # No history yet
            "cardio_completion_pct": 0,  # No history yet
            "intensity_multiplier": 0.8 if experience == 'beginner' else 1.0,
            "effort_score": 0.7  # Conservative for new users
        },
        "user_info": {
            "weight_kg": weight,
            "experience": experience
        },
        "new_user_warnings": [
            "NEW USER: Start with reduced intensity and volume",
            "Prioritize form and technique over weight",
            "Allow extra recovery time for adaptation",
            "Monitor for excessive soreness or fatigue",
            "Progress gradually - no rush for first 4-6 weeks"
        ]
    }

    return normalized_report


# ============================================================================
# SHARED TOOLS
# ============================================================================
def web_search(query: str) -> Dict[str, Any]:
    """
    Performs a live web search to find up-to-date information.

    Args:
        query: Search query string

    Returns:
        Search results dictionary or error dictionary
    """
    print(f"  🔍 [Web Search] Query: {query}")
    try:
        search_result = tavily_client.search(query=query, max_results=5)
        print(f"  ✓ Found {len(search_result.get('results', []))} results")
        return search_result
    except Exception as e:
        error_msg = f"Web search failed: {str(e)}"
        print(f"  ✗ [Error] {error_msg}")
        return {"error": error_msg}


def get_fitness_plan_by_latest_date(db_name: str = None) -> Dict[str, Any]:
    """
    Retrieves the most recent daily workout plan from the database.

    Args:
        db_name: Database filename (defaults to fitness.db)

    Returns:
        Dictionary containing plan data and exercises, or error dictionary
    """
    if not db_name:
        db_name = Config.DEFAULT_DB_NAME

    print(f"  💾 [Database] Fetching latest plan from {db_name}")

    try:
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get most recent plan
        plan_query = "SELECT * FROM daily_plans ORDER BY date DESC LIMIT 1"
        cursor.execute(plan_query)
        plan_row = cursor.fetchone()

        if not plan_row:
            conn.close()
            print("  ⚠ No previous plans found (likely a new user)")
            return {"message": "No previous plans found in database - this is a new user"}

        plan_data = dict(plan_row)
        plan_id = plan_data['id']
        print(f"  ✓ Found plan ID {plan_id} from {plan_data.get('date', 'unknown date')}")

        # Get associated exercises
        exercise_query = "SELECT * FROM exercises WHERE daily_plan_id = ?"
        cursor.execute(exercise_query, (plan_id,))
        exercise_rows = cursor.fetchall()

        plan_data['exercises'] = [dict(ex) for ex in exercise_rows]
        print(f"  ✓ Loaded {len(plan_data['exercises'])} exercises")

        conn.close()
        return plan_data

    except sqlite3.Error as e:
        error_msg = f"Database error: {str(e)}"
        print(f"  ✗ [Error] {error_msg}")
        return {"error": error_msg}


# ============================================================================
# RESPONSE PARSING UTILITIES
# ============================================================================
def extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Extract JSON from LLM response text, handling various formats.

    Args:
        text: Response text that may contain JSON

    Returns:
        Parsed JSON dictionary or None if no valid JSON found
    """
    if not text:
        return None

    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    # Remove leading "json" token if present
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Extract JSON object safely
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        return None

    json_text = text[start:end]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass

    return None


# ============================================================================
# ORCHESTRATOR AGENT (ENHANCED)
# ============================================================================
ORCHESTRATOR_SYSTEM_PROMPT = '''
You are the Orchestrator Agent for a fitness planning system.

==========================
YOUR ROLE
==========================
Analyze adjustment reports (including NEW USER registrations) and workout history
to create comprehensive JSON instructions for the Executor Agent that will generate
specific workout plans.

==========================
NEW USER HANDLING (CRITICAL)
==========================
When you see "user_type": "new_registration" or "new_user_warnings" in the report:

1. **CONSERVATIVE APPROACH MANDATORY**
   - Reduce intensity by 20-30% from normal programming
   - Limit exercises to 3-4 compound movements only
   - Use longer rest periods (2-3 minutes)
   - Focus on FORM and TECHNIQUE over weight

2. **EXPERIENCE-BASED PROGRAMMING**
   - Beginner: 2-3 exercises, full-body or upper/lower split, low intensity
   - Intermediate: 4-5 exercises, more variation, moderate intensity
   - Advanced: 5-6 exercises, can use splits, moderate-high intensity

3. **FIRST WORKOUT PRINCIPLES**
   - NO isolation exercises for beginners
   - Focus on: squat, bench press, row, overhead press, deadlift patterns
   - Teach proper breathing and bracing
   - Set conservative weights that allow 12-15 reps (even if goal is strength)
   - Plan for learning phase, not performance phase

4. **SAFETY GUARDRAILS**
   - No advanced techniques (drop sets, supersets, etc.)
   - No max effort lifts
   - Conservative calorie targets (small deficits/surpluses)

==========================
YOUR PROCESS (ALL USERS)
==========================
1. READ the adjustment report thoroughly - check if new user or existing
2. Call web_search() to research:
   - Muscle recovery requirements (for existing users)
   - Experience-appropriate exercises (for new users)
   - Progressive overload principles for the user's goal
   - Optimal training splits and rep ranges
   - Cardio recommendations based on goal
3. Call get_fitness_plan_by_latest_date() - if empty, this confirms new user
4. SYNTHESIZE everything into clear JSON instructions

==========================
KEY CONSIDERATIONS
==========================
- Total workout duration: 60 minutes (including cardio)
- Muscle groups typically need 48-72 hours recovery
- NEW USERS need 72-96 hours recovery initially
- Progressive overload: gradually increase intensity/volume over time
- Goal-specific training:
  * Fat loss: Higher cardio volume, moderate strength, calorie deficit
  * Muscle gain: Higher strength volume, lower cardio, calorie surplus
  * Maintenance: Balanced approach

==========================
OUTPUT FORMAT (STRICT JSON ONLY)
==========================
You MUST output ONLY valid JSON. Start with { and end with }. NO other text before or after.

{
  "user": {
    "date": "DD/MM/YYYY",
    "goal": "fat_loss|muscle_gain|maintenance",
    "user_type": "new_registration|returning_user",
    "experience": "beginner|intermediate|advanced"
    "weight_kg": "From database for exsisting(No database give none)| From input for new"
  },
  "previous_session": {
    "date": "DD/MM/YYYY or null",
    "trained": ["muscle group 1", "muscle group 2"] or [],
    "avoid_today": ["muscle group 1"] or [],
    "recovery_reason": "Detailed explanation or 'No previous workout - new user'"
  },
  "today_plan": {
    "muscles_to_train": [
      {"muscle": "chest", "intensity": "low|moderate|high"},
      {"muscle": "back", "intensity": "low|moderate|high"}
    ],
    "duration_min": 60,
    "training_style": "hypertrophy|strength|endurance",
    "overall_intensity": "low|moderate|high",
    "new_user_modifications": "Detailed safety guidelines if user_type is new_registration"
  },
  "cardio_requirements": {
    "enabled": true,
    "duration_min": 20,
    "target_heart_rate_bpm": "120-140",
    "intensity_label": "low|moderate|high"
  },
  "nutrition_targets": {
    "calories": 2200,
    "protein_g": 180,
    "carbs_g": 220,
    "fat_g": 60
  },
  "special_considerations": "Any important notes, warnings, or new user guidance"
}
'''


def create_orchestrator_model():
    """Create and configure the Orchestrator model"""
    return genai.GenerativeModel(
        model_name=Config.MODEL_NAME,
        system_instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40
        }
    )


# ============================================================================
# EXECUTOR AGENT (ENHANCED)
# ============================================================================
EXECUTOR_SYSTEM_PROMPT = '''
You are the Executor Agent for a fitness planning system.

==========================
YOUR ROLE
==========================
Parse JSON instructions from the Orchestrator Agent and generate a complete,
specific workout plan with exercises, sets, reps, cardio, and nutrition details.

**CRITICAL**: Pay special attention to user_type and experience level.

==========================
NEW USER SAFETY PROTOCOLS
==========================
When user_type is "new_registration":

1. **EXERCISE SELECTION FOR NEW USERS**
   - Beginners: ONLY compound movements with simple form
     * Goblet Squat (NOT barbell squat)
     * Dumbbell Bench Press (NOT barbell initially)
     * Lat Pulldown (NOT pull-ups)
     * Dumbbell Row
     * Dumbbell Shoulder Press
   - NO barbell back squats, deadlifts, or Olympic lifts for first 2-4 weeks
   - NO isolation exercises for beginners

2. **REP RANGES FOR NEW USERS**
   - Beginners: 10-15 reps, 2-3 sets, 2-3 min rest (learning phase)
   - Intermediate: 8-12 reps, 3 sets, 90 sec rest
   - Advanced: Can use varied rep ranges per goal

3. **WORKOUT STRUCTURE FOR NEW USERS**
 
   - Strength: 30-35 minutes (3-4 exercises maximum)
   - Cardio: 15-20 minutes (low intensity)
   - Total: 60 minutes with extra time for form instruction

4. **INTENSITY FOR NEW USERS**
   - Use RPE (Rate of Perceived Exertion) instead of % max
   - Target RPE 6-7 out of 10 (moderate, could do 3-4 more reps)
   - NO training to failure
   - Focus on "perfect reps" over "max reps"

==========================
YOUR PROCESS (ALL USERS)
==========================
1. PARSE the Orchestrator's JSON instructions carefully
2. IDENTIFY if this is a new user (check user_type and experience)
3. Call web_search() to research:
   - Experience-appropriate exercises for each target muscle group
   - Proper form and technique considerations for experience level
   - Rep ranges and set schemes for the training style AND experience
   - Specific cardio options and intensity guidance
   - Nutrition calculations for the user's stats
4. DESIGN a complete workout that:
   - Targets the specified muscles
   - Avoids the muscles that need recovery
   - Matches user's experience level (CRITICAL)
   - Fits within 60 minutes total
   - Matches the prescribed intensity and style
5. CALCULATE nutrition with detailed rationale

==========================
EXERCISE SELECTION RULES
==========================
- ALWAYS search for exercises - NEVER guess
- NEW USERS: 3-4 exercises maximum, all compound
- EXISTING USERS: 4-6 exercises, mix of compound and isolation
- Balance compound movements with isolation based on experience
- Compound exercises first, isolation later
- Allocate realistic time including rest between sets

==========================
REP RANGES BY EXPERIENCE AND STYLE
==========================
NEW USERS (First 4 weeks):
- All styles: 10-15 reps, 2-3 sets, 2-3 min rest (motor learning)

EXPERIENCED USERS:
- Strength: 3-6 reps, 4-5 sets, 3-4 min rest
- Hypertrophy: 8-12 reps, 3-4 sets, 1-2 min rest
- Endurance: 15+ reps, 2-3 sets, 30-60 sec rest

==========================
OUTPUT FORMAT (STRICT JSON ONLY)
==========================
Output ONLY valid JSON. Start with { and end with }. NO explanatory text.

{
  "date": "DD/MM/YYYY",
  "user_goal": "string",
  "daily_macros": {
    "calories": 2200,
    "protein_g": 180,
    "carbs_g": 220,
    "fats_g": 60
  },
  "workout_split": {
    "name": "Full Body - Beginner Foundation" or "Upper Body Push Day",
    "primary_muscles": ["chest", "legs", "back"],
    "secondary_muscles": ["arms", "shoulders"],
    "style": "motor_learning|hypertrophy|strength|endurance",
    "cardio": {
      "type": "Walking|Running|Cycling",
      "duration_minutes": 15,
      "distance_km": 2.0,
      "intensity": "low|moderate",
      "target_heart_rate_bpm": "120-140"
    }
  },
  "exercises": [
    {
      "name": "Barbell Bench Press",
      "sets": 4,
      "reps": "8-10",
      "time_minutes": 12
    }
  ],
  "time_required_minutes": 60,
  "diet_rationale": "Detailed explanation based on research and user goal",
  "workout_rationale": "Detailed explanation of exercise selection and structure",
  "current_weight": 80.0,
  "workout_intensity": "low|moderate|high",
  "calories_burnt": 300
}

==========================
CRITICAL RULES
==========================
- Total workout time (exercises + cardio) must equal ~60 minutes
- NEW USERS: Reduce intensity, focus on form, limit exercise count
- Exercises MUST match experience level appropriately
- Exercises MUST target muscles from today_plan
- NO exercises targeting muscles in avoid_today
- Use exact nutrition values from Orchestrator instructions
- Follow the prescribed training style, intensity, AND experience level
- Valid JSON syntax: no trailing commas, proper quotes, valid numbers
'''


def create_executor_model():
    """Create and configure the Executor model"""
    return genai.GenerativeModel(
        model_name=Config.MODEL_NAME,
        system_instruction=EXECUTOR_SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 40
        }
    )


# ============================================================================
# MAIN WORKFLOW WITH FUNCTION CALLING
# ============================================================================
def run_orchestrator_phase(adjustment_report: Dict, max_retries: int) -> Optional[str]:
    """
    Phase 1: Orchestrator analyzes report and creates instructions.

    Args:
        adjustment_report: User's fitness adjustment report (normalized)
        max_retries: Number of retry attempts

    Returns:
        Raw orchestrator output string or None
    """
    print("\n" + "=" * 80)
    print("PHASE 1: ORCHESTRATOR ANALYSIS")
    print("=" * 80)

    model = create_orchestrator_model()
    chat = model.start_chat(history=[])

    # Check if new user
    is_new_user = adjustment_report.get('user_type') == 'new_registration'
    experience = adjustment_report.get('experience_level', 'beginner')

    if is_new_user:
        print(f"\n⚠️  NEW USER DETECTED - {experience.upper()} level")
        print("    Applying conservative programming protocols...")

    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")

        try:
            print("\n  🔧 Gathering context for Orchestrator...")

            # 1. Search for experience-appropriate training
            if is_new_user:
                print(f"\n  → Searching for {experience} training guidelines...")
                training_search = web_search(
                    f"{experience} {adjustment_report['goal']} workout plan first time gym"
                )
            else:
                print("\n  → Searching for training recommendations...")
                training_search = web_search(
                    f"{adjustment_report['goal']} workout best practices progressive overload"
                )

            # 2. Get previous workout
            print("\n  → Fetching previous workout...")
            previous_workout = get_fitness_plan_by_latest_date()

            # 3. Search for recovery/beginner info
            if is_new_user:
                print("\n  → Searching for beginner safety guidelines...")
                safety_search = web_search(f"{experience} gym mistakes to avoid first workout")
            else:
                print("\n  → Searching for muscle recovery times...")
                safety_search = web_search(
                    f"{adjustment_report['goal']} muscle recovery time days"
                )

            # Build context prompt
            context_prompt = f"""
Based on your research:

PREVIOUS WORKOUT DATA:
{json.dumps(previous_workout, indent=2)}

TRAINING RESEARCH:
{json.dumps(training_search.get('results', [])[:2], indent=2)}

SAFETY/RECOVERY RESEARCH:
{json.dumps(safety_search.get('results', [])[:2], indent=2)}

USER ADJUSTMENT REPORT:
{json.dumps(adjustment_report, indent=2)}

{"⚠️ CRITICAL: This is a NEW USER - Apply all conservative programming protocols!" if is_new_user else ""}

Now generate your JSON instructions for the Executor Agent.
Remember: ONLY output valid JSON. Start with {{ and end with }}.
"""

            response = chat.send_message(context_prompt)
            response_text = response.text.strip()

            print(f"\n  📥 Orchestrator Output ({len(response_text)} chars):")
            print("  " + "-" * 76)
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            print("  " + "-" * 76)

            if len(response_text) < 50:
                print(f"  ✗ Output too short ({len(response_text)} chars)")
                continue

            # Validate JSON
            test_json = extract_json_from_text(response_text)
            if test_json:
                print("\n  ✓ Valid JSON detected in output")
                print(f"  📋 Keys found: {', '.join(test_json.keys())}")

                # Verify new user handling
                if is_new_user:
                    user_type = test_json.get('user', {}).get('user_type')
                    if user_type == 'new_registration':
                        print("  ✓ New user status correctly propagated")
            else:
                print("\n  ⚠ Could not extract valid JSON, but passing to Executor anyway")

            print("\n  ✓ Orchestrator phase complete")
            return response_text

        except Exception as e:
            print(f"  ✗ Orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()

    return None


def run_executor_phase(orchestrator_output: str, max_retries: int) -> Optional[Dict]:
    """
    Phase 2: Executor generates specific workout plan from instructions.

    Args:
        orchestrator_output: Raw output from Orchestrator
        max_retries: Number of retry attempts

    Returns:
        Parsed workout plan dictionary or None
    """
    print("\n" + "=" * 80)
    print("PHASE 2: EXECUTOR PLAN GENERATION")
    print("=" * 80)

    model = create_executor_model()
    chat = model.start_chat(history=[])

    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")

        try:
            print("  📤 Sending prompt to Executor...")

            # Extract structured data from orchestrator output
            orch_json = extract_json_from_text(orchestrator_output)

            if orch_json and 'today_plan' in orch_json:
                muscles = orch_json['today_plan'].get('muscles_to_train', [])
                training_style = orch_json['today_plan'].get('training_style', 'hypertrophy')
                user_type = orch_json.get('user', {}).get('user_type', 'returning_user')
                experience = orch_json.get('user', {}).get('experience', 'intermediate')

                is_new_user = user_type == 'new_registration'

                if is_new_user:
                    print(f"\n⚠️  NEW USER - Searching for {experience}-appropriate exercises...")
                else:
                    print(f"\n  🔧 Searching for exercises...")

                exercise_searches = []

                for muscle_obj in muscles[:3]:
                    if isinstance(muscle_obj, dict):
                        muscle = muscle_obj.get('muscle', '')
                    else:
                        muscle = str(muscle_obj)

                    if muscle:
                        if is_new_user:
                            search_query = f"{experience} beginner safe {muscle} exercises proper form"
                        else:
                            search_query = f"best {training_style} exercises for {muscle}"

                        print(f"\n  → Searching: {search_query}")
                        search_result = web_search(search_query)
                        exercise_searches.append({
                            "muscle": muscle,
                            "exercises": search_result.get('results', [])[:2]
                        })

                # Build context with exercise research
                context_prompt = f"""
ORCHESTRATOR INSTRUCTIONS:
{orchestrator_output}

EXERCISE RESEARCH:
{json.dumps(exercise_searches, indent=2)}

{"⚠️ CRITICAL: This is a NEW USER - Apply all safety protocols and conservative programming!" if is_new_user else ""}

Now generate the complete workout plan in JSON format.
Remember: ONLY output valid JSON. Start with {{ and end with }}.
"""

                response = chat.send_message(context_prompt)
            else:
                # Fallback if can't parse orchestrator output
                prompt = f"""
The Orchestrator has created these instructions for you:

{orchestrator_output}

Generate a complete workout plan following all safety protocols.
Remember: ONLY output valid JSON. Start with {{ and end with }}.
"""
                response = chat.send_message(prompt)

            response_text = response.text.strip()

            print(f"\n  📥 Executor Output ({len(response_text)} chars):")
            print("  " + "-" * 76)
            print(response_text[:800] + "..." if len(response_text) > 800 else response_text)
            print("  " + "-" * 76)

            # Parse JSON
            workout_plan = extract_json_from_text(response_text)

            if workout_plan:
                print(f"\n  ✓ Workout plan parsed successfully")
                print(f"  📋 Keys found: {', '.join(workout_plan.keys())}")

                # Validate required fields
                required_fields = ['date', 'user_goal', 'daily_macros', 'exercises']
                missing_fields = [f for f in required_fields if f not in workout_plan]

                if missing_fields:
                    print(f"  ⚠ Missing fields: {', '.join(missing_fields)}")
                    continue

                # Verify new user safety notes if applicable
                if workout_plan.get('user_type') == 'new_registration':
                    print("  ✓ New user workout plan generated with safety protocols")

                return workout_plan
            else:
                print(f"  ✗ Failed to parse JSON from response")

        except Exception as e:
            print(f"  ✗ Executor error: {str(e)}")
            import traceback
            traceback.print_exc()

    return None


def run_two_llm_workflow(
    user_input: Dict,
    max_retries: int = None
) -> Optional[Dict]:
    """
    Main workflow orchestrating both agents with input normalization.

    Args:
        user_input: Raw user input (either new user or adjustment report)
        max_retries: Number of retry attempts (defaults to Config.MAX_RETRIES)

    Returns:
        Complete workout plan dictionary or None if failed
    """
    if max_retries is None:
        max_retries = Config.MAX_RETRIES

    print("\n" + "=" * 80)
    print("🏋️  TWO-LLM FITNESS AGENT WORKFLOW (ENHANCED)")
    print("=" * 80)
    print(f"Configuration: {max_retries} retries per phase")
    print(f"Model: {Config.MODEL_NAME}")

    # Normalize input
    print("\n📋 INPUT NORMALIZATION")
    print("-" * 80)
    adjustment_report = normalize_input_to_report(user_input)

    # Phase 1: Orchestrator
    orchestrator_output = run_orchestrator_phase(adjustment_report, max_retries)

    if not orchestrator_output:
        print("\n" + "=" * 80)
        print("❌ WORKFLOW FAILED: Orchestrator phase failed")
        print("=" * 80)
        return None

    # Phase 2: Executor
    workout_plan = run_executor_phase(orchestrator_output, max_retries)

    if not workout_plan:
        print("\n" + "=" * 80)
        print("❌ WORKFLOW FAILED: Executor phase failed")
        print("=" * 80)
        return None

    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 80)

    return workout_plan


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================
def create_sample_adjustment_report() -> Dict:
    """Create a sample adjustment report for testing (existing user)"""
    return {
        "report_id": "adjustment_report_001",
        "goal": "fat_loss",
        "overall_status": "needs_adjustment",
        "strengths": [
            "Strength training completion was excellent (100% completion).",
            "Protein intake is adequate.",
            "Overall effort is high (effort score 0.933)."
        ],
        "adjustments": {
            "intensity_guidance": "Training intensity is currently adequate.",
            "volume_guidance": "Strength training volume is well-tolerated.",
            "cardio_vs_strength_emphasis": "Cardio completion is low (40%). Increase cardio.",
            "recovery_considerations": "The calorie deficit is very high (1492.3 calories)."
        },
        "protected_elements": [
            "Continue prioritizing strength training sessions.",
            "Maintain current protein intake levels.",
            "Sustain high effort levels."
        ],
        "adjustment_rationale": {
            "calorie_deficit_too_high": "Very high deficit can lead to fatigue and muscle loss.",
            "low_cardio_completion": "Cardio completion significantly below target affects fat loss."
        },
        "metrics_reference": {
            "calorie_deficit": 1492.3,
            "protein_deficit": 36.24,
            "strength_completion_pct": 100.0,
            "cardio_completion_pct": 40.0,
            "intensity_multiplier": 1.33,
            "effort_score": 0.933
        },
    }


def create_sample_new_user() -> Dict:
    """Create a sample new user registration (minimal format)"""
    user_weight = input("Enter your weight in Kg's: ")
    user_experience = input("Enter your experience in working out in one word")
    
    return {
        "weight": user_weight,
        "experience": user_experience,
        "goal": "muscle_gain",
    }
def generate_workout_plan(
    user_input: Dict,
    workout_adjustments: Optional[Dict] = None
) -> Dict:
    """
    Entry point for Stage 1 workflow.

    Priority:
    1. If workout_adjustments exists → use it
    2. Else → use user_input
    """

    if workout_adjustments is not None:
        workflow_input = workout_adjustments
    else:
        workflow_input = user_input

    plan = run_two_llm_workflow(workflow_input)

    if not plan:
        raise RuntimeError("Workout plan generation failed")

    # Server-authoritative date
    plan["date"] = datetime.now().strftime("%d/%m/%Y")

    return plan




# def main():

    

#     # # Test 2: Existing User with Adjustment Report
#     if workout_adjustments is not None:
#         existing_user = workout_adjustments
#     else:
#         existing_user = create_sample_new_user()

#     plan2 = run_two_llm_workflow(existing_user)
    


#     if plan2:
#         today_date = datetime.now().strftime("%d/%m/%y")
#         plan2["date"] = today_date  # overwrite date field

#         print(json.dumps(plan2, indent=2))

#         output_file1 = "./output.json"
#         os.makedirs(os.path.dirname(output_file1), exist_ok=True)
#         with open(output_file1, 'w') as f:
#             json.dump(plan2, f, indent=2)

#         print(f"\n💾 Saved to: {output_file1}")


# if __name__ == "__main__":
#     main()