from flask import current_app
from urllib.parse import urljoin
import sqlite3
import json
import random
import os

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def make_url_dev(rel: str) -> str:
    """Development URL - serve from local quiz-time folder"""
    if not rel:
        return ""
    # url = f"/quiz-time/{rel}"
    url = f"/{rel}"
    return url

def make_url_prod(rel: str) -> str:
    """Production URL - serve from remote CDN/web server"""
    prod_base = current_app.config.get('QUIZ_ASSETS_PROD_URL', '')
    if not prod_base:
        return make_url_dev(rel)
    return urljoin(prod_base, rel.lstrip('/'))

def make_url(rel: str) -> str:
    """Environment-aware URL builder"""
    if not rel:
        return ""
    source = current_app.config.get('QUIZ_ASSETS_SOURCE', 'dev').lower()
    return make_url_prod(rel) if source == 'prod' else make_url_dev(rel)

def getListOfQuestions():
    """
    Get list of quiz questions from SQLite database
    
    Returns list of dictionaries with question data including:
    - db_id: rowid from database (for recording responses)
    - question_path: ano/tema/aula for display at top
    - title: optional question title (from titulo)
    - note: optional question note (from nota)
    - is_multiple_choice: boolean from type_of_selection
    - type_of_answer: 'latex', 'text', or 'image'
    - options: list of answer options
    - scoring: list of point values per option
    - composed_note: if type_of_problem == 'composed', shows "Responder apenas a pergunta X"
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Your SQL query - get 15 from ano=5 and 15 from ano<5
    query = """
    SELECT 
        r.rowid,
        t.ano,
        t.nome_tema,
        a.title as aula_title,
        a.num_tema,
        r.uuid,
        r.imagem,
        r.type_of_problem,
        (r.type_of_selection = 'multiple_choice') as is_multiple_choice,
        r.question_number,
        r.formatting,
        r.possible_answers,
        r.correct_answer,
        r.scoring_system,
        r.titulo,
        r.nota
    FROM responses r
    JOIN aulas a ON a.num_aula = r.aula 
    JOIN temas t ON t.num_tema = a.num_tema AND t.ano = a.ano
    WHERE r.rowid IN (
        SELECT rowid FROM responses
        WHERE rowid IN (SELECT rowid FROM responses WHERE ano = ? ORDER BY RANDOM() LIMIT ?)
        UNION
        SELECT rowid FROM responses
        WHERE rowid IN (SELECT rowid FROM responses WHERE ano < ? ORDER BY RANDOM() LIMIT ?)
    )
    ORDER BY RANDOM();
    """
    
    cursor.execute(query,(5,20,5,15))
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    
    for row in rows:
        print(f"Raw from DB: {repr(row['possible_answers'])}")

        # Parse CSV fields (not JSON!)
        try:
            # Split by comma and strip whitespace
            possible_answers = [s.strip() for s in row['possible_answers'].split(',')] if row['possible_answers'] else []
            scoring_system = [s.strip() for s in row['scoring_system'].split(',')] if row['scoring_system'] else []


            # Fix: unescape double backslashes for LaTeX
            if row['formatting'] == 'latex':
                possible_answers = [opt.replace('\\\\', '\\') for opt in possible_answers]


            # # IMPORTANT: Ensure backslashes in LaTeX are preserved
            # # If formatting is 'latex', make sure the options keep their backslashes
            # if row['formatting'] == 'latex':
            #     # The backslashes should already be there if stored correctly
            #     # But verify by checking if they exist
            #     possible_answers = [opt if opt.startswith('\\') or opt == 'Não sei' else opt for opt in possible_answers]


            print(f"DEBUG Options: {possible_answers}")
            print(f"DEBUG Scoring: {scoring_system}")
            
        except (ValueError, AttributeError):
            possible_answers = []
            scoring_system = []

        # Build question path: ano/tema/aula
        question_path = f"{row['ano']}/{row['nome_tema']}/{row['aula_title']}"
        
        # Build composed question note if needed
        composed_note = ""
        if row['type_of_problem'] == 'composed':
            composed_note = f"Responder apenas a pergunta {row['question_number']}"
        
        # Build title text (combine titulo and composed_note if both exist)
        title_text = row['titulo'] if row['titulo'] else ""
        if composed_note:
            title_text = f"{title_text} {composed_note}" if title_text else composed_note
        
        # Image URL
        imageName = row['imagem'].replace('ano','anos/ano').replace('aula',f'tema{row['num_tema']}/aula').replace('.jpg','.png')
        image_url = make_url(imageName) if row['imagem'] else ""

        question = {
            'db_id': row['rowid'],  # Use rowid to record responses
            'uuid': row['uuid'],
            'question_path': question_path,  # Display at top: ano/tema/aula
            'image_url': image_url,
            'title': title_text,  # Combined titulo + composed note
            'note': row['nota'],  # Only if not null
            'is_multiple_choice': bool(row['is_multiple_choice']),
            'question_number': row['question_number'],  # For composed questions
            'type_of_answer': row['formatting'],  # 'latex', 'text', or 'image'
            'options': possible_answers,
            'scoring': scoring_system,
            'type_of_problem': row['type_of_problem'],
            'composed_instruction': f"Responder apenas à {row['question_number']}ª pergunta." if row['type_of_problem'] == 'composed' else None
        }
        
        questions.append(question)
    
    # Randomize order
    random.shuffle(questions)
    
    print(f"DEBUG: Loaded {len(questions)} questions from database")
    
    return questions

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
        is_skipped = (
            not user_answer or
            (len(user_answer) == 1 and user_answer == '0')
        )
        
        if is_skipped:
            n_skip += 1
            question_points = 0
            result_type = 'skipped'
        else:
            question_points = 0
            for answer_idx in user_answer:
                try:
                    idx = int(answer_idx)
                    if 0 <= idx < len(scoring):
                        question_points += float(scoring[idx])
                except (ValueError, IndexError):
                    continue
            
            if question_points > 0:
                n_correct += 1
                result_type = 'correct'
            else:
                n_wrong += 1
                result_type = 'wrong'
            
            total_points += question_points
        
        question_results.append({
            'question': question,
            'user_answer': user_answer,
            'points': question_points,
            'result_type': result_type
        })
    
    # Calculate percentage
    percentage = (total_points / max_possible_points * 100) if max_possible_points > 0 else 0
    
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
