# ============================================================
# mcq.py — Multiple Choice Grader (improved)
# ============================================================

from sentence_transformers import SentenceTransformer, util

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def grade_mcq(student_answer: str, options: dict, correct_key: str) -> dict:

    student_clean = student_answer.strip().lower()
    correct_key   = correct_key.strip().upper()
    correct_text  = options.get(correct_key, "").lower()

    def make_result(chosen_key: str) -> dict:
        if chosen_key == correct_key:
            return {
                "grade"    : "Correct",
                "score"    : 1,
                "max_score": 1,
                "feedback" : f"Correct! ✅ The answer is {correct_key}: {options[correct_key]}"
            }
        else:
            return {
                "grade"    : "Incorrect",
                "score"    : 0,
                "max_score": 1,
                "feedback" : f"Incorrect. ❌ You chose {chosen_key}: {options.get(chosen_key, '?')}, but the correct answer is {correct_key}: {options[correct_key]}"
            }

    # ── Strategy 1: did they say the letter explicitly? ──────
    # e.g. "A", "option A", "letter A", "I think A"
    for key in options:
        patterns = [
            f" {key.lower()} ",
            f"option {key.lower()}",
            f"letter {key.lower()}",
            f"answer {key.lower()}",
            f"choose {key.lower()}",
            f"pick {key.lower()}",
        ]
        # also check if it starts or ends with the letter
        if (student_clean.startswith(key.lower()) or
            student_clean.endswith(key.lower()) or
            any(p in f" {student_clean} " for p in patterns)):
            return make_result(key)

    # ── Strategy 2: did they say the exact answer text? ──────
    for key, text in options.items():
        if text.strip().lower() in student_clean:
            return make_result(key)

    # ── Strategy 3: SBERT semantic match against all options ─
    best_key, best_score = None, -1

    for key, text in options.items():
        student_emb = sbert_model.encode(student_answer, convert_to_tensor=True)
        opt_emb     = sbert_model.encode(text, convert_to_tensor=True)
        score       = float(util.cos_sim(student_emb, opt_emb)[0][0])
        if score > best_score:
            best_score = score
            best_key   = key

    # ── Only use SBERT result if confidence is reasonable ────
    if best_score >= 0.4 and best_key:
        return make_result(best_key)

    # ── Fallback: unclear answer ──────────────────────────────
    return {
        "grade"    : "Unclear",
        "score"    : 0,
        "max_score": 1,
        "feedback" : f"⚠️ I couldn't clearly match your answer to one of the options. The correct answer was {correct_key}: {options[correct_key]}"
    }