import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)


def generate_nutrition_tip_with_flash(goal):
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured. Add it to the .env file.")

    prompt = f"""
Give one concise, practical nutrition or recovery tip for someone whose fitness goal is: {goal}.

Keep it actionable and beginner-friendly.
Do not provide extreme diets or unsafe medical advice.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text