/**
 * Admin Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Sidebar Toggle
  const sidebar = document.getElementById('adminSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
    });
  }
  
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', function() {
      sidebar.classList.toggle('show');
    });
  }
  
  // Close sidebar on mobile when clicking outside
  document.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
        sidebar.classList.remove('show');
      }
    }
  });
  
  // Profile Dropdown
  const profileBtn = document.getElementById('profileBtn');
  const profileDropdown = document.getElementById('profileDropdown');
  
  if (profileBtn && profileDropdown) {
    profileBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      profileDropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', function() {
      profileDropdown.classList.remove('show');
    });
  }
  
  // Notification Dropdown
  const notificationBtn = document.getElementById('notificationBtn');
  const notificationDropdown = document.getElementById('notificationDropdown');
  
  if (notificationBtn && notificationDropdown) {
    notificationBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      notificationDropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', function() {
      notificationDropdown.classList.remove('show');
    });
  }
  
  // Quick Search
  const quickSearch = document.getElementById('quickSearch');
  if (quickSearch) {
    let searchTimeout;
    quickSearch.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      
      if (query.length >= 2) {
        searchTimeout = setTimeout(() => {
          performQuickSearch(query);
        }, 300);
      }
    });
  }
  
  // Mark all notifications as read
  const markAllRead = document.querySelector('.mark-all-read');
  if (markAllRead) {
    markAllRead.addEventListener('click', function() {
      // Implement notification read functionality
      console.log('Mark all as read');
    });
  }
  
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Auto-refresh dashboard stats every 5 minutes
  if (window.location.pathname.includes('/admin/dashboard') || window.location.pathname === '/admin/') {
    setInterval(refreshDashboardStats, 300000);
  }
});

/**
 * Perform quick search
 */
function performQuickSearch(query) {
  // Implement search functionality
  console.log('Searching for:', query);
  // You can make an AJAX call here to search bookings, rooms, guests
}

/**
 * Refresh dashboard statistics
 */
function refreshDashboardStats() {
  // Implement auto-refresh
  console.log('Refreshing dashboard stats');
}

/**
 * Update room status via AJAX
 */
function updateRoomStatus(roomId, newStatus) {
  fetch(`/admin/rooms/${roomId}/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ status: newStatus })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast('Room status updated successfully', 'success');
      // Update UI
      location.reload();
    } else {
      showToast(data.error || 'Failed to update room status', 'error');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast('Error updating room status', 'error');
  });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
  toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
  toast.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 5000);
}

/**
 * Confirm delete action
 */
function confirmDelete(message, callback) {
  if (confirm(message || 'Are you sure you want to delete this item?')) {
    callback();
  }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP'
  }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

/**
 * Initialize data tables
 */
function initDataTable(tableId) {
  // You can integrate DataTables library here
  const table = document.getElementById(tableId);
  if (table) {
    // Basic table initialization
    console.log('Table initialized:', tableId);
  }
}

/**
 * Export table to CSV
 */
function exportToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  let csv = [];
  const rows = table.querySelectorAll('tr');
  
  for (let i = 0; i < rows.length; i++) {
    const row = [];
    const cols = rows[i].querySelectorAll('td, th');
    
    for (let j = 0; j < cols.length; j++) {
      row.push(cols[j].innerText);
    }
    
    csv.push(row.join(','));
  }
  
  const csvContent = csv.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'export.csv';
  a.click();
  window.URL.revokeObjectURL(url);
}
