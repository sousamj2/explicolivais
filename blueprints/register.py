from flask import Blueprint, request, session, redirect, url_for, flash, current_app, render_template
from Funhelpers.registration_token import generate_token, confirm_token
from Funhelpers.send_email import send_email
from markupsafe import Markup

bp_register = Blueprint('register', __name__, url_prefix='/register')

@bp_register.route('/', methods=['GET', 'POST'])
def request_confirmation():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash('Please enter your email address.')
            return redirect(url_for('register.request_confirmation'))

        # Optional: Check if email is blacklisted and reject if so

        # Capture IP address for unsubscribe tracking
        ip_addr = request.remote_addr

        # Generate token for email verification
        token = generate_token(email)

        confirm_url = url_for('register.confirm_email', token=token, _external=True)
        unsubscribe_url = url_for('register.unsubscribe', email=email, ip=ip_addr, _external=True)

        subject = "Confirm your email address"
        html_message = f"""
        <p>Please confirm your email by clicking the link below:</p>
        <p><a href="{confirm_url}">{confirm_url}</a></p>
        <p>If you do not want to receive emails from us, you can unsubscribe here:</p>
        <p><a href="{unsubscribe_url}">Unsubscribe</a></p>
        <p>This confirmation link is valid for 1 hour.</p>
        """

        send_email(subject, email, html_message)

        flash('Confirmation email sent. Please check your inbox.')
        # return redirect(url_for('signin_redirect.signin_redirect'))
        return redirect(url_for('register.request_confirmation'))

    main_content_html = render_template(
        'content/request_new_user.html'
    )
    return render_template('index.html',
                            admin_email=current_app.config['ADMIN_EMAIL'],
                            user=session.get("userinfo"),
                            # metadata=session.get("metadata"),
                            page_title="Explicações em Lisboa",
                            title="Explicações em Lisboa",
                            main_content=Markup(main_content_html))

    # return render_template('content/request_new_user.html')

@bp_register.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("Invalid or expired confirmation token.")
        return redirect(url_for('register.request_confirmation'))

    # Redirect to signup page with email prefilled or in URL for completion
    return redirect(url_for('signup.signup', email=email))

@bp_register.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email')
    ip = request.args.get('ip')

    # Add logic to insert email & ip into your blacklist db or cache

    flash("You have been unsubscribed and will not receive further emails.")
    return redirect(url_for('signin.signin'))
