import logging

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Error"])
logger = logging.getLogger(__name__)

@router.post("/log-error")
async def log_client_error(error_data: dict):
    """
    Log client-side errors sent from the frontend.
    """
    try:
        error_message = error_data.get("error", "Unknown error")
        stack = error_data.get("stack", "No stack trace")
        context = error_data.get("context", "Unknown context")
        response_text = error_data.get("responseText", "")
        logger.error(f"Client-side error [Context: {context}]: {error_message}\nStack: {stack}\nResponse: {response_text[:500]}")
        return {"status": "Error logged successfully"}
    except Exception as e:
        logger.error(f"Failed to log client error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"detail": f"Failed to log error: {str(e)}"})