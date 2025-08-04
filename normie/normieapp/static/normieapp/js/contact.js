// Contact Form JavaScript
class ContactForm {
    constructor() {
        this.form = document.querySelector('form[method="post"]');
        this.submitButton = this.form?.querySelector('button[type="submit"]');
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        console.log('Initializing contact form');
        
        // Add form submission handler
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Add real-time validation
        this.addValidation();
        
        // Add character counter for message field
        this.addCharacterCounter();
        
        console.log('Contact form initialized successfully');
    }
    
    handleSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            return;
        }
        
        this.submitForm();
    }
    
    validateForm() {
        const requiredFields = ['name', 'email', 'subject', 'message'];
        let isValid = true;
        
        // Clear previous error states
        this.clearErrors();
        
        requiredFields.forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            const value = field.value.trim();
            
            if (!value) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Validate email format
        const emailField = this.form.querySelector('[name="email"]');
        if (emailField.value && !this.isValidEmail(emailField.value)) {
            this.showFieldError(emailField, 'Please enter a valid email address');
            isValid = false;
        }
        
        return isValid;
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    clearErrors() {
        // Remove error classes and messages
        this.form.querySelectorAll('.form-group').forEach(group => {
            group.classList.remove('has-error');
            const errorMsg = group.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        });
    }
    
    showFieldError(field, message) {
        const formGroup = field.closest('.form-group');
        formGroup.classList.add('has-error');
        
        // Add error message if not already present
        if (!formGroup.querySelector('.error-message')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-danger mt-1';
            errorDiv.textContent = message;
            formGroup.appendChild(errorDiv);
        }
    }
    
    submitForm() {
        const formData = new FormData(this.form);
        
        // Show loading state
        this.setLoadingState(true);
        
        fetch(this.form.action || window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showSuccess(data.message);
                this.resetForm();
            } else {
                this.showError(data.message || 'An error occurred while sending your message.');
            }
        })
        .catch(error => {
            console.error('Contact form submission error:', error);
            this.showError('An error occurred while sending your message. Please try again.');
        })
        .finally(() => {
            this.setLoadingState(false);
        });
    }
    
    setLoadingState(loading) {
        if (!this.submitButton) return;
        
        if (loading) {
            this.submitButton.disabled = true;
            this.submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        } else {
            this.submitButton.disabled = false;
            this.submitButton.innerHTML = 'Submit';
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.contact-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `contact-notification alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert notification at the top of the form container
        const formContainer = this.form.closest('.contact-form-container');
        if (formContainer) {
            formContainer.insertBefore(notification, formContainer.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Scroll to notification
        notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    resetForm() {
        this.form.reset();
        this.clearErrors();
        
        // Reset character counter
        const messageField = this.form.querySelector('[name="message"]');
        if (messageField) {
            this.updateCharacterCount(messageField);
        }
    }
    
    addValidation() {
        // Add real-time validation for email field
        const emailField = this.form.querySelector('[name="email"]');
        if (emailField) {
            emailField.addEventListener('blur', () => {
                if (emailField.value && !this.isValidEmail(emailField.value)) {
                    this.showFieldError(emailField, 'Please enter a valid email address');
                } else {
                    const formGroup = emailField.closest('.form-group');
                    formGroup.classList.remove('has-error');
                    const errorMsg = formGroup.querySelector('.error-message');
                    if (errorMsg) errorMsg.remove();
                }
            });
        }
        
        // Clear errors on input
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => {
                const formGroup = field.closest('.form-group');
                if (formGroup.classList.contains('has-error')) {
                    formGroup.classList.remove('has-error');
                    const errorMsg = formGroup.querySelector('.error-message');
                    if (errorMsg) errorMsg.remove();
                }
            });
        });
    }
    
    addCharacterCounter() {
        const messageField = this.form.querySelector('[name="message"]');
        if (!messageField) return;
        
        // Create character counter element
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted mt-1';
        counter.style.fontSize = '0.875rem';
        
        // Insert counter after the message field
        const formGroup = messageField.closest('.form-group');
        formGroup.appendChild(counter);
        
        // Update counter function
        const updateCounter = () => this.updateCharacterCount(messageField);
        
        // Add event listeners
        messageField.addEventListener('input', updateCounter);
        messageField.addEventListener('keyup', updateCounter);
        
        // Initial update
        updateCounter();
    }
    
    updateCharacterCount(messageField) {
        const counter = messageField.closest('.form-group').querySelector('.character-counter');
        if (!counter) return;
        
        const currentLength = messageField.value.length;
        const maxLength = messageField.getAttribute('maxlength') || 2000;
        
        counter.textContent = `${currentLength}/${maxLength} characters`;
        
        // Change color based on usage
        if (currentLength > maxLength * 0.9) {
            counter.className = 'character-counter text-warning mt-1';
        } else if (currentLength === parseInt(maxLength)) {
            counter.className = 'character-counter text-danger mt-1';
        } else {
            counter.className = 'character-counter text-muted mt-1';
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    new ContactForm();
});
