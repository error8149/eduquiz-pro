import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, validator


class QuestionBase(BaseModel):
    """
    Base schema for quiz questions, used for both input and output.
    """
    question_text: str = Field(..., min_length=1, max_length=500, strip_whitespace=True)
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str = Field(..., min_length=1, strip_whitespace=True)
    explanation: str = Field(..., min_length=1, max_length=1000, strip_whitespace=True)
    section: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    topic: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    user_answer: Optional[str] = Field(None, min_length=1, strip_whitespace=True)

    @validator("correct_answer")
    def correct_answer_in_options(cls, v, values):
        """Ensure correct_answer is one of the options."""
        if "options" in values and v not in values["options"]:
            raise ValueError("Correct answer must be one of the provided options")
        return v

    @validator("options")
    def options_unique(cls, v):
        """Ensure all options are unique."""
        if len(set(v)) != len(v):
            raise ValueError("Options must be unique")
        return v

    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }

class QuestionCreate(QuestionBase):
    """
    Schema for creating a new question, inherits from QuestionBase.
    """
    pass

class Question(QuestionBase):
    """
    Schema for retrieving a question, includes database-generated fields.
    """
    id: int
    quiz_id: int

    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    """
    Base schema for quizzes, used for both input and output.
    """
    score: int
    total_questions: int
    time_taken: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    mode: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    sections: str = Field(..., min_length=1, max_length=500, strip_whitespace=True)
    grade_level: Optional[str] = Field("high school", min_length=1, max_length=50, strip_whitespace=True)
    difficulty: Optional[str] = Field("medium", min_length=1, max_length=20, strip_whitespace=True)

    @validator("score")
    def score_valid(cls, v, values):
        """Ensure score is between 0 and total_questions."""
        if "total_questions" in values and (v < 0 or v > values["total_questions"]):
            raise ValueError("Score must be between 0 and total questions")
        return v

    @validator("total_questions")
    def total_questions_valid(cls, v):
        """Ensure total_questions is between 1 and 50."""
        if v < 1 or v > 50:
            raise ValueError("Total questions must be between 1 and 50")
        return v

    @validator("time_taken")
    def time_taken_format(cls, v):
        """Ensure time_taken matches MM:SS format."""
        import re
        if not re.match(r"^\d+:[0-5]\d$", v):
            raise ValueError("Time taken must be in MM:SS format")
        return v

    @validator("difficulty")
    def difficulty_valid(cls, v):
        """Ensure difficulty is one of the valid options."""
        if v and v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be one of: easy, medium, hard")
        return v

class QuizCreate(QuizBase):
    """
    Schema for creating a new quiz, includes questions.
    """
    questions: List[QuestionCreate] = Field(..., min_items=1)

class Quiz(QuizBase):
    """
    Schema for retrieving a quiz, includes database-generated fields and questions.
    """
    id: int
    timestamp: datetime.datetime
    questions: List[Question] = []

    class Config:
        from_attributes = True

class StartQuizRequest(BaseModel):
    """
    Schema for starting a quiz with AI-generated questions.
    """
    topics: List[dict] = Field(..., min_items=1)
    num_questions: int
    api_provider: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    api_key: str = Field(..., min_length=1, strip_whitespace=True)
    grade_level: Optional[str] = Field("high school", min_length=1, max_length=50, strip_whitespace=True)
    difficulty: Optional[str] = Field("medium", min_length=1, max_length=20, strip_whitespace=True)

    @validator("num_questions")
    def num_questions_valid(cls, v):
        """Ensure num_questions is between 1 and 50."""
        if v < 1 or v > 50:
            raise ValueError("Number of questions must be between 1 and 50")
        return v

    @validator("api_provider")
    def api_provider_valid(cls, v):
        """Ensure api_provider is one of the supported providers."""
        valid_providers = ["gemini", "openai", "groq"]
        if v not in valid_providers:
            raise ValueError(f"API provider must be one of: {', '.join(valid_providers)}")
        return v

    @validator("topics")
    def topics_valid(cls, v):
        """Ensure each topic dict has valid section and topic fields."""
        for topic_dict in v:
            if not isinstance(topic_dict, dict) or "section" not in topic_dict or "topic" not in topic_dict:
                raise ValueError("Each topic must be a dict with 'section' and 'topic' keys")
            if not topic_dict["section"] or not topic_dict["topic"]:
                raise ValueError("Section and topic must not be empty")
        return v

    @validator("difficulty")
    def difficulty_valid(cls, v):
        """Ensure difficulty is one of the valid options."""
        if v and v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be one of: easy, medium, hard")
        return v

    @validator("grade_level")
    def grade_level_valid(cls, v):
        """Ensure grade_level is valid."""
        valid_grades = ["elementary", "middle school", "high school", "college", "graduate"]
        if v and v not in valid_grades:
            raise ValueError(f"Grade level must be one of: {', '.join(valid_grades)}")
        return v

class GeneratePromptRequest(BaseModel):
    """
    Schema for generating a prompt for manual mode.
    """
    num_questions: int
    topics: Dict[str, List[str]] = Field(..., min_items=1)
    grade_level: Optional[str] = Field("high school", min_length=1, max_length=50, strip_whitespace=True)
    difficulty: Optional[str] = Field("medium", min_length=1, max_length=20, strip_whitespace=True)

    @validator("num_questions")
    def num_questions_valid(cls, v):
        """Ensure num_questions is between 1 and 50."""
        if v < 1 or v > 50:
            raise ValueError("Number of questions must be between 1 and 50")
        return v

    @validator("topics")
    def topics_valid(cls, v):
        """Ensure topics dict is not empty and contains valid topics."""
        if not v:
            raise ValueError("At least one section with topics must be provided")
        for section, topics in v.items():
            if not section:
                raise ValueError("Section name must not be empty")
            if not topics:
                raise ValueError(f"At least one topic must be provided for section: {section}")
        return v

    @validator("difficulty")
    def difficulty_valid(cls, v):
        """Ensure difficulty is one of the valid options."""
        if v and v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be one of: easy, medium, hard")
        return v

    @validator("grade_level")
    def grade_level_valid(cls, v):
        """Ensure grade_level is valid."""
        valid_grades = ["elementary", "middle school", "high school", "college", "graduate"]
        if v and v not in valid_grades:
            raise ValueError(f"Grade level must be one of: {', '.join(valid_grades)}")
        return v

class GeneratePromptResponse(BaseModel):
    """
    Schema for the response containing the generated prompt.
    """
    prompt: str = Field(..., min_length=1, strip_whitespace=True)

class AskAIRequest(BaseModel):
    """
    Schema for requesting an AI explanation.
    """
    question_context: dict
    user_query: str = Field(..., min_length=1, max_length=500, strip_whitespace=True)
    api_key: str = Field(..., min_length=1, strip_whitespace=True)

    @validator("question_context")
    def question_context_valid(cls, v):
        """Ensure question_context has required fields."""
        required_fields = ["question_text", "explanation"]
        if not isinstance(v, dict) or not all(field in v for field in required_fields):
            raise ValueError("Question context must include question_text and explanation")
        return v

class AskAIResponse(BaseModel):
    """
    Schema for the AI explanation response.
    """
    response: str = Field(..., min_length=1, max_length=2000, strip_whitespace=True)