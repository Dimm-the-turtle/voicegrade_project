# ============================================================
# document_analyser.py — Claude-powered Document Analysis
# Reads a PDF/TXT and auto-detects questions using Claude API
# ============================================================

import os
import fitz  # pymupdf
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from PDF, TXT or DOCX file bytes."""
    name = filename.lower()

    if name.endswith(".pdf"):
        doc  = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

    elif name.endswith(".docx"):
        import docx
        import io
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in document.paragraphs if para.text.strip())

    else:
        return file_bytes.decode("utf-8", errors="ignore")


def analyse_document(file_bytes: bytes, filename: str) -> list:
    """
    Sends document text to Claude and asks it to detect questions.
    Returns a list of question dicts ready for the question bank.
    """

    text = extract_text(file_bytes, filename)

    if not text.strip():
        return []

    prompt = f"""You are an expert exam question analyser.

Read the following document and extract all questions from it.
For each question, identify:
- The question text
- The question type (short_answer, mcq, true_false, fill_blank, or numeric)
- The correct answer
- For MCQ: the options as a dict like {{"A": "...", "B": "...", "C": "...", "D": "..."}} and the correct key
- For numeric: the tolerance (default 0)

Return ONLY a valid JSON array. No explanation, no markdown, no backticks.
Each item must have these exact keys:
  question_text, question_type, correct_answer, kwargs

kwargs should be:
- For mcq: {{"options": {{"A": "...", ...}}, "correct_key": "B"}}
- For numeric: {{"tolerance": 0}}
- For others: {{}}

Document:
\"\"\"
{text[:6000]}
\"\"\"

JSON array:"""

    message = client.messages.create(
        model      = "claude-opus-4-6",
        max_tokens = 2000,
        messages   = [{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    # ── Clean up any accidental markdown fences ──────────────
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    import json
    questions = json.loads(raw)
    return questions