# ============================================================
# numeric.py — Numeric Answer Grader
# Ported from Block 11 (Colab) — includes the name fix
# ============================================================

import re
from word2number import w2n


def extract_number(text: str):
    """
    Three-strategy number extractor.
    Always returns the FIRST number found to avoid double-counting
    when students repeat their answer.
    """
    text = text.strip().lower()

    # ── Pre-process: strip filler phrases ───────────────────
    fillers = [
        "the answer is", "i think it is", "i think it's",
        "it is", "it's", "i believe it is", "i believe it's",
        "my answer is", "approximately", "about", "around",
        "i would say", "i'd say", "the result is",
    ]
    for filler in fillers:
        text = text.replace(filler, " ")

    # ── Strip repeated sentences — take only first clause ───
    # e.g. "Six. The answer is six." → "Six."
    sentences = [s.strip() for s in text.replace(".", "|").split("|") if s.strip()]
    text = sentences[0] if sentences else text

    text = text.replace(".", " ").replace(",", " ").strip()

    # ── Strategy 1: direct digit ─────────────────────────────
    digit_match = re.search(r'-?\d+\.?\d*', text)
    if digit_match:
        return float(digit_match.group())

    # ── Strategy 2: word2number ──────────────────────────────
    try:
        return float(w2n.word_to_num(text))
    except ValueError:
        pass

    # ── Strategy 3: pick first recognisable number word ─────
    for word in text.split():
        try:
            return float(w2n.word_to_num(word))
        except ValueError:
            pass

    return None

def grade_numeric(student_answer: str, correct_answer: float, tolerance: float = 0) -> dict:

    correct_num = float(correct_answer)
    extracted   = extract_number(student_answer)

    if extracted is None:
        return {
            "grade"            : "Unclear",
            "score"            : 0,
            "max_score"        : 1,
            "extracted_number" : None,
            "difference"       : None,
            "feedback"         : "⚠️ I couldn't detect a number in your answer. Please say a number clearly, e.g. 'one hundred' or '100'."
        }

    difference = abs(extracted - correct_num)
    is_correct = difference <= tolerance

    if is_correct:
        if difference == 0:
            feedback = f"Perfect! ✅ {extracted} is exactly right! 🌟"
        else:
            feedback = f"Correct! ✅ {extracted} is within the accepted range. (Exact: {correct_num}, tolerance: ±{tolerance})"
    else:
        feedback = f"Not quite. ❌ You said {extracted}, but the correct answer is {correct_num}. You were off by {difference:.1f}."

    return {
        "grade"            : "Correct" if is_correct else "Incorrect",
        "score"            : 1 if is_correct else 0,
        "max_score"        : 1,
        "extracted_number" : extracted,
        "difference"       : round(difference, 4),
        "feedback"         : feedback
    }