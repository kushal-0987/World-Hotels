
# ==========================================
# 1. IMPORT LIBRARIES
# ==========================================

import os
import time

import mysql.connector
from mysql.connector import pooling

from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv


# ==========================================
# 2. LOAD ENVIRONMENT VARIABLES
# ==========================================

# Load .env from the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


# ==========================================
# 3. CREATE FLASK APPLICATION
# ==========================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==========================================
# 4. FLASK SECURITY CONFIGURATION
# ==========================================

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")


# ==========================================
# 5. EMAIL CONFIGURATION
# ==========================================

mail = Mail()

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_SUPPRESS_SEND"] = False
app.config["TESTING"] = False
app.config["DEBUG"] = (
    os.getenv("FLASK_DEBUG", "false").lower() == "true"
)

mail.init_app(app)


# ==========================================
# 6. DATABASE CONFIGURATION
# ==========================================

_db_config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "world_hotels"),
    "auth_plugin": "mysql_native_password",
    "connection_timeout": 10,
}

if not _db_config["password"]:
    raise RuntimeError("DB_PASSWORD is missing from .env")


# ==========================================
# 7. DATABASE CONNECTION POOL
# ==========================================

_db_pool = None
_use_pooling = True


def get_db_connection():
    """
    Get a database connection from the connection pool.

    If the pool is unavailable or exhausted, create a
    direct database connection with retry logic.

    Always close database connections after using them.
    """

    global _db_pool, _use_pooling

    # Create the connection pool if it does not exist
    if _db_pool is None and _use_pooling:
        try:
            _db_pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=1,
                pool_reset_session=True,
                **_db_config
            )

        except mysql.connector.Error:
            # Disable pooling if pool creation fails
            _use_pooling = False
            _db_pool = None

    # Try to get a connection from the pool
    if _db_pool is not None:
        try:
            return _db_pool.get_connection()

        except pooling.PoolError:
            # Pool is exhausted, use direct connection
            pass

    # Direct connection with retry logic
    max_retries = 5
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            return mysql.connector.connect(**_db_config)

        except mysql.connector.errors.OperationalError as e:

            error_str = str(e)

            # Retry if the server has too many connections
            if "1040" in error_str or "Too many connections" in error_str:

                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    time.sleep(wait_time)
                    continue

                raise Exception(
                    "Database server is busy with too many connections. "
                    "Please wait a few moments and refresh the page."
                ) from e

            # Raise other database errors immediately
            raise

    raise Exception(
        "Failed to connect to database after multiple attempts."
    )


# Make the database connection function available
# to other parts of the application
app.get_db_connection = get_db_connection


# ==========================================
# 8. DATABASE CLEANUP
# ==========================================

@app.teardown_appcontext
def close_db(error):
    """
    Safety-net cleanup handler.

    Database connections should still be closed explicitly
    inside routes using try/finally blocks.
    """
    pass


# ==========================================
# 9. IMPORT ROUTE BLUEPRINTS
# ==========================================

from flask_app.main.routes import main_bp
from flask_app.auth.routes import auth_bp
from flask_app.booking.routes import booking_bp
from flask_app.admin.routes import admin_bp


# ==========================================
# 10. REGISTER BLUEPRINTS
# ==========================================

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)


# ==========================================
# 11. RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
