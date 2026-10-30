# World Hotels – 3NF (Third Normal Form) Design

## Overview
This document describes the Third Normal Form (3NF) database design for World Hotels booking system. This is the **production database schema** currently in use.

**3NF Definition:** A table is in 3NF if:
1. It is in 2NF (Second Normal Form)
2. All non-key attributes are **non-transitively dependent** on the primary key
   - No non-key attribute depends on another non-key attribute

## Starting Point
From 2NF: Tables are separated, but Booking table contains denormalized fields (CustomerName, HotelName, RoomTypeName, etc.) which create transitive dependencies.

## Goal
Remove all transitive dependencies by ensuring that non-key attributes depend **only** on the primary key, not on other non-key attributes.

---

## Identified Entities

The main entities in the 3NF design:

1. **Customer** - Stores unique customer information
2. **Hotel** - Stores hotel and city information with rates
3. **RoomType** - Defines room types and their pricing multipliers
4. **CancellationPolicy** - Stores cancellation policy rules
5. **Booking** - Stores booking transactions (ONLY foreign keys, no denormalized data)
6. **Cancellation** - Stores cancellation records
7. **users** - Stores user accounts (linked to customers)
8. **Room** - Stores individual room details
9. **Maintenance** - Tracks room maintenance
10. **RoomBooking** - Links bookings to specific rooms
11. **SeasonalPricing** - Manages seasonal pricing rules
12. **MaintenanceHistory** - Tracks maintenance history
13. **payments** - Stores payment records
14. **reviews** - Stores hotel reviews

---

## 3NF Table Designs

### 1. Customer Table

Stores unique customer information. This is the **single source of truth** for customer data.

**Primary Key:** `CustomerID`

| Field         | Type          | Constraints | Notes                  |
|---------------|---------------|-------------|------------------------|
| CustomerID    | INT           | PK, AUTO_INCREMENT | Unique identifier |
| CustomerName  | VARCHAR(100)  | NOT NULL    | Customer full name |
| CustomerEmail | VARCHAR(150)  | NOT NULL, UNIQUE | Email address |
| CustomerPhone | VARCHAR(20)   | NULL        | Phone number |
| AddressLine1  | VARCHAR(200)  | NULL        | Street address |
| AddressLine2  | VARCHAR(200)  | NULL        | Additional address |
| City          | VARCHAR(100)  | NULL        | City |
| Country       | VARCHAR(100)  | NULL        | Country |
| Preferences   | TEXT          | NULL        | Customer preferences |
| CreatedAt     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| UpdatedAt     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update time |

**3NF Compliance:** All attributes depend directly on CustomerID (primary key). No transitive dependencies.

---

### 2. Hotel Table

Stores hotel information and standard room rates. This is the **single source of truth** for hotel data.

**Primary Key:** `HotelID`

| Field         | Type          | Constraints | Notes                             |
|---------------|---------------|-------------|-----------------------------------|
| HotelID       | INT           | PK, AUTO_INCREMENT | Unique identifier |
| HotelName     | VARCHAR(120)  | NOT NULL    | e.g. "WH London Central" |
| City          | VARCHAR(80)   | NOT NULL    | e.g. "London" |
| CapacityRooms | INT           | NOT NULL    | Total number of rooms |
| PeakRateGBP   | DECIMAL(8,2)  | NOT NULL    | Standard rate in peak season |
| OffPeakRateGBP| DECIMAL(8,2)  | NOT NULL    | Standard rate off-peak |
| Description   | TEXT          | NULL        | Hotel description |
| ImageURL      | VARCHAR(500)  | NULL        | Hotel image URL |
| Rating        | DECIMAL(2,1)  | DEFAULT 4.0 | Hotel rating (1-5) |
| Status        | ENUM          | DEFAULT 'Active' | Active/Inactive |
| CreatedAt     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**3NF Compliance:** All attributes depend directly on HotelID (primary key). No transitive dependencies.

---

### 3. RoomType Table

Defines different room types and their price multipliers. This is the **single source of truth** for room type data.

**Primary Key:** `RoomTypeID`

| Field              | Type          | Constraints | Notes                                           |
|--------------------|---------------|-------------|-------------------------------------------------|
| RoomTypeID         | INT           | PK, AUTO_INCREMENT | Unique identifier |
| RoomTypeName       | VARCHAR(30)   | NOT NULL    | Standard / Double / Family |
| PriceMultiplier    | DECIMAL(4,2)  | NOT NULL    | e.g. 1.0 for Standard, 1.2 for Double, 1.5 for Family |
| MaxGuests          | INT           | NOT NULL    | Maximum occupancy (1, 2, or 4) |
| Description        | VARCHAR(255)  | NULL        | Room type description |

**3NF Compliance:** All attributes depend directly on RoomTypeID (primary key). No transitive dependencies.

---

### 4. CancellationPolicy Table

Stores the rules for cancellation charges. This is the **single source of truth** for policy data.

**Primary Key:** `CancellationPolicyID`

| Field                   | Type          | Constraints | Notes                                           |
|-------------------------|---------------|-------------|-------------------------------------------------|
| CancellationPolicyID    | INT           | PK, AUTO_INCREMENT | Unique identifier |
| PolicyCode              | VARCHAR(20)   | NOT NULL, UNIQUE | e.g. "FLEX" |
| Description             | VARCHAR(255)  | NULL        | Text description of the policy |
| ChargeBetween30And60Pct | INT           | NOT NULL    | Percentage charge (e.g. 50) |
| ChargeUnder30DaysPct    | INT           | NOT NULL    | Percentage charge (e.g. 100) |

**3NF Compliance:** All attributes depend directly on CancellationPolicyID (primary key). No transitive dependencies.

---

### 5. Booking Table (3NF - FULLY Normalized)

Stores each booking and links to other entities. **In 3NF, this table contains ONLY foreign keys and booking-specific data** (no denormalized fields).

**Primary Key:** `BookingID`  
**Foreign Keys:** CustomerID, HotelID, RoomTypeID, CancellationPolicyID

| Field                   | Type          | Constraints | Notes                                   |
|-------------------------|---------------|-------------|-----------------------------------------|
| BookingID               | INT           | PK, AUTO_INCREMENT | Unique identifier |
| BookingYear             | YEAR          | NOT NULL    | Year of booking |
| BookingDate             | DATE          | NOT NULL    | Date booking was made |
| CustomerID              | INT           | NOT NULL, FK | → Customer.CustomerID |
| HotelID                 | INT           | NOT NULL, FK | → Hotel.HotelID |
| RoomTypeID              | INT           | NOT NULL, FK | → RoomType.RoomTypeID |
| CancellationPolicyID    | INT           | NOT NULL, FK | → CancellationPolicy.CancellationPolicyID |
| CheckInDate             | DATE          | NOT NULL    | Check-in date |
| CheckOutDate            | DATE          | NOT NULL    | Check-out date |
| Nights                  | INT           | NOT NULL    | Number of nights |
| NumRooms                | INT           | NOT NULL    | Number of rooms booked |
| NumGuests               | INT           | NOT NULL    | Number of guests |
| Currency                | VARCHAR(10)   | DEFAULT 'GBP' | Currency code |
| AdvanceDays             | INT           | NULL        | Days between booking and check-in |
| AdvanceDiscountPercent  | DECIMAL(5,2)  | NULL        | Discount percentage (0, 10, 20, 30) |
| CalculatedNightlyRate   | DECIMAL(8,2)  | NULL        | Rate after multipliers/discounts |
| TotalPriceGBP           | DECIMAL(10,2) | NULL        | Final booking price |
| BookingStatus           | ENUM          | DEFAULT 'Pending' | Pending/Confirmed/Cancelled/Completed |
| CancellationChargeGBP   | DECIMAL(10,2) | DEFAULT 0   | Cancellation charge if applicable |
| SpecialRequests         | TEXT          | NULL        | Special requests from customer |
| CreatedAt               | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| UpdatedAt               | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update time |

**3NF Compliance:**
- All non-key attributes depend directly on BookingID (primary key)
- No partial dependencies (BookingID is a simple key)
- **NO transitive dependencies** - CustomerName, HotelName, RoomTypeName are NOT stored here
- **NO denormalized fields** - All entity data is in separate tables

**Key Difference from 2NF:**
- **NO** CustomerName, CustomerEmail fields
- **NO** HotelName, HotelCity fields
- **NO** RoomTypeName, RoomTypeMultiplier fields
- **NO** BaseRateGBP field
- **ONLY** foreign keys (CustomerID, HotelID, RoomTypeID, CancellationPolicyID)

---

### 6. Cancellation Table (3NF)

Stores cancellation records with detailed information.

**Primary Key:** `CancellationID`  
**Foreign Key:** BookingID → Booking.BookingID

| Field                   | Type          | Constraints | Notes                                   |
|-------------------------|---------------|-------------|-----------------------------------------|
| CancellationID          | INT           | PK, AUTO_INCREMENT | Unique identifier |
| BookingID               | INT           | NOT NULL, FK | → Booking.BookingID |
| BookingYear             | YEAR          | NOT NULL    | Year of booking |
| CancellationDate        | DATE          | NOT NULL    | Date of cancellation |
| DaysBeforeCheckIn       | INT           | NOT NULL    | Days before check-in when cancelled |
| CancellationPercentage  | DECIMAL(5,2)  | NOT NULL    | Percentage charged |
| CancellationAmount      | DECIMAL(10,2) | NOT NULL    | Amount charged |
| RefundAmount            | DECIMAL(10,2) | NOT NULL    | Amount refunded |
| CancellationStatus      | ENUM          | DEFAULT 'Processed' | Processed/Refunded/Pending |
| CreatedAt               | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |

---

### 7. Additional Tables (3NF)

The 3NF design includes additional tables for a complete hotel management system:

- **users** - User accounts (linked to customers)
- **Room** - Individual room details
- **Maintenance** - Room maintenance tracking
- **RoomBooking** - Links bookings to specific rooms
- **SeasonalPricing** - Seasonal pricing rules
- **MaintenanceHistory** - Maintenance history log
- **payments** - Payment records
- **reviews** - Hotel reviews

All these tables follow 3NF principles with proper foreign key relationships and no transitive dependencies.

---

## 3NF Characteristics Summary

### What 3NF Achieves:
1. **Removes Partial Dependencies:** All non-key attributes depend on the entire primary key
2. **Removes Transitive Dependencies:** No non-key attribute depends on another non-key attribute
3. **Single Source of Truth:** Each piece of data is stored in exactly one place
4. **No Data Redundancy:** Entity data (customer name, hotel name, etc.) stored only in their respective tables
5. **Data Integrity:** Updates to entity data automatically reflected in all queries via JOINs

### Benefits of 3NF Approach:
- **No Data Redundancy:** Saves storage space
- **No Update Anomalies:** Update once, reflected everywhere
- **Data Consistency:** Single source of truth prevents inconsistencies
- **Maintainability:** Easier to maintain and modify
- **Scalability:** Better for large databases

### Trade-offs of 3NF Approach:
- **Requires JOINs:** More complex queries needed
- **Slightly Slower Reads:** Multiple table access (though indexes help)
- **More Complex Queries:** Must understand relationships

---

## Example Queries (3NF)

### Complete Booking Query (Requires JOINs):
```sql
-- Get booking with customer and hotel names via JOINs
SELECT 
    b.BookingID,
    b.BookingDate,
    b.CheckInDate,
    b.CheckOutDate,
    b.TotalPriceGBP,
    -- Customer data from Customer table (not in Booking)
    c.CustomerName,
    c.CustomerEmail,
    c.CustomerPhone,
    -- Hotel data from Hotel table (not in Booking)
    h.HotelName,
    h.City AS HotelCity,
    h.PeakRateGBP,
    h.OffPeakRateGBP,
    -- Room type data from RoomType table (not in Booking)
    rt.RoomTypeName,
    rt.PriceMultiplier,
    rt.MaxGuests,
    -- Cancellation policy from CancellationPolicy table
    cp.PolicyCode,
    cp.Description AS PolicyDescription
FROM Booking b
JOIN Customer c ON b.CustomerID = c.CustomerID
JOIN Hotel h ON b.HotelID = h.HotelID
JOIN RoomType rt ON b.RoomTypeID = rt.RoomTypeID
JOIN CancellationPolicy cp ON b.CancellationPolicyID = cp.CancellationPolicyID
WHERE b.BookingID = 1;
```

### Update Scenario (3NF):
```sql
-- If customer changes name, update ONLY Customer table:
UPDATE Customer SET CustomerName = 'New Name' WHERE CustomerID = 1;
-- All queries automatically get updated data via JOINs!
-- Single update required - no need to update Booking table
```

---

## Normalization Progression

- **Un-normalised:** One wide table with all data mixed together
- **1NF:** Atomic values, but still one large table with repetition
- **2NF:** Separated into multiple tables, but Booking contains denormalized fields
- **3NF:** Fully normalized - all transitive dependencies removed, no denormalized fields

---

## 3NF Compliance Verification

### Booking Table Verification:
- **No CustomerName field** - Customer name only in Customer table
- **No CustomerEmail field** - Customer email only in Customer table
- **No HotelName field** - Hotel name only in Hotel table
- **No HotelCity field** - Hotel city only in Hotel table
- **No RoomTypeName field** - Room type name only in RoomType table
- **No RoomTypeMultiplier field** - Room type multiplier only in RoomType table
- **No BaseRateGBP field** - Base rate only in Hotel table
- **Only Foreign Keys** - CustomerID, HotelID, RoomTypeID, CancellationPolicyID

### Data Retrieval:
All entity data must be retrieved via JOINs:
```sql
-- Customer name: JOIN Customer table
-- Hotel name: JOIN Hotel table
-- Room type name: JOIN RoomType table
```

### Update Operations:
Updates to entity data require changes to only one table:
```sql
-- Update customer: Only Customer table
-- Update hotel: Only Hotel table
-- Update room type: Only RoomType table
```

---

## Conclusion

The 3NF design is the **fully normalized** version that removes all partial and transitive dependencies. The Booking table contains **only foreign keys and booking-specific data**, with all entity data stored in their respective tables. This ensures:

1. **No data redundancy** - Each piece of data stored once
2. **Data integrity** - Single source of truth
3. **Easier maintenance** - Update once, reflected everywhere
4. **Scalability** - Better performance for large databases

This is the **production database schema** currently in use for the World Hotels booking system.
