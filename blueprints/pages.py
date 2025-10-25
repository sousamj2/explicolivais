from flask import Blueprint, render_template, session, redirect, url_for, current_app
from markupsafe import Markup
from pprint import pprint

from Funhelpers.render_profile_template import render_profile_template

pages_bp = Blueprint('pages', __name__)


def render_page(blueprint, route="/", template_name="home", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata=None):
    def view_func():
        with open(f'templates/content/{template_name}.html', 'r', encoding='utf-8') as file:
            if route == "/maps":
                print(session.get("metadata"))
                main_content_html = render_profile_template(Markup(file.read()))
            else :
                main_content_html = Markup(file.read())
        user = session.get('user') or session.get('userinfo')
        # pprint(user)
        if not user and template_name == "profile":
            return redirect(url_for('signin.signin'))
        elif (not user or user['email'].lower() != current_app.config['ADMIN_EMAIL']) and template_name == "adminDB":
            return redirect(url_for('signin.signin'))

        if route == "/profile":
            pprint("metadata is:", metadata)

        # if template_name == "adminDB":

        return render_template(
            'index.html',
            admin_email=current_app.config['ADMIN_EMAIL'],
            user=user,
            metadata=metadata,
            page_title=page_title,
            title=title,
            main_content=main_content_html
            )
    view_func.__name__ = f'view_func_{template_name.replace("-", "_").replace("/", "_")}'
    blueprint.route(route, methods=['GET'])(view_func)
    return view_func

render_page(pages_bp,route="/"        , template_name="home"     , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(pages_bp,route="/maps"    , template_name="maps"     , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(pages_bp,route="/prices"  , template_name="prices"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(pages_bp,route="/calendar", template_name="calendar" , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(pages_bp,route="/terms"   , template_name="terms"    , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
render_page(pages_bp,route="/adminDB" , template_name="adminDB"  , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(pages_bp,route="/profile" , template_name="profile"  , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={session["metadata"]})
# render_page(pages_bp,route="/signin"  , template_name="signin"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(pages_bp,route="/signup"  , template_name="signup"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# render_page(pages_bp,route="/logout"  , template_name="logout"   , page_title="Explicações em Lisboa", title="Explicações em Lisboa",metadata={})
# The above function creates routes dynamically, so the below individual route definitions are commented out.
# They can be removed if the dynamic function works as intended.




# @app.route('/adminDB', methods=['POST'])
# def admin_db():
#     data = request.json
#     query = data.get('query')
#     if not query:
#         return jsonify({'error': 'No SQL query provided'}), 400

#     result = submit_query(query)
#     if isinstance(result, str):  # Indicates an error message
#         return jsonify({'error': result}), 400
    
#     if isinstance(result, list):
#         if len(result) > 0 and isinstance(result[0],str):
#             result = " ("+",".join(result[1:]) + ") "
#             return jsonify(result)
        
#         html_table = results_to_html_table(result)
#         # pprint(html_table)
        
#         result = {'html_table': html_table}

#     return jsonify(result)
