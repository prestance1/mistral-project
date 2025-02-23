from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from econome.routers import api_router
from fastapi.responses import JSONResponse
from bson.errors import InvalidId
from pymongo.errors import ConnectionFailure, OperationFailure
from econome.exceptions import *
import logging

app = FastAPI()
app.include_router(api_router)

logging.basicConfig(level="DEBUG")
logger = logging.getLogger("econome")


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_exception_handler(
    request: Request, exc: DocumentNotFoundError
):
    message = "Resource not found"
    logger.error(message, dict(error=str(exc)))
    return JSONResponse(status_code=404, content={"detail": message})


@app.exception_handler(ConnectionFailure)
async def database_connection_failure_handler(request: Request, exc: ConnectionFailure):
    logger.error("Connection error", dict(error=str(exc)))
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection error. Please try again later."},
    )


@app.exception_handler(OperationFailure)
async def database_operation_handler(request: Request, exc: OperationFailure):
    logger.error("Operation error", dict(error=str(exc)))
    return JSONResponse(
        status_code=503, content={"detail": f"Database operation error: {str(exc)}"}
    )


@app.exception_handler(InvalidId)
async def database_invalid_id_handler(request: Request, exc: InvalidId):
    logger.error("Invalid Id passed", dict(error=str(exc)))
    return JSONResponse(
        status_code=503,
        content={"detail": "Invalid Id passed"},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
