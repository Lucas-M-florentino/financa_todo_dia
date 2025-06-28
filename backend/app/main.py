from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.api import routes, chat


load_dotenv()

app = FastAPI(title="FastAPI Backend",swagger_ui_parameters={"syntaxHighlighting": {"theme": "obsidian"}})

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router, prefix="/api", tags=["items"])
app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "FastAPI Backend Running"}
