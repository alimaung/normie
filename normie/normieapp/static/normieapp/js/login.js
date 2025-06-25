// Form switching functions
function showLogin() {
    hideAllForms();
    document.getElementById('login-form').classList.add('active');
    clearAllValidationErrors();
}

function showSignUp() {
    hideAllForms();
    document.getElementById('signup-form').classList.add('active');
    clearAllValidationErrors();
}

function showForgotPassword() {
    hideAllForms();
    document.getElementById('forgot-form').classList.add('active');
    clearAllValidationErrors();
}

function hideAllForms() {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
}

// Clear all validation errors
function clearAllValidationErrors() {
    // Clear error states
    document.querySelectorAll('.input-wrapper').forEach(wrapper => {
        wrapper.classList.remove('error', 'success');
    });
    
    // Hide error messages
    document.querySelectorAll('.field-error').forEach(error => {
        error.classList.add('hidden');
    });
    
    // Clear dynamic error messages
    const termsError = document.getElementById('terms_error');
    if (termsError) {
        termsError.remove();
    }
    
    // Clear success and validation error messages
    document.querySelectorAll('.signup-success-message, .signup-validation-error').forEach(msg => {
        msg.remove();
    });
    
    // Hide username availability indicator
    const usernameAvailability = document.getElementById('username-availability');
    if (usernameAvailability) {
        usernameAvailability.style.display = 'none';
    }
}

// Show field error
function showFieldError(fieldId, message) {
    const wrapper = document.getElementById(fieldId + '_wrapper');
    const errorElement = document.getElementById(fieldId + '_error');
    
    if (wrapper && errorElement) {
        wrapper.classList.add('error');
        wrapper.classList.remove('success');
        errorElement.classList.remove('hidden');
        errorElement.querySelector('span').textContent = message;
    }
}

// Hide field error
function hideFieldError(fieldId) {
    const wrapper = document.getElementById(fieldId + '_wrapper');
    const errorElement = document.getElementById(fieldId + '_error');
    
    if (wrapper && errorElement) {
        wrapper.classList.remove('error');
        errorElement.classList.add('hidden');
    }
}

// Show field success
function showFieldSuccess(fieldId) {
    const wrapper = document.getElementById(fieldId + '_wrapper');
    
    if (wrapper) {
        wrapper.classList.remove('error');
        wrapper.classList.add('success');
    }
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate individual fields
function validateField(fieldId, value, validationType = 'required', showErrors = true) {
    let isValid = true;
    let errorMessage = '';

    // Check if field is empty
    if (!value || value.trim() === '') {
        isValid = false;
        errorMessage = 'This field is required';
    } else {
        // Field-specific validation
        switch (validationType) {
            case 'email':
                if (!isValidEmail(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid email address';
                }
                break;
            case 'username':
                if (!validateUsername(value)) {
                    isValid = false;
                    errorMessage = 'Username must be at least 4 characters (letters, numbers, periods, underscores, hyphens)';
                }
                break;
            case 'name':
                if (value.trim().length < 2) {
                    isValid = false;
                    errorMessage = 'Must be at least 2 characters long';
                }
                break;
            case 'password':
                const passwordStrength = checkPasswordStrength(value);
                if (passwordStrength.score < 3) {
                    isValid = false;
                    errorMessage = 'Password is too weak';
                }
                break;
            case 'password_confirm':
                const originalPassword = document.getElementById('signup_password');
                if (originalPassword && value !== originalPassword.value) {
                    isValid = false;
                    errorMessage = 'Passwords do not match';
                }
                break;
        }
    }

    if (showErrors) {
        if (isValid) {
            hideFieldError(fieldId);
            showFieldSuccess(fieldId);
        } else {
            showFieldError(fieldId, errorMessage);
        }
    }

    return isValid;
}

// Setup login form interactions (no validation until submission)
function setupLoginValidation() {
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');

    if (usernameField) {
        usernameField.addEventListener('input', function() {
            // Clear errors as user types
            hideFieldError('username');
        });
    }

    if (passwordField) {
        passwordField.addEventListener('input', function() {
            // Clear errors as user types
            hideFieldError('password');
        });
    }
}

// Setup signup form interactions 
function setupSignupValidation() {
    const fields = [
        'first_name', 'last_name', 'signup_email', 'signup_username', 
        'signup_password', 'confirm_password', 'department', 'telephone'
    ];

    fields.forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            element.addEventListener('input', function() {
                // Clear errors as user types
                hideFieldError(fieldId);
                
                // Special handling for specific fields
                if (fieldId === 'signup_password') {
                    updatePasswordStrength();
                    checkPasswordMatch();
                } else if (fieldId === 'confirm_password') {
                    checkPasswordMatch();
                } else if (fieldId === 'signup_username') {
                    // Check username availability after a delay
                    clearTimeout(this.usernameTimeout);
                    this.usernameTimeout = setTimeout(() => {
                        if (this.value.trim().length >= 4) {
                            showUsernameAvailability(this.value.trim());
                        } else {
                            document.getElementById('username-availability').style.display = 'none';
                        }
                    }, 500);
                }
            });
        }
    });
}

// Validate entire login form
function validateLoginForm() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    let isValid = true;
    let firstInvalidField = null;
    
    if (!validateField('username', username, 'required')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('username');
    }
    
    if (!validateField('password', password, 'required')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('password');
    }
    
    // Scroll to first invalid field
    if (firstInvalidField) {
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidField.focus();
    }
    
    return isValid;
}

// Validate entire signup form
async function validateSignupForm() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('signup_email').value;
    const username = document.getElementById('signup_username').value;
    const password = document.getElementById('signup_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const termsAccepted = document.getElementById('terms_accepted').checked;
    
    let isValid = true;
    let firstInvalidField = null;
    
    // Required fields validation
    if (!validateField('first_name', firstName, 'name')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('first_name');
    }
    
    if (!validateField('last_name', lastName, 'name')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('last_name');
    }
    
    if (!validateField('signup_email', email, 'email')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('signup_email');
    }
    
    if (!validateField('signup_username', username, 'username')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('signup_username');
    }
    
    if (!validateField('signup_password', password, 'password')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('signup_password');
    }
    
    if (!validateField('confirm_password', confirmPassword, 'password_confirm')) {
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('confirm_password');
    }
    
    // Check username availability if format is valid
    if (username && validateUsername(username)) {
        const availabilityResult = await checkUsernameAvailability(username);
        if (!availabilityResult.available) {
            showFieldError('signup_username', availabilityResult.message);
            isValid = false;
            if (!firstInvalidField) firstInvalidField = document.getElementById('signup_username');
        }
    }
    
    // Handle terms acceptance with inline error instead of alert
    if (!termsAccepted) {
        // Create terms error if it doesn't exist
        let termsError = document.getElementById('terms_error');
        if (!termsError) {
            termsError = document.createElement('div');
            termsError.id = 'terms_error';
            termsError.className = 'field-error';
            termsError.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>You must accept the Terms of Service and Privacy Policy</span>';
            
            const termsGroup = document.querySelector('.terms-agreement').parentElement;
            termsGroup.appendChild(termsError);
        } else {
            termsError.classList.remove('hidden');
        }
        isValid = false;
        if (!firstInvalidField) firstInvalidField = document.getElementById('terms_accepted');
    } else {
        // Hide terms error if it exists
        const termsError = document.getElementById('terms_error');
        if (termsError) {
            termsError.classList.add('hidden');
        }
    }
    
    // Scroll to first invalid field
    if (firstInvalidField) {
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalidField.focus();
    }
    
    return isValid;
}

// Password toggle function
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.password-toggle i');
    
    if (input.type === 'password') {
        input.type = 'text';
        button.classList.remove('fa-eye');
        button.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        button.classList.remove('fa-eye-slash');
        button.classList.add('fa-eye');
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    let score = 0;
    let feedback = [];

    // Length check
    if (password.length >= 8) score += 1;
    else feedback.push('At least 8 characters');

    // Uppercase check
    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('One uppercase letter');

    // Lowercase check
    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('One lowercase letter');

    // Number check
    if (/\d/.test(password)) score += 1;
    else feedback.push('One number');

    // Special character check
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 1;
    else feedback.push('One special character');

    let strength = 'weak';
    let text = 'Weak password';

    if (score >= 2) {
        strength = 'fair';
        text = 'Fair password';
    }
    if (score >= 4) {
        strength = 'good';
        text = 'Good password';
    }
    if (score >= 5) {
        strength = 'strong';
        text = 'Strong password';
    }

    return { strength, text, feedback, score };
}

// Update password strength display
function updatePasswordStrength() {
    const passwordInput = document.getElementById('signup_password');
    const strengthIndicator = document.getElementById('password-strength');
    
    if (!passwordInput || !strengthIndicator) return;

    const password = passwordInput.value;
    const result = checkPasswordStrength(password);

    // Remove all strength classes
    strengthIndicator.className = 'password-strength';
    
    if (password.length > 0) {
        strengthIndicator.classList.add(`strength-${result.strength}`);
        strengthIndicator.querySelector('.strength-text').textContent = result.text;
    } else {
        strengthIndicator.querySelector('.strength-text').textContent = 'Enter password to see strength';
    }
}

// Check password match
function checkPasswordMatch() {
    const password = document.getElementById('signup_password');
    const confirmPassword = document.getElementById('confirm_password');
    const matchIndicator = document.getElementById('password-match');
    
    if (!password || !confirmPassword || !matchIndicator) return;

    if (confirmPassword.value.length > 0) {
        if (password.value === confirmPassword.value) {
            matchIndicator.style.display = 'flex';
            hideFieldError('confirm_password');
            showFieldSuccess('confirm_password');
        } else {
            matchIndicator.style.display = 'none';
            showFieldError('confirm_password', 'Passwords do not match');
        }
    } else {
        matchIndicator.style.display = 'none';
        hideFieldError('confirm_password');
    }
}

// Validate username
function validateUsername(username) {
    const usernameRegex = /^[a-zA-Z0-9._-]{4,30}$/;
    return usernameRegex.test(username);
}

// Check username availability via API
async function checkUsernameAvailability(username) {
    try {
        const response = await fetch(`/ajax/check-username/?username=${encodeURIComponent(username)}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error checking username availability:', error);
        return {
            available: false,
            message: 'Error checking username availability',
            type: 'error'
        };
    }
}

// Show username availability
async function showUsernameAvailability(username) {
    const availabilityElement = document.getElementById('username-availability');
    const wrapperElement = document.getElementById('signup_username_wrapper');
    
    if (!availabilityElement) return;
    
    // First check basic format validation
    if (!validateUsername(username)) {
        availabilityElement.style.display = 'none';
        return;
    }
    
    // Show loading state
    availabilityElement.style.display = 'flex';
    availabilityElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Checking availability...</span>';
    availabilityElement.style.color = '#6b7280';
    
    // Check availability via API
    const result = await checkUsernameAvailability(username);
    
    if (result.available) {
        // Username is available - show green checkmark
        availabilityElement.innerHTML = '<i class="fas fa-check"></i><span>Username is available</span>';
        availabilityElement.style.color = '#10b981';
        availabilityElement.style.display = 'flex';
        hideFieldError('signup_username');
        showFieldSuccess('signup_username');
    } else {
        // Username is taken - show error
        availabilityElement.style.display = 'none';
        showFieldError('signup_username', result.message);
    }
}

// Handle login form submission
function handleLogin(event) {
    event.preventDefault();
    
    if (!validateLoginForm()) {
        return;
    }
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
    submitButton.disabled = true;
    
    // Here you would normally submit the form to the backend
    // For now, we'll just reset the button after a short delay
    setTimeout(() => {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
        // The actual form submission should happen here
        // event.target.submit(); // Uncomment when ready to submit to backend
    }, 1000);
}

// Handle signup form submission
async function handleSignup(event) {
    event.preventDefault();
    
    // Show loading state immediately
    const submitButton = document.getElementById('signup-button');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validating...';
    submitButton.disabled = true;
    
    try {
        const isValid = await validateSignupForm();
        
        if (!isValid) {
            // Reset button if validation failed
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
            return;
        }
        
        // Update button text for form submission
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
        
        const form = event.target;
        const formData = new FormData(form);
        
        // Simulate API call (replace with actual backend call)
        setTimeout(() => {
            // Reset button
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
            
            // Show inline success message
            let successContainer = document.querySelector('.signup-success-message');
            if (!successContainer) {
                successContainer = document.createElement('div');
                successContainer.className = 'signup-success-message message message-success';
                successContainer.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <span>Account created successfully! Please check your email for verification.</span>
                `;
                const signupForm = document.getElementById('signup-form');
                signupForm.insertBefore(successContainer, signupForm.firstChild);
                
                // Auto-switch to login after showing success
                setTimeout(() => {
                    showLogin();
                }, 3000);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Error during signup validation:', error);
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
        
        // Show inline error message instead of alert
        let errorContainer = document.querySelector('.signup-validation-error');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.className = 'signup-validation-error message message-error';
            errorContainer.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>An error occurred during validation. Please try again.</span>
                <button class="message-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            const signupForm = document.getElementById('signup-form');
            signupForm.insertBefore(errorContainer, signupForm.firstChild);
        }
    }
}

// Show signup errors
function showSignupErrors(errors) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.signup-errors');
    existingErrors.forEach(error => error.remove());
    
    // Create error container
    const errorContainer = document.createElement('div');
    errorContainer.className = 'signup-errors message message-error';
    errorContainer.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <div>
            <strong>Please fix the following errors:</strong>
            <ul style="margin: 0.5rem 0 0 1rem; padding: 0;">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        </div>
        <button class="message-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Insert before the signup form
    const signupForm = document.getElementById('signup-form');
    signupForm.insertBefore(errorContainer, signupForm.firstChild);
    
    // Scroll to top of form
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Mock functions for terms and privacy
function showTerms() {
    alert('Terms of Service would be displayed in a modal or new page.');
}

function showPrivacy() {
    alert('Privacy Policy would be displayed in a modal or new page.');
}

// Mock Microsoft SSO
function mockMicrosoftSSO() {
    alert('Microsoft SSO integration would be implemented here. This is a demo.');
}

// Handle forgot password form submission
function handleForgotPassword(event) {
    event.preventDefault();
    const email = document.getElementById('forgot_email').value;
    alert('Password reset email would be sent to: ' + email);
    showLogin();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    showLogin(); // Show login form by default
    
    // Setup validation for both forms
    setupLoginValidation();
    setupSignupValidation();
    
    // Add form submit handlers
    const loginForm = document.querySelector('#login-form form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});