from sqlalchemy import Column, Integer, String, Text, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

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
    rater = Column(String, nullable=True)    

    response = relationship("Response", back_populates="ratings")

engine = create_engine("sqlite:///database.db",connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
