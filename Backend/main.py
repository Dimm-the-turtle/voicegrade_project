# ============================================================
# main.py — VoiceGrade FastAPI Backend
# ============================================================
# Run with: uvicorn main:app --port 8000 --no-access-log
# ============================================================

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from dispatcher        import grade
from transcriber       import transcribe_audio
from document_analyser import analyse_document

app = FastAPI(title="VoiceGrade API", version="1.0.0")

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory question bank ───────────────────────────────────
question_bank = []


# ============================================================
# REQUEST MODELS
# ============================================================

class GradeRequest(BaseModel):
    question_type   : str
    transcribed_text: str
    correct_answer  : str
    kwargs          : Optional[dict] = {}


class Question(BaseModel):
    question_text : str
    question_type : str
    correct_answer: Optional[str] = None
    kwargs        : Optional[dict] = {}


# ============================================================
# ENDPOINTS
# ============================================================

# ── Health check ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "VoiceGrade backend is running ✅"}


# ── Transcribe audio ─────────────────────────────────────────
@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Receives an audio file from the browser mic,
    runs Whisper, returns the transcript.
    """
    try:
        audio_bytes = await file.read()
        extension   = file.filename.split(".")[-1] if file.filename else "webm"
        result      = transcribe_audio(audio_bytes, extension)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Grade an answer ───────────────────────────────────────────
@app.post("/api/grade")
def grade_answer(req: GradeRequest):
    """
    Receives a transcribed answer + question details,
    routes through the Dispatcher, returns grade + feedback.
    """
    try:
        result = grade(
            question_type   = req.question_type,
            transcribed_text= req.transcribed_text,
            correct_answer  = req.correct_answer,
            **(req.kwargs or {})
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Question bank — save ──────────────────────────────────────
@app.post("/api/questions")
def save_questions(questions: list[dict]):
    """
    Receives the full question bank from the Dashboard
    and stores it in memory.
    """
    global question_bank
    question_bank = []
    for q in questions:
        question_bank.append({
            "question_text" : q.get("question_text", ""),
            "question_type" : q.get("question_type", "short_answer"),
            "correct_answer": q.get("correct_answer", "") or "",
            "kwargs"        : q.get("kwargs", {}) or {},
        })
    return {"saved": len(question_bank), "status": "ok"}


# ── Question bank — load ──────────────────────────────────────
@app.get("/api/questions")
def get_questions():
    """
    Returns the current question bank to the Quiz page.
    """
    return {"questions": question_bank}


# ── Analyse uploaded document ─────────────────────────────────
@app.post("/api/analyse-document")
async def analyse_doc(file: UploadFile = File(...)):
    """
    Receives a PDF or TXT file, runs Claude analysis,
    returns detected questions.
    """
    try:
        file_bytes = await file.read()
        questions  = analyse_document(file_bytes, file.filename)
        return {"questions": questions, "count": len(questions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))