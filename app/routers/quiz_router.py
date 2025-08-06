import asyncio
import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import api_utils, crud, schemas
from ..database import get_db

router = APIRouter(tags=["Quiz"])
logger = logging.getLogger(__name__)

@router.post("/quiz/start", response_model=List[schemas.QuestionCreate])
async def start_quiz(request: schemas.StartQuizRequest):
    grade_level = getattr(request, 'grade_level', 'high school')
    difficulty = getattr(request, 'difficulty', 'medium')
    
    logger.info(f"Received /quiz/start request: num_questions={request.num_questions}, provider={request.api_provider}, topics={len(request.topics)}, grade_level={grade_level}, difficulty={difficulty}")
    
    if not request.api_key or request.api_key == "null":
        logger.warning("API key is missing in start_quiz request.")
        raise HTTPException(status_code=401, detail=f"API key for {request.api_provider} is missing. Please set it in Settings.")

    # Validate topics
    if not request.topics or len(request.topics) == 0:
        logger.error("No topics provided in start_quiz request.")
        raise HTTPException(status_code=400, detail="No topics provided. Please add topics in Settings.")

    try:
        logger.info(f"Calling api_utils.get_questions with {len(request.topics)} topics")
        questions = await api_utils.get_questions(request)
        
        if not questions:
            logger.error("Question generation returned no valid questions.")
            raise HTTPException(status_code=503, detail="AI provider failed to generate any valid questions.")
        
        # Check if the first item is an error
        if questions and isinstance(questions[0], dict) and "error" in questions[0]:
            logger.error(f"Question generation returned error: {questions[0]['error']}")
            raise HTTPException(status_code=503, detail=questions[0]["error"])
        
        # Check if we got the exact number requested
        if len(questions) < request.num_questions:
            logger.warning(f"Only generated {len(questions)} out of {request.num_questions} requested questions.")
        
        # Validate each question to ensure JSON compatibility
        valid_questions = []
        for i, q in enumerate(questions):
            try:
                if not all(key in q for key in ["question_text", "options", "correct_answer", "explanation", "section", "topic"]):
                    logger.error(f"Invalid question structure at index {i}: {q}")
                    continue
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    logger.error(f"Invalid options in question at index {i}: {q['options']}")
                    continue
                if q["correct_answer"] not in q["options"]:
                    logger.error(f"Correct answer not in options at index {i}: {q['correct_answer']} not in {q['options']}")
                    continue
                valid_questions.append(q)
            except Exception as e:
                logger.error(f"Error validating question at index {i}: {str(e)}")
                continue

        if not valid_questions:
            logger.error("No valid questions after validation.")
            raise HTTPException(status_code=503, detail="No valid questions could be generated. Please try again.")

        logger.info(f"Successfully generated {len(valid_questions)} valid questions. Returning to the client.")
        response = valid_questions[:request.num_questions]
        logger.debug(f"Sending response with {len(response)} questions")
        return response
        
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        logger.error(f"Request to {request.api_provider} timed out.", exc_info=True)
        raise HTTPException(status_code=504, detail=f"Request to {request.api_provider} timed out.")
    except Exception as e:
        logger.error(f"Unexpected error in start_quiz: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.post("/quiz", response_model=schemas.Quiz)
async def save_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db)):
    logger.info(f"Received /quiz request to save quiz: score={quiz.score}, total_questions={quiz.total_questions}")
    try:
        db_quiz = crud.create_quiz(db, quiz)
        logger.info(f"Quiz saved successfully with ID {db_quiz.id}")
        return db_quiz
    except Exception as e:
        logger.error(f"Error saving quiz: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save quiz: {str(e)}")

@router.post("/quiz/generate-prompt", response_model=schemas.GeneratePromptResponse)
async def generate_prompt(request: schemas.GeneratePromptRequest):
    grade_level = getattr(request, 'grade_level', 'high school')
    difficulty = getattr(request, 'difficulty', 'medium')
    
    logger.info(f"Received /quiz/generate-prompt request for {request.num_questions} questions, grade_level={grade_level}, difficulty={difficulty}")
    try:
        prompt = api_utils.get_generation_prompt_for_manual_mode(
            request.num_questions, 
            request.topics,
            grade_level,
            difficulty
        )
        response = {"prompt": prompt}
        logger.debug(f"Sending prompt response: {json.dumps(response)[:500]}...")
        return response
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")

@router.post("/quiz/ask-ai", response_model=schemas.AskAIResponse)
async def ask_ai(request: schemas.AskAIRequest):
    logger.info("Received /quiz/ask-ai request.")
    if not request.api_key:
        logger.warning("API key is missing in ask_ai request.")
        raise HTTPException(status_code=401, detail="API key is required for this feature.")
    try:
        response = await api_utils.get_ai_explanation(request.question_context, request.user_query, request.api_key)
        logger.debug(f"Sending AI explanation response: {json.dumps({'response': response})[:500]}...")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in ask-ai endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get AI explanation: {str(e)}")

@router.post("/settings")
async def save_settings(settings: dict, db: Session = Depends(get_db)):
    logger.info("Received /settings request to save settings")
    try:
        logger.debug(f"Settings received: {json.dumps(settings, default=str)[:500]}...")
        return {"status": "Settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")