import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Quiz(Base):
    """
    Represents a completed quiz session in the database.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_taken = Column(String)
    mode = Column(String)
    sections = Column(String)
    grade_level = Column(String, default="high school", nullable=True)
    difficulty = Column(String, default="medium", nullable=True)

    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    """
    Represents a single question that belongs to a quiz session.
    """
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)

    question_text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String, nullable=False)
    user_answer = Column(String)
    explanation = Column(String)
    section = Column(String)
    topic = Column(String)

    quiz = relationship("Quiz", back_populates="questions")