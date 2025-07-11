// Gmail-style Inbox JavaScript
class InboxManager {
    constructor() {
        this.currentFilters = {
            search: '',
            unread: false,
            important: false,
            attachments: false,
            sort_by: 'received_time',
            sort_order: 'desc'
        };
        this.currentPage = 1;
        this.selectedEmails = new Set();
        this.refreshInterval = null;
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Gmail-style inbox system');
        
        // Initialize from window data if available
        if (window.inboxData) {
            this.currentFilters = { ...this.currentFilters, ...window.inboxData.currentFilters };
            this.currentPage = window.inboxData.pagination?.current_page || 1;
        }
        
        this.bindEvents();
        this.initializeTooltips();
        this.startAutoRefresh();
        
        console.log('Inbox system initialized successfully');
    }
    
    bindEvents() {
        // Search functionality
        $('#search-input').on('input', (e) => this.handleSearchInput(e));
        $('#search-btn').on('click', () => this.performSearch());
        $('#clear-search').on('click', () => this.clearSearch());
        
        // Enter key for search
        $('#search-input').on('keypress', (e) => {
            if (e.which === 13) {
                this.performSearch();
            }
        });
        
        // Filter checkboxes
        $('#filter-unread').on('change', (e) => this.handleFilterChange('unread', e.target.checked));
        $('#filter-important').on('change', (e) => this.handleFilterChange('important', e.target.checked));
        $('#filter-attachments').on('change', (e) => this.handleFilterChange('attachments', e.target.checked));
        
        // Clear filters
        $('#clear-filters, #clear-all-filters').on('click', () => this.clearAllFilters());
        
        // Quick filter links
        $('.filter-item a[data-filter]').on('click', (e) => {
            e.preventDefault();
            const filter = $(e.currentTarget).data('filter');
            this.toggleQuickFilter(filter);
        });
        
        // Sort links
        $('.sort-link').on('click', (e) => {
            e.preventDefault();
            const sortBy = $(e.currentTarget).data('sort');
            this.handleSort(sortBy);
        });
        
        // Pagination
        $(document).on('click', '.page-link', (e) => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            if (page) {
                this.loadPage(page);
            }
        });
        
        // Select all checkbox
        $('#select-all').on('change', (e) => this.handleSelectAll(e.target.checked));
        
        // Individual email checkboxes
        $(document).on('change', '.email-checkbox', (e) => this.handleEmailSelect(e));
        
        // Toolbar actions
        $('#refresh-btn').on('click', () => this.refreshInbox());
        $('#delete-selected').on('click', () => this.deleteSelected());
        $('#mark-read').on('click', () => this.markSelectedAsRead());
        $('#retry-connection').on('click', () => this.retryConnection());
        
        // Email row clicks (for selection)
        $(document).on('click', '.email-item', (e) => {
            if (!$(e.target).is('input, a, button')) {
                const checkbox = $(e.currentTarget).find('.email-checkbox');
                checkbox.prop('checked', !checkbox.prop('checked')).trigger('change');
            }
        });
        
        // Prevent link clicks from selecting row
        $(document).on('click', '.email-item a', (e) => {
            e.stopPropagation();
        });
    }
    
    initializeTooltips() {
        if (typeof $().tooltip === 'function') {
            $('[title]').tooltip();
        }
    }
    
    handleSearchInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Show/hide clear button
        if (query) {
            $('#clear-search').show();
        } else {
            $('#clear-search').hide();
        }
        
        // Debounce search
        this.searchTimeout = setTimeout(() => {
            if (query !== this.currentFilters.search) {
                this.currentFilters.search = query;
                this.currentPage = 1;
                this.loadEmails();
            }
        }, 500);
    }
    
    performSearch() {
        const query = $('#search-input').val().trim();
        this.currentFilters.search = query;
        this.currentPage = 1;
        this.loadEmails();
    }
    
    clearSearch() {
        $('#search-input').val('');
        $('#clear-search').hide();
        this.currentFilters.search = '';
        this.currentPage = 1;
        this.loadEmails();
    }
    
    handleFilterChange(filterType, checked) {
        this.currentFilters[filterType] = checked;
        this.currentPage = 1;
        this.loadEmails();
    }
    
    toggleQuickFilter(filterType) {
        const isActive = this.currentFilters[filterType];
        this.currentFilters[filterType] = !isActive;
        
        // Update UI
        $(`#filter-${filterType}`).prop('checked', this.currentFilters[filterType]);
        
        this.currentPage = 1;
        this.loadEmails();
    }
    
    clearAllFilters() {
        this.currentFilters = {
            search: '',
            unread: false,
            important: false,
            attachments: false,
            sort_by: 'received_time',
            sort_order: 'desc'
        };
        this.currentPage = 1;
        
        // Update UI
        $('#search-input').val('');
        $('#clear-search').hide();
        $('#filter-unread, #filter-important, #filter-attachments').prop('checked', false);
        
        this.loadEmails();
    }
    
    handleSort(sortBy) {
        if (this.currentFilters.sort_by === sortBy) {
            // Toggle sort order
            this.currentFilters.sort_order = this.currentFilters.sort_order === 'asc' ? 'desc' : 'asc';
        } else {
            // New sort column
            this.currentFilters.sort_by = sortBy;
            this.currentFilters.sort_order = 'desc';
        }
        
        this.currentPage = 1;
        this.loadEmails();
    }
    
    loadPage(page) {
        this.currentPage = page;
        this.loadEmails();
    }
    
    handleSelectAll(checked) {
        $('.email-checkbox').prop('checked', checked);
        
        if (checked) {
            $('.email-checkbox').each((i, checkbox) => {
                this.selectedEmails.add($(checkbox).val());
            });
        } else {
            this.selectedEmails.clear();
        }
        
        this.updateToolbarState();
    }
    
    handleEmailSelect(e) {
        const emailId = $(e.target).val();
        const checked = $(e.target).prop('checked');
        
        if (checked) {
            this.selectedEmails.add(emailId);
        } else {
            this.selectedEmails.delete(emailId);
        }
        
        // Update select all checkbox
        const totalCheckboxes = $('.email-checkbox').length;
        const checkedCheckboxes = $('.email-checkbox:checked').length;
        
        $('#select-all').prop('indeterminate', checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes);
        $('#select-all').prop('checked', checkedCheckboxes === totalCheckboxes);
        
        this.updateToolbarState();
    }
    
    updateToolbarState() {
        const hasSelection = this.selectedEmails.size > 0;
        $('#delete-selected, #mark-read').prop('disabled', !hasSelection);
    }
    
    loadEmails() {
        this.showLoading();
        
        const params = new URLSearchParams({
            page: this.currentPage,
            per_page: 25,
            sort_by: this.currentFilters.sort_by,
            sort_order: this.currentFilters.sort_order
        });
        
        // Add filters
        if (this.currentFilters.search) {
            params.append('search', this.currentFilters.search);
        }
        if (this.currentFilters.unread) {
            params.append('unread', '1');
        }
        if (this.currentFilters.important) {
            params.append('important', '1');
        }
        if (this.currentFilters.attachments) {
            params.append('attachments', '1');
        }
        
        // Use AJAX for smooth loading
        $.ajax({
            url: window.inboxData?.urls?.inbox || '/inbox/',
            method: 'GET',
            data: params.toString(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: (response) => {
                if (response.success) {
                    this.updateEmailList(response.emails);
                    this.updatePagination(response.pagination);
                    this.updateFolderStats(response.folder_stats);
                } else {
                    this.showError('Failed to load emails');
                }
            },
            error: () => {
                this.showError('Failed to load emails');
            },
            complete: () => {
                this.hideLoading();
            }
        });
    }
    
    refreshInbox() {
        const $refreshBtn = $('#refresh-btn');
        const $icon = $refreshBtn.find('i');
        
        $icon.addClass('fa-spin');
        
        $.ajax({
            url: window.inboxData?.urls?.refresh || '/inbox/refresh/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                page: this.currentPage,
                search: this.currentFilters.search || null,
                unread: this.currentFilters.unread || null,
                important: this.currentFilters.important || null,
                attachments: this.currentFilters.attachments || null
            }),
            success: (response) => {
                if (response.success) {
                    this.updateEmailList(response.emails);
                    this.updatePagination(response.pagination);
                    this.updateFolderStats(response.folder_stats);
                    this.updateDataStatus(response.data_status);
                    this.showSuccess('Inbox refreshed successfully');
                } else {
                    this.showError('Failed to refresh inbox');
                }
            },
            error: () => {
                this.showError('Failed to refresh inbox');
            },
            complete: () => {
                $icon.removeClass('fa-spin');
            }
        });
    }
    
    deleteSelected() {
        if (this.selectedEmails.size === 0) return;
        
        if (!confirm(`Delete ${this.selectedEmails.size} selected email(s)?`)) {
            return;
        }
        
        const emailIds = Array.from(this.selectedEmails);
        
        $.ajax({
            url: window.inboxData?.urls?.delete || '/inbox/delete/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                email_ids: emailIds
            }),
            success: (response) => {
                if (response.success) {
                    this.showSuccess('Emails deleted successfully');
                    this.selectedEmails.clear();
                    this.loadEmails();
                } else {
                    this.showError(response.error || 'Failed to delete emails');
                }
            },
            error: () => {
                this.showError('Failed to delete emails');
            }
        });
    }
    
    markSelectedAsRead() {
        if (this.selectedEmails.size === 0) return;
        
        const emailIds = Array.from(this.selectedEmails);
        
        $.ajax({
            url: window.inboxData?.urls?.markRead || '/inbox/mark-read/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                email_ids: emailIds,
                read: true
            }),
            success: (response) => {
                if (response.success) {
                    this.showSuccess('Emails marked as read');
                    this.selectedEmails.clear();
                    this.loadEmails();
                } else {
                    this.showError(response.error || 'Failed to mark emails as read');
                }
            },
            error: () => {
                this.showError('Failed to mark emails as read');
            }
        });
    }
    
    retryConnection() {
        location.reload();
    }
    
    updateEmailList(emails) {
        const $emailItems = $('#email-items');
        $emailItems.empty();
        
        if (emails.length === 0) {
            $emailItems.html(`
                <div class="no-emails-message">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h4>No emails found</h4>
                    <p>Try adjusting your search or filters.</p>
                </div>
            `);
            return;
        }
        
        emails.forEach(email => {
            const emailHtml = this.renderEmailItem(email);
            $emailItems.append(emailHtml);
        });
        
        // Clear selections
        this.selectedEmails.clear();
        $('#select-all').prop('checked', false).prop('indeterminate', false);
        this.updateToolbarState();
    }
    
    renderEmailItem(email) {
        const unreadClass = email.unread ? 'unread' : '';
        const importantIcon = email.importance > 1 ? '<i class="fas fa-star text-warning" title="Important"></i>' : '';
        const attachmentIcon = email.attachments && email.attachments.length > 0 ? '<i class="fas fa-paperclip text-muted" title="Has attachments"></i>' : '';
        const unreadIndicator = email.unread ? '<i class="fas fa-circle text-primary unread-indicator" title="Unread"></i>' : '';
        
        const senderName = email.sender_name || email.sender_email;
        const subject = email.subject || '(No subject)';
        const preview = email.body ? email.body.substring(0, 100) : '';
        const receivedTime = new Date(email.received_time).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div class="email-item ${unreadClass}" data-email-id="${email.id}">
                <div class="email-item-checkbox">
                    <input type="checkbox" class="email-checkbox" value="${email.id}">
                </div>
                <div class="email-item-flags">
                    ${importantIcon}
                    ${attachmentIcon}
                    ${unreadIndicator}
                </div>
                <div class="email-item-sender">
                    <span class="sender-name" title="${email.sender_email}">${senderName}</span>
                </div>
                <div class="email-item-subject">
                    <a href="/inbox/view/${email.id}/" class="email-link">
                        <span class="subject">${subject}</span>
                        <span class="email-preview">${preview}</span>
                    </a>
                </div>
                <div class="email-item-date">
                    <span class="date-time" title="${email.received_time}">${receivedTime}</span>
                </div>
            </div>
        `;
    }
    
    updatePagination(pagination) {
        // Update pagination info and controls
        // This would be implemented based on the pagination structure
        console.log('Pagination updated:', pagination);
    }
    
    updateFolderStats(stats) {
        $('#unread-count').text(stats.unread_emails > 0 ? stats.unread_emails : '');
        $('.filter-count').each((i, el) => {
            const $el = $(el);
            const filterType = $el.closest('a').data('filter');
            if (filterType === 'unread') {
                $el.text(stats.unread_emails || '');
            } else if (filterType === 'important') {
                $el.text(stats.important_emails || '');
            } else if (filterType === 'attachments') {
                $el.text(stats.emails_with_attachments || '');
            }
        });
    }
    
    updateDataStatus(status) {
        const $indicator = $('.status-indicator');
        const $lastUpdate = $('.last-update');
        
        if (status.available) {
            $indicator.removeClass('status-offline').addClass('status-online');
            $indicator.find('span').text('VBA Online');
            if (status.last_modified) {
                $lastUpdate.find('small').text(`Updated: ${status.last_modified}`);
            }
        } else {
            $indicator.removeClass('status-online').addClass('status-offline');
            $indicator.find('span').text('VBA Offline');
        }
    }
    
    startAutoRefresh() {
        // Auto-refresh every 2 minutes
        this.refreshInterval = setInterval(() => {
            this.refreshInbox();
        }, 120000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    showLoading() {
        $('#loading-overlay').show();
    }
    
    hideLoading() {
        $('#loading-overlay').hide();
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas fa-${icon}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        // Add to messages container or create one
        let $messages = $('.messages');
        if ($messages.length === 0) {
            $messages = $('<div class="messages"></div>');
            $('.content').prepend($messages);
        }
        
        $messages.append(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.fadeOut(() => notification.remove());
        }, 5000);
    }
}

// Initialize when document is ready
$(document).ready(function() {
    window.inboxManager = new InboxManager();
}); 