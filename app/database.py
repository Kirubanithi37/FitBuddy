from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:////tmp/fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(20), nullable=False)
    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    user = relationship("User", back_populates="plans")


Base.metadata.create_all(bind=engine)


def save_user(user_id, username, age, weight, goal, intensity):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.user_id == user_id).first()
        if existing:
            existing.username = username
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
            db.commit()
            db.refresh(existing)
            return existing
        user = User(user_id=user_id, username=username, age=age, weight=weight,
                    goal=goal, intensity=intensity)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def save_plan(user_id, original_plan, nutrition_tip=""):
    db = SessionLocal()
    try:
        plan = WorkoutPlan(user_id=user_id, original_plan=original_plan,
                           nutrition_tip=nutrition_tip)
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    finally:
        db.close()


def update_plan(plan_id, updated_plan, feedback, nutrition_tip=None):
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.feedback = feedback
        if nutrition_tip is not None:
            plan.nutrition_tip = nutrition_tip
        db.commit()
        db.refresh(plan)
        return plan
    finally:
        db.close()


def get_original_plan(user_id):
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).join(User).filter(User.user_id == user_id).order_by(WorkoutPlan.id.desc()).first()
    finally:
        db.close()


def get_user(user_id):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    finally:
        db.close()


def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).order_by(User.id.desc()).all()
    finally:
        db.close()


def get_all_plans():
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).order_by(WorkoutPlan.id.desc()).all()
    finally:
        db.close()


def delete_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
    finally:
        db.close()
