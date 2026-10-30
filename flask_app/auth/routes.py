import mysql.connector
import secrets
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify

from flask_mail import Message

# Try to import PIL (Python Imaging Library) for image processing
# This is used for resizing profile pictures when users upload them
# If PIL is not installed, we just skip image resizing
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Helper function to get mail instance for sending emails
# This gets the email configuration we set up in app.py
def get_mail():
    return current_app.extensions.get('mail')

# Creating auth blueprint - handles all authentication routes
# This includes login, register, logout, password reset, etc.
auth_bp = Blueprint("auth", __name__)

# Helper function to connect to database
# This ensures we always use the correct database configuration
def get_db_connection():
    return current_app.get_db_connection()


# Registration route - handles new user sign up
# When user submits the form, we create a customer record first
# then link it to the users table. This ensures data consistency.
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form.get("phone")  # optional

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Step 1: Insert into Customer table first
            # We create customer record before user account to maintain
            # proper relationship between customer and user tables.
            cur.execute(
                """
                INSERT INTO Customer (CustomerName, CustomerEmail, CustomerPhone)
                VALUES (%s, %s, %s)
                """,
                (full_name, email, phone),
            )
            customer_id = cur.lastrowid

            # Step 2: Insert into users table and link to Customer
            # This creates the actual user account that can login to the system.
            # The customer_id links user to their customer record.
            cur.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role, customer_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (full_name, email, password_hash, "user", customer_id),
            )

            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("auth.login"))

        except mysql.connector.IntegrityError:
            conn.rollback()
            flash("Email already registered.")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/register.html")


# Login route - handles user authentication
# After successful login, we send an email notification to user
# for security purposes. Admin users are redirected to admin panel
# while regular users go to home page.
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    register_hint = session.pop("show_register_hint", False)

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Use try/finally to ensure connection is always closed, even if an error occurs
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            # Use buffered cursor to prevent "Unread result found" errors
            cur = conn.cursor(dictionary=True, buffered=True)
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()

        if user and check_password_hash(user["password_hash"], password):
            # Check if user is active
            if not user.get("is_active", True):
                flash("Your account has been deactivated. Please contact support.")
                return render_template("auth/login.html", register_hint=register_hint)
            
            # store user info in session
            session["user_id"] = user["id"]
            session["role"] = user.get("role", "user")
            session["customer_id"] = user.get("customer_id")
            session["full_name"] = user.get("full_name")

            flash("Logged in successfully.")

            # Login alert email - sends notification when user logs in
            # This is a security feature to let users know if someone
            # accessed their account. If email fails, we just log it
            # but don't stop the login process.
            try:
                msg = Message(
                    subject="World Hotels login alert",
                    recipients=[user["email"]],
                )
                msg.body = (
                    f"Hello {user['full_name']},\n\n"
                    f"This is a notification that your World Hotels account "
                    f"was just logged into.\n\n"
                    f"If this was not you, please change your password."
                )
                get_mail().send(msg)
            except Exception as e:
                # If email sending fails, we just log the error
                # This way login still works even if email service is down
                print("Login email error:", e)

            # redirect based on role
            if session["role"] == "admin":
                return redirect(url_for("admin.admin_bookings"))
            
            # Check if user is new (has no bookings) - redirect to booking page
            # New users should be directed to book their first hotel
            customer_id = session.get("customer_id")
            if customer_id:
                conn_check = None
                cur_check = None
                try:
                    conn_check = get_db_connection()
                    cur_check = conn_check.cursor(dictionary=True, buffered=True)
                    cur_check.execute(
                        "SELECT COUNT(*) as booking_count FROM Booking WHERE CustomerID = %s",
                        (customer_id,)
                    )
                    booking_result = cur_check.fetchone()
                    booking_count = booking_result.get("booking_count", 0) if booking_result else 0
                    
                    # If user has no bookings, they're new - redirect to booking page
                    if booking_count == 0:
                        return redirect(url_for("booking.booking"))
                finally:
                    if cur_check:
                        cur_check.close()
                    if conn_check:
                        conn_check.close()
            
            # Existing users with bookings go to home page
            return redirect(url_for("main.home"))
        else:
            flash("Invalid email or password.")

    return render_template("auth/login.html", register_hint=register_hint)


# Logout route - clears user session and redirects to home
# This ensures that user is properly logged out and their
# session data is removed for security reasons.
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("main.home"))


# Forgot Password Route
# Allows users to request a password reset link via email
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        
        # Use try/finally to ensure connection is always closed, even if an error occurs
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            # Use buffered cursor to prevent "Unread result found" errors
            cur = conn.cursor(dictionary=True, buffered=True)
            
            # Find user by email
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            
            if user:
                # Generate token valid for 1 hour
                token = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=1)
                
                cur.execute(
                    """
                    UPDATE users
                    SET reset_token = %s,
                        reset_expires = %s
                    WHERE id = %s
                    """,
                    (token, expires, user["id"])
                )
                conn.commit()
                
                reset_link = url_for("auth.reset_password", token=token, _external=True)
                # For demo: just show the link in flash message
                flash(f"Password reset link (for demo): {reset_link}")
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        # Always show generic message
        flash("If this email exists, a reset link has been generated.")
        return redirect(url_for("auth.forgot_password"))
    
    return render_template("auth/forgot_password.html")


# Reset Password Route
# Allows users to set a new password using the reset token
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        # Find valid token (not expired)
        cur.execute(
            """
            SELECT id
            FROM users
            WHERE reset_token = %s
              AND reset_expires > NOW()
            """,
            (token,)
        )
        user = cur.fetchone()
        
        if not user:
            flash("The password reset link is invalid or has expired.")
            return redirect(url_for("auth.forgot_password"))
        
        if request.method == "POST":
            password = request.form.get("password")
            confirm = request.form.get("confirm_password")
            
            if not password or password != confirm:
                flash("Passwords do not match.")
                return render_template("auth/reset_password.html", token=token)
            
            hashed = generate_password_hash(password)
            
            # Update password and clear token
            cur.execute(
                """
                UPDATE users
                SET password_hash = %s,
                    reset_token = NULL,
                    reset_expires = NULL
                WHERE id = %s
                """,
                (hashed, user["id"])
            )
            conn.commit()
            
            flash("Your password has been reset. Please log in.")
            return redirect(url_for("auth.login"))
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("auth/reset_password.html", token=token)


# Profile Route
# Allows logged-in users to view and update their profile details
@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    """Allow a logged-in user to view and update their profile details."""
    
    # Require login
    if "user_id" not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    customer_id = session.get("customer_id")
    
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        # Handle profile update (POST)
        if request.method == "POST":
            full_name = request.form.get("full_name")
            phone = request.form.get("phone")
            
            try:
                # Update users table
                cur.execute(
                    """
                    UPDATE users
                    SET full_name = %s
                    WHERE id = %s
                    """,
                    (full_name, user_id)
                )
                
                # Update Customer table if customer_id exists
                if customer_id:
                    cur.execute(
                        """
                        UPDATE Customer
                        SET CustomerName = %s,
                            CustomerPhone = %s
                        WHERE CustomerID = %s
                        """,
                        (full_name, phone, customer_id)
                    )
                
                conn.commit()
                flash("Profile updated successfully!")
                
                # Update session
                session['full_name'] = full_name
                
            except Exception as e:
                conn.rollback()
                flash(f"Error updating profile: {str(e)}")
            
            return redirect(url_for("auth.profile"))
        
        # GET request - show profile
        # Get user info
        cur.execute(
            """
            SELECT u.*, c.CustomerName, c.CustomerEmail, c.CustomerPhone
            FROM users u
            LEFT JOIN Customer c ON u.customer_id = c.CustomerID
            WHERE u.id = %s
            """,
            (user_id,)
        )
        user_data = cur.fetchone()
        
        if not user_data:
            flash("User not found.")
            return redirect(url_for("main.home"))
        
        # Get customer data
        customer = {
            'CustomerName': user_data.get('CustomerName') or user_data.get('full_name'),
            'CustomerEmail': user_data.get('CustomerEmail') or user_data.get('email'),
            'CustomerPhone': user_data.get('CustomerPhone', ''),
            'AddressLine1': user_data.get('AddressLine1', ''),
            'AddressLine2': user_data.get('AddressLine2', ''),
            'City': user_data.get('City', ''),
            'Country': user_data.get('Country', ''),
            'Preferences': user_data.get('Preferences', '')
        }
        
        # Get booking statistics
        stats = {'total_bookings': 0, 'last_booking_date': None}
        if customer_id:
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_bookings,
                    MAX(BookingDate) as last_booking_date
                FROM Booking
                WHERE CustomerID = %s
                """,
                (customer_id,)
            )
            stats_row = cur.fetchone()
            if stats_row:
                stats['total_bookings'] = stats_row['total_bookings'] or 0
                stats['last_booking_date'] = stats_row['last_booking_date']
        
        # Additional template variables
        user_email = user_data.get('email')
        member_since = user_data.get('created_at').strftime('%B %Y') if user_data.get('created_at') else 'Recently'
        
    except Exception as e:
        flash(f"Error loading profile: {str(e)}")
        customer = None
        stats = {'total_bookings': 0, 'last_booking_date': None}
        user_email = session.get('email', '')
        member_since = 'Recently'
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("profile.html", 
                         customer=customer, 
                         user=user_data,
                         stats=stats,
                         user_email=user_email,
                         member_since=member_since)


# Profile Photo Upload Route
# Handles profile photo upload via AJAX
@auth_bp.route("/profile/upload-photo", methods=["POST"])
def upload_profile_photo():
    """Handle profile photo upload"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    if "profile_photo" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files["profile_photo"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    # Validate file type
    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
    if not (file.filename and "." in file.filename and 
            file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
        return jsonify({"success": False, "error": "Invalid file type"}), 400
    
    try:
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", "profiles")
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate secure filename
        user_id = session["user_id"]
        file_ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"profile_{user_id}_{secrets.token_hex(8)}.{file_ext}"
        filepath = os.path.join(upload_folder, filename)
        
        # Save and resize image if Pillow is available
        if HAS_PILLOW:
            img = Image.open(file.stream)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            img.save(filepath, optimize=True, quality=85)
        else:
            # Save file directly without resizing
            file.save(filepath)
        
        # Update database
        # Use try/finally to ensure connection is always closed, even if an error occurs
        photo_url = f"/static/uploads/profiles/{filename}"
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET profile_picture = %s WHERE id = %s",
                (photo_url, user_id)
            )
            conn.commit()
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        # Update session
        session["profile_picture"] = photo_url
        
        return jsonify({"success": True, "photo_url": photo_url})
        
    except Exception as e:
        print(f"Photo upload error: {e}")
        return jsonify({"success": False, "error": "Failed to upload photo"}), 500
