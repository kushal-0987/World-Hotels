// Booking Page JavaScript
// Handles form validation, price calculation, and user interactions

document.addEventListener('DOMContentLoaded', function() {
  // City rates mapping
  const cityRates = {
    'London': 200, 'Edinburgh': 160, 'Manchester': 180, 'Birmingham': 150,
    'Glasgow': 150, 'Bristol': 140, 'Cardiff': 130, 'Aberdeen': 140,
    'Belfast': 130, 'New Castle': 120, 'Norwich': 130, 'Nottingham': 130,
    'Oxford': 180, 'Plymouth': 180, 'Swansea': 130, 'Bournemouth': 130, 'Kent': 140
  };

  const cityImages = {
    'London': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=300&q=80',
    'Edinburgh': 'https://images.unsplash.com/photo-1506377585622-bedcbb5f5dcc?w=300&q=80',
    'Manchester': 'https://images.unsplash.com/photo-1515586838455-8f8f940d6853?w=300&q=80',
    'Birmingham': 'https://images.unsplash.com/photo-1598881034666-3e0c2c0f3d2e?w=300&q=80',
    'Glasgow': 'https://images.unsplash.com/photo-1583225214464-9296029427aa?w=300&q=80',
    'Bristol': 'https://images.unsplash.com/photo-1580137197581-df2bb346a786?w=300&q=80',
    'default': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=300&q=80'
  };

  // Set min date to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('checkInDate').min = today;
  
  // Update check-out min date when check-in changes
  const checkInInput = document.getElementById('checkInDate');
  const checkOutInput = document.getElementById('checkOutDate');
  
  // Listen to both input and change events for real-time updates
  checkInInput.addEventListener('input', function() {
    const nextDay = new Date(this.value);
    nextDay.setDate(nextDay.getDate() + 1);
    checkOutInput.min = nextDay.toISOString().split('T')[0];
    updateSummary();
    calculatePrice();
  });
  
  checkInInput.addEventListener('change', function() {
    const nextDay = new Date(this.value);
    nextDay.setDate(nextDay.getDate() + 1);
    checkOutInput.min = nextDay.toISOString().split('T')[0];
    updateSummary();
    calculatePrice();
  });

  checkOutInput.addEventListener('input', function() {
    updateSummary();
    calculatePrice();
  });
  
  checkOutInput.addEventListener('change', function() {
    updateSummary();
    calculatePrice();
  });

  // City selection
  document.getElementById('bookingCity').addEventListener('change', function() {
    updateSummary();
    calculatePrice();
  });

  // Room type selection
  document.querySelectorAll('input[name="room_type"]').forEach(radio => {
    radio.addEventListener('change', function() {
      updateSummary();
      calculatePrice();
      validateGuestCapacity();
    });
  });

  // Quantity changes
  document.getElementById('numRooms').addEventListener('input', function() {
    updateSummary();
    calculatePrice();
  });

  document.getElementById('numGuests').addEventListener('input', function() {
    validateGuestCapacity();
    updateSummary();
    calculatePrice();
  });

  // Card number formatting (removed - payment section removed)

  // Form validation
  const form = document.getElementById('bookingForm');
  form.addEventListener('submit', function(e) {
    // Validate form before submission
    const isValid = validateForm();
    
    if (!isValid) {
      e.preventDefault();
      // Scroll to first error
      const firstError = document.querySelector('.booking-form-group.error, .terms-checkbox[style*="border"]');
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return false;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
      submitBtn.classList.add('loading');
      submitBtn.disabled = true;
    }
    form.classList.add('loading');
    
    // Allow form to submit - don't prevent default if valid
  });

  // Real-time validation
  document.querySelectorAll('input[required], select[required]').forEach(field => {
    field.addEventListener('blur', function() {
      validateField(this);
    });
  });

  // Email validation
  document.getElementById('guestEmail').addEventListener('blur', function() {
    const email = this.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
      showFieldError(this, 'Please enter a valid email address');
    } else {
      clearFieldError(this);
    }
  });

  // Phone validation
  document.getElementById('guestPhone').addEventListener('blur', function() {
    const phone = this.value.replace(/\D/g, '');
    if (phone && phone.length < 10) {
      showFieldError(this, 'Please enter a valid phone number');
    } else {
      clearFieldError(this);
    }
  });

  // Auto-save to localStorage
  setInterval(function() {
    saveFormDraft();
  }, 30000);

  // Load draft on page load
  loadFormDraft();

  // Initial summary update
  updateSummary();
  calculatePrice();
});

// Update booking summary
function updateSummary() {
  const city = document.getElementById('bookingCity').value;
  const checkIn = document.getElementById('checkInDate').value;
  const checkOut = document.getElementById('checkOutDate').value;
  const numRooms = parseInt(document.getElementById('numRooms').value) || 1;
  const numGuests = parseInt(document.getElementById('numGuests').value) || 1;
  const roomType = document.querySelector('input[name="room_type"]:checked')?.value || '';

  // Update hotel info
  if (city) {
    document.getElementById('summaryCity').textContent = city;
    document.getElementById('summaryHotelName').textContent = `WH ${city}`;
    const image = cityImages[city] || cityImages['default'];
    document.getElementById('summaryHotelImage').src = image;
  }

  // Update dates
  if (checkIn) {
    document.getElementById('summaryCheckIn').textContent = formatDate(checkIn);
  }
  if (checkOut) {
    document.getElementById('summaryCheckOut').textContent = formatDate(checkOut);
  }

  // Calculate nights - ensure dates are valid and calculate correctly
  if (checkIn && checkOut) {
    const checkInDate = new Date(checkIn + 'T00:00:00'); // Add time to avoid timezone issues
    const checkOutDate = new Date(checkOut + 'T00:00:00');
    
    // Validate dates
    if (isNaN(checkInDate.getTime()) || isNaN(checkOutDate.getTime())) {
      document.getElementById('summaryNights').textContent = '0';
      document.getElementById('pricingNights').textContent = '0';
      return;
    }
    
    // Calculate difference in milliseconds, then convert to days
    const timeDiff = checkOutDate.getTime() - checkInDate.getTime();
    const nights = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    
    // Update nights display
    const nightsValue = nights > 0 ? nights : 0;
    document.getElementById('summaryNights').textContent = nightsValue;
    document.getElementById('pricingNights').textContent = nightsValue;
  } else {
    // Reset to 0 if dates are missing
    document.getElementById('summaryNights').textContent = '0';
    document.getElementById('pricingNights').textContent = '0';
  }

  // Update rooms and guests
  document.getElementById('summaryRooms').textContent = numRooms;
  document.getElementById('summaryGuests').textContent = numGuests;

  // Update room type
  const roomTypeNames = {
    'standard': 'Standard',
    'double': 'Double',
    'family': 'Family'
  };
  document.getElementById('summaryRoomType').textContent = roomTypeNames[roomType] || '--';

  // Update progress indicator
  updateProgress();
}

// Calculate price
function calculatePrice() {
  const city = document.getElementById('bookingCity').value;
  const checkIn = document.getElementById('checkInDate').value;
  const checkOut = document.getElementById('checkOutDate').value;
  const roomType = document.querySelector('input[name="room_type"]:checked')?.value;
  const numRooms = parseInt(document.getElementById('numRooms').value) || 1;
  const numGuests = parseInt(document.getElementById('numGuests').value) || 1;

  if (!city || !checkIn || !checkOut || !roomType) {
    return;
  }

  // Get base rate
  const baseRate = cityRates[city] || 130;
  
  // Room type multiplier
  const multipliers = {
    'standard': 1.0,
    'double': 1.2,
    'family': 1.5
  };
  const multiplier = multipliers[roomType] || 1.0;
  
  // Calculate nightly rate
  let nightlyRate = baseRate * multiplier;
  
  // Extra guest charge for double room
  if (roomType === 'double' && numGuests === 2) {
    nightlyRate += baseRate * 0.1;
  }

  // Calculate nights - ensure dates are valid and calculate correctly
  const checkInDate = new Date(checkIn + 'T00:00:00'); // Add time to avoid timezone issues
  const checkOutDate = new Date(checkOut + 'T00:00:00');
  
  // Validate dates
  if (isNaN(checkInDate.getTime()) || isNaN(checkOutDate.getTime())) {
    return;
  }
  
  // Calculate difference in milliseconds, then convert to days
  const timeDiff = checkOutDate.getTime() - checkInDate.getTime();
  const nights = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
  
  if (nights <= 0) return;

  // Calculate advance days and discount
  const today = new Date();
  const checkInDate = new Date(checkIn);
  const advanceDays = Math.ceil((checkInDate - today) / (1000 * 60 * 60 * 24));
  
  let discountPercent = 0;
  if (advanceDays > 90) discountPercent = 30;  // Max discount is 30% for bookings more than 90 days in advance
  else if (advanceDays >= 80) discountPercent = 30;
  else if (advanceDays >= 60) discountPercent = 20;
  else if (advanceDays >= 45) discountPercent = 10;
  else if (advanceDays >= 10) discountPercent = 3;  // 3% discount for prebooking before 10 days

  // Calculate subtotal
  const subtotal = nightlyRate * nights * numRooms;
  const discount = subtotal * (discountPercent / 100);
  const afterDiscount = subtotal - discount;
  
  // Calculate taxes (10% of subtotal)
  const taxes = afterDiscount * 0.1;
  const total = afterDiscount + taxes;

  // Update pricing display
  document.getElementById('pricingRate').textContent = `£${nightlyRate.toFixed(2)}`;
  document.getElementById('pricingSubtotal').textContent = `£${subtotal.toFixed(2)}`;
  document.getElementById('pricingTaxes').textContent = `£${taxes.toFixed(2)}`;
  
  if (discount > 0) {
    document.getElementById('discountItem').style.display = 'flex';
    document.getElementById('pricingDiscount').textContent = `-£${discount.toFixed(2)}`;
  } else {
    document.getElementById('discountItem').style.display = 'none';
  }
  
  document.getElementById('pricingTotal').textContent = `£${total.toFixed(2)}`;

  // Show urgency message
  if (numRooms >= 2) {
    document.getElementById('urgencyMessage').style.display = 'flex';
    document.getElementById('urgencyText').textContent = `Only ${5 - numRooms} rooms left at this price!`;
  } else {
    document.getElementById('urgencyMessage').style.display = 'none';
  }
}

// Validate guest capacity
function validateGuestCapacity() {
  const roomType = document.querySelector('input[name="room_type"]:checked')?.value;
  const numGuests = parseInt(document.getElementById('numGuests').value) || 1;
  const guestsField = document.getElementById('numGuests');
  
  const maxGuests = {
    'standard': 1,
    'double': 2,
    'family': 4
  };

  if (roomType && numGuests > maxGuests[roomType]) {
    showFieldError(guestsField, `${roomType.charAt(0).toUpperCase() + roomType.slice(1)} room can have maximum ${maxGuests[roomType]} guest${maxGuests[roomType] > 1 ? 's' : ''}`);
    return false;
  } else {
    clearFieldError(guestsField);
    return true;
  }
}

// Validate form
function validateForm() {
  let isValid = true;
  
  // Clear all previous errors
  document.querySelectorAll('.booking-form-group').forEach(group => {
    group.classList.remove('error');
  });
  
  // Validate all required fields (excluding payment fields which are removed)
  document.querySelectorAll('input[required]:not([name^="card"]):not([name="upi_id"]):not([name="bank"]), select[required]:not([name="bank"])').forEach(field => {
    if (!validateField(field)) {
      isValid = false;
    }
  });

  // Validate terms checkbox
  const termsCheckbox = document.getElementById('agreeTerms');
  if (termsCheckbox && !termsCheckbox.checked) {
    const termsGroup = termsCheckbox.closest('.terms-checkbox');
    if (termsGroup) {
      termsGroup.style.border = '1px solid #E74C3C';
      termsGroup.style.borderRadius = '8px';
      termsGroup.style.padding = '12px';
      termsGroup.style.backgroundColor = '#FFF5F5';
    }
    isValid = false;
  } else if (termsCheckbox) {
    const termsGroup = termsCheckbox.closest('.terms-checkbox');
    if (termsGroup) {
      termsGroup.style.border = 'none';
      termsGroup.style.padding = '0';
      termsGroup.style.backgroundColor = 'transparent';
    }
  }

  // Validate guest capacity
  if (!validateGuestCapacity()) {
    isValid = false;
  }

  return isValid;
}

// Validate single field
function validateField(field) {
  if (field.hasAttribute('required') && !field.value.trim()) {
    showFieldError(field, 'This field is required');
    return false;
  }
  clearFieldError(field);
  return true;
}

// Show field error
function showFieldError(field, message) {
  const group = field.closest('.booking-form-group');
  if (group) {
    group.classList.add('error');
    const errorMsg = group.querySelector('.error-message');
    if (errorMsg) {
      errorMsg.textContent = message;
      errorMsg.style.display = 'block';
    }
  }
}

// Clear field error
function clearFieldError(field) {
  const group = field.closest('.booking-form-group');
  if (group) {
    group.classList.remove('error');
    const errorMsg = group.querySelector('.error-message');
    if (errorMsg) {
      errorMsg.style.display = 'none';
    }
  }
}

// Payment methods removed - no longer needed

// Toggle special requests
function toggleSpecialRequests() {
  const content = document.getElementById('specialRequests');
  const icon = document.getElementById('requestsIcon');
  content.classList.toggle('show');
  icon.classList.toggle('bi-chevron-down');
  icon.classList.toggle('bi-chevron-up');
}

// Toggle terms
function toggleTerms(type) {
  const content = document.getElementById(`${type}Content`);
  const icon = document.getElementById(`${type}Icon`);
  content.classList.toggle('show');
  icon.classList.toggle('bi-chevron-down');
  icon.classList.toggle('bi-chevron-up');
}

// Apply promo code
function applyPromoCode() {
  const promoInput = document.querySelector('input[name="promo_code"]');
  const code = promoInput.value.trim().toUpperCase();
  
  // Simple promo code validation (for demo)
  if (code === 'WELCOME10') {
    alert('Promo code applied! 10% discount will be applied at checkout.');
  } else if (code) {
    alert('Invalid promo code. Please try again.');
  }
}

// Update progress indicator
function updateProgress() {
  const city = document.getElementById('bookingCity').value;
  const checkIn = document.getElementById('checkInDate').value;
  const checkOut = document.getElementById('checkOutDate').value;
  const roomType = document.querySelector('input[name="room_type"]:checked')?.value;
  const email = document.getElementById('guestEmail').value;
  const termsCheckbox = document.getElementById('agreeTerms');
  const terms = termsCheckbox ? termsCheckbox.checked : false;

  // Step 1: Select Room
  if (city && checkIn && checkOut && roomType) {
    markStepCompleted(1);
    markStepActive(2);
  }

  // Step 2: Guest Details
  if (email) {
    markStepCompleted(2);
    if (terms) {
      markStepActive(3);
    }
  }

  // Step 3: Confirmation (after submission)
}

function markStepCompleted(step) {
  const stepEl = document.querySelector(`[data-step="${step}"]`);
  if (stepEl) {
    stepEl.classList.add('completed');
    stepEl.classList.remove('active');
  }
}

function markStepActive(step) {
  const stepEl = document.querySelector(`[data-step="${step}"]`);
  if (stepEl) {
    stepEl.classList.add('active');
  }
}

// Format date
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

// Save form draft to localStorage
function saveFormDraft() {
  const formData = {
    city: document.getElementById('bookingCity').value,
    checkIn: document.getElementById('checkInDate').value,
    checkOut: document.getElementById('checkOutDate').value,
    roomType: document.querySelector('input[name="room_type"]:checked')?.value,
    numRooms: document.getElementById('numRooms').value,
    numGuests: document.getElementById('numGuests').value,
    guestName: document.getElementById('guestName').value,
    guestEmail: document.getElementById('guestEmail').value,
    guestPhone: document.getElementById('guestPhone').value
  };
  
  localStorage.setItem('bookingDraft', JSON.stringify(formData));
}

// Load form draft from localStorage
function loadFormDraft() {
  const draft = localStorage.getItem('bookingDraft');
  if (draft) {
    try {
      const formData = JSON.parse(draft);
      if (formData.city) document.getElementById('bookingCity').value = formData.city;
      if (formData.checkIn) document.getElementById('checkInDate').value = formData.checkIn;
      if (formData.checkOut) document.getElementById('checkOutDate').value = formData.checkOut;
      if (formData.roomType) {
        const radio = document.querySelector(`input[name="room_type"][value="${formData.roomType}"]`);
        if (radio) radio.checked = true;
      }
      if (formData.numRooms) document.getElementById('numRooms').value = formData.numRooms;
      if (formData.numGuests) document.getElementById('numGuests').value = formData.numGuests;
      if (formData.guestName) document.getElementById('guestName').value = formData.guestName;
      if (formData.guestEmail) document.getElementById('guestEmail').value = formData.guestEmail;
      if (formData.guestPhone) document.getElementById('guestPhone').value = formData.guestPhone;
      
      updateSummary();
      calculatePrice();
    } catch (e) {
      console.error('Error loading draft:', e);
    }
  }
}

// Exit intent detection
let exitIntentShown = false;
document.addEventListener('mouseout', function(e) {
  if (!e.toElement && !e.relatedTarget && !exitIntentShown) {
    exitIntentShown = true;
    if (confirm('Your booking is incomplete. Stay to finish?')) {
      exitIntentShown = false;
    }
  }
});
