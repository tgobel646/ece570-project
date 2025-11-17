from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True)
    prompt = Column(Text)
    model = Column(String)
    response = Column(Text)
    rating = Column(Integer, nullable=True)
    correct_answer = Column(Text, nullable=True)

engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
