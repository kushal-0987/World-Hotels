
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

# Load .env from the project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def create_app():
    """
    Flask application factory pattern.
    Database connection is defined in app.py.
    """
    app = Flask(__name__)

    secret_key = os.getenv("FLASK_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

    app.config["SECRET_KEY"] = secret_key

    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .booking.routes import booking_bp
    from .admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    return app

