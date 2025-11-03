from flask import current_app
from urllib.parse import urljoin
import random

def make_url_dev(rel: str) -> str:
    """
    Development URL - serve from local quiz-time folder
    Direct path avoiding blueprint context issues
    """
    if not rel:
        return ""
    
    # Simple direct path - no url_for() context confusion
    url = f"/quiz-time/{rel}"
    print(f"DEBUG: make_url_dev({rel}) -> {url}")
    return url

def make_url_prod(rel: str) -> str:
    """
    Production URL - serve from remote CDN/web server
    """
    prod_base = current_app.config.get('QUIZ_ASSETS_PROD_URL', '')
    if not prod_base:
        # Fallback to dev if no prod URL configured
        return make_url_dev(rel)
    return urljoin(prod_base, rel.lstrip('/'))

def make_url(rel: str) -> str:
    """
    Environment-aware URL builder.
    
    Set QUIZ_ASSETS_SOURCE in config to 'dev' or 'prod'.
    For production, also set QUIZ_ASSETS_PROD_URL.
    """
    if not rel:
        return ""
    
    source = current_app.config.get('QUIZ_ASSETS_SOURCE', 'dev').lower()
    
    if source == 'prod':
        url = make_url_prod(rel)
    else:
        url = make_url_dev(rel)
    
    return url

def getListOfQuestions():
    """
    Get list of quiz questions
    Returns list of dictionaries with question data
    """
    # Sample data - replace with database query later
    list_of_questions = [
        {
            "uuid": "bd415bce-6028-4a73-9273-295310b3f3b6",
            "question_number": 1,
            "image_path": "anos/ano5/tema1/aula106/e1.png",
            "title": "Responda apenas a a)",
            "note": "Note 1",
            "is_multiple_choice": False,
            "options": ["Não sei", "700", "600", "620", "580"],
            "scoring": ["0", "-2", "5", "-2", "-2"]
        },
        {
            "uuid": "a28eac48-a6e9-4b26-9840-08805e2a7a2d",
            "question_number": 2,
            "image_path": "anos/ano5/tema1/aula106/e1.png",
            "title": "Responda apenas a b)",
            "note": "Note 1",
            "is_multiple_choice": False,
            "options": ["Não sei", "1400", "1450", "1250", "1427"],
            "scoring": ["0", "5", "-2", "-2", "-2"]
        },
        {
            "uuid": "31019225-8336-45d4-825b-3cefd953984c",
            "question_number": 3,
            "image_path": "anos/ano5/tema1/aula106/e1.png",
            "title": "Responda apenas a c)",
            "note": "Note 1",
            "is_multiple_choice": False,
            "options": ["Não sei", "1102", "1010", "1200", "1100"],
            "scoring": ["0", "-2", "-2", "-2", "5"]
        },
        {
            "uuid": "c2fbaf7e-b689-44e6-b0e1-a76246019222",
            "question_number": 4,
            "image_path": "anos/ano5/tema2/aula113/e5.png",
            "title": "",
            "note": "",
            "is_multiple_choice": False,
            "options": ["Não sei", "O João tem razão", "A Joana tem razão"],
            "scoring": ["0", "-3", "5"]
        },
        {
            "uuid": "4d72c744-2b85-4bc6-848c-9f60de652595",
            "question_number": 5,
            "image_path": "anos/ano5/tema1/aula112/e3.png",
            "title": "Responda apenas a b)",
            "note": "<img>another_image.png</img>",
            "is_multiple_choice": True,
            "options": ["Não sei", "2^4", "2^5", "2^6", "2^8"],
            "scoring": ["0", "-1", "5", "-1", "-1"]
        }
    ]
    
    random.shuffle(list_of_questions)
    
    out = []
    for question in list_of_questions:
        img_url = make_url(question['image_path'])
        out.append({
            'uuid': question['uuid'],
            'question_number': question['question_number'],
            'image_url': img_url,
            'title': question['title'],
            'note': question['note'],
            'is_multiple_choice': question['is_multiple_choice'],
            'options': question['options'],
            'scoring': question['scoring']
        })
    
    return out


def calculate_score(questions, user_answers):
    """
    Calculate quiz results
    Returns dictionary with results summary
    
    Scoring logic:
    - "Não sei" (index 0, score 0) = skipped question (no points, doesn't count as wrong)
    - Any other answer = correct (positive score) or wrong (negative score)
    """
    total_questions = len(questions)
    n_correct = 0
    n_wrong = 0
    n_skip = 0
    total_points = 0
    max_possible_points = 0
    
    question_results = []
    
    for i, question in enumerate(questions):
        question_idx = str(i)
        user_answer = user_answers.get(question_idx, [])
        
        # Get scoring system for this question
        scoring = question['scoring']
        options = question['options']
        
        # Calculate max possible points for this question
        max_points = max([float(score) for score in scoring if float(score) > 0])
        max_possible_points += max_points
        
        # Determine if answer was given
        # A question is skipped if:
        # 1. No answer was submitted at all (empty list)
        # 2. Only "Não sei" (index 0) is selected
        is_skipped = (
            not user_answer or  # No answer submitted
            (len(user_answer) == 1 and user_answer[0] == '0')  # Only "Não sei"
        )
        
        if is_skipped:
            # Skipped question - 0 points, doesn't count as wrong
            n_skip += 1
            question_points = 0
            result_type = 'skipped'
            print(f"DEBUG: Question {i} is SKIPPED (user_answer={user_answer})")
        else:
            # Calculate points for this question
            question_points = 0
            for answer_idx in user_answer:
                try:
                    idx = int(answer_idx)
                    if 0 <= idx < len(scoring):
                        question_points += float(scoring[idx])
                except (ValueError, IndexError):
                    continue
            
            # Determine if correct or wrong
            if question_points > 0:
                n_correct += 1
                result_type = 'correct'
                print(f"DEBUG: Question {i} is CORRECT (points={question_points})")
            else:
                n_wrong += 1
                result_type = 'wrong'
                print(f"DEBUG: Question {i} is WRONG (points={question_points})")
            
            total_points += question_points
        
        question_results.append({
            'question': question,
            'user_answer': user_answer,
            'points': question_points,
            'result_type': result_type
        })
    
    # Calculate percentage
    if max_possible_points > 0:
        percentage = (total_points / max_possible_points) * 100
    else:
        percentage = 0
    
    print(f"\nDEBUG SUMMARY: correct={n_correct}, wrong={n_wrong}, skip={n_skip}, total_points={total_points}")
    
    return {
        'total_points': round(total_points, 1),
        'percentage': round(percentage, 1),
        'n_correct': n_correct,
        'n_wrong': n_wrong,
        'n_skip': n_skip,
        'total_questions': total_questions,
        'max_possible_points': max_possible_points,
        'question_results': question_results
    }
