/**
 * Contacts Management JavaScript
 * 
 * Provides functionality for searching, viewing, and managing contacts
 * from the organizational directory database.
 */

class ContactsManager {
    constructor() {
        this.currentQuery = '';
        this.currentPage = 1;
        this.perPage = 25;
        this.sortBy = 'name';
        this.sortOrder = 'asc';
        this.searchTimeout = null;
        this.currentRequest = null;
        this.selectedContact = null;
        
        this.init();
    }
    
    init() {
        if (!window.contactsData.isAvailable) {
            console.log('Contacts database not available');
            return;
        }
        
        this.bindEvents();
        console.log('ContactsManager initialized');
    }
    
    bindEvents() {
        // Search functionality
        $('#contact-search').on('input', (e) => this.handleSearchInput(e));
        $('#search-btn').on('click', () => this.performSearch());
        $('#clear-search').on('click', () => this.clearSearch());
        
        // Sort controls
        $('#sort-by').on('change', () => this.handleSortChange());
        $('#sort-order').on('click', () => this.toggleSortOrder());
        
        // Action buttons
        $('#export-btn').on('click', () => this.openExportModal());
        $('#refresh-btn').on('click', () => this.refreshResults());
        
        // View controls
        $('.view-btn').on('click', (e) => this.changeView(e));
        
        // Enter key in search
        $('#contact-search').on('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
        
        // Contact item clicks (delegated)
        $(document).on('click', '.contact-item', (e) => this.handleContactClick(e));
        
        // Pagination (delegated)
        $(document).on('click', '.pagination-btn', (e) => this.handlePaginationClick(e));
    }
    
    handleSearchInput(e) {
        const query = e.target.value.trim();
        
        // Show/hide clear button
        if (query) {
            $('#clear-search').show();
        } else {
            $('#clear-search').hide();
        }
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Debounce search
        this.searchTimeout = setTimeout(() => {
            if (query !== this.currentQuery) {
                this.currentQuery = query;
                this.currentPage = 1;
                
                if (query.length >= 2) {
                    this.performSearch();
                } else if (query.length === 0) {
                    this.showEmptyState();
                }
            }
        }, 500);
    }
    
    performSearch() {
        const query = $('#contact-search').val().trim();
        
        if (query.length < 2) {
            this.showMessage('Please enter at least 2 characters to search', 'warning');
            return;
        }
        
        this.currentQuery = query;
        this.loadContacts();
    }
    
    clearSearch() {
        $('#contact-search').val('');
        $('#clear-search').hide();
        this.currentQuery = '';
        this.currentPage = 1;
        this.showEmptyState();
        $('#export-btn').prop('disabled', true);
    }
    
    handleSortChange() {
        this.sortBy = $('#sort-by').val();
        this.currentPage = 1;
        
        if (this.currentQuery) {
            this.loadContacts();
        }
    }
    
    toggleSortOrder() {
        const $btn = $('#sort-order');
        const currentOrder = $btn.data('order');
        
        if (currentOrder === 'asc') {
            this.sortOrder = 'desc';
            $btn.data('order', 'desc')
               .attr('title', 'Sort descending')
               .html('<i class="fas fa-sort-alpha-up"></i>');
        } else {
            this.sortOrder = 'asc';
            $btn.data('order', 'asc')
               .attr('title', 'Sort ascending')
               .html('<i class="fas fa-sort-alpha-down"></i>');
        }
        
        this.currentPage = 1;
        
        if (this.currentQuery) {
            this.loadContacts();
        }
    }
    
    async loadContacts() {
        if (!this.currentQuery) {
            this.showEmptyState();
            return;
        }
        
        // Cancel previous request
        if (this.currentRequest) {
            this.currentRequest.abort();
        }
        
        this.showLoading();
        
        try {
            const url = new URL(window.contactsData.urls.search, window.location.origin);
            url.searchParams.set('q', this.currentQuery);
            url.searchParams.set('page', this.currentPage);
            url.searchParams.set('per_page', this.perPage);
            url.searchParams.set('sort_by', this.sortBy);
            url.searchParams.set('sort_order', this.sortOrder);
            
            const controller = new AbortController();
            this.currentRequest = controller;
            
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                signal: controller.signal
            });
            
            const data = await response.json();
            this.currentRequest = null;
            
            if (data.success) {
                this.displayResults(data.results, data.pagination);
                $('#export-btn').prop('disabled', data.pagination.total_count === 0);
            } else {
                this.showError(data.error || 'Search failed');
            }
            
        } catch (error) {
            this.currentRequest = null;
            if (error.name !== 'AbortError') {
                console.error('Contact search error:', error);
                this.showError('Search failed. Please try again.');
            }
        }
    }
    
    displayResults(contacts, pagination) {
        const $list = $('#contacts-list');
        
        if (contacts.length === 0) {
            $list.html(`
                <div class="no-results">
                    <div class="empty-icon">
                        <i class="fas fa-user-slash"></i>
                    </div>
                    <h3>No contacts found</h3>
                    <p>No contacts match your search for "${this.escapeHtml(this.currentQuery)}"</p>
                    <p>Try a different search term or check the spelling.</p>
                </div>
            `);
            this.updateResultsInfo(pagination);
            this.hidePagination();
            return;
        }
        
        // Render contacts
        const html = contacts.map(contact => this.renderContactItem(contact)).join('');
        $list.html(html);
        
        // Update pagination and info
        this.updateResultsInfo(pagination);
        this.updatePagination(pagination);
    }
    
    renderContactItem(contact) {
        const name = this.escapeHtml(contact.display_name || contact.name || 'Unknown');
        const email = this.escapeHtml(contact.email || '');
        const company = this.escapeHtml(contact.company || '');
        const department = this.escapeHtml(contact.department || '');
        const title = this.escapeHtml(contact.title || '');
        
        const subtitle = [title, department, company].filter(Boolean).join(' • ');
        
        return `
            <div class="contact-item" data-email="${email}">
                <div class="contact-avatar">
                    <div class="avatar-circle">
                        ${this.getInitials(name)}
                    </div>
                </div>
                <div class="contact-info">
                    <div class="contact-main">
                        <div class="contact-name">${name}</div>
                        <div class="contact-email">${email}</div>
                    </div>
                    ${subtitle ? `<div class="contact-subtitle">${subtitle}</div>` : ''}
                </div>
                <div class="contact-actions">
                    <button class="action-btn" onclick="contactsManager.composeToContact('${email}')" title="Compose email">
                        <i class="fas fa-envelope"></i>
                    </button>
                    <button class="action-btn" onclick="contactsManager.viewContactDetail('${email}')" title="View details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    getInitials(name) {
        if (!name) return '?';
        
        const parts = name.split(/[\s,]+/);
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        } else {
            return name.substring(0, 2).toUpperCase();
        }
    }
    
    updateResultsInfo(pagination) {
        const $info = $('#results-count');
        
        if (pagination.total_count === 0) {
            $info.text('No contacts found');
        } else if (pagination.total_count === 1) {
            $info.text('1 contact found');
        } else {
            $info.text(`${pagination.total_count.toLocaleString()} contacts found`);
        }
    }
    
    updatePagination(pagination) {
        const $container = $('#pagination-container');
        const $info = $('#pagination-info');
        const $controls = $('#pagination-controls');
        
        if (pagination.total_pages <= 1) {
            $container.hide();
            return;
        }
        
        // Update pagination info
        $info.text(`Showing ${pagination.start_index}-${pagination.end_index} of ${pagination.total_count}`);
        
        // Generate pagination buttons
        let html = '';
        
        // Previous button
        if (pagination.has_previous) {
            html += `<button class="pagination-btn" data-page="${pagination.current_page - 1}">
                <i class="fas fa-chevron-left"></i> Previous
            </button>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, pagination.current_page - 2);
        const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === pagination.current_page;
            html += `<button class="pagination-btn ${isActive ? 'active' : ''}" data-page="${i}">
                ${i}
            </button>`;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `<button class="pagination-btn" data-page="${pagination.current_page + 1}">
                Next <i class="fas fa-chevron-right"></i>
            </button>`;
        }
        
        $controls.html(html);
        $container.show();
    }
    
    hidePagination() {
        $('#pagination-container').hide();
    }
    
    handlePaginationClick(e) {
        const page = parseInt($(e.currentTarget).data('page'));
        if (page && page !== this.currentPage) {
            this.currentPage = page;
            this.loadContacts();
        }
    }
    
    handleContactClick(e) {
        const $item = $(e.currentTarget);
        const email = $item.data('email');
        
        // Don't trigger if clicking on action buttons
        if ($(e.target).closest('.contact-actions').length > 0) {
            return;
        }
        
        this.viewContactDetail(email);
    }
    
    async viewContactDetail(email) {
        if (!email) return;
        
        try {
            const url = window.contactsData.urls.detail.replace('EMAIL_PLACEHOLDER', encodeURIComponent(email));
            
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success && data.contact) {
                this.showContactDetail(data.contact);
            } else {
                this.showMessage(data.error || 'Contact not found', 'error');
            }
            
        } catch (error) {
            console.error('Error loading contact detail:', error);
            this.showMessage('Failed to load contact details', 'error');
        }
    }
    
    showContactDetail(contact) {
        this.selectedContact = contact;
        
        const name = this.escapeHtml(contact.DisplayName || contact.name || 'Unknown');
        const email = this.escapeHtml(contact.SmtpAddress || contact.email || '');
        
        const html = `
            <div class="contact-detail">
                <div class="contact-header">
                    <div class="contact-avatar-large">
                        ${this.getInitials(name)}
                    </div>
                    <div class="contact-title">
                        <h4>${name}</h4>
                        <p>${email}</p>
                    </div>
                </div>
                <div class="contact-fields">
                    ${this.renderContactField('Company', contact.CompanyName)}
                    ${this.renderContactField('Department', contact.DepartmentName)}
                    ${this.renderContactField('Title', contact.Title)}
                    ${this.renderContactField('Office Location', contact.OfficeLocation)}
                    ${this.renderContactField('Business Phone', contact.BusinessTelephoneNumber)}
                    ${this.renderContactField('Mobile Phone', contact.MobileTelephoneNumber)}
                    ${this.renderContactField('Fax', contact.PrimaryFaxNumber)}
                </div>
            </div>
        `;
        
        $('#contact-detail-content').html(html);
        $('#contact-detail-modal').show();
    }
    
    renderContactField(label, value) {
        if (!value) return '';
        
        return `
            <div class="contact-field">
                <label>${this.escapeHtml(label)}:</label>
                <span>${this.escapeHtml(value)}</span>
            </div>
        `;
    }
    
    composeToContact(email) {
        if (!email) {
            if (this.selectedContact) {
                email = this.selectedContact.SmtpAddress || this.selectedContact.email;
            }
        }
        
        if (email) {
            const composeUrl = `${window.contactsData.urls.compose}?to=${encodeURIComponent(email)}`;
            window.location.href = composeUrl;
        }
    }
    
    openExportModal() {
        if (!this.currentQuery) {
            this.showMessage('Please perform a search first', 'warning');
            return;
        }
        
        // Update export count (this would need to be calculated)
        $('#export-count').text(`Results from current search will be exported`);
        $('#export-modal').show();
    }
    
    async performExport() {
        if (!this.currentQuery) {
            this.showMessage('Please perform a search first', 'warning');
            return;
        }
        
        try {
            const response = await fetch(window.contactsData.urls.export, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.contactsData.csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    format: $('#export-format').val(),
                    query: this.currentQuery
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Create and trigger download
                const blob = new Blob([data.content], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = data.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showMessage(`Exported ${data.count} contacts successfully`, 'success');
                this.closeExportModal();
            } else {
                this.showMessage(data.error || 'Export failed', 'error');
            }
            
        } catch (error) {
            console.error('Export error:', error);
            this.showMessage('Export failed. Please try again.', 'error');
        }
    }
    
    changeView(e) {
        const $btn = $(e.currentTarget);
        const view = $btn.data('view');
        
        $('.view-btn').removeClass('active');
        $btn.addClass('active');
        
        // Toggle view classes on container
        const $list = $('#contacts-list');
        if (view === 'grid') {
            $list.addClass('grid-view');
        } else {
            $list.removeClass('grid-view');
        }
    }
    
    refreshResults() {
        if (this.currentQuery) {
            this.loadContacts();
        } else {
            this.showMessage('Enter a search query first', 'info');
        }
    }
    
    showLoading() {
        $('#contacts-list').html(`
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <h3>Searching contacts...</h3>
                <p>Please wait while we search the directory</p>
            </div>
        `);
    }
    
    showEmptyState() {
        $('#contacts-list').html(`
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3>Search Contacts</h3>
                <p>Enter a name, email address, or company to find contacts</p>
            </div>
        `);
        $('#results-count').text('Enter search query to find contacts');
        this.hidePagination();
    }
    
    showError(message) {
        $('#contacts-list').html(`
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Search Error</h3>
                <p>${this.escapeHtml(message)}</p>
                <button class="btn btn-primary" onclick="contactsManager.refreshResults()">
                    Try Again
                </button>
            </div>
        `);
    }
    
    showMessage(message, type = 'info') {
        // Simple toast notification (you could enhance this)
        const toast = $(`
            <div class="toast toast-${type}">
                <div class="toast-content">
                    <i class="fas fa-${this.getToastIcon(type)}"></i>
                    <span>${this.escapeHtml(message)}</span>
                </div>
            </div>
        `);
        
        $('body').append(toast);
        
        setTimeout(() => {
            toast.addClass('show');
        }, 100);
        
        setTimeout(() => {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for modal management
window.closeContactDetail = function() {
    $('#contact-detail-modal').hide();
    window.contactsManager.selectedContact = null;
};

window.closeExportModal = function() {
    $('#export-modal').hide();
};

window.composeToContact = function() {
    window.contactsManager.composeToContact();
};

// Initialize on page load
$(document).ready(function() {
    window.contactsManager = new ContactsManager();
}); 