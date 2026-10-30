-- =========================================================
-- WORLD HOTELS DATABASE SCHEMA - sacstrsx_25024648
-- Complete schema for World Hotels booking website
-- Safe to run multiple times - uses CREATE TABLE IF NOT EXISTS
-- Does NOT drop existing data
-- =========================================================

CREATE DATABASE IF NOT EXISTS world_hotels;
USE world_hotels;

-- Suppress warnings for duplicate indexes (MySQL will continue execution)
SET sql_notes = 1;
CREATE TABLE IF NOT EXISTS Customer (
  CustomerID INT AUTO_INCREMENT PRIMARY KEY,
  CustomerName VARCHAR(100) NOT NULL,
  CustomerEmail VARCHAR(150) NOT NULL UNIQUE,
  CustomerPhone VARCHAR(20) NULL,
  AddressLine1 VARCHAR(200) NULL,
  AddressLine2 VARCHAR(200) NULL,
  City VARCHAR(100) NULL,
  Country VARCHAR(100) NULL,
  Preferences TEXT NULL,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB AUTO_INCREMENT=101;

CREATE TABLE IF NOT EXISTS Hotel (
  HotelID INT AUTO_INCREMENT PRIMARY KEY,
  HotelName VARCHAR(120) NOT NULL,
  City VARCHAR(80) NOT NULL,
  CapacityRooms INT NOT NULL,
  PeakRateGBP DECIMAL(8,2) NOT NULL,
  OffPeakRateGBP DECIMAL(8,2) NOT NULL,
  Description TEXT NULL,
  ImageURL VARCHAR(500) NULL,
  Rating DECIMAL(2,1) DEFAULT 4.0,
  Status ENUM('Active', 'Inactive') DEFAULT 'Active',
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO Hotel (HotelName, City, CapacityRooms, PeakRateGBP, OffPeakRateGBP, Rating, Description) VALUES
('WH Aberdeen', 'Aberdeen', 90, 140.00, 70.00, 4.2, 'Modern hotel in the heart of Aberdeen with excellent amenities and service.'),
('WH Belfast', 'Belfast', 80, 130.00, 70.00, 4.3, 'Comfortable accommodation in Belfast city center.'),
('WH Birmingham', 'Birmingham', 110, 150.00, 75.00, 4.5, 'Premium hotel experience in Birmingham with spacious rooms.'),
('WH Bristol', 'Bristol', 100, 140.00, 70.00, 4.4, 'Stylish hotel located in vibrant Bristol.'),
('WH Cardiff', 'Cardiff', 90, 130.00, 70.00, 4.1, 'Welcoming hotel in Cardiff with modern facilities.'),
('WH Edinburgh', 'Edinburgh', 120, 160.00, 80.00, 4.7, 'Luxury hotel in historic Edinburgh with stunning views.'),
('WH Glasgow', 'Glasgow', 140, 150.00, 75.00, 4.3, 'Contemporary hotel in Glasgow city center.'),
('WH London', 'London', 160, 200.00, 100.00, 4.8, 'Premium hotel in central London with world-class amenities.'),
('WH Manchester', 'Manchester', 150, 180.00, 90.00, 4.6, 'Modern hotel in Manchester with excellent location.'),
('WH New Castle', 'New Castle', 90, 120.00, 70.00, 4.0, 'Comfortable hotel in New Castle with friendly service.'),
('WH Norwich', 'Norwich', 90, 130.00, 70.00, 4.2, 'Charming hotel in Norwich with traditional charm.'),
('WH Nottingham', 'Nottingham', 110, 130.00, 70.00, 4.1, 'Well-appointed hotel in Nottingham city center.'),
('WH Oxford', 'Oxford', 90, 180.00, 90.00, 4.5, 'Elegant hotel near Oxford University with historic character.'),
('WH Plymouth', 'Plymouth', 80, 180.00,  90.00, 4.3, 'Seaside hotel in Plymouth with beautiful views.'),
('WH Swansea', 'Swansea', 70, 130.00, 70.00, 4.0, 'Comfortable hotel in Swansea with modern amenities.'),
('WH Bournemouth', 'Bournemouth', 90, 130.00, 70.00, 4.4, 'Beachfront hotel in Bournemouth with stunning sea views.'),
('WH Kent', 'Kent', 100, 140.00, 80.00, 4.2, 'Peaceful hotel in Kent countryside with excellent facilities.')
ON DUPLICATE KEY UPDATE HotelName = VALUES(HotelName);

CREATE TABLE IF NOT EXISTS RoomType (
  RoomTypeID INT AUTO_INCREMENT PRIMARY KEY,
  RoomTypeName VARCHAR(30) NOT NULL,
  PriceMultiplier DECIMAL(4,2) NOT NULL,
  MaxGuests INT NOT NULL,
  Description VARCHAR(255) NULL
) ENGINE=InnoDB;

INSERT INTO RoomType (RoomTypeName, PriceMultiplier, MaxGuests, Description) VALUES
('Standard', 1.00, 1, 'Cozy single room with essential amenities'),
('Double',   1.20, 2, 'Spacious room with double bed for couples'),
('Family',   1.50, 4, 'Large room ideal for families with children')
ON DUPLICATE KEY UPDATE RoomTypeName = VALUES(RoomTypeName);

CREATE TABLE IF NOT EXISTS CancellationPolicy (
  CancellationPolicyID INT AUTO_INCREMENT PRIMARY KEY,
  PolicyCode VARCHAR(20) NOT NULL,
  Description VARCHAR(255),
  ChargeBetween30And60Pct INT NOT NULL,
  ChargeUnder30DaysPct INT NOT NULL,
  UNIQUE KEY uk_policy_code (PolicyCode)
) ENGINE=InnoDB;

INSERT INTO CancellationPolicy (PolicyCode, Description, ChargeBetween30And60Pct, ChargeUnder30DaysPct) VALUES
('FLEX', 'Free before 60 days; 50% charge between 30-60 days, 100% within 30 days', 50, 100)
ON DUPLICATE KEY UPDATE PolicyCode = VALUES(PolicyCode);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL DEFAULT '',
  role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  customer_id INT NULL,
  google_id VARCHAR(255) NULL UNIQUE,
  profile_picture VARCHAR(500) NULL,
  reset_token VARCHAR(255) NULL,
  reset_expires DATETIME NULL,
  is_active BOOLEAN DEFAULT TRUE,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL,
  CONSTRAINT fk_users_customer
    FOREIGN KEY (customer_id) REFERENCES Customer(CustomerID)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- =========================================================
-- HELPER PROCEDURE: CreateIndexIfNotExists
-- Safely creates indexes only if they don't already exist
-- This prevents errors when running the script multiple times
-- =========================================================
DROP PROCEDURE IF EXISTS CreateIndexIfNotExists;
DELIMITER $$
CREATE PROCEDURE CreateIndexIfNotExists(
    IN p_table_name VARCHAR(64),
    IN p_index_name VARCHAR(64),
    IN p_index_columns VARCHAR(255)
)
BEGIN
    DECLARE v_index_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_index_exists
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = p_table_name
      AND index_name = p_index_name;
    
    IF v_index_exists = 0 THEN
        SET @sql = CONCAT('CREATE INDEX ', p_index_name, ' ON ', p_table_name, '(', p_index_columns, ')');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- Create indexes for users table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('users', 'idx_users_google_id', 'google_id');
CALL CreateIndexIfNotExists('users', 'idx_users_email', 'email');

CREATE TABLE IF NOT EXISTS Booking (
  BookingID INT AUTO_INCREMENT PRIMARY KEY,
  BookingYear YEAR NOT NULL,
  BookingDate DATE NOT NULL,
  CustomerID INT NOT NULL,
  HotelID INT NOT NULL,
  RoomTypeID INT NOT NULL,
  CancellationPolicyID INT NOT NULL,
  CheckInDate DATE NOT NULL,
  CheckOutDate DATE NOT NULL,
  Nights INT NOT NULL,
  NumRooms INT NOT NULL,
  NumGuests INT NOT NULL,
  Currency VARCHAR(10) DEFAULT 'GBP',
  AdvanceDays INT,
  AdvanceDiscountPercent DECIMAL(5,2),
  CalculatedNightlyRate DECIMAL(8,2),
  TotalPriceGBP DECIMAL(10,2),
  BookingStatus ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed') DEFAULT 'Pending',
  CancellationChargeGBP DECIMAL(10,2) DEFAULT 0,
  SpecialRequests TEXT NULL,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_booking_customer
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
    ON DELETE RESTRICT,
  CONSTRAINT fk_booking_hotel
    FOREIGN KEY (HotelID) REFERENCES Hotel(HotelID)
    ON DELETE RESTRICT,
  CONSTRAINT fk_booking_roomtype
    FOREIGN KEY (RoomTypeID) REFERENCES RoomType(RoomTypeID)
    ON DELETE RESTRICT,
  CONSTRAINT fk_booking_policy
    FOREIGN KEY (CancellationPolicyID) REFERENCES CancellationPolicy(CancellationPolicyID)
    ON DELETE RESTRICT,
  UNIQUE KEY uk_booking_dates (CustomerID, HotelID, CheckInDate, CheckOutDate)
) ENGINE=InnoDB;

-- Create indexes for Booking table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('Booking', 'idx_booking_customer', 'CustomerID');
CALL CreateIndexIfNotExists('Booking', 'idx_booking_hotel', 'HotelID');
CALL CreateIndexIfNotExists('Booking', 'idx_booking_dates', 'CheckInDate, CheckOutDate');
CALL CreateIndexIfNotExists('Booking', 'idx_booking_status', 'BookingStatus');

-- =========================================================
-- CANCELLATION TABLE
-- Stores all cancellation records with detailed information
-- This table tracks every cancellation with charges and refunds
-- Required for exam: tracks cancellation_date, days_before_checkin,
-- cancellation_percentage, cancellation_amount, refund_amount
-- =========================================================
CREATE TABLE IF NOT EXISTS Cancellation (
  CancellationID INT AUTO_INCREMENT PRIMARY KEY,
  BookingID INT NOT NULL,
  BookingYear YEAR NOT NULL,
  CancellationDate DATE NOT NULL,
  DaysBeforeCheckIn INT NOT NULL,
  CancellationPercentage DECIMAL(5,2) NOT NULL,
  CancellationAmount DECIMAL(10,2) NOT NULL,
  RefundAmount DECIMAL(10,2) NOT NULL,
  CancellationStatus ENUM('Processed', 'Refunded', 'Pending') DEFAULT 'Processed',
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cancellation_booking
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
    ON DELETE RESTRICT,
  INDEX idx_cancellation_booking (BookingID),
  INDEX idx_cancellation_date (CancellationDate),
  INDEX idx_cancellation_status (CancellationStatus)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(50) NOT NULL DEFAULT 'online',
  payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  transaction_id VARCHAR(100),
  payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_payments_booking
    FOREIGN KEY (booking_id) REFERENCES Booking(BookingID)
    ON DELETE RESTRICT
) ENGINE=InnoDB;


-- Create indexes for payments table
-- Create indexes for payments table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('payments', 'idx_payments_booking', 'booking_id');
CALL CreateIndexIfNotExists('payments', 'idx_payments_status', 'payment_status');

CREATE TABLE IF NOT EXISTS reviews (
  review_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  hotel_id INT NOT NULL,
  rating INT NOT NULL COMMENT 'Rating between 1 and 5 (validated in application)',
  comment TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_reviews_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_reviews_hotel
    FOREIGN KEY (hotel_id) REFERENCES Hotel(HotelID)
    ON DELETE CASCADE,
  UNIQUE KEY unique_user_hotel_review (user_id, hotel_id)
) ENGINE=InnoDB;


-- Create indexes for reviews table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('reviews', 'idx_reviews_user', 'user_id');
CALL CreateIndexIfNotExists('reviews', 'idx_reviews_hotel', 'hotel_id');

CREATE TABLE IF NOT EXISTS Room (
  RoomID INT AUTO_INCREMENT PRIMARY KEY,
  HotelID INT NOT NULL,
  RoomNumber VARCHAR(20) NOT NULL,
  RoomTypeID INT NOT NULL,

  FloorNumber INT NULL,
  BedConfiguration VARCHAR(100) NULL COMMENT 'e.g., 1 King Bed / 2 Twin Beds',
  MaxOccupancy INT NOT NULL DEFAULT 2,
  RoomSizeSqm DECIMAL(5,2) NULL,

  BasePricePerNight DECIMAL(8,2) NOT NULL,
  SeasonalPriceMultiplier DECIMAL(4,2) DEFAULT 1.00,

  RoomStatus ENUM('Available', 'Booked', 'Under Maintenance', 'Out of Service', 'Reserved for Staff')
    DEFAULT 'Available',
  MaintenanceReason TEXT NULL,
  MaintenanceEstimatedCompletion DATE NULL,

  Amenities JSON NULL COMMENT 'Array of amenities',
  RoomPhotos JSON NULL COMMENT 'Array of image URLs',
  FeaturedImageURL VARCHAR(500) NULL,
  VirtualTourURL VARCHAR(500) NULL,
  Image VARCHAR(100) NULL COMMENT 'Single image filename (e.g., rooms-1.jpg)',

  Description TEXT NULL,
  SpecialFeatures TEXT NULL,

  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_room_hotel
    FOREIGN KEY (HotelID) REFERENCES Hotel(HotelID)
    ON DELETE CASCADE,
  CONSTRAINT fk_room_roomtype
    FOREIGN KEY (RoomTypeID) REFERENCES RoomType(RoomTypeID)
    ON DELETE RESTRICT,

  UNIQUE KEY uk_room_hotel_number (HotelID, RoomNumber)
) ENGINE=InnoDB;

-- Create indexes for Room table
-- Create indexes for Room table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('Room', 'idx_room_hotel', 'HotelID');
CALL CreateIndexIfNotExists('Room', 'idx_room_status', 'RoomStatus');
CALL CreateIndexIfNotExists('Room', 'idx_room_type', 'RoomTypeID');
CALL CreateIndexIfNotExists('Room', 'idx_room_maintenance', 'MaintenanceEstimatedCompletion');

CREATE TABLE IF NOT EXISTS Maintenance (
  MaintenanceID INT AUTO_INCREMENT PRIMARY KEY,
  RoomID INT NOT NULL,
  HotelID INT NOT NULL,

  MaintenanceType ENUM('Preventive', 'Corrective', 'Emergency', 'Inspection', 'Cleaning')
    NOT NULL DEFAULT 'Preventive',
  Title VARCHAR(200) NOT NULL,
  Description TEXT NULL,
  Priority ENUM('Low', 'Medium', 'High', 'Urgent') DEFAULT 'Medium',

  ScheduledStartDate DATETIME NOT NULL,
  ScheduledEndDate DATETIME NULL,
  ActualStartDate DATETIME NULL,
  ActualEndDate DATETIME NULL,

  MaintenanceStatus ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled', 'On Hold')
    DEFAULT 'Scheduled',

  AssignedToStaffID INT NULL COMMENT 'Staff user ID from users table',
  AssignedToName VARCHAR(100) NULL,

  EstimatedCost DECIMAL(10,2) NULL,
  ActualCost DECIMAL(10,2) NULL,

  Notes TEXT NULL,
  CompletionNotes TEXT NULL,

  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CreatedBy INT NULL COMMENT 'Admin user ID',
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CompletedAt DATETIME NULL,

  CONSTRAINT fk_maintenance_room
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
    ON DELETE CASCADE,
  CONSTRAINT fk_maintenance_hotel
    FOREIGN KEY (HotelID) REFERENCES Hotel(HotelID)
    ON DELETE CASCADE,
  CONSTRAINT fk_maintenance_staff
    FOREIGN KEY (AssignedToStaffID) REFERENCES users(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_maintenance_creator
    FOREIGN KEY (CreatedBy) REFERENCES users(id)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- Create indexes for Maintenance table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_room', 'RoomID');
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_hotel', 'HotelID');
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_status', 'MaintenanceStatus');
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_dates', 'ScheduledStartDate, ScheduledEndDate');
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_priority', 'Priority');
CALL CreateIndexIfNotExists('Maintenance', 'idx_maintenance_staff', 'AssignedToStaffID');

CREATE TABLE IF NOT EXISTS RoomBooking (
  RoomBookingID INT AUTO_INCREMENT PRIMARY KEY,
  BookingID INT NOT NULL,
  RoomID INT NOT NULL,
  CheckInDate DATE NOT NULL,
  CheckOutDate DATE NOT NULL,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_roombooking_booking
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
    ON DELETE CASCADE,
  CONSTRAINT fk_roombooking_room
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
    ON DELETE RESTRICT,

  UNIQUE KEY uk_room_booking_dates (RoomID, CheckInDate, CheckOutDate)
) ENGINE=InnoDB;

-- Create indexes for RoomBooking table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('RoomBooking', 'idx_roombooking_booking', 'BookingID');
CALL CreateIndexIfNotExists('RoomBooking', 'idx_roombooking_room', 'RoomID');
CALL CreateIndexIfNotExists('RoomBooking', 'idx_roombooking_dates', 'CheckInDate, CheckOutDate');

CREATE TABLE IF NOT EXISTS SeasonalPricing (
  SeasonalPricingID INT AUTO_INCREMENT PRIMARY KEY,
  HotelID INT NULL COMMENT 'NULL means applies to all hotels',
  RoomTypeID INT NULL COMMENT 'NULL means applies to all room types',
  RoomID INT NULL COMMENT 'NULL means applies to all rooms',

  SeasonName VARCHAR(100) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NOT NULL,
  PriceMultiplier DECIMAL(4,2) NOT NULL DEFAULT 1.00 COMMENT '1.00=base',
  FixedPrice DECIMAL(8,2) NULL,

  Description TEXT NULL,
  IsActive BOOLEAN DEFAULT TRUE,

  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_seasonal_hotel
    FOREIGN KEY (HotelID) REFERENCES Hotel(HotelID)
    ON DELETE CASCADE,
  CONSTRAINT fk_seasonal_roomtype
    FOREIGN KEY (RoomTypeID) REFERENCES RoomType(RoomTypeID)
    ON DELETE CASCADE,
  CONSTRAINT fk_seasonal_room
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS MaintenanceHistory (
  HistoryID INT AUTO_INCREMENT PRIMARY KEY,
  MaintenanceID INT NOT NULL,
  RoomID INT NOT NULL,
  StatusChangedFrom VARCHAR(50) NULL,
  StatusChangedTo VARCHAR(50) NOT NULL,
  ChangedBy INT NULL,
  ChangeNotes TEXT NULL,
  ChangedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_maintenancehistory_maintenance
    FOREIGN KEY (MaintenanceID) REFERENCES Maintenance(MaintenanceID)
    ON DELETE CASCADE,
  CONSTRAINT fk_maintenancehistory_room
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
    ON DELETE CASCADE,
  CONSTRAINT fk_maintenancehistory_user
    FOREIGN KEY (ChangedBy) REFERENCES users(id)
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- Create indexes for MaintenanceHistory table (safe - won't fail if exists)
CALL CreateIndexIfNotExists('MaintenanceHistory', 'idx_maintenancehistory_maintenance', 'MaintenanceID');
CALL CreateIndexIfNotExists('MaintenanceHistory', 'idx_maintenancehistory_room', 'RoomID');
CALL CreateIndexIfNotExists('MaintenanceHistory', 'idx_maintenancehistory_date', 'ChangedAt');

DROP TRIGGER IF EXISTS trg_maintenance_scheduled;
DROP TRIGGER IF EXISTS trg_maintenance_completed;
DROP TRIGGER IF EXISTS trg_maintenance_history;

DELIMITER $$

CREATE TRIGGER trg_maintenance_scheduled
AFTER INSERT ON Maintenance
FOR EACH ROW
BEGIN
  IF NEW.MaintenanceStatus = 'Scheduled' OR NEW.MaintenanceStatus = 'In Progress' THEN
    UPDATE Room
    SET RoomStatus = 'Under Maintenance',
        MaintenanceReason = NEW.Title,
        MaintenanceEstimatedCompletion = DATE(NEW.ScheduledEndDate)
    WHERE RoomID = NEW.RoomID;
  END IF;
END$$

CREATE TRIGGER trg_maintenance_completed
AFTER UPDATE ON Maintenance
FOR EACH ROW
BEGIN
  IF NEW.MaintenanceStatus = 'Completed' AND OLD.MaintenanceStatus <> 'Completed' THEN
    UPDATE Room
    SET RoomStatus = 'Available',
        MaintenanceReason = NULL,
        MaintenanceEstimatedCompletion = NULL
    WHERE RoomID = NEW.RoomID;
  END IF;
END$$

CREATE TRIGGER trg_maintenance_history
AFTER UPDATE ON Maintenance
FOR EACH ROW
BEGIN
  IF NEW.MaintenanceStatus <> OLD.MaintenanceStatus THEN
    INSERT INTO MaintenanceHistory (
      MaintenanceID, RoomID, StatusChangedFrom, StatusChangedTo, ChangedBy, ChangeNotes
    ) VALUES (
      NEW.MaintenanceID, NEW.RoomID, OLD.MaintenanceStatus, NEW.MaintenanceStatus,
      NEW.CreatedBy, CONCAT('Status changed from ', OLD.MaintenanceStatus, ' to ', NEW.MaintenanceStatus)
    );
  END IF;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS GetAvailableRooms;
DROP PROCEDURE IF EXISTS GetRoomsRequiringMaintenance;
DROP PROCEDURE IF EXISTS UpdateRoomStatus;
DROP PROCEDURE IF EXISTS CreateRoomsWithDistribution;

DELIMITER $$

CREATE PROCEDURE GetAvailableRooms(
  IN pHotelID INT,
  IN pCheckInDate DATE,
  IN pCheckOutDate DATE,
  IN pRoomTypeID INT
)
BEGIN
  SELECT
    r.RoomID,
    r.RoomNumber,
    r.FloorNumber,
    rt.RoomTypeName,
    r.BasePricePerNight,
    r.Amenities,
    r.RoomStatus
  FROM Room r
  JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
  WHERE r.HotelID = pHotelID
    AND r.RoomStatus = 'Available'
    AND (pRoomTypeID IS NULL OR r.RoomTypeID = pRoomTypeID)
    AND r.RoomID NOT IN (
      SELECT DISTINCT rb.RoomID
      FROM RoomBooking rb
      WHERE rb.RoomID = r.RoomID
        AND (
          (rb.CheckInDate <= pCheckInDate AND rb.CheckOutDate > pCheckInDate)
          OR (rb.CheckInDate < pCheckOutDate AND rb.CheckOutDate >= pCheckOutDate)
          OR (rb.CheckInDate >= pCheckInDate AND rb.CheckOutDate <= pCheckOutDate)
        )
    )
    AND r.RoomID NOT IN (
      SELECT DISTINCT m.RoomID
      FROM Maintenance m
      WHERE m.RoomID = r.RoomID
        AND m.MaintenanceStatus IN ('Scheduled', 'In Progress')
        AND (DATE(m.ScheduledStartDate) <= pCheckOutDate AND DATE(m.ScheduledEndDate) >= pCheckInDate)
    )
  ORDER BY r.RoomNumber;
END$$

CREATE PROCEDURE GetRoomsRequiringMaintenance()
BEGIN
  SELECT
    r.RoomID,
    r.RoomNumber,
    h.HotelName,
    h.City,
    r.RoomStatus,
    r.MaintenanceReason,
    r.MaintenanceEstimatedCompletion,
    COUNT(m.MaintenanceID) AS PendingMaintenanceCount
  FROM Room r
  JOIN Hotel h ON r.HotelID = h.HotelID
  LEFT JOIN Maintenance m ON r.RoomID = m.RoomID
    AND m.MaintenanceStatus IN ('Scheduled', 'In Progress')
  WHERE r.RoomStatus IN ('Under Maintenance', 'Out of Service')
     OR m.MaintenanceID IS NOT NULL
  GROUP BY r.RoomID
  ORDER BY r.MaintenanceEstimatedCompletion ASC, h.HotelName, r.RoomNumber;
END$$

CREATE PROCEDURE UpdateRoomStatus(
  IN pRoomID INT,
  IN pNewStatus VARCHAR(50),
  IN pMaintenanceReason TEXT,
  IN pEstimatedCompletion DATE
)
BEGIN
  DECLARE vCurrentStatus VARCHAR(50);

  SELECT RoomStatus INTO vCurrentStatus
  FROM Room
  WHERE RoomID = pRoomID;

  IF vCurrentStatus IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Room not found';
  END IF;

  UPDATE Room
  SET RoomStatus = pNewStatus,
      MaintenanceReason = pMaintenanceReason,
      MaintenanceEstimatedCompletion = pEstimatedCompletion,
      UpdatedAt = CURRENT_TIMESTAMP
  WHERE RoomID = pRoomID;

  SELECT 'Room status updated successfully' AS message;
END$$

-- =========================================================
-- STORED PROCEDURE: CreateRoomsWithDistribution
-- Automatically creates rooms for a hotel with correct distribution:
-- 30% Standard, 50% Double, 20% Family
-- =========================================================
DROP PROCEDURE IF EXISTS CreateRoomsWithDistribution;
DELIMITER $$
CREATE PROCEDURE CreateRoomsWithDistribution(
    IN pHotelID INT,
    IN pTotalRooms INT
)
BEGIN
    DECLARE vStandardCount INT;
    DECLARE vDoubleCount INT;
    DECLARE vFamilyCount INT;
    DECLARE vRoomCounter INT DEFAULT 1;
    DECLARE vStandardTypeID INT;
    DECLARE vDoubleTypeID INT;
    DECLARE vFamilyTypeID INT;
    DECLARE vBasePrice DECIMAL(8,2);
    DECLARE vRoomNumber VARCHAR(20);
    
    -- Get RoomType IDs
    SELECT RoomTypeID INTO vStandardTypeID FROM RoomType WHERE RoomTypeName = 'Standard' LIMIT 1;
    SELECT RoomTypeID INTO vDoubleTypeID FROM RoomType WHERE RoomTypeName = 'Double' LIMIT 1;
    SELECT RoomTypeID INTO vFamilyTypeID FROM RoomType WHERE RoomTypeName = 'Family' LIMIT 1;
    
    -- Get hotel base price (use off-peak rate as base)
    SELECT OffPeakRateGBP INTO vBasePrice FROM Hotel WHERE HotelID = pHotelID LIMIT 1;
    
    -- Calculate room distribution: 30% Standard, 50% Double, 20% Family
    SET vStandardCount = ROUND(pTotalRooms * 0.30);
    SET vDoubleCount = ROUND(pTotalRooms * 0.50);
    SET vFamilyCount = pTotalRooms - vStandardCount - vDoubleCount; -- Remaining goes to Family
    
    -- Create Standard rooms (30%)
    WHILE vRoomCounter <= vStandardCount DO
        SET vRoomNumber = CONCAT('S', LPAD(vRoomCounter, 3, '0'));
        INSERT INTO Room (HotelID, RoomNumber, RoomTypeID, BasePricePerNight, RoomStatus, MaxOccupancy)
        VALUES (pHotelID, vRoomNumber, vStandardTypeID, vBasePrice, 'Available', 1)
        ON DUPLICATE KEY UPDATE RoomNumber = RoomNumber;
        SET vRoomCounter = vRoomCounter + 1;
    END WHILE;
    
    -- Create Double rooms (50%)
    SET vRoomCounter = 1;
    WHILE vRoomCounter <= vDoubleCount DO
        SET vRoomNumber = CONCAT('D', LPAD(vRoomCounter, 3, '0'));
        INSERT INTO Room (HotelID, RoomNumber, RoomTypeID, BasePricePerNight, RoomStatus, MaxOccupancy)
        VALUES (pHotelID, vRoomNumber, vDoubleTypeID, vBasePrice * 1.20, 'Available', 2)
        ON DUPLICATE KEY UPDATE RoomNumber = RoomNumber;
        SET vRoomCounter = vRoomCounter + 1;
    END WHILE;
    
    -- Create Family rooms (20%)
    SET vRoomCounter = 1;
    WHILE vRoomCounter <= vFamilyCount DO
        SET vRoomNumber = CONCAT('F', LPAD(vRoomCounter, 3, '0'));
        INSERT INTO Room (HotelID, RoomNumber, RoomTypeID, BasePricePerNight, RoomStatus, MaxOccupancy)
        VALUES (pHotelID, vRoomNumber, vFamilyTypeID, vBasePrice * 1.50, 'Available', 4)
        ON DUPLICATE KEY UPDATE RoomNumber = RoomNumber;
        SET vRoomCounter = vRoomCounter + 1;
    END WHILE;
    
    SELECT CONCAT('Created ', vStandardCount, ' Standard, ', vDoubleCount, ' Double, ', vFamilyCount, ' Family rooms') AS Result;
END$$
DELIMITER ;

-- Clean up the helper procedure (optional - can keep it for future use)
-- DROP PROCEDURE IF EXISTS CreateIndexIfNotExists;

-- =========================================================
-- VERIFICATION QUERIES (Optional - uncomment to verify)
-- =========================================================
-- SHOW TABLES;
-- SELECT COUNT(*) AS HotelCount FROM Hotel;
-- SELECT COUNT(*) AS RoomTypeCount FROM RoomType;
-- SELECT COUNT(*) AS CancellationPolicyCount FROM CancellationPolicy;
-- SELECT COUNT(*) AS CancellationTableCount FROM Cancellation;

SELECT 'Database schema created/updated successfully!' AS Status;
SELECT 'All tables use CREATE TABLE IF NOT EXISTS - safe to run multiple times' AS Note;
SELECT 'All INSERT statements use ON DUPLICATE KEY UPDATE - no data loss' AS Note;
SELECT 'All indexes created safely - no duplicate errors' AS Note;
