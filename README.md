# AI-Powered Fitness Planning System

A comprehensive fitness planning system that uses multi-agent AI architecture to generate personalized workout plans, meal plans, and track progress with intelligent adjustments.

## Overview

This system combines three major components:
1. **Workout Plan Generation** - Two-LLM orchestrator-executor architecture for creating personalized daily workout plans
2. **Meal Plan Generation** - Semantic meal planning with real-time nutritional data
3. **Progress Tracking & Adjustment** - Intelligent tracking system that evaluates performance and suggests adjustments

## Key Features

### Intelligent Workout Planning
- **Two-LLM Architecture**: Orchestrator analyzes user data and generates plans for Executor agent to generate specific plan
- **Adaptive to Experience Levels**: Beginner, Intermediate, Advanced
- **New User Safety Protocols**: Conservative programming for first-time gym-goers
- **Web Search Integration**: Real-time research for exercise recommendations and best practices
- **Goal-Specific Training**: Fat loss, muscle gain, or maintenance
- **Tracks History**: Considers the previous workout routines and selects muscle groups to target

### Smart Meal Planning
- **Macro-Based Recipe Generation**: Automatically creates recipes matching nutritional targets
- **Real-Time Nutrition Database**: Integrates with Open Food Facts API
- **Adaptive Meal Structure**: Adjusts meal timing based on workout intensity
- **Dietary Customization**: Supports various diets, allergies, and cooking skill levels

### Progress Tracking
- **Workout Performance Tracking**: Track sets, reps, cardio distance, and time
- **Intelligent Evaluation**: Analyzes calorie deficits, macro adherence, and training completion
- **Automated Adjustments**: Generates adjustment reports for next workout
- **Handling Database**: Maintains MongoDb dat

## Architecture

### Workout Generation Pipeline

```
User Input (New/Existing)
    ↓
Normalization Layer
    ↓
Orchestrator Agent (Gemini 2.5 Flash)
    ├── Web Search (Tavily)
    ├── Database Query (Previous Workouts)
    └── Analysis & Instruction Generation
    ↓
Executor Agent (Gemini 2.5 Flash)
    ├── Exercise Research
    ├── Rep Range Calculation
    └── Complete Workout Plan Generation
    ↓
SQLite Database Storage and passed for multi-agentic workflow
```

### Meal Planning Pipeline

```
Workout Plan Output
    ↓
Semantic Classification (Gemini)
    ├── Workout Focus Detection
    ├── Intensity Analysis
    └── Recovery Requirements
    ↓
Meal Structure Decision
    ├── Breakfast
    ├── Post-Workout (if needed)
    ├── Lunch
    └── Dinner
    ↓
Per-Meal Recipe Generation (Gemini)
    ├── Ingredient Selection
    ├── Macro Calculation (Open Food Facts)
    └── Recipe Instructions
```

### Tracking & Adjustment Pipeline

```
User Logs Food & Workout
    ↓
Nutrition Analysis (Computer Vision + Database)
    ↓
Workout Performance Evaluation
    ├── Strength Completion 
    ├── Cardio Completion 
    ├── Intensity Multiplier
    └── Effort Score
    ↓
Threshold Evaluation (Goal-Specific)
    ├── Calorie Deficit Analysis
    ├── Macro Adherence Check
    ├── Training Volume Assessment
    └── Recovery Considerations
    ↓
Adjustment Report Generation (Gemini)
    ├── Strengths
    ├── Required Adjustments
    ├── Protected Elements
    └── Rationale
```

##  Getting Started

### Prerequisites

```bash
Python 3.8+
SQLite3
PIL (Pillow)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Prabhatkukunuri/innov-ai-tion.git
cd fitness-planning-system
```

2. **Install dependencies**
```bash
pip install google-generativeai tavily-python python-dotenv pillow requests
```

3. **Set up environment variables**

Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_KEY2=your_gemini_api_key_here
GEMINI_API_KEY3=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

4. **Initialize the database**
```bash
python tracking_system.py  # Creates fitness.db automatically
```
## Project Structure

```
fitness-planning-system
├── workout_llm.py           # Two-LLM workout generation system
├── cooking_LLM.py           # Meal planning and recipe generation
├── tracking_llm.py         # Progress tracking and evaluation
├── fitness.db                 # SQLite database
├── nutrition_db.json          # Cached nutrition data
├── nutrition_db2.json          # Cached nutrition data
├── .env                       # Environment variables
├── requirements.txt           # Environment variables
└── README.md                  # This file


```

## Key Features Explained

### 1. **New User Safety Protocols**
- Automatically detects first-time users
- Applies conservative programming (20-30% reduced intensity)
- Focuses on compound movements only
- Extended rest periods and learning phase approach

### 2. **Web Search Integration**
- Real-time research for exercises based on experience level
- Muscle recovery requirements
- Progressive overload principles
- Training split recommendations

### 3. **Computer Vision Food Logging**
- Upload food images
- AI identifies ingredients
- Fetches nutritional data from Open Food Facts
- Calculates total macros

### 4. **Intelligent Adjustment System**
- Analyzes workout completion rates
- Evaluates nutritional adherence
- Generates structured adjustment reports
- Provides specific, actionable recommendations

### 5. **Semantic Meal Planning**
- Classifies workout characteristics
- Determines optimal meal structure
- Generates recipes matching macro targets
- Validates nutritional accuracy

## 📊 Database Schema

### `daily_plans` Table
```sql
- id (PRIMARY KEY)
- date (UNIQUE)
- user_goal
- calories, protein_g, carbs_g, fats_g
- workout_split
- time_required_minutes
- diet_rationale, workout_rationale
- current_weight
- workout_intensity
- calories_to_burn
```


## 🔐 API Keys Required

1. **Google Gemini API** - For LLM generation
   - Get it from: https://ai.google.dev/
   
2. **Tavily API** - For web search
   - Get it from: https://tavily.com/

## ⚠️ Important Notes

- The system uses **Gemini 2.5 Flash** for fast, cost-effective generation
- Nutrition data is cached in `nutrition_db.json` to reduce API calls
- Database resets between tasks in the current implementation
- Web search is used judiciously to stay within rate limits

## 🤝 Contributing

This is a hackathon project. Contributions, issues, and feature requests are welcome!

## 👥 Authors

Hackathon Team - Rishab Pillai, Harish, Prabhat Kukunuri

## 🙏 Acknowledgments

- Google Gemini for powerful LLM capabilities
- Tavily for web search integration
- Open Food Facts for nutritional database
- Anthropic Claude for development assistance

---

**Built for Innov-ai-tion - 2025**
