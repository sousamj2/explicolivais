from flask import Blueprint, request, session, redirect, url_for,current_app
from pprint import pprint
import bleach
from Funhelpers import check_ip_in_portugal, valid_cellphone,valid_NIF, mask_email
from DBhelpers import *
from typing import Any, Mapping, cast
from werkzeug.security import generate_password_hash
import re

bp_updateDB = Blueprint('updateDB', __name__)


@bp_updateDB.route('/updateDB', methods = ["GET","POST"])

def updateDB():
    pprint('Updating user in the database...')
    userinfo = session.get('userinfo', {})
    # pprint(userinfo)

    notes = "NA"

    # Helper: request.form.get can return None; coerce to empty string before cleaning
    def get_clean(field: str, default: str = "") -> str:
        return bleach.clean(request.form.get(field) or default)

    first_name = userinfo.get('given_name')
    if not first_name:
        first_name = get_clean('given_name')
    last_name = userinfo.get('family_name')
    if not last_name:
        last_name = get_clean('family_name')
    email = userinfo.get('email')
    if not email:
        email = get_clean('email')

    email = email.lower()

    errorMessage = ""
    username = None
    if userinfo.get('email'):
        username = email
    else:
        username = get_clean('username').lower()
        if username == email:
            pass
        elif not re.match(r'^[A-Za-z0-9._-]+$', username):
            errorMessage += "O username pode conter letras, números ou os símbolos '.' , '-' ou '_' <br> \n"
            errorMessage += "Em alternativa pode utilizar o email como username."

    h_password = None
    password = get_clean('password') or None
    if password:
        h_password = generate_password_hash(password)

    address = get_clean('address')
    number = get_clean('number') or "NA"
    floor = get_clean('floor') or "NA"
    door = get_clean('door') or "NA"
    zip_code1 = get_clean('zip_code1')
    zip_code2 = get_clean('zip_code2')
    cell_phone = get_clean('cell_phone')
    nif = get_clean('nfiscal')
    g_address = address
    if number != "NA":
        g_address = address + ", " + str(number)
    full_address = g_address
    if floor != "NA":
        full_address += ", " + str(floor)
    if door != "NA":
        full_address += " " + str(door)
    session['metadata'] = {
        'name': (first_name or "") + " " + (last_name or ""),
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'full_address': full_address,
        'g_address': g_address,
        'address': address,
        'number': number,
        'floor': floor,
        'door': door,
        'notes': notes,
        'zip_code1': str(zip_code1),
        'zip_code2': str(zip_code2),
        'zip_code': str(zip_code1) + "-" + str(zip_code2),
        'cell_phone': cell_phone,
        'nfiscal': nif
    }
    session['error_message'] = ""
    # print("------------------------------------------------")
    sameEmail = getDataFromEmail(email)
    print("sameEmail", sameEmail)
    if sameEmail:
        sameEmail_map = cast(Mapping[str, Any], sameEmail)
        errorMessage += f"Este email ({sameEmail_map.get('email','')}) já tem uma conta aqui criada em {sameEmail_map.get('createdatts','')}. <br>\n"
    register_ip = request.remote_addr
    # sameIP = getDataFromIPcreated(register_ip)
    # print("sameIP",sameIP)
    # if sameIP:
    #     errorMessage += f"Este IP ({register_ip}) já registou o email {mask_email(sameIP["email"])} em {sameIP["createdatts"]}.<br>\n"
    sameNIF = getDataFromNIF(nif)
    # print("sameNIF",sameNIF)
    if sameNIF:
        sameNIF_map = cast(Mapping[str, Any], sameNIF)
        errorMessage += f"Este NIF ({nif}) já pertence a uma conta com o email {mask_email(sameNIF_map.get('email',''))} em {sameNIF_map.get('createdatts','')}.<br>\n"
    sameCell = getDataFromCellNumber(cell_phone)
    # print("sameCell",sameCell)
    if sameCell:
        sameCell_map = cast(Mapping[str, Any], sameCell)
        errorMessage += f"Este Telemóvel ({cell_phone}) já pertence a uma conta com o email {mask_email(sameCell_map.get('email',''))} em {sameCell_map.get('createdatts','')}.<br>\n"
    if not check_ip_in_portugal(register_ip):
        # pprint(f"IP {register_ip} is not from Lisboa/Portugal.")
        errorMessage += f"Este endereço de IP {register_ip} está localizado fora de Lisboa. Tente de novo quando voltar. <br> Nota: só é necessário para o registro não para o acesso.<br>\n"
    if not valid_NIF (nif):
        errorMessage += f"Este NIF ({nif}) não é válido. <br> \n"
    if not valid_cellphone (cell_phone):
        errorMessage += f"Este telemóvel ({cell_phone}) não é válido. <br> \n"
    # print("------------------------------------------------")

    if len(errorMessage) > 0:
        session['metadata']['error_message'] = errorMessage
        print(errorMessage)
        return redirect(url_for('signup.signup',email = email))

    successUser = insertNewUser(first_name,last_name,email,h_password,username)
    successPers = insertNewPersonalData(email, address, number, floor, door, notes, zip_code1,zip_code2,cell_phone,nif)
    successIP   = insertNewIP(email,register_ip)
    successConn = insertNewConnectionData(email,register_ip)
    if successPers and successUser and successIP and successConn:

        return redirect(url_for('profile.profile'))
    else:
        return "Error registering user", 500

