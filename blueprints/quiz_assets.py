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
    Serve quiz assets (images, etc.) from quiz-time folder
    Handles safe path traversal
    """
    safe = os.path.normpath(filename)
    if safe.startswith('..'):
        abort(404)
    print(f"DEBUG: Serving quiz asset: {filename} from {ASSETS_ROOT}")
    return send_from_directory(ASSETS_ROOT, safe)
