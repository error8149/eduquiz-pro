import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(tags=["History"])
logger = logging.getLogger("quiz_app.routers.history")

@router.get("/history", response_model=List[schemas.Quiz])
def read_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    mode: str = Query(None, description="Filter by quiz mode (ai or manual)"),
    date: str = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of past quiz sessions from the database, with optional filtering by mode and date.
    """
    logger.info(f"Fetching quiz history with skip={skip}, limit={limit}, mode={mode}, date={date}")
    try:
        query = db.query(crud.models.Quiz).order_by(crud.models.Quiz.timestamp.desc())
        if mode and mode in ["ai", "manual"]:
            query = query.filter(crud.models.Quiz.mode == mode)
        if date:
            try:
                query = query.filter(crud.models.Quiz.timestamp >= datetime.strptime(date, "%Y-%m-%d"))
                query = query.filter(crud.models.Quiz.timestamp < datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        quizzes = query.offset(skip).limit(limit).all()
        return quizzes
    except Exception as e:
        logger.error(f"Error fetching quiz history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not fetch quiz history: {str(e)}")