// TKZ Directory Management System
class TKZManager {
    constructor() {
        this.data = [];
        this.filteredData = []; 
        this.searchResults = []; 
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.sortColumn = 'Teilenummer';
        this.sortDirection = 'desc';
        this.activeFilters = {};
        this.searchTerms = [];
        this.currentSearchQuery = '';
        this.currentView = 'table';
        this.attachmentsVisible = false;
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            this.setupEventListeners();
            this.sortData();
            this.searchResults = [...this.filteredData];
            
            // Initialize attachment columns as hidden
            const tableContainer = document.querySelector('.table-container');
            const gridContainer = document.querySelector('.grid-container');
            if (tableContainer) {
                tableContainer.classList.add('hide-attachments');
            }
            if (gridContainer) {
                gridContainer.classList.add('hide-attachments');
            }
            
            this.renderView();
            this.updatePagination();
            this.updateStats();
            this.updateSortIcons();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize TKZ:', error);
            this.hideLoading();
            this.showError('Failed to load TKZ data');
        }
    }
    
    async loadData() {
        try {
            const response = await fetch('/static/normieapp/data/TKZ.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const jsonData = await response.json();
            this.data = jsonData.data || [];
            
            // Apply default sort immediately after loading (Part Number descending - newest/highest first)
            this.sortColumn = 'Teilenummer';
            this.sortDirection = 'desc';
            this.data.sort((a, b) => {
                let aVal = a[this.sortColumn] || '';
                let bVal = b[this.sortColumn] || '';
                
                // Handle null/undefined values
                if (aVal == null) aVal = '';
                if (bVal == null) bVal = '';
                
                // Try numeric sort for part numbers (descending - highest first)
                const aNum = parseInt(aVal);
                const bNum = parseInt(bVal);
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return bNum - aNum; // Descending order for default sort
                }
                
                // Fall back to string sort (descending)
                return String(bVal).localeCompare(String(aVal));
            });
            
            this.filteredData = [...this.data];
            this.searchResults = [...this.filteredData];
            console.log(`Loaded ${this.data.length} TKZ records (sorted by Part Number descending)`);
        } catch (error) {
            console.error('Error loading TKZ data:', error);
            throw error;
        }
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('tkz-search');
        if (searchInput) {
            // Handle real-time search as user types
            searchInput.addEventListener('input', (e) => {
                this.currentSearchQuery = e.target.value.trim();
                this.handleSearch();
            });
            
            // Handle Enter key to add search terms
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const term = e.target.value.trim();
                    if (term && !this.searchTerms.includes(term)) {
                        this.addSearchTerm(term);
                        e.target.value = '';
                    }
                }
            });
        }
        
        // Attachment toggle functionality
        const attachmentBtn = document.getElementById('toggle-attachments');
        if (attachmentBtn) {
            attachmentBtn.addEventListener('click', () => {
                this.toggleAttachments();
            });
        }

        // View toggle functionality
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach((btn, index) => {
            btn.addEventListener('click', () => {
                viewBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentView = index === 0 ? 'table' : 'grid';
                this.renderView();
            });
        });
        
        // Filter functionality
        this.setupFilterListeners();
        
        // Pagination
        this.setupPaginationListeners();
        
        // Table sorting
        this.setupTableSorting();
        
        // Update filter count on form changes
        document.querySelectorAll('#filter-section input[type="checkbox"], #filter-section input[type="radio"], #filter-section input[type="text"], #filter-section input[type="date"]')
            .forEach(input => {
                input.addEventListener('change', () => {
                    this.updateFilterCount();
                });
            });
        
        document.querySelectorAll('#filter-section input[type="text"]')
            .forEach(input => {
                input.addEventListener('input', () => {
                    this.updateFilterCount();
                });
            });
        
        // Initial filter count
        this.updateFilterCount();
    }
    
    setupFilterListeners() {
        // Filter section toggle
        const filterBtn = document.getElementById('toggle-filter-panel');
        const filterSection = document.getElementById('filter-section');
        const closeFilterBtn = document.getElementById('close-filter-section');
        
        if (filterBtn && filterSection) {
            filterBtn.addEventListener('click', () => {
                if (filterSection.style.display === 'none' || !filterSection.style.display) {
                    filterSection.style.display = 'block';
                    filterBtn.classList.add('active');
                } else {
                    filterSection.style.display = 'none';
                    filterBtn.classList.remove('active');
                }
            });
        }
        
        if (closeFilterBtn && filterSection) {
            closeFilterBtn.addEventListener('click', () => {
                filterSection.style.display = 'none';
                if (filterBtn) filterBtn.classList.remove('active');
            });
        }
        
        // Filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                document.querySelectorAll('.filter-tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.querySelector(`.filter-tab-content[data-tab="${tabId}"]`).classList.add('active');
            });
        });
        
        // Apply/Reset filters
        const applyFilterBtn = document.querySelector('.filter-apply-btn');
        const resetFilterBtn = document.querySelector('.filter-reset-btn');
        const clearAllFiltersBtn = document.querySelector('.clear-filters-btn');
        
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', () => {
                this.applyFilters();
                if (filterSection) filterSection.style.display = 'none';
                if (filterBtn) filterBtn.classList.remove('active');
            });
        }
        
        if (resetFilterBtn) {
            resetFilterBtn.addEventListener('click', () => this.resetFilters());
        }
        
        if (clearAllFiltersBtn) {
            clearAllFiltersBtn.addEventListener('click', () => this.clearAllFilters());
        }
    }
    
    setupTableSorting() {
        document.querySelectorAll('.tkz-table th.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const column = this.getColumnFromHeader(header);
                this.handleSort(column);
            });
        });
    }
    
    getColumnFromHeader(header) {
        const headerText = header.textContent.trim().replace(/\s*\u{f0dc}|\s*\u{f0de}|\s*\u{f0dd}/gu, '');
        const columnMap = {
            'Part Number': 'Teilenummer',
            'TO Number': 'TO-Nummer',
            'Status': 'status',
            'Category': 'Benennung / Kategorie',
            'Title/Description': 'Normkurzbezeichnung / Titel',
            'Project': 'Projekt ',
            'Responsible Person': 'Name',
            'Department': 'Abteilung',
            'Date': 'Datum'
        };
        return columnMap[headerText] || headerText;
    }
    
    handleSort(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        
        this.sortData();
        this.renderView();
        this.updateSortIcons();
    }
    
    sortData() {
        this.searchResults.sort((a, b) => {
            let aVal = a[this.sortColumn] || '';
            let bVal = b[this.sortColumn] || '';
            
            // Special handling for part numbers
            if (this.sortColumn === 'Teilenummer') {
                const aNum = parseInt(aVal);
                const bNum = parseInt(bVal);
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return this.sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
                }
            }
            
            // Handle dates
            if (this.sortColumn === 'Datum') {
                aVal = new Date(aVal || '1900-01-01');
                bVal = new Date(bVal || '1900-01-01');
            } else {
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
            }
            
            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }
    
    updateSortIcons() {
        document.querySelectorAll('.tkz-table th.sortable i').forEach(icon => {
            icon.className = 'fas fa-sort';
        });
        
        const currentHeader = Array.from(document.querySelectorAll('.tkz-table th.sortable'))
            .find(header => this.getColumnFromHeader(header) === this.sortColumn);
        
        if (currentHeader) {
            const icon = currentHeader.querySelector('i');
            if (icon) {
                icon.className = this.sortDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
            }
        }
    }
    
    handleSearch() {
        // Get search terms (including current input and badges)
        const allSearchTerms = [...this.searchTerms];
        if (this.currentSearchQuery) {
            allSearchTerms.push(this.currentSearchQuery);
        }
        
        // If no search terms, show all filtered data
        if (allSearchTerms.length === 0) {
            this.searchResults = [...this.filteredData];
        } else {
            // Search only within the filtered data (Sequential Filtering Model)
            this.searchResults = this.filteredData.filter(item => {
                // Item must match ANY search term (OR logic)
                return allSearchTerms.some(term => {
                    const termLower = term.toLowerCase();
                    return Object.values(item).some(value => {
                        if (value && typeof value === 'string') {
                            return value.toLowerCase().includes(termLower);
                        }
                        if (value && typeof value === 'object' && value.display_text) {
                            return value.display_text.toLowerCase().includes(termLower);
                        }
                        return false;
                    });
                });
            });
        }
        
        this.currentPage = 1;
        this.renderView();
        this.updatePagination();
    }
    
    renderView() {
        if (this.currentView === 'table') {
            this.renderTable();
        } else {
            this.renderGrid();
        }
    }
    
    renderTable() {
        const tableContainer = document.getElementById('table-container');
        const gridContainer = document.getElementById('grid-container');
        const tbody = document.querySelector('.tkz-table tbody');
        
        if (!tbody || !tableContainer || !gridContainer) return;
        
        tableContainer.style.display = 'block';
        gridContainer.style.display = 'none';
        
        tbody.innerHTML = '';
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.searchResults.slice(startIndex, endIndex);
        
        pageData.forEach(item => {
            const row = this.createTableRow(item);
            tbody.appendChild(row);
        });
    }
    
    renderGrid() {
        const tableContainer = document.getElementById('table-container');
        const gridContainer = document.getElementById('grid-container');
        
        if (!tableContainer || !gridContainer) return;
        
        tableContainer.style.display = 'none';
        gridContainer.style.display = 'grid';
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.searchResults.slice(startIndex, endIndex);
        
        gridContainer.innerHTML = pageData.map(item => this.createCard(item)).join('');
    }
    
    createTableRow(item) {
        const row = document.createElement('tr');
        const status = this.getItemStatus(item);
        row.className = `status-${status.replace(' ', '-')}`;
        
        // Apply styling based on status only
        // Font color and strikethrough styling is handled by CSS status classes
        
        row.innerHTML = `
            <td class="text-center">${item['Teilenummer'] || ''}</td>
            <td class="text-center">${item['TO-Nummer'] || '-'}</td>
            <td class="text-center">${this.createStatusBadge(status)}</td>
            <td>${item['Benennung / Kategorie'] || '-'}</td>
            <td>${item['Normkurzbezeichnung / Titel'] || '-'}</td>
            <td>${item['Projekt '] || '-'}</td>
            <td>${item['Name'] || '-'}</td>
            <td>${item['Abteilung'] || '-'}</td>
            <td>${this.formatDate(item['Datum'])}</td>
            <td>${item['Bemerkungen:'] || '-'}</td>
            <td>${item['BEN_EN'] || '-'}</td>
            <td class="document-cell attachment-column">${this.createDocumentCell(item['Zusatzinfo'])}</td>
            <td class="text-center">
                <a href="/tkz/part/${this.getItemRowNumber(item)}/" class="action-btn" title="View">
                    <i class="fas fa-eye"></i>
                </a>
            </td>
        `;
        
        return row;
    }
    
    createCard(item) {
        const status = this.getItemStatus(item);
        
        // No inline font styling - handled by CSS status classes
        
        return `
            <div class="tkz-card status-${status.replace(' ', '-')}">
                <div class="card-header">
                    <div>
                        <h3 class="card-part-no">${item['Teilenummer'] || 'N/A'}</h3>
                        <div class="card-to-number">TO: ${item['TO-Nummer'] || 'N/A'}</div>
                    </div>
                    <div class="card-status-container">
                        ${this.createStatusBadge(status)}
                    </div>
                </div>
                
                <div class="card-body">
                    <h4 class="card-title">${item['Normkurzbezeichnung / Titel'] || 'No Title'}</h4>
                    <p class="card-description">${item['Benennung / Kategorie'] || 'No description available'}</p>
                    
                    <div class="card-details">
                        <div class="card-detail">
                            <span class="card-detail-label">Project</span>
                            <span class="card-detail-value">${item['Projekt '] || '-'}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Responsible</span>
                            <span class="card-detail-value">${item['Name'] || '-'}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Department</span>
                            <span class="card-detail-value">${item['Abteilung'] || '-'}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Date</span>
                            <span class="card-detail-value">${this.formatDate(item['Datum'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Comments</span>
                            <span class="card-detail-value">${item['Bemerkungen:'] || '-'}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">English Description</span>
                            <span class="card-detail-value">${item['BEN_EN'] || '-'}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Additional Info</span>
                            <span class="card-detail-value">${item['Zusatzinfo'] || '-'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="card-meta">
                        <!-- Status styling handled by card CSS classes -->
                    </div>
                    <div class="card-actions">
                        <a href="/tkz/part/${this.getItemRowNumber(item)}/" class="card-action-btn" title="View">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
    
    createStatusBadge(status) {
        const statusMap = {
            'active': 'Active',
            'discontinued': 'Discontinued'
        };
        
        return `<span class="status-badge ${status.replace(' ', '-')}">${statusMap[status] || status}</span>`;
    }
    
    createDocumentCell(additionalInfo) {
        if (additionalInfo && additionalInfo.trim() !== '') {
            // Check if it's a URL/link or just text
            const isUrl = additionalInfo.includes('http') || additionalInfo.includes('www.');
            if (isUrl) {
                return `
                    <div class="doc-container">
                        <a href="${additionalInfo}" target="_blank" class="doc-icon" title="Additional Info Link">
                            <i class="fas fa-external-link-alt"></i>
                        </a>
                    </div>
                `;
            } else {
                return `
                    <div class="doc-container">
                        <span class="doc-icon available" title="Additional Info: ${additionalInfo}">
                            <i class="fas fa-info-circle"></i>
                        </span>
                    </div>
                `;
            }
        } else {
            return `<span class="doc-dash" title="No Additional Info">-</span>`;
        }
    }
    

    
    formatDate(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('de-DE');
        } catch (error) {
            return dateString;
        }
    }
    
    getItemRowNumber(item) {
        const index = this.searchResults.findIndex(dataItem => 
            dataItem['Teilenummer'] === item['Teilenummer']
        );
        return index + 1;
    }
    
    updateStats() {
        const totalParts = this.data.length;
        const withTO = this.data.filter(item => item['TO-Nummer'] && item['TO-Nummer'].trim() !== '').length;
        
        // Count active parts (not discontinued)
        const activeParts = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'active';
        }).length;
        
        // Count discontinued parts
        const discontinuedParts = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'discontinued';
        }).length;
        
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 3) {
            statCards[0].querySelector('.stat-value').textContent = totalParts.toLocaleString();
            statCards[1].querySelector('.stat-value').textContent = withTO.toLocaleString();
            statCards[2].querySelector('.stat-value').textContent = activeParts.toLocaleString();
            
            // Update stat labels to be more meaningful
            statCards[0].querySelector('.stat-label').textContent = 'Total Parts';
            statCards[1].querySelector('.stat-label').textContent = 'With TO Numbers';
            statCards[2].querySelector('.stat-label').textContent = 'Active Parts';
            
            // If there's a 4th stat card, show discontinued count
            if (statCards.length >= 4) {
                statCards[3].querySelector('.stat-value').textContent = discontinuedParts.toLocaleString();
                statCards[3].querySelector('.stat-label').textContent = 'Discontinued Parts';
            }
        }
    }
    
    // Comprehensive filter functionality
    applyFilters() {
        // Get filter values from form
        const filters = this.getFilterValues();
        this.activeFilters = filters;
        
        // Apply filters to the full dataset
        this.filteredData = this.data.filter(item => {
            return this.matchesFilters(item, filters);
        });
        
        // After filtering, apply current search to the filtered data
        this.handleSearch();
        
        this.currentPage = 1;
        this.updateActiveFiltersDisplay();
    }
    
    getFilterValues() {
        const filters = {};
        
        // Part status filter
        const statusCheckboxes = document.querySelectorAll('input[name="part-status"]');
        const statusFilters = [];
        let allStatusChecked = false;
        
        statusCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allStatusChecked = true;
                } else {
                    statusFilters.push(cb.value);
                }
            }
        });
        
        if (!allStatusChecked && statusFilters.length > 0) {
            filters.status = statusFilters;
        }
        

        
        // Font color filter
        const fontColorCheckboxes = document.querySelectorAll('input[name="font-color"]');
        const fontColorFilters = [];
        let allFontColorChecked = false;
        
        fontColorCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allFontColorChecked = true;
                } else {
                    fontColorFilters.push(cb.value);
                }
            }
        });
        
        if (!allFontColorChecked && fontColorFilters.length > 0) {
            filters.fontColor = fontColorFilters;
        }
        
        // Text filters
        const partGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Part Number'));
        if (partGroup) {
            const partCondition = partGroup.querySelector('.filter-condition');
            const partText = partGroup.querySelector('.filter-text-input');
            if (partCondition && partText && partText.value.trim()) {
                filters.partNumber = {
                    condition: partCondition.value,
                    text: partText.value.trim()
                };
            }
        }
        
        const toGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('TO Number'));
        if (toGroup) {
            const toCondition = toGroup.querySelector('.filter-condition');
            const toText = toGroup.querySelector('.filter-text-input');
            if (toCondition && toText && toText.value.trim()) {
                filters.toNumber = {
                    condition: toCondition.value,
                    text: toText.value.trim()
                };
            }
        }
        
        const descriptionGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Description'));
        if (descriptionGroup) {
            const descriptionCondition = descriptionGroup.querySelector('.filter-condition');
            const descriptionText = descriptionGroup.querySelector('.filter-text-input');
            if (descriptionCondition && descriptionText && descriptionText.value.trim()) {
                filters.description = {
                    condition: descriptionCondition.value,
                    text: descriptionText.value.trim()
                };
            }
        }
        
        const titleGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Title'));
        if (titleGroup) {
            const titleCondition = titleGroup.querySelector('.filter-condition');
            const titleText = titleGroup.querySelector('.filter-text-input');
            if (titleCondition && titleText && titleText.value.trim()) {
                filters.title = {
                    condition: titleCondition.value,
                    text: titleText.value.trim()
                };
            }
        }
        
        const departmentGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Department'));
        if (departmentGroup) {
            const departmentCondition = departmentGroup.querySelector('.filter-condition');
            const departmentText = departmentGroup.querySelector('.filter-text-input');
            if (departmentCondition && departmentText && departmentText.value.trim()) {
                filters.department = {
                    condition: departmentCondition.value,
                    text: departmentText.value.trim()
                };
            }
        }
        
        const projectGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Project'));
        if (projectGroup) {
            const projectCondition = projectGroup.querySelector('.filter-condition');
            const projectText = projectGroup.querySelector('.filter-text-input');
            if (projectCondition && projectText && projectText.value.trim()) {
                filters.project = {
                    condition: projectCondition.value,
                    text: projectText.value.trim()
                };
            }
        }
        
        const responsibleGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Responsible Person'));
        if (responsibleGroup) {
            const responsibleCondition = responsibleGroup.querySelector('.filter-condition');
            const responsibleText = responsibleGroup.querySelector('.filter-text-input');
            if (responsibleCondition && responsibleText && responsibleText.value.trim()) {
                filters.responsible = {
                    condition: responsibleCondition.value,
                    text: responsibleText.value.trim()
                };
            }
        }
        
        // Date filters
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        if ((dateFromInput && dateFromInput.value) || (dateToInput && dateToInput.value)) {
            filters.dateRange = {
                from: dateFromInput ? dateFromInput.value : null,
                to: dateToInput ? dateToInput.value : null
            };
        }
        
        return filters;
    }
    
    matchesFilters(item, filters) {
        // Status filter
        if (filters.status && filters.status.length > 0) {
            const itemStatus = this.getItemStatus(item);
            if (!filters.status.includes(itemStatus)) {
                return false;
            }
        }
        

        
        // Font color filter
        if (filters.fontColor && filters.fontColor.length > 0) {
            let matchesFontColor = false;
            
            for (const colorFilter of filters.fontColor) {
                switch (colorFilter) {
                    case 'default':
                        matchesFontColor = !item.font_color || item.font_color === "#000000";
                        break;
                    case 'red':
                        matchesFontColor = item.font_color === "#FF0000";
                        break;
                    case 'strikethrough':
                        matchesFontColor = item.strikethrough === true;
                        break;
                }
                if (matchesFontColor) break;
            }
            
            if (!matchesFontColor) return false;
        }
        
        // Text filters
        if (filters.partNumber) {
            const partNumber = item['Teilenummer'] || '';
            if (!this.matchesTextFilter(String(partNumber), filters.partNumber)) {
                return false;
            }
        }
        
        if (filters.toNumber) {
            const toNumber = item['TO-Nummer'] || '';
            if (!this.matchesTextFilter(String(toNumber), filters.toNumber)) {
                return false;
            }
        }
        
        if (filters.description) {
            const description = item['Benennung / Kategorie'] || '';
            if (!this.matchesTextFilter(description, filters.description)) {
                return false;
            }
        }
        
        if (filters.title) {
            const title = item['Normkurzbezeichnung / Titel'] || '';
            if (!this.matchesTextFilter(title, filters.title)) {
                return false;
            }
        }
        
        if (filters.department) {
            const department = item['Abteilung'] || '';
            if (!this.matchesTextFilter(String(department), filters.department)) {
                return false;
            }
        }
        
        if (filters.project) {
            const project = item['Projekt '] || '';
            if (!this.matchesTextFilter(String(project), filters.project)) {
                return false;
            }
        }
        
        if (filters.responsible) {
            const responsible = item['Name'] || '';
            if (!this.matchesTextFilter(String(responsible), filters.responsible)) {
                return false;
            }
        }
        
        // Date range filter
        if (filters.dateRange) {
            const itemDate = new Date(item['Datum'] || '1900-01-01');
            if (filters.dateRange.from) {
                const fromDate = new Date(filters.dateRange.from);
                if (itemDate < fromDate) return false;
            }
            if (filters.dateRange.to) {
                const toDate = new Date(filters.dateRange.to);
                if (itemDate > toDate) return false;
            }
        }
        
        return true;
    }
    
    matchesTextFilter(text, filter) {
        const textLower = text.toLowerCase();
        const filterTextLower = filter.text.toLowerCase();
        
        switch (filter.condition) {
            case 'contains':
                return textLower.includes(filterTextLower);
            case 'not_contains':
                return !textLower.includes(filterTextLower);
            case 'starts_with':
                return textLower.startsWith(filterTextLower);
            case 'ends_with':
                return textLower.endsWith(filterTextLower);
            case 'equals':
                return textLower === filterTextLower;
            default:
                return true;
        }
    }
    
    getItemStatus(item) {
        // Check status field first
        if (item.status) {
            return item.status;
        }
        
        // Fallback: determine from font color (both red font and strikethrough = discontinued)
        if (item.font_color === "#FF0000") {
            return "discontinued";
        }
        
        // Default to active if no special formatting
        return "active";
    }
    
    resetFilters() {
        // Reset part status checkboxes
        document.querySelectorAll('input[name="part-status"]').forEach(cb => {
            cb.checked = cb.value === 'all';
        });
        

        
        // Reset font color checkboxes
        document.querySelectorAll('input[name="font-color"]').forEach(cb => {
            cb.checked = cb.value === 'all';
        });
        
        // Reset text inputs
        document.querySelectorAll('.filter-text-input').forEach(input => {
            input.value = '';
        });
        
        // Reset date inputs
        document.querySelectorAll('input[type="date"]').forEach(input => {
            input.value = '';
        });
        
        // Reset to first tab
        document.querySelectorAll('.filter-tab').forEach((tab, index) => {
            tab.classList.toggle('active', index === 0);
        });
        
        document.querySelectorAll('.filter-tab-content').forEach((content, index) => {
            content.classList.toggle('active', index === 0);
        });
        
        // Update filter count
        this.updateFilterCount();
        
        // Apply the reset filters (which will be empty)
        this.applyFilters();
    }
    
    clearAllFilters() {
        this.activeFilters = {};
        this.searchTerms = [];
        this.currentSearchQuery = '';
        this.filteredData = [...this.data]; // Reset filtered data to full dataset
        this.searchResults = [...this.filteredData]; // Reset search results
        this.currentPage = 1;
        
        // Clear search input and badges
        const searchInput = document.getElementById('tkz-search');
        if (searchInput) searchInput.value = '';
        this.updateSearchBadges();
        
        // Restore default sort settings (data is already sorted)
        this.sortColumn = 'Teilenummer';
        this.sortDirection = 'desc';
        this.updateSortIcons();
        
        this.renderView();
        this.updatePagination();
        this.updateActiveFiltersDisplay();
        this.resetFilters();
    }
    
    updateActiveFiltersDisplay() {
        const activeFiltersContainer = document.querySelector('.active-filters-container');
        if (!activeFiltersContainer) return;
        
        // Get current filters
        const filters = this.getFilterValues();
        
        // Clear existing filter badges
        const filtersList = activeFiltersContainer.querySelector('.active-filters-list');
        if (filtersList) {
            filtersList.innerHTML = '';
        }
        
        // Check if there are any active filters
        const hasFilters = Object.keys(filters).length > 0;
        
        // Toggle container visibility
        activeFiltersContainer.classList.toggle('has-filters', hasFilters);
        
        if (!hasFilters) return;
        
        // Add filter badges for each filter
        for (const [key, value] of Object.entries(filters)) {
            if (Array.isArray(value)) {
                // Handle array values (like status, fontColor)
                value.forEach(val => {
                    this.addFilterBadge(filtersList, key, val);
                });
            } else if (typeof value === 'object') {
                // Handle text filters and date ranges
                if (key === 'dateRange') {
                    // Format date range
                    let dateText = '';
                    if (value.from && value.to) {
                        dateText = `${value.from} to ${value.to}`;
                    } else if (value.from) {
                        dateText = `from ${value.from}`;
                    } else if (value.to) {
                        dateText = `until ${value.to}`;
                    }
                    this.addFilterBadge(filtersList, key, dateText);
                } else {
                    // Text filters with condition
                    const filterText = `${value.condition.replace('_', ' ')}: ${value.text}`;
                    this.addFilterBadge(filtersList, key, filterText);
                }
            } else {
                // Handle simple values
                this.addFilterBadge(filtersList, key, value);
            }
        }
    }
    
    addFilterBadge(container, key, value) {
        if (!container) return;
        
        // Create list item
        const listItem = document.createElement('li');
        listItem.className = 'filter-badge';
        
        // Create label span
        const labelSpan = document.createElement('span');
        labelSpan.textContent = `${this.formatFilterLabel(key)}: `;
        
        // Create value text node
        const valueText = document.createTextNode(value);
        
        // Create remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'filter-remove-btn';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.title = 'Remove filter';
        removeBtn.addEventListener('click', () => {
            this.removeFilter(key, value);
        });
        
        // Assemble badge
        listItem.appendChild(labelSpan);
        listItem.appendChild(valueText);
        listItem.appendChild(removeBtn);
        
        // Add to container
        container.appendChild(listItem);
    }
    
    formatFilterLabel(key) {
        switch (key) {
            case 'status':
                return 'Part Status';

            case 'fontColor':
                return 'Font Color';
            case 'partNumber':
                return 'Part Number';
            case 'toNumber':
                return 'TO Number';
            case 'description':
                return 'Description';
            case 'title':
                return 'Title';
            case 'department':
                return 'Department';
            case 'project':
                return 'Project';
            case 'responsible':
                return 'Responsible Person';
            case 'dateRange':
                return 'Entry Date';
            default:
                return key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
        }
    }
    
    removeFilter(key, value) {
        // Implementation for removing specific filters (similar to directory.js)
        // This would update the form controls and reapply filters
        this.applyFilters();
    }
    
    updateFilterCount() {
        const filterCountBadge = document.getElementById('filter-count-badge');
        if (!filterCountBadge) return;
        
        let count = 0;
        
        // Count status filters
        const statusCheckboxes = document.querySelectorAll('input[name="part-status"]');
        let hasStatusFilter = false;
        statusCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasStatusFilter = true;
            }
        });
        if (hasStatusFilter) count++;
        

        
        // Count font color filters
        const fontColorCheckboxes = document.querySelectorAll('input[name="font-color"]');
        let hasFontColorFilter = false;
        fontColorCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasFontColorFilter = true;
            }
        });
        if (hasFontColorFilter) count++;
        
        // Count text filters
        const textInputs = document.querySelectorAll('.filter-text-input');
        textInputs.forEach(input => {
            if (input.value.trim()) {
                count++;
            }
        });
        
        // Count date filters
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        if ((dateFromInput && dateFromInput.value) || (dateToInput && dateToInput.value)) {
            count++;
        }
        
        // Update the badge
        filterCountBadge.textContent = count;
    }

    toggleAttachments() {
        this.attachmentsVisible = !this.attachmentsVisible;
        const attachmentBtn = document.getElementById('toggle-attachments');
        const tableContainer = document.querySelector('.table-container');
        const gridContainer = document.querySelector('.grid-container');
        
        if (this.attachmentsVisible) {
            attachmentBtn.classList.add('active');
            attachmentBtn.innerHTML = '<i class="fas fa-paperclip"></i> Hide Attachments';
            tableContainer.classList.remove('hide-attachments');
            if (gridContainer) {
                gridContainer.classList.remove('hide-attachments');
            }
        } else {
            attachmentBtn.classList.remove('active');
            attachmentBtn.innerHTML = '<i class="fas fa-paperclip"></i> Show Attachments';
            tableContainer.classList.add('hide-attachments');
            if (gridContainer) {
                gridContainer.classList.add('hide-attachments');
            }
        }
    }
    
    addSearchTerm(term) {
        this.searchTerms.push(term);
        this.updateSearchBadges();
        this.handleSearch();
    }
    
    removeSearchTerm(term) {
        this.searchTerms = this.searchTerms.filter(t => t !== term);
        this.updateSearchBadges();
        this.handleSearch();
    }
    
    updateSearchBadges() {
        const badgesContainer = document.getElementById('search-badges');
        if (!badgesContainer) return;
        
        // Get existing badges to avoid re-animating them
        const existingBadges = Array.from(badgesContainer.children);
        const existingTerms = existingBadges.map(badge => 
            badge.querySelector('span').textContent
        );
        
        // Remove badges that are no longer in searchTerms
        existingBadges.forEach(badge => {
            const term = badge.querySelector('span').textContent;
            if (!this.searchTerms.includes(term)) {
                badge.remove();
            }
        });
        
        // Add new badges (only animate these)
        this.searchTerms.forEach(term => {
            if (!existingTerms.includes(term)) {
                const badge = document.createElement('div');
                badge.className = 'search-badge';
                badge.innerHTML = `
                    <span>${term}</span>
                    <button class="search-badge-remove" title="Remove search term">
                        ×
                    </button>
                `;
                
                const removeBtn = badge.querySelector('.search-badge-remove');
                removeBtn.addEventListener('click', () => {
                    this.removeSearchTerm(term);
                });
                
                badgesContainer.appendChild(badge);
            }
        });
    }
    
    // Placeholder pagination methods
    setupPaginationListeners() {
        // Items per page (both top and bottom selectors)
        const itemsPerPageSelects = document.querySelectorAll('#items-per-page-select, #items-per-page-select-bottom');
        itemsPerPageSelects.forEach(select => {
            if (select) {
                select.addEventListener('change', (e) => {
                    this.itemsPerPage = parseInt(e.target.value);
                    this.currentPage = 1;
                    
                    // Sync both selectors
                    itemsPerPageSelects.forEach(otherSelect => {
                        if (otherSelect !== e.target) {
                            otherSelect.value = e.target.value;
                        }
                    });
                    
                    this.renderView();
                    this.updatePagination();
                });
            }
        });
    }
    
    updatePagination() {
        const totalItems = this.searchResults.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, totalItems);
        
        // Update pagination info
        document.querySelectorAll('.current-range').forEach(el => {
            el.textContent = totalItems > 0 ? `${startItem}-${endItem}` : '0-0';
        });
        
        document.querySelectorAll('.total-items').forEach(el => {
            el.textContent = totalItems.toLocaleString();
        });
        
        // Update pagination controls
        this.updatePaginationControls(totalPages);
    }
    
    updatePaginationControls(totalPages) {
        const paginationContainers = document.querySelectorAll('.pagination-controls');
        
        paginationContainers.forEach(container => {
            container.innerHTML = '';
            
            // Previous button
            const prevBtn = document.createElement('button');
            prevBtn.className = 'pagination-btn';
            prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
            prevBtn.disabled = this.currentPage === 1;
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.renderView();
                    this.updatePagination();
                }
            });
            container.appendChild(prevBtn);
            
            // Page numbers
            this.addPageNumbers(container, totalPages);
            
            // Next button
            const nextBtn = document.createElement('button');
            nextBtn.className = 'pagination-btn';
            nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
            nextBtn.disabled = this.currentPage === totalPages || totalPages === 0;
            nextBtn.addEventListener('click', () => {
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.renderView();
                    this.updatePagination();
                }
            });
            container.appendChild(nextBtn);
        });
    }
    
    addPageNumbers(container, totalPages) {
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        // First page
        if (startPage > 1) {
            this.addPageButton(container, 1);
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                container.appendChild(ellipsis);
            }
        }
        
        // Visible pages
        for (let i = startPage; i <= endPage; i++) {
            this.addPageButton(container, i);
        }
        
        // Last page
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                container.appendChild(ellipsis);
            }
            this.addPageButton(container, totalPages);
        }
    }
    
    addPageButton(container, pageNumber) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `pagination-btn page-number ${pageNumber === this.currentPage ? 'active' : ''}`;
        pageBtn.textContent = pageNumber;
        pageBtn.addEventListener('click', () => {
            this.currentPage = pageNumber;
            this.renderView();
            this.updatePagination();
        });
        container.appendChild(pageBtn);
    }
    
    hideLoading() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        this.renderView();
    }
    
    showError(message) {
        const container = document.querySelector('.tkz-container');
        if (container) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.cssText = `
                background-color: #fff5f5;
                border: 1px solid #fed7d7;
                border-radius: 8px;
                padding: 16px;
                margin: 20px 0;
                color: #c53030;
                text-align: center;
            `;
            errorDiv.textContent = message;
            container.insertBefore(errorDiv, container.firstChild);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new TKZManager();
}); 