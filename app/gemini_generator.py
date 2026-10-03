import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)


def generate_workout_gemini(username, age, weight, goal, intensity):
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured. Add it to the .env file.")

    prompt = f"""
Create a personalized 7-day fitness plan for the following user.

Name: {username}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

Return a clear day-by-day plan. For every day include:
- Day and workout focus
- Warm-up (5-10 minutes)
- Main workout with exercise name, sets, reps or duration, and rest
- Cooldown or recovery tip

Keep the plan practical, structured, safe, and easy to follow.
Consider the user's goal and intensity.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text