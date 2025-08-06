# Make routers a package and export APIRouter instances
from .error_router import router as error_router
from .history import router as history
from .quiz_router import router as quiz_router