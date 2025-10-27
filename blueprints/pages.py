
from flask import Blueprint, render_template, session, redirect, url_for, current_app
from markupsafe import Markup
from pprint import pprint

from Funhelpers.render_profile_template import render_profile_template

# Define a blueprint for each page
bp_home = Blueprint('home', __name__, url_prefix='/')
bp_maps = Blueprint('maps', __name__, url_prefix='/maps')
bp_prices = Blueprint('prices', __name__, url_prefix='/prices')
bp_calendar = Blueprint('calendar', __name__, url_prefix='/calendar')
bp_terms = Blueprint('terms', __name__, url_prefix='/terms')
bp_adminDB = Blueprint('adminDB', __name__, url_prefix='/adminDB')

def render_page(blueprint, route="/", template_name="home", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata=None):
    def view_func():
        with open(f'templates/content/{template_name}.html', 'r', encoding='utf-8') as file:
            if template_name == "maps":
                main_content_html = render_profile_template(Markup(file.read()))
            else:
                main_content_html = Markup(file.read())
        # user = session.get('user') or session.get('userinfo')
        # pprint(user)
        user = session and session.get("metadata")
        if not user and template_name == "profile":
            return redirect(url_for('signin.signin'))
        elif (not user or 
              (session.get("metadata") and
               session.get("metadata").get('email') and
               session.get("metadata").get('email').lower() != current_app.config['ADMIN_EMAIL'])
              ) and template_name == "adminDB":
            return redirect(url_for('profile.profile'))

        print("metadata is:", session.get("metadata"))

        if route == "/profile":
            pprint("metadata is:", metadata)
        if not session.get("metadata").get('email') :
            user = None
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

# Register each page route with its blueprint
render_page(bp_home, route="/", template_name="home", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})
render_page(bp_maps, route="/", template_name="maps", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})
render_page(bp_prices, route="/", template_name="prices", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})
render_page(bp_calendar, route="/", template_name="calendar", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})
render_page(bp_terms, route="/", template_name="terms", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})
render_page(bp_adminDB, route="/", template_name="adminDB", page_title="Explicações em Lisboa", title="Explicações em Lisboa", metadata={})

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


