"""
This module handles the logic for an authenticated user to claim a quiz
that they completed anonymously.
"""
import os
import json
import csv
from DBhelpers import getQuestionFromQid, save_quiz_history
from Funhelpers.quiz_storage import get_quiz_result
from Funhelpers.quiz_helpers import calculate_score

def claim_anonymous_quiz(email, quiz_uuid, quiz_config, question_ids_raw, user_answers):
    """
    Associates an anonymous quiz with a user's account.

    1. Uses quiz data from session to rebuild the result.
    2. Saves this quiz data to the user's permanent history in the database.
    3. Deletes the claimed quiz from the CSV file.

    Args:
        email (str): The email of the user claiming the quiz.
        quiz_uuid (str): The UUID of the anonymous quiz.
        quiz_config (dict): The configuration of the quiz (year, num_exercises, etc.)
        question_ids_raw (list): The list of question IDs (raw from session, e.g., [(id,)])
        user_answers (dict): The user's answers for the quiz.

    Returns:
        bool: True if the quiz was successfully claimed, False otherwise.
    """
    # 1. Prepare data for saving to DB
    # Convert question_ids from list of tuples to list of ints
    qids_flat = [q[0] for q in question_ids_raw]

    raw_questions = []
    for qid in qids_flat:
        q_row = getQuestionFromQid(qid)
        if q_row:
            raw_questions.append(dict(q_row))
            
    if not raw_questions:
        return False

    # Re-create answers in the format calculate_score expects ({index: [options]})
    answers_by_index = {}
    for idx, q in enumerate(raw_questions):
        # The key in user_answers is the question's index in the quiz flow
        # Ensure it's correct for calculate_score
        if str(idx) in user_answers:
            answers_by_index[str(idx)] = user_answers[str(idx)]

    # 2. Recalculate the score.
    quiz_results = calculate_score(raw_questions, answers_by_index)

    # Get the original timestamp from the anonymous quiz CSV
    anonymous_quiz_data = get_quiz_result(quiz_uuid)
    start_ts = None
    if anonymous_quiz_data and 'timestamp' in anonymous_quiz_data:
        start_ts = anonymous_quiz_data['timestamp']

    # 3. Save to user's permanent history in the database.
    print(f"DEBUG: Attempting to save quiz {quiz_uuid} for {email}...")
    was_saved_status = save_quiz_history(
        email=email,
        results=quiz_results,
        quiz_config=quiz_config,
        q_uuid=quiz_uuid,
        start_ts=start_ts # Pass the original timestamp
    )
    print(f"DEBUG: save_quiz_history returned: {was_saved_status}")

    if "ERROR" in was_saved_status:
        print(f"DEBUG: Error saving quiz {quiz_uuid}: {was_saved_status}")
        return False

    # DEBUG: Attempt to retrieve the quiz immediately after saving
    from DBhelpers import get_quiz_history_by_uuid
    retrieved_quiz = get_quiz_history_by_uuid(email, quiz_uuid)
    print(f"DEBUG: Immediately retrieved quiz from DB: {retrieved_quiz}")

    # 4. Delete the claimed quiz from the CSV file.
    QUIZ_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz_results')
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        return True # Nothing to delete if file doesn't exist

    rows_to_keep = []
    deleted = False
    
    with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames: # Handle empty file case
            return True
        
        header = reader.fieldnames
        for row in reader:
            if row.get('quiz_uuid') == quiz_uuid:
                deleted = True
            else:
                rows_to_keep.append(row)

    if deleted:
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows_to_keep)

    return True