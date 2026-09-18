"""Expense Tracker API - application entrypoint.

Run locally with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, expenses, users

app = FastAPI(
    title="Expense Tracker API",
    description=(
        "A RESTful API for tracking personal expenses, with JWT authentication "
        "and per-user data isolation."
    ),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(users.router)


@app.get("/", tags=["Health"], summary="Health check")
def read_root():
    return {"status": "ok"}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Error handling: keep responses clean and never leak internals.
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces or internal details to the client.
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
