import traceback
import datetime as dt
from sqlalchemy.orm import Session
from .models import Job
from .video_pipeline.run_pipeline import run_full_pipeline

def run_job(db: Session, job_id: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return

    try:
        job.status = "running"
        job.updated_at = dt.datetime.utcnow()
        db.commit()

        out_mp4 = run_full_pipeline(text=job.input_text, job_id=job_id)

        job.status = "succeeded"
        job.output_file = out_mp4
        job.updated_at = dt.datetime.utcnow()
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error = f"{e}\n\n{traceback.format_exc()}"
        job.updated_at = dt.datetime.utcnow()
        db.commit()
