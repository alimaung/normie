/**
 * Right Sidebar Manager - Gmail-style sidebar with persistent icons and expandable content
 * Default: collapsed, positioned below navbar, toggle behavior for icons
 */

class RightSidebarManager {
    constructor() {
        this.isContentExpanded = localStorage.getItem('rightSidebarContentExpanded') === 'true'; // Default to collapsed
        this.activeTab = localStorage.getItem('rightSidebarActiveTab') || 'calendar';
        this.currentDate = new Date();
        
        this.init();
    }
    
    init() {
        this.setupSidebar();
        this.bindEvents();
        
        // Only load content if expanded
        if (this.isContentExpanded) {
            this.switchTab(this.activeTab);
        }
        
        this.generateCalendar();
        this.loadNotes();
        this.loadTasks();
        this.loadRecentContacts();
        
        console.log('RightSidebarManager initialized');
    }
    
    setupSidebar() {
        const content = document.getElementById('right-sidebar-content');
        const inboxMain = document.querySelector('.inbox-main');
        
        if (this.isContentExpanded) {
            content?.classList.remove('collapsed');
            content?.classList.add('expanded');
            inboxMain?.classList.remove('sidebar-collapsed');
            inboxMain?.classList.add('sidebar-expanded');
        } else {
            content?.classList.remove('expanded');
            content?.classList.add('collapsed');
            inboxMain?.classList.remove('sidebar-expanded');
            inboxMain?.classList.add('sidebar-collapsed');
        }
    }
    
    bindEvents() {
        // Tab switching - now using icon buttons with toggle behavior
        document.querySelectorAll('.sidebar-icon').forEach(icon => {
            icon.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.toggleTab(tabName);
            });
        });
        
        // Search contacts in sidebar
        const contactSearch = document.getElementById('sidebar-contact-search');
        if (contactSearch) {
            let searchTimeout;
            contactSearch.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchContacts(e.target.value);
                }, 300);
            });
        }
        
        // Quick note and task inputs
        const quickNoteInput = document.getElementById('quick-note-input');
        if (quickNoteInput) {
            quickNoteInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.saveQuickNote();
                }
            });
        }
        
        const quickTaskInput = document.getElementById('quick-task-input');
        if (quickTaskInput) {
            quickTaskInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.saveQuickTask();
                }
            });
        }
    }
    
    toggleTab(tabName) {
        // If the content is expanded and the same tab is clicked, collapse it
        if (this.isContentExpanded && this.activeTab === tabName) {
            this.collapseContent();
            return;
        }
        
        // Otherwise, switch to the tab and expand if needed
        this.switchTab(tabName);
        
        if (!this.isContentExpanded) {
            this.expandContent();
        }
    }
    
    switchTab(tabName) {
        this.activeTab = tabName;
        localStorage.setItem('rightSidebarActiveTab', tabName);
        
        // Update icon buttons
        document.querySelectorAll('.sidebar-icon').forEach(icon => {
            if (icon.dataset.tab === tabName) {
                icon.classList.add('active');
            } else {
                icon.classList.remove('active');
            }
        });
        
        // Update panels
        document.querySelectorAll('.sidebar-panel').forEach(panel => {
            if (panel.id === `${tabName}-panel`) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
        
        // Load tab-specific content
        switch (tabName) {
            case 'calendar':
                this.refreshCalendar();
                break;
            case 'contacts':
                this.loadRecentContacts();
                break;
        }
    }
    
    expandContent() {
        const content = document.getElementById('right-sidebar-content');
        const inboxMain = document.querySelector('.inbox-main');
        
        this.isContentExpanded = true;
        localStorage.setItem('rightSidebarContentExpanded', true);
        
        content?.classList.remove('collapsed');
        content?.classList.add('expanded');
        inboxMain?.classList.remove('sidebar-collapsed');
        inboxMain?.classList.add('sidebar-expanded');
        
        console.log('Content panel expanded');
    }
    
    collapseContent() {
        const content = document.getElementById('right-sidebar-content');
        const inboxMain = document.querySelector('.inbox-main');
        
        this.isContentExpanded = false;
        localStorage.setItem('rightSidebarContentExpanded', false);
        
        content?.classList.remove('expanded');
        content?.classList.add('collapsed');
        inboxMain?.classList.remove('sidebar-expanded');
        inboxMain?.classList.add('sidebar-collapsed');
        
        // Clear active state from all icons
        document.querySelectorAll('.sidebar-icon').forEach(icon => {
            icon.classList.remove('active');
        });
        
        console.log('Content panel collapsed');
    }
    
    // Calendar Functions
    generateCalendar() {
        const grid = document.getElementById('calendar-grid');
        if (!grid) return;
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Update title
        const title = document.getElementById('calendar-title');
        if (title) {
            title.textContent = new Date(year, month).toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
            });
        }
        
        // Clear grid
        grid.innerHTML = '';
        
        // Add day headers
        const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
        days.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            grid.appendChild(dayHeader);
        });
        
        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day empty';
            grid.appendChild(emptyDay);
        }
        
        // Add days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            // Highlight today
            if (year === today.getFullYear() && 
                month === today.getMonth() && 
                day === today.getDate()) {
                dayElement.classList.add('today');
            }
            
            grid.appendChild(dayElement);
        }
    }
    
    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.generateCalendar();
    }
    
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.generateCalendar();
    }
    
    refreshCalendar() {
        this.generateCalendar();
        this.loadUpcomingEvents();
    }
    
    loadUpcomingEvents() {
        const eventsList = document.getElementById('events-list');
        if (!eventsList) return;
        
        // For now, show placeholder events
        eventsList.innerHTML = `
            <div class="event-item">
                <div class="event-time">9:00 AM</div>
                <div class="event-title">Team Meeting</div>
            </div>
            <div class="event-item">
                <div class="event-time">2:00 PM</div>
                <div class="event-title">Project Review</div>
            </div>
        `;
    }
    
    // Notes Functions
    loadNotes() {
        const notesList = document.getElementById('notes-list');
        if (!notesList) return;
        
        const notes = this.getStoredNotes();
        
        if (notes.length === 0) {
            notesList.innerHTML = '<div class="no-notes">No notes yet</div>';
            return;
        }
        
        notesList.innerHTML = notes.map(note => `
            <div class="note-item" data-id="${note.id}">
                <div class="note-content">${this.escapeHtml(note.content)}</div>
                <div class="note-meta">
                    <span class="note-date">${new Date(note.created).toLocaleDateString()}</span>
                    <button class="note-delete" onclick="rightSidebar.deleteNote('${note.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    saveQuickNote() {
        const input = document.getElementById('quick-note-input');
        if (!input) return;
        
        const content = input.value.trim();
        if (!content) return;
        
        const notes = this.getStoredNotes();
        const newNote = {
            id: Date.now().toString(),
            content: content,
            created: new Date().toISOString()
        };
        
        notes.unshift(newNote);
        localStorage.setItem('inbox_notes', JSON.stringify(notes));
        
        input.value = '';
        this.loadNotes();
    }
    
    deleteNote(noteId) {
        const notes = this.getStoredNotes().filter(note => note.id !== noteId);
        localStorage.setItem('inbox_notes', JSON.stringify(notes));
        this.loadNotes();
    }
    
    getStoredNotes() {
        try {
            return JSON.parse(localStorage.getItem('inbox_notes') || '[]');
        } catch {
            return [];
        }
    }
    
    // Tasks Functions
    loadTasks() {
        const tasksList = document.getElementById('tasks-list');
        if (!tasksList) return;
        
        const tasks = this.getStoredTasks();
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<div class="no-tasks">No tasks yet</div>';
            return;
        }
        
        tasksList.innerHTML = tasks.map(task => `
            <div class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
                <input type="checkbox" ${task.completed ? 'checked' : ''} 
                       onchange="rightSidebar.toggleTask('${task.id}')">
                <span class="task-content">${this.escapeHtml(task.content)}</span>
                <button class="task-delete" onclick="rightSidebar.deleteTask('${task.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }
    
    saveQuickTask() {
        const input = document.getElementById('quick-task-input');
        if (!input) return;
        
        const content = input.value.trim();
        if (!content) return;
        
        const tasks = this.getStoredTasks();
        const newTask = {
            id: Date.now().toString(),
            content: content,
            completed: false,
            created: new Date().toISOString()
        };
        
        tasks.unshift(newTask);
        localStorage.setItem('inbox_tasks', JSON.stringify(tasks));
        
        input.value = '';
        this.loadTasks();
    }
    
    toggleTask(taskId) {
        const tasks = this.getStoredTasks();
        const task = tasks.find(t => t.id === taskId);
        if (task) {
            task.completed = !task.completed;
            localStorage.setItem('inbox_tasks', JSON.stringify(tasks));
            this.loadTasks();
        }
    }
    
    deleteTask(taskId) {
        const tasks = this.getStoredTasks().filter(task => task.id !== taskId);
        localStorage.setItem('inbox_tasks', JSON.stringify(tasks));
        this.loadTasks();
    }
    
    getStoredTasks() {
        try {
            return JSON.parse(localStorage.getItem('inbox_tasks') || '[]');
        } catch {
            return [];
        }
    }
    
    // Contacts Functions
    async loadRecentContacts() {
        const contactsList = document.getElementById('sidebar-contacts-list');
        if (!contactsList) return;
        
        contactsList.innerHTML = '<div class="loading">Loading contacts...</div>';
        
        try {
            // Load recent contacts (could be from localStorage or API)
            const recentContacts = this.getRecentContacts();
            
            if (recentContacts.length === 0) {
                contactsList.innerHTML = '<div class="no-contacts">No recent contacts</div>';
                return;
            }
            
            contactsList.innerHTML = recentContacts.map(contact => `
                <div class="sidebar-contact-item" data-email="${contact.email}">
                    <div class="contact-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="contact-info">
                        <div class="contact-name">${this.escapeHtml(contact.name)}</div>
                        <div class="contact-email">${this.escapeHtml(contact.email)}</div>
                    </div>
                    <div class="contact-actions">
                        <button onclick="rightSidebar.composeToContact('${contact.email}')" title="Compose email">
                            <i class="fas fa-envelope"></i>
                        </button>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error loading contacts:', error);
            contactsList.innerHTML = '<div class="error">Failed to load contacts</div>';
        }
    }
    
    async searchContacts(query) {
        if (query.length < 2) {
            this.loadRecentContacts();
            return;
        }
        
        const contactsList = document.getElementById('sidebar-contacts-list');
        if (!contactsList) return;
        
        contactsList.innerHTML = '<div class="loading">Searching...</div>';
        
        try {
            const response = await fetch(`/inbox/contacts/autocomplete/?q=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();
            
            if (data.success && data.results) {
                contactsList.innerHTML = data.results.map(contact => `
                    <div class="sidebar-contact-item" data-email="${contact.email}">
                        <div class="contact-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="contact-info">
                            <div class="contact-name">${this.escapeHtml(contact.display_name || contact.name)}</div>
                            <div class="contact-email">${this.escapeHtml(contact.email)}</div>
                        </div>
                        <div class="contact-actions">
                            <button onclick="rightSidebar.composeToContact('${contact.email}')" title="Compose email">
                                <i class="fas fa-envelope"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            } else {
                contactsList.innerHTML = '<div class="no-results">No contacts found</div>';
            }
        } catch (error) {
            console.error('Contact search error:', error);
            contactsList.innerHTML = '<div class="error">Search failed</div>';
        }
    }
    
    composeToContact(email) {
        // Navigate to compose with pre-filled recipient
        window.inboxManager?.navigateToCompose('new', null, email);
    }
    
    getRecentContacts() {
        try {
            return JSON.parse(localStorage.getItem('recent_contacts') || '[]');
        } catch {
            return [];
        }
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for inline event handlers
window.closeSidebarPanel = function() {
    window.rightSidebar?.collapseContent();
};

window.previousMonth = function() {
    window.rightSidebar?.previousMonth();
};

window.nextMonth = function() {
    window.rightSidebar?.nextMonth();
};

window.refreshCalendar = function() {
    window.rightSidebar?.refreshCalendar();
};

window.saveQuickNote = function() {
    window.rightSidebar?.saveQuickNote();
};

window.saveQuickTask = function() {
    window.rightSidebar?.saveQuickTask();
};

window.refreshContacts = function() {
    window.rightSidebar?.loadRecentContacts();
};

window.searchSidebarContacts = function() {
    const input = document.getElementById('sidebar-contact-search');
    window.rightSidebar?.searchContacts(input?.value || '');
};

window.openContactsPage = function() {
    window.location.href = '/contacts/';
};

// Auto-initialize
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('right-sidebar')) {
        window.rightSidebar = new RightSidebarManager();
    }
});

// Export for manual initialization
window.RightSidebarManager = RightSidebarManager; 
window.RightSidebarManager = RightSidebarManager; 