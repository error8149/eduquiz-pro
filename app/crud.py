from sqlalchemy.orm import Session

from . import models, schemas

# --- CRUD Operations for Quizzes ---

def get_quiz(db: Session, quiz_id: int):
    """
    Reads a single quiz from the database by its ID.
    """
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

def get_quizzes(db: Session, skip: int = 0, limit: int = 100):
    """
    Reads a list of all quizzes from the database, with pagination.
    """
    return db.query(models.Quiz).order_by(models.Quiz.timestamp.desc()).offset(skip).limit(limit).all()

def create_quiz(db: Session, quiz: schemas.QuizCreate) -> models.Quiz:
    """
    Creates a new quiz session and all its associated questions in the database.
    """
    # Create the main Quiz object with new fields
    db_quiz = models.Quiz(
        score=quiz.score,
        total_questions=quiz.total_questions,
        time_taken=quiz.time_taken,
        mode=quiz.mode,
        sections=quiz.sections,
        grade_level=getattr(quiz, 'grade_level', 'high school'),
        difficulty=getattr(quiz, 'difficulty', 'medium')
    )
    db.add(db_quiz)
    
    # We need to commit here so that db_quiz gets its ID from the database.
    # This ID is needed to associate the questions with it.
    db.commit()
    db.refresh(db_quiz)

    # Create and add all the QuizQuestion objects
    for question_data in quiz.questions:
        # Convert Pydantic model to dict, then to SQLAlchemy model
        question_dict = question_data.dict() if hasattr(question_data, 'dict') else question_data
        db_question = models.QuizQuestion(**question_dict, quiz_id=db_quiz.id)
        db.add(db_question)

    # Commit the new questions to the database.
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz