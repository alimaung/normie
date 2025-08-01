/**
 * Check Names Component - Outlook-style contact verification
 * 
 * Provides detailed contact search and selection modal similar to Outlook's
 * "Check Names" feature with expanded contact details.
 */

class CheckNamesManager {
    constructor() {
        this.currentTargetField = null;
        this.selectedContacts = new Set();
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        console.log('CheckNamesManager initialized');
    }
    
    bindEvents() {
        // Check names button clicks
        $(document).on('click', '.check-names-btn', (e) => {
            const targetField = $(e.currentTarget).data('target');
            this.openModal(targetField);
        });
        
        // Modal events
        $(document).on('click', '.modal-overlay', () => this.closeModal());
        $(document).on('click', '.modal-close', () => this.closeModal());
        $(document).on('keydown', '#check-names-search', (e) => this.handleSearchKeydown(e));
        $(document).on('input', '#check-names-search', (e) => this.handleSearchInput(e));
        $(document).on('click', '#check-names-search-btn', () => this.performSearch());
        
        // Contact selection
        $(document).on('click', '.contact-item', (e) => this.toggleContactSelection(e));
        $(document).on('dblclick', '.contact-item', (e) => this.addContactAndClose(e));
        
        // Modal actions
        $(document).on('click', '.add-selected-btn', () => this.addSelectedContacts());
        $(document).on('click', '.cancel-btn', () => this.closeModal());
        
        // Keyboard shortcuts
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape' && this.isModalOpen()) {
                this.closeModal();
            }
        });
    }
    
    openModal(targetFieldId) {
        this.currentTargetField = targetFieldId;
        this.selectedContacts.clear();
        
        // Show modal
        $('#check-names-modal').show();
        
        // Focus search field
        setTimeout(() => {
            $('#check-names-search').focus();
        }, 100);
        
        // Clear previous results
        $('#check-names-results').html('<div class="no-results">Start typing to search contacts...</div>');
        
        console.log('Check Names modal opened for field:', targetFieldId);
    }
    
    closeModal() {
        $('#check-names-modal').hide();
        this.currentTargetField = null;
        this.selectedContacts.clear();
        $('#check-names-search').val('');
        $('#check-names-results').empty();
    }
    
    isModalOpen() {
        return $('#check-names-modal').is(':visible');
    }
    
    handleSearchKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.performSearch();
        }
    }
    
    handleSearchInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Debounce search
        this.searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                this.performSearch(query);
            } else if (query.length === 0) {
                $('#check-names-results').html('<div class="no-results">Start typing to search contacts...</div>');
            }
        }, 500);
    }
    
    async performSearch(query = null) {
        if (!query) {
            query = $('#check-names-search').val().trim();
        }
        
        if (query.length < 2) {
            return;
        }
        
        // Show loading
        $('#check-names-results').html('<div class="loading">Searching contacts...</div>');
        
        try {
            const response = await fetch(`/inbox/contacts/autocomplete/?q=${encodeURIComponent(query)}&limit=50`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success && data.results) {
                this.displayResults(data.results, query);
            } else {
                this.displayError(data.error || 'Search failed');
            }
            
        } catch (error) {
            console.error('Contact search error:', error);
            this.displayError('Search failed. Please try again.');
        }
    }
    
    displayResults(contacts, query) {
        if (contacts.length === 0) {
            $('#check-names-results').html(`
                <div class="no-results">
                    <div class="no-results-message">No contacts found for "${this.escapeHtml(query)}"</div>
                    <div class="no-results-suggestion">Try a different name or email address</div>
                </div>
            `);
            return;
        }
        
        const html = contacts.map(contact => this.renderContactItem(contact)).join('');
        $('#check-names-results').html(html);
        
        // Update count
        $('.results-count').text(`${contacts.length} contacts found`);
    }
    
    renderContactItem(contact) {
        const name = this.escapeHtml(contact.display_name || contact.name || '');
        const email = this.escapeHtml(contact.email || '');
        const company = this.escapeHtml(contact.company || '');
        const department = this.escapeHtml(contact.department || '');
        const title = this.escapeHtml(contact.title || '');
        const formatted = this.escapeHtml(contact.formatted || `${name} <${email}>`);
        
        const subtitle = [title, department, company].filter(Boolean).join(' • ');
        
        return `
            <div class="contact-item" data-formatted="${formatted}" data-email="${email}">
                <div class="contact-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="contact-details">
                    <div class="contact-main-info">
                        <div class="contact-name">${name}</div>
                        <div class="contact-email">${email}</div>
                    </div>
                    ${subtitle ? `<div class="contact-subtitle">${subtitle}</div>` : ''}
                </div>
                <div class="contact-actions">
                    <button class="contact-add-btn" title="Add this contact">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    displayError(message) {
        $('#check-names-results').html(`
            <div class="error-results">
                <div class="error-message">${this.escapeHtml(message)}</div>
            </div>
        `);
    }
    
    toggleContactSelection(e) {
        const $contactItem = $(e.currentTarget);
        const email = $contactItem.data('email');
        
        if ($contactItem.hasClass('selected')) {
            $contactItem.removeClass('selected');
            this.selectedContacts.delete(email);
        } else {
            $contactItem.addClass('selected');
            this.selectedContacts.add(email);
        }
        
        this.updateSelectionCount();
    }
    
    addContactAndClose(e) {
        const $contactItem = $(e.currentTarget);
        this.addSingleContact($contactItem);
        this.closeModal();
    }
    
    addSingleContact($contactItem) {
        const formatted = $contactItem.data('formatted');
        const targetField = $(`#${this.currentTargetField}`);
        
        if (targetField.length && formatted) {
            const currentValue = targetField.val().trim();
            const newValue = currentValue ? 
                currentValue + ', ' + formatted : 
                formatted;
                
            targetField.val(newValue);
            targetField.trigger('change');
        }
    }
    
    addSelectedContacts() {
        if (this.selectedContacts.size === 0) {
            return;
        }
        
        const targetField = $(`#${this.currentTargetField}`);
        if (!targetField.length) {
            return;
        }
        
        // Get formatted strings for selected contacts
        const selectedFormatted = [];
        $('.contact-item.selected').each((i, item) => {
            selectedFormatted.push($(item).data('formatted'));
        });
        
        if (selectedFormatted.length > 0) {
            const currentValue = targetField.val().trim();
            const newValue = currentValue ? 
                currentValue + ', ' + selectedFormatted.join(', ') : 
                selectedFormatted.join(', ');
                
            targetField.val(newValue);
            targetField.trigger('change');
        }
        
        this.closeModal();
    }
    
    updateSelectionCount() {
        const count = this.selectedContacts.size;
        const $button = $('.add-selected-btn');
        
        if (count > 0) {
            $button.text(`Add Selected (${count})`);
            $button.prop('disabled', false);
        } else {
            $button.text('Add Selected');
            $button.prop('disabled', true);
        }
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Auto-initialize
$(document).ready(function() {
    if (typeof window.checkNamesManager === 'undefined') {
        window.checkNamesManager = new CheckNamesManager();
    }
});

// Export for manual initialization
window.CheckNamesManager = CheckNamesManager; 