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

@quiz_bp.route('/quiz-config')
def quiz_config():
    """Display quiz configuration page"""
    user = session.get('user', None)
    
    content_html = render_template(
        'content/quiz_config.html'
    )
    
    return render_template(
        'index.html',
        admin_email=current_app.config.get('ADMIN_EMAIL', ''),
        user=user,
        metadata={},
        page_title='Configuração do Quiz',
        title='Configurar Quiz',
        main_content=content_html
    )


@quiz_bp.route('/quiz')
def start_quiz():
    """Initialize quiz - cleanup expired results"""
    cleanup_expired_results()
    
    # Get configuration from query parameters or use defaults
    year = request.args.get('year', 7, type=int)
    num_exercises = request.args.get('num_exercises', 20, type=int)
    current_year_percent = request.args.get('current_year_percent', 50, type=int)
        
    if num_exercises not in [20, 40, 60, 80, 100]:
        flash('Número de exercícios inválido.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    
    # Auto-adjust percentage for edge cases
    if year == 5:
        current_year_percent = 100  # Force 100% for year 5 (no previous years)
    elif year > 7:
        current_year_percent = 0  # Force 0% for years under construction (use previous years only)
    
    # Validate percentage (only if year is 6 or 7)
    if year in [6, 7]:
        if current_year_percent not in [25, 50, 75]:
            flash('Percentagem inválida.', 'error')
            return redirect(url_for('quiz.quiz_config'))
        
    # Store configuration in session
    session['quiz_config'] = {
        'year': year,
        'num_exercises': num_exercises,
        'current_year_percent': current_year_percent
    }
    
    # Get questions for the current year
    current_year_questions = getQuestionIDsForYear(year=year,num_exercises=num_exercises,current_year_percent=current_year_percent)
    
    if not current_year_questions:
        flash('Erro ao carregar perguntas. Tente novamente.', 'error')
        return redirect(url_for('quiz.quiz_config'))


    # question_ids = getQuestionIDsForYear(year=7)
    
    # if not question_ids:
    #     flash('Erro ao carregar perguntas. Tente novamente.','error')
    #     return redirect(url_for('index'))
    
    session['question_ids'] = current_year_questions  # ✓ CORRECT
    session['current_question'] = 0
    session['user_answers'] = {}
    session['quiz_started'] = True
    
    # print(f"Quiz started with {len(question_ids)} question IDs")
    return redirect(url_for('quiz.question', question_num=0))

@quiz_bp.route('/quiz/<int:question_num>')
def question(question_num):
    """Display a specific question"""
    if 'question_ids' not in session:  # ✓ CHANGED FROM 'quiz_question_ids'
        flash('Erro: Sessão de quiz não encontrada. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    question_ids = session['question_ids']  # ✓ CHANGED FROM 'quiz_question_ids'
    # print("question_ids =", question_ids)
    
    # Validate question number
    if question_num < 0 or question_num >= len(question_ids):
        flash('Pergunta não encontrada.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    # Fetch the actual question data by ID
    qid = question_ids[question_num]
    # print(qid)
    question_data = getQuestionFromQid(qid)
    # print(question_data)
    # print()

    if not question_data:
        flash('Erro ao carregar pergunta.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    question_path = f"{question_data['ano']}/{question_data['nome_tema']}/{question_data['aula_title']}/{question_data['num_aula']}/{question_data['uuid']}"
    imageName = question_data['imagem']#.replace('ano','anos/ano').replace('aula',f'tema{question_data['num_tema']}/aula').replace('.jpg','.png')

    # image_url = make_url(imageName) if question_data['imagem'] else ""
    image_url = imageName
    # print("147",image_url)


    possible_answers = [s.strip() for s in parse_possible_answers(question_data['possible_answers'])] if question_data['possible_answers'] else []
    scoring_system = [s.strip() for s in question_data['scoring_system'].split(',')] if question_data['scoring_system'] else []

    # Fix: unescape double backslashes for LaTeX
    if question_data['formatting'] == 'latex':
        possible_answers = [opt.replace('\\\\', '\\') for opt in possible_answers]

    composed_instruction = None
    if question_data['type_of_problem'] == 'composed':
        composed_instruction = f"Responder apenas à {question_data['question_number']}ª pergunta"
        if question_data['titulo']:
            composed_instruction += question_data['titulo']
    
    note = question_data['nota']

    # print("------------------------------",note)
    # Convert to dictionary
    current_question = {
        'db_id': question_data['rowid'],
        'uuid': question_data['uuid'],
        'question_path': question_path,
        'image_url': image_url,
        # 'title': question_data['titulo'],
        'note': note,
        'is_multiple_choice': bool(question_data['is_multiple_choice']),
        'type_of_answer': question_data['formatting'],
        'options': possible_answers,
        'scoring': scoring_system,
        'type_of_problem': question_data['type_of_problem'],
        'question_number': question_data['question_number'],
        'composed_instruction': composed_instruction
        # print(question['question_number'],question['type_of_problem'])

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

# @quiz_bp.route('/results')
@quiz_bp.route('/results', methods=['GET'])
def results():
    """
    Display quiz results with robust question normalization so templates
    always have image data available.
    """
    # 1) Validate session payload
    if 'question_ids' not in session or 'user_answers' not in session:
        flash('Erro: Dados do quiz não encontrados. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))

    question_ids = session['question_ids']
    user_answers = session['user_answers']

    # 2) Load raw questions (sqlite3.Row) and convert to dict
    raw_questions = []
    for qid in question_ids:
        q_row = getQuestionFromQid(qid)
        if q_row:
            raw_questions.append(dict(q_row))  # convert Row -> dict

    # 3) Normalize each question into a consistent view model
    #    - Ensure image_url exists
    #    - Keep original imagem in case template wants a fallback
    #    - Keep options/scoring as raw strings (your calculate_score already knows how to read them)
    questions_fixed = []
    for q in raw_questions:
        q_fixed = dict(q)

        # Guarantee image_url is present; DB now holds full path in 'imagem'
        img = q_fixed.get('imagem', '') or ''
        q_fixed['image_url'] = img

        # Ensure required keys exist to avoid template KeyErrors
        q_fixed.setdefault('type_of_answer', q_fixed.get('formatting', 'text'))
        q_fixed.setdefault('is_multiple_choice', bool(q_fixed.get('is_multiple_choice', 0)))
        q_fixed.setdefault('options', q_fixed.get('possible_answers', ''))
        q_fixed.setdefault('scoring', q_fixed.get('scoring_system', ''))
        q_fixed.setdefault('title', q_fixed.get('titulo'))
        q_fixed.setdefault('note', q_fixed.get('nota'))

        questions_fixed.append(q_fixed)

    # print(questions_fixed)

    # 4) Score using the normalized list (order preserved)
    quiz_results = calculate_score(questions_fixed, user_answers)

    # After: quiz_results = calculate_score(questions_fixed, user_answers)

    if isinstance(quiz_results, dict) and quiz_results.get('question_results'):
        qr0 = quiz_results['question_results'][0]
        q0 = qr0.get('question', {})
        # print('RESULTS FIRST IMG:', q0)
    else:
        # print('RESULTS payload has no question_results or is not a dict:', type(quiz_results))
        pass
    

    # 5) Auth and optional persistence
    email = session.get('metadata', {}).get('email', '') if session.get('metadata') else ''
    is_authenticated = bool(email)
    quiz_uuid = None

    if not is_authenticated:
        # Save the normalized version to keep structure stable if viewed later
        quiz_uuid = save_quiz_result(user_answers, questions_fixed)
        session['quiz_uuid'] = quiz_uuid

    user = session.get('user')

    # 6) Render the results content
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=questions_fixed,         # pass normalized list to template
        user_answers=user_answers,
        quiz_uuid=quiz_uuid,
        is_authenticated=is_authenticated,
        email=email
    )

    # 7) Wrap in main layout
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
        # print(qnum)
        qnum = int(qnum)
        # print(qnum)

        question = getQuestionFromQid(qnum)
        # print(question)

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
