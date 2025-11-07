from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from DBhelpers import getQuestionIDsForYear, getQuestionFromQid
from Funhelpers.quiz_helpers import calculate_score
from Funhelpers.quiz_storage import (
    save_quiz_result,
    get_quiz_result,
    cleanup_expired_results
)
from urllib.parse import urljoin

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

def split_top_level_commas(s: str):
    parts = []
    buf = []
    depth = 0  # tracks nesting of { }
    for ch in s:
        if ch == '{':
            depth += 1
            buf.append(ch)
        elif ch == '}':
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append(''.join(buf).strip())
    return parts

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

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz')
def start_quiz():
    """Initialize quiz - cleanup expired results"""
    cleanup_expired_results()
    
    question_ids = getQuestionIDsForYear(year=5)
    
    if not question_ids:
        flash('Erro ao carregar perguntas. Tente novamente.','error')
        return redirect(url_for('index'))
    
    session['question_ids'] = question_ids  # ✓ CORRECT
    session['current_question'] = 0
    session['user_answers'] = {}
    session['quiz_started'] = True
    
    print(f"Quiz started with {len(question_ids)} question IDs")
    return redirect(url_for('quiz.question', question_num=0))

@quiz_bp.route('/quiz/<int:question_num>')
def question(question_num):
    """Display a specific question"""
    if 'question_ids' not in session:  # ✓ CHANGED FROM 'quiz_question_ids'
        flash('Erro: Sessão de quiz não encontrada. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    question_ids = session['question_ids']  # ✓ CHANGED FROM 'quiz_question_ids'
    print("question_ids =", question_ids)
    
    # Validate question number
    if question_num < 0 or question_num >= len(question_ids):
        flash('Pergunta não encontrada.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    # Fetch the actual question data by ID
    qid = question_ids[question_num]
    print(qid)
    question_data = getQuestionFromQid(qid)
    print(question_data)
    print()

    if not question_data:
        flash('Erro ao carregar pergunta.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    question_path = f"{question_data['ano']}/{question_data['nome_tema']}/{question_data['aula_title']} / aula{question_data['num_aula']} / {question_data['uuid']}"
    imageName = question_data['imagem'].replace('ano','anos/ano').replace('aula',f'tema{question_data['num_tema']}/aula').replace('.jpg','.png')

    image_url = make_url(imageName) if question_data['imagem'] else ""



    possible_answers = [s.strip() for s in parse_possible_answers(question_data['possible_answers'])] if question_data['possible_answers'] else []
    scoring_system = [s.strip() for s in question_data['scoring_system'].split(',')] if question_data['scoring_system'] else []

    # Fix: unescape double backslashes for LaTeX
    if question_data['formatting'] == 'latex':
        possible_answers = [opt.replace('\\\\', '\\') for opt in possible_answers]

    # Convert to dictionary
    current_question = {
        'db_id': question_data['rowid'],
        'uuid': question_data['uuid'],
        'question_path': question_path,
        'image_url': image_url,
        'title': question_data['titulo'],
        'note': question_data['nota'],
        'is_multiple_choice': bool(question_data['is_multiple_choice']),
        'type_of_answer': question_data['formatting'],
        'options': possible_answers,
        'scoring': scoring_system,
        'type_of_problem': question_data['type_of_problem'],
        'question_number': question_data['question_number']
    }
    
    user_answers = session.get('user_answers', {})
    current_answer = user_answers.get(str(question_num), [])
    user = session.get('user', None)
    
    content_html = render_template(
        'content/quiz_question.html',
        question=current_question,
        question_num=question_num,
        total_questions=len(question_ids),
        current_answer=current_answer
    )
    
    return render_template(
        'index.html',
        admin_email=current_app.config.get('ADMIN_EMAIL', ''),
        user=user,
        metadata={},
        page_title=f'Quiz - Pergunta {question_num + 1}/{len(question_ids)}',
        title=f'Quiz - Pergunta {question_num + 1} de {len(question_ids)}',
        main_content=content_html
    )



@quiz_bp.route('/quiz/submit', methods=['POST'])
def submit_answer():
    """Handle answer submission"""
    if 'question_ids' not in session:  # ✓ CHANGED
        return jsonify({'error': 'Sessão de quiz não encontrada'}), 400
    
    question_num = int(request.form.get('question_num'))
    answer_data = request.form.getlist('answer')
    
    if 'user_answers' not in session:
        session['user_answers'] = {}
    
    session['user_answers'][str(question_num)] = answer_data
    session.modified = True
    
    return jsonify({'success': True})

@quiz_bp.route('/quiz/navigate', methods=['POST'])
def navigate():
    """Handle navigation between questions"""
    if 'question_ids' not in session:  # ✓ CHANGED
        return jsonify({'error': 'Sessão de quiz não encontrada'}), 400
    
    action = request.form.get('action')
    current_question = int(request.form.get('current_question'))
    total_questions = len(session['question_ids'])  # ✓ CHANGED
    
    if action == 'next':
        next_question = current_question + 1
        if next_question >= total_questions:
            return jsonify({'redirect': url_for('quiz.results')})
        else:
            return jsonify({'redirect': url_for('quiz.question', question_num=next_question)})
    elif action == 'previous':
        prev_question = max(0, current_question - 1)
        return jsonify({'redirect': url_for('quiz.question', question_num=prev_question)})
    elif action == 'finish':
        return jsonify({'redirect': url_for('quiz.results')})
    
    return jsonify({'error': 'Ação inválida'}), 400

@quiz_bp.route('/results')
def results():
    """Display quiz results"""
    if 'question_ids' not in session or 'user_answers' not in session:  # ✓ CHANGED
        flash('Erro: Dados do quiz não encontrados. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    question_ids = session['question_ids']  # ✓ CHANGED
    user_answers = session['user_answers']
    
    questions = []
    for qid in question_ids:
        q_data = getQuestionFromQid(qid)
        if q_data:
            questions.append(q_data)
    
    quiz_results = calculate_score(questions, user_answers)
    
    email = session.get('metadata', {}).get('email', '') if session.get('metadata') else ''
    is_authenticated = bool(email)
    quiz_uuid = None
    
    if not is_authenticated:
        quiz_uuid = save_quiz_result(user_answers, questions)
        session['quiz_uuid'] = quiz_uuid
    else:
        print(f"TODO: Save authenticated user quiz to database: {email}")
    
    user = session.get('user', None)
    
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=questions,
        user_answers=user_answers,
        quiz_uuid=quiz_uuid,
        is_authenticated=is_authenticated,
        email=email
    )
    
    return render_template(
        'index.html',
        admin_email=current_app.config.get('ADMIN_EMAIL', ''),
        user=user,
        metadata={},
        page_title='Quiz - Resultados',
        title='Resultados do Quiz',
        main_content=content_html
    )


@quiz_bp.route('/results/<quiz_uuid>')
def view_quiz_result(quiz_uuid):
    """
    Display a previously saved anonymous quiz result by UUID.
    Results expire after 1 hour.
    """
    from Funhelpers.quiz_storage import get_quiz_result
    from DBhelpers import getQuestionFromQid
    
    # Retrieve the quiz result (answers keyed by question_number)
    quiz_data = get_quiz_result(quiz_uuid)
    
    if not quiz_data:
        flash('Quiz não encontrado ou expirado. Os resultados têm validade de 1 hora.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    answers = quiz_data['answers_by_question_number']  # {question_number: [option_indices]}
    timestamp = quiz_data['timestamp']
    
    # Convert question_numbers to rowids, then fetch full questions
    questions = []
    answers_by_index = {}  # Rebuild as {index: [options]} for calculate_score
    
    for idx, (qnum, options) in enumerate(sorted(answers.items())):
        print(qnum)
        qnum = int(qnum)
        print(qnum)

        question = getQuestionFromQid(qnum)
        print(question)

        if question:
            questions.append(question)
            answers_by_index[str(idx)] = options
    
    if not questions:
        flash('Não foi possível carregar as perguntas do quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    # Calculate results
    quiz_results = calculate_score(questions, answers_by_index)
    
    user = session.get('user', None)
    
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=questions,
        user_answers=answers_by_index,
        quiz_uuid=quiz_uuid,
        is_authenticated=False,
        email='',
        timestamp=timestamp
    )
    
    return render_template(
        'index.html',
        admin_email=current_app.config.get('ADMIN_EMAIL', ''),
        user=user,
        metadata={},
        page_title=f'Quiz - Resultados ({quiz_uuid[:8]}...)',
        title=f'Resultados do Quiz',
        main_content=content_html
    )




@quiz_bp.route('/quiz/restart')
def restart_quiz():
    """Clear quiz session and start over"""
    session.pop('quiz_questions', None)
    session.pop('current_question', None)
    session.pop('user_answers', None)
    session.pop('quiz_started', None)
    session.pop('quiz_uuid', None)
    
    flash('Quiz reiniciado com sucesso!', 'success')
    return redirect(url_for('quiz.start_quiz'))
