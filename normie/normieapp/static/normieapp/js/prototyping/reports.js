document.addEventListener('DOMContentLoaded', function() {
    // Initialize report categories
    initReportCategories();
    
    // Initialize report generator
    initReportGenerator();
    
    // Initialize report actions
    initReportActions();
    
    // Initialize analytics interactions
    initAnalytics();
});

function initReportCategories() {
    const categories = document.querySelectorAll('.report-category');
    
    categories.forEach(category => {
        category.addEventListener('click', function() {
            // Remove active class from all categories
            categories.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked category
            this.classList.add('active');
            
            // Update report generator based on selection
            const categoryType = this.querySelector('h4').textContent.toLowerCase();
            updateReportGenerator(categoryType);
            
            // Visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
        
        // Hover effects
        category.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.borderColor = 'var(--primary-color, #1a73e8)';
                this.style.background = 'var(--primary-light, #f8f9fa)';
            }
        });
        
        category.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.borderColor = 'var(--border-color, #e0e0e0)';
                this.style.background = '';
            }
        });
    });
}

function updateReportGenerator(categoryType) {
    const reportTypeSelect = document.getElementById('report-type');
    if (!reportTypeSelect) return;
    
    // Clear existing options
    reportTypeSelect.innerHTML = '';
    
    let options = [];
    switch(categoryType) {
        case 'inventory':
            options = [
                { value: 'stock-levels', text: 'Stock Levels Report' },
                { value: 'usage-patterns', text: 'Usage Patterns' },
                { value: 'reorder-alerts', text: 'Reorder Alerts' }
            ];
            break;
        case 'compliance':
            options = [
                { value: 'iso-compliance', text: 'ISO Compliance Report' },
                { value: 'audit-findings', text: 'Audit Findings' },
                { value: 'policy-adherence', text: 'Policy Adherence' }
            ];
            break;
        case 'financial':
            options = [
                { value: 'cost-analysis', text: 'Cost Analysis' },
                { value: 'budget-variance', text: 'Budget Variance' },
                { value: 'roi-report', text: 'ROI Report' }
            ];
            break;
        default:
            options = [
                { value: 'general', text: 'General Report' },
                { value: 'summary', text: 'Summary Report' }
            ];
    }
    
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        reportTypeSelect.appendChild(optionElement);
    });
}

function initReportGenerator() {
    const generatorForm = document.querySelector('.generator-form');
    
    if (generatorForm) {
        generatorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const reportType = document.getElementById('report-type')?.value;
            const startDate = document.getElementById('start-date')?.value;
            const endDate = document.getElementById('end-date')?.value;
            const format = document.getElementById('format')?.value;
            
            if (!reportType || !startDate || !endDate) {
                showNotification('Please fill in all required fields', 'warning');
                return;
            }
            
            // Simulate report generation
            generateReport(reportType, startDate, endDate, format);
        });
    }
}

function generateReport(type, startDate, endDate, format) {
    const submitBtn = document.querySelector('.generator-form .btn-primary');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    submitBtn.disabled = true;
    
    // Simulate generation time
    setTimeout(() => {
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        // Show success notification
        showNotification(`${format.toUpperCase()} report generated successfully!`, 'success');
        
        // Add new report card to the grid (simulate)
        addNewReportCard(type, format);
        
    }, 2000 + Math.random() * 2000); // 2-4 seconds
}

function addNewReportCard(type, format) {
    const reportsGrid = document.querySelector('.reports-grid');
    if (!reportsGrid) return;
    
    const newCard = document.createElement('div');
    newCard.className = 'report-card';
    newCard.style.opacity = '0';
    newCard.style.transform = 'translateY(20px)';
    
    const currentDate = new Date().toISOString().split('T')[0];
    
    newCard.innerHTML = `
        <div class="report-header">
            <div>
                <div class="report-title">New ${type.replace('-', ' ')} Report</div>
                <div class="report-type">${type} Report</div>
            </div>
            <span class="status-badge status-ready">
                <i class="fas fa-check-circle"></i>
                Ready
            </span>
        </div>
        <div class="report-content">
            <div class="report-meta">
                <div class="meta-item">
                    <div class="meta-label">Generated</div>
                    <div class="meta-value">${currentDate}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Format</div>
                    <div class="meta-value">${format.toUpperCase()}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Size</div>
                    <div class="meta-value">${(Math.random() * 5 + 0.5).toFixed(1)} MB</div>
                </div>
            </div>
            <div class="report-actions">
                <button class="btn btn-primary btn-sm">
                    <i class="fas fa-download"></i> Download
                </button>
                <button class="btn btn-secondary btn-sm">
                    <i class="fas fa-share"></i> Share
                </button>
            </div>
        </div>
    `;
    
    reportsGrid.insertBefore(newCard, reportsGrid.firstChild);
    
    // Animate in
    setTimeout(() => {
        newCard.style.transition = 'all 0.3s ease';
        newCard.style.opacity = '1';
        newCard.style.transform = 'translateY(0)';
    }, 100);
    
    // Initialize actions for new card
    initReportCardActions(newCard);
}

function initReportActions() {
    document.querySelectorAll('.report-card').forEach(card => {
        initReportCardActions(card);
    });
}

function initReportCardActions(card) {
    // Download buttons
    const downloadBtn = card.querySelector('.btn-primary');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const reportTitle = card.querySelector('.report-title').textContent;
            showNotification(`Downloading ${reportTitle}...`, 'info');
            
            // Simulate download
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-download"></i> Download';
                showNotification('Download completed!', 'success');
            }, 1500);
        });
    }
    
    // Share buttons
    const shareBtn = card.querySelector('.btn-secondary');
    if (shareBtn && shareBtn.textContent.includes('Share')) {
        shareBtn.addEventListener('click', function() {
            const reportTitle = card.querySelector('.report-title').textContent;
            const recipients = prompt('Enter email addresses (comma-separated):');
            if (recipients) {
                showNotification(`${reportTitle} shared with ${recipients.split(',').length} recipients`, 'success');
            }
        });
    }
    
    // Preview buttons
    const previewBtn = card.querySelector('.btn-secondary[title*="Preview"], .btn-secondary:contains("Preview")');
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            const reportTitle = card.querySelector('.report-title').textContent;
            showNotification(`Opening preview for ${reportTitle}`, 'info');
        });
    }
}

function initAnalytics() {
    const analyticsCards = document.querySelectorAll('.analytics-card');
    
    analyticsCards.forEach(card => {
        card.addEventListener('click', function() {
            const chartTitle = this.querySelector('h4').textContent;
            showNotification(`Opening detailed view for ${chartTitle}`, 'info');
            
            // Add click animation
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
        
        // Hover effect for chart placeholders
        const chartPlaceholder = card.querySelector('.chart-placeholder');
        if (chartPlaceholder) {
            chartPlaceholder.addEventListener('mouseenter', function() {
                this.style.background = 'linear-gradient(135deg, var(--primary-color, #1a73e8) 0%, var(--primary-light, #e3f2fd) 100%)';
                this.style.color = 'white';
            });
            
            chartPlaceholder.addEventListener('mouseleave', function() {
                this.style.background = 'linear-gradient(135deg, var(--primary-light, #e3f2fd) 0%, var(--card-header-bg, #f8f9fa) 100%)';
                this.style.color = 'var(--text-secondary, #666)';
            });
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