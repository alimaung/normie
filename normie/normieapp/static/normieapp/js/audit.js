document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initSearch();
    
    // Initialize filters
    initFilters();
    
    // Initialize audit entry interactions
    initAuditEntries();
    
    // Initialize compliance cards
    initComplianceCards();
    
    // Auto-refresh functionality
    initAutoRefresh();
});

function initSearch() {
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterAuditEntries();
            }, 300); // Debounce search
        });
        
        // Search on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                clearTimeout(searchTimeout);
                filterAuditEntries();
            }
        });
    }
    
    // Refresh button
    const refreshBtn = document.querySelector('.timeline-controls .btn-secondary');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.querySelector('i').classList.add('fa-spin');
            
            setTimeout(() => {
                this.querySelector('i').classList.remove('fa-spin');
                showNotification('Audit trail refreshed', 'success');
                
                // Simulate new entries (could add new entries here)
                highlightRecentEntries();
            }, 1000);
        });
    }
}

function initFilters() {
    const filterInputs = document.querySelectorAll('.filter-group input, .filter-group select');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            filterAuditEntries();
        });
    });
    
    // Apply filters button
    const applyFiltersBtn = document.querySelector('.audit-filters .btn-primary');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            filterAuditEntries();
            showNotification('Filters applied', 'info');
        });
    }
    
    // Filter tag removal
    document.querySelectorAll('.filter-tag .remove').forEach(removeBtn => {
        removeBtn.addEventListener('click', function() {
            const tag = this.parentElement;
            tag.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                tag.remove();
                filterAuditEntries();
            }, 300);
        });
    });
}

function filterAuditEntries() {
    const searchTerm = document.querySelector('.search-box input')?.value.toLowerCase() || '';
    const actionType = document.getElementById('action-type')?.value || '';
    const user = document.getElementById('user')?.value || '';
    const severity = document.getElementById('severity')?.value || '';
    const ipAddress = document.getElementById('ip-address')?.value || '';
    
    const auditEntries = document.querySelectorAll('.audit-entry');
    let visibleCount = 0;
    
    auditEntries.forEach(entry => {
        const action = entry.querySelector('.audit-action')?.textContent.toLowerCase() || '';
        const description = entry.querySelector('.audit-description')?.textContent.toLowerCase() || '';
        const entryUser = entry.querySelector('.audit-meta span:first-child')?.textContent.toLowerCase() || '';
        const severityBadge = entry.querySelector('.severity-badge')?.textContent.toLowerCase() || '';
        const entryIP = entry.querySelector('.audit-meta span:nth-child(3)')?.textContent || '';
        
        // Get action type from icon
        const icon = entry.querySelector('.audit-icon');
        let entryActionType = '';
        if (icon.classList.contains('create')) entryActionType = 'create';
        else if (icon.classList.contains('update')) entryActionType = 'update';
        else if (icon.classList.contains('delete')) entryActionType = 'delete';
        else if (icon.classList.contains('approve')) entryActionType = 'approve';
        else if (icon.classList.contains('reject')) entryActionType = 'reject';
        else if (icon.classList.contains('login')) entryActionType = 'login';
        else if (icon.classList.contains('export')) entryActionType = 'export';
        
        const matchesSearch = !searchTerm || action.includes(searchTerm) || description.includes(searchTerm);
        const matchesActionType = !actionType || entryActionType === actionType;
        const matchesUser = !user || entryUser.includes(user.toLowerCase());
        const matchesSeverity = !severity || severityBadge.includes(severity);
        const matchesIP = !ipAddress || entryIP.includes(ipAddress);
        
        if (matchesSearch && matchesActionType && matchesUser && matchesSeverity && matchesIP) {
            entry.style.display = '';
            visibleCount++;
        } else {
            entry.style.display = 'none';
        }
    });
    
    // Update timeline header with count
    const timelineHeader = document.querySelector('.timeline-header h3');
    if (timelineHeader) {
        timelineHeader.innerHTML = `<i class="fas fa-history"></i> Audit Trail (${visibleCount} entries)`;
    }
}

function initAuditEntries() {
    const auditEntries = document.querySelectorAll('.audit-entry');
    
    auditEntries.forEach(entry => {
        // Click to expand/collapse details
        entry.addEventListener('click', function() {
            const isExpanded = this.classList.contains('expanded');
            
            // Remove expanded class from all entries
            auditEntries.forEach(e => e.classList.remove('expanded'));
            
            if (!isExpanded) {
                this.classList.add('expanded');
                showAuditDetails(this);
            }
        });
        
        // Hover effects
        entry.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        });
        
        entry.addEventListener('mouseleave', function() {
            if (!this.classList.contains('expanded')) {
                this.style.transform = 'translateX(0)';
                this.style.boxShadow = '';
            }
        });
    });
}

function showAuditDetails(entry) {
    // Check if details already exist
    let detailsDiv = entry.querySelector('.audit-details');
    
    if (!detailsDiv) {
        detailsDiv = document.createElement('div');
        detailsDiv.className = 'audit-details';
        detailsDiv.style.cssText = `
            margin-top: 1rem;
            padding: 1rem;
            background: var(--card-header-bg, #f8f9fa);
            border-radius: 4px;
            border-left: 4px solid var(--primary-color, #1a73e8);
            font-size: 0.9rem;
        `;
        
        // Generate mock details based on action type
        const action = entry.querySelector('.audit-action').textContent;
        let details = '';
        
        if (action.includes('Request')) {
            details = `
                <strong>Request Details:</strong><br>
                • Request ID: REQ-2024-001<br>
                • Material: Steel Pipes<br>
                • Quantity: 50 units<br>
                • Estimated Cost: $6,250<br>
                • Justification: Construction project requirements<br>
                • Department: Engineering
            `;
        } else if (action.includes('Standard')) {
            details = `
                <strong>Standard Modification:</strong><br>
                • Standard: ISO 9001:2015 v2.1<br>
                • Changes: Updated compliance requirements<br>
                • Sections Modified: 4.2, 7.1, 8.3<br>
                • Review Status: Pending approval<br>
                • Next Review Date: 2024-06-15
            `;
        } else if (action.includes('Login')) {
            details = `
                <strong>Login Information:</strong><br>
                • Device: Chrome on Windows 10<br>
                • Location: Office Building A<br>
                • Session Duration: 4h 23m<br>
                • Previous Login: 2024-03-14 09:15<br>
                • Failed Attempts: 0
            `;
        } else {
            details = `
                <strong>Additional Information:</strong><br>
                • Transaction ID: TXN-${Math.random().toString(36).substr(2, 9).toUpperCase()}<br>
                • System Module: ${action.split(' ')[0]} Management<br>
                • Data Integrity: Verified<br>
                • Backup Status: Completed<br>
                • Compliance Check: Passed
            `;
        }
        
        detailsDiv.innerHTML = details;
        entry.querySelector('.audit-content').appendChild(detailsDiv);
    }
    
    // Animate details appearance
    detailsDiv.style.opacity = '0';
    detailsDiv.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
        detailsDiv.style.transition = 'all 0.3s ease';
        detailsDiv.style.opacity = '1';
        detailsDiv.style.transform = 'translateY(0)';
    }, 100);
}

function initComplianceCards() {
    const complianceCards = document.querySelectorAll('.compliance-card');
    
    complianceCards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('.compliance-title').textContent;
            const score = this.querySelector('.compliance-score').textContent;
            
            showNotification(`${title}: ${score} compliance score`, 'info');
            
            // Animate progress bar
            const progressFill = this.querySelector('.progress-fill');
            const currentWidth = progressFill.style.width;
            progressFill.style.width = '0%';
            
            setTimeout(() => {
                progressFill.style.transition = 'width 1s ease';
                progressFill.style.width = currentWidth;
            }, 100);
        });
        
        // Hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
        });
    });
}

function initAutoRefresh() {
    let autoRefreshInterval;
    let isAutoRefreshEnabled = false;
    
    // Add auto-refresh toggle (could be added to UI)
    const autoRefreshBtn = document.createElement('button');
    autoRefreshBtn.className = 'btn btn-secondary btn-sm';
    autoRefreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Auto-refresh: OFF';
    autoRefreshBtn.style.marginLeft = '0.5rem';
    
    const timelineControls = document.querySelector('.timeline-controls');
    if (timelineControls) {
        timelineControls.appendChild(autoRefreshBtn);
        
        autoRefreshBtn.addEventListener('click', function() {
            isAutoRefreshEnabled = !isAutoRefreshEnabled;
            
            if (isAutoRefreshEnabled) {
                this.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Auto-refresh: ON';
                this.style.background = 'var(--primary-color, #1a73e8)';
                this.style.color = 'white';
                
                autoRefreshInterval = setInterval(() => {
                    highlightRecentEntries();
                    showNotification('Audit trail updated', 'info');
                }, 30000); // Refresh every 30 seconds
                
            } else {
                this.innerHTML = '<i class="fas fa-sync-alt"></i> Auto-refresh: OFF';
                this.style.background = 'transparent';
                this.style.color = 'var(--primary-color, #1a73e8)';
                
                clearInterval(autoRefreshInterval);
            }
        });
    }
}

function highlightRecentEntries() {
    const auditEntries = document.querySelectorAll('.audit-entry');
    
    // Highlight first few entries as "recent"
    auditEntries.forEach((entry, index) => {
        if (index < 3) {
            entry.style.background = 'linear-gradient(90deg, #e3f2fd 0%, transparent 100%)';
            entry.style.borderLeft = '4px solid var(--primary-color, #1a73e8)';
            
            setTimeout(() => {
                entry.style.background = '';
                entry.style.borderLeft = '';
            }, 3000);
        }
    });
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
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
        max-width: 350px;
        animation: slideIn 0.3s ease;
    `;
    
    // Add slide-in animation
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes fadeOut {
                from { opacity: 1; transform: scale(1); }
                to { opacity: 0; transform: scale(0.8); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => notification.remove(), 300);
        }
    }, 4000);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    });
} 