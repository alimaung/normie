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
    
    // Handle category assignment
    $('.category-item').on('click', function(e) {
        e.preventDefault();
        
        const selectedEmails = getSelectedEmailIds();
        
        if (selectedEmails.length === 0) {
            showNotification('Please select at least one email to categorize.', 'warning');
            return;
        }
        
        const category = $(this).data('category');
        const categoryName = category ? $(this).text().trim() : 'None';
        const account = $('#account-selector').val();
        
        // Show loading indicator
        $('.dropdown-toggle').html('<i class="fas fa-spinner fa-spin"></i> Categorizing...');
        $('.dropdown-toggle').prop('disabled', true);
        
        categorizeEmails(selectedEmails, category, account);
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
            $('.dropdown-toggle').prop('disabled', false);
        } else {
            $('#delete-btn').prop('disabled', true);
            $('.dropdown-toggle').prop('disabled', true);
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
    
    // Function to categorize emails
    function categorizeEmails(emailIds, category, account) {
        $.ajax({
            url: '/inbox/categorize/',
            type: 'POST',
            data: {
                'email_ids': emailIds,
                'category': category,
                'account': account,
                'csrfmiddlewaretoken': $('#csrf-form input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update UI to show the new category
                    const count = emailIds.length;
                    let message;
                    
                    if (category) {
                        message = count === 1 
                            ? `Email categorized as "${category}".` 
                            : `${count} emails categorized as "${category}".`;
                    } else {
                        message = count === 1 
                            ? 'Category removed from email.' 
                            : `Categories removed from ${count} emails.`;
                    }
                    
                    showNotification(message, 'success');
                    
                    // Reload to show updated categories
                    setTimeout(function() {
                        showLoadingOverlay();
                        location.reload();
                    }, 1000);
                } else {
                    showNotification('Error categorizing email(s): ' + response.error, 'danger');
                    
                    // Reset button
                    $('.dropdown-toggle').html('<i class="fas fa-tag"></i> Categorize');
                    updateToolbarState();
                }
            },
            error: function() {
                showNotification('An error occurred while categorizing the email(s).', 'danger');
                
                // Reset button
                $('.dropdown-toggle').html('<i class="fas fa-tag"></i> Categorize');
                updateToolbarState();
            }
        });
    }
    
    // Create context menu for right-click
    function createContextMenu() {
        // Create the context menu
        const contextMenu = $(`
            <div id="email-context-menu" class="dropdown-menu">
                <h6 class="dropdown-header">Categorize</h6>
                <div class="category-menu-items">
                    ${getCategoryMenuItems()}
                </div>
                <div class="dropdown-divider"></div>
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
                    min-width: 200px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    border: 1px solid #e5e5e5;
                    border-radius: 4px;
                    background-color: #fff;
                    padding: 8px 0;
                }
                #email-context-menu .dropdown-header {
                    font-weight: 600;
                    color: #333;
                    padding: 8px 16px;
                }
                #email-context-menu .dropdown-item {
                    padding: 8px 16px;
                    cursor: pointer;
                }
                #email-context-menu .dropdown-item:hover {
                    background-color: #f0f7ff;
                }
                #email-context-menu .category-color {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 3px;
                    margin-right: 10px;
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
        
        // Handle click on category items in context menu
        $('#email-context-menu').on('click', '.context-category-item', function(e) {
            e.preventDefault();
            
            // Get the email ID and category
            const emailId = $('#email-context-menu').data('email-id');
            const category = $(this).data('category');
            const account = $('#account-selector').val();
            
            // Hide the context menu
            $('#email-context-menu').hide();
            
            // Categorize the email
            categorizeEmails([emailId], category, account);
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
    
    // Helper function to get category menu items HTML
    function getCategoryMenuItems() {
        let html = '';
        
        // Get available categories
        if ($('.category-item').length > 0) {
            $('.category-item').each(function() {
                const category = $(this).data('category');
                if (category) {  // Skip the "Clear Category" item
                    const color = $(this).find('.category-color').css('background-color');
                    html += `
                        <a class="dropdown-item context-category-item" href="#" data-category="${category}">
                            <span class="category-color" style="background-color: ${color || $(this).find('.category-color').attr('style').split('background-color: ')[1].split(';')[0]};"></span>
                            ${$(this).text().trim()}
                        </a>
                    `;
                }
            });
            
            // Add "Clear Category" item
            html += `
                <div class="dropdown-divider"></div>
                <a class="dropdown-item context-category-item" href="#" data-category="">
                    <i class="fas fa-times"></i> Clear Category
                </a>
            `;
        } else {
            // Default categories if none are available
            html += `
                <a class="dropdown-item context-category-item" href="#" data-category="Important">
                    <span class="category-color" style="background-color: #FF0000;"></span> Important
                </a>
                <a class="dropdown-item context-category-item" href="#" data-category="Work">
                    <span class="category-color" style="background-color: #FFA500;"></span> Work
                </a>
                <a class="dropdown-item context-category-item" href="#" data-category="Personal">
                    <span class="category-color" style="background-color: #0000FF;"></span> Personal
                </a>
                <a class="dropdown-item context-category-item" href="#" data-category="Follow-up">
                    <span class="category-color" style="background-color: #008000;"></span> Follow-up
                </a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item context-category-item" href="#" data-category="">
                    <i class="fas fa-times"></i> Clear Category
                </a>
            `;
        }
        
        return html;
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