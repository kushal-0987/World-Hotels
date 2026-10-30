# Importing libraries for main public routes
from flask import Blueprint, render_template, current_app, send_from_directory, request, flash, redirect, url_for
import os

# Creating main blueprint - handles public pages like home, hotels, about
main_bp = Blueprint("main", __name__)


# Helper function to connect to database
def get_db_connection():
    return current_app.get_db_connection()


# Home page route - the main landing page of the website
# Shows list of all active hotels to visitors
@main_bp.route("/")
def home():
    # Get all active hotels from database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        # Get hotel name, city, capacity, and pricing information
        # Only show active hotels, sorted by city name
        cur.execute(
            "SELECT HotelName, City, CapacityRooms, PeakRateGBP, OffPeakRateGBP FROM Hotel WHERE Status = 'Active' ORDER BY City"
        )
        hotels = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    # Display home page with hotel list
    return render_template("index.html", hotels=hotels)


# Hotels listing page - shows all hotels with more details
# This is a dedicated page for browsing hotels
@main_bp.route("/hotels")
def hotels():
    # Get destination filter from query parameters (from search form)
    destination = request.args.get("destination", "").strip()
    
    # Get all active hotels with ratings included
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        # Get all cities for filter pills (always get all cities, not just filtered ones)
        cur.execute(
            "SELECT DISTINCT City FROM Hotel WHERE Status = 'Active' ORDER BY City"
        )
        all_cities = [row['City'] for row in cur.fetchall()]
        
        # Filter hotels by destination if provided
        if destination:
            # Filter by city name (case-insensitive match)
            cur.execute(
                "SELECT HotelName, City, CapacityRooms, PeakRateGBP, OffPeakRateGBP, Rating FROM Hotel WHERE Status = 'Active' AND LOWER(City) = LOWER(%s) ORDER BY City",
                (destination,)
            )
        else:
            # Get all hotels if no destination filter
            cur.execute(
                "SELECT HotelName, City, CapacityRooms, PeakRateGBP, OffPeakRateGBP, Rating FROM Hotel WHERE Status = 'Active' ORDER BY City"
            )
        hotels = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    # Display hotels page with destination filter and all cities for filter pills
    return render_template("hotels.html", hotels=hotels, destination_filter=destination, all_cities=all_cities)


# About page - shows information about World Hotels
# This is a static page with company information
@main_bp.route("/about")
def about():
    return render_template("about.html")


# Route to serve video files from Images folder
# This allows us to display videos on the website (like background videos)
@main_bp.route("/video/<filename>")
def serve_video(filename):
    # Find the Images folder in project root
    # We go up two directories from this file to reach project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    images_folder = os.path.join(project_root, "Images")
    # Try lowercase 'images' if 'Images' doesn't exist
    if not os.path.exists(images_folder):
        images_folder = os.path.join(project_root, "images")
    # Send the video file to browser
    return send_from_directory(images_folder, filename)


# Route to serve image files from Images folder
# This allows us to display images on the website
@main_bp.route("/images/<filename>")
def serve_image(filename):
    # Find the Images folder in project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    images_folder = os.path.join(project_root, "Images")
    # Try lowercase 'images' if 'Images' doesn't exist
    if not os.path.exists(images_folder):
        images_folder = os.path.join(project_root, "images")
    # Send the image file to browser
    return send_from_directory(images_folder, filename)


# Contact page - shows contact information and contact form
# Users can reach out to us through this page
@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    # If form is submitted, process the contact message
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        # For now, just show success message
        # In a real application, you would send an email or save to database
        flash(f"Thank you {name}! Your message has been received. We'll get back to you at {email} soon.")
        return redirect(url_for("main.contact"))
    
    # Display contact page
    return render_template("contact.html")


# Help page - shows frequently asked questions and help information
# Users can find answers to common questions here
@main_bp.route("/help")
def help():
    return render_template("help.html")
