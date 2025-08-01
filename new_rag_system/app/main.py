from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file before other imports
load_dotenv()

from .database import create_db_and_tables
from .api import auth, documents, query, admin, notifications, categories, history, user
from .services.expiration import start_background_tasks

app = FastAPI(
    title="Advanced RAG System API",
    description="API for the Advanced RAG System",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    # Create the database and tables if they don't exist
    create_db_and_tables()
    # Start background services
    start_background_tasks()

# Include the API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(user.router, prefix="/user", tags=["User"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Advanced RAG System API"}
