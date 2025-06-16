document.addEventListener('DOMContentLoaded', function() {
    // Initialize approval actions
    initApprovalActions();
    
    // Initialize filters
    initFilters();
    
    // Initialize workflow interactions
    initWorkflowSteps();
});

function initApprovalActions() {
    // Approve buttons
    document.querySelectorAll('.btn-approve').forEach(btn => {
        btn.addEventListener('click', function() {
            const approvalItem = this.closest('.approval-item');
            const title = approvalItem.querySelector('.approval-title').textContent;
            
            if (confirm(`Are you sure you want to approve "${title}"?`)) {
                // Add approval animation
                approvalItem.style.background = '#e8f5e8';
                approvalItem.style.border = '2px solid #4caf50';
                
                // Update actions
                this.innerHTML = '<i class="fas fa-check"></i> Approved';
                this.style.background = '#4caf50';
                this.disabled = true;
                
                // Hide reject button
                const rejectBtn = approvalItem.querySelector('.btn-reject');
                if (rejectBtn) rejectBtn.style.display = 'none';
                
                showNotification(`${title} approved successfully`, 'success');
                
                // Reset styling after animation
                setTimeout(() => {
                    approvalItem.style.background = '';
                    approvalItem.style.border = '';
                }, 2000);
            }
        });
    });
    
    // Reject buttons
    document.querySelectorAll('.btn-reject').forEach(btn => {
        btn.addEventListener('click', function() {
            const approvalItem = this.closest('.approval-item');
            const title = approvalItem.querySelector('.approval-title').textContent;
            
            const reason = prompt(`Please provide a reason for rejecting "${title}":`);
            if (reason) {
                // Add rejection animation
                approvalItem.style.background = '#ffebee';
                approvalItem.style.border = '2px solid #f44336';
                
                // Update actions
                this.innerHTML = '<i class="fas fa-times"></i> Rejected';
                this.style.background = '#f44336';
                this.disabled = true;
                
                // Hide approve button
                const approveBtn = approvalItem.querySelector('.btn-approve');
                if (approveBtn) approveBtn.style.display = 'none';
                
                showNotification(`${title} rejected: ${reason}`, 'warning');
                
                // Reset styling after animation
                setTimeout(() => {
                    approvalItem.style.background = '';
                    approvalItem.style.border = '';
                }, 2000);
            }
        });
    });
    
    // Review buttons
    document.querySelectorAll('.btn-review').forEach(btn => {
        btn.addEventListener('click', function() {
            const approvalItem = this.closest('.approval-item');
            const title = approvalItem.querySelector('.approval-title').textContent;
            showNotification(`Opening review for ${title}`, 'info');
        });
    });
}

function initFilters() {
    const typeFilter = document.querySelector('.queue-filters select:nth-child(1)');
    const priorityFilter = document.querySelector('.queue-filters select:nth-child(2)');
    const assigneeFilter = document.querySelector('.queue-filters select:nth-child(3)');
    
    [typeFilter, priorityFilter, assigneeFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', function() {
                filterApprovals();
            });
        }
    });
}

function filterApprovals() {
    const typeFilter = document.querySelector('.queue-filters select:nth-child(1)')?.value || '';
    const priorityFilter = document.querySelector('.queue-filters select:nth-child(2)')?.value || '';
    const assigneeFilter = document.querySelector('.queue-filters select:nth-child(3)')?.value || '';
    
    const approvalItems = document.querySelectorAll('.approval-item');
    
    approvalItems.forEach(item => {
        const icon = item.querySelector('.approval-icon');
        const priority = item.querySelector('.priority-badge')?.textContent.toLowerCase() || '';
        
        let itemType = '';
        if (icon.classList.contains('request')) itemType = 'request';
        else if (icon.classList.contains('standard')) itemType = 'standard';
        else if (icon.classList.contains('release')) itemType = 'release';
        
        const matchesType = !typeFilter || itemType === typeFilter;
        const matchesPriority = !priorityFilter || priority.includes(priorityFilter.toLowerCase());
        const matchesAssignee = !assigneeFilter; // Simplified for demo
        
        if (matchesType && matchesPriority && matchesAssignee) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function initWorkflowSteps() {
    const workflowSteps = document.querySelectorAll('.workflow-step');
    
    workflowSteps.forEach((step, index) => {
        step.addEventListener('click', function() {
            // Remove active class from all steps
            workflowSteps.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked step and all previous steps
            for (let i = 0; i <= index; i++) {
                workflowSteps[i].classList.add('completed');
            }
            
            // Set current step as active
            this.classList.add('active');
            this.classList.remove('completed');
            
            const stepName = this.querySelector('strong').textContent;
            showNotification(`Workflow step: ${stepName}`, 'info');
        });
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
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
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