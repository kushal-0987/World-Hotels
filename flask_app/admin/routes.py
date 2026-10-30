# Importing all necessary libraries for admin functionality
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, session, current_app, request, jsonify
)
from datetime import datetime, timedelta, date
from functools import wraps  # For creating decorators
import random  # For randomly assigning room images
import os

# Creating admin blueprint - all admin routes will start with /admin
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Helper function to get database connection
# This connects us to the MySQL database where all data is stored
def get_db_connection():
    return current_app.get_db_connection()


# Decorator function to protect admin routes
# This checks if the logged in user is an admin before allowing access
# If not admin, it redirects them to home page
def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access only.")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function


# Function to automatically assign room images when room goes under maintenance
# It picks from rooms-1.jpg to rooms-15.jpg and tries to use unused images first
# If all images are used, it randomly picks one (allows reuse)
def get_unused_room_image(cur):
    # List of all available room images we have
    available_images = [f"rooms-{i}.jpg" for i in range(1, 16)]
    
    # First check if the Image column exists in Room table
    # This prevents errors if database schema is old
    cur.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = 'Room' 
          AND COLUMN_NAME = 'Image'
    """)
    has_image_column = cur.fetchone() is not None
    
    # If column doesn't exist, just return random image
    if not has_image_column:
        return random.choice(available_images)
    
    # Get all images that are currently being used in the database
    cur.execute("SELECT DISTINCT Image FROM Room WHERE Image IS NOT NULL AND Image != ''")
    used_images = {row["Image"] for row in cur.fetchall() if row["Image"]}
    
    # Find images that haven't been used yet
    unused_images = [img for img in available_images if img not in used_images]
    
    # If we have unused images, pick one randomly
    # Otherwise, all images are used so we reuse one randomly
    if unused_images:
        return random.choice(unused_images)
    else:
        return random.choice(available_images)


# Admin page to view all bookings
# Shows list of all bookings with customer name, hotel, dates, and status
@admin_bp.route("/bookings")
def admin_bookings():
    # Security check - only admins can access this page
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("main.home"))

    # Connect to database and get all bookings
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Query to get all bookings with customer and hotel information
        # We join Booking with Customer and Hotel tables to get complete details
        # Order by most recent bookings first
        cur.execute(
            """
            SELECT
                b.BookingID,
                CONCAT('W_H-', b.BookingYear, '-', b.BookingID) AS BookingCode,
                c.CustomerName,
                h.City,
                b.CheckInDate,
                b.CheckOutDate,
                b.Nights,
                b.NumRooms,
                b.TotalPriceGBP,
                b.BookingStatus
            FROM Booking b
            JOIN Customer c ON b.CustomerID = c.CustomerID
            JOIN Hotel h ON b.HotelID = h.HotelID
            ORDER BY b.BookingDate DESC, b.BookingID DESC
            """
        )
        bookings = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    # Display the bookings list page
    return render_template("admin/admin_bookings.html", bookings=bookings)


# Route to update booking status (like Pending, Confirmed, Cancelled)
# Admin can change the status of any booking from the bookings list
@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
def update_booking_status(booking_id):
    # Security check
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("main.home"))

    # Get the new status from the form (what admin selected)
    new_status = request.form.get("status")
    if not new_status:
        flash("No status selected.")
        return redirect(url_for("admin.admin_bookings"))

    # Update the booking status in database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Change the booking status to the new value
        cur.execute(
            "UPDATE Booking SET BookingStatus = %s WHERE BookingID = %s",
            (new_status, booking_id)
        )
        conn.commit()  # Save changes to database
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Show success message and go back to bookings list
    flash(f"Booking {booking_id} status updated to {new_status}.")
    return redirect(url_for("admin.admin_bookings"))

# Admin can view receipt for any booking
# This shows the full booking details and payment information
@admin_bp.route("/bookings/<int:booking_id>/receipt")
def admin_receipt(booking_id):
    # Security check
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("main.home"))

    # Get booking details from database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Query to get all booking information including hotel details
        # This includes prices, dates, discounts, cancellation charges etc
        cur.execute(
            """
            SELECT
                b.BookingID,
                CONCAT('W_H-', b.BookingYear, '-', b.BookingID) AS BookingCode,
                h.HotelName,
                h.City,
                b.CheckInDate,
                b.CheckOutDate,
                b.Nights,
                b.NumRooms,
                b.NumGuests,
                b.CalculatedNightlyRate,
                b.AdvanceDays,
                b.AdvanceDiscountPercent,
                b.TotalPriceGBP,
                b.BookingStatus,
                b.CancellationChargeGBP
            FROM Booking b
            JOIN Hotel h ON b.HotelID = h.HotelID
            WHERE b.BookingID = %s
            """,
            (booking_id,),
        )
        booking = cur.fetchone()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # If booking doesn't exist, show error
    if not booking:
        flash("Receipt not found for this booking.")
        return redirect(url_for("admin.admin_bookings"))
    
    # Display the receipt page with booking details
    return render_template("receipt.html", booking=booking)


# Admin reports page - shows sales statistics and booking analytics
# Helps admin understand business performance
@admin_bp.route("/reports")
def admin_reports():
    # Security check
    if session.get("role") != "admin":
        flash("Admin access only.")
        return redirect(url_for("main.home"))

    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Get monthly sales report - total revenue and number of bookings per month
        # This helps see which months are busiest
        cur.execute(
            """
            SELECT
                DATE_FORMAT(BookingDate, '%%Y-%%m') AS YearMonth,
                SUM(TotalPriceGBP) AS TotalSales,
                COUNT(*) AS NumBookings
            FROM Booking
            GROUP BY DATE_FORMAT(BookingDate, '%%Y-%%m')
            ORDER BY YearMonth
            """
        )
        monthly_sales = cur.fetchall()

        # Get statistics for each hotel - how many bookings and total sales
        # Also calculates estimated profit (70% of sales is profit estimate)
        cur.execute(
            """
            SELECT
                h.City,
                h.HotelName,
                COUNT(b.BookingID) AS NumBookings,
                COALESCE(SUM(b.TotalPriceGBP), 0) AS TotalSales,
                COALESCE(SUM(b.TotalPriceGBP), 0) * 0.7 AS EstimatedProfit
            FROM Hotel h
            LEFT JOIN Booking b ON b.HotelID = h.HotelID
            GROUP BY h.HotelID, h.City, h.HotelName
            ORDER BY NumBookings DESC
            """
        )

        hotel_stats = cur.fetchall()

        # Get top customers by total bookings and revenue
        # Shows which customers have made the most bookings and spent the most money
        cur.execute(
            """
            SELECT
                c.CustomerID,
                c.CustomerName,
                c.CustomerEmail,
                COUNT(b.BookingID) AS TotalBookings,
                COALESCE(SUM(b.TotalPriceGBP), 0) AS TotalSpent
            FROM Customer c
            LEFT JOIN Booking b ON c.CustomerID = b.CustomerID
            GROUP BY c.CustomerID, c.CustomerName, c.CustomerEmail
            HAVING TotalBookings > 0
            ORDER BY TotalSpent DESC
            LIMIT 10
            """
        )
        top_customers = cur.fetchall()

        # Calculate profit vs loss per hotel
        # Assumes cost is 30% of revenue (operating costs), profit is 70% of revenue
        # Hotels with positive profit are marked as "Profit", others as "Loss"
        cur.execute(
            """
            SELECT
                h.HotelID,
                h.HotelName,
                h.City,
                COALESCE(SUM(b.TotalPriceGBP), 0) AS TotalRevenue,
                COALESCE(SUM(b.TotalPriceGBP), 0) * 0.3 AS EstimatedCost,
                COALESCE(SUM(b.TotalPriceGBP), 0) * 0.7 AS EstimatedProfit,
                CASE 
                    WHEN COALESCE(SUM(b.TotalPriceGBP), 0) * 0.7 > 0 THEN 'Profit'
                    ELSE 'Loss'
                END AS Status
            FROM Hotel h
            LEFT JOIN Booking b ON h.HotelID = b.HotelID
            GROUP BY h.HotelID, h.HotelName, h.City
            ORDER BY EstimatedProfit DESC
            """
        )
        profit_loss_hotels = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Display reports page with monthly sales, hotel statistics, top customers, and profit/loss analysis
    return render_template(
        "admin/admin_reports.html",
        monthly_sales=monthly_sales,
        hotel_stats=hotel_stats,
        top_customers=top_customers,
        profit_loss_hotels=profit_loss_hotels,
    )


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute(
            "SELECT COALESCE(SUM(TotalPriceGBP), 0) AS revenue FROM Booking WHERE DATE(BookingDate) = CURDATE()"
        )
        today_revenue = cur.fetchone()["revenue"]
        
        cur.execute(
            "SELECT COUNT(*) AS count FROM Booking"
        )
        total_bookings = cur.fetchone()["count"]
        
        cur.execute(
            "SELECT COUNT(*) AS count FROM Booking WHERE BookingStatus IN ('Pending', 'Confirmed')"
        )
        active_bookings = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) AS count FROM Booking WHERE BookingStatus = 'Pending'")
        pending_bookings = cur.fetchone()["count"]
        
        cur.execute(
            """
            SELECT
                b.BookingID,
                CONCAT('W_H-', b.BookingYear, '-', b.BookingID) AS BookingCode,
                c.CustomerName,
                h.HotelName,
                h.City,
                b.CheckInDate,
                b.CheckOutDate,
                b.Nights,
                b.NumRooms,
                b.NumGuests,
                b.TotalPriceGBP,
                b.BookingStatus
            FROM Booking b
            JOIN Customer c ON b.CustomerID = c.CustomerID
            JOIN Hotel h ON b.HotelID = h.HotelID
            ORDER BY b.BookingDate DESC
            LIMIT 10
            """
        )
        recent_bookings = cur.fetchall()
        
        # Upcoming check-ins
        cur.execute(
            """
            SELECT
                b.BookingID,
                c.CustomerName,
                h.HotelName,
                h.City,
                b.CheckInDate,
                b.NumRooms,
                b.NumGuests
            FROM Booking b
            JOIN Customer c ON b.CustomerID = c.CustomerID
            JOIN Hotel h ON b.HotelID = h.HotelID
            WHERE b.CheckInDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            AND b.BookingStatus IN ('Pending', 'Confirmed')
            ORDER BY b.CheckInDate ASC
            LIMIT 5
            """
        )
        upcoming_checkins = cur.fetchall()
        
        # Upcoming check-outs
        cur.execute(
            """
            SELECT
                b.BookingID,
                c.CustomerName,
                h.HotelName,
                h.City,
                b.CheckOutDate,
                b.NumRooms,
                b.TotalPriceGBP
            FROM Booking b
            JOIN Customer c ON b.CustomerID = c.CustomerID
            JOIN Hotel h ON b.HotelID = h.HotelID
            WHERE b.CheckOutDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            AND b.BookingStatus IN ('Confirmed', 'Checked-in')
            ORDER BY b.CheckOutDate ASC
            LIMIT 5
            """
        )
        upcoming_checkouts = cur.fetchall()
        
        # Revenue chart data (last 30 days)
        revenue_data = []
        revenue_labels = []
        for i in range(29, -1, -1):
            day = date.today() - timedelta(days=i)
            cur.execute(
                "SELECT COALESCE(SUM(TotalPriceGBP), 0) AS revenue FROM Booking WHERE DATE(BookingDate) = %s",
                (day,)
            )
            revenue_data.append(float(cur.fetchone()["revenue"]))
            revenue_labels.append(day.strftime("%d %b"))
            revenue_labels.append(day.strftime("%d %b"))
        
        # Hotel revenue
        cur.execute(
            """
            SELECT
                h.HotelName,
                COALESCE(SUM(b.TotalPriceGBP), 0) AS revenue
            FROM Hotel h
            LEFT JOIN Booking b ON h.HotelID = b.HotelID
            GROUP BY h.HotelID, h.HotelName
            ORDER BY revenue DESC
            LIMIT 8
            """
        )
        hotel_revenue_data = cur.fetchall()
        hotel_names = [h["HotelName"] for h in hotel_revenue_data]
        hotel_revenues = [float(h["revenue"]) for h in hotel_revenue_data]
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template(
        "admin/dashboard.html",
        today_revenue=today_revenue,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        pending_bookings=pending_bookings,
        recent_bookings=recent_bookings,
        upcoming_checkins=upcoming_checkins,
        upcoming_checkouts=upcoming_checkouts,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data,
        hotel_names=hotel_names,
        hotel_revenues=hotel_revenues
    )


@admin_bp.route("/hotels")
@admin_required
def hotels():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("SELECT * FROM Hotel ORDER BY HotelName")
        hotels_list = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/hotels.html", hotels=hotels_list)


@admin_bp.route("/hotels/add", methods=["GET", "POST"])
@admin_required
def add_hotel():
    if request.method == "POST":
        # Get form data
        hotel_name = request.form.get("hotel_name")
        city = request.form.get("city")
        capacity_rooms = int(request.form.get("capacity_rooms"))
        peak_rate = float(request.form.get("peak_rate"))
        off_peak_rate = float(request.form.get("off_peak_rate"))
        rating = float(request.form.get("rating"))
        status = request.form.get("status", "Active")
        description = request.form.get("description")
        image_url = request.form.get("image_url")
        
        # Use try/finally to ensure connection is always closed, even if an error occurs
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Insert new hotel
            cur.execute(
                """
                INSERT INTO Hotel (HotelName, City, CapacityRooms, PeakRateGBP, 
                                   OffPeakRateGBP, Rating, Status, Description, ImageURL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (hotel_name, city, capacity_rooms, peak_rate, off_peak_rate, 
                 rating, status, description, image_url)
            )
            conn.commit()
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        flash(f"Hotel '{hotel_name}' added successfully!")
        return redirect(url_for("admin.hotels"))
    
    return render_template("admin/hotel_form.html", hotel=None)


@admin_bp.route("/hotels/<int:hotel_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_hotel(hotel_id):
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        if request.method == "POST":
            # Get form data
            hotel_name = request.form.get("hotel_name")
            city = request.form.get("city")
            capacity_rooms = int(request.form.get("capacity_rooms"))
            peak_rate = float(request.form.get("peak_rate"))
            off_peak_rate = float(request.form.get("off_peak_rate"))
            rating = float(request.form.get("rating"))
            status = request.form.get("status")
            description = request.form.get("description")
            image_url = request.form.get("image_url")
            
            # Update hotel
            cur.execute(
                """
                UPDATE Hotel 
                SET HotelName = %s, City = %s, CapacityRooms = %s, 
                    PeakRateGBP = %s, OffPeakRateGBP = %s, Rating = %s, 
                    Status = %s, Description = %s, ImageURL = %s
                WHERE HotelID = %s
                """,
                (hotel_name, city, capacity_rooms, peak_rate, off_peak_rate, 
                 rating, status, description, image_url, hotel_id)
            )
            conn.commit()
            
            flash(f"Hotel '{hotel_name}' updated successfully!")
            return redirect(url_for("admin.hotels"))
        
        cur.execute("SELECT * FROM Hotel WHERE HotelID = %s", (hotel_id,))
        hotel = cur.fetchone()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    if not hotel:
        flash("Hotel not found.")
        return redirect(url_for("admin.hotels"))
    
    return render_template("admin/hotel_form.html", hotel=hotel)


@admin_bp.route("/rooms")
@admin_required
def rooms():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'Room' 
              AND COLUMN_NAME = 'Image'
        """)
        has_image_column = cur.fetchone() is not None
        
        if has_image_column:
            cur.execute("""
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    r.Image,
                    r.BasePricePerNight,
                    r.RoomStatus,
                    h.HotelName,
                    h.City,
                    rt.RoomTypeName
                FROM Room r
                JOIN Hotel h ON r.HotelID = h.HotelID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                ORDER BY h.HotelName, r.RoomNumber
            """)
        else:
            cur.execute("""
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    NULL as Image,
                    r.BasePricePerNight,
                    r.RoomStatus,
                    h.HotelName,
                    h.City,
                    rt.RoomTypeName
                FROM Room r
                JOIN Hotel h ON r.HotelID = h.HotelID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                ORDER BY h.HotelName, r.RoomNumber
            """)
        rooms_list = cur.fetchall()
        
        # Get hotels list for bulk room creation
        cur.execute("SELECT HotelID, HotelName, City, CapacityRooms FROM Hotel WHERE Status = 'Active' ORDER BY HotelName")
        hotels = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/rooms.html", rooms=rooms_list, hotels=hotels)


@admin_bp.route("/rooms/bulk_create", methods=["POST"])
@admin_required
def bulk_create_rooms():
    # Bulk create rooms with correct distribution (30% Standard, 50% Double, 20% Family)
    # This route allows admin to create rooms for a hotel following the distribution rule
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True, buffered=True)
        
        hotel_id = int(request.form.get("hotel_id"))
        total_rooms_str = request.form.get("total_rooms", "").strip()
        
        # Get hotel capacity to use as total rooms if not specified
        cur.execute("SELECT CapacityRooms FROM Hotel WHERE HotelID = %s", (hotel_id,))
        hotel = cur.fetchone()
        if not hotel:
            flash("Hotel not found.")
            return redirect(url_for("admin.rooms"))
        
        # Use hotel capacity if total_rooms not provided, otherwise use provided value
        if total_rooms_str:
            total_rooms = int(total_rooms_str)
        else:
            total_rooms = hotel["CapacityRooms"]
        
        # Call stored procedure to create rooms with distribution
        # MySQL connector requires calling procedure with CALL statement
        cur.execute("CALL CreateRoomsWithDistribution(%s, %s)", (hotel_id, total_rooms))
        
        # Fetch result from procedure
        result = cur.fetchone()
        if result:
            flash(f"Rooms created successfully: {result.get('Result', 'Rooms created')}")
        else:
            flash("Rooms created successfully!")
        
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error creating rooms: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return redirect(url_for("admin.rooms"))


@admin_bp.route("/rooms/add", methods=["GET", "POST"])
@admin_required
def add_room():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        if request.method == "POST":
            hotel_id = int(request.form.get("hotel_id"))
            room_number = request.form.get("room_number")
            room_type_id = int(request.form.get("room_type_id"))
            price_per_night = float(request.form.get("price_per_night"))
            status = request.form.get("status", "Available")
            image = None
            if status == "Under Maintenance":
                image = get_unused_room_image(cur)
            
            try:
                cur.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = 'Room' 
                      AND COLUMN_NAME = 'Image'
                """)
                has_image_column = cur.fetchone() is not None
                
                if has_image_column:
                    cur.execute("""
                        INSERT INTO Room (HotelID, RoomNumber, RoomTypeID, BasePricePerNight, RoomStatus, Image)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (hotel_id, room_number, room_type_id, price_per_night, status, image))
                else:
                    cur.execute("""
                        INSERT INTO Room (HotelID, RoomNumber, RoomTypeID, BasePricePerNight, RoomStatus)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (hotel_id, room_number, room_type_id, price_per_night, status))
                conn.commit()
                flash(f"Room {room_number} added successfully!")
                return redirect(url_for("admin.rooms"))
            except Exception as e:
                conn.rollback()
                flash(f"Error adding room: {str(e)}")
        
        cur.execute("SELECT HotelID, HotelName, City FROM Hotel ORDER BY HotelName")
        hotels = cur.fetchall()
        
        cur.execute("SELECT RoomTypeID, RoomTypeName FROM RoomType ORDER BY RoomTypeID")
        room_types = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/room_form.html", room=None, hotels=hotels, room_types=room_types)


@admin_bp.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_room(room_id):
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        if request.method == "POST":
            hotel_id = int(request.form.get("hotel_id"))
            room_number = request.form.get("room_number")
            room_type_id = int(request.form.get("room_type_id"))
            price_per_night = float(request.form.get("price_per_night"))
            status = request.form.get("status")
            
            old_status = None
            old_image = None
            cur.execute("SELECT RoomStatus, Image FROM Room WHERE RoomID = %s", (room_id,))
            old_room = cur.fetchone()
            if old_room:
                old_status = old_room["RoomStatus"]
                old_image = old_room.get("Image")
            image = old_image
            if status == "Under Maintenance" and old_status != "Under Maintenance":
                image = get_unused_room_image(cur)
            elif status != "Under Maintenance" and old_status == "Under Maintenance":
                image = None
            
            try:
                cur.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = 'Room' 
                      AND COLUMN_NAME = 'Image'
                """)
                has_image_column = cur.fetchone() is not None
                
                if has_image_column:
                    cur.execute("""
                        UPDATE Room 
                        SET HotelID = %s, RoomNumber = %s, RoomTypeID = %s, 
                            BasePricePerNight = %s, RoomStatus = %s, Image = %s
                        WHERE RoomID = %s
                    """, (hotel_id, room_number, room_type_id, price_per_night, status, image, room_id))
                else:
                    cur.execute("""
                        UPDATE Room 
                        SET HotelID = %s, RoomNumber = %s, RoomTypeID = %s, 
                            BasePricePerNight = %s, RoomStatus = %s
                        WHERE RoomID = %s
                    """, (hotel_id, room_number, room_type_id, price_per_night, status, room_id))
                conn.commit()
                
                if status == "Under Maintenance" and old_status != "Under Maintenance":
                    cur.execute("""
                        INSERT INTO Maintenance (RoomID, HotelID, Title, MaintenanceStatus, ScheduledStartDate, CreatedBy)
                        VALUES (%s, %s, %s, 'In Progress', NOW(), %s)
                    """, (room_id, hotel_id, f"Maintenance for Room {room_number}", session.get("user_id")))
                    conn.commit()
                elif status == "Available" and old_status == "Under Maintenance":
                    cur.execute("""
                        UPDATE Maintenance 
                        SET MaintenanceStatus = 'Completed', ActualEndDate = NOW()
                        WHERE RoomID = %s AND MaintenanceStatus = 'In Progress'
                    """, (room_id,))
                    conn.commit()
                
                flash(f"Room {room_number} updated successfully!")
                return redirect(url_for("admin.rooms"))
            except Exception as e:
                conn.rollback()
                flash(f"Error updating room: {str(e)}")
        
        cur.execute("""
            SELECT r.*, h.HotelName, h.City, rt.RoomTypeName
            FROM Room r
            JOIN Hotel h ON r.HotelID = h.HotelID
            JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
            WHERE r.RoomID = %s
        """, (room_id,))
        room = cur.fetchone()
        
        if not room:
            flash("Room not found.")
            return redirect(url_for("admin.rooms"))
        
        cur.execute("SELECT HotelID, HotelName, City FROM Hotel ORDER BY HotelName")
        hotels = cur.fetchall()
        
        cur.execute("SELECT RoomTypeID, RoomTypeName FROM RoomType ORDER BY RoomTypeID")
        room_types = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/room_form.html", room=room, hotels=hotels, room_types=room_types)


@admin_bp.route("/customers")
@admin_required
def customers():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("""
            SELECT 
                c.*,
                COUNT(b.BookingID) as booking_count
            FROM Customer c
            LEFT JOIN Booking b ON c.CustomerID = b.CustomerID
            GROUP BY c.CustomerID
            ORDER BY c.CustomerName
        """)
        customers_list = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/customers.html", customers=customers_list)


@admin_bp.route("/maintenance")
@admin_required
def maintenance():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'Room' 
              AND COLUMN_NAME = 'Image'
        """)
        has_image_column = cur.fetchone() is not None
        
        if has_image_column:
            cur.execute("""
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    r.Image,
                    r.RoomStatus,
                    r.MaintenanceReason,
                    r.MaintenanceEstimatedCompletion,
                    h.HotelName,
                    h.City,
                    rt.RoomTypeName,
                    m.MaintenanceID,
                    m.MaintenanceStatus,
                    m.ScheduledStartDate,
                    m.ScheduledEndDate,
                    m.Title,
                    m.Description
                FROM Room r
                JOIN Hotel h ON r.HotelID = h.HotelID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                LEFT JOIN Maintenance m ON r.RoomID = m.RoomID AND m.MaintenanceStatus IN ('Scheduled', 'In Progress')
                WHERE r.RoomStatus = 'Under Maintenance'
                ORDER BY h.HotelName, r.RoomNumber
            """)
        else:
            cur.execute("""
                SELECT 
                    r.RoomID,
                    r.RoomNumber,
                    NULL as Image,
                    r.RoomStatus,
                    r.MaintenanceReason,
                    r.MaintenanceEstimatedCompletion,
                    h.HotelName,
                    h.City,
                    rt.RoomTypeName,
                    m.MaintenanceID,
                    m.MaintenanceStatus,
                    m.ScheduledStartDate,
                    m.ScheduledEndDate,
                    m.Title,
                    m.Description
                FROM Room r
                JOIN Hotel h ON r.HotelID = h.HotelID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                LEFT JOIN Maintenance m ON r.RoomID = m.RoomID AND m.MaintenanceStatus IN ('Scheduled', 'In Progress')
                WHERE r.RoomStatus = 'Under Maintenance'
                ORDER BY h.HotelName, r.RoomNumber
            """)
        maintenance_list = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/maintenance.html", maintenance_tasks=maintenance_list)


@admin_bp.route("/pricing")
@admin_required
def pricing():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("SELECT * FROM Hotel ORDER BY HotelName")
        hotels_list = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/pricing.html", hotels=hotels_list)


@admin_bp.route("/settings")
@admin_required
def settings():
    return render_template("admin/settings.html")


@admin_bp.route("/users")
@admin_required
def users():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("SELECT * FROM users ORDER BY created_at DESC")
        users_list = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        # Get current status
        cur.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            flash("User not found.")
            return redirect(url_for("admin.users"))
        
        # Toggle status
        new_status = not user["is_active"]
        cur.execute("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    status_text = "activated" if new_status else "deactivated"
    flash(f"User has been {status_text}.")
    return redirect(url_for("admin.users"))


@admin_bp.route("/bookings/add", methods=["GET", "POST"])
@admin_required
def add_booking():
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        
        if request.method == "POST":
            # Get form data
            customer_id = request.form.get("customer_id")
            hotel_id = request.form.get("hotel_id")
            check_in_str = request.form.get("check_in")
            check_out_str = request.form.get("check_out")
            room_type = request.form.get("room_type")
            num_rooms = int(request.form.get("num_rooms"))
            num_guests = int(request.form.get("num_guests"))
            status = request.form.get("status", "Confirmed")
            
            # Convert dates
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            nights = (check_out - check_in).days
            
            if nights <= 0:
                flash("Check-out date must be after check-in date.")
                return redirect(url_for("admin.add_booking"))
            
            # Calculate advance days (booking date is today)
            booking_date = date.today()
            advance_days = (check_in - booking_date).days
            
            if advance_days < 0:
                flash("Check-in date cannot be in the past.")
                return redirect(url_for("admin.add_booking"))
            
            # Determine peak/off-peak
            month = check_in.month
            is_peak = month in [4, 5, 6, 7, 8, 11, 12]
            
            # Get hotel rates
            cur.execute(
                "SELECT PeakRateGBP, OffPeakRateGBP FROM Hotel WHERE HotelID = %s",
                (hotel_id,)
            )
            hotel_row = cur.fetchone()
            if not hotel_row:
                flash("Selected hotel not found.")
                return redirect(url_for("admin.add_booking"))
            
            standard_rate = hotel_row["PeakRateGBP"] if is_peak else hotel_row["OffPeakRateGBP"]
            
            # Room type multiplier
            if room_type == "standard":
                multiplier = 1.00
            elif room_type == "double":
                multiplier = 1.20
            elif room_type == "family":
                multiplier = 1.50
            else:
                multiplier = 1.00
            
            nightly_rate = float(standard_rate) * multiplier
            
            # Advance booking discount
            # Maximum discount is 30% for bookings 80-90 days in advance
            if advance_days > 90:
                discount_percent = 30  # More than 90 days = 30% off (max discount)
            elif 80 <= advance_days <= 90:
                discount_percent = 30  # 80-90 days = 30% off
            elif 60 <= advance_days <= 79:
                discount_percent = 20  # 60-79 days = 20% off
            elif 45 <= advance_days <= 59:
                discount_percent = 10  # 45-59 days = 10% off
            elif 10 <= advance_days <= 44:
                discount_percent = 3  # 10-44 days = 3% off (prebooking discount)
            else:
                discount_percent = 0  # Less than 10 days = no discount
            
            discount_factor = 1.0 - (discount_percent / 100)
            total_price = nightly_rate * nights * num_rooms * discount_factor
            
            # Get RoomTypeID
            room_type_name_map = {
                "standard": "Standard",
                "double": "Double",
                "family": "Family"
            }
            room_type_name = room_type_name_map.get(room_type, "Standard")
            
            cur.execute(
                "SELECT RoomTypeID FROM RoomType WHERE RoomTypeName = %s",
                (room_type_name,)
            )
            rt_row = cur.fetchone()
            if not rt_row:
                flash("Room type not found in database.")
                return redirect(url_for("admin.add_booking"))
            
            room_type_id = rt_row["RoomTypeID"]
            
            # Default cancellation policy
            cancellation_policy_id = 1
            
            # Insert booking
            insert_sql = """
                INSERT INTO Booking (
                    BookingDate, CustomerID, HotelID, RoomTypeID, CancellationPolicyID,
                    CheckInDate, CheckOutDate, Nights, NumRooms, NumGuests,
                    Currency, AdvanceDays, AdvanceDiscountPercent,
                    CalculatedNightlyRate, TotalPriceGBP, BookingStatus
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """
            
            cur.execute(
                insert_sql,
                (
                    booking_date, customer_id, hotel_id, room_type_id, cancellation_policy_id,
                    check_in, check_out, nights, num_rooms, num_guests,
                    "GBP", advance_days, discount_percent,
                    nightly_rate, total_price, status
                )
            )
            conn.commit()
            flash(f"Booking created successfully!")
            return redirect(url_for("admin.admin_bookings"))
        
        cur.execute("SELECT * FROM Hotel ORDER BY HotelName")
        hotels = cur.fetchall()
        
        cur.execute("SELECT * FROM Customer ORDER BY CustomerName")
        customers = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    today = date.today().strftime("%Y-%m-%d")
    return render_template("admin/add_booking.html", hotels=hotels, customers=customers, today=today)

