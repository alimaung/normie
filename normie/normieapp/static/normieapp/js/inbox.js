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
        this.sidebarPinned = true; // Default to pinned
        this.sidebarHoverTimeout = null;
        this.sidebarCollapseTimeout = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Gmail-style inbox system');
        
        // Clean up malformed URLs if they exist
        this.cleanupURL();
        
        // Initialize from window data if available
        if (window.inboxData) {
            this.currentFilters = { ...this.currentFilters, ...window.inboxData.currentFilters };
            this.currentPage = window.inboxData.pagination?.current_page || 1;
        }
        
        // Set initial folder state from URL
        this.setInitialFolderState();
        
        this.bindEvents();
        this.initializeTooltips();
        this.initializeSidebar();
        this.startAutoRefresh();
        
        console.log('Inbox system initialized successfully');
    }
    
    cleanupURL() {
        const currentPath = window.location.pathname;
        
        // Check for malformed URLs with multiple folder segments
        if (currentPath.match(/\/(sent|deleted|drafts|outbox)\/.*\/(sent|deleted|drafts|outbox|inbox)\//)) {
            console.log('Detected malformed URL, cleaning up:', currentPath);
            
            // Extract the last valid folder segment
            let cleanFolder = 'Inbox';
            if (currentPath.includes('/sent/')) {
                cleanFolder = 'Sent Items';
            } else if (currentPath.includes('/deleted/')) {
                cleanFolder = 'Deleted Items';
            } else if (currentPath.includes('/drafts/')) {
                cleanFolder = 'Drafts';
            } else if (currentPath.includes('/outbox/')) {
                cleanFolder = 'Outbox';
            }
            
            // Redirect to clean URL
            const cleanUrl = this.getFolderUrl(cleanFolder);
            console.log('Redirecting to clean URL:', cleanUrl);
            window.history.replaceState({ folder: cleanFolder }, `${cleanFolder} - Email Inbox`, cleanUrl);
        }
    }
    
    setInitialFolderState() {
        const currentPath = window.location.pathname;
        let currentFolder = 'Inbox'; // default
        
        if (currentPath.includes('/inbox/sent/')) {
            currentFolder = 'Sent Items';
        } else if (currentPath.includes('/inbox/deleted/')) {
            currentFolder = 'Deleted Items';
        } else if (currentPath.includes('/inbox/drafts/')) {
            currentFolder = 'Drafts';
        } else if (currentPath.includes('/inbox/outbox/')) {
            currentFolder = 'Outbox';
        } else if (currentPath.includes('/inbox/')) {
            currentFolder = 'Inbox';
        }
        
        console.log(`Initial folder detected: ${currentFolder} from path: ${currentPath}`);
        
        this.currentFilters.folder = currentFolder;
        
        // Set active state in sidebar - fix the selector
        this.updateActiveFolderInSidebar(currentFolder);
    }
    
    updateActiveFolderInSidebar(folder) {
        // Remove active class from all folder items
        $('.folder-item').removeClass('active');
        
        // Add active class to the current folder
        let selector = '';
        switch(folder) {
            case 'Inbox':
                selector = '.folder-item a[href*="/inbox/"]:not([href*="/sent/"]):not([href*="/deleted/"]):not([href*="/drafts/"]):not([href*="/outbox/"])';
                break;
            case 'Sent Items':
            case 'Sent Mail':
                selector = '.folder-item a[href*="/sent/"]';
                break;
            case 'Deleted Items':
            case 'Trash':
                selector = '.folder-item a[href*="/deleted/"]';
                break;
            case 'Drafts':
                selector = '.folder-item a[href*="/drafts/"]';
                break;
            case 'Outbox':
                selector = '.folder-item a[href*="/outbox/"]';
                break;
        }
        
        if (selector) {
            $(selector).closest('.folder-item').addClass('active');
        }
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
        
        // Quick action buttons
        $(document).on('click', '.delete-btn', (e) => this.handleQuickDelete(e));
        $(document).on('click', '.importance-btn', (e) => this.handleImportanceToggle(e));
        
        // Sidebar controls
        $('#sidebar-toggle').on('click', () => this.expandSidebar());
        $('#sidebar-pin').on('click', () => this.toggleSidebarPin());
        
        // Toolbar actions
        $('#refresh-btn').on('click', () => this.refreshInbox());
        $('#select-all-action').on('click', () => this.selectAllEmails());
        
        // Selection actions
        $('#delete-selected').on('click', () => this.deleteSelected());
        $('#mark-read-unread-toggle').on('click', () => this.toggleSelectedReadUnread());
        $('#retry-connection').on('click', () => this.retryConnection());
        
        // SPA Navigation - Folder links
        $('.folder-item a').on('click', (e) => {
            e.preventDefault();
            const url = $(e.currentTarget).attr('href');
            this.navigateToFolder(url);
        });
        
        // SPA Navigation - Email view links
        $(document).on('click', '.email-link', (e) => {
            e.preventDefault();
            const url = $(e.currentTarget).attr('href');
            this.navigateToEmailView(url);
        });
        
        // Handle back navigation from email view
        $(document).on('click', '.back-arrow-btn', (e) => {
            e.preventDefault();
            this.navigateBackToInbox();
        });
        
        // Compose email actions
        $(document).on('click', '#compose-btn', (e) => {
            e.preventDefault();
            this.navigateToCompose('new');
        });
        
        $(document).on('click', '.reply-btn', (e) => {
            e.preventDefault();
            const emailId = $(e.currentTarget).data('email-id');
            this.navigateToCompose('reply', emailId);
        });
        
        $(document).on('click', '.forward-btn', (e) => {
            e.preventDefault();
            const emailId = $(e.currentTarget).data('email-id');
            this.navigateToCompose('forward', emailId);
        });
        
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
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', (e) => {
            if (e.state) {
                if (e.state.view === 'email' && e.state.emailId) {
                    // Navigate to email view
                    this.loadEmailById(e.state.emailId);
                } else if (e.state.folder) {
                    // Navigate to folder view - hide email view if open
                    this.hideEmailView();
                    // Don't reload folder content if it's already the current folder
                    if (this.currentFilters.folder !== e.state.folder) {
                        this.loadFolderContent(e.state.folder, false); // false = don't push to history
                    }
                }
            } else {
                // No state, go to default inbox
                this.hideEmailView();
                if (this.currentFilters.folder !== 'Inbox') {
                    this.loadFolderContent('Inbox', false);
                }
            }
        });
    }
    
    initializeTooltips() {
        if (typeof $().tooltip === 'function') {
            $('[title]').tooltip({
                placement: 'bottom',
                trigger: 'hover',
                delay: { show: 500, hide: 100 }
            });
        }
    }
    
    initializeSidebar() {
        const $sidebar = $('#inbox-sidebar');
        
        // Handle hover behavior for collapsed sidebar
        $sidebar.on('mouseenter', () => {
            if (!this.sidebarPinned && $sidebar.hasClass('collapsed')) {
                // Clear any existing timeouts
                clearTimeout(this.sidebarHoverTimeout);
                clearTimeout(this.sidebarCollapseTimeout);
                
                // Add hover expand after 1 second delay
                this.sidebarHoverTimeout = setTimeout(() => {
                    $sidebar.addClass('hover-expand');
                    // Reset icon styles when hovering
                    $('.folder-icon').each(function() {
                        $(this).css({
                            'font-weight': '',
                            'font-size': ''
                        });
                    });
                }, 500);
            }
        });
        
        $sidebar.on('mouseleave', () => {
            if (!this.sidebarPinned && $sidebar.hasClass('collapsed')) {
                // Clear hover expand immediately when mouse leaves
                clearTimeout(this.sidebarHoverTimeout);
                $sidebar.removeClass('hover-expand');
                
                // Reapply collapsed icon styles
                this.hideElementsForCollapse();
                
                // If the sidebar was temporarily expanded, collapse it again
                this.sidebarCollapseTimeout = setTimeout(() => {
                    this.collapseSidebar();
                }, 100);
            }
        });
    }
    
    expandSidebar() {
        const $sidebar = $('#inbox-sidebar');
        
        // If collapsed, expand and pin
        if ($sidebar.hasClass('collapsed')) {
            $sidebar.removeClass('collapsed hover-expand');
            this.sidebarPinned = true;
            
            // Show counts when expanded (if they have values) and reset styles
            this.showElementsForExpansion();
        }
    }
    
    collapseSidebar() {
        const $sidebar = $('#inbox-sidebar');
        
        $sidebar.addClass('collapsed');
        $sidebar.removeClass('hover-expand');
        
        // Hide counts, headers, and change icon weights
        this.hideElementsForCollapse();
    }
    
    toggleSidebarPin() {
        const $sidebar = $('#inbox-sidebar');
        
        if (this.sidebarPinned) {
            // Unpinning - collapse immediately
            this.sidebarPinned = false;
            this.collapseSidebar();
        } else {
            // Pinning - expand and stay expanded
            this.sidebarPinned = true;
            this.expandSidebar();
        }
    }
    
    hideElementsForCollapse() {
        // Hide counts and headers immediately without visual flash
        $('.folder-count, .filter-count').hide();
        $('.folder-header-text').hide();
        
        // Apply bold weight to icons
        $('.folder-icon').css('font-weight', '900');
    }
    
    showElementsForExpansion() {
        // Show counts when expanded (if they have values)
        $('.folder-count, .filter-count').each((i, el) => {
            const $el = $(el);
            if ($el.text() && $el.text() !== '0') {
                $el.show();
            }
        });
        
        // Show headers
        $('.folder-header-text').show();
        
        // Reset icon weight and remove any inline styles completely
        $('.folder-icon').each(function() {
            $(this).removeAttr('style');
        });
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
        this.updateReadUnreadButton();
    }
    
    handleReadUnreadToggle(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = $(e.currentTarget);
        const emailId = button.data('email-id');
        const emailRow = button.closest('.email-item');
        
        // Determine current state from the email row class (this is the source of truth)
        const isCurrentlyUnread = emailRow.hasClass('unread');
        const shouldMarkAsRead = isCurrentlyUnread; // If unread, mark as read; if read, mark as unread
        
        console.log(`Email ${emailId} current state: ${isCurrentlyUnread ? 'unread' : 'read'}, will mark as: ${shouldMarkAsRead ? 'read' : 'unread'}`);
        
        // Toggle read status
        this.toggleEmailReadStatus(emailId, shouldMarkAsRead, button);
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
        
        // Always use the main inbox endpoint for SPA navigation
        const baseUrl = window.inboxData?.urls?.inbox || '/inbox/';
        
        // Use AJAX for smooth loading
        $.ajax({
            url: baseUrl,
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
                    
                    // Update page title
                    const folderName = this.currentFilters.folder || 'Inbox';
                    document.title = `${folderName} - Email Inbox`;
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
                    // this.showSuccess('Inbox refreshed successfully'); // Commented out - too noisy
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
    
    toggleSelectedReadUnread() {
        const selectedEmailElements = $('.email-checkbox:checked').closest('.email-item');
        let hasUnread = false;
        
        // Check if any selected emails are unread
        selectedEmailElements.each((i, element) => {
            if ($(element).hasClass('unread')) {
                hasUnread = true;
                return false; // Break out of each loop
            }
        });
        
        // If any email is unread, mark all as read. If all are read, mark all as unread.
        const shouldMarkAsRead = hasUnread;
        this.markSelectedAs(shouldMarkAsRead, shouldMarkAsRead ? 'read' : 'unread');
    }
    
    updateReadUnreadButton() {
        const $button = $('#mark-read-unread-toggle');
        const $icon = $button.find('i');
        const $text = $button.find('.read-unread-text');
        
        if (this.selectedEmails.size === 0) {
            return;
        }
        
        const selectedEmailElements = $('.email-checkbox:checked').closest('.email-item');
        let hasUnread = false;
        
        // Check if any selected emails are unread
        selectedEmailElements.each((i, element) => {
            if ($(element).hasClass('unread')) {
                hasUnread = true;
                return false; // Break out of each loop
            }
        });
        
        // Update button based on selection state
        if (hasUnread) {
            // At least one unread email - button should say "Mark as read"
            $icon.removeClass('fa-envelope').addClass('fa-envelope-open');
            $text.text('Mark as read');
            $button.attr('title', 'Mark as read');
        } else {
            // All selected emails are read - button should say "Mark as unread"
            $icon.removeClass('fa-envelope-open').addClass('fa-envelope');
            $text.text('Mark as unread');
            $button.attr('title', 'Mark as unread');
        }
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
            url: window.inboxData?.urls?.markSingleReadUnread?.replace('MESSAGE_ID', emailId) || `/inbox/mark-read-unread/${emailId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || ''
            },
            success: (response) => {
                if (response.success) {
                    console.log('Read/unread response:', response);
                    
                    // Update email row appearance first
                    const emailRow = button.closest('.email-item');
                    const newReadState = response.read;
                    
                    if (newReadState) {
                        // Email is now read
                        emailRow.removeClass('unread');
                        // Show envelope icon (closed envelope = read email shows "mark as unread" action)
                        button.html('<i class="fas fa-envelope text-muted"></i>');
                        button.attr('title', 'Mark as unread');
                    } else {
                        // Email is now unread
                        emailRow.addClass('unread');
                        // Show envelope-open icon (open envelope = unread email shows "mark as read" action)
                        button.html('<i class="fas fa-envelope-open text-primary"></i>');
                        button.attr('title', 'Mark as read');
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
    
    handleQuickDelete(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const emailId = $(e.currentTarget).data('email-id');
        
        if (confirm('Are you sure you want to delete this email?')) {
            this.deleteEmails([emailId]);
        }
    }
    
    handleImportanceToggle(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const button = $(e.currentTarget);
        const emailId = button.data('email-id');
        const icon = button.find('i');
        
        // Determine current flag state
        const isCurrentlyFlagged = icon.hasClass('fas') && icon.hasClass('fa-flag');
        const shouldFlag = !isCurrentlyFlagged;
        
        // Show loading state
        const originalHtml = button.html();
        button.html('<i class="fas fa-spinner fa-spin"></i>');
        
        // Make AJAX request to flag/unflag email
        $.ajax({
            url: `/inbox/flag/${emailId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                flagged: shouldFlag
            }),
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || ''
            },
            success: (response) => {
                if (response.success) {
                    // Update button appearance based on new flag state
                    if (response.flagged) {
                        button.html('<i class="fas fa-flag text-danger" title="Flagged"></i>');
                        button.attr('title', 'Remove flag');
                    } else {
                        button.html('<i class="far fa-flag text-muted opacity-25" title="Not flagged"></i>');
                        button.attr('title', 'Add flag');
                    }
                    
                    this.showSuccess(`Email ${response.flagged ? 'flagged' : 'unflagged'} successfully`);
                } else {
                    button.html(originalHtml);
                    this.showError(response.error || 'Failed to update flag status');
                }
            },
            error: () => {
                button.html(originalHtml);
                this.showError('Failed to update flag status');
            }
        });
    }
    
    deleteEmails(emailIds) {
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
                    this.showSuccess(response.message || 'Email deleted successfully');
                    this.loadEmails();
                } else {
                    this.showError(response.error || 'Failed to delete email');
                }
            },
            error: () => {
                this.showError('Failed to delete email');
            }
        });
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
        
        // Attachment icon - check for both array and boolean formats
        const hasAttachments = (Array.isArray(email.attachments) && email.attachments.length > 0) || 
                              (email.attachments === true) ||
                              (typeof email.attachments === 'string' && email.attachments.length > 0);
        const attachmentIcon = hasAttachments ? '<i class="fas fa-paperclip text-muted" title="Has attachments"></i>' : '';
        
        // Flag button - check 'flagged' field only (no longer using importance)
        const isFlagged = email.flagged === true;
        const flagButton = isFlagged
            ? `<button class="importance-btn" data-email-id="${email.id}" title="Remove flag">
                 <i class="fas fa-flag text-danger" title="Flagged"></i>
               </button>`
            : `<button class="importance-btn" data-email-id="${email.id}" title="Add flag">
                 <i class="far fa-flag text-muted opacity-25" title="Not flagged"></i>
               </button>`;
        
        // Categories - safely handle and escape
        const categoriesHtml = email.categories && email.categories.trim()
            ? `<span class="categories-text" title="${this.escapeHtml(email.categories)}">${this.escapeHtml(email.categories.length > 12 ? email.categories.substring(0, 12) + '...' : email.categories)}</span>`
            : '<span class="text-muted">-</span>';
        
        const senderName = this.escapeHtml(email.sender_name || email.sender_email || '');
        const subject = this.escapeHtml(email.subject || '(No subject)');
        
        // Clean email preview - no truncation
        let preview = '';
        if (email.body) {
            preview = email.body.replace(/\s+/g, ' ').trim();
        }
        preview = this.escapeHtml(preview);
        
        // Format date
        let formattedDate = 'Unknown';
        if (email.received_time) {
            try {
                const date = new Date(email.received_time + ' UTC');
                const now = new Date();
                const diffTime = Math.abs(now - date);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays === 1) {
                    formattedDate = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                } else if (diffDays <= 7) {
                    formattedDate = date.toLocaleDateString([], {weekday: 'short'});
                } else if (date.getFullYear() === now.getFullYear()) {
                    formattedDate = date.toLocaleDateString([], {month: 'short', day: 'numeric'});
                } else {
                    formattedDate = date.toLocaleDateString([], {year: '2-digit', month: 'short', day: 'numeric'});
                }
            } catch (e) {
                formattedDate = email.received_time.split(' ')[0];
            }
        }
        
        // Quick actions for hover - fix icon logic
        const quickActions = `
            <div class="email-item-actions">
                <button class="quick-action-btn read-unread-btn" 
                        data-email-id="${email.id}"
                        title="${email.unread ? 'Mark as read' : 'Mark as unread'}">
                    ${email.unread 
                        ? '<i class="fas fa-envelope-open text-primary"></i>'
                        : '<i class="fas fa-envelope text-muted"></i>'
                    }
                </button>
                <button class="quick-action-btn delete-btn" 
                        data-email-id="${email.id}" 
                        title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        return `
            <div class="email-item ${unreadClass}" data-email-id="${email.id}">
                <div class="email-item-checkbox">
                    <input type="checkbox" class="email-checkbox" value="${email.id}">
                </div>
                <div class="email-item-categories">
                    ${categoriesHtml}
                </div>
                <div class="email-item-importance">
                    ${flagButton}
                </div>
                <div class="email-item-sender">
                    <span class="sender-name" title="${this.escapeHtml(email.sender_email || '')}">${senderName}</span>
                </div>
                <div class="email-item-subject">
                    <a href="/inbox/view/${this.escapeHtml(email.id)}/" class="email-link">
                        <span class="subject">
                            ${subject}
                            ${attachmentIcon}
                        </span>
                        <span class="email-preview">${preview}</span>
                    </a>
                </div>
                <div class="email-item-date">
                    <span class="date-time" title="${email.received_time || ''}">${formattedDate}</span>
                </div>
                ${quickActions}
            </div>
        `;
    }
    
    updatePagination(pagination) {
        // Update pagination info and controls
        // This would be implemented based on the pagination structure
        console.log('Pagination updated:', pagination);
    }
    
    updateFolderStats(stats) {
        const $sidebar = $('#inbox-sidebar');
        const isCollapsed = $sidebar.hasClass('collapsed');
        
        if (!isCollapsed) {
            // Update folder counts only when expanded
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
        // Auto-refresh every 20 seconds, but only if no emails are selected
        this.refreshInterval = setInterval(() => {
            if (this.selectedEmails.size === 0) {
                this.refreshInbox();
            }
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
        if (this.sidebarCollapseTimeout) {
            clearTimeout(this.sidebarCollapseTimeout);
        }
    }
    
    showLoading() {
        $('.email-list').addClass('loading');
        $('#loading-overlay').show();
    }
    
    hideLoading() {
        $('.email-list').removeClass('loading');
        $('#loading-overlay').hide();
        // Also remove folder loading states when emails finish loading
        this.removeLoadingFromFolders();
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

    navigateToFolder(url) {
        // Extract folder from URL - be more specific with patterns
        let folder = 'Inbox'; // default
        
        if (url.includes('/inbox/sent/')) {
            folder = 'Sent Items';
        } else if (url.includes('/inbox/deleted/')) {
            folder = 'Deleted Items';
        } else if (url.includes('/inbox/drafts/')) {
            folder = 'Drafts';
        } else if (url.includes('/inbox/outbox/')) {
            folder = 'Outbox';
        } else if (url.includes('/inbox/')) {
            folder = 'Inbox';
        }
        
        console.log(`Navigating to folder: ${folder} from URL: ${url}`);
        
        // Add loading state to the clicked folder
        $('.folder-item').removeClass('loading');
        this.addLoadingToFolder(folder);
        
        this.loadFolderContent(folder, true);
    }
    
    addLoadingToFolder(folder) {
        // Add loading state based on folder name, not URL matching
        switch(folder) {
            case 'Inbox':
                $('.folder-item a[href*="/inbox/"]:not([href*="/sent/"]):not([href*="/deleted/"]):not([href*="/drafts/"]):not([href*="/outbox/"])').closest('.folder-item').addClass('loading');
                break;
            case 'Sent Items':
            case 'Sent Mail':
                $('.folder-item a[href*="/sent/"]').closest('.folder-item').addClass('loading');
                break;
            case 'Deleted Items':
            case 'Trash':
                $('.folder-item a[href*="/deleted/"]').closest('.folder-item').addClass('loading');
                break;
            case 'Drafts':
                $('.folder-item a[href*="/drafts/"]').closest('.folder-item').addClass('loading');
                break;
            case 'Outbox':
                $('.folder-item a[href*="/outbox/"]').closest('.folder-item').addClass('loading');
                break;
        }
    }
    
    removeLoadingFromFolders() {
        // Remove loading state from all folders
        $('.folder-item').removeClass('loading');
    }
    
    loadFolderContent(folder, pushHistory = true) {
        // Update active folder in sidebar
        this.updateActiveFolderInSidebar(folder);
        
        // Update current filters
        this.currentFilters.folder = folder;
        this.currentPage = 1;
        
        // Clear selections
        this.selectedEmails.clear();
        $('#select-all').prop('checked', false).prop('indeterminate', false);
        this.updateSelectionState(0);
        
        // Update URL without page refresh
        if (pushHistory) {
            const newUrl = this.getFolderUrl(folder);
            window.history.pushState({ folder: folder }, `${folder} - Email Inbox`, newUrl);
        }
        
        // Update page title and any folder indicators
        this.updateFolderDisplay(folder);
        
        // Load emails for the new folder
        this.loadEmails();
    }
    
    updateFolderDisplay(folder) {
        // Update page title
        document.title = `${folder} - Email Inbox`;
        
        // You can add a breadcrumb or header update here if needed
        // For example, if you have a folder name display in the header:
        // $('.current-folder-name').text(folder);
    }
    
    getFolderUrl(folder) {
        // Get the base path up to /inbox/ or just the domain
        const currentPath = window.location.pathname;
        let basePath = '';
        
        // Find the base path (everything before /inbox/)
        const inboxIndex = currentPath.indexOf('/inbox');
        if (inboxIndex !== -1) {
            basePath = currentPath.substring(0, inboxIndex);
        } else {
            // If no /inbox/ found, use just the domain
            basePath = '';
        }
        
        // Generate clean folder URL
        const folderPath = this.getFolderUrlPath(folder);
        return basePath + folderPath;
    }
    
    getFolderUrlPath(folder) {
        const folderMap = {
            'Inbox': '/inbox/',
            'Sent Items': '/inbox/sent/',
            'Sent Mail': '/inbox/sent/',
            'Deleted Items': '/inbox/deleted/',
            'Trash': '/inbox/deleted/',
            'Drafts': '/inbox/drafts/',
            'Outbox': '/inbox/outbox/'
        };
        return folderMap[folder] || '/inbox/';
    }

    navigateToEmailView(url) {
        // Extract email ID from URL
        const emailIdMatch = url.match(/\/inbox\/view\/([^\/]+)\//);
        const emailId = emailIdMatch ? emailIdMatch[1] : null;

        if (!emailId) {
            this.showError('Invalid email URL');
            return;
        }

        // Add loading state to the email item
        $(`.email-item[data-email-id="${emailId}"]`).addClass('loading');

        // Update current filters to show only this email
        this.currentFilters = {
            search: '',
            unread: false,
            important: false,
            attachments: false,
            sort_by: 'received_time',
            sort_order: 'desc',
            folder: this.currentFilters.folder // Keep current folder
        };
        this.currentPage = 1;

        // Clear selections
        this.selectedEmails.clear();
        $('#select-all').prop('checked', false).prop('indeterminate', false);
        this.updateSelectionState(0);

        // Update URL without page refresh
        const newUrl = url; // Use the original URL as-is
        window.history.pushState({ 
            folder: this.currentFilters.folder,
            emailId: emailId,
            view: 'email'
        }, `Email - ${this.currentFilters.folder}`, newUrl);

        // Load the specific email
        this.loadEmailById(emailId);
    }

    loadEmailById(emailId) {
        this.showLoading();

        const params = new URLSearchParams({
            email_id: emailId
        });

        // Always use the main inbox endpoint for SPA navigation
        const baseUrl = window.inboxData?.urls?.inbox || '/inbox/';
        
        // Use AJAX for smooth loading
        $.ajax({
            url: baseUrl,
            method: 'GET',
            data: params.toString(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: (response) => {
                if (response.success && response.email_view) {
                    // Replace the email list with the email view
                    this.updateEmailView(response.html);
                    
                    // Update page title with email subject
                    const emailSubject = response.email?.subject || 'Email';
                    document.title = `${emailSubject} - Email Inbox`;
                    
                    // Automatically mark email as read when opening it
                    this.markEmailAsReadOnOpen(emailId);
                } else {
                    this.showError('Failed to load email details');
                }
            },
            error: () => {
                this.showError('Failed to load email details');
            },
            complete: () => {
                this.hideLoading();
            }
        });
    }
    
    updateEmailView(html) {
        // Create email view overlay instead of replacing content
        let $overlay = $('.email-view-overlay');
        if ($overlay.length === 0) {
            $overlay = $('<div class="email-view-overlay"></div>');
            $('.inbox-main').append($overlay);
        }
        
        // Set the email view content
        $overlay.html(html).show();
        
        // Include the email view CSS if not already included
        if (!$('link[href*="email_view.css"]').length) {
            $('<link>', {
                rel: 'stylesheet',
                type: 'text/css',
                href: '/static/normieapp/css/email_view.css'
            }).appendTo('head');
        }
        
        // Hide pagination and update toolbar for email view
        $('.pagination-container').hide();
        this.updateToolbarForEmailView();
    }
    
    updateToolbarForEmailView() {
        // Hide selection controls and search for email view
        $('.select-actions, .search-container, .filter-dropdown').hide();
        
        // Show only basic actions
        $('.toolbar-actions').hide();
    }
    
    hideEmailView() {
        // Hide the email view overlay
        $('.email-view-overlay').hide();
        
        // Restore toolbar and pagination
        this.restoreToolbarForInbox();
    }
    
    restoreToolbarForInbox() {
        // Show selection controls, search, and filter dropdown
        $('.select-actions, .search-container, .filter-dropdown').show();
        
        // Show default toolbar actions
        $('.toolbar-actions').show();
        
        // Show pagination container
        $('.pagination-container').show();
    }
    
    navigateBackToInbox() {
        // Simply hide the email view overlay
        this.hideEmailView();
        
        // Update URL to current folder without email ID
        const currentFolder = this.currentFilters.folder || 'Inbox';
        const newUrl = this.getFolderUrl(currentFolder);
        window.history.pushState({ 
            folder: currentFolder 
        }, `${currentFolder} - Email Inbox`, newUrl);
        
        // Update page title
        document.title = `${currentFolder} - Email Inbox`;
    }
    
    markEmailAsReadOnOpen(emailId) {
        // Silently mark email as read when opened (don't show notifications for this automatic action)
        $.ajax({
            url: window.inboxData?.urls?.mark_single_read_unread?.replace('MESSAGE_ID', emailId) || `/inbox/mark-read-unread/${emailId}/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val(),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                read: true
            }),
            success: (response) => {
                if (response.success) {
                    // Update the email row in the background if it exists
                    const $emailRow = $(`.email-item[data-email-id="${emailId}"]`);
                    if ($emailRow.length) {
                        $emailRow.removeClass('email-unread');
                        $emailRow.find('.read-unread-btn')
                            .attr('title', 'Mark as unread')
                            .find('i')
                            .removeClass('fa-envelope-open')
                            .addClass('fa-envelope');
                    }
                }
                // Don't show error messages for automatic mark-as-read to avoid UI noise
            },
            error: () => {
                // Silently fail - don't disrupt the user experience
                console.debug('Could not automatically mark email as read:', emailId);
            }
        });
    }
    
    navigateToCompose(mode = 'new', emailId = null) {
        // Show loading state
        this.showLoading();
        
        // Clear selections
        this.selectedEmails.clear();
        $('#select-all').prop('checked', false).prop('indeterminate', false);
        this.updateSelectionState(0);
        
        // Update URL without page refresh
        let newUrl = '/inbox/compose/';
        if (mode === 'reply' && emailId) {
            newUrl = `/inbox/reply/${emailId}/`;
        } else if (mode === 'forward' && emailId) {
            newUrl = `/inbox/forward/${emailId}/`;
        }
        
        window.history.pushState({ 
            folder: this.currentFilters.folder,
            view: 'compose',
            mode: mode,
            emailId: emailId
        }, `${mode === 'new' ? 'Compose' : mode === 'reply' ? 'Reply' : 'Forward'} - Email Inbox`, newUrl);
        
        // Load the compose interface
        this.loadComposeInterface(mode, emailId);
    }
    
    loadComposeInterface(mode = 'new', emailId = null) {
        const params = new URLSearchParams({
            mode: mode
        });
        
        if (emailId) {
            params.append('email_id', emailId);
        }
        
        // Always use the compose endpoint
        const baseUrl = window.inboxData?.urls?.compose || '/inbox/compose/';
        
        // Use AJAX for smooth loading
        $.ajax({
            url: baseUrl,
            method: 'GET',
            data: params.toString(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: (response) => {
                if (response.success && response.compose_view) {
                    // Replace the email list with the compose view
                    this.updateEmailView(response.html);
                    
                    // Initialize compose manager
                    this.initializeComposeManager();
                    
                    // Update page title
                    const title = mode === 'new' ? 'Compose' : mode === 'reply' ? 'Reply' : 'Forward';
                    document.title = `${title} - Email Inbox`;
                } else {
                    this.showError('Failed to load compose interface');
                }
            },
            error: () => {
                this.showError('Failed to load compose interface');
            },
            complete: () => {
                this.hideLoading();
            }
        });
    }
    
    initializeComposeManager() {
        // Initialize the compose manager if it doesn't exist
        if (!window.composeManager) {
            window.composeManager = new ComposeManager();
        }
        window.composeManager.initializeCompose();
    }
}

// Initialize when document is ready
$(document).ready(function() {
    window.inboxManager = new InboxManager();
}); 