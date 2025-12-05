from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

# Initialize FastAPI
app = FastAPI(title="AI Interview Bot API", version="1.0.0")

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# In-memory session storage (use Redis/DB in production)
sessions = {}

# Request/Response Models
class StartInterviewRequest(BaseModel):
    mode: str  # "role" or "resume"
    content: str  # job role or resume text
    session_id: Optional[str] = None

class StartInterviewResponse(BaseModel):
    session_id: str
    first_question: str
    message: str

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str

class SubmitAnswerResponse(BaseModel):
    feedback: str
    next_question: Optional[str]
    is_followup: bool
    interview_complete: bool
    final_feedback: Optional[str]
    score: Optional[float]

class SessionStatus(BaseModel):
    session_id: str
    mode: str
    question_count: int
    total_exchanges: int
    current_question: str
    interview_active: boo