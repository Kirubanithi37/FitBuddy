import os
import logging
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .schemas import UserInput, FeedbackRequest
from .database import (
    save_user, save_plan, update_plan, get_original_plan, get_user,
    get_all_users, get_all_plans, delete_user
)
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
router = APIRouter()

logger = logging.getLogger(__name__)


def get_user_friendly_error(exc):
    error_text = str(exc)

    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        return (
            "AI service is temporarily unavailable because the daily "
            "Gemini API request limit has been reached. Please try again later."
        )

    if "GOOGLE_API_KEY" in error_text:
        return (
            "The AI service is not configured correctly. "
            "Please check the Gemini API configuration."
        )

    if "google" in error_text.lower() or "gemini" in error_text.lower():
        return (
            "The AI service is temporarily unavailable. "
            "Please try again later."
        )

    return "Something went wrong while creating your fitness plan. Please try again."


def render_error(request, message):
    return templates.TemplateResponse(request = request, name="index.html", context = {"request": request, "error": message})


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={"request": request}
    )


@router.post("/generate-workout")
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight,
                         goal=goal, intensity=intensity)
        user = save_user(data.user_id, data.username, data.age, data.weight, data.goal, data.intensity)
        workout_plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
        nutrition_tip = generate_nutrition_tip_with_flash(data.goal)
        plan = save_plan(user.id, workout_plan, nutrition_tip)

        return templates.TemplateResponse(request = request, name="result.html", context = {
            "request": request,
            "username": data.username,
            "user_id": data.user_id,
            "age": data.age,
            "weight": data.weight,
            "goal": data.goal,
            "intensity": data.intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "plan_id": plan.id,
        })
    except Exception as exc:
        logger.exception("Error while processing request")
        return render_error(request, get_user_friendly_error(exc))


@router.post("/submit-feedback")
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        request_data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(request_data.user_id)
        plan = get_original_plan(request_data.user_id)

        if not user or not plan:
            return render_error(request, "User or workout plan was not found.")

        revised_plan = update_workout_plan(
            plan.original_plan,
            request_data.feedback,
            user.username,
            user.goal,
            user.intensity,
        )
        nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
        updated = update_plan(plan.id, revised_plan, request_data.feedback, nutrition_tip)

        return templates.TemplateResponse(request = request, name="result.html", context= {
            "request": request,
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": updated.updated_plan,
            "nutrition_tip": updated.nutrition_tip,
            "plan_id": updated.id,
            "feedback_message": "Your workout plan has been updated successfully.",
        })
    except Exception as exc:
        logger.exception("Error while processing feedback")
        return render_error(request, get_user_friendly_error(exc))


@router.get("/view-all-users")
async def view_all_users(request: Request):
    users = get_all_users()
    plans = get_all_plans()
    return templates.TemplateResponse(request = request, name="all_users.html", context= {
        "request": request,
        "users": users,
        "plans": plans,
    })


@router.post("/delete-user")
async def remove_user(user_id: str = Form(...)):
    delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)

@router.get("/sample-plan")
async def sample_plan(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "username": "Demo User",
            "user_id": "DEMO001",
            "age": 18,
            "weight": 65,
            "goal": "Weight Loss",
            "intensity": "Moderate",
            "workout_plan": """**Day 1 - Full Body**

Warm-up: 5-10 minutes

**Main Workout**
- Squats - 3 sets × 12 reps
- Lunges - 3 sets × 10 reps
- Plank - 3 × 30 seconds
- Jumping Jacks - 3 × 20 reps

Rest: 60 seconds between sets.

**Cooldown**
5-10 minutes of stretching.

---

**Day 2 - Cardio**

- Brisk Walking - 30 minutes
- Light Jogging - 10 minutes

Cooldown: 5 minutes of stretching.

---

**Day 3 - Upper Body**

- Push-ups - 3 × 10
- Shoulder Taps - 3 × 12
- Arm Circles - 3 × 20

Cooldown: 5-10 minutes.

---

**Day 4 - Recovery**

Light walking and stretching.

---

**Day 5 - Lower Body**

- Squats - 3 × 12
- Lunges - 3 × 10
- Calf Raises - 3 × 15

---

**Day 6 - Cardio + Core**

- Brisk Walking - 30 minutes
- Plank - 3 × 30 seconds
- Mountain Climbers - 3 × 15

---

**Day 7 - Active Recovery**

Light walking, stretching and rest.""",
            "nutrition_tip": "Stay hydrated and include enough protein, vegetables and whole foods in your daily meals.",
            "feedback_message": None
        }
    )