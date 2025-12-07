from .check_ip_in_portugal import check_ip_in_portugal
from .format_data import format_data
from .get_lisbon_greeting import get_lisbon_greeting
from .mask_email import mask_email
from .render_profile_template import render_profile_template
from .results_to_html_table import results_to_html_table
from .valid_nif import valid_NIF
from .valid_phone import valid_cellphone
from .extensions import mail
from .send_email import send_email

from .quizFunctions import (
    score_counts,
    score_points_total,
)

from .quiz_storage import (
    save_quiz_history_for_user,
)

__all__ = [
    "check_ip_in_portugal",
    "format_data",
    "get_lisbon_greeting",
    "mask_email",
    "render_profile_template",
    "results_to_html_table",
    "valid_NIF",
    "valid_cellphone",
    "mail",
    "send_email",
    "score_counts",
    "score_points_total",
    "save_quiz_history_for_user",
]