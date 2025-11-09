from flask import current_app
from urllib.parse import urljoin
import sqlite3
import json
import random
import os

def split_top_level_commas_with_quotes(s: str):
    parts = []
    buf = []
    depth = 0          # { } nesting
    in_quote = False   # single quotes '
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "'" and not in_quote:
            in_quote = True
            buf.append(ch)
        elif ch == "'" and in_quote:
            in_quote = False
            buf.append(ch)
        elif ch == '{' and not in_quote:
            depth += 1
            buf.append(ch)
        elif ch == '}' and not in_quote:
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == ',' and not in_quote and depth == 0:
            parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        parts.append(''.join(buf).strip())
    return parts

def parse_possible_answers(field: str):
    items = split_top_level_commas_with_quotes(field)
    # strip outer single quotes if present
    cleaned = []
    for x in items:
        x = x.strip()
        if len(x) >= 2 and x[0] == "'" and x[-1] == "'":
            x = x[1:-1]
        cleaned.append(x.strip())
    return cleaned

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

from DBhelpers import getQuestionIDsForYear, getQuestionFromQid

def getListOfQuestionIDs(year=5):
    """
    Get list of question IDs only - keeps session cookie tiny.
    Wrapper around DBhelpers.getQuestionIDsForYear()
    """
    return getQuestionIDsForYear(year)


def getQuestionFromRowID(qid):
    """
    Fetch a single full question by ID.
    Wrapper around DBhelpers.getQuestionFromQid()
    """
    return getQuestionFromQid(qid)


def calculate_score(questions, user_answers):
    """
    Calculate quiz results
    Returns dictionary with results summary
    
    Scoring logic:
    - "Não sei" (index 0, score 0) = skipped question (no points, doesn't count as wrong)
    - Any other answer = correct (positive score) or wrong (negative score)
    
    Args:
        questions: list of sqlite3.Row objects from getQuestionFromQid()
        user_answers: dict like {'0': ['1'], '1': ['2'], ...} (index-based)
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
        
        # Parse scoring and options from sqlite3.Row or dict
        if isinstance(question, dict):
            scoring_str = question.get('scoring_system', '')
            options_str = question.get('possible_answers', '')
        else:
            # sqlite3.Row object
            scoring_str = question['scoring_system']
            options_str = question['possible_answers']
        

        
        # Parse CSV fields
        scoring = [s.strip() for s in scoring_str.split(',')] if scoring_str else []
        options = [s.strip() for s in options_str.split(',')] if options_str else []
        options = [s.strip() for s in parse_possible_answers(question['possible_answers'])] if question['possible_answers'] else []


        print("scoring_system",len(scoring),scoring)
        print("possible_answers",len(options),options)


        # Calculate max possible points for this question
        try:
            max_points = sum([float(score) for score in scoring if float(score) > 0])
        except ValueError:
            max_points = 0
        max_possible_points += max_points
        
        # Determine if answer was given
        is_skipped = (
            not user_answer or
            (len(user_answer) == 1 and user_answer[0] == '0')
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
        

        # print("--------------------",question)


        composed_instruction = None
        if question['type_of_problem'] == 'composed':
            composed_instruction = f"Responder apenas à {question['question_number']}ª pergunta"
            if question['titulo']:
                composed_instruction += question['titulo']


        # Build question dict for results display
        question_dict = {
            'db_id': question['rowid'],
            'uuid': question['uuid'],
            'question_path': f"{question['ano']}/{question['nome_tema']}/{question['aula_title']}",
            # 'title': question['titulo'],
            'note': question['nota'],
            'is_multiple_choice': bool(question['is_multiple_choice']),
            'type_of_answer': question['formatting'],
            'options': options,
            'scoring': scoring,
            'img_url': question['imagem'],
            'type_of_problem': question['type_of_problem'],
            'question_number': question['question_number'],
            'composed_instruction': composed_instruction
        }
        
        question_results.append({
            'question': question_dict,
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
