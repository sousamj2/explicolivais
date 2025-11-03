from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from Funhelpers.quiz_helpers import getListOfQuestions, calculate_score

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz')
def start_quiz():
    """Initialize a new quiz session"""
    questions = getListOfQuestions()
    
    # Initialize session variables
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
    print(f"Current question is : {current_question}")
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
        main_content=content_html  # This is already processed HTML string
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
    print(user_answers)
    # Calculate results
    quiz_results = calculate_score(questions, user_answers)
    
    # Get user info from session if needed
    user = session.get('user', None)
    
    # Render the content template first
    content_html = render_template(
        'content/quiz_results.html',
        results=quiz_results,
        questions=questions,
        user_answers=user_answers
    )
    
    # Now render the full page with the processed content
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
    
    flash('Quiz reiniciado com sucesso!', 'success')
    return redirect(url_for('quiz.start_quiz'))

