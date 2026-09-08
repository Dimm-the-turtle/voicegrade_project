# ============================================================
# fill_blank.py — Fill in the Blank Grader
# Ported from Block 10 (Colab)
# ============================================================

from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def grade_fill_blank(student_answer: str, correct_answer: str) -> dict:

    student_clean = student_answer.strip().lower()
    correct_clean = correct_answer.strip().lower()

    # ── Strategy 1: exact match ──────────────────────────────
    if correct_clean in student_clean:
        return {
            "grade"    : "Correct",
            "score"    : 1,
            "max_score": 1,
            "feedback" : f"Correct! ✅ '{correct_answer}' is the right answer."
        }

    # ── Strategy 2: fuzzy match ──────────────────────────────
    fuzzy_score = fuzz.partial_ratio(correct_clean, student_clean)

    if fuzzy_score >= 85:
        return {
            "grade"    : "Correct",
            "score"    : 1,
            "max_score": 1,
            "feedback" : f"Correct! ✅ Close enough to '{correct_answer}'. (Match: {fuzzy_score}%)"
        }

    # ── Strategy 3: SBERT semantic fallback ─────────────────
    student_emb = sbert_model.encode(student_answer, convert_to_tensor=True)
    correct_emb = sbert_model.encode(correct_answer, convert_to_tensor=True)
    similarity  = float(util.cos_sim(student_emb, correct_emb)[0][0])

    if similarity >= 0.80:
        return {
            "grade"    : "Correct",
            "score"    : 1,
            "max_score": 1,
            "feedback" : f"Correct! ✅ Your answer is semantically close to '{correct_answer}'. (Similarity: {similarity:.2f})"
        }

    return {
        "grade"    : "Incorrect",
        "score"    : 0,
        "max_score": 1,
        "feedback" : f"Incorrect. ❌ The correct answer is '{correct_answer}'."
    }