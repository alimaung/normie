// ChemScan Management System
class ChemScanManager {
    constructor() {
        this.data = [];
        this.filteredData = []; // Data after filters are applied
        this.searchResults = []; // Data after search is applied to filteredData
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.sortColumn = 'name';
        this.sortDirection = 'asc';
        this.activeFilters = {};
        this.searchTerms = [];
        this.currentSearchQuery = '';
        this.attachmentsVisible = false;
        this.currentView = 'table'; // 'table' or 'grid'
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            this.setupEventListeners();
            this.sortData(); // Apply default sort
            this.searchResults = [...this.filteredData]; // Initialize search results
            
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
            this.updateSortIcons(); // Update sort icons to show default sort
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize ChemScan:', error);
            this.hideLoading();
            this.showError('Failed to load ChemScan data');
        }
    }
    
    async loadData() {
        try {
            const response = await fetch('/static/normieapp/data/chemscan_data.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const jsonData = await response.json();
            this.data = jsonData.data || [];
            
            // Apply default sort immediately after loading (name ascending)
            this.sortColumn = 'name';
            this.sortDirection = 'asc';
            this.data.sort((a, b) => {
                let aVal = a[this.sortColumn] || '';
                let bVal = b[this.sortColumn] || '';
                
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
                
                if (aVal < bVal) return -1;
                if (aVal > bVal) return 1;
                return 0;
            });
            
            this.filteredData = [...this.data];
            this.searchResults = [...this.filteredData];
            console.log(`Loaded ${this.data.length} ChemScan records (sorted by name ascending)`);
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('directory-search');
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
                // Remove active class from all buttons
                viewBtns.forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Switch view based on button index (0 = table, 1 = grid)
                this.currentView = index === 0 ? 'table' : 'grid';
                this.renderView();
            });
        });
        
        // Filter section toggle
        const filterBtn = document.getElementById('toggle-filter-panel');
        const filterSection = document.getElementById('filter-section');
        const closeFilterBtn = document.getElementById('close-filter-section');
        
        if (filterBtn && filterSection) {
            filterBtn.addEventListener('click', () => {
                if (filterSection.style.display === 'none' || !filterSection.style.display) {
                    filterSection.style.display = 'block';
                    filterSection.classList.add('show');
                    filterBtn.classList.add('active');
                } else {
                    filterSection.style.display = 'none';
                    filterSection.classList.remove('show');
                    filterBtn.classList.remove('active');
                }
            });
        }
        
        if (closeFilterBtn && filterSection) {
            closeFilterBtn.addEventListener('click', () => {
                filterSection.style.display = 'none';
                filterSection.classList.remove('show');
                if (filterBtn) {
                    filterBtn.classList.remove('active');
                }
            });
        }
        
        // Filter tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                
                // Update active tab
                filterTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                document.querySelectorAll('.filter-tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.querySelector(`.filter-tab-content[data-tab="${tabId}"]`).classList.add('active');
            });
        });
        
        // Filter controls
        const applyFilterBtn = document.querySelector('.filter-apply-btn');
        const resetFilterBtn = document.querySelector('.filter-reset-btn');
        const clearAllFiltersBtn = document.querySelector('.clear-filters-btn');
        
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', () => {
                this.applyFilters();
                if (filterSection) {
                    filterSection.style.display = 'none';
                    filterSection.classList.remove('show');
                }
                if (filterBtn) {
                    filterBtn.classList.remove('active');
                }
            });
        }
        
        if (resetFilterBtn) {
            resetFilterBtn.addEventListener('click', () => {
                this.resetFilters();
            });
        }
        
        if (clearAllFiltersBtn) {
            clearAllFiltersBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }
        
        // Update filter count on checkbox/radio changes
        document.querySelectorAll('#filter-section input[type="checkbox"], #filter-section input[type="radio"], #filter-section input[type="text"]')
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
        
        // Table sorting
        this.setupTableSorting();
        
        // Pagination
        this.setupPagination();
        
        // Initial filter count
        this.updateFilterCount();
    }
    
    setupTableSorting() {
        const sortableHeaders = document.querySelectorAll('.directory-table th.sortable');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const column = this.getColumnFromHeader(header);
                this.handleSort(column);
            });
        });
    }
    
    getColumnFromHeader(header) {
        const headerText = header.textContent.trim().replace(/\s*\u{f0dc}|\s*\u{f0de}|\s*\u{f0dd}/gu, '');
        const columnMap = {
            'Status': 'active',
            'WGK': 'hsWaterHazardClass',
            'Interne Bezeichnung': 'internalName',
            'Handelsname': 'name',
            'Alternative Bezeichnung': 'alternativeName',
            'Hersteller / Lieferant': 'manufacturerName'
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
            let aVal = a[this.sortColumn];
            let bVal = b[this.sortColumn];
            
            // Handle null/undefined values
            if (aVal == null) aVal = '';
            if (bVal == null) bVal = '';
            
            // Convert to string for comparison
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
            
            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }
    
    updateSortIcons() {
        // Reset all sort icons
        document.querySelectorAll('.directory-table th.sortable i').forEach(icon => {
            icon.className = 'fas fa-sort';
        });
        
        // Update current sort icon
        const currentHeader = Array.from(document.querySelectorAll('.directory-table th.sortable'))
            .find(header => this.getColumnFromHeader(header) === this.sortColumn);
        
        if (currentHeader) {
            const icon = currentHeader.querySelector('i');
            if (icon) {
                icon.className = this.sortDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
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
                        return false;
                    });
                });
            });
        }
        
        this.currentPage = 1;
        this.renderView();
        this.updatePagination();
    }
    
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
        
        // Status filter
        const statusCheckboxes = document.querySelectorAll('input[name="status"]');
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
        
        // Water hazard class filter
        const wgkCheckboxes = document.querySelectorAll('input[name="water-hazard"]');
        const wgkFilters = [];
        let allWgkChecked = false;
        
        wgkCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allWgkChecked = true;
                } else {
                    wgkFilters.push(cb.value);
                }
            }
        });
        
        if (!allWgkChecked && wgkFilters.length > 0) {
            filters.waterHazardClass = wgkFilters;
        }
        
        // Business unit filter
        const buCheckboxes = document.querySelectorAll('input[name="business-unit"]');
        const buFilters = [];
        let allBuChecked = false;
        
        buCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allBuChecked = true;
                } else {
                    buFilters.push(cb.value);
                }
            }
        });
        
        if (!allBuChecked && buFilters.length > 0) {
            filters.businessUnit = buFilters;
        }
        
        // Responsible person filter
        const responsibleCheckboxes = document.querySelectorAll('input[name="responsible"]');
        const responsibleFilters = [];
        let allResponsibleChecked = false;
        
        responsibleCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allResponsibleChecked = true;
                } else {
                    responsibleFilters.push(cb.value);
                }
            }
        });
        
        if (!allResponsibleChecked && responsibleFilters.length > 0) {
            filters.responsible = responsibleFilters;
        }
        
        // GHS symbol filter
        const ghsCheckboxes = document.querySelectorAll('input[name="ghs-symbol"]');
        const ghsFilters = [];
        let allGhsChecked = false;
        
        ghsCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allGhsChecked = true;
                } else {
                    ghsFilters.push(cb.value);
                }
            }
        });
        
        if (!allGhsChecked && ghsFilters.length > 0) {
            filters.ghsSymbols = ghsFilters;
        }
        
        // Text filters
        const textFilters = [
            { name: 'internalName', group: 'Internal Name' },
            { name: 'tradeName', group: 'Trade Name' },
            { name: 'alternativeName', group: 'Alternative Name' },
            { name: 'manufacturer', group: 'Manufacturer' },
            { name: 'hStatements', group: 'H-Statements' },
            { name: 'substanceCas', group: 'Substance/CAS' }
        ];
        
        textFilters.forEach(({ name, group }) => {
            const filterGroup = Array.from(document.querySelectorAll('.filter-group')).find(g => 
                g.querySelector('h4')?.textContent.includes(group));
            if (filterGroup) {
                const condition = filterGroup.querySelector('.filter-condition');
                const textInput = filterGroup.querySelector('.filter-text-input');
                if (condition && textInput && textInput.value.trim()) {
                    filters[name] = {
                        condition: condition.value,
                        text: textInput.value.trim()
                    };
                }
            }
        });
        
        // Document availability filters
        const docFilters = [];
        document.querySelectorAll('input[name^="doc-"]').forEach(cb => {
            if (cb.checked) {
                docFilters.push(cb.name.replace('doc-', ''));
            }
        });
        
        if (docFilters.length > 0) {
            filters.documents = docFilters;
        }
        
        return filters;
    }
    
    matchesFilters(item, filters) {
        // Status filter
        if (filters.status && filters.status.length > 0) {
            const isActive = item.active === true;
            const itemStatus = isActive ? 'active' : 'inactive';
            if (!filters.status.includes(itemStatus)) {
                return false;
            }
        }
        
        // Water hazard class filter
        if (filters.waterHazardClass && filters.waterHazardClass.length > 0) {
            const wgk = item.hsWaterHazardClass || '';
            if (!filters.waterHazardClass.includes(wgk)) {
                return false;
            }
        }
        
        // Text filters
        const textFilterMap = {
            internalName: 'internalName',
            tradeName: 'name',
            alternativeName: 'alternativeName',
            manufacturer: 'manufacturerName',
            hStatements: 'catalogRRates',
            substanceCas: 'substanceName'
        };
        
        for (const [filterKey, itemKey] of Object.entries(textFilterMap)) {
            if (filters[filterKey]) {
                const itemValue = item[itemKey] || '';
                if (!this.matchesTextFilter(String(itemValue), filters[filterKey])) {
                    return false;
                }
            }
        }
        
        // GHS symbols filter
        if (filters.ghsSymbols && filters.ghsSymbols.length > 0) {
            const itemSymbols = item.symbolSigns || '';
            const hasAnySymbol = filters.ghsSymbols.some(symbol => 
                itemSymbols.includes(symbol)
            );
            if (!hasAnySymbol) {
                return false;
            }
        }
        
        // Document availability filter
        if (filters.documents && filters.documents.length > 0) {
            let matchesAnyDocument = false;
            
            for (const docType of filters.documents) {
                let hasDocument = false;
                
                switch (docType) {
                    case 'sds':
                        hasDocument = item.hsSds && item.hsSds.trim().length > 0;
                        break;
                    case 'gbu':
                        hasDocument = item.hsHa && item.hsHa.trim().length > 0;
                        break;
                }
                
                if (hasDocument) {
                    matchesAnyDocument = true;
                    break;
                }
            }
            
            if (!matchesAnyDocument) {
                return false;
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
    
    resetFilters() {
        // Reset all checkboxes to "all" selected
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = cb.value === 'all';
        });
        
        // Reset text inputs
        document.querySelectorAll('.filter-text-input').forEach(input => {
            input.value = '';
        });
        
        // Reset to first tab
        document.querySelectorAll('.filter-tab').forEach((tab, index) => {
            tab.classList.toggle('active', index === 0);
        });
        
        document.querySelectorAll('.filter-tab-content').forEach((content, index) => {
            content.classList.toggle('active', index === 0);
        });
        
        // Reset filter count
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
        const searchInput = document.getElementById('directory-search');
        if (searchInput) searchInput.value = '';
        this.updateSearchBadges();
        
        // Restore default sort settings
        this.sortColumn = 'name';
        this.sortDirection = 'asc';
        this.updateSortIcons();
        
        this.renderView();
        this.updatePagination();
        this.updateActiveFiltersDisplay();
        this.resetFilters();
    }
    
    updateActiveFiltersDisplay() {
        // This would be similar to directory.js implementation
        // Simplified for now
        const activeFiltersContainer = document.querySelector('.active-filters-container');
        if (activeFiltersContainer) {
            const hasFilters = Object.keys(this.activeFilters).length > 0;
            activeFiltersContainer.classList.toggle('has-filters', hasFilters);
        }
    }
    
    setupPagination() {
        // Pagination will be set up dynamically in updatePagination
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
        const tbody = document.querySelector('.directory-table tbody');
        
        if (!tbody || !tableContainer || !gridContainer) return;
        
        // Show table, hide grid
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
        
        // Show grid, hide table
        tableContainer.style.display = 'none';
        gridContainer.style.display = 'grid';
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.searchResults.slice(startIndex, endIndex);
        
        gridContainer.innerHTML = pageData.map(item => this.createCard(item)).join('');
    }
    
    // Helper function to handle empty values
    formatEmptyValue(value) {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
            return '-';
        }
        return value;
    }

    createTableRow(item) {
        const row = document.createElement('tr');
        const wgkClass = this.getWgkClass(item.hsWaterHazardClass);
        row.className = wgkClass;
        
        row.innerHTML = `
            <td class="text-center">${this.createStatusBadge(item.active)}</td>
            <td class="text-center">${this.createWgkBadge(item.hsWaterHazardClass)}</td>
            <td>${this.formatEmptyValue(item.internalName)}</td>
            <td>${this.formatEmptyValue(item.name)}</td>
            <td>${this.formatEmptyValue(item.alternativeName)}</td>
            <td>${this.formatEmptyValue(item.manufacturerName)}</td>
            <td>${this.createGhsSymbols(item.symbolSigns)}</td>
            <td>${this.createHStatements(item.catalogRRates)}</td>
            <td class="substance-cell">${this.createSubstanceList(item.substanceName)}</td>
            <td class="business-unit-cell">${this.createBusinessUnitList(item.hazardSubstanceAssessmentBU)}</td>
            <td>${this.formatEmptyValue(item.responsibleUserGroup)}</td>
            <td class="attachment-column">${this.createDocumentLink(item.hsSds, 'SDS')}</td>
            <td class="attachment-column">${this.createDocumentLink(item.hsHa, 'GBU')}</td>
            <td class="actions-cell">
                <button class="action-btn" title="View" onclick="window.open('https://app.chemscan.de${item.view_link}', '_blank')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        
        return row;
    }
    
    createCard(item) {
        const wgkClass = this.getWgkClass(item.hsWaterHazardClass);
        
        return `
            <div class="directory-card ${wgkClass}">
                <div class="card-header">
                    <h3 class="card-application-no">${this.formatEmptyValue(item.name)}</h3>
                    <div class="card-status-container">
                        ${this.createStatusBadge(item.active)}
                        ${this.createWgkBadge(item.hsWaterHazardClass)}
                    </div>
                </div>
                
                <div class="card-body">
                    <h4 class="card-title">${this.formatEmptyValue(item.internalName)}</h4>
                    <p class="card-description">${this.formatEmptyValue(item.alternativeName)}</p>
                    
                    <div class="card-hazard-symbols">
                        ${this.createGhsSymbols(item.symbolSigns)}
                    </div>
                    
                    <div class="card-h-statements">
                        ${this.createHStatements(item.catalogRRates)}
                    </div>
                    
                    <div class="card-substances">
                        ${this.createSubstanceList(item.substanceName)}
                    </div>
                    
                    <div class="card-details">
                        <div class="card-detail">
                            <span class="card-detail-label">Manufacturer</span>
                            <span class="card-detail-value">${this.formatEmptyValue(item.manufacturerName)}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Responsible Person</span>
                            <span class="card-detail-value">${this.formatEmptyValue(item.responsibleUserGroup)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="card-meta">
                        <div class="card-business-units">
                            ${this.createBusinessUnitList(item.hazardSubstanceAssessmentBU)}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="card-action-btn" title="View" onclick="window.open('${item.view_link}', '_blank')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    createStatusBadge(active) {
        const status = active ? 'active' : 'inactive';
        const statusText = active ? 'Active' : 'Inactive';
        return `<span class="status-badge ${status}">${statusText}</span>`;
    }
    
    createWgkBadge(wgkClass) {
        if (!wgkClass) return '-';
        const wgkNumber = wgkClass.replace('WGK ', '');
        return `<span class="wgk-badge wgk${wgkNumber.toLowerCase()}">${wgkNumber}</span>`;
    }
    
    getWgkClass(wgkClass) {
        if (!wgkClass) return '';
        const wgkNumber = wgkClass.replace('WGK ', '').toLowerCase();
        return `wgk${wgkNumber}`;
    }
    
    createGhsSymbols(symbolSigns) {
        if (!symbolSigns) return '-';
        
        const symbols = symbolSigns.split(', ').map(symbol => {
            const symbolNumber = symbol.replace('GHS', '').padStart(2, '0');
            return `<span class="ghs-symbol ghs${symbolNumber}" title="${symbol}">${symbol}</span>`;
        });
        
        return symbols.join('');
    }
    
    createHStatements(catalogRRates) {
        if (!catalogRRates) return '-';
        
        const statements = catalogRRates.split(', ').map(statement => 
            `<span class="h-statement">${statement}</span>`
        );
        
        return statements.join(' ');
    }
    
    createSubstanceList(substanceName) {
        if (!substanceName) return '-';
        
        // Remove HTML tags and split by <br/>
        const substances = substanceName.replace(/<br\/?>/g, '|').split('|');
        
        if (substances.length <= 3) {
            return substances.map(substance => {
                const match = substance.match(/^(.*?)\s*\[([^\]]+)\]$/);
                if (match) {
                    return `${match[1].trim()} <span class="cas-number">[${match[2]}]</span>`;
                }
                return substance.trim();
            }).join('<br>');
        } else {
            const firstThree = substances.slice(0, 3).map(substance => {
                const match = substance.match(/^(.*?)\s*\[([^\]]+)\]$/);
                if (match) {
                    return `${match[1].trim()} <span class="cas-number">[${match[2]}]</span>`;
                }
                return substance.trim();
            }).join('<br>');
            
            return `${firstThree}<br><small>... and ${substances.length - 3} more</small>`;
        }
    }
    
    createBusinessUnitList(hazardSubstanceAssessmentBU) {
        if (!hazardSubstanceAssessmentBU) return '-';
        
        // Extract business unit names from HTML
        const matches = hazardSubstanceAssessmentBU.match(/>([^<]+)</g);
        if (!matches) return '-';
        
        const businessUnits = matches.map(match => match.slice(1, -1).trim());
        
        if (businessUnits.length <= 2) {
            return businessUnits.join(', ');
        } else {
            return `${businessUnits.slice(0, 2).join(', ')} (+${businessUnits.length - 2} more)`;
        }
    }
    
    createDocumentLink(docHtml, docType) {
        if (!docHtml || docHtml.trim() === '') {
            return '<span class="doc-dash" title="No document">-</span>';
        }
        
        const iconMap = {
            'SDS': 'fas fa-file-medical',
            'GBU': 'fas fa-shield-alt'
        };
        
        return `
            <div class="doc-container">
                <a href="#" class="doc-icon" title="${docType}">
                    <i class="${iconMap[docType] || 'fas fa-file'}"></i>
                </a>
            </div>
        `;
    }
    
    updateStats() {
        const totalSubstances = this.data.length;
        const activeCount = this.data.filter(item => item.active === true).length;
        const wgk3Count = this.data.filter(item => item.hsWaterHazardClass === 'WGK 3').length;
        
        // Update stat cards
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 3) {
            statCards[0].querySelector('.stat-value').textContent = totalSubstances.toLocaleString();
            statCards[1].querySelector('.stat-value').textContent = activeCount.toLocaleString();
            statCards[2].querySelector('.stat-value').textContent = wgk3Count.toLocaleString();
        }
    }
    
    hideLoading() {
        const loadingIndicator = document.getElementById('loading-indicator');
        
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // Show the appropriate view
        this.renderView();
    }
    
    showError(message) {
        const container = document.querySelector('.directory-container');
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
    
    updateFilterCount() {
        const filterCountBadge = document.getElementById('filter-count-badge');
        if (!filterCountBadge) return;
        
        let count = 0;
        
        // Count status filters
        const statusCheckboxes = document.querySelectorAll('input[name="status"]');
        let hasStatusFilter = false;
        statusCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasStatusFilter = true;
            }
        });
        if (hasStatusFilter) count++;
        
        // Count water hazard class filters
        const wgkCheckboxes = document.querySelectorAll('input[name="water-hazard"]');
        let hasWgkFilter = false;
        wgkCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasWgkFilter = true;
            }
        });
        if (hasWgkFilter) count++;
        
        // Count text filters
        const textInputs = document.querySelectorAll('.filter-text-input');
        textInputs.forEach(input => {
            if (input.value.trim()) {
                count++;
            }
        });
        
        // Count document filters
        const docCheckboxes = document.querySelectorAll('input[name^="doc-"]');
        let hasDocFilter = false;
        docCheckboxes.forEach(cb => {
            if (cb.checked) {
                hasDocFilter = true;
            }
        });
        if (hasDocFilter) count++;
        
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ChemScanManager();
});
