from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from DBhelpers import getQuestionIDsForYear, getQuestionFromQid
from Funhelpers.quiz_helpers import calculate_score
from Funhelpers.quiz_storage import (
    save_quiz_result,
    save_quiz_history_for_user,
    # get_quiz_result,
    cleanup_expired_results
)
from urllib.parse import urljoin
import json

def split_top_level_commas_with_quotes(s: str):
    """
    Splits a string by top-level commas, ignoring commas within curly braces and single quotes.

    This function is designed to parse comma-separated fields that may contain nested
    structures (e.g., JSON-like objects) or string literals. It correctly handles nested
    braces and quoted sections, ensuring that only commas at the top level are used as
    delimiters.

    Args:
        s (str): The string to be split.

    Returns:
        list[str]: A list of strings, representing the split parts of the input string.
    """
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
    """
    Splits a string by top-level commas, ignoring commas within curly braces.

    This utility function is used to parse comma-separated strings that may contain
    nested structures enclosed in curly braces, such as simple object representations.
    It only splits by commas that are not inside any level of brace nesting.

    Args:
        s (str): The string to be split.

    Returns:
        list[str]: A list of strings, representing the split parts of the input string.
    """
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
    """
    Generates a URL for a quiz asset in a development environment.

    This helper function constructs a local URL for serving quiz assets from the
    'quiz-time' folder during development. It returns an empty string if the
    relative path is empty.

    Args:
        rel (str): The relative path to the asset.

    Returns:
        str: The development URL for the asset.
    """
    if not rel:
        return ""
    # url = f"/quiz-time/{rel}"
    url = f"/{rel}"
    return url

def make_url_prod(rel: str) -> str:
    """
    Generates a production-ready URL for a quiz asset.

    This function constructs an absolute URL for serving quiz assets from a production
    environment, such as a CDN or a dedicated web server. It retrieves the base URL
    from the application's configuration ('QUIZ_ASSETS_PROD_URL'). If the base URL
    is not set, it falls back to the development URL structure.

    Args:
        rel (str): The relative path to the asset.

    Returns:
        str: The absolute production URL for the asset.
    """
    prod_base = current_app.config.get('QUIZ_ASSETS_PROD_URL', '')
    if not prod_base:
        return make_url_dev(rel)
    return urljoin(prod_base, rel.lstrip('/'))

def make_url(rel: str) -> str:
    """
    Creates an environment-aware URL for a quiz asset.

    This function acts as a dispatcher, generating the appropriate URL for an asset based
    on the application's current environment, which is determined by the
    'QUIZ_ASSETS_SOURCE' configuration variable. It will call either `make_url_prod` for
    'prod' environments or `make_url_dev` for any other case.

    Args:
        rel (str): The relative path to the asset.

    Returns:
        str: The full URL (either local or remote) for the asset, or an empty string
             if the relative path is empty.
    """
    if not rel:
        return ""
    source = current_app.config.get('QUIZ_ASSETS_SOURCE', 'dev').lower()
    return make_url_prod(rel) if source == 'prod' else make_url_dev(rel)


def parse_possible_answers(field: str):
    """
    Parses a string of comma-separated possible answers for a quiz question.

    This function takes a raw string from the database, which contains the possible
    answers for a question, and processes it into a list of clean, individual answer
    options. It uses `split_top_level_commas_with_quotes` to correctly handle answers
    that may contain commas or other special characters. It also strips leading/trailing
    whitespace and removes any surrounding single quotes from each answer.

    Args:
        field (str): The raw string containing the possible answers.

    Returns:
        list[str]: A list of cleaned answer strings.
    """
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
    """
    Renders the quiz configuration page.

    This view function displays the page where users can configure their quiz settings,
    such as the academic year and the number of questions. The page is rendered using
    the 'quiz_config.html' template, which is then embedded into the main 'index.html'
    layout.
    """
    # user = session.get('user', None)
    user = session and session.get("metadata")    
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
    """
    Initializes a new quiz session based on user-selected configuration.

    This function serves as the entry point for starting a quiz. It performs the following steps:
    1.  Cleans up any expired, anonymously saved quiz results.
    2.  Retrieves quiz configuration settings (year, number of exercises, etc.) from the
        request's query parameters, with default values as fallbacks.
    3.  Validates the provided configuration, flashing an error and redirecting if the
        parameters are invalid.
    4.  Auto-adjusts the `current_year_percent` for certain edge-case years (e.g., year 5
        or years under construction).
    5.  Stores the final, validated configuration in the user's session.
    6.  Fetches the list of question IDs for the configured quiz from the database.
    7.  Initializes the quiz state in the session (question IDs, current question index, etc.).
    8.  Redirects the user to the first question of the quiz.
    """
    cleanup_expired_results()
    
    # Get configuration from query parameters or use defaults
    year = request.args.get('year', 7, type=int)
    num_exercises = request.args.get('num_exercises', 20, type=int)
    current_year_percent = request.args.get('current_year_percent', 50, type=int)
        
    if num_exercises not in [2, 20, 40, 60, 80, 100]:
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
    """
    Displays a specific quiz question based on its number in the sequence.

    This function is responsible for rendering a single question page. It performs the following steps:
    1.  Validates that a quiz session is active; otherwise, redirects to the config page.
    2.  Checks if the requested `question_num` is within the valid range of the current quiz.
    3.  Retrieves the question's unique ID from the session's list of question IDs.
    4.  Fetches the full question data from the database using the ID.
    5.  Processes the raw question data:
        - Parses the possible answer options.
        - Unescapes characters for special formatting like LaTeX.
        - Constructs additional instructions for 'composed' problems.
    6.  Renders the 'quiz_question.html' template with the processed data.
    7.  Embeds the rendered content into the main 'index.html' layout.

    Args:
        question_num (int): The zero-based index of the question in the current quiz.

    Returns:
        A rendered HTML page for the specific question, or a redirect if an error occurs.
    """
    if 'question_ids' not in session:  # ✓ CHANGED FROM 'quiz_question_ids'
        flash('Erro: Sessão de quiz não encontrada. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    
    question_ids = session['question_ids']  # ✓ CHANGED FROM 'quiz_question_ids'
    # print("question_ids =", question_ids)
    
    # Validate question number
    if question_num < 0 or question_num >= len(question_ids):
        flash('Pergunta não encontrada.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    
    # Fetch the actual question data by ID
    qid = question_ids[question_num]
    # print(qid)
    question_data = getQuestionFromQid(qid)
    # print(question_data)
    # print()

    if not question_data:
        flash('Erro ao carregar pergunta.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    
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
    # user = session.get('user', None)
    user = session and session.get("metadata")



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
    """
    Handles the submission of a user's answer for a specific question.

    This endpoint is called via a POST request (typically using JavaScript) when a user
    submits an answer to a question. It retrieves the question number and the submitted
    answer(s) from the form data.

    The function then stores the answer in the `user_answers` dictionary within the session,
    keyed by the question number. It marks the session as modified to ensure the data is
    saved.

    Returns:
        A JSON response indicating the success or failure of the operation.
    """
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
    """
    Handles navigation between quiz questions (next, previous, finish).

    This endpoint is called via a POST request from the quiz interface to handle user
    navigation. It processes the 'action' from the form data ('next', 'previous', or
    'finish') and determines the appropriate URL to redirect the user to.

    - 'next': Moves to the next question or to the results page if it's the last question.
    - 'previous': Moves to the previous question.
    - 'finish': Proceeds directly to the results page.

    Returns:
        A JSON response containing the URL for the next page, or an error if the action
        is invalid or the session is missing.
    """
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

@quiz_bp.route('/results', methods=['GET'])
def results():
    """
    Calculates and displays the final results of the quiz.

    This function orchestrates the end of the quiz process. It performs these steps:
    1.  Validates that the necessary quiz data (question IDs, user answers) exists in the session.
    2.  Fetches the full data for each question from the database.
    3.  Normalizes the question data into a consistent view model, ensuring that essential keys
        like 'image_url' and 'options' are always present to prevent template errors.
    4.  Calculates the user's score by passing the normalized questions and user answers to the
        `calculate_score` helper function.
    5.  Handles both authenticated and anonymous users:
        - If the user is not authenticated, it saves the quiz results to temporary storage
          and generates a unique UUID for them to view later.
    6.  Renders the 'content/quiz_results.html' template, passing in the score, the list of
        questions, user answers, and authentication status.
    7.  Embeds the rendered content into the main 'index.html' layout.

    Returns:
        A rendered HTML page with the quiz results, or a redirect if the session is invalid.
    """
    # 1) Validate session payload
    if 'question_ids' not in session or 'user_answers' not in session:
        flash('Erro: Dados do quiz não encontrados. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.quiz_config'))

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
        quiz_uuid = save_quiz_result(user_answers, question_ids)
        session['quiz_uuid'] = quiz_uuid
    else:
        # For authenticated users, save to their history
        quiz_config = session.get('quiz_config', {})
        save_quiz_history_for_user(email, quiz_results, quiz_config)

    # user = session.get('user')
    user = session and session.get("metadata")

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
    Displays a previously saved anonymous quiz result using its UUID.

    This function allows users to view the results of a quiz they completed anonymously.
    The results are retrieved from temporary storage using the unique identifier provided
    in the URL. These saved results are configured to expire after one hour.

    The process is as follows:
    1.  Retrieves the saved quiz data (answers and timestamp) using the `quiz_uuid`.
    2.  If the result is not found or has expired, it redirects to the quiz config page.
    3.  Fetches the full question data from the database based on the IDs stored in the result.
    4.  Recalculates the score using the retrieved questions and answers.
    5.  Renders the 'content/quiz_results.html' template with the calculated results,
        original questions, and user answers.

    Args:
        quiz_uuid (str): The unique identifier for the saved quiz result.

    Returns:
        A rendered HTML page with the quiz results, or a redirect if the result is not found.
    """
    from Funhelpers.quiz_storage import get_quiz_result as get_anonymous_quiz_result
    from DBhelpers import getQuestionFromQid, get_quiz_history_by_uuid
    
    email = session.get('metadata', {}).get('email') if session.get('metadata') else ''
    is_authenticated = bool(email)
    quiz_data = None
    
    # 1. If authenticated, try to get result from user's history first
    if is_authenticated:
        quiz_data = get_quiz_history_by_uuid(email, quiz_uuid)
    # print("quiz_data =", quiz_data)

    # 2. If not found or not authenticated, fall back to anonymous results
    if not quiz_data:
        quiz_data = get_anonymous_quiz_result(quiz_uuid)
        if quiz_data:
            # Anonymous results have a different structure
            quiz_data['answers'] = quiz_data.pop('answers_by_question_number', {})
    
    if not quiz_data:
        flash('Quiz não encontrado ou expirado. Os resultados têm validade de 1 hora.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    

    # The key for answers is 'answers' for both DB and anonymous results now
    answers = quiz_data.get('answers', {})
    timestamp = quiz_data['quiz_date']
    
    # Fetch full questions. The keys in 'answers' are question IDs (rowid).
    questions = []
    answers_by_index = {}  # Rebuild as {index: [options]} for calculate_score
    
    # Sort by question ID to maintain a consistent order
    # print("answers:",answers)
    answers = json.loads(answers)
    sorted_qids = sorted([int(k) for k in answers.keys()])

    for idx, qid in enumerate(sorted_qids):
        question = getQuestionFromQid(qid)
        if question:
            questions.append(question)
            answers_by_index[str(idx)] = answers[str(qid)]
    
    if not questions:
        flash('Não foi possível carregar as perguntas do quiz.', 'error')
        return redirect(url_for('quiz.quiz_config'))
    
    # Calculate results
    # Convert sqlite3.Row to dict for calculate_score
    questions_as_dicts = [dict(q) for q in questions]
    quiz_results = calculate_score(questions_as_dicts, answers_by_index)
    
    user = session.get("metadata")
    
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=questions_as_dicts,
        user_answers=answers_by_index,
        quiz_uuid=quiz_uuid,
        is_authenticated=is_authenticated,
        email=email,
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
    """
    Clears all quiz-related data from the session to allow the user to start over.

    This function removes all data associated with the current quiz from the user's session,
    including the list of question IDs, the current question index, all user answers, and
    any UUID from a saved anonymous result.

    After clearing the session, it flashes a success message and redirects the user back
    to the quiz configuration page, allowing them to start a fresh quiz.
    """
    session.pop('quiz_questions', None)
    session.pop('current_question', None)
    session.pop('user_answers', None)
    session.pop('quiz_started', None)
    session.pop('quiz_uuid', None)
    
    flash('Quiz reiniciado com sucesso!', 'success')
    return redirect(url_for('quiz.quiz_config'))
