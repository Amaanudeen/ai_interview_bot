from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
import google.generativeai as genai
import tempfile
import json
from datetime import datetime

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

# Initialize models
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# Lazy load whisper model
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        import whisper
        whisper_model = whisper.load_model("small")
    return whisper_model

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

class SessionStatus(BaseModel):
    session_id: str
    mode: str
    question_count: int
    total_exchanges: int
    current_question: str
    interview_active: bool


# API Endpoints

@app.get("/")
def root():
    return {
        "message": "AI Interview Bot API",
        "version": "1.0.0",
        "endpoints": {
            "start_interview": "/api/interview/start",
            "submit_answer": "/api/interview/answer",
            "transcribe_audio": "/api/interview/transcribe",
            "get_status": "/api/interview/status/{session_id}",
            "end_interview": "/api/interview/end/{session_id}"
        }
    }

@app.post("/api/interview/start", response_model=StartInterviewResponse)
def start_interview(request: StartInterviewRequest):
    """Start a new interview session"""
    try:
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        # Generate first question
        first_question = "Tell me about yourself"
        
        # Initialize session
        sessions[session_id] = {
            "mode": request.mode,
            "content": request.content,
            "conversation_history": [],
            "question_count": 0,
            "current_question": first_question,
            "interview_active": True
        }
        
        return StartInterviewResponse(
            session_id=session_id,
            first_question=first_question,
            message="Interview started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/answer", response_model=SubmitAnswerResponse)
def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer and get feedback + next question"""
    try:
        session = sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session["interview_active"]:
            raise HTTPException(status_code=400, detail="Interview already ended")
        
        current_question = session["current_question"]
        answer = request.answer
        
        # Evaluate answer
        evaluation = evaluate_answer(current_question, answer, session["content"])
        
        # Store in history
        session["conversation_history"].append({
            "question": current_question,
            "answer": answer,
            "feedback": evaluation["feedback"],
            "score": evaluation["score"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if interview should continue
        session["question_count"] += 1
        max_questions = 10
        
        if session["question_count"] >= max_questions:
            # End interview
            final_feedback = generate_final_feedback(session["conversation_history"])
            session["interview_active"] = False
            
            return SubmitAnswerResponse(
                feedback=evaluation["feedback"],
                next_question=None,
                is_followup=False,
                interview_complete=True,
                final_feedback=final_feedback
            )
        
        # Generate next question or followup
        is_followup = evaluation.get("needs_followup", False)
        
        if is_followup:
            next_question = generate_followup(current_question, answer, evaluation)
        else:
            next_question = generate_next_question(session)
        
        session["current_question"] = next_question
        
        return SubmitAnswerResponse(
            feedback=evaluation["feedback"],
            next_question=next_question,
            is_followup=is_followup,
            interview_complete=False,
            final_feedback=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio file to text"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Transcribe
        model = get_whisper_model()
        result = model.transcribe(temp_path, fp16=False)
        transcribed_text = result["text"].strip()
        
        # Cleanup
        os.remove(temp_path)
        
        return {"transcription": transcribed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/api/interview/status/{session_id}", response_model=SessionStatus)
def get_session_status(session_id: str):
    """Get current interview session status"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStatus(
        session_id=session_id,
        mode=session["mode"],
        question_count=session["question_count"],
        total_exchanges=len(session["conversation_history"]),
        current_question=session["current_question"],
        interview_active=session["interview_active"]
    )

@app.delete("/api/interview/end/{session_id}")
def end_interview(session_id: str):
    """End interview and get final feedback"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    final_feedback = generate_final_feedback(session["conversation_history"])
    session["interview_active"] = False
    
    return {
        "message": "Interview ended",
        "final_feedback": final_feedback,
        "total_questions": session["question_count"]
    }


# Helper Functions

def evaluate_answer(question: str, answer: str, context: str) -> Dict:
    """Evaluate answer using Gemini"""
    prompt = f"""Evaluate this interview answer and return JSON:

Question: {question}
Answer: {answer}
Context: {context}

Return JSON format:
{{
    "feedback": "detailed feedback",
    "is_correct": true/false,
    "needs_followup": true/false,
    "score": 0.0-1.0,
    "strengths": ["strength1"],
    "weaknesses": ["weakness1"]
}}"""
    
    response = gemini_model.generate_content(prompt)
    response_text = response.text.strip()
    
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    
    return json.loads(response_text)

def generate_next_question(session: Dict) -> str:
    """Generate next interview question"""
    mode = session["mode"]
    content = session["content"]
    history = session["conversation_history"]
    
    history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:]])
    
    prompt = f"""Generate a technical interview question for {mode}: {content}

Previous questions:
{history_text}

Return ONLY the question text."""
    
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def generate_followup(question: str, answer: str, evaluation: Dict) -> str:
    """Generate follow-up question"""
    prompt = f"""Generate a follow-up question based on:

Original: {question}
Answer: {answer}
Issues: {', '.join(evaluation.get('weaknesses', []))}

Return ONLY the follow-up question."""
    
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def generate_final_feedback(history: List[Dict]) -> str:
    """Generate consolidated feedback"""
    summary = "\n".join([
        f"Q: {h['question']}\nA: {h['answer']}\nScore: {h['score']}"
        for h in history
    ])
    
    prompt = f"""Provide final interview feedback:

{summary}

Include: overall performance, strengths, improvements, recommendations."""
    
    response = gemini_model.generate_content(prompt)
    return response.text.strip()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
