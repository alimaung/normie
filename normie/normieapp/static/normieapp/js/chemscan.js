// ChemScan Analysis JavaScript

class ChemScanManager {
    constructor() {
        this.currentView = 'table';
        this.searchQuery = '';
        this.statusFilter = '';
        this.riskFilter = '';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeAnimations();
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('chemscan-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.filterTable();
            });
        }
        
        // Filter dropdowns
        const filterSelects = document.querySelectorAll('.filter-select');
        filterSelects.forEach((select, index) => {
            select.addEventListener('change', (e) => {
                if (index === 0) {
                    this.statusFilter = e.target.value;
                } else if (index === 1) {
                    this.riskFilter = e.target.value;
                }
                this.filterTable();
            });
        });
        
        // View toggle buttons
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.getAttribute('data-view');
                this.switchView(view);
            });
        });
        
        // Action buttons
        const actionBtns = document.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleAction(btn);
            });
        });
        
        // Quick action cards
        const actionCards = document.querySelectorAll('.action-card');
        actionCards.forEach(card => {
            card.addEventListener('click', () => {
                this.handleQuickAction(card);
            });
        });
        
        // Header action buttons
        const headerBtns = document.querySelectorAll('.header-actions .btn');
        headerBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleHeaderAction(btn);
            });
        });
    }
    
    initializeAnimations() {
        // Animate stat cards on load
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100);
            }, index * 100);
        });
        
        // Animate table rows
        const tableRows = document.querySelectorAll('.scan-row');
        tableRows.forEach((row, index) => {
            setTimeout(() => {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                row.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, 50);
            }, index * 50);
        });
    }
    
    filterTable() {
        const rows = document.querySelectorAll('.scan-row');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const substanceName = row.querySelector('.substance-name .name').textContent.toLowerCase();
            const analysisId = row.querySelector('.analysis-id').textContent.toLowerCase();
            const status = row.querySelector('.status-badge').textContent.toLowerCase().trim();
            const riskLevel = row.querySelector('.risk-badge').textContent.toLowerCase().trim();
            
            let showRow = true;
            
            // Search filter
            if (this.searchQuery) {
                showRow = substanceName.includes(this.searchQuery) || 
                         analysisId.includes(this.searchQuery);
            }
            
            // Status filter
            if (this.statusFilter && showRow) {
                showRow = status.includes(this.statusFilter);
            }
            
            // Risk filter
            if (this.riskFilter && showRow) {
                showRow = riskLevel.includes(this.riskFilter);
            }
            
            if (showRow) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update results count (if you want to add this feature)
        this.updateResultsCount(visibleCount);
    }
    
    updateResultsCount(count) {
        // You can add a results counter element if needed
        console.log(`Showing ${count} results`);
    }
    
    switchView(view) {
        this.currentView = view;
        
        // Update button states
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-view') === view) {
                btn.classList.add('active');
            }
        });
        
        // Switch view (for now just log, you can implement grid view later)
        if (view === 'grid') {
            this.showNotification('Grid view coming soon!', 'info');
        }
    }
    
    handleAction(btn) {
        const title = btn.getAttribute('title');
        const row = btn.closest('.scan-row');
        const analysisId = row.querySelector('.analysis-id').textContent;
        
        switch (title) {
            case 'View Details':
                this.viewDetails(analysisId);
                break;
            case 'Download Report':
                this.downloadReport(analysisId);
                break;
            case 'Edit Analysis':
                this.editAnalysis(analysisId);
                break;
        }
    }
    
    handleQuickAction(card) {
        const title = card.querySelector('h4').textContent;
        
        switch (title) {
            case 'Start New Analysis':
                this.startNewAnalysis();
                break;
            case 'Export Reports':
                this.exportReports();
                break;
            case 'Substance Database':
                this.openDatabase();
                break;
            case 'Analytics Dashboard':
                this.openDashboard();
                break;
        }
    }
    
    handleHeaderAction(btn) {
        const text = btn.textContent.trim();
        
        if (text.includes('New Analysis')) {
            this.startNewAnalysis();
        } else if (text.includes('Import Data')) {
            this.importData();
        }
    }
    
    viewDetails(analysisId) {
        this.showNotification(`Opening details for ${analysisId}`, 'info');
        // Implement navigation to details page
    }
    
    downloadReport(analysisId) {
        this.showNotification(`Downloading report for ${analysisId}`, 'success');
        // Implement report download
    }
    
    editAnalysis(analysisId) {
        this.showNotification(`Opening editor for ${analysisId}`, 'info');
        // Implement navigation to edit page
    }
    
    startNewAnalysis() {
        this.showNotification('Starting new chemical analysis...', 'info');
        // Implement new analysis workflow
    }
    
    exportReports() {
        this.showNotification('Preparing reports for export...', 'info');
        // Implement bulk export functionality
    }
    
    openDatabase() {
        this.showNotification('Opening substance database...', 'info');
        // Implement database navigation
    }
    
    openDashboard() {
        this.showNotification('Opening analytics dashboard...', 'info');
        // Implement dashboard navigation
    }
    
    importData() {
        this.showNotification('Opening data import wizard...', 'info');
        // Implement data import functionality
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;
        
        notification.querySelector('.notification-content').style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-triangle';
            case 'warning': return 'exclamation-circle';
            default: return 'info-circle';
        }
    }
    
    getNotificationColor(type) {
        switch (type) {
            case 'success': return '#4caf50';
            case 'error': return '#f44336';
            case 'warning': return '#ff9800';
            default: return '#2196f3';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ChemScanManager();
});

// Add some utility functions for enhanced UX
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn, .action-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Add keyboard navigation for table
    document.addEventListener('keydown', function(e) {
        if (e.key === '/') {
            e.preventDefault();
            const searchInput = document.getElementById('chemscan-search');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}); 