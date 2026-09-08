# ============================================================
# short_answer.py — Short Answer Grader
# ============================================================

from sentence_transformers import SentenceTransformer, util

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def grade_short_answer(student_answer: str, correct_answer: str, question_text: str = "") -> dict:

    student_emb = sbert_model.encode(student_answer, convert_to_tensor=True)
    correct_emb = sbert_model.encode(correct_answer, convert_to_tensor=True)
    similarity  = float(util.cos_sim(student_emb, correct_emb)[0][0])

    if similarity >= 0.85:
        grade    = "Full"
        score    = 2
        feedback = f"Spot on! 🌟 The answer is: {correct_answer}."
    elif similarity >= 0.60:
        grade    = "Partial"
        score    = 1
        feedback = f"Close! You are definitely headed in the right direction. 💡 The complete answer is:{correct_answer}."
    else:
        grade    = "Incorrect"
        score    = 0
        feedback = f"Not quite this time, but keep at it! 💪 The answer we were looking for is: {correct_answer}."

    return {
        "grade"     : grade,
        "score"     : score,
        "max_score" : 2,
        "similarity": round(similarity, 4),
        "feedback"  : feedback
    }