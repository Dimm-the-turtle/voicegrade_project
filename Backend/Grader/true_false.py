# ============================================================
# true_false.py — True/False Grader
# Ported from Block 9 (Colab)
# ============================================================

def grade_true_false(student_answer: str, correct_answer: str) -> dict:

    student_clean = student_answer.strip().lower()
    correct_clean = correct_answer.strip().lower()

    # ── Detect what the student said ────────────────────────
    if "true" in student_clean:
        student_choice = "true"
    elif "false" in student_clean:
        student_choice = "false"
    else:
        return {
            "grade"    : "Unclear",
            "score"    : 0,
            "max_score": 1,
            "feedback" : "⚠️ I couldn't detect 'True' or 'False' in your answer. Please say one clearly."
        }

    # ── Compare to correct answer ────────────────────────────
    if student_choice == correct_clean:
        return {
            "grade"    : "Correct",
            "score"    : 1,
            "max_score": 1,
            "feedback" : f"Correct! ✅ The answer is {correct_answer}."
        }
    else:
        return {
            "grade"    : "Incorrect",
            "score"    : 0,
            "max_score": 1,
            "feedback" : f"Incorrect. ❌ The correct answer is {correct_answer}."
        }