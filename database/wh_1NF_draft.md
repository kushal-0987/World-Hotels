# World Hotels – 1NF draft

Starting from the un‑normalised table, the goal of 1NF is:
- Each cell contains a single (atomic) value.
- There are no repeating groups or comma‑separated lists in one column.

## 1NF Booking table (still one big table, but cleaned)

| BookingID | BookingDate | CustomerName | CustomerEmail        | CustomerPhone | City      | HotelName          | HotelCapacity | PeakRateGBP | OffPeakRateGBP | RoomType  | RoomFeature1 | RoomFeature2 | RoomFeature3  | RoomFeature4  | CheckInDate | CheckOutDate | Nights | NumRooms | NumGuests | BasePricePerNight | CalculatedNightlyRate | TotalPriceGBP | Currency | AdvanceDays | AdvanceDiscountPercent | CancellationPolicyCode | BookingStatus |
|----------|-------------|--------------|----------------------|---------------|-----------|--------------------|---------------|-------------|----------------|-----------|-------------|-------------|--------------|--------------|-------------|--------------|--------|----------|-----------|--------------------|------------------------|---------------|----------|-------------|------------------------|------------------------|--------------|
| B001     | 2026-05-01  | Alex Smith   | alex.smith@mail.com  | 9800000011    | London    | WH London Central  | 160           | 200         | 100            | Standard  | Wifi        | TV          | Breakfast    |              | 2026-07-10  | 2026-07-13   | 3      | 1        | 1         | 200                | 200                    | 600           | GBP      | 70          | 20                     | CANC_30_60_50          | Confirmed    |
| B002     | 2026-10-01  | Alex Smith   | alex.smith@mail.com  | 9800000011    | London    | WH London Central  | 160           | 200         | 100            | Double    | Wifi        | TV          | Breakfast    | Mini-bar     | 2026-12-05  | 2026-12-10   | 5      | 1        | 2         | 200                | 220                    | 1100          | GBP      | 40          | 0                      | CANC_30_60_50          | Pending      |
| B003     | 2026-01-15  | Sara Jones   | sara.jones@mail.com  | 9800000022    | Edinburgh | WH Edinburgh City  | 120           | 160         | 80             | Family    | Wifi        | TV          | Breakfast    | Sofa-bed     | 2026-03-01  | 2026-03-04   | 3      | 2        | 4         | 120                | 180                    | 1080          | GBP      | 85          | 30                     | CANC_30_60_50          | Cancelled    |

Notes:
- Room features have been split into separate columns (RoomFeature1–4) instead of a comma‑separated list.
- CancellationPolicyDescription has been replaced with a single code (CANC_30_60_50) so the cell is atomic.
- Still one big table, so 2NF/3NF improvements will come later.

