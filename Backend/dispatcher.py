# ============================================================
# dispatcher.py — Universal Grading Router
# Ported from Block 12 (Colab)
# ============================================================

from Grader.short_answer import grade_short_answer
from Grader.mcq          import grade_mcq
from Grader.true_false   import grade_true_false
from Grader.fill_blank   import grade_fill_blank
from Grader.numeric      import grade_numeric


def grade(question_type: str, transcribed_text: str, correct_answer, **kwargs) -> dict:

    q_type = question_type.strip().lower().replace(" ", "_")

    # ── Base result shell ────────────────────────────────────
    result = {
        "question_type"   : q_type,
        "transcribed_text": transcribed_text,
        "grade"           : None,
        "score"           : 0,
        "max_score"       : 1,
        "feedback"        : None,
        "error"           : None
    }

    # ── Guard: empty transcription ───────────────────────────
    if not transcribed_text or not transcribed_text.strip():
        result["grade"]    = "Incorrect"
        result["score"]    = 0
        result["feedback"] = "⚠️ No speech detected. Please speak clearly and try again."
        return result

    # ── Guard: unsupported question type ─────────────────────
    SUPPORTED_TYPES = [
        "short_answer", "mcq", "true_false", "fill_blank", "numeric"
    ]

    if q_type not in SUPPORTED_TYPES:
        result["grade"]    = "Error"
        result["feedback"] = f"⚠️ Unknown question type: '{q_type}'."
        result["error"]    = "unsupported_question_type"
        return result

    # ── Route to correct grader ──────────────────────────────
    try:

        if q_type == "short_answer":
            question_text = kwargs.get("question_text", "")
            raw = grade_short_answer(transcribed_text, correct_answer, question_text)
            result["max_score"] = 2

        elif q_type == "mcq":
            options     = kwargs.get("options", {})
            correct_key = kwargs.get("correct_key", "")

            # ── If correct_key is answer text not a letter,
            #    find the matching key from options ──────────
            if correct_key and correct_key.upper() not in ["A", "B", "C", "D"]:
                for k, v in options.items():
                    if v.strip().lower() == correct_key.strip().lower():
                        correct_key = k
                        break

            raw = grade_mcq(transcribed_text, options, correct_key)

        elif q_type == "true_false":
            raw = grade_true_false(transcribed_text, correct_answer)

        elif q_type == "fill_blank":
            raw = grade_fill_blank(transcribed_text, correct_answer)

        elif q_type == "numeric":
            tolerance = kwargs.get("tolerance", 0)
            raw = grade_numeric(transcribed_text, correct_answer, tolerance)

        # ── Merge grader output into result shell ────────────
        result["grade"]    = raw.get("grade",    "Unknown")
        result["score"]    = raw.get("score",    0)
        result["feedback"] = raw.get("feedback", "No feedback returned.")

    except Exception as e:
        result["grade"]    = "Error"
        result["score"]    = 0
        result["feedback"] = "⚠️ Grader crashed. Please check your input."
        result["error"]    = str(e)

    return result