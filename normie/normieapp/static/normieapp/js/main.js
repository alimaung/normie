// Main JavaScript functionality for Microfilm Processing System

// DOM ready function
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle functionality
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const logo = document.getElementById('logo');
    const darkModeIcon = document.getElementById('dark-mode-icon');
    const restartServerButton = document.getElementById('restart-server');
    
    // Handle prefers-color-scheme media query
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Get the base static URL for the logo images (only if logo exists)
    const logoLightPath = logo ? logo.getAttribute('src') : null;
    const logoDarkPath = logoLightPath ? logoLightPath.replace('logo-light.png', 'logo-dark.png') : null;

    // Function to set dark mode state
    function setDarkMode(isDark) {
        // Apply or remove dark mode class
        body.classList.toggle('dark-mode', isDark);
        
        // Update logo source (only if logo exists)
        if (logo && logoLightPath && logoDarkPath) {
            logo.src = isDark ? logoDarkPath : logoLightPath;
        }
        
        // Update icon class with transition (only if icon exists)
        if (darkModeIcon) {
            if (isDark) {
                darkModeIcon.classList.add('fa-sun');
                darkModeIcon.classList.remove('fa-moon');
            } else {
                darkModeIcon.classList.add('fa-moon');
                darkModeIcon.classList.remove('fa-sun');
            }
        }
        
        // Store preference
        localStorage.setItem('dark-mode', isDark ? 'enabled' : 'disabled');
    }
    
    // Initialize dark mode based on user preference or system preference
    function initializeTheme() {
        const savedTheme = localStorage.getItem('dark-mode');
        
        if (savedTheme === 'enabled') {
            setDarkMode(true);
        } else if (savedTheme === 'disabled') {
            setDarkMode(false);
        } else if (prefersDarkMode.matches) {
            // If no saved preference, respect system preference
            setDarkMode(true);
        }
    }

    // Initialize theme on load
    initializeTheme();

    // Add click event for dark mode toggle with animation (only if toggle button exists)
    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            const isDarkMode = body.classList.contains('dark-mode');
            
            // First animate the icon (only if it exists)
            if (darkModeIcon) {
                darkModeIcon.style.transform = 'rotate(360deg)';
            }
            
            // After a small delay, toggle the theme
            setTimeout(() => {
                setDarkMode(!isDarkMode);
                if (darkModeIcon) {
                    darkModeIcon.style.transform = '';
                }
            }, 200);
        });
    }
    
    // Listen for changes in system color scheme preference
    prefersDarkMode.addEventListener('change', (event) => {
        // Only apply if the user hasn't set a preference
        if (!localStorage.getItem('dark-mode')) {
            setDarkMode(event.matches);
        }
    });
    
    // Enhanced Message System
    function initializeMessages() {
        const messages = document.querySelectorAll('.message');
        
        messages.forEach((message, index) => {
            // Add staggered animation delay
            message.style.animationDelay = `${index * 0.1}s`;
            
            // Add auto-dismiss for non-error messages
            if (!message.classList.contains('message-error')) {
                message.classList.add('auto-dismiss');
                
                // Auto-dismiss after 15 seconds
                setTimeout(() => {
                    dismissMessage(message);
                }, 15000);
            }
            
            // Handle close button clicks
            const closeButton = message.querySelector('.message-close');
            if (closeButton) {
                closeButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    dismissMessage(message);
                });
            }
            
            // Add click to dismiss (except for close button)
            message.addEventListener('click', (e) => {
                if (!e.target.closest('.message-close')) {
                    dismissMessage(message);
                }
            });
            
            // No special styling needed - all messages are uniform
        });
    }
    
    function dismissMessage(message) {
        message.classList.add('dismissing');
        
        setTimeout(() => {
            if (message.parentElement) {
                message.remove();
                
                // If no more messages, remove the container
                const messagesContainer = document.querySelector('.messages');
                if (messagesContainer && messagesContainer.children.length === 0) {
                    messagesContainer.remove();
                }
            }
        }, 300);
    }
    
    // Function to create and show a new message
    function showMessage(text, type = 'info', autoDismiss = true) {
        let messagesContainer = document.querySelector('.messages');
        
        // Create messages container if it doesn't exist
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages';
            document.body.appendChild(messagesContainer);
        }
        
        // Create message element
        const message = document.createElement('div');
        message.className = `message message-${type}`;
        
        // Determine icon based on type
        let iconClass = 'fa-info-circle';
        if (type === 'error') iconClass = 'fa-exclamation-triangle';
        else if (type === 'warning') iconClass = 'fa-exclamation-circle';
        else if (type === 'success') iconClass = 'fa-check-circle';
        
        message.innerHTML = `
            <i class="fas ${iconClass}"></i>
            ${text}
            <button class="message-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to container
        messagesContainer.appendChild(message);
        
        // Handle close button
        const closeButton = message.querySelector('.message-close');
        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            dismissMessage(message);
        });
        
        // Auto-dismiss if enabled
        if (autoDismiss && type !== 'error') {
            message.classList.add('auto-dismiss');
            setTimeout(() => {
                dismissMessage(message);
            }, 15000);
        }
        
        return message;
    }
    
    // Initialize messages on page load
    initializeMessages();
    
    // Make showMessage globally available
    window.showMessage = showMessage;
    
    // Function to show notification
    function showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.classList.add('notification');
            document.body.appendChild(notification);
        }
        
        // Set background color based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#4caf50';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#f44336';
        } else if (type === 'warning') {
            notification.style.backgroundColor = '#ff9800';
        } else {
            notification.style.backgroundColor = '#2196f3';
        }
        
        // Set message
        notification.textContent = message;
        
        // Show notification
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        
        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }
    
    // Add restart server button functionality
    if (restartServerButton) {
        restartServerButton.addEventListener('click', () => {
            // Animate the icon
            const restartIcon = restartServerButton.querySelector('i');
            restartIcon.style.transform = 'rotate(360deg)';
            
            // Confirm before restarting
            if (confirm('Are you sure you want to restart the server? This may cause temporary service disruption.')) {
                // Show loading state
                restartIcon.classList.add('loading-state');
                
                // Send request to restart server
                fetch('/api/restart-server/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading state
                    restartIcon.classList.remove('loading-state');
                    
                    // Reset icon animation
                    setTimeout(() => {
                        restartIcon.style.transform = '';
                    }, 200);
                    
                    // Show notification based on result
                    if (data.success) {
                        showNotification('Server restarting...', 'success');
                        // Optional: redirect to a maintenance page or home after a delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 5000);
                    } else {
                        showNotification('Failed to restart server: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    // Remove loading state
                    restartIcon.classList.remove('loading-state');
                    
                    // Reset icon animation
                    setTimeout(() => {
                        restartIcon.style.transform = '';
                    }, 200);
                    
                    // Show error notification
                    showNotification('Error: ' + error.message, 'error');
                });
            } else {
                // Reset icon animation if cancelled
                setTimeout(() => {
                    restartIcon.style.transform = '';
                }, 200);
            }
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    // Handle dropdown menu functionality
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (dropdownToggle && dropdownMenu) {
        // Prevent dropdown toggle from navigating
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
        });
        
        // Handle dropdown menu item clicks
        dropdownMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function(e) {
                // Don't interfere with ctrl/cmd clicks or right clicks
                if (e.ctrlKey || e.metaKey || e.button !== 0) return;
                
                const href = this.getAttribute('href');
                if (href && href !== '#' && !href.startsWith('javascript:')) {
                    e.preventDefault();
                    
                    // Fade out current content
                    document.querySelector('.content').style.opacity = '0';
                    
                    // Navigate after fade animation
                    setTimeout(() => {
                        window.location.href = href;
                    }, 300);
                }
            });
        });
    }

    // Add smooth page transitions for regular navbar links
    document.querySelectorAll('.navbar-links > a').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't interfere with ctrl/cmd clicks or right clicks
            if (e.ctrlKey || e.metaKey || e.button !== 0) return;
            
            const href = this.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript:')) {
                e.preventDefault();
                
                // Fade out current content
                document.querySelector('.content').style.opacity = '0';
                
                // Navigate after fade animation
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            }
        });
    });
}); 