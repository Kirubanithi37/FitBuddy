import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)


def update_workout_plan(original_plan, feedback, username, goal, intensity):
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured. Add it to the .env file.")

    prompt = f"""
Update the following fitness plan based on the user's feedback.

User: {username}
Goal: {goal}
Intensity: {intensity}

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Return a complete revised 7-day plan. Preserve useful parts of the original plan while applying the feedback.

Keep:
- Warm-up
- Main workout
- Sets/reps or duration
- Rest
- Cooldown/recovery guidance
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text