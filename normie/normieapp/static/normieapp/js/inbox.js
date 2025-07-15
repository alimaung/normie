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
        this.sidebarPinned = false;
        this.sidebarHoverTimeout = null;
        
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
        this.initializeSidebar();
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
        
        // Read/Unread toggle buttons
        $(document).on('click', '.read-unread-btn', (e) => this.handleReadUnreadToggle(e));
        
        // Sidebar controls
        $('#sidebar-toggle').on('click', () => this.toggleSidebar());
        $('#sidebar-pin').on('click', () => this.toggleSidebarPin());
        
        // Toolbar actions
        $('#refresh-btn, #refresh-action').on('click', () => this.refreshInbox());
        $('#select-all-action').on('click', () => this.selectAllEmails());
        
        // Selection actions
        $('#delete-selected').on('click', () => this.deleteSelected());
        $('#mark-read-selected').on('click', () => this.markSelectedAsRead());
        $('#mark-unread-selected').on('click', () => this.markSelectedAsUnread());
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
    
    initializeSidebar() {
        const $sidebar = $('#inbox-sidebar');
        
        // Handle hover behavior when not pinned
        $sidebar.on('mouseenter', () => {
            if (!this.sidebarPinned && $sidebar.hasClass('collapsed')) {
                clearTimeout(this.sidebarHoverTimeout);
                this.expandSidebar();
            }
        });
        
        $sidebar.on('mouseleave', () => {
            if (!this.sidebarPinned && !$sidebar.hasClass('collapsed')) {
                this.sidebarHoverTimeout = setTimeout(() => {
                    this.collapseSidebar();
                }, 300); // Delay before collapsing
            }
        });
    }
    
    toggleSidebar() {
        const $sidebar = $('#inbox-sidebar');
        if ($sidebar.hasClass('collapsed')) {
            this.expandSidebar();
        } else {
            this.collapseSidebar();
        }
    }
    
    expandSidebar() {
        const $sidebar = $('#inbox-sidebar');
        const $toggle = $('#sidebar-toggle');
        const $pin = $('#sidebar-pin');
        
        $sidebar.removeClass('collapsed');
        $toggle.find('i').removeClass('fa-chevron-right').addClass('fa-chevron-left');
        $toggle.attr('title', 'Collapse sidebar');
        
        if (!this.sidebarPinned) {
            $pin.show();
        }
    }
    
    collapseSidebar() {
        const $sidebar = $('#inbox-sidebar');
        const $toggle = $('#sidebar-toggle');
        const $pin = $('#sidebar-pin');
        
        $sidebar.addClass('collapsed');
        $toggle.find('i').removeClass('fa-chevron-left').addClass('fa-chevron-right');
        $toggle.attr('title', 'Expand sidebar');
        $pin.hide();
    }
    
    toggleSidebarPin() {
        const $pin = $('#sidebar-pin');
        
        this.sidebarPinned = !this.sidebarPinned;
        
        if (this.sidebarPinned) {
            $pin.addClass('pinned');
            $pin.attr('title', 'Unpin sidebar');
        } else {
            $pin.removeClass('pinned');
            $pin.attr('title', 'Pin sidebar open');
        }
    }
    
    selectAllEmails() {
        $('#select-all').prop('checked', true).trigger('change');
    }
    
    updateSelectionState(checkedCount) {
        const $selectedCount = $('#selected-count');
        const $defaultActions = $('#default-actions');
        const $selectionActions = $('#selection-actions');
        
        if (checkedCount > 0) {
            $selectedCount.text(`${checkedCount} selected`);
            $defaultActions.hide();
            $selectionActions.show();
        } else {
            $selectedCount.text('0 selected');
            $defaultActions.show();
            $selectionActions.hide();
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
        
        // Update selection counter and toolbar state
        this.updateSelectionState(checkedCheckboxes);
    }
    
    handleReadUnreadToggle(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = $(e.currentTarget);
        const emailId = button.data('email-id');
        const isCurrentlyRead = button.data('read') === 'true';
        
        // Toggle read status
        this.toggleEmailReadStatus(emailId, !isCurrentlyRead, button);
    }
    
    updateToolbarState() {
        const hasSelection = this.selectedEmails.size > 0;
        this.updateSelectionState(this.selectedEmails.size);
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
        if (this.currentFilters.folder) {
            params.append('folder', this.currentFilters.folder);
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
                attachments: this.currentFilters.attachments || null,
                folder: this.currentFilters.folder || null  // ✅ Add missing folder filter
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
        
        const count = this.selectedEmails.size;
        const confirmation = count === 1 ? 
            'Are you sure you want to delete this email?' : 
            `Are you sure you want to delete ${count} selected emails?`;
            
        if (!confirm(confirmation)) {
            return;
        }
        
        const emailIds = Array.from(this.selectedEmails);
        const $deleteBtn = $('#delete-selected');
        const originalText = $deleteBtn.text();
        
        // Show loading state
        $deleteBtn.prop('disabled', true).text('Deleting...');
        
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
                    const message = response.message || 'Emails deleted successfully';
                    this.showSuccess(message);
                    this.selectedEmails.clear();
                    this.loadEmails();
                } else {
                    this.showError(response.error || 'Failed to delete emails');
                }
            },
            error: (xhr) => {
                let errorMessage = 'Failed to delete emails';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.error || response.message || errorMessage;
                } catch (e) {
                    // Use default error message
                }
                this.showError(errorMessage);
            },
            complete: () => {
                // Restore button state
                $deleteBtn.prop('disabled', false).text(originalText);
            }
        });
    }
    
    markSelectedAsRead() {
        this.markSelectedAs(true, 'read');
    }
    
    markSelectedAsUnread() {
        this.markSelectedAs(false, 'unread');
    }
    
    markSelectedAs(readStatus, statusText) {
        if (this.selectedEmails.size === 0) return;
        
        const emailIds = Array.from(this.selectedEmails);
        
        $.ajax({
            url: window.inboxData?.urls?.markReadUnread || '/inbox/mark-read-unread/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                email_ids: emailIds,
                read: readStatus
            }),
            success: (response) => {
                if (response.success) {
                    const message = response.message || `Emails marked as ${statusText}`;
                    this.showSuccess(message);
                    this.selectedEmails.clear();
                    this.loadEmails();
                } else {
                    this.showError(response.error || `Failed to mark emails as ${statusText}`);
                }
            },
            error: () => {
                this.showError(`Failed to mark emails as ${statusText}`);
            }
        });
    }
    
    toggleEmailReadStatus(emailId, markAsRead, button) {
        console.log(`Toggling email ${emailId} to ${markAsRead ? 'read' : 'unread'}`);
        
        const data = {
            read: markAsRead
        };
        
        // Show loading state
        const originalHtml = button.html();
        button.html('<i class="fas fa-spinner fa-spin"></i>');
        
        $.ajax({
            url: `/inbox/mark-read-unread/${emailId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || ''
            },
            success: (response) => {
                if (response.success) {
                    // Debug logging
                    console.log('Read/unread response:', response);
                    console.log('Original button state:', button.data('read'));
                    
                    // Update button appearance
                    const newReadState = response.read;
                    const newUnreadState = response.unread;
                    
                    // Update button data attribute
                    button.data('read', newReadState ? 'true' : 'false');
                    
                    console.log('New button state:', button.data('read'));
                    
                    if (newReadState) {
                        button.html('<i class="far fa-envelope text-muted" title="Read"></i>');
                        button.attr('title', 'Mark as unread');
                    } else {
                        button.html('<i class="fas fa-envelope text-primary" title="Unread"></i>');
                        button.attr('title', 'Mark as read');
                    }
                    
                    // Update email row appearance
                    const emailRow = button.closest('.email-item');
                    if (newReadState) {
                        emailRow.removeClass('unread');
                    } else {
                        emailRow.addClass('unread');
                    }
                    
                    this.showSuccess(`Email marked as ${newReadState ? 'read' : 'unread'}`);
                } else {
                    button.html(originalHtml);
                    this.showError(response.error || 'Failed to update read status');
                }
            },
            error: () => {
                button.html(originalHtml);
                this.showError('Failed to update read status');
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
        this.updateSelectionState(0);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    renderEmailItem(email) {
        const unreadClass = email.unread ? 'unread' : '';
        
        // Read/unread button
        const readUnreadButton = email.unread 
            ? `<button class="btn btn-sm btn-link read-unread-btn" data-email-id="${email.id}" data-read="false" title="Mark as read">
                 <i class="fas fa-envelope text-primary" title="Unread"></i>
               </button>`
            : `<button class="btn btn-sm btn-link read-unread-btn" data-email-id="${email.id}" data-read="true" title="Mark as unread">
                 <i class="far fa-envelope text-muted" title="Read"></i>
               </button>`;
        
        // Attachment icon - check for both array and boolean formats
        const hasAttachments = (Array.isArray(email.attachments) && email.attachments.length > 0) || 
                              (email.attachments === true) ||
                              (typeof email.attachments === 'string' && email.attachments.length > 0);
        const attachmentIcon = hasAttachments ? '<i class="fas fa-paperclip text-muted" title="Has attachments"></i>' : '';
        
        // Importance icon
        const importanceIcon = email.importance > 1 
            ? '<i class="fas fa-star text-warning" title="Important"></i>'
            : '<i class="far fa-star text-muted opacity-25" title="Normal Priority"></i>';
        
        // Categories - safely handle and escape
        const categoriesHtml = email.categories && email.categories.trim()
            ? `<span class="categories-text" title="${this.escapeHtml(email.categories)}">${this.escapeHtml(email.categories.length > 15 ? email.categories.substring(0, 12) + '...' : email.categories)}</span>`
            : '<span class="text-muted">-</span>';
        
        const senderName = this.escapeHtml(email.sender_name || email.sender_email || '');
        const subject = this.escapeHtml(email.subject || '(No subject)');
        
        // Clean and truncate email preview - mimic Django's truncatechars filter
        let preview = '';
        if (email.body) {
            // First escape HTML entities like Django does
            let cleanText = this.escapeHtml(email.body);
            // Then remove remaining HTML tags and normalize text
            cleanText = cleanText
                .replace(/<[^>]*>/g, '') // Remove HTML tags
                .replace(/&\w+;/g, ' ')  // Remove HTML entities that might remain
                .replace(/\s+/g, ' ')    // Normalize whitespace  
                .trim();                 // Remove leading/trailing spaces
            
            // Truncate like Django's truncatechars (97 chars + "...")
            if (cleanText.length > 97) {
                preview = cleanText.substring(0, 97) + '...';
            } else {
                preview = cleanText;
            }
        }
        
        // Format date to match Django template
        let formattedDate = '<span class="text-muted">No date</span>';
        if (email.received_time) {
            try {
                const date = new Date(email.received_time);
                if (isNaN(date.getTime())) {
                    formattedDate = '<span class="text-muted">Invalid date</span>';
                } else {
                    formattedDate = date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    });
                }
            } catch (e) {
                formattedDate = '<span class="text-muted">Invalid date</span>';
            }
        }
        
        return `
            <div class="email-item ${unreadClass}" data-email-id="${email.id}">
                <div class="email-item-checkbox">
                    <input type="checkbox" class="email-checkbox" value="${email.id}">
                </div>
                <div class="email-item-flags">
                    ${readUnreadButton}
                    ${attachmentIcon}
                </div>
                <div class="email-item-importance">
                    ${importanceIcon}
                </div>
                <div class="email-item-categories">
                    ${categoriesHtml}
                </div>
                <div class="email-item-sender">
                    <span class="sender-name" title="${this.escapeHtml(email.sender_email || '')}">${senderName}</span>
                </div>
                <div class="email-item-subject">
                    <a href="/inbox/view/${this.escapeHtml(email.id)}/" class="email-link">
                        <span class="subject">${subject}</span>
                        <span class="email-preview">${preview}</span>
                    </a>
                </div>
                <div class="email-item-date">
                    <span class="date-time" title="${email.received_time || ''}">${formattedDate}</span>
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
        // Update folder counts
        $('#inbox-count').text(stats.folder_counts?.Inbox || '');
        $('#sent-count').text(stats.folder_counts?.['Sent Items'] || stats.folder_counts?.['Sent Mail'] || '');
        $('#drafts-count').text(stats.folder_counts?.Drafts || '');
        $('#deleted-count').text(stats.folder_counts?.['Deleted Items'] || stats.folder_counts?.Trash || '');
        $('#outbox-count').text(stats.folder_counts?.Outbox || '');
        
        // Update filter counts
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
        
        // Hide empty counts
        $('.folder-count, .filter-count').each((i, el) => {
            const $el = $(el);
            if (!$el.text() || $el.text() === '0') {
                $el.hide();
            } else {
                $el.show();
            }
        });
    }
    
    updateDataStatus(status, comStatus = null) {
        const $indicator = $('.status-indicator');
        const $lastUpdate = $('.last-update');
        const $comIndicator = $('.com-status-indicator');
        
        // Update VBA status
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
        
        // Update COM status if provided
        if (comStatus && $comIndicator.length) {
            if (comStatus.available && comStatus.initialized) {
                $comIndicator.removeClass('status-offline').addClass('status-online');
                $comIndicator.find('span').text('COM Ready');
                $comIndicator.attr('title', comStatus.message);
            } else {
                $comIndicator.removeClass('status-online').addClass('status-offline');
                $comIndicator.find('span').text('COM Offline');
                $comIndicator.attr('title', comStatus.message || 'COM interface not available');
            }
        }
    }
    
    startAutoRefresh() {
        // Auto-refresh every 20 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshInbox();
        }, 20000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    cleanup() {
        this.stopAutoRefresh();
        if (this.sidebarHoverTimeout) {
            clearTimeout(this.sidebarHoverTimeout);
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