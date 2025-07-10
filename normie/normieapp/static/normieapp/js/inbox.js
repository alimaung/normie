// Inbox JavaScript functionality

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Create context menu for right-click
    createContextMenu();
    
    // Handle account selector change
    $('#account-selector').on('change', function() {
        const account = $(this).val();
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('account', account);
        
        // Show loading indicator
        showLoadingOverlay();
        
        window.location.href = currentUrl.toString();
    });
    
    // Handle email selection
    $('.email-item').on('click', function(e) {
        if (!$(e.target).is('input[type="checkbox"]') && !$(e.target).is('a')) {
            const id = $(this).data('id');
            const account = $('#account-selector').val();
            
            // Show loading indicator
            showLoadingOverlay();
            
            window.location.href = `/inbox/view/${id}/?account=${account}`;
        }
    });
    
    // Handle checkbox selection without navigating
    $('.email-checkbox').on('click', function(e) {
        e.stopPropagation();
        const checked = $(this).prop('checked');
        const emailItem = $(this).closest('.email-item');
        
        if (checked) {
            emailItem.addClass('selected');
        } else {
            emailItem.removeClass('selected');
        }
        
        updateToolbarState();
    });
    
    // Select all emails
    $('#select-all').on('click', function() {
        const checked = $(this).prop('checked');
        $('.email-checkbox').prop('checked', checked);
        
        if (checked) {
            $('.email-item').addClass('selected');
        } else {
            $('.email-item').removeClass('selected');
        }
        
        updateToolbarState();
    });
    
    // Handle refresh button
    $('#refresh-btn').on('click', function() {
        // Show loading indicator
        showLoadingOverlay();
        
        location.reload();
    });
    
    // Handle delete button
    $('#delete-btn').on('click', function() {
        const selectedEmails = getSelectedEmailIds();
        
        if (selectedEmails.length === 0) {
            showNotification('Please select at least one email to delete.', 'warning');
            return;
        }
        
        // Use Bootstrap modal for confirmation
        if (confirm('Are you sure you want to delete the selected email(s)?')) {
            const account = $('#account-selector').val();
            
            // Show loading indicator
            $('#delete-btn').html('<i class="fas fa-spinner fa-spin"></i> Deleting...');
            $('#delete-btn').prop('disabled', true);
            
            $.ajax({
                url: '/inbox/delete/',
                type: 'POST',
                data: {
                    'email_ids': selectedEmails,
                    'account': account,
                    'csrfmiddlewaretoken': $('#csrf-form input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    if (response.success) {
                        // Remove deleted emails from the UI with animation
                        selectedEmails.forEach(function(id) {
                            $(`.email-item[data-id="${id}"]`).fadeOut(300, function() {
                                $(this).remove();
                                
                                // Check if there are no more emails
                                if ($('.email-item').length === 0) {
                                    $('.email-list').html(`
                                        <div class="no-emails-message">
                                            <i class="fas fa-envelope-open"></i>
                                            <h3>No emails found</h3>
                                            <p>There are no emails in this folder or matching your search criteria.</p>
                                        </div>
                                    `);
                                }
                            });
                        });
                        
                        // Show success message
                        const count = selectedEmails.length;
                        const message = count === 1 ? 'Email deleted successfully.' : `${count} emails deleted successfully.`;
                        showNotification(message, 'success');
                        
                        // Reset toolbar state
                        updateToolbarState();
                    } else {
                        showNotification('Error deleting email(s): ' + response.error, 'danger');
                        
                        // Reset button
                        $('#delete-btn').html('<i class="fas fa-trash-alt"></i> Delete');
                        updateToolbarState();
                    }
                },
                error: function() {
                    showNotification('An error occurred while deleting the email(s).', 'danger');
                    
                    // Reset button
                    $('#delete-btn').html('<i class="fas fa-trash-alt"></i> Delete');
                    updateToolbarState();
                }
            });
        }
    });
    
    // Clear search
    $('#clear-search').on('click', function() {
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.delete('search');
        
        // Show loading indicator
        showLoadingOverlay();
        
        window.location.href = currentUrl.toString();
    });
    
    // Helper function to get selected email IDs
    function getSelectedEmailIds() {
        const ids = [];
        $('.email-checkbox:checked').each(function() {
            ids.push($(this).data('id'));
        });
        return ids;
    }
    
    // Helper function to update toolbar state based on selection
    function updateToolbarState() {
        const selectedCount = $('.email-checkbox:checked').length;
        
        if (selectedCount > 0) {
            $('#delete-btn').prop('disabled', false);
        } else {
            $('#delete-btn').prop('disabled', true);
        }
        
        // Update button text to show count
        if (selectedCount > 0) {
            $('#delete-btn').html(`<i class="fas fa-trash-alt"></i> Delete (${selectedCount})`);
        } else {
            $('#delete-btn').html(`<i class="fas fa-trash-alt"></i> Delete`);
        }
        
        // Update select all checkbox state
        if ($('.email-checkbox').length > 0) {
            $('#select-all').prop('checked', selectedCount === $('.email-checkbox').length);
        }
    }
    
    // Create context menu for right-click
    function createContextMenu() {
        // Create the context menu
        const contextMenu = $(`
            <div id="email-context-menu" class="dropdown-menu">
                <a class="dropdown-item" href="#" id="context-delete">
                    <i class="fas fa-trash-alt text-danger"></i> Delete
                </a>
            </div>
        `);
        
        // Add the context menu to the body
        $('body').append(contextMenu);
        
        // Add CSS for the context menu
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                #email-context-menu {
                    position: absolute;
                    z-index: 1000;
                    display: none;
                    min-width: 120px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    border: 1px solid #e5e5e5;
                    border-radius: 4px;
                    background-color: #fff;
                    padding: 8px 0;
                }
                #email-context-menu .dropdown-item {
                    padding: 8px 16px;
                    cursor: pointer;
                }
                #email-context-menu .dropdown-item:hover {
                    background-color: #f0f7ff;
                }
            `)
            .appendTo('head');
        
        // Handle right-click on email items
        $('.email-item').on('contextmenu', function(e) {
            e.preventDefault();
            
            // Get the email ID
            const emailId = $(this).data('id');
            
            // Set the email ID as data attribute on the context menu
            $('#email-context-menu').data('email-id', emailId);
            
            // Select the email
            const checkbox = $(this).find('.email-checkbox');
            checkbox.prop('checked', true);
            $(this).addClass('selected');
            updateToolbarState();
            
            // Position the context menu
            $('#email-context-menu').css({
                top: e.pageY + 'px',
                left: e.pageX + 'px'
            }).show();
        });
        
        // Handle click on delete item in context menu
        $('#context-delete').on('click', function(e) {
            e.preventDefault();
            
            // Get the email ID
            const emailId = $('#email-context-menu').data('email-id');
            const account = $('#account-selector').val();
            
            // Hide the context menu
            $('#email-context-menu').hide();
            
            // Confirm deletion
            if (confirm('Are you sure you want to delete this email?')) {
                // Delete the email
                $.ajax({
                    url: '/inbox/delete/',
                    type: 'POST',
                    data: {
                        'email_ids': [emailId],
                        'account': account,
                        'csrfmiddlewaretoken': $('#csrf-form input[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            // Remove the email from the UI
                            $(`.email-item[data-id="${emailId}"]`).fadeOut(300, function() {
                                $(this).remove();
                                
                                // Check if there are no more emails
                                if ($('.email-item').length === 0) {
                                    $('.email-list').html(`
                                        <div class="no-emails-message">
                                            <i class="fas fa-envelope-open"></i>
                                            <h3>No emails found</h3>
                                            <p>There are no emails in this folder or matching your search criteria.</p>
                                        </div>
                                    `);
                                }
                                
                                // Show success message
                                showNotification('Email deleted successfully.', 'success');
                                
                                // Reset toolbar state
                                updateToolbarState();
                            });
                        } else {
                            showNotification('Error deleting email: ' + response.error, 'danger');
                        }
                    },
                    error: function() {
                        showNotification('An error occurred while deleting the email.', 'danger');
                    }
                });
            }
        });
        
        // Hide context menu on click outside
        $(document).on('click', function() {
            $('#email-context-menu').hide();
        });
    }
    

    
    // Show notification
    function showNotification(message, type) {
        // Check if notification container exists
        let notificationContainer = $('.notification-container');
        
        if (notificationContainer.length === 0) {
            // Create notification container if it doesn't exist
            notificationContainer = $('<div class="notification-container"></div>');
            $('.inbox-main').prepend(notificationContainer);
        }
        
        // Create notification
        const notification = $(`
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        
        // Add notification to container
        notificationContainer.append(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            notification.alert('close');
        }, 5000);
    }
    
    // Show loading overlay
    function showLoadingOverlay() {
        // Check if loading overlay exists
        if ($('#loading-overlay').length === 0) {
            // Create loading overlay
            const loadingOverlay = $(`
                <div id="loading-overlay">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `);
            
            // Add loading overlay to body
            $('body').append(loadingOverlay);
            
            // Add CSS for loading overlay
            $('<style>')
                .prop('type', 'text/css')
                .html(`
                    #loading-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(255, 255, 255, 0.7);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 9999;
                    }
                `)
                .appendTo('head');
        } else {
            // Show existing loading overlay
            $('#loading-overlay').show();
        }
    }
    
    // Initialize toolbar state
    updateToolbarState();
    
    // Add CSRF token to all AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}); 