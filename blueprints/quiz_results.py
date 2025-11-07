from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from markupsafe import Markup
import json
from datetime import datetime

bp_quiz = Blueprint("quiz", __name__, url_prefix="/quiz")

# --- Helpers (replace with DB-backed versions) ---

def get_answer_key():
    """
    Return a dict keyed by question number with correct answer(s).
    For multi-select use a list of indices as strings.
    Example: { 1: "2", 2: ["0","3"], ... }
    """
    return {
        1: "2",
        2: "0",
        3: "1",
        4: "1",
    }

# def evaluateResults(responses: dict, questions: list):
#     """
#     responses: { q_numb: "k" or ["k1","k2"] }
#     questions: list of tuples (uuid, q_numb, image, title, note, isMultiple, options)
#     Returns a summary dict with total, correct, score and breakdown.
#     """
#     key = get_answer_key()
#     breakdown = []
#     correct_count = 0

#     for q in questions:
#         uuid, qn, image, title, note, isMultiple, options = q
#         user = responses.get(str(qn)) or responses.get(qn)
#         target = key.get(qn)

#         is_correct = False
#         if isinstance(target, list):
#             # multi-select: compare sets of strings
#             su = set(map(str, user or []))
#             st = set(map(str, target))
#             is_correct = su == st
#         else:
#             # single: compare stringified index
#             is_correct = (str(user) == str(target))

#         if is_correct:
#             correct_count += 1

#         breakdown.append({
#             "q_numb": qn,
#             "title": title,
#             "image": image,
#             "user": user,
#             "correct": target,
#             "is_correct": is_correct,
#             "options": options,
#             "isMultiple": isMultiple,
#         })

#     total = len(questions)
#     score = correct_count  # replace with your scoring system
#     return {
#         "total": total,
#         "correct": correct_count,
#         "score": score,
#         "breakdown": breakdown,
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#     }


@bp_quiz.route("/results", methods=["GET"])
def results():
    questions = session.get("quiz_questions") or []
    answers = session.get("quiz_answers") or {}
    summary = evaluateResults(answers, questions)

    with open("templates/content/quiz_results.html", "r", encoding="utf-8") as f:
        main_content_html = Markup(f.read())

    return render_template("index.html",
                           main_content=main_content_html,
                           results_payload=summary,
                           is_quiz_results=True)



# ------------------- DATA -------------------
def getPointsPerQuestions(ano: int = 5):
    # uuid, q_numb, image, title, note, isMultipleChoice, list_of_answers
    list_of_questions = [
        (
            "bd415bce-6028-4a73-9273-295310b3f3b6",
            1,
            ["0", "-2", "5", "-2", "-2"],
        ),
        (
            "a28eac48-a6e9-4b26-9840-08805e2a7a2d",
            2,
            ["0", "5", "-2", "-2", "-2"],
        ),
        (
            "31019225-8336-45d4-825b-3cefd953984c",
            3,
            ["0", "-2", "-2", "-2","5"],
        ),
        (
            "c2fbaf7e-b689-44e6-b0e1-a76246019222",
            4,
            ["0","-3","5"]
        ),
        (
            "4d72c744-2b85-4bc6-848c-9f60de652595",
            5,
            ['0','-1','5','-1','-1']
        )

        
    ]

    return list_of_questions

def evaluateResults(responses: dict, questions: list):
    # responses: { q_numb: "k" or ["k1","k2"] }
    # “skip” rule: single-choice "0" (Não sei) or empty/no answer is a skip;
    # multi-choice: ["0"] or empty/no answer is a skip.
    key = get_answer_key()

    total = len(questions)
    correct = 0
    wrong = 0
    skip = 0

    for q in questions:
        _, qn, _, _, _, isMultiple, _ = q
        user = responses.get(str(qn)) or responses.get(qn)
        target = key.get(qn)

        # Normalize user to list of strings for uniform checks
        if isMultiple:
            u = list(map(str, user or []))
            if not u or u == ["0"]:
                skip += 1
                continue
            # correct if sets match exactly
            ok = set(u) == set(map(str, target if isinstance(target, list) else [target]))
        else:
            u = None if user is None else str(user)
            if u in (None, "", "0"):
                skip += 1
                continue
            ok = (u == str(target))

        if ok:
            correct += 1
        else:
            wrong += 1

    return {"total": total, "correct": correct, "wrong": wrong, "skip": skip}
