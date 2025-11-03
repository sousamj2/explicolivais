from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from Funhelpers.quiz_helpers import getListOfQuestions, calculate_score
from Funhelpers.quiz_storage import (
    save_quiz_result,
    get_quiz_result,
    cleanup_expired_results
)

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz')
def start_quiz():
    """Initialize quiz - cleanup expired results"""
    # Clean up expired anonymous results (lazy cleanup)
    cleanup_expired_results()
    
    questions = getListOfQuestions()
    session['quiz_questions'] = questions
    session['current_question'] = 0
    session['user_answers'] = {}
    session['quiz_started'] = True
    
    return redirect(url_for('quiz.question', question_num=0))

@quiz_bp.route('/quiz/<int:question_num>')
def question(question_num):
    """Display a specific question"""
    if 'quiz_questions' not in session:
        flash('Erro: Sessão de quiz não encontrada. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    questions = session['quiz_questions']
    
    # Validate question number
    if question_num < 0 or question_num >= len(questions):
        flash('Pergunta não encontrada.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    current_question = questions[question_num]
    
    user_answers = session.get('user_answers', {})
    current_answer = user_answers.get(str(question_num), [])
    
    # Get user info from session if needed
    user = session.get('user', None)
    
    # Render the content template first to get processed HTML
    content_html = render_template(
        'content/quiz_question.html',
        question=current_question,
        question_num=question_num,
        total_questions=len(questions),
        current_answer=current_answer
    )
    
    # Now render the full page with the processed content
    return render_template(
        'index.html',
        admin_email=current_app.config.get('ADMIN_EMAIL', ''),
        user=user,
        metadata={},
        page_title=f'Quiz - Pergunta {question_num + 1}/{len(questions)}',
        title=f'Quiz - Pergunta {question_num + 1} de {len(questions)}',
        main_content=content_html
    )

@quiz_bp.route('/quiz/submit', methods=['POST'])
def submit_answer():
    """Handle answer submission"""
    if 'quiz_questions' not in session:
        return jsonify({'error': 'Sessão de quiz não encontrada'}), 400
    
    question_num = int(request.form.get('question_num'))
    answer_data = request.form.getlist('answer')
    
    # Store answer in session
    if 'user_answers' not in session:
        session['user_answers'] = {}
    
    session['user_answers'][str(question_num)] = answer_data
    session.modified = True
    
    return jsonify({'success': True})

@quiz_bp.route('/quiz/navigate', methods=['POST'])
def navigate():
    """Handle navigation between questions"""
    if 'quiz_questions' not in session:
        return jsonify({'error': 'Sessão de quiz não encontrada'}), 400
    
    action = request.form.get('action')
    current_question = int(request.form.get('current_question'))
    total_questions = len(session['quiz_questions'])
    
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
    if 'quiz_questions' not in session or 'user_answers' not in session:
        flash('Erro: Dados do quiz não encontrados. Por favor, inicie um novo quiz.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    questions = session['quiz_questions']
    user_answers = session['user_answers']
    
    # Calculate results
    quiz_results = calculate_score(questions, user_answers)
    
    # Check if user is authenticated
    email = session.get('metadata', {}).get('email', '') if session.get('metadata') else ''
    is_authenticated = bool(email)
    
    quiz_uuid = None
    
    # Only save to file if anonymous
    if not is_authenticated:
        quiz_uuid = save_quiz_result(user_answers, questions)
        session['quiz_uuid'] = quiz_uuid
    else:
        # For authenticated users, results go to their user area
        # TODO: call insertQuizResults(email) to save in user's database
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
    """View anonymous quiz results"""
    saved_result = get_quiz_result(quiz_uuid)
    
    if not saved_result:
        flash('Quiz não encontrado ou expirou. UUID válido por 1 hora.', 'error')
        return redirect(url_for('quiz.start_quiz'))
    
    all_questions = getListOfQuestions()
    answers_by_question_number = saved_result['answers_by_question_number']
    
    # Remap answers from question_number to indices
    user_answers = {}
    for question_idx, question in enumerate(all_questions):
        question_num = question['question_number']
        if str(question_num) in answers_by_question_number:
            user_answers[str(question_idx)] = answers_by_question_number[str(question_num)]
    
    quiz_results = calculate_score(all_questions, user_answers)
    
    user = session.get('user', None)
    
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=all_questions,
        user_answers=user_answers,
        quiz_uuid=quiz_uuid,
        is_authenticated=False,  # Anonymous results never show details
        is_saved=True
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
