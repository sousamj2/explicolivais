"""
Quiz functions using database-backed questions
Works with the new dictionary-based question structure
"""

from typing import Dict, List, Union
import json

def score_points_total(
    answers: Dict[Union[str, int], List],
    questions: List[Dict]
) -> Dict[str, object]:
    """
    Sum per-option points for selections.
    
    Args:
        answers: dict like {'0': ['1'], '1': ['2'], ...} (index-based)
        questions: list of question dicts from getListOfQuestions()
    
    Returns:
        dict with total_points and per_question_points
    """
    total_points = 0
    per_question = {}
    
    for i, question in enumerate(questions):
        question_idx = str(i)
        user_answer = answers.get(question_idx, [])
        
        # Get scoring for this question
        scoring = question.get('scoring', [])
        options = question.get('options', [])
        
        # Skip if no answer or only "Não sei" (index 0)
        is_skipped = (
            not user_answer or 
            (len(user_answer) == 1 and user_answer == '0')
        )
        
        if is_skipped:
            per_question[question_idx] = 0
            continue
        
        # Calculate points for selected options
        question_points = 0
        for answer_idx in user_answer:
            try:
                idx = int(answer_idx)
                if 0 <= idx < len(scoring):
                    question_points += float(scoring[idx])
            except (ValueError, IndexError):
                continue
        
        per_question[question_idx] = question_points
        total_points += question_points
    
    return {
        "total_points": total_points,
        "per_question_points": per_question
    }

def score_counts(
    answers: Dict[Union[str, int], List],
    questions: List[Dict]
) -> Dict[str, int]:
    """
    Count correct/wrong/skip.
    
    Scoring logic:
    - Skip: no answer or only "Não sei" (index 0)
    - Correct: sum of points > 0
    - Wrong: selected but sum <= 0
    
    Args:
        answers: dict like {'0': ['1'], '1': ['2'], ...}
        questions: list of question dicts from getListOfQuestions()
    
    Returns:
        dict with total, correct, wrong, skip counts
    """
    correct = 0
    wrong = 0
    skip = 0
    total = len(questions)
    
    for i, question in enumerate(questions):
        question_idx = str(i)
        user_answer = answers.get(question_idx, [])
        
        scoring = question.get('scoring', [])
        options = question.get('options', [])
        
        # Check if skipped
        is_skipped = (
            not user_answer or 
            (len(user_answer) == 1 and user_answer == '0')
        )
        
        if is_skipped:
            skip += 1
            continue
        
        # Calculate points
        question_points = 0
        for answer_idx in user_answer:
            try:
                idx = int(answer_idx)
                if 0 <= idx < len(scoring):
                    question_points += float(scoring[idx])
            except (ValueError, IndexError):
                continue
        
        # Count as correct or wrong
        if question_points > 0:
            correct += 1
        else:
            wrong += 1
    
    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "skip": skip
    }

def format_score_summary(score_result: Dict) -> Dict:
    """
    Format score results for display.
    
    Args:
        score_result: result from calculate_score() in quiz_helpers.py
    
    Returns:
        formatted dict ready for templates
    """
    total_points = score_result.get('total_points', 0)
    max_points = score_result.get('max_possible_points', 1)
    
    percentage = (total_points / max_points * 100) if max_points > 0 else 0
    
    return {
        'percentage': round(percentage, 1),
        'total_points': round(total_points, 1),
        'max_points': max_points,
        'n_correct': score_result.get('n_correct', 0),
        'n_wrong': score_result.get('n_wrong', 0),
        'n_skip': score_result.get('n_skip', 0),
        'total_questions': score_result.get('total_questions', 0)
    }
