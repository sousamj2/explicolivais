from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    current_app,
    flash, # Import flash
)
from markupsafe import Markup
from pprint import pprint
from math import ceil

from DBhelpers import (
    get_user_profile_tier1,
    get_user_profile_tier2,
    get_quiz_history_for_user,
)
from Funhelpers import get_lisbon_greeting
from Funhelpers.claim_quiz import claim_anonymous_quiz # Import claim_anonymous_quiz

bp_profile = Blueprint("profile", __name__, url_prefix="/profile")


# Register the custom filter
@bp_profile.app_template_filter()
def format_data(value):
    from Funhelpers.format_data import format_data as f_data

    return f_data(value)


@bp_profile.route("/")
def profile():
    """
    Renders the user's profile page with content tailored to their account tier.

    This function first ensures that the user is logged in by checking for session metadata.
    If the user is not authenticated, they are redirected to the sign-in page.

    The function retrieves the user's profile information from the database. The level of detail
    depends on the user's tier:
    - Tier 1: Basic profile information.
    - Tier 2: Includes additional details such as a full address.

    After fetching the data, it is processed and formatted for display (e.g., constructing a
    full name and address). Finally, it renders the 'profile.html' template with the
    retrieved information and embeds it within the main 'index.html' layout. The content
    displayed on the profile page is conditionally rendered based on the user's tier.
    """
    source_method = request.args.get("source_method", "GET")
    email = None
    mypict = ""

    if session and session.get("metadata"):
        email = session.get("metadata").get("email")
    else:
        return redirect(url_for("signin.signin"))

    if session and session.get("userinfo"):
        mypict = session.get("userinfo").get("picture", "")

    if email:
        pprint("Rendering profile page...")

        # Get full profile from DB
        session["metadata"] = get_user_profile_tier1(email)
        # GET USER TIER FROM DATABASE - critical for conditional rendering
        user_tier = session["metadata"].get("tier", 1)  # Default to tier 1
        full_address = None
        zip_full = None

        if user_tier > 1:
            session["metadata"] = get_user_profile_tier2(email)
            # Build address
            g_address = session["metadata"]["address"]
            if session["metadata"]["number"] != "NA":
                g_address = (
                    session["metadata"]["address"]
                    + ", "
                    + str(session["metadata"]["number"])
                )
            full_address = g_address
            if session["metadata"]["floor"] != "NA":
                full_address = full_address + " " + str(session["metadata"]["floor"])
            if session["metadata"]["door"] != "NA":
                full_address = full_address + " " + str(session["metadata"]["door"])
            session["metadata"]["full_address"] = full_address
            session["metadata"]["g_address"] = g_address
            zip_full = (
                str(session["metadata"].get("zip_code1", ""))
                + "-"
                + str(session["metadata"].get("zip_code2", ""))
            )

        session["metadata"]["full_name"] = (
            session["metadata"]["first_name"] + " " + session["metadata"]["last_name"]
        )
        session["metadata"]["greeting"] = get_lisbon_greeting()
        # pprint(session)
        # print()

        # --- Claim anonymous quiz if present in session ---
        quiz_uuid_to_claim = session.pop('pending_quiz_uuid', None)
        if quiz_uuid_to_claim:
            quiz_config = session.pop('quiz_config', {})
            question_ids = session.pop('question_ids', [])
            user_answers = session.pop('user_answers', {})

            if claim_anonymous_quiz(email, quiz_uuid_to_claim, quiz_config, question_ids, user_answers):
                flash('O quiz que realizou anonimamente foi adicionado ao seu histórico!', 'success')
            else:
                flash('Não foi possível associar o quiz que realizou anonimamente.', 'warning')
        # --- End Claim anonymous quiz logic ---

        # Fetch quiz history for the user
        quiz_history_raw = get_quiz_history_for_user(email)
        # print("quiz_history_raw:", quiz_history_raw)
        quiz_history = []
        if isinstance(quiz_history_raw, list):
            # Filter out any non-dictionary items just in case
            quiz_history = [item for item in quiz_history_raw if isinstance(item, dict)]
            # print("quiz_history:", quiz_history)
            # if len(quiz_history) != len(quiz_history_raw):
                # print(f"WARNING: Filtered out non-dictionary items from quiz_history.")
        # else:
            # print(f"WARNING: quiz_history was not a list, but type {type(quiz_history_raw)}. Forcing to empty list.")
            # quiz_history is already []

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = 10
        total_items = len(quiz_history)
        total_pages = ceil(total_items / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_quiz_history = quiz_history[start:end]


        # Render content template with tier information
        main_content_html = render_template(
            "content/profile.html",
            greeting=session["metadata"]["greeting"],
            full_name=session["metadata"].get("full_name", ""),
            email=session["metadata"].get("email", ""),
            lastlogin=format_data(session["metadata"].get("lastlogints", "")),
            user_picture=mypict,
            morada=session["metadata"].get("full_address", ""),
            codigopostal=zip_full,
            nif=session["metadata"].get("nfiscal", ""),
            telemovel=session["metadata"].get("cell_phone", ""),
            tier=user_tier,  # Pass tier to template
            vpn_check_color="green",
            primeiro_contacto_color="yellow",
            primeira_aula_color="red",
            quiz_history=paginated_quiz_history,
            page=page,
            total_pages=total_pages,
        )

        return render_template(
            "index.html",
            admin_email=current_app.config["ADMIN_EMAIL"],
            user=session.get("userinfo"),
            metadata=session.get("metadata"),
            page_title="Explicações em Lisboa",
            title="Explicações em Lisboa",
            main_content=Markup(main_content_html),
        )

    else:
        return redirect(url_for("index"))
