/**
 * Fast Contact Autocomplete Component
 * 
 * Provides real-time autocomplete for email recipient fields using SQLite-backed
 * contact database. Optimized for performance with debouncing and caching.
 */

class ContactAutocomplete {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            minLength: 2,
            maxResults: 10,
            debounceDelay: 300,
            cache: true,
            cacheTimeout: 300000, // 5 minutes
            placeholder: 'Type name or email...',
            ...options
        };
        
        this.dropdown = null;
        this.cache = new Map();
        this.debounceTimer = null;
        this.currentRequest = null;
        this.selectedIndex = -1;
        this.isVisible = false;
        
        this.init();
    }
    
    init() {
        this.setupInput();
        this.createDropdown();
        this.bindEvents();
        
        console.log('ContactAutocomplete initialized for', this.input);
    }
    
    setupInput() {
        // Add styling and attributes to input
        this.input.setAttribute('autocomplete', 'off');
        this.input.setAttribute('spellcheck', 'false');
        
        if (!this.input.placeholder) {
            this.input.placeholder = this.options.placeholder;
        }
        
        // Wrap input in container for positioning
        if (!this.input.parentElement.classList.contains('autocomplete-container')) {
            const container = document.createElement('div');
            container.className = 'autocomplete-container';
            this.input.parentElement.insertBefore(container, this.input);
            container.appendChild(this.input);
        }
        
        this.container = this.input.closest('.autocomplete-container');
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.display = 'none';
        
        // Position dropdown relative to input
        this.container.appendChild(this.dropdown);
    }
    
    bindEvents() {
        // Input events
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));
        
        // Dropdown events
        this.dropdown.addEventListener('mousedown', (e) => this.handleDropdownClick(e));
        
        // Global events
        document.addEventListener('click', (e) => this.handleDocumentClick(e));
        window.addEventListener('resize', () => this.updateDropdownPosition());
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Cancel any pending request
        if (this.currentRequest) {
            this.currentRequest.abort();
            this.currentRequest = null;
        }
        
        if (query.length < this.options.minLength) {
            this.hideDropdown();
            return;
        }
        
        // Debounce the search
        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, this.options.debounceDelay);
    }
    
    handleKeydown(e) {
        if (!this.isVisible) return;
        
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
                    this.selectItem(items[this.selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.hideDropdown();
                break;
        }
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= this.options.minLength) {
            this.search(query);
        }
    }
    
    handleBlur(e) {
        // Delay hiding to allow dropdown clicks
        setTimeout(() => {
            if (!this.dropdown.matches(':hover')) {
                this.hideDropdown();
            }
        }, 150);
    }
    
    handleDropdownClick(e) {
        const item = e.target.closest('.autocomplete-item');
        if (item) {
            this.selectItem(item);
        }
    }
    
    handleDocumentClick(e) {
        if (!this.container.contains(e.target)) {
            this.hideDropdown();
        }
    }
    
    search(query) {
        // Check cache first
        if (this.options.cache && this.cache.has(query)) {
            const cached = this.cache.get(query);
            if (Date.now() - cached.timestamp < this.options.cacheTimeout) {
                this.showResults(cached.results, query);
                return;
            }
        }
        
        // Perform API search
        this.currentRequest = this.performSearch(query)
            .then(results => {
                this.currentRequest = null;
                
                // Cache results
                if (this.options.cache) {
                    this.cache.set(query, {
                        results: results,
                        timestamp: Date.now()
                    });
                }
                
                this.showResults(results, query);
            })
            .catch(error => {
                this.currentRequest = null;
                if (error.name !== 'AbortError') {
                    console.error('Autocomplete search error:', error);
                    this.showError('Search failed. Please try again.');
                }
            });
    }
    
    async performSearch(query) {
        const url = new URL('/inbox/contacts/autocomplete/', window.location.origin);
        url.searchParams.set('q', query);
        url.searchParams.set('limit', this.options.maxResults);
        
        const controller = new AbortController();
        this.currentRequest = controller;
        
        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            signal: controller.signal
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Search failed');
        }
        
        return data.results || [];
    }
    
    showResults(results, query) {
        if (results.length === 0) {
            this.showNoResults(query);
            return;
        }
        
        const html = results.map((contact, index) => 
            this.renderContactItem(contact, index)
        ).join('');
        
        this.dropdown.innerHTML = html;
        this.selectedIndex = -1;
        this.showDropdown();
    }
    
    renderContactItem(contact, index) {
        const name = this.escapeHtml(contact.name || contact.display_name || '');
        const email = this.escapeHtml(contact.email || '');
        const subtitle = this.escapeHtml(contact.subtitle || '');
        const formatted = this.escapeHtml(contact.formatted || `${name} <${email}>`);
        
        return `
            <div class="autocomplete-item" data-index="${index}" data-formatted="${formatted}">
                <div class="contact-main">
                    <div class="contact-name">${name}</div>
                    <div class="contact-email">${email}</div>
                </div>
                ${subtitle ? `<div class="contact-subtitle">${subtitle}</div>` : ''}
            </div>
        `;
    }
    
    showNoResults(query) {
        this.dropdown.innerHTML = `
            <div class="autocomplete-no-results">
                <div class="no-results-message">No contacts found for "${this.escapeHtml(query)}"</div>
                <div class="no-results-suggestion">Try a different name or email address</div>
            </div>
        `;
        this.selectedIndex = -1;
        this.showDropdown();
    }
    
    showError(message) {
        this.dropdown.innerHTML = `
            <div class="autocomplete-error">
                <div class="error-message">${this.escapeHtml(message)}</div>
            </div>
        `;
        this.selectedIndex = -1;
        this.showDropdown();
    }
    
    showDropdown() {
        this.updateDropdownPosition();
        this.dropdown.style.display = 'block';
        this.isVisible = true;
    }
    
    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.isVisible = false;
        this.selectedIndex = -1;
    }
    
    updateDropdownPosition() {
        if (!this.isVisible) return;
        
        const inputRect = this.input.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        // Position dropdown below input
        this.dropdown.style.top = `${inputRect.height + 2}px`;
        this.dropdown.style.left = '0';
        this.dropdown.style.width = `${inputRect.width}px`;
    }
    
    updateSelection() {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }
    
    selectItem(item) {
        const formatted = item.dataset.formatted;
        this.input.value = formatted;
        this.hideDropdown();
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Custom selection event
        this.input.dispatchEvent(new CustomEvent('contactSelected', {
            detail: { formatted: formatted },
            bubbles: true
        }));
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        if (this.currentRequest) {
            this.currentRequest.abort();
        }
        
        if (this.dropdown) {
            this.dropdown.remove();
        }
        
        this.cache.clear();
    }
}

// Auto-initialize autocomplete on recipient fields
document.addEventListener('DOMContentLoaded', function() {
    // Initialize autocomplete on compose recipient fields
    const recipientFields = document.querySelectorAll('#compose-to, #compose-cc, #compose-bcc');
    
    recipientFields.forEach(field => {
        if (field) {
            new ContactAutocomplete(field, {
                placeholder: field.placeholder || 'Start typing name or email...'
            });
        }
    });
});

// Export for manual initialization
window.ContactAutocomplete = ContactAutocomplete; 