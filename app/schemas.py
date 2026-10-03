from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: str = Field(min_length=1, max_length=100)
    intensity: str


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    feedback: str = Field(min_length=1, max_length=2000)
