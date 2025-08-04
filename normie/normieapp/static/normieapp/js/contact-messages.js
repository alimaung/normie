/**
 * Contact Messages Management
 * Handles contact-specific functionality in the inbox
 */

class ContactMessages {
    constructor() {
        this.archivePanel = document.getElementById('contact-archive-panel');
        this.archiveToggle = document.getElementById('contact-archive-toggle');
        this.archiveContent = document.getElementById('contact-archive-content');
        this.archiveList = document.getElementById('archive-list');
        this.archiveCount = document.getElementById('archive-count');
        this.isArchiveExpanded = false;
        
        this.bindEvents();
    }
    
    bindEvents() {
        // Archive panel toggle
        if (this.archiveToggle) {
            this.archiveToggle.addEventListener('click', () => this.toggleArchivePanel());
        }
        
        // Contact message actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.flag-btn')) {
                e.preventDefault();
                this.handleFlag(e.target.closest('.flag-btn'));
            } else if (e.target.closest('.reply-btn')) {
                e.preventDefault();
                this.handleReply(e.target.closest('.reply-btn'));
            } else if (e.target.closest('.mark-progress-btn')) {
                e.preventDefault();
                this.handleStatusUpdate(e.target.closest('.mark-progress-btn'), 'mark_progress');
            } else if (e.target.closest('.mark-resolved-btn')) {
                e.preventDefault();
                this.handleStatusUpdate(e.target.closest('.mark-resolved-btn'), 'mark_resolved');
            } else if (e.target.closest('.assign-btn')) {
                e.preventDefault();
                this.handleAssign(e.target.closest('.assign-btn'));
            } else if (e.target.closest('.add-notes-btn')) {
                e.preventDefault();
                this.handleAddNotes(e.target.closest('.add-notes-btn'));
            } else if (e.target.closest('.delete-message-btn')) {
                e.preventDefault();
                this.handleDelete(e.target.closest('.delete-message-btn'));
            }
        });
    }
    
    showArchivePanel() {
        if (this.archivePanel) {
            this.archivePanel.classList.add('visible');
            this.loadArchivedMessages();
        }
    }
    
    hideArchivePanel() {
        if (this.archivePanel) {
            this.archivePanel.classList.remove('visible', 'expanded');
            this.isArchiveExpanded = false;
            if (this.archiveContent) {
                this.archiveContent.style.display = 'none';
            }
        }
    }
    
    toggleArchivePanel() {
        this.isArchiveExpanded = !this.isArchiveExpanded;
        
        if (this.isArchiveExpanded) {
            this.archivePanel.classList.add('expanded');
            this.archiveToggle.querySelector('.archive-chevron').classList.add('fa-chevron-down');
            this.archiveToggle.querySelector('.archive-chevron').classList.remove('fa-chevron-up');
            this.archiveContent.style.display = 'block';
            this.loadArchivedMessages();
        } else {
            this.archivePanel.classList.remove('expanded');
            this.archiveToggle.querySelector('.archive-chevron').classList.add('fa-chevron-up');
            this.archiveToggle.querySelector('.archive-chevron').classList.remove('fa-chevron-down');
            this.archiveContent.style.display = 'none';
        }
    }
    
    async loadArchivedMessages() {
        try {
            const response = await fetch('/inbox/contact/archived/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.renderArchivedMessages(data.messages);
                this.updateArchiveCount(data.pagination.total_count);
            } else {
                console.error('Failed to load archived messages:', data.error);
            }
        } catch (error) {
            console.error('Error loading archived messages:', error);
        }
    }
    
    renderArchivedMessages(messages) {
        if (!messages || messages.length === 0) {
            this.archiveList.innerHTML = '<p class="text-muted">{% trans "No processed messages found." %}</p>';
            return;
        }
        
        const html = messages.map(msg => `
            <div class="contact-archive-item" data-message-id="${msg.id}">
                <div class="item-info">
                    <div class="item-subject">${this.escapeHtml(msg.subject)}</div>
                    <div class="item-meta">
                        <span class="sender">${this.escapeHtml(msg.sender_name)} &lt;${this.escapeHtml(msg.sender_email)}&gt;</span>
                        <span class="status badge contact-status-${msg.status}">${msg.status_display}</span>
                        <span class="date">${msg.updated_at}</span>
                        ${msg.assigned_to ? `<span class="assigned">Assigned to: ${this.escapeHtml(msg.assigned_to)}</span>` : ''}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-sm btn-outline-primary view-archived-btn" data-message-id="${msg.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary restore-btn" data-message-id="${msg.id}">
                        <i class="fas fa-undo"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        this.archiveList.innerHTML = html;
    }
    
    updateArchiveCount(count) {
        if (this.archiveCount) {
            this.archiveCount.textContent = `(${count})`;
        }
    }
    
    async handleFlag(button) {
        const messageId = button.dataset.messageId;
        const currentlyFlagged = button.dataset.flagged === 'true';
        
        try {
            const response = await this.sendAction(messageId, 'flag');
            
            if (response.success) {
                // Update button state
                button.dataset.flagged = response.flagged;
                const icon = button.querySelector('i');
                if (response.flagged) {
                    icon.classList.remove('fa-flag-o');
                    icon.classList.add('fa-flag');
                    button.classList.add('flagged');
                } else {
                    icon.classList.remove('fa-flag');
                    icon.classList.add('fa-flag-o');
                    button.classList.remove('flagged');
                }
                
                this.showNotification('Flag updated successfully', 'success');
            } else {
                this.showNotification('Failed to update flag: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error flagging message:', error);
            this.showNotification('Error updating flag', 'error');
        }
    }
    
    handleReply(button) {
        const email = button.dataset.email;
        const name = button.dataset.name;
        const subject = button.dataset.subject || `Re: Contact Message from ${name}`;
        const messageId = button.dataset.messageId;
        
        // Use inbox manager's navigation if available
        if (window.inboxManager) {
            // Show loading state
            window.inboxManager.showLoading();
            
            // Build the compose URL with prefilled parameters
            const params = new URLSearchParams({
                mode: 'new',
                to: `${name} <${email}>`,
                subject: subject,
                contact_message_id: messageId
            });
            
            const composeUrl = `/inbox/compose/?${params.toString()}`;
            console.log('Contact Reply - Compose URL:', composeUrl);
            console.log('Contact Reply - Parameters:', {
                name: name,
                email: email,
                subject: subject,
                messageId: messageId
            });
            
            // Update URL without page refresh
            window.history.pushState({ 
                folder: window.inboxManager.currentFilters.folder,
                view: 'compose',
                mode: 'new'
            }, 'Compose - Email Inbox', composeUrl);
            
            // Load the compose interface via AJAX
            $.ajax({
                url: composeUrl,
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: (response) => {
                    console.log('Contact Reply - AJAX Response:', response);
                    if (response.success) {
                        // Update the inbox content with compose interface
                        $('#inbox-content').html(response.html);
                        
                        // Update view state
                        window.inboxManager.currentView = 'compose';
                        window.inboxManager.updateToolbarForEmailView();
                        
                        // Initialize the compose manager with a delay to ensure DOM is ready
                        setTimeout(() => {
                            if (typeof ComposeManager !== 'undefined') {
                                window.composeManager = new ComposeManager();
                                window.composeManager.initializeCompose();
                                
                                // Get the original contact message data from the current view
                                const originalMessage = this.getOriginalMessageData();
                                
                                // Manually prefill fields since URL params aren't available in AJAX context
                                window.composeManager.prefillFields({
                                    to: `${name} <${email}>`,
                                    subject: subject,
                                    originalMessage: originalMessage
                                });
                            } else {
                                console.error('ComposeManager not available');
                            }
                        }, 100);
                    } else {
                        console.error('Failed to load compose interface:', response.error);
                        this.showNotification('error', 'Failed to load compose interface');
                    }
                },
                error: (xhr, status, error) => {
                    console.error('AJAX error loading compose:', error);
                    this.showNotification('error', 'Error loading compose interface');
                },
                complete: () => {
                    window.inboxManager.hideLoading();
                }
            });
        } else {
            // Fallback: redirect to compose page with parameters
            const params = new URLSearchParams({
                to: `${name} <${email}>`,
                subject: subject,
                contact_message_id: messageId
            });
            window.location.href = `/inbox/compose/?${params.toString()}`;
        }
    }
    
    getOriginalMessageData() {
        // Extract original message data from the current contact message view
        const messageView = document.querySelector('.contact-message-view');
        if (!messageView) return null;
        
        try {
            const senderName = messageView.querySelector('.sender-name')?.textContent?.trim() || '';
            const senderEmail = messageView.querySelector('.sender-email')?.textContent?.trim() || '';
            const senderDepartment = messageView.querySelector('.sender-department')?.textContent?.trim() || '';
            const messageDate = messageView.querySelector('.date-full')?.textContent?.trim() || '';
            const messageCategory = messageView.querySelector('.category-badge')?.textContent?.trim() || '';
            const messageContent = messageView.querySelector('.message-text')?.textContent?.trim() || '';
            
            return {
                name: senderName,
                email: senderEmail,
                department: senderDepartment,
                date: messageDate,
                category: messageCategory,
                content: messageContent
            };
        } catch (error) {
            console.error('Error extracting original message data:', error);
            return null;
        }
    }
    
    async handleStatusUpdate(button, action) {
        const messageId = button.dataset.messageId;
        
        try {
            const response = await this.sendAction(messageId, action);
            
            if (response.success) {
                this.showNotification('Status updated successfully', 'success');
                // Refresh the current view
                if (window.inboxManager) {
                    window.inboxManager.refreshInbox();
                }
            } else {
                this.showNotification('Failed to update status: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error updating status:', error);
            this.showNotification('Error updating status', 'error');
        }
    }
    
    async handleAssign(button) {
        const messageId = button.dataset.messageId;
        
        try {
            const response = await this.sendAction(messageId, 'assign');
            
            if (response.success) {
                this.showNotification('Message assigned successfully', 'success');
                if (window.inboxManager) {
                    window.inboxManager.refreshInbox();
                }
            } else {
                this.showNotification('Failed to assign message: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error assigning message:', error);
            this.showNotification('Error assigning message', 'error');
        }
    }
    
    async handleAddNotes(button) {
        const messageId = button.dataset.messageId;
        const notes = prompt('Enter internal notes:');
        
        if (notes !== null) {
            try {
                const response = await this.sendAction(messageId, 'add_notes', { notes });
                
                if (response.success) {
                    this.showNotification('Notes added successfully', 'success');
                    if (window.inboxManager) {
                        window.inboxManager.refreshInbox();
                    }
                } else {
                    this.showNotification('Failed to add notes: ' + response.error, 'error');
                }
            } catch (error) {
                console.error('Error adding notes:', error);
                this.showNotification('Error adding notes', 'error');
            }
        }
    }
    
    async handleDelete(button) {
        const messageId = button.dataset.messageId;
        
        if (confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
            try {
                const response = await this.sendAction(messageId, 'delete');
                
                if (response.success) {
                    this.showNotification('Message deleted successfully', 'success');
                    if (window.inboxManager) {
                        window.inboxManager.refreshInbox();
                    }
                } else {
                    this.showNotification('Failed to delete message: ' + response.error, 'error');
                }
            } catch (error) {
                console.error('Error deleting message:', error);
                this.showNotification('Error deleting message', 'error');
            }
        }
    }
    
    async sendAction(messageId, action, extraData = {}) {
        const response = await fetch('/inbox/contact/action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                message_id: messageId,
                action: action,
                ...extraData
            })
        });
        
        return await response.json();
    }
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
               window.inboxData?.csrf || '';
    }
    
    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.inboxManager && window.inboxManager.showNotification) {
            window.inboxManager.showNotification(message, type);
        } else {
            // Fallback notification
            console.log(`${type.toUpperCase()}: ${message}`);
            alert(message);
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.contactMessages = new ContactMessages();
}); 