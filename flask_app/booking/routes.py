# Importing libraries needed for booking functionality
from decimal import Decimal  # For precise money calculations
from datetime import datetime, date
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app, jsonify
)

# Creating booking blueprint - handles all booking related routes
booking_bp = Blueprint("booking", __name__)


# Helper function to connect to database
def get_db_connection():
    return current_app.get_db_connection()


# Helper function to calculate cancellation charges
# This function implements the exact business rules for cancellation charges
# Business Rules:
# - More than 60 days before check-in → 0% charge (free cancellation)
# - 30-60 days before check-in → 50% charge
# - Less than 30 days before check-in → 100% charge (no refund)
# This function is used in the cancellation route and can be called from frontend for preview
def calculate_cancellation_charge(check_in_date, total_price):
    """
    Calculate cancellation charge based on days before check-in date.
    
    Args:
        check_in_date: The check-in date (date object)
        total_price: Total booking price (Decimal or float)
    
    Returns:
        dict with:
            - days_before_checkin: Number of days between today and check-in
            - cancellation_percentage: Percentage charge (0, 50, or 100)
            - cancellation_amount: Actual charge amount
            - refund_amount: Amount to be refunded
    """
    # Get today's date for calculation
    today = date.today()
    
    # Calculate days before check-in date
    # Positive number means check-in is in the future
    days_before_checkin = (check_in_date - today).days
    
    # Convert total_price to Decimal for precise calculations
    total_price_decimal = Decimal(str(total_price))
    
    # Determine cancellation charge percentage based on business rules
    # Rule 1: More than 60 days before check-in → 0% charge
    if days_before_checkin > 60:
        cancellation_percentage = Decimal("0")
    # Rule 2: 30-60 days before check-in → 50% charge
    elif 30 <= days_before_checkin <= 60:
        cancellation_percentage = Decimal("50")
    # Rule 3: Less than 30 days before check-in → 100% charge
    elif days_before_checkin < 30:
        cancellation_percentage = Decimal("100")
    # Edge case: Already past check-in date (shouldn't happen but handle it)
    else:
        cancellation_percentage = Decimal("100")
    
    # Calculate cancellation charge amount
    # Formula: (percentage / 100) * total_price
    cancellation_amount = (cancellation_percentage / Decimal("100")) * total_price_decimal
    
    # Calculate refund amount
    # Refund = Total Price - Cancellation Charge
    refund_amount = total_price_decimal - cancellation_amount
    
    # Return all calculated values
    return {
        "days_before_checkin": days_before_checkin,
        "cancellation_percentage": float(cancellation_percentage),
        "cancellation_amount": float(cancellation_amount),
        "refund_amount": float(refund_amount)
    }


# Main booking page - users can make hotel reservations here
# This handles both showing the booking form (GET) and processing bookings (POST)
@booking_bp.route("/booking", methods=["GET", "POST"])
def booking():
    # Check if user is logged in - you need to login before booking
    if "user_id" not in session:
        flash("Please log in to make a booking.")
        session["show_register_hint"] = True
        return redirect(url_for("auth.login"))

    price_info = None  # Will store calculated price information

    # When user submits the booking form
    if request.method == "POST":
        # Get all the information from the booking form
        city = request.form["city"]  # Which city/hotel they want
        check_in_str = request.form["check_in"]  # Check-in date
        check_out_str = request.form["check_out"]  # Check-out date
        room_type = request.form["room_type"]  # Standard, Double, or Family
        num_rooms = int(request.form["num_rooms"])  # How many rooms
        num_guests = int(request.form["num_guests"])  # How many guests

        # Validate guest capacity - each room type has maximum guests
        # Standard room = 1 guest, Double = 2 guests, Family = 4 guests
        if room_type == "standard" and num_guests > 1:
            flash("Standard room can have maximum 1 guest.")
            return render_template("booking.html", price_info=None)
        if room_type == "double" and num_guests > 2:
            flash("Double room can have maximum 2 guests.")
            return render_template("booking.html", price_info=None)
        if room_type == "family" and num_guests > 4:
            flash("Family room can have maximum 4 guests.")
            return render_template("booking.html", price_info=None)


        # Convert date strings to date objects and calculate number of nights
        check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        nights = (check_out - check_in).days  # Calculate how many nights they're staying

        # Validate dates - check-out must be after check-in
        if nights <= 0:
            flash("Check-out date must be after check-in date.")
            return render_template("booking.html", price_info=None)

        # Maximum stay is 30 nights
        if nights > 30:
            flash("Maximum stay is 30 nights. Please reduce your dates.")
            return render_template("booking.html", price_info=None)

        # Calculate how many days in advance they're booking
        # This is used to calculate early booking discounts
        booking_date = date.today()
        advance_days = (check_in - booking_date).days
        
        # Can't book in the past
        if advance_days < 0:
            flash("Check-in date cannot be in the past.")
            return render_template("booking.html", price_info=None)

        # Can only book up to 3 months (90 days) in advance
        if advance_days > 90:
            flash("You can only book up to 3 months in advance.")
            return render_template("booking.html", price_info=None)

        # Determine if it's peak season or off-peak season
        # Peak months: April, May, June, July, August, November, December
        # Off-peak months: January, February, March, September, October
        month = check_in.month
        is_peak = month in [4, 5, 6, 7, 8, 11, 12]

        # Get hotel information from database
        # Use try/finally to ensure connection is always closed, even if an error occurs
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            # Use buffered cursor to prevent "Unread result found" errors
            # Buffered cursors load all results into memory immediately
            cur = conn.cursor(dictionary=True, buffered=True)
            cur.execute(
                "SELECT HotelID, PeakRateGBP, OffPeakRateGBP, Status FROM Hotel WHERE City = %s",
                (city,)
            )
            hotel_row = cur.fetchone()

            # Check if hotel exists
            if not hotel_row:
                flash("Selected city not found in database.")
                return render_template("booking.html", price_info=None)
            
            # Check if hotel is active - can't book at inactive hotels
            if hotel_row.get("Status") != "Active":
                flash("This hotel is currently unavailable. Please choose another hotel.")
                return redirect(url_for("main.hotels"))

            # Get hotel ID and base price (peak or off-peak rate)
            hotel_id = hotel_row["HotelID"]
            standard_rate = hotel_row["PeakRateGBP"] if is_peak else hotel_row["OffPeakRateGBP"]
            
            # Convert room type from form value to database value
            # Also set price multiplier - Double costs 20% more, Family costs 50% more
            if room_type == "standard":
                room_type_name = "Standard"
                multiplier = Decimal("1.00")  # Standard price (no extra)
            elif room_type == "double":
                room_type_name = "Double"
                multiplier = Decimal("1.20")  # 20% more expensive
            elif room_type == "family":
                room_type_name = "Family"
                multiplier = Decimal("1.50")  # 50% more expensive
            else:
                room_type_name = "Standard"
                multiplier = Decimal("1.00")
            
            # Check if there are available rooms (not under maintenance)
            # We need to make sure rooms exist and are available before allowing booking
            cur.execute("""
                SELECT COUNT(*) as available_count
                FROM Room r
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE r.HotelID = %s 
                  AND rt.RoomTypeName = %s
                  AND r.RoomStatus != 'Under Maintenance'
            """, (hotel_id, room_type_name))
            room_availability = cur.fetchone()
            
            # Also check total rooms (including maintenance ones)
            cur.execute("""
                SELECT COUNT(*) as total_count
                FROM Room r
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE r.HotelID = %s 
                  AND rt.RoomTypeName = %s
            """, (hotel_id, room_type_name))
            total_rooms = cur.fetchone()
            
            # If rooms exist but all are under maintenance, block the booking
            if total_rooms and total_rooms["total_count"] > 0:
                if not room_availability or room_availability["available_count"] == 0:
                    flash("This room type is currently under maintenance. Please choose another room type or hotel.")
                    return render_template("booking.html", price_info=None)

            # Calculate base nightly rate based on room type
            # Standard = base price, Double = 20% more, Family = 50% more
            nightly_rate = standard_rate * multiplier

            # Extra charge for second guest in double room (10% of base rate)
            # This is only applied when booking double room with 2 guests
            extra_guest_charge = Decimal("0.00")
            if room_type == "double" and num_guests == 2:
                extra_guest_charge = standard_rate * Decimal("0.10")

            # Final nightly rate per room (including extra guest charge if applicable)
            nightly_rate_with_extra = nightly_rate + extra_guest_charge

            # Calculate early booking discount based on how many days in advance
            # More days in advance = bigger discount (encourages early bookings)
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

            # Apply discount to total price
            # discount_factor converts percentage to multiplier (e.g., 20% off = 0.80 multiplier)
            discount_factor = Decimal("1.00") - (Decimal(str(discount_percent)) / Decimal("100"))
            # Total = (nightly rate + extra charges) × nights × number of rooms × discount
            total_price = nightly_rate_with_extra * Decimal(nights) * Decimal(num_rooms) * discount_factor

            cur.execute(
                "SELECT RoomTypeID FROM RoomType WHERE RoomTypeName = %s",
                (room_type_name,)
            )
            rt_row = cur.fetchone()
            if not rt_row:
                flash("Could not find room type in database.")
                return render_template("booking.html", price_info=None)
            room_type_id = rt_row["RoomTypeID"]
            customer_id = session.get("customer_id")
            if not customer_id:
                flash("No customer linked to this user. Please log in again.")
                return redirect(url_for("auth.login"))

            cancellation_policy_id = 1
            booking_status = "Confirmed"
            booking_year = booking_date.year

            insert_sql = """
                INSERT INTO Booking (
                    BookingYear, BookingDate, CustomerID, HotelID, RoomTypeID, CancellationPolicyID,
                    CheckInDate, CheckOutDate, Nights, NumRooms, NumGuests,
                    Currency, AdvanceDays, AdvanceDiscountPercent,
                    CalculatedNightlyRate, TotalPriceGBP, BookingStatus
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """

            cur.execute(
                insert_sql,
                (
                    booking_year, booking_date, customer_id, hotel_id, room_type_id, cancellation_policy_id,
                    check_in, check_out, nights, num_rooms, num_guests,
                    "GBP", advance_days, discount_percent,
                    float(nightly_rate_with_extra), float(total_price), booking_status
                )
            )

            # Save changes to database
            conn.commit()
            booking_id = cur.lastrowid  # Get the ID of the booking we just created
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()

        # Generate booking code for display (format: W_H-2025-123)
        # Note: booking_id is available here because we only reach this point if no exception occurred
        booking_code = f"W_H-{booking_year}-{booking_id}"

        # Create summary text for booking (not used in redirect, but kept for reference)
        price_info = (
            f"Booking {booking_code}: {nights} night(s) in {city} "
            f"({'peak' if is_peak else 'off-peak'}), room type: {room_type}, rooms: {num_rooms}, "
            f"advance days: {advance_days}, discount: {discount_percent}%, "
            f"total: £{float(total_price):.2f}"
        )

        # Show success message and redirect to receipt page
        flash("Booking confirmed.")
        return redirect(url_for("booking.receipt", booking_id=booking_id))

    # If GET request (just viewing the booking form)
    # Pre-fill form with customer data if they're logged in
    customer_data = None
    if "customer_id" in session:
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            # Use buffered cursor to prevent "Unread result found" errors
            cur = conn.cursor(dictionary=True, buffered=True)
            # Get customer information to pre-fill the form
            cur.execute(
                "SELECT CustomerName, CustomerEmail, CustomerPhone FROM Customer WHERE CustomerID = %s",
                (session.get("customer_id"),)
            )
            customer_data = cur.fetchone()
        finally:
            # Always close cursor and connection, even if an error occurred
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # Display booking form page
    return render_template("booking.html", price_info=None, customer=customer_data)


# Route to preview cancellation charges before canceling
# This allows users to see cancellation charges and refund amount before confirming
# This is a GET route that returns JSON data for the frontend
@booking_bp.route("/cancel_booking/<int:booking_id>/preview", methods=["GET"])
def cancel_booking_preview(booking_id):
    # Check if user is logged in
    if "user_id" not in session:
        return jsonify({"error": "Please log in to view cancellation details."}), 401

    # Get customer ID to verify booking ownership
    customer_id = session.get("customer_id")
    if not customer_id:
        return jsonify({"error": "No customer linked to this user."}), 401

    # Get booking details from database
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Get booking details including check-in date and total price
        # We need these to calculate cancellation charges
        cur.execute(
            """
            SELECT BookingID, BookingYear, CheckInDate, BookingStatus, TotalPriceGBP
            FROM Booking
            WHERE BookingID = %s AND CustomerID = %s
            """,
            (booking_id, customer_id),
        )
        row = cur.fetchone()

        # Check if booking exists
        if not row:
            return jsonify({"error": "Booking not found."}), 404

        # Can't cancel if already cancelled
        if row["BookingStatus"] == "Cancelled":
            return jsonify({"error": "This booking is already cancelled."}), 400

        # Can't cancel on or after check-in date
        if row["CheckInDate"] <= date.today():
            return jsonify({"error": "You cannot cancel a booking on or after the check-in date."}), 400

        # Calculate cancellation charges using the helper function
        # This follows the exact business rules: >60 days = 0%, 30-60 days = 50%, <30 days = 100%
        cancellation_info = calculate_cancellation_charge(
            row["CheckInDate"],
            row["TotalPriceGBP"]
        )

        # Return cancellation preview data as JSON
        return jsonify({
            "booking_id": booking_id,
            "check_in_date": str(row["CheckInDate"]),
            "total_price": float(row["TotalPriceGBP"]),
            "days_before_checkin": cancellation_info["days_before_checkin"],
            "cancellation_percentage": cancellation_info["cancellation_percentage"],
            "cancellation_amount": cancellation_info["cancellation_amount"],
            "refund_amount": cancellation_info["refund_amount"]
        })
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()


# Route to cancel a booking
# Users can cancel their bookings and cancellation charges are calculated based on timing
# This route stores all cancellation data in the Cancellation table as required for the exam
@booking_bp.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to manage your bookings.")
        session["show_register_hint"] = True
        return redirect(url_for("auth.login"))

    # Get customer ID to verify booking ownership
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("No customer linked to this user. Please log in again.")
        return redirect(url_for("auth.login"))

    # Get booking details from database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Get booking details including booking year, check-in date, and total price
        # We need these to calculate cancellation charges and store in Cancellation table
        cur.execute(
            """
            SELECT BookingYear, BookingID, BookingDate, CheckInDate,
                   BookingStatus, TotalPriceGBP
            FROM Booking
            WHERE BookingID = %s AND CustomerID = %s
            """,
            (booking_id, customer_id),
        )
        row = cur.fetchone()

        # Check if booking exists
        if not row:
            flash("Booking not found.")
            return redirect(url_for("booking.my_bookings"))

        # Can't cancel if already cancelled
        if row["BookingStatus"] == "Cancelled":
            flash("This booking is already cancelled.")
            return redirect(url_for("booking.my_bookings"))

        # Can't cancel on or after check-in date
        if row["CheckInDate"] <= date.today():
            flash("You cannot cancel a booking on or after the check-in date.")
            return redirect(url_for("booking.my_bookings"))

        # Calculate cancellation charges using the helper function
        # This implements the exact business rules:
        # - More than 60 days before check-in → 0% charge
        # - 30-60 days before check-in → 50% charge
        # - Less than 30 days before check-in → 100% charge
        cancellation_info = calculate_cancellation_charge(
            row["CheckInDate"],
            row["TotalPriceGBP"]
        )

        # Get today's date for cancellation record
        today = date.today()

        # Insert cancellation record into Cancellation table
        # This stores all cancellation data as required for the exam
        # The table includes: cancellation_date, days_before_checkin, cancellation_percentage,
        # cancellation_amount, refund_amount, cancellation_status
        cur.execute(
            """
            INSERT INTO Cancellation (
                BookingID, BookingYear, CancellationDate, DaysBeforeCheckIn,
                CancellationPercentage, CancellationAmount, RefundAmount, CancellationStatus
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Processed')
            """,
            (
                row["BookingID"],
                row["BookingYear"],
                today,
                cancellation_info["days_before_checkin"],
                cancellation_info["cancellation_percentage"],
                cancellation_info["cancellation_amount"],
                cancellation_info["refund_amount"]
            )
        )

        # Update booking status to Cancelled and save cancellation charge
        # This ensures referential integrity and updates the booking record
        cur.execute(
            """
            UPDATE Booking
            SET BookingStatus = 'Cancelled',
                CancellationChargeGBP = %s
            WHERE BookingYear = %s AND BookingID = %s AND CustomerID = %s
            """,
            (
                cancellation_info["cancellation_amount"],
                row["BookingYear"],
                row["BookingID"],
                customer_id
            ),
        )

        # Commit all database changes
        # Both the Cancellation record and Booking status update must succeed together
        conn.commit()

    except Exception as e:
        # Rollback on error to maintain data consistency
        if conn:
            conn.rollback()
        flash(f"An error occurred while canceling the booking: {str(e)}")
        return redirect(url_for("booking.my_bookings"))
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Show cancellation confirmation with charge and refund amounts
    # This provides clear feedback to the user about the cancellation
    flash(
        f"Booking cancelled successfully. "
        f"Cancellation charge: £{cancellation_info['cancellation_amount']:.2f}. "
        f"Refund amount: £{cancellation_info['refund_amount']:.2f}"
    )
    return redirect(url_for("booking.my_bookings"))



# My Bookings page - shows all bookings for the logged in user
# Users can view their booking history and cancel bookings from here
@booking_bp.route("/my_bookings")
def my_bookings():
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to view your bookings.")
        session["show_register_hint"] = True
        return redirect(url_for("auth.login"))

    # Get customer ID to fetch their bookings
    customer_id = session.get("customer_id")

    # Get all bookings for this customer from database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)
        # Query to get all booking details including hotel information
        # Shows booking code, hotel name, dates, prices, status, etc.
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
            WHERE b.CustomerID = %s
            ORDER BY b.BookingDate DESC, b.BookingID DESC
            """,
            (customer_id,)
        )
        bookings = cur.fetchall()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Display my bookings page with all user's bookings
    return render_template("my_bookings.html", bookings=bookings)


# Receipt page - shows detailed booking receipt with all payment information
# Users can view and print their booking receipt after making a reservation
@booking_bp.route("/booking/<int:booking_id>/receipt")
def receipt(booking_id):
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to view your receipt.")
        session["show_register_hint"] = True
        return redirect(url_for("auth.login"))

    # Get customer ID to verify booking ownership
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("No customer linked to this user. Please log in again.")
        return redirect(url_for("auth.login"))

    # Get booking details from database
    # Use try/finally to ensure connection is always closed, even if an error occurs
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        # Use buffered cursor to prevent "Unread result found" errors
        cur = conn.cursor(dictionary=True, buffered=True)

        # Query to get complete booking information including hotel details
        # This includes all pricing, dates, discounts, cancellation charges, etc.
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
            WHERE b.BookingID = %s AND b.CustomerID = %s
            """,
            (booking_id, customer_id),
        )
        booking = cur.fetchone()
    finally:
        # Always close cursor and connection, even if an error occurred
        if cur:
            cur.close()
        if conn:
            conn.close()

    # Check if booking exists and belongs to this user
    if not booking:
        flash("Receipt not found for this booking.")
        return redirect(url_for("booking.my_bookings"))

    # Display receipt page with all booking details
    return render_template("receipt.html", booking=booking)
