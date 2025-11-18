# backend/models.py

from sqlalchemy import Column, Integer, String, Text, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import os

Base = declarative_base()

DATABASE_URL = os.getenv("postgresql://llm_eval_db_344y_user:XboiOQGXAea1V8BphCgn8mXbRHFIQ2er@dpg-d4dn5pc9c44c73bcbsmg-a.ohio-postgres.render.com/llm_eval_db_344y")

if not DATABASE_URL:
    # Local fallback: SQLite (for running on your laptop)
    DATABASE_URL = "sqlite:///./database.db"
    connect_args = {"check_same_thread": False}
else:
    # Postgres on Render
    connect_args = {}

print(f"Using DATABASE_URL={DATABASE_URL}")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True)
    prompt = Column(Text)
    model = Column(String)
    response = Column(Text)
    rating = Column(Integer, nullable=True)     
    correct_answer = Column(Text, nullable=True)
    ratings = relationship("Rating", back_populates="response")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    score = Column(Integer, nullable=False)  # e.g., 1 for 👍, -1 for 👎
    rater = Column(String, nullable=True)    # optional: user id/name

    response = relationship("Response", back_populates="ratings")


engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
