class ComposeManager {
    constructor() {
        this.editor = null;
        this.attachments = [];
        this.isDraftSaved = false;
        this.draftSaveInterval = null;
        
        console.log('ComposeManager initialized');
    }
    
    initializeCompose() {
        console.log('Initializing compose interface');
        
        // Initialize editor
        this.initializeEditor();
        
        // Handle URL parameters for prefilling
        this.handleUrlParameters();
        
        // Bind events
        this.bindEvents();
        
        // Initialize auto-save
        this.startAutoSave();
        
        // Focus on To field or editor
        this.focusInitialField();
    }
    
    handleUrlParameters() {
        // Parse URL parameters to prefill form fields (override template values)
        const urlParams = new URLSearchParams(window.location.search);
        console.log('Current URL params:', urlParams.toString());
        
        // Prefill 'to' field (URL params override template values)
        const toParam = urlParams.get('to');
        if (toParam) {
            const toField = document.getElementById('compose-to');
            if (toField) {
                toField.value = decodeURIComponent(toParam);
                console.log('Prefilled To field with:', decodeURIComponent(toParam));
            } else {
                console.log('To field not found!');
            }
        }
        
        // Prefill 'subject' field (URL params override template values)
        const subjectParam = urlParams.get('subject');
        if (subjectParam) {
            const subjectField = document.getElementById('compose-subject');
            if (subjectField) {
                subjectField.value = decodeURIComponent(subjectParam);
                console.log('Prefilled Subject field with:', decodeURIComponent(subjectParam));
            } else {
                console.log('Subject field not found!');
            }
        }
        
        // Prefill 'cc' field if present
        const ccParam = urlParams.get('cc');
        if (ccParam) {
            const ccField = document.getElementById('compose-cc');
            if (ccField) {
                ccField.value = ccParam;
                // Show CC field if it's hidden
                const ccFieldContainer = ccField.closest('.cc-field');
                if (ccFieldContainer) {
                    ccFieldContainer.style.display = 'block';
                }
            }
        }
        
        // Prefill 'bcc' field if present
        const bccParam = urlParams.get('bcc');
        if (bccParam) {
            const bccField = document.getElementById('compose-bcc');
            if (bccField) {
                bccField.value = bccParam;
                // Show BCC field if it's hidden
                const bccFieldContainer = bccField.closest('.bcc-field');
                if (bccFieldContainer) {
                    bccFieldContainer.style.display = 'block';
                }
            }
        }
    }
    
    prefillFields(data) {
        console.log('Prefilling fields with data:', data);
        
        // Prefill 'to' field
        if (data.to) {
            const toField = document.getElementById('compose-to');
            if (toField) {
                toField.value = data.to;
                console.log('Prefilled To field with:', data.to);
            } else {
                console.log('To field not found!');
            }
        }
        
        // Prefill 'subject' field
        if (data.subject) {
            const subjectField = document.getElementById('compose-subject');
            if (subjectField) {
                subjectField.value = data.subject;
                console.log('Prefilled Subject field with:', data.subject);
            } else {
                console.log('Subject field not found!');
            }
        }
        
        // Prefill 'cc' field if present
        if (data.cc) {
            const ccField = document.getElementById('compose-cc');
            if (ccField) {
                ccField.value = data.cc;
                // Show CC field if it's hidden
                const ccFieldContainer = ccField.closest('.cc-field');
                if (ccFieldContainer) {
                    ccFieldContainer.style.display = 'block';
                }
            }
        }
        
        // Prefill 'bcc' field if present
        if (data.bcc) {
            const bccField = document.getElementById('compose-bcc');
            if (bccField) {
                bccField.value = data.bcc;
                // Show BCC field if it's hidden
                const bccFieldContainer = bccField.closest('.bcc-field');
                if (bccFieldContainer) {
                    bccFieldContainer.style.display = 'block';
                }
            }
        }
        
        // Add original message to compose body
        if (data.originalMessage && this.editor) {
            this.insertOriginalMessage(data.originalMessage);
        }
    }
    
    insertOriginalMessage(originalMessage) {
        console.log('Inserting original message:', originalMessage);
        
        // Create the original message HTML
        let originalMessageHtml = '<br><br><div class="original-message">';
        originalMessageHtml += '<div class="original-message-header">';
        originalMessageHtml += '-----Original Contact Message-----<br>';
        originalMessageHtml += `<strong>From:</strong> ${this.escapeHtml(originalMessage.name)}`;
        if (originalMessage.email) {
            originalMessageHtml += ` &lt;${this.escapeHtml(originalMessage.email)}&gt;`;
        }
        originalMessageHtml += '<br>';
        if (originalMessage.date) {
            originalMessageHtml += `<strong>Date:</strong> ${this.escapeHtml(originalMessage.date)}<br>`;
        }
        if (originalMessage.category) {
            originalMessageHtml += `<strong>Subject:</strong> [${this.escapeHtml(originalMessage.category)}] ${this.escapeHtml(originalMessage.name)}<br>`;
        }
        if (originalMessage.department) {
            originalMessageHtml += `<strong>Department:</strong> ${this.escapeHtml(originalMessage.department)}<br>`;
        }
        originalMessageHtml += '</div>';
        originalMessageHtml += '<div class="original-message-body">';
        if (originalMessage.content) {
            // Convert line breaks to <br> tags
            const escapedContent = this.escapeHtml(originalMessage.content);
            originalMessageHtml += escapedContent.replace(/\n/g, '<br>');
        }
        originalMessageHtml += '</div>';
        originalMessageHtml += '</div>';
        
        // Insert the original message into the editor
        this.editor.innerHTML = originalMessageHtml;
        
        // Position cursor at the beginning for the reply
        this.editor.focus();
        const range = document.createRange();
        const selection = window.getSelection();
        range.setStart(this.editor, 0);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
        
        console.log('Original message inserted into compose body');
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    initializeEditor() {
        this.editor = document.getElementById('compose-editor');
        if (!this.editor) return;
        
        // Set up contenteditable functionality
        this.editor.addEventListener('focus', () => {
            // Remove placeholder when focused
            if (this.editor.textContent.trim() === '') {
                this.editor.innerHTML = '';
            }
        });
        
        this.editor.addEventListener('blur', () => {
            // Show placeholder if empty
            if (this.editor.textContent.trim() === '') {
                this.editor.innerHTML = '';
            }
        });
        
        this.editor.addEventListener('input', () => {
            this.handleEditorInput();
        });
        
        // Handle paste events
        this.editor.addEventListener('paste', (e) => {
            this.handlePaste(e);
        });
        
        console.log('Rich text editor initialized');
    }
    
    bindEvents() {
        // Toolbar buttons
        $(document).on('click', '.toolbar-btn', (e) => {
            e.preventDefault();
            const command = $(e.currentTarget).data('command');
            this.executeCommand(command);
        });
        
        // Font size change
        $(document).on('change', '#font-size', (e) => {
            this.executeCommand('fontSize', $(e.target).val());
        });
        
        // Text color change
        $(document).on('change', '#text-color', (e) => {
            this.executeCommand('foreColor', $(e.target).val());
        });
        
        // Recipients toggles
        $(document).on('click', '#toggle-cc', () => {
            $('.cc-field').toggle();
        });
        
        $(document).on('click', '#toggle-bcc', () => {
            $('.bcc-field').toggle();
        });
        
        // File attachments
        $(document).on('change', '#compose-attachments', (e) => {
            this.handleAttachments(e.target.files);
        });
        
        // Form submission
        $(document).on('submit', '#compose-email-form', (e) => {
            e.preventDefault();
            this.sendEmail();
        });
        
        // Compose actions
        $(document).on('click', '.compose-action-btn.close', () => {
            this.closeCompose();
        });
        
        // Back button
        $(document).on('click', '.back-arrow-btn', () => {
            this.navigateBackToInbox();
        });
        
        console.log('Compose events bound');
    }
    
    executeCommand(command, value = null) {
        // Save current selection
        this.saveSelection();
        
        // Focus editor
        this.editor.focus();
        
        // Restore selection
        this.restoreSelection();
        
        // Execute the command
        try {
            if (value !== null) {
                document.execCommand(command, false, value);
            } else {
                document.execCommand(command, false, null);
            }
            
            // Update button states
            this.updateToolbarStates();
            
        } catch (error) {
            console.error('Error executing command:', command, error);
        }
    }
    
    saveSelection() {
        if (window.getSelection) {
            const sel = window.getSelection();
            if (sel.getRangeAt && sel.rangeCount) {
                this.savedRange = sel.getRangeAt(0);
            }
        }
    }
    
    restoreSelection() {
        if (this.savedRange) {
            if (window.getSelection) {
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(this.savedRange);
            }
        }
    }
    
    updateToolbarStates() {
        // Update button active states based on current selection
        const commands = ['bold', 'italic', 'underline'];
        
        commands.forEach(command => {
            const isActive = document.queryCommandState(command);
            const button = $(`.toolbar-btn[data-command="${command}"]`);
            
            if (isActive) {
                button.addClass('active');
            } else {
                button.removeClass('active');
            }
        });
    }
    
    handleEditorInput() {
        // Mark as draft modified
        this.isDraftSaved = false;
        
        // Update toolbar states
        this.updateToolbarStates();
        
        // Auto-save will handle saving
    }
    
    handlePaste(e) {
        e.preventDefault();
        
        // Get pasted data
        const clipboardData = e.clipboardData || window.clipboardData;
        let pastedData = clipboardData.getData('text/html') || clipboardData.getData('text/plain');
        
        // Clean the pasted data (remove scripts, etc.)
        pastedData = this.cleanPastedContent(pastedData);
        
        // Insert at current position
        this.insertHtmlAtCursor(pastedData);
    }
    
    cleanPastedContent(html) {
        // Create a temporary div to clean content
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove dangerous elements
        const dangerousElements = temp.querySelectorAll('script, object, embed, link, meta, style');
        dangerousElements.forEach(el => el.remove());
        
        // Remove dangerous attributes
        const allElements = temp.querySelectorAll('*');
        allElements.forEach(el => {
            const allowedAttrs = ['href', 'src', 'alt', 'title'];
            Array.from(el.attributes).forEach(attr => {
                if (!allowedAttrs.includes(attr.name.toLowerCase()) && 
                    !attr.name.startsWith('data-')) {
                    el.removeAttribute(attr.name);
                }
            });
        });
        
        return temp.innerHTML;
    }
    
    insertHtmlAtCursor(html) {
        if (window.getSelection) {
            const sel = window.getSelection();
            if (sel.getRangeAt && sel.rangeCount) {
                const range = sel.getRangeAt(0);
                range.deleteContents();
                
                const div = document.createElement('div');
                div.innerHTML = html;
                const frag = document.createDocumentFragment();
                let node;
                while ((node = div.firstChild)) {
                    frag.appendChild(node);
                }
                range.insertNode(frag);
            }
        }
    }
    
    handleAttachments(files) {
        Array.from(files).forEach(file => {
            // Check file size (limit to 25MB)
            if (file.size > 25 * 1024 * 1024) {
                this.showError(`File "${file.name}" is too large. Maximum size is 25MB.`);
                return;
            }
            
            this.attachments.push(file);
            this.displayAttachment(file);
        });
        
        // Show attachment list if we have attachments
        if (this.attachments.length > 0) {
            $('#attachment-list').show();
        }
    }
    
    displayAttachment(file) {
        const attachmentHtml = `
            <div class="attachment-item" data-filename="${file.name}">
                <div class="attachment-info">
                    <i class="fas fa-paperclip"></i>
                    <span class="attachment-name">${file.name}</span>
                    <span class="attachment-size">(${this.formatFileSize(file.size)})</span>
                </div>
                <button type="button" class="attachment-remove" onclick="composeManager.removeAttachment('${file.name}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        $('#attachment-list').append(attachmentHtml);
    }
    
    removeAttachment(filename) {
        // Remove from attachments array
        this.attachments = this.attachments.filter(file => file.name !== filename);
        
        // Remove from UI
        $(`.attachment-item[data-filename="${filename}"]`).remove();
        
        // Hide attachment list if empty
        if (this.attachments.length === 0) {
            $('#attachment-list').hide();
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    sendEmail() {
        console.log('=== Attempting to send email ===');
        
        // Validate form
        if (!this.validateForm()) {
            console.log('Form validation failed');
            return;
        }
        
        console.log('Form validation passed');
        
        // Show sending status
        this.showSendingStatus();
        
        // Prepare form data
        const formData = this.prepareFormData();
        console.log('Form data prepared:', formData);
        
        const sendUrl = window.inboxData?.urls?.send || '/inbox/send/';
        const csrfToken = window.inboxData?.csrf || $('[name=csrfmiddlewaretoken]').val();
        
        console.log('Send URL:', sendUrl);
        console.log('CSRF Token:', csrfToken);
        
        // Send email via AJAX
        $.ajax({
            url: sendUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: (response) => {
                console.log('Send email response:', response);
                
                if (response.success) {
                    console.log('Email sent successfully!');
                    this.showSuccess('Email sent successfully!');
                    // Navigate back to inbox after a brief delay
                    setTimeout(() => {
                        this.navigateBackToInbox();
                    }, 2000);
                } else {
                    console.error('Send email failed:', response.error);
                    this.showError(response.error || 'Failed to send email');
                }
            },
            error: (xhr, status, error) => {
                console.error('Send email AJAX error:', { xhr, status, error, response: xhr.responseText });
                this.showError('Failed to send email. Please try again.');
            },
            complete: () => {
                this.hideSendingStatus();
            }
        });
    }
    
    validateForm() {
        const to = $('#compose-to').val().trim();
        const subject = $('#compose-subject').val().trim();
        const body = this.editor.textContent.trim();
        
        console.log('Validating form:', { to, subject, body: body.substring(0, 50) + '...' });
        
        if (!to) {
            console.log('Validation failed: No recipients');
            this.showError('Please enter at least one recipient');
            $('#compose-to').focus();
            return false;
        }
        
        if (!subject) {
            console.log('Validation failed: No subject');
            this.showError('Please enter a subject');
            $('#compose-subject').focus();
            return false;
        }
        
        if (!body) {
            console.log('Validation failed: No message body');
            this.showError('Please enter a message');
            this.editor.focus();
            return false;
        }
        
        console.log('Form validation successful');
        return true;
    }
    
    prepareFormData() {
        const formData = new FormData();
        
        // Add text fields
        formData.append('to', $('#compose-to').val());
        formData.append('cc', $('#compose-cc').val() || '');
        formData.append('bcc', $('#compose-bcc').val() || '');
        formData.append('subject', $('#compose-subject').val());
        formData.append('body', this.editor.innerHTML);
        formData.append('body_text', this.editor.textContent);
        
        // Add attachments
        this.attachments.forEach((file, index) => {
            formData.append(`attachment_${index}`, file);
        });
        
        return formData;
    }
    
    startAutoSave() {
        // Auto-save every 30 seconds
        this.draftSaveInterval = setInterval(() => {
            if (!this.isDraftSaved) {
                this.saveDraft();
            }
        }, 30000);
    }
    
    saveDraft() {
        // Implement draft saving logic
        const draftData = {
            to: $('#compose-to').val(),
            cc: $('#compose-cc').val(),
            bcc: $('#compose-bcc').val(),
            subject: $('#compose-subject').val(),
            body: this.editor.innerHTML,
            body_text: this.editor.textContent
        };
        
        // Save to localStorage for now (could be enhanced to save to server)
        localStorage.setItem('email_draft', JSON.stringify(draftData));
        this.isDraftSaved = true;
        
        console.log('Draft saved');
    }
    
    focusInitialField() {
        // Focus on To field if empty, otherwise focus on editor
        const toField = $('#compose-to');
        if (!toField.val()) {
            toField.focus();
        } else {
            this.editor.focus();
        }
    }
    
    closeCompose() {
        // Check if there are unsaved changes
        if (!this.isDraftSaved && this.hasContent()) {
            if (confirm('You have unsaved changes. Do you want to save as draft before closing?')) {
                this.saveDraft();
            }
        }
        
        this.navigateBackToInbox();
    }
    
    hasContent() {
        const to = $('#compose-to').val().trim();
        const subject = $('#compose-subject').val().trim();
        const body = this.editor.textContent.trim();
        
        return to || subject || body;
    }
    
    navigateBackToInbox() {
        // Clean up
        if (this.draftSaveInterval) {
            clearInterval(this.draftSaveInterval);
        }
        
        // Navigate back using inbox manager
        if (window.inboxManager) {
            window.inboxManager.navigateBackToInbox();
        }
    }
    
    showSendingStatus() {
        $('#send-status').show();
        $('#send-email').prop('disabled', true);
    }
    
    hideSendingStatus() {
        $('#send-status').hide();
        $('#send-email').prop('disabled', false);
    }
    
    showSuccess(message) {
        // Use inbox manager's notification system if available
        if (window.inboxManager) {
            window.inboxManager.showSuccess(message);
        } else {
            alert(message);
        }
    }
    
    showError(message) {
        // Use inbox manager's notification system if available
        if (window.inboxManager) {
            window.inboxManager.showError(message);
        } else {
            alert(message);
        }
    }
}

// Global functions for template usage
function toggleSendOptions() {
    $('#send-options-menu').toggle();
}

function scheduleSend() {
    alert('Schedule send functionality will be implemented in a future update');
    $('#send-options-menu').hide();
}

function saveDraft() {
    if (window.composeManager) {
        window.composeManager.saveDraft();
    }
}

function discardDraft() {
    if (confirm('Are you sure you want to discard this email?')) {
        if (window.composeManager) {
            window.composeManager.navigateBackToInbox();
        }
    }
}

// Initialize on document ready
$(document).ready(function() {
    // ComposeManager will be initialized by InboxManager when needed
    console.log('Compose.js loaded');
}); 