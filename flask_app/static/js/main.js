/**
 * ============================================
 * WORLD HOTELS - Animation & Interaction Engine
 * ============================================
 * 
 * Features:
 * 1. Scroll-triggered animations
 * 2. Parallax effects
 * 3. Counter animations
 * 4. Smooth scrolling
 * 5. Back to top button
 * 6. Navbar effects
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all animation modules
  initScrollAnimations();
  initParallaxEffects();
  initCounterAnimations();
  initBackToTop();
  initSmoothScroll();
  initNavbarEffects();
  initHoverEffects();
  initNavIndicator();
  initYear();
  initDigitalClock();
});

/**
 * ============================================
 * SCROLL-TRIGGERED ANIMATIONS
 * Smooth bidirectional scroll animations
 * ============================================
 */
function initScrollAnimations() {
  // Add animation classes to elements
  addAnimationClasses();
  
  const animatedElements = document.querySelectorAll('.animate-on-scroll, .animate-fade-up, .animate-fade-down, .animate-fade-left, .animate-fade-right, .animate-scale');
  
  if (!animatedElements.length) return;

  // Track scroll direction
  let lastScrollY = window.scrollY;
  let scrollDirection = 'down';
  
  window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    scrollDirection = currentScrollY > lastScrollY ? 'down' : 'up';
    lastScrollY = currentScrollY;
  }, { passive: true });

  const observerOptions = {
    root: null,
    rootMargin: '50px 0px -50px 0px',
    threshold: [0, 0.1, 0.2, 0.3]
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const el = entry.target;
      
      if (entry.isIntersecting && entry.intersectionRatio >= 0.1) {
        // Element entering viewport - animate in
        el.classList.add('is-visible');
        el.classList.remove('is-hidden');
      } else if (!entry.isIntersecting && scrollDirection === 'up') {
        // Element leaving viewport while scrolling up - keep visible for smooth experience
        // Don't remove is-visible immediately
      } else if (!entry.isIntersecting && entry.boundingClientRect.top > 0) {
        // Element is below viewport - reset for re-animation when scrolling down
        el.classList.remove('is-visible');
        el.classList.add('is-hidden');
      }
    });
  }, observerOptions);

  animatedElements.forEach(el => {
    el.classList.add('is-hidden');
    observer.observe(el);
  });
  
  // Initialize destinations page animations
  initDestinationsAnimations();
}

/**
 * Add animation classes to elements automatically
 */
function addAnimationClasses() {
  // Stats items - staggered animation
  document.querySelectorAll('.wh-stat-item').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', i + 1);
  });

  // Offer cards
  document.querySelectorAll('.wh-offer-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', i + 1);
  });

  // Property type cards
  document.querySelectorAll('.wh-property-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', (i % 4) + 1);
  });

  // Destination cards
  document.querySelectorAll('.wh-destination-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', (i % 3) + 1);
  });

  // Hotel cards
  document.querySelectorAll('.wh-hotel-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', (i % 4) + 1);
  });

  // Trust items
  document.querySelectorAll('.wh-trust-item').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', i + 1);
  });

  // Section headers
  document.querySelectorAll('.wh-section-title').forEach(el => {
    el.classList.add('animate-on-scroll');
  });

  // Loyalty card
  document.querySelectorAll('.wh-loyalty-card').forEach(el => {
    el.classList.add('animate-on-scroll');
  });
  
  // Destinations page elements
  document.querySelectorAll('.dest-feature-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', (i % 3) + 1);
  });
  
  document.querySelectorAll('.dest-hotel-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', (i % 4) + 1);
  });
  
  document.querySelectorAll('.dest-why-card').forEach((el, i) => {
    el.classList.add('animate-on-scroll');
    el.setAttribute('data-delay', i + 1);
  });
  
  document.querySelectorAll('.dest-section-header').forEach(el => {
    el.classList.add('animate-on-scroll');
  });
}

/**
 * ============================================
 * DESTINATIONS PAGE SPECIFIC ANIMATIONS
 * Optimized for smooth bidirectional scrolling
 * ============================================
 */
function initDestinationsAnimations() {
  // Hero parallax for destinations
  const destHero = document.querySelector('.dest-hero');
  const destHeroBg = document.querySelector('.dest-hero-bg');
  const heroContent = destHero?.querySelector('.dest-hero-content');
  const particles = destHero?.querySelectorAll('.dest-particles span');
  
  if (destHero && destHeroBg) {
    let ticking = false;
    let lastScrollY = 0;
    
    // Use lerp for smooth interpolation
    let currentY = 0;
    let targetY = 0;
    
    function lerp(start, end, factor) {
      return start + (end - start) * factor;
    }
    
    function smoothScroll() {
      const scrollY = window.scrollY;
      const heroHeight = destHero.offsetHeight;
      
      // Only update if scroll is within hero area
      if (scrollY < heroHeight * 1.2) {
        targetY = scrollY;
        
        // Smooth interpolation for buttery animations
        currentY = lerp(currentY, targetY, 0.12);
        
        // Parallax background - smooth movement
        const bgYPos = currentY * 0.35;
        const bgScale = 1 + (currentY * 0.0001);
        destHeroBg.style.transform = `translate3d(0, ${bgYPos}px, 0) scale(${bgScale})`;
        
        // Fade out hero content smoothly
        if (heroContent) {
          const fadeStart = heroHeight * 0.1;
          const fadeEnd = heroHeight * 0.5;
          let opacity = 1;
          
          if (currentY > fadeStart) {
            opacity = Math.max(0, 1 - ((currentY - fadeStart) / (fadeEnd - fadeStart)));
          }
          
          const translateY = currentY * 0.25;
          heroContent.style.opacity = opacity;
          heroContent.style.transform = `translate3d(0, ${translateY}px, 0)`;
        }
        
        // Animate particles with varied speeds - smooth
        if (particles) {
          particles.forEach((p, i) => {
            const speed = 0.08 + (i * 0.03);
            const yOffset = currentY * speed;
            p.style.transform = `translate3d(0, ${yOffset}px, 0)`;
          });
        }
      }
      
      lastScrollY = scrollY;
      
      // Continue animation loop
      if (Math.abs(currentY - targetY) > 0.5) {
        requestAnimationFrame(smoothScroll);
        ticking = true;
      } else {
        ticking = false;
      }
    }
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(smoothScroll);
        ticking = true;
      }
    }, { passive: true });
    
    // Trigger initial state
    smoothScroll();
  }
  
  // Smooth reveal for filter pills
  const filterPills = document.querySelectorAll('.dest-pill');
  filterPills.forEach((pill, i) => {
    pill.style.animationDelay = `${i * 0.05}s`;
  });
  
  // Enhanced card hover with smooth 3D effect
  const destCards = document.querySelectorAll('.dest-hotel-card, .dest-feature-card');
  
  destCards.forEach(card => {
    let animationFrame = null;
    let targetRotateX = 0;
    let targetRotateY = 0;
    let currentRotateX = 0;
    let currentRotateY = 0;
    
    function animateCard() {
      currentRotateX += (targetRotateX - currentRotateX) * 0.15;
      currentRotateY += (targetRotateY - currentRotateY) * 0.15;
      
      card.style.transform = `perspective(1000px) rotateX(${currentRotateX}deg) rotateY(${currentRotateY}deg) translateY(-6px) scale(1.015)`;
      
      if (Math.abs(targetRotateX - currentRotateX) > 0.1 || Math.abs(targetRotateY - currentRotateY) > 0.1) {
        animationFrame = requestAnimationFrame(animateCard);
      }
    }
    
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      // Subtle 3D tilt
      targetRotateX = ((y - centerY) / centerY) * 4;
      targetRotateY = ((centerX - x) / centerX) * 4;
      
      if (!animationFrame) {
        animationFrame = requestAnimationFrame(animateCard);
      }
      
      // Move image slightly for parallax effect
      const img = card.querySelector('img');
      if (img) {
        const moveX = ((x - centerX) / centerX) * 4;
        const moveY = ((y - centerY) / centerY) * 4;
        img.style.transform = `scale(1.08) translate(${moveX}px, ${moveY}px)`;
      }
    });
    
    card.addEventListener('mouseleave', () => {
      targetRotateX = 0;
      targetRotateY = 0;
      
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
      }
      
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
      card.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      
      const img = card.querySelector('img');
      if (img) {
        img.style.transform = 'scale(1)';
        img.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      }
      
      // Reset transition after animation
      setTimeout(() => {
        card.style.transition = '';
        if (img) img.style.transition = '';
      }, 500);
    });
  });
}

/**
 * ============================================
 * PARALLAX EFFECTS
 * Smooth parallax scrolling for backgrounds
 * ============================================
 */
function initParallaxEffects() {
  const parallaxElements = document.querySelectorAll('.wh-hero-bg, .parallax-bg');
  const heroSection = document.querySelector('.wh-hero');
  
  if (!parallaxElements.length && !heroSection) return;

  let ticking = false;
  let lastScrollY = window.scrollY;

  function updateParallax() {
    const scrollY = window.scrollY;
    
    // Hero parallax
    if (heroSection) {
      const heroBg = heroSection.querySelector('.wh-hero-bg');
      if (heroBg) {
        const speed = 0.4;
        const yPos = scrollY * speed;
        heroBg.style.transform = `translate3d(0, ${yPos}px, 0)`;
      }

      // Floating elements parallax
      const heroHeight = heroSection.offsetHeight;
      if (scrollY < heroHeight) {
        const progress = scrollY / heroHeight;
        heroSection.style.setProperty('--scroll-progress', progress);
      }
    }

    // Generic parallax elements
    parallaxElements.forEach(el => {
      const speed = parseFloat(el.dataset.parallaxSpeed) || 0.5;
      const rect = el.getBoundingClientRect();
      
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        const yPos = (window.innerHeight - rect.top) * speed * 0.1;
        el.style.transform = `translate3d(0, ${yPos}px, 0)`;
      }
    });

    ticking = false;
  }

  window.addEventListener('scroll', () => {
    lastScrollY = window.scrollY;
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }, { passive: true });

  // Initial update
  updateParallax();
}

/**
 * ============================================
 * COUNTER ANIMATIONS
 * Animate numbers counting up
 * ============================================
 */
function initCounterAnimations() {
  const statItems = document.querySelectorAll('.wh-stat-item strong');
  
  if (!statItems.length) return;

  const observerOptions = {
    threshold: 0.5
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const text = el.textContent;
        const match = text.match(/^([\d.]+)(\+?)$/);
        
        if (match) {
          const target = parseFloat(match[1]);
          const hasSuffix = match[2] === '+';
          animateCounter(el, target, hasSuffix);
        }
        
        observer.unobserve(el);
      }
    });
  }, observerOptions);

  statItems.forEach(el => observer.observe(el));
}

/**
 * Animate a single counter
 */
function animateCounter(element, target, hasSuffix = false) {
  const duration = 2000;
  const startTime = performance.now();
  const isDecimal = target % 1 !== 0;

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease out cubic
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = target * easeOut;

    if (isDecimal) {
      element.textContent = current.toFixed(1) + (hasSuffix ? '+' : '');
    } else {
      element.textContent = Math.floor(current) + (hasSuffix ? '+' : '');
    }

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = (isDecimal ? target.toFixed(1) : target) + (hasSuffix ? '+' : '');
    }
  }

  requestAnimationFrame(update);
}

/**
 * ============================================
 * BACK TO TOP BUTTON
 * ============================================
 */
function initBackToTop() {
  const btn = document.getElementById('whBackToTop');
  if (!btn) return;

  const showThreshold = 400;
  let ticking = false;

  function updateButton() {
    if (window.scrollY > showThreshold) {
      btn.classList.add('is-visible');
    } else {
      btn.classList.remove('is-visible');
    }
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateButton);
      ticking = true;
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  updateButton();
}

/**
 * ============================================
 * SMOOTH SCROLL
 * ============================================
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        
        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.scrollY - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/**
 * ============================================
 * NAVBAR EFFECTS
 * ============================================
 */
function initNavbarEffects() {
  const header = document.querySelector('.wh-header');
  if (!header) return;

  let lastScroll = 0;
  let ticking = false;

  function updateNavbar() {
    const currentScroll = window.scrollY;
    
    // Add shadow on scroll
    if (currentScroll > 10) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    
    // Hide/show on scroll direction (optional)
    // if (currentScroll > lastScroll && currentScroll > 200) {
    //   header.classList.add('hidden');
    // } else {
    //   header.classList.remove('hidden');
    // }
    
    lastScroll = currentScroll;
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateNavbar);
      ticking = true;
    }
  }, { passive: true });
}

/**
 * ============================================
 * NAV INDICATOR - Sliding pill effect
 * ============================================
 */
function initNavIndicator() {
  const navTabs = document.querySelector('.wh-nav-tabs');
  const tabs = document.querySelectorAll('.wh-tab');
  
  if (!navTabs || !tabs.length) return;

  // Create the sliding indicator element
  const indicator = document.createElement('div');
  indicator.className = 'wh-nav-indicator';
  navTabs.appendChild(indicator);

  // Position indicator on active tab
  function updateIndicator(tab) {
    if (!tab) return;
    
    const tabRect = tab.getBoundingClientRect();
    const navRect = navTabs.getBoundingClientRect();
    
    indicator.style.width = `${tabRect.width}px`;
    indicator.style.height = `${tabRect.height}px`;
    indicator.style.left = `${tabRect.left - navRect.left}px`;
    indicator.style.opacity = '1';
  }

  // Find and highlight active tab
  const activeTab = document.querySelector('.wh-tab.active');
  if (activeTab) {
    // Delay to ensure proper positioning after page load
    setTimeout(() => updateIndicator(activeTab), 100);
  }

  // Add hover effect
  tabs.forEach(tab => {
    tab.addEventListener('mouseenter', () => {
      updateIndicator(tab);
    });
    
    tab.addEventListener('mouseleave', () => {
      // Return to active tab
      const active = document.querySelector('.wh-tab.active');
      if (active) {
        updateIndicator(active);
      } else {
        indicator.style.opacity = '0';
      }
    });
  });

  // Update on resize
  window.addEventListener('resize', debounce(() => {
    const active = document.querySelector('.wh-tab.active');
    if (active) {
      updateIndicator(active);
    }
  }, 100));
}

/**
 * ============================================
 * HOVER EFFECTS
 * Enhanced interactions
 * ============================================
 */
function initHoverEffects() {
  // Card tilt effect on hover
  const cards = document.querySelectorAll('.wh-hotel-card, .wh-destination-card');
  
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
  });

  // Ripple effect on buttons
  const buttons = document.querySelectorAll('.wh-search-btn, .wh-btn-primary, .wh-offer-btn');
  
  buttons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      const rect = this.getBoundingClientRect();
      const ripple = document.createElement('span');
      const size = Math.max(rect.width, rect.height);
      
      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(255,255,255,0.4);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        left: ${e.clientX - rect.left - size/2}px;
        top: ${e.clientY - rect.top - size/2}px;
      `;
      
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // Add ripple animation to CSS dynamically
  if (!document.querySelector('#ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = `
      @keyframes ripple {
        to {
          transform: scale(4);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

/**
 * ============================================
 * YEAR UPDATE
 * ============================================
 */
function initYear() {
  const yearSpan = document.getElementById('whYear');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
  
  // Also update the current date in topbar
  initDateDisplay();
  initCurrencySelector();
}

/**
 * ============================================
 * DATE DISPLAY
 * ============================================
 */
function initDateDisplay() {
  const dateSpan = document.getElementById('currentDate');
  if (!dateSpan) return;
  
  function updateDate() {
    const now = new Date();
    const options = { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    };
    
    dateSpan.textContent = now.toLocaleDateString('en-GB', options);
  }
  
  // Update immediately
  updateDate();
  
  // Update every minute (in case day changes)
  setInterval(updateDate, 60000);
}

/**
 * ============================================
 * CURRENCY SELECTOR WITH CONVERSION
 * ============================================
 */

// Exchange rates (relative to GBP) - Updated January 2026
// Rates based on Bank of England and major currency exchange platforms
const exchangeRates = {
  GBP: 1,
  EUR: 1.1475,      // 1 GBP = 1.1475 EUR (Bank of England)
  USD: 1.34,        // 1 GBP = 1.34 USD (approximate)
  INR: 122.489,     // 1 GBP = 122.489 INR (Bank of England)
  AUD: 1.9960,      // 1 GBP = 1.9960 AUD (Bank of England)
  CAD: 1.8611,      // 1 GBP = 1.8611 CAD (Bank of England)
  NPR: 181.85       // 1 GBP = 181.85 NPR (Nepali Rupee - recent rate)
};

// Currency symbols
const currencySymbols = {
  GBP: '£',
  EUR: '€',
  USD: '$',
  INR: '₹',
  AUD: 'A$',
  CAD: 'C$',
  NPR: 'रू'
};

function initCurrencySelector() {
  const currencyItems = document.querySelectorAll('.wh-currency-item');
  const currencyCode = document.getElementById('currencyCode');
  const currencyFlag = document.getElementById('currencyFlag');

  if (!currencyItems.length) return;

  // Load saved currency from localStorage
  const savedCurrency = localStorage.getItem('selectedCurrency') || 'GBP';
  const savedFlag = localStorage.getItem('selectedFlag') || 'gb';
  const savedSymbol = localStorage.getItem('selectedSymbol') || '£';

  // Set initial state
  if (currencyCode) currencyCode.textContent = savedCurrency;
  if (currencyFlag) currencyFlag.src = `https://flagcdn.com/w20/${savedFlag}.png`;

  // Update active state and convert prices on page load
  currencyItems.forEach(item => {
    if (item.dataset.currency === savedCurrency) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Convert prices on page load if not GBP
  if (savedCurrency !== 'GBP') {
    convertAllPrices(savedCurrency, savedSymbol);
  }

  // Handle currency selection
  currencyItems.forEach(item => {
    item.addEventListener('click', function() {
      const currency = this.dataset.currency;
      const flag = this.dataset.flag;
      const symbol = this.dataset.symbol;

      // Update display
      if (currencyCode) currencyCode.textContent = currency;
      if (currencyFlag) currencyFlag.src = `https://flagcdn.com/w20/${flag}.png`;

      // Update active state
      currencyItems.forEach(i => i.classList.remove('active'));
      this.classList.add('active');

      // Save to localStorage
      localStorage.setItem('selectedCurrency', currency);
      localStorage.setItem('selectedFlag', flag);
      localStorage.setItem('selectedSymbol', symbol);

      // Convert all prices
      convertAllPrices(currency, symbol);

      // Close dropdown
      const dropdown = this.closest('.dropdown');
      if (dropdown) {
        const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.querySelector('.dropdown-toggle'));
        if (bsDropdown) bsDropdown.hide();
      }
      
      // Optional: Dispatch event for price updates
      window.dispatchEvent(new CustomEvent('currencyChanged', {
        detail: { currency, flag, symbol }
      }));
    });
  });
}

/**
 * Convert all prices on the page to selected currency
 */
function convertAllPrices(currency, symbol) {
  const rate = exchangeRates[currency] || 1;
  
  // Convert main price elements (with class .price-convert)
  document.querySelectorAll('.price-convert').forEach(el => {
    const gbpPrice = parseFloat(el.dataset.price);
    if (!isNaN(gbpPrice)) {
      const convertedPrice = Math.round(gbpPrice * rate);
      el.textContent = formatPrice(convertedPrice, symbol, currency);
      el.classList.add('price-updated');
      
      // Add animation
      el.style.animation = 'none';
      el.offsetHeight; // Trigger reflow
      el.style.animation = 'priceUpdate 0.4s ease-out';
    }
  });
  
  // Convert peak price elements
  document.querySelectorAll('.price-convert-inline').forEach(el => {
    const gbpPrice = parseFloat(el.dataset.price);
    if (!isNaN(gbpPrice)) {
      const convertedPrice = Math.round(gbpPrice * rate);
      const peakSpan = el.querySelector('.peak-price');
      if (peakSpan) {
        peakSpan.textContent = formatPrice(convertedPrice, symbol, currency);
        peakSpan.classList.add('price-updated');
      }
    }
  });
  
  // Show conversion notification
  showCurrencyNotification(currency, symbol);
}

/**
 * Format price with symbol
 */
function formatPrice(amount, symbol, currency) {
  // Format based on currency
  if (currency === 'INR') {
    // Indian numbering system (lakhs, crores)
    return symbol + amount.toLocaleString('en-IN');
  } else if (currency === 'NPR') {
    // Nepali numbering system (similar to Indian)
    return symbol + amount.toLocaleString('en-IN');
  } else if (currency === 'EUR') {
    return symbol + amount.toLocaleString('de-DE');
  } else {
    return symbol + amount.toLocaleString('en-GB');
  }
}

/**
 * Show currency change notification
 */
function showCurrencyNotification(currency, symbol) {
  // Remove existing notification
  const existing = document.querySelector('.currency-notification');
  if (existing) existing.remove();
  
  // Create notification
  const notification = document.createElement('div');
  notification.className = 'currency-notification';
  notification.innerHTML = `
    <i class="bi bi-check-circle-fill"></i>
    <span>Prices now shown in <strong>${currency}</strong> (${symbol})</span>
  `;
  
  document.body.appendChild(notification);
  
  // Trigger animation
  setTimeout(() => notification.classList.add('show'), 10);
  
  // Remove after delay
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

/**
 * ============================================
 * UTILITY FUNCTIONS
 * ============================================
 */

// Throttle function
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * ============================================
 * PRELOADER - Beautiful Loading Animation
 * ============================================
 */
function initPreloader() {
  const preloader = document.getElementById('whPreloader');
  if (!preloader) return;
  
  // Add loading class to body
  document.body.classList.add('loading');
  
  // Minimum display time for the loader (for aesthetic purposes)
  const minDisplayTime = 2000; // 2 seconds
  const startTime = Date.now();
  
  // Hide preloader when page is fully loaded
  function hidePreloader() {
    const elapsedTime = Date.now() - startTime;
    const remainingTime = Math.max(0, minDisplayTime - elapsedTime);
    
    setTimeout(() => {
      preloader.classList.add('loaded');
      document.body.classList.remove('loading');
      document.body.classList.add('loaded');
      
      // Trigger entrance animations after loader fades
      setTimeout(() => {
        document.querySelectorAll('.animate-on-load').forEach(el => {
          el.classList.add('is-visible');
        });
      }, 300);
      
      // Remove preloader from DOM after animation
      setTimeout(() => {
        preloader.remove();
      }, 800);
    }, remainingTime);
  }
  
  // Check if page is already loaded
  if (document.readyState === 'complete') {
    hidePreloader();
  } else {
    window.addEventListener('load', hidePreloader);
  }
}

// Initialize preloader immediately
initPreloader();

/**
 * ============================================
 * LOADING ANIMATION (Optional)
 * ============================================
 */
window.addEventListener('load', () => {
  // Additional loaded state handling
  if (!document.body.classList.contains('loaded')) {
    document.body.classList.add('loaded');
    
    // Trigger initial animations after page load
    setTimeout(() => {
      document.querySelectorAll('.animate-on-load').forEach(el => {
        el.classList.add('is-visible');
      });
    }, 100);
  }
});

/**
 * ============================================
 * ABOUT PAGE - COUNTER ANIMATION
 * ============================================
 */
function initAboutCounters() {
  const counters = document.querySelectorAll('.counter-number, .stat-number, .stat-number-new');
  if (!counters.length) return;
  
  const animateCounter = (counter) => {
    const target = parseInt(counter.dataset.count) || 0;
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
      current += step;
      if (current < target) {
        counter.textContent = Math.floor(current).toLocaleString();
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target.toLocaleString();
      }
    };
    
    updateCounter();
  };
  
  // Use Intersection Observer to trigger animation when visible
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        animateCounter(entry.target);
      }
    });
  }, { threshold: 0.5 });
  
  counters.forEach(counter => observer.observe(counter));
}

// Initialize about page counters
document.addEventListener('DOMContentLoaded', initAboutCounters);

/**
 * ============================================
 * TOAST NOTIFICATIONS
 * ============================================
 */
function initToastNotifications() {
  const toasts = document.querySelectorAll('.wh-toast');
  
  toasts.forEach((toast, index) => {
    // Stagger animation for multiple toasts
    toast.style.animationDelay = `${index * 0.1}s`;
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      dismissToast(toast);
    }, 5000 + (index * 500));
  });
}

function dismissToast(toast) {
  toast.style.transform = 'translateX(120%)';
  toast.style.opacity = '0';
  setTimeout(() => {
    toast.remove();
  }, 400);
}

// Show toast programmatically
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  
  const icons = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill'
  };
  
  const toast = document.createElement('div');
  toast.className = 'wh-toast wh-toast-show';
  toast.innerHTML = `
    <div class="wh-toast-icon">
      <i class="bi ${icons[type] || icons.info}"></i>
    </div>
    <div class="wh-toast-content">
      <span class="wh-toast-message">${message}</span>
    </div>
    <button class="wh-toast-close" onclick="dismissToast(this.parentElement)">
      <i class="bi bi-x-lg"></i>
    </button>
    <div class="wh-toast-progress"></div>
  `;
  
  container.appendChild(toast);
  
  // Auto dismiss
  setTimeout(() => {
    dismissToast(toast);
  }, 5000);
}

document.addEventListener('DOMContentLoaded', initToastNotifications);

/**
 * ============================================
 * DIGITAL CLOCK
 * Calculator-style digital clock with seconds and AM/PM
 * ============================================
 */
function initDigitalClock() {
  const clockElement = document.getElementById('digitalClock');
  if (!clockElement) return;
  
  const timeElement = clockElement.querySelector('.wh-clock-time');
  if (!timeElement) return;
  
  function updateClock() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    
    // Convert to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // 0 should be 12
    hours = String(hours).padStart(2, '0');
    
    timeElement.textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
  }
  
  // Update immediately
  updateClock();
  
  // Update every second
  setInterval(updateClock, 1000);
}
