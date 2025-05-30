document.addEventListener('DOMContentLoaded', function() {
    // Animate stats numbers on page load
    animateStats();
    
    // Add hover effects to feature cards
    initFeatureCards();
    
    // Add click handlers for CTA buttons
    initCTAButtons();
});

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        let currentValue = 0;
        const increment = finalValue / 50; // Animate over 50 steps
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                stat.textContent = finalValue;
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(currentValue);
            }
        }, 30);
    });
}

function initFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('fa-clipboard-list')) {
                window.location.href = '/standards/';
            } else if (icon.classList.contains('fa-paper-plane')) {
                window.location.href = '/requests/';
            } else if (icon.classList.contains('fa-boxes')) {
                window.location.href = '/materials/';
            } else if (icon.classList.contains('fa-rocket')) {
                window.location.href = '/releases/';
            } else if (icon.classList.contains('fa-check-circle')) {
                window.location.href = '/approvals/';
            } else if (icon.classList.contains('fa-warehouse')) {
                window.location.href = '/inventory/';
            } else if (icon.classList.contains('fa-chart-bar')) {
                window.location.href = '/reports/';
            } else if (icon.classList.contains('fa-shield-alt')) {
                window.location.href = '/audit/';
            }
        });
    });
}

function initCTAButtons() {
    const createRequestBtn = document.querySelector('.btn-primary');
    const viewDashboardBtn = document.querySelector('.btn-secondary');
    
    if (createRequestBtn) {
        createRequestBtn.addEventListener('click', function() {
            window.location.href = '/requests/';
        });
    }
    
    if (viewDashboardBtn) {
        viewDashboardBtn.addEventListener('click', function() {
            window.location.href = '/inventory/';
        });
    }
} 