from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from markupsafe import Markup
from pprint import pprint
import bleach
from werkzeug.security import generate_password_hash
from Funhelpers import valid_cellphone, valid_NIF, mask_email
from DBhelpers import insertNewPersonalData, getDataFromNIF, getDataFromCellNumber
import re

bp_elevate_tier = Blueprint('elevate_tier', __name__)

@bp_elevate_tier.route('/elevate-tier', methods=['GET', 'POST'])
def elevate_tier():
    """
    Handles the user account tier elevation process.

    On a GET request, it displays the tier upgrade form, pre-filling the user's email.
    If the user is not logged in (i.e., no email in the session), it redirects to the sign-in page.

    On a POST request, it processes the submitted form data, which includes personal information
    like address, phone number, and NIF (Portuguese tax identification number).
    The function validates the NIF and cell phone number for correctness and uniqueness in the database.
    If validation fails, it flashes an error message and redirects back to the form.
    On successful validation, it inserts the new data into the database, updates the user's tier to 2,
    refreshes the session data with the new information, and redirects to the user's profile page.
    """
    
    if request.method == 'GET':
        # Show the upgrade form
        email = session.get('metadata', {}).get('email')
        if not email:
            return redirect(url_for('signin.signin'))
        
        main_content_html = render_template(
            'content/elevate_tier.html',
            email=email,
            greeting=session.get('metadata', {}).get('greeting', '')
        )
        
        return render_template('index.html',
            admin_email=current_app.config['ADMIN_EMAIL'],
            user=session.get('userinfo'),
            metadata=session.get('metadata'),
            page_title="Elevar para Tier 2",
            title="Elevar para Tier 2",
            main_content=Markup(main_content_html))
    
    elif request.method == 'POST':
        email = session.get('metadata', {}).get('email')
        if not email:
            return redirect(url_for('signin.signin'))
        
        # Helper: clean form input
        def get_clean(field: str, default: str = "") -> str:
            """
            Retrieves and sanitizes a field from the request form.

            Args:
                field (str): The name of the form field to retrieve.
                default (str, optional): The default value to return if the field is not found. Defaults to "".

            Returns:
                str: The sanitized content of the form field.
            """
            return bleach.clean(request.form.get(field) or default)
        
        address = get_clean('address')
        number = get_clean('number') or "NA"
        floor = get_clean('floor') or "NA"
        door = get_clean('door') or "NA"
        zip_code1 = get_clean('zip_code1')
        zip_code2 = get_clean('zip_code2')
        cell_phone = get_clean('cell_phone')
        nif = get_clean('nfiscal')
        notes = "NA"
        
        errorMessage = ""
        
        # Validation
        sameNIF = getDataFromNIF(nif)
        if sameNIF:
            sameNIF_map = sameNIF
            errorMessage += f"Este NIF ({nif}) já pertence a uma conta com o email {mask_email(sameNIF_map.get('email',''))}.\n"
        
        sameCell = getDataFromCellNumber(cell_phone)
        if sameCell:
            sameCell_map = sameCell
            errorMessage += f"Este Telemóvel ({cell_phone}) já pertence a uma conta com o email {mask_email(sameCell_map.get('email',''))}.\n"
        
        if not valid_NIF(nif):
            errorMessage += f"Este NIF ({nif}) não é válido.\n"
        
        if not valid_cellphone(cell_phone):
            errorMessage += f"Este telemóvel ({cell_phone}) não é válido.\n"
        
        if len(errorMessage) > 0:
            session['metadata']['error_message'] = errorMessage
            return redirect(url_for('elevate_tier.elevate_tier'))
        
        # Insert personal data and update tier (you handle tier update on DB side)
        success = insertNewPersonalData(
            email, address, number, floor, door, notes, 
            zip_code1, zip_code2, cell_phone, nif
        )
        
        if success:
            # Update session metadata
            session['metadata'].update({
                'address': address,
                'number': number,
                'floor': floor,
                'door': door,
                'zip_code1': zip_code1,
                'zip_code2': zip_code2,
                'cell_phone': cell_phone,
                'nfiscal': nif,
                'tier': 2
            })
            session.modified = True
            return redirect(url_for('profile.profile'))
        else:
            session['metadata']['error_message'] = "Erro ao atualizar a base de dados."
            return redirect(url_for('elevate_tier.elevate_tier'))
