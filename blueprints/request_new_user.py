from flask import Blueprint, render_template, request, redirect, url_for, flash

bp_request_new_user = Blueprint('request_new_user', __name__, url_prefix='/request_new_user')

@bp_request_new_user.route('/', methods=['GET', 'POST'])
def request_new_user():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Por favor, insira um email válido.', 'error')
            return render_template('content/request_new_user.html')
        # Here you could add logic to check if email is already registered, send a confirmation, etc.
        # For now, just redirect to /register and pass the email as a query param
        return redirect(url_for('register.register_user', email=email))
    return render_template('content/request_new_user.html')
