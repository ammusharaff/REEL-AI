import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    credits = Column(Integer, default=5)

    created_at = Column(DateTime, default=lambda: dt.datetime.utcnow())

    jobs = relationship("Job", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String(64), primary_key=True)  # job_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String(32), default="queued")  # queued/running/succeeded/failed
    input_text = Column(Text, default="")
    error = Column(Text, default="")

    output_file = Column(String(512), default="")  # path
    created_at = Column(DateTime, default=lambda: dt.datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: dt.datetime.utcnow())

    user = relationship("User", back_populates="jobs")
