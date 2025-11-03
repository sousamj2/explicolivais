"""
Quiz results storage and retrieval system
Saves quiz results to CSV using question_number as key
Compact format ready for database migration
"""

import csv
import json
import os
from datetime import datetime
from uuid import uuid4
from pathlib import Path

# Directory to store quiz results
QUIZ_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz_results')

# Create directory if it doesn't exist
Path(QUIZ_RESULTS_DIR).mkdir(exist_ok=True)

def save_quiz_result(user_answers, questions=None, user_id=None):
    """
    Save quiz results to CSV file using question_number as key
    
    Args:
        user_answers: dict like {'0': ['1'], '1': ['2'], ...} (index-based from session)
        questions: list of question objects (needed to map index to question_number)
        user_id: optional user identifier
    
    Returns:
        quiz_uuid: unique identifier for this quiz attempt
    
    Data format (compact and database-ready):
    {
        "1": ["2"],      // question_number: 1, user answered index 2
        "2": ["1"],      // question_number: 2, user answered index 1
        "3": ["1", "2"]  // question_number: 3, user answered indices 1 and 2
    }
    """
    quiz_uuid = str(uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build answer map with question_number as key
    answers_by_question_number = {}
    
    if questions:
        for question_idx_str, answer_indices in user_answers.items():
            question_idx = int(question_idx_str)
            
            # Get the question_number at this index
            if question_idx < len(questions):
                question_number = questions[question_idx]['question_number']
                # Store using question_number as key
                answers_by_question_number[str(question_number)] = answer_indices
    else:
        # Fallback if no questions provided
        answers_by_question_number = user_answers
    
    # Convert to JSON string for storage (very compact!)
    answers_json = json.dumps(answers_by_question_number)
    
    # CSV file path
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    # Check if file exists to determine if we need to write header
    file_exists = os.path.exists(csv_filepath)
    
    # Write to CSV
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['quiz_uuid', 'timestamp', 'user_id', 'answers'])
        
        # Write data row
        writer.writerow([quiz_uuid, timestamp, user_id or 'anonymous', answers_json])
    
    print(f"DEBUG: Saved quiz results")
    print(f"  UUID: {quiz_uuid}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Compact answers (by question_number): {answers_json}")
    
    return quiz_uuid

def get_quiz_result(quiz_uuid):
    """
    Retrieve quiz results by UUID
    Returns answers keyed by question_number
    
    Args:
        quiz_uuid: unique identifier for the quiz attempt
    
    Returns:
        dict with quiz data, or None if not found
    """
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        print(f"DEBUG: Quiz results file not found: {csv_filepath}")
        return None
    
    # Read CSV and find matching UUID
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['quiz_uuid'] == quiz_uuid:
                # Parse the JSON answers (keyed by question_number)
                answers_by_question_number = json.loads(row.get('answers', '{}'))
                
                result = {
                    'quiz_uuid': row['quiz_uuid'],
                    'timestamp': row['timestamp'],
                    'user_id': row['user_id'],
                    'answers_by_question_number': answers_by_question_number
                }
                
                print(f"DEBUG: Retrieved quiz result for UUID: {quiz_uuid}")
                print(f"  Answers (by question_number): {answers_by_question_number}")
                
                return result
    
    print(f"DEBUG: Quiz UUID not found: {quiz_uuid}")
    return None

def list_all_quiz_results(user_id=None):
    """
    List all quiz results, optionally filtered by user_id
    
    Args:
        user_id: optional filter by user_id
    
    Returns:
        list of quiz result summaries
    """
    csv_filepath = os.path.join(QUIZ_RESULTS_DIR, 'quiz_results.csv')
    
    if not os.path.exists(csv_filepath):
        return []
    
    results = []
    
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if user_id is None or row['user_id'] == user_id:
                results.append({
                    'quiz_uuid': row['quiz_uuid'],
                    'timestamp': row['timestamp'],
                    'user_id': row['user_id']
                })
    
    return results
