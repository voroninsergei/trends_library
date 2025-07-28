# flake8: noqa
"""Main FastAPI application for the Trends Library project.

This module defines the API endpoints used to trigger the collection of trends and generation of articles and images. It also exposes a health check endpoint.

Endpoints:
- GET /health: Returns status of the service.
- POST /generate: Accepts a GenerationRequest and returns a Celery task ID.
- GET /tasks/{task_id}: Returns the status and result of a Celery task.

The application uses Celery for asynchronous task processing. To configure the message broker and result backend, set the environment variables
`CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in your environment or `.env` file.
"""

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from celery import Celery
import os

# Initialize FastAPI application
app = FastAPI(
    title="Trends Library API",
    description=(
        "API for retrieving trending topics, generating articles and images, "
        "and publishing content to the CMS."
    ),
    version="0.1.0",  # noqa: E501
)  # noqa: E501
  # noqa: E501
# Configure Celery application
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
celery_app = Celery("trends_tasks", broker=BROKER_URL, backend=RESULT_BACKEND)


class GenerationRequest(BaseModel):
    """Pydantic model representing a request to generate a trend article and image."""

    country: str
    category: str
    title: str
    period: Optional[str] = None


@app.get("/health", summary="Health check", tags=["Health"])
async def health() -> dict[str, str]:
    """Simple endpoint to verify that the service is running."""

    return {"status": "ok"}


@app.post("/generate", summary="Enqueue content generation", tags=["Generation"])
async def generate(req: GenerationRequest) -> dict[str, str]:
    """Enqueue a Celery task to generate an article and image.

    Args:
        req: Parameters for the content generation including country, category, title, and optional period.

    Returns:
        A dictionary containing the Celery task identifier.
    """

    # Send a task to the Celery worker. The task name should correspond to the task function registered in celery_app.py.
    task = celery_app.send_task("tasks.generate_content_task", args=[req.dict()])
    return {"task_id": task.id}


@app.get("/tasks/{task_id}", summary="Get task status", response_model=dict, tags=["Tasks"])
async def get_task_status(task_id: str) -> dict:
    """Retrieve the status and result of a Celery task by ID.

    Args:
        task_id: Identifier of the Celery task.

    Returns:
        A dictionary with the state and, if complete, the result of the task.
    """

    result = celery_app.AsyncResult(task_id)
    state = result.state
    # Depending on the state, return appropriate information
    if state == "PENDING":
        return {"state": state}
    elif state == "FAILURE":
        # If the task failed, include the error message
        return {"state": state, "error": str(result.result)}
    elif state == "SUCCESS":
        return {"state": state, "result": result.result}
    else:
        # For other states (RETRY, STARTED, etc.), return the state and meta
        return {"state": state, "info": str(result.result)}
