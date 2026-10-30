# World Hotels - Sitemap and Wireframes

## Sitemap

### Public Pages
- Home (`/`)
- Hotels (`/hotels`)
- About (`/about`)
- Contact (`/contact`)
- Help (`/help`)
- Login (`/login`)
- Register (`/register`)
- Forgot Password (`/forgot-password`)
- Reset Password (`/reset-password/<token>`)

### Authenticated User Pages
- Profile (`/profile`)
- My Bookings (`/my_bookings`)
- Booking (`/booking`)
- Booking Receipt (`/booking/<booking_id>/receipt`)
- Cancel Booking Preview (`/cancel_booking/<booking_id>/preview`)
- Cancel Booking (`/cancel_booking/<booking_id>`)

### Admin Pages
- Admin Dashboard (`/admin/dashboard`)
- Admin Bookings (`/admin/bookings`)
- Add Booking (`/admin/bookings/add`)
- Booking Status Update (`/admin/bookings/<booking_id>/status`)
- Booking Receipt (`/admin/bookings/<booking_id>/receipt`)
- Hotels Management (`/admin/hotels`)
- Add Hotel (`/admin/hotels/add`)
- Edit Hotel (`/admin/hotels/<hotel_id>/edit`)
- Rooms Management (`/admin/rooms`)
- Add Room (`/admin/rooms/add`)
- Edit Room (`/admin/rooms/<room_id>/edit`)
- Bulk Create Rooms (`/admin/rooms/bulk_create`)
- Customers (`/admin/customers`)
- Maintenance (`/admin/maintenance`)
- Pricing (`/admin/pricing`)
- Reports (`/admin/reports`)
- Settings (`/admin/settings`)
- Users Management (`/admin/users`)
- Toggle User Status (`/admin/users/<user_id>/toggle-status`)

---

## Wireframes

### Public Pages

#### Home Page (`/`)
**Layout Structure:**
- Top navigation bar with logo, search bar, and user account links
- Hero section with search functionality for destination, check-in, and check-out dates
- Featured hotels section displaying active hotels with city, capacity, and pricing
- Statistics section showing total hotels, happy guests, and average rating
- Footer with links to About, Contact, Help, and social media

**Key Elements:**
- Search bar with destination dropdown and date pickers
- Hotel cards showing city name, capacity, peak rate, and off-peak rate
- Call-to-action buttons for booking and browsing hotels

#### Hotels Page (`/hotels`)
**Layout Structure:**
- Top navigation bar consistent with home page
- Filter section with city pills for quick filtering
- Hotel grid displaying all active hotels
- Each hotel card shows name, city, capacity, peak rate, off-peak rate, and rating
- Search functionality integrated in header

**Key Elements:**
- City filter pills for destination selection
- Hotel cards with detailed information
- Responsive grid layout adapting to screen size

#### About Page (`/about`)
**Layout Structure:**
- Top navigation bar
- Hero section with company introduction
- Mission and vision section
- Timeline showing company milestones
- Team section displaying leadership members with photos and roles
- Statistics counter section
- Footer

**Key Elements:**
- Company story and values
- Leadership team cards with photos
- Timeline visualization
- Key statistics and achievements

#### Contact Page (`/contact`)
**Layout Structure:**
- Top navigation bar
- Page header with contact information
- Contact form with name, email, phone, subject, and message fields
- Contact information cards displaying address, phone, and email
- Location section if applicable
- Footer

**Key Elements:**
- Contact form for inquiries
- Contact information display
- Form validation and submission feedback

#### Help Page (`/help`)
**Layout Structure:**
- Top navigation bar
- Help center header with search functionality
- Quick links to common help categories
- FAQ sections organized by topic with accordion interface
- Contact support section
- Footer

**Key Elements:**
- Searchable help content
- Categorized FAQ sections
- Accordion interface for easy navigation
- Support contact options

#### Login Page (`/login`)
**Layout Structure:**
- Fullscreen background with hotel imagery
- Left side branding with logo and welcome message
- Right side login form card
- Email and password input fields
- Remember me checkbox
- Forgot password link
- Link to registration page
- Security badge indicating SSL encryption

**Key Elements:**
- Clean login form
- Password visibility toggle
- Form validation
- Redirect to booking page if accessed from booking flow

#### Register Page (`/register`)
**Layout Structure:**
- Two-column layout
- Left side registration form
- Right side benefits and statistics
- Registration form with full name, email, password fields
- Password strength indicator
- Terms and conditions checkbox
- Newsletter subscription option
- Link to login page

**Key Elements:**
- Registration form with validation
- Password strength meter
- Benefits showcase
- Terms acceptance checkbox

#### Forgot Password Page (`/forgot-password`)
**Layout Structure:**
- Centered form card
- Email input field
- Submit button
- Link back to login page
- Instructions for password reset process

**Key Elements:**
- Simple email input form
- Clear instructions
- Success message after submission

#### Reset Password Page (`/reset-password/<token>`)
**Layout Structure:**
- Centered form card
- New password input field
- Confirm password input field
- Submit button
- Token validation message

**Key Elements:**
- Password reset form
- Password confirmation field
- Token expiration handling

---

### Authenticated User Pages

#### Profile Page (`/profile`)
**Layout Structure:**
- Profile header with gradient background
- Profile photo with upload functionality
- User information display
- Quick statistics showing total bookings, last booking, and login method
- Two-column content grid
- Left column: Personal information form, security settings
- Right column: Booking summary, preferences

**Key Elements:**
- Editable profile information
- Photo upload with preview
- Security settings including password change
- Booking statistics
- Form validation and save functionality

#### My Bookings Page (`/my_bookings`)
**Layout Structure:**
- Page header with title
- Booking cards displaying booking details
- Each card shows hotel name, check-in date, check-out date, room type, total price, and status
- Cancel booking button for eligible bookings
- View receipt link for each booking
- Empty state message when no bookings exist

**Key Elements:**
- Booking cards with status indicators
- Filter options by status
- Cancel booking functionality
- Receipt access
- Responsive card layout

#### Booking Page (`/booking`)
**Layout Structure:**
- Page header
- Booking form with destination selection
- Date pickers for check-in and check-out
- Room type selection with capacity information
- Number of rooms and guests selection
- Price calculation display
- Booking summary section
- Submit booking button
- Trust badges and security indicators

**Key Elements:**
- Multi-step booking form
- Real-time price calculation
- Date validation
- Room capacity validation
- Booking confirmation flow

#### Booking Receipt Page (`/booking/<booking_id>/receipt`)
**Layout Structure:**
- Receipt header with booking reference
- Booking details section
- Hotel information
- Guest information
- Payment summary
- Print receipt button
- Download receipt option
- Return to bookings link

**Key Elements:**
- Printable receipt format
- Complete booking information
- Payment details
- Booking reference number

#### Cancel Booking Pages (`/cancel_booking/<booking_id>/preview` and `/cancel_booking/<booking_id>`)
**Layout Structure:**
- Cancellation preview showing booking details
- Cancellation policy information
- Refund calculation display
- Cancellation charges breakdown
- Confirm cancellation button
- Cancel action button

**Key Elements:**
- Cancellation policy display
- Refund calculation
- Charge breakdown
- Confirmation dialog

---

### Admin Pages

#### Admin Dashboard (`/admin/dashboard`)
**Layout Structure:**
- Admin sidebar navigation
- Top admin header with user profile
- Dashboard cards showing key metrics
- Recent bookings table
- Revenue charts
- Quick action buttons
- Statistics overview

**Key Elements:**
- Key performance indicators
- Revenue visualization
- Recent activity feed
- Quick access to common tasks

#### Admin Bookings (`/admin/bookings`)
**Layout Structure:**
- Admin sidebar and header
- Bookings table with filters
- Search and filter options
- Booking status management
- View receipt functionality
- Add booking button
- Export options

**Key Elements:**
- Comprehensive bookings table
- Status filter dropdown
- Search functionality
- Bulk actions
- Individual booking management

#### Hotels Management (`/admin/hotels`)
**Layout Structure:**
- Admin sidebar and header
- Hotels table with all hotel information
- Add hotel button
- Edit and delete actions for each hotel
- Hotel status toggle
- Capacity and pricing display

**Key Elements:**
- Hotels data table
- Add and edit forms
- Status management
- Pricing information display

#### Rooms Management (`/admin/rooms`)
**Layout Structure:**
- Admin sidebar and header
- Rooms table filtered by hotel
- Room details including number, type, status, and pricing
- Add room button
- Bulk room creation functionality
- Edit and maintenance actions
- Room status indicators

**Key Elements:**
- Rooms data table
- Hotel filter
- Room type management
- Maintenance status
- Bulk operations

#### Customers Page (`/admin/customers`)
**Layout Structure:**
- Admin sidebar and header
- Customers table with contact information
- Customer booking history
- Search and filter options
- Customer details view
- Contact information display

**Key Elements:**
- Customer data table
- Search functionality
- Booking history per customer
- Contact details

#### Maintenance Page (`/admin/maintenance`)
**Layout Structure:**
- Admin sidebar and header
- Maintenance requests table
- Room maintenance status
- Schedule maintenance functionality
- Maintenance history
- Status updates

**Key Elements:**
- Maintenance requests list
- Room status indicators
- Scheduling interface
- History tracking

#### Reports Page (`/admin/reports`)
**Layout Structure:**
- Admin sidebar and header
- Revenue reports with charts
- Booking statistics
- Hotel performance metrics
- Top customers list
- Profit and loss analysis
- Date range filters

**Key Elements:**
- Revenue visualization charts
- Statistical summaries
- Performance metrics
- Exportable reports

#### Settings Page (`/admin/settings`)
**Layout Structure:**
- Admin sidebar and header
- Settings categories
- System configuration options
- Email settings
- General preferences
- Save settings button

**Key Elements:**
- Configuration forms
- System preferences
- Settings categories

#### Users Management (`/admin/users`)
**Layout Structure:**
- Admin sidebar and header
- Users table with roles and status
- User activation and deactivation
- Role management
- User search functionality
- Account status indicators

**Key Elements:**
- Users data table
- Role assignment
- Status toggle
- Search and filter

---

## Navigation Structure

### Public Navigation
- Logo (links to home)
- Search bar
- Hotels
- About
- Contact
- Help
- Login / Register (when not authenticated)
- User menu (when authenticated)

### Authenticated User Navigation
- Logo (links to home)
- Search bar
- Hotels
- My Bookings
- Profile
- Logout

### Admin Navigation
- Admin sidebar with collapsible menu
- Dashboard
- Bookings
- Hotels
- Rooms
- Customers
- Maintenance
- Pricing
- Reports
- Settings
- Users
- Logout

---

## Common UI Components

### Header
- Sticky top navigation bar
- Logo on the left
- Search functionality in center
- User account menu on the right
- Responsive mobile menu

### Footer
- Company information
- Quick links to main pages
- Contact information
- Social media links
- Copyright notice

### Forms
- Consistent input styling
- Validation messages
- Required field indicators
- Submit buttons with loading states
- Error and success notifications

### Cards
- Consistent card design across pages
- Hover effects
- Shadow and border styling
- Responsive grid layouts

### Buttons
- Primary action buttons
- Secondary buttons
- Icon buttons
- Disabled states
- Loading states
