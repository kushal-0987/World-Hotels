# World Hotels – 2NF (Second Normal Form) Design

## Overview
This document describes the Second Normal Form (2NF) database design for World Hotels booking system.

**2NF Definition:** A table is in 2NF if:
1. It is in 1NF (First Normal Form)
2. All non-key attributes depend on the **entire** primary key (no partial dependencies)

## Starting Point
From 1NF: A single wide booking table with atomic values but still containing repeated customer, hotel, and room type information.

## Goal
Remove partial dependencies by ensuring all non-key attributes depend on the complete primary key. However, 2NF may still contain some transitive dependencies (which are removed in 3NF).

---

## Identified Entities

The main entities identified from the 1NF table:

1. **Customer** - Stores unique customer information
2. **Hotel** - Stores hotel and city information with rates
3. **RoomType** - Defines room types and their pricing multipliers
4. **CancellationPolicy** - Stores cancellation policy rules
5. **Booking** - Stores booking transactions (with some denormalized fields)

---

## 2NF Table Designs

### 1. Customer Table

Stores unique customer information separately to avoid repetition in booking records.

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
| CreatedAt     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| UpdatedAt     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update time |

**Normalization Reason:** Customer data was repeated in every booking row in 1NF. In 2NF, each customer is stored once and referenced via CustomerID.

---

### 2. Hotel Table

Stores hotel information and standard room rates.

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

**Normalization Reason:** Hotel name, city, capacity, and rates were repeated for every booking in 1NF. In 2NF, they depend only on HotelID.

---

### 3. RoomType Table

Defines different room types and their price multipliers.

**Primary Key:** `RoomTypeID`

| Field              | Type          | Constraints | Notes                                           |
|--------------------|---------------|-------------|-------------------------------------------------|
| RoomTypeID         | INT           | PK, AUTO_INCREMENT | Unique identifier |
| RoomTypeName       | VARCHAR(30)   | NOT NULL    | Standard / Double / Family |
| PriceMultiplier    | DECIMAL(4,2)  | NOT NULL    | e.g. 1.0 for Standard, 1.2 for Double, 1.5 for Family |
| MaxGuests          | INT           | NOT NULL    | Maximum occupancy (1, 2, or 4) |
| Description        | VARCHAR(255)  | NULL        | Room type description |

**Normalization Reason:** Room type name and pricing rules were mixed into booking rows in 1NF. In 2NF, they belong to a separate entity that can be reused by many bookings.

---

### 4. CancellationPolicy Table

Stores the rules for cancellation charges.

**Primary Key:** `CancellationPolicyID`

| Field                   | Type          | Constraints | Notes                                           |
|-------------------------|---------------|-------------|-------------------------------------------------|
| CancellationPolicyID    | INT           | PK, AUTO_INCREMENT | Unique identifier |
| PolicyCode              | VARCHAR(20)   | NOT NULL, UNIQUE | e.g. "FLEX" |
| Description             | VARCHAR(255)  | NULL        | Text description of the policy |
| ChargeBetween30And60Pct | INT           | NOT NULL    | Percentage charge (e.g. 50) |
| ChargeUnder30DaysPct    | INT           | NOT NULL    | Percentage charge (e.g. 100) |

**Normalization Reason:** In 1NF, the full policy text was repeated in every booking. In 2NF, the booking stores a foreign key to this table.

---

### 5. Booking Table (2NF - WITH Denormalized Fields)

Stores each booking and links to other entities. **In 2NF, this table includes denormalized fields** (which violate 3NF but are acceptable in 2NF).

**Primary Key:** `BookingID`  
**Foreign Keys:** CustomerID, HotelID, RoomTypeID, CancellationPolicyID

| Field                   | Type          | Constraints | Notes                                   |
|-------------------------|---------------|-------------|-----------------------------------------|
| BookingID               | INT           | PK, AUTO_INCREMENT | Unique identifier |
| BookingYear             | YEAR          | NOT NULL    | Year of booking |
| BookingDate             | DATE          | NOT NULL    | Date booking was made |
| CustomerID              | INT           | NOT NULL, FK | → Customer.CustomerID |
| **CustomerName**        | **VARCHAR(100)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| **CustomerEmail**       | **VARCHAR(150)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| HotelID                 | INT           | NOT NULL, FK | → Hotel.HotelID |
| **HotelName**           | **VARCHAR(120)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| **HotelCity**           | **VARCHAR(80)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| RoomTypeID              | INT           | NOT NULL, FK | → RoomType.RoomTypeID |
| **RoomTypeName**        | **VARCHAR(30)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| **RoomTypeMultiplier**  | **DECIMAL(4,2)** | **NOT NULL** | **Denormalized (violates 3NF)** |
| CancellationPolicyID    | INT           | NOT NULL, FK | → CancellationPolicy.CancellationPolicyID |
| CheckInDate             | DATE          | NOT NULL    | Check-in date |
| CheckOutDate            | DATE          | NOT NULL    | Check-out date |
| Nights                  | INT           | NOT NULL    | Number of nights |
| NumRooms                | INT           | NOT NULL    | Number of rooms booked |
| NumGuests               | INT           | NOT NULL    | Number of guests |
| Currency                | VARCHAR(10)   | DEFAULT 'GBP' | Currency code |
| AdvanceDays             | INT           | NULL        | Days between booking and check-in |
| AdvanceDiscountPercent  | DECIMAL(5,2)  | NULL        | Discount percentage (0, 10, 20, 30) |
| **BaseRateGBP**         | **DECIMAL(8,2)** | **NOT NULL** | **Denormalized (could be from Hotel table)** |
| CalculatedNightlyRate   | DECIMAL(8,2)  | NULL        | Rate after multipliers/discounts |
| TotalPriceGBP           | DECIMAL(10,2) | NULL        | Final booking price |
| BookingStatus           | ENUM          | DEFAULT 'Pending' | Pending/Confirmed/Cancelled/Completed |
| CancellationChargeGBP   | DECIMAL(10,2) | DEFAULT 0   | Cancellation charge if applicable |
| SpecialRequests         | TEXT          | NULL        | Special requests from customer |
| CreatedAt               | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| UpdatedAt               | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update time |

**2NF Compliance:**
- All non-key attributes depend on the **entire** primary key (BookingID)
- No partial dependencies (BookingID is a simple key, not composite)
- Contains transitive dependencies (denormalized fields violate 3NF)

**Denormalized Fields (2NF Characteristic):**
The following fields are stored redundantly in the Booking table:
- `CustomerName`, `CustomerEmail` (also in Customer table)
- `HotelName`, `HotelCity` (also in Hotel table)
- `RoomTypeName`, `RoomTypeMultiplier` (also in RoomType table)
- `BaseRateGBP` (could be calculated from Hotel table)

**Why This is 2NF:**
- These fields don't create partial dependencies (they depend on BookingID, not part of a composite key)
- However, they create transitive dependencies (CustomerName depends on CustomerID, which depends on BookingID)
- Transitive dependencies are removed in 3NF, but are acceptable in 2NF

---

### 6. Cancellation Table (2NF)

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

## 2NF Characteristics Summary

### What 2NF Achieves:
1. **Removes Partial Dependencies:** All non-key attributes depend on the entire primary key
2. **Separates Entities:** Customer, Hotel, RoomType, and CancellationPolicy are in separate tables
3. **Reduces Repetition:** Entity data is stored once and referenced via foreign keys

### What 2NF Allows (but 3NF removes):
1. **Transitive Dependencies:** Denormalized fields in Booking table
   - CustomerName depends on CustomerID (which depends on BookingID)
   - HotelName depends on HotelID (which depends on BookingID)
   - RoomTypeName depends on RoomTypeID (which depends on BookingID)

2. **Data Redundancy:** Same data stored in multiple places
   - Customer name in both Customer and Booking tables
   - Hotel name in both Hotel and Booking tables

### Benefits of 2NF Approach:
- Simpler queries (no JOINs needed for basic booking data)
- Faster reads (all data in one table)
- Easier to understand for simple queries

### Drawbacks of 2NF Approach:
- Data redundancy (more storage space)
- Update anomalies (must update multiple tables)
- Risk of data inconsistency
- Not fully normalized (violates 3NF)

---

## Example Queries (2NF)

### Simple Query (No JOINs needed):
```sql
-- Get booking with customer and hotel names directly
SELECT 
    BookingID,
    CustomerName,  -- Directly from Booking table
    HotelName,     -- Directly from Booking table
    RoomTypeName,  -- Directly from Booking table
    TotalPriceGBP
FROM Booking_2NF
WHERE BookingID = 1;
```

### Update Scenario (2NF):
```sql
-- If customer changes name, must update BOTH tables:
UPDATE Customer_2NF SET CustomerName = 'New Name' WHERE CustomerID = 1;
UPDATE Booking_2NF SET CustomerName = 'New Name' WHERE CustomerID = 1;
-- Multiple updates required!
```

---

## Normalization Progression

- **Un-normalised:** One wide table with all data mixed together
- **1NF:** Atomic values, but still one large table with repetition
- **2NF:** Separated into multiple tables, but Booking contains denormalized fields
- **3NF:** Fully normalized - all transitive dependencies removed

---

## Conclusion

The 2NF design successfully removes partial dependencies by ensuring all attributes depend on the complete primary key. However, it intentionally includes denormalized fields in the Booking table to demonstrate the difference between 2NF and 3NF. These denormalized fields violate 3NF but are acceptable in 2NF as they don't create partial dependencies.
