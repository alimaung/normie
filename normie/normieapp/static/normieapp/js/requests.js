document.addEventListener('DOMContentLoaded', function() {
    // Initialize table functionality
    initTableControls();
    
    // Initialize filters
    initFilters();
    
    // Initialize action buttons
    initActionButtons();
    
    // Initialize bulk actions
    initBulkActions();
});

function initTableControls() {
    // Select all checkbox functionality
    const selectAllCheckbox = document.getElementById('select-all');
    const rowCheckboxes = document.querySelectorAll('.row-select');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActionsVisibility();
        });
    }
    
    // Individual row selection
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBulkActionsVisibility();
        });
    });
}

function updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('select-all');
    const rowCheckboxes = document.querySelectorAll('.row-select');
    const checkedBoxes = document.querySelectorAll('.row-select:checked');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = checkedBoxes.length === rowCheckboxes.length;
        selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < rowCheckboxes.length;
    }
}

function updateBulkActionsVisibility() {
    const checkedBoxes = document.querySelectorAll('.row-select:checked');
    const bulkActionsBtn = document.querySelector('.page-actions .btn-secondary:last-child');
    
    if (bulkActionsBtn) {
        if (checkedBoxes.length > 0) {
            bulkActionsBtn.style.background = 'var(--primary-color, #1a73e8)';
            bulkActionsBtn.style.color = 'white';
            bulkActionsBtn.innerHTML = `<i class="fas fa-check-double"></i> Bulk Actions (${checkedBoxes.length})`;
        } else {
            bulkActionsBtn.style.background = 'transparent';
            bulkActionsBtn.style.color = 'var(--primary-color, #1a73e8)';
            bulkActionsBtn.innerHTML = '<i class="fas fa-check-double"></i> Bulk Actions';
        }
    }
}

function initFilters() {
    const searchInput = document.querySelector('.search-input');
    const statusFilter = document.querySelector('.filter-select');
    const priorityFilter = document.querySelectorAll('.filter-select')[1];
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTable();
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterTable();
        });
    }
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', function() {
            filterTable();
        });
    }
}

function filterTable() {
    const searchTerm = document.querySelector('.search-input')?.value.toLowerCase() || '';
    const statusFilter = document.querySelector('.filter-select')?.value || '';
    const priorityFilter = document.querySelectorAll('.filter-select')[1]?.value || '';
    const rows = document.querySelectorAll('.data-table tbody tr');
    
    rows.forEach(row => {
        const requestId = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
        const material = row.querySelector('.material-info strong')?.textContent.toLowerCase() || '';
        const status = row.querySelector('.status-badge')?.textContent.toLowerCase() || '';
        const priority = row.querySelector('.priority-badge')?.textContent.toLowerCase() || '';
        
        const matchesSearch = requestId.includes(searchTerm) || material.includes(searchTerm);
        const matchesStatus = !statusFilter || status.includes(statusFilter.toLowerCase());
        const matchesPriority = !priorityFilter || priority.includes(priorityFilter.toLowerCase());
        
        if (matchesSearch && matchesStatus && matchesPriority) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function initActionButtons() {
    // View details buttons
    document.querySelectorAll('.btn-icon[title*="View"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const requestId = row.querySelector('td:nth-child(2)').textContent;
            showNotification(`Viewing details for ${requestId}`, 'info');
        });
    });
    
    // Edit buttons
    document.querySelectorAll('.btn-icon[title*="Edit"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const requestId = row.querySelector('td:nth-child(2)').textContent;
            showNotification(`Editing ${requestId}`, 'info');
        });
    });
    
    // Approve buttons
    document.querySelectorAll('.btn-approve').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const requestId = row.querySelector('td:nth-child(2)').textContent;
            
            if (confirm(`Are you sure you want to approve ${requestId}?`)) {
                // Update status badge
                const statusBadge = row.querySelector('.status-badge');
                statusBadge.textContent = 'Approved';
                statusBadge.className = 'status-badge status-success';
                
                // Update progress
                const progressFill = row.querySelector('.progress-fill');
                const progressText = row.querySelector('.progress-indicator small');
                progressFill.style.width = '75%';
                progressText.textContent = '75% complete';
                
                // Hide approve/reject buttons
                this.style.display = 'none';
                row.querySelector('.btn-reject').style.display = 'none';
                
                showNotification(`${requestId} approved successfully`, 'success');
            }
        });
    });
    
    // Reject buttons
    document.querySelectorAll('.btn-reject').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const requestId = row.querySelector('td:nth-child(2)').textContent;
            
            if (confirm(`Are you sure you want to reject ${requestId}?`)) {
                const statusBadge = row.querySelector('.status-badge');
                statusBadge.textContent = 'Rejected';
                statusBadge.className = 'status-badge status-danger';
                
                this.style.display = 'none';
                row.querySelector('.btn-approve').style.display = 'none';
                
                showNotification(`${requestId} rejected`, 'warning');
            }
        });
    });
}

function initBulkActions() {
    const bulkActionsBtn = document.querySelector('.page-actions .btn-secondary:last-child');
    
    if (bulkActionsBtn) {
        bulkActionsBtn.addEventListener('click', function() {
            const checkedBoxes = document.querySelectorAll('.row-select:checked');
            
            if (checkedBoxes.length === 0) {
                showNotification('Please select requests to perform bulk actions', 'warning');
                return;
            }
            
            const actions = ['Approve Selected', 'Reject Selected', 'Export Selected'];
            const action = prompt(`Select action:\n${actions.map((a, i) => `${i + 1}. ${a}`).join('\n')}\n\nEnter number (1-3):`);
            
            if (action && action >= 1 && action <= 3) {
                const selectedAction = actions[action - 1];
                showNotification(`${selectedAction} - ${checkedBoxes.length} requests`, 'info');
            }
        });
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : '#2196f3'};
        color: white;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        max-width: 300px;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
} 