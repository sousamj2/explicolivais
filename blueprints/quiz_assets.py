"""
Blueprint for serving quiz assets (images, etc.)
Handles both development (local files) and production (CDN/remote URLs)
"""

from flask import Blueprint, send_from_directory, abort
import os

quiz_assets_bp = Blueprint('quiz_assets', __name__, url_prefix='')

# Get the root directory where quiz-time folder is located
ASSETS_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quiz-time')

@quiz_assets_bp.route('/quiz-time/<path:filename>')
def serve_quiz_asset(filename):
    """
    Serves static assets for the quiz, such as images, from the 'quiz-time' directory.

    This function is responsible for delivering quiz-related static files. It ensures safe
    file access by normalizing the requested path and checking for directory traversal
    sequences ('..'). If a traversal attempt is detected, it aborts the request with a 404
    error.

    Args:
        filename (str): The path to the asset within the 'quiz-time' directory.

    Returns:
        The requested file using Flask's `send_from_directory`, or a 404 error if the
        path is unsafe.
    """
    safe = os.path.normpath(filename)
    if safe.startswith('..'):
        abort(404)
    # print(f"DEBUG: Serving quiz asset: {filename} from {ASSETS_ROOT}")
    return send_from_directory(ASSETS_ROOT, safe)
