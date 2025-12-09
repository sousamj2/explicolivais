"""
Quiz results storage - Anonymous only
- Authenticated users' history is saved to the main database.
- Stores anonymous quiz results temporarily
- 1-hour expiration checked lazily on /quiz access
- No TTL field needed, just check timestamp age
- Registered users store results in their own area (database)
"""

import csv
import json
import os
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

from DBhelpers import save_quiz_history

QUIZ_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz_results')
Path(QUIZ_RESULTS_DIR).mkdir(exist_ok=True)

def save_quiz_result(user_answers, questions):
    """
    Save anonymous quiz results to CSV
    Registered users save to their own area instead
    
    Args:
        user_answers: dict of answers by index
        questions: list of question objects
    
    Returns:
        quiz_uuid: unique identifier for this quiz (valid 1 hour)
    
    CSV Format (compact and anonymous):
    quiz_uuid,timestamp,answers
    a1b2c3d4-...,2025-11-03 20:00:00,"{1: , 2: , ...}"
    """
    quiz_uuid = str(uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert index-based answers to question_number-based
    answers_by_question_number = {}
    questions = [x[0] for x in questions]

    if questions:
        for idx,q_num in enumerate(questions):            
            try:
                answers_by_question_number[str(q_num)] = user_answers[str(idx)]
            except Exception as e:
                print(e)
                answers_by_question_number[str(q_num)] = "0"
    else:
        answers_by_question_number = user_answers
    
    answers_json = json.dumps(answers_by_question_number)
    
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    file_exists = os.path.exists(csv_filepath)
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header only if file is new
        if not file_exists:
            writer.writerow(['quiz_uuid', 'timestamp', 'answers'])
        
        # Write quiz result (anonymous, no email)
        writer.writerow([quiz_uuid, timestamp, answers_json])
    
    # print(f"DEBUG: Saved anonymous quiz result")
    # print(f"  UUID: {quiz_uuid}")
    # print(f"  Timestamp: {timestamp}")
    
    return quiz_uuid

def save_quiz_history_for_user(email, quiz_results, quiz_config):
    """
    Saves a completed quiz's results to the database for an authenticated user.

    Args:
        email (str): The user's email address.
        quiz_results (dict): The dictionary of results from calculate_score.
        quiz_config (dict): The quiz configuration dictionary from the session.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    if not email or not isinstance(quiz_results, dict):
        return False

    quiz_uuid = str(uuid4())

    try:
        save_quiz_history(
            email=email,
            results=quiz_results,
            quiz_config=quiz_config,
        )
        return True
    except Exception as e:
        print(f"ERROR: Could not save quiz history for {email}: {e}")
        return False

def cleanup_expired_results():
    """
    Remove quiz results older than 1 hour
    Called at start of /quiz (lazy cleanup)
    
    Returns:
        Number of rows deleted
    """
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        return 0
    
    current_time = datetime.now()
    one_hour_ago = current_time - timedelta(hours=1)
    rows_to_keep = []
    rows_deleted = 0
    
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return 0
        
        header = reader.fieldnames
        
        for row in reader:
            try:
                row_time = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                
                # Keep if less than 1 hour old
                if row_time > one_hour_ago:
                    rows_to_keep.append(row)
                else:
                    rows_deleted += 1
                    # print(f"DEBUG: Deleted expired quiz {row['quiz_uuid']}")
            except ValueError:
                # Keep rows with invalid timestamp (safety)
                rows_to_keep.append(row)
    
    # Write back only valid rows
    if rows_deleted > 0:
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows_to_keep)
        
        # print(f"DEBUG: Cleanup removed {rows_deleted} expired quiz results")
    
    return rows_deleted

def get_quiz_result(quiz_uuid):
    """
    Retrieve anonymous quiz result by UUID
    
    Args:
        quiz_uuid: unique identifier for the quiz
    
    Returns:
        dict with quiz data, or None if not found/expired
    """
    # First cleanup expired results
    cleanup_expired_results()
    
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        return None
    
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['quiz_uuid'] == quiz_uuid:
                answers_by_question_number = json.loads(row.get('answers', '{}'))
                
                result = {
                    'quiz_uuid': row['quiz_uuid'],
                    'timestamp': row['timestamp'],
                    'answers_by_question_number': answers_by_question_number
                }
                
                # print(f"DEBUG: Retrieved quiz result: {quiz_uuid}")
                return result
    
    # print(f"DEBUG: Quiz UUID not found or expired: {quiz_uuid}")
    return None

def list_all_quiz_results():
    """
    List all valid (not expired) anonymous quiz results
    
    Returns:
        list of quiz summaries
    """
    # First cleanup expired results
    cleanup_expired_results()
    
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        return []
    
    results = []
    
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'quiz_uuid': row['quiz_uuid'],
                'timestamp': row['timestamp']
            })
    
    return results
