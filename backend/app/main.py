import os
import uuid
import datetime as dt
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .config import settings
from .db import engine, get_db
from .models import Base, User, Job
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .jobs import run_job

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage dirs
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
os.makedirs(settings.ASSETS_DIR, exist_ok=True)

# Serve outputs
app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_DIR), name="outputs")

Base.metadata.create_all(bind=engine)

class SignupIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class GenerateIn(BaseModel):
    text: str
    style: str = "bold"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/signup")
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    u = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        credits=settings.STARTING_CREDITS,
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    token = create_access_token(u.id)
    return {"access_token": token, "credits": u.credits}


@app.post("/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == payload.email.lower()).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(u.id)
    return {"access_token": token, "credits": u.credits}


@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"email": user.email, "credits": user.credits}

@app.post("/generate-video")
def generate_video(
    payload: GenerateIn,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    text = (payload.text or "").strip()
    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Text too short")

    if user.credits < settings.VIDEO_COST_CREDITS:
        raise HTTPException(status_code=402, detail="Not enough credits")

    # Deduct credits immediately (simple MVP)
    user.credits -= settings.VIDEO_COST_CREDITS
    db.commit()

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job = Job(
        id=job_id,
        user_id=user.id,
        status="queued",
        input_text=text,
        created_at=dt.datetime.utcnow(),
        updated_at=dt.datetime.utcnow(),
    )
    db.add(job)
    db.commit()

    # Run in background
    bg.add_task(run_job, db, job_id)

    return {"job_id": job_id, "status": "queued", "credits_left": user.credits}

@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    output_url = ""
    if job.status == "succeeded" and job.output_file:
        # output_file is a path; expose via /outputs static mount
        # Convert ".../storage/outputs/{job_id}/final.mp4" into URL
        # We’ll build it using known structure:
        output_url = f"/outputs/{job_id}/final.mp4"

    return {
        "job_id": job.id,
        "status": job.status,
        "error": job.error,
        "output_url": output_url,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

@app.get("/videos")
def list_videos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    jobs = (
        db.query(Job)
        .filter(Job.user_id == user.id)
        .order_by(Job.created_at.desc())
        .limit(50)
        .all()
    )
    out = []
    for j in jobs:
        out.append({
            "job_id": j.id,
            "status": j.status,
            "output_url": f"/outputs/{j.id}/final.mp4" if j.status == "succeeded" else "",
            "created_at": j.created_at,
        })
    return {"items": out}
