// Directory Management System
class DirectoryManager {
    constructor() {
        this.data = [];
        this.filteredData = []; // Data after filters are applied
        this.searchResults = []; // Data after search is applied to filteredData
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.sortColumn = 'Antrag-nummer';
        this.sortDirection = 'desc';
        this.activeFilters = {};
        this.searchTerms = [];
        this.currentSearchQuery = '';
        this.attachmentsVisible = false;
        this.currentView = 'table'; // 'table' or 'grid'
        this.statusPollingInterval = null;
        
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
            this.startStatusPolling(); // Start monitoring update service status
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize directory:', error);
            this.hideLoading();
            this.showError('Failed to load directory data');
        }
    }
    
    async loadData() {
        try {
            // Try compressed version first, fallback to original
            let response;
            let jsonData;
            
            try {
                response = await fetch('/static/normieapp/data/Verzeichnis_compressed.json');
                if (response.ok) {
                    jsonData = await response.json();
                    console.log('Loaded compressed directory data');
                    
                    // Decompress if needed
                    if (jsonData.metadata && jsonData.metadata.compressed) {
                        this.data = this.decompressData(jsonData);
                    } else {
                        this.data = jsonData.data || [];
                    }
                } else {
                    throw new Error('Compressed version not available');
                }
            } catch (e) {
                console.log('Compressed version not available, loading full version...');
                response = await fetch('/static/normieapp/data/Verzeichnis.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                jsonData = await response.json();
                this.data = jsonData.data || [];
            }
            
            // Apply default sort immediately after loading (Application No. descending)
            this.sortColumn = 'Antrag-nummer';
            this.sortDirection = 'desc';
            this.data.sort((a, b) => {
                let aVal = a[this.sortColumn];
                let bVal = b[this.sortColumn];
                
                // Handle null/undefined values
                if (aVal == null) aVal = '';
                if (bVal == null) bVal = '';
                
                // Special handling for Application No. (XXX/YYYY format)
                const parseAppNo = (appNo) => {
                    if (!appNo || typeof appNo !== 'string') return { number: 0, year: 0 };
                    const parts = appNo.split('/');
                    if (parts.length !== 2) return { number: 0, year: 0 };
                    return {
                        number: parseInt(parts[0]) || 0,
                        year: parseInt(parts[1]) || 0
                    };
                };
                
                const aParsed = parseAppNo(aVal);
                const bParsed = parseAppNo(bVal);
                
                // Sort by year first (descending), then by number (descending)
                if (aParsed.year !== bParsed.year) {
                    return bParsed.year - aParsed.year; // Always descending for default sort
                }
                // If years are the same, sort by number (descending)
                return bParsed.number - aParsed.number; // Always descending for default sort
            });
            
            this.filteredData = [...this.data];
            this.searchResults = [...this.filteredData];
            console.log(`Loaded ${this.data.length} records (sorted by Application No. descending)`);
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    decompressData(compressedData) {
        // Decompress the JSON data on the client side
        console.log('Decompressing directory data...');
        
        const metadata = compressedData.metadata || {};
        const columnMap = metadata.column_map || {};
        const baseUrl = metadata.base_url || '';
        const compressedItems = compressedData.data || [];
        
        const decompressedData = compressedItems.map(item => {
            const decompressed = {};
            
            // Restore original column names and values
            for (const [shortKey, value] of Object.entries(item)) {
                const originalKey = columnMap[shortKey] || shortKey;
                
                // Decompress document URLs
                if (['Antrag', 'Datenblatt', 'Produkt-zulassung', 'SDB MSDS',
                     'Gefährdungsprüfungeurteilung', 'Gefährdungsprüfung', 
                     'Sonstiges', 'Schriftverkehr', 'Änd. Historie'].includes(originalKey)) {
                    
                    if (value && typeof value === 'string') {
                        decompressed[originalKey] = {
                            display_text: 'pdf',
                            url: baseUrl + value,
                            original_url: null,
                            tooltip: ''
                        };
                    } else {
                        decompressed[originalKey] = null;
                    }
                } else {
                    decompressed[originalKey] = value;
                }
            }
            
            // Add null values for missing document columns
            ['Antrag', 'Datenblatt', 'Produkt-zulassung', 'SDB MSDS',
             'Gefährdungsprüfungeurteilung', 'Gefährdungsprüfung', 
             'Sonstiges', 'Schriftverkehr', 'Änd. Historie'].forEach(docCol => {
                if (!(docCol in decompressed)) {
                    decompressed[docCol] = null;
                }
            });
            
            return decompressed;
        });
        
        console.log(`Decompressed ${decompressedData.length} items`);
        return decompressedData;
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
        
        // Quick date buttons
        const quickDateBtns = document.querySelectorAll('.quick-date-btn');
        quickDateBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const range = btn.getAttribute('data-range');
                const target = btn.getAttribute('data-target') || 'entry';
                
                // Remove active class from all buttons in the same group
                btn.parentElement.querySelectorAll('.quick-date-btn').forEach(b => {
                    b.classList.remove('active');
                });
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Set date inputs based on range
                const today = new Date();
                let fromDate = new Date();
                let toDate = new Date();
                
                switch (range) {
                    case 'today':
                        // From and to are both today
                        break;
                    case 'yesterday':
                        fromDate.setDate(fromDate.getDate() - 1);
                        toDate.setDate(toDate.getDate() - 1);
                        break;
                    case 'week':
                        // Start of current week (Sunday)
                        const dayOfWeek = today.getDay();
                        fromDate.setDate(today.getDate() - dayOfWeek);
                        break;
                    case 'month':
                        // Start of current month
                        fromDate.setDate(1);
                        break;
                    case 'year':
                        // Start of current year
                        fromDate.setMonth(0);
                        fromDate.setDate(1);
                        break;
                }
                
                // Format dates as YYYY-MM-DD for input fields
                const formatDateForInput = (date) => {
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');
                    return `${year}-${month}-${day}`;
                };
                
                // Set date inputs
                if (target === 'completion') {
                    document.getElementById('completion-from').value = formatDateForInput(fromDate);
                    document.getElementById('completion-to').value = formatDateForInput(toDate);
                } else {
                    document.getElementById('date-from').value = formatDateForInput(fromDate);
                    document.getElementById('date-to').value = formatDateForInput(toDate);
                }
            });
        });
        
        // Range sliders
        const setupRangeSlider = (minId, maxId, valMinId, valMaxId) => {
            const minSlider = document.getElementById(minId);
            const maxSlider = document.getElementById(maxId);
            const minValue = document.getElementById(valMinId);
            const maxValue = document.getElementById(valMaxId);
            
            if (minSlider && maxSlider) {
                // Update range slider values
                const updateRangeValues = () => {
                    const min = parseInt(minSlider.value);
                    const max = parseInt(maxSlider.value);
                    
                    // Ensure min doesn't exceed max
                    if (min > max) {
                        minSlider.value = max;
                    }
                    
                    // Update displayed values
                    minValue.textContent = `${minSlider.value} days`;
                    maxValue.textContent = max === 365 ? '365+ days' : `${maxSlider.value} days`;
                    
                    // Update the colored range
                    const minPercent = (minSlider.value / minSlider.max) * 100;
                    const maxPercent = (maxSlider.value / maxSlider.max) * 100;
                    
                    // Update the range progress element
                    const rangeProgress = minSlider.parentElement.querySelector('.range-progress');
                    if (rangeProgress) {
                        rangeProgress.style.left = `${minPercent}%`;
                        rangeProgress.style.right = `${100 - maxPercent}%`;
                    }
                };
                
                // Set up event listeners
                minSlider.addEventListener('input', updateRangeValues);
                maxSlider.addEventListener('input', updateRangeValues);
                
                // Initialize values
                updateRangeValues();
            }
        };
        
        // Set up processing time range slider
        setupRangeSlider(
            'processing-time-min-range',
            'processing-time-max-range',
            'processing-time-min',
            'processing-time-max'
        );
        
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
            'Application No.': 'Antrag-nummer',
            'Part No.': 'Teile-nummer',
            'Description': 'Benennung',
            'Product Name': 'Produktname / Normkurzbezeichnung',
            'Entry Date': 'Eingang',
            'Completion Date': 'Abschluss',
            'Department': 'Abteilung',
            'Applicant': 'Antragsteller'
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
            
            // Special handling for Application No. (XXX/YYYY format)
            if (this.sortColumn === 'Antrag-nummer') {
                const parseAppNo = (appNo) => {
                    if (!appNo || typeof appNo !== 'string') return { number: 0, year: 0 };
                    const parts = appNo.split('/');
                    if (parts.length !== 2) return { number: 0, year: 0 };
                    return {
                        number: parseInt(parts[0]) || 0,
                        year: parseInt(parts[1]) || 0
                    };
                };
                
                const aParsed = parseAppNo(aVal);
                const bParsed = parseAppNo(bVal);
                
                // Sort by year first (descending), then by number (descending)
                if (aParsed.year !== bParsed.year) {
                    return this.sortDirection === 'desc' ? bParsed.year - aParsed.year : aParsed.year - bParsed.year;
                }
                // If years are the same, sort by number
                return this.sortDirection === 'desc' ? bParsed.number - aParsed.number : aParsed.number - bParsed.number;
            }
            
            // Handle dates
            if (this.sortColumn === 'Eingang' || this.sortColumn === 'Abschluss') {
                aVal = new Date(aVal || '1900-01-01');
                bVal = new Date(bVal || '1900-01-01');
            }
            
            // Convert to string for comparison if not date
            if (!(aVal instanceof Date)) {
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
            }
            
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
        
        // Approval status
        const approvalCheckboxes = document.querySelectorAll('input[name="approval-status"]');
        const approvalFilters = [];
        let allApprovalChecked = false;
        
        approvalCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allApprovalChecked = true;
                } else {
                    approvalFilters.push(cb.value.replace('-', ' '));
                }
            }
        });
        
        if (!allApprovalChecked && approvalFilters.length > 0) {
            filters.approval = approvalFilters;
        }
        
        // Product relevance
        const relevanceRadios = document.querySelectorAll('input[name="relevance"]');
        relevanceRadios.forEach(radio => {
            if (radio.checked && radio.parentElement.textContent.trim() !== 'All') {
                filters.relevance = radio.parentElement.textContent.trim().toLowerCase();
            }
        });
        
        // Location (now radio buttons)
        const locationRadios = document.querySelectorAll('input[name="location"]');
        locationRadios.forEach(radio => {
            if (radio.checked && radio.value !== 'all') {
                filters.location = radio.value.toUpperCase();
            }
        });
        
        // Processor
        const processorCheckboxes = document.querySelectorAll('input[name="processor"]');
        const processorFilters = [];
        let allProcessorChecked = false;
        
        processorCheckboxes.forEach(cb => {
            if (cb.checked) {
                if (cb.value === 'all') {
                    allProcessorChecked = true;
                } else {
                    processorFilters.push(cb.value);
                }
            }
        });
        
        if (!allProcessorChecked && processorFilters.length > 0) {
            filters.processor = processorFilters;
        }
        
        // Text filters - using compatible selectors
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
        
        // Application Number filter
        const appGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Application Number'));
        if (appGroup) {
            const appCondition = appGroup.querySelector('.filter-condition');
            const appText = appGroup.querySelector('.filter-text-input');
            if (appCondition && appText && appText.value.trim()) {
                filters.applicationNumber = {
                    condition: appCondition.value,
                    text: appText.value.trim()
                };
            }
        }
        
        // Department filter
        const deptGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Department'));
        if (deptGroup) {
            const deptCondition = deptGroup.querySelector('.filter-condition');
            const deptText = deptGroup.querySelector('.filter-text-input');
            if (deptCondition && deptText && deptText.value.trim()) {
                filters.department = {
                    condition: deptCondition.value,
                    text: deptText.value.trim()
                };
            }
        }
        
        // Product Name filter
        const productGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Product Name'));
        if (productGroup) {
            const productCondition = productGroup.querySelector('.filter-condition');
            const productText = productGroup.querySelector('.filter-text-input');
            if (productCondition && productText && productText.value.trim()) {
                filters.productName = {
                    condition: productCondition.value,
                    text: productText.value.trim()
                };
            }
        }
        
        // Applicant filter
        const applicantGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
            group.querySelector('h4')?.textContent.includes('Applicant'));
        if (applicantGroup) {
            const applicantCondition = applicantGroup.querySelector('.filter-condition');
            const applicantText = applicantGroup.querySelector('.filter-text-input');
            if (applicantCondition && applicantText && applicantText.value.trim()) {
                filters.applicant = {
                    condition: applicantCondition.value,
                    text: applicantText.value.trim()
                };
            }
        }
        
        // Entry Date filter
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        if ((dateFromInput && dateFromInput.value) || (dateToInput && dateToInput.value)) {
            filters.entryDateRange = {
                from: dateFromInput ? dateFromInput.value : null,
                to: dateToInput ? dateToInput.value : null
            };
        }
        
        // Completion Date filter
        const completionFromInput = document.getElementById('completion-from');
        const completionToInput = document.getElementById('completion-to');
        if ((completionFromInput && completionFromInput.value) || (completionToInput && completionToInput.value)) {
            filters.completionDateRange = {
                from: completionFromInput ? completionFromInput.value : null,
                to: completionToInput ? completionToInput.value : null
            };
        }
        
        // Processing Time Range filter
        const minTimeRange = document.getElementById('processing-time-min-range');
        const maxTimeRange = document.getElementById('processing-time-max-range');
        if (minTimeRange && maxTimeRange && 
            (parseInt(minTimeRange.value) > 0 || parseInt(maxTimeRange.value) < 365)) {
            filters.processingTimeRange = {
                min: parseInt(minTimeRange.value),
                max: parseInt(maxTimeRange.value)
            };
        }
        
        // Document Availability filters
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
        // Approval status filter
        if (filters.approval && filters.approval.length > 0) {
            const itemStatus = this.getItemStatus(item);
            if (!filters.approval.includes(itemStatus)) {
                return false;
            }
        }
        
        // Product relevance filter
        if (filters.relevance) {
            const relevanceValue = item['relevant für Luftfahrtteile'];
            const isAircraft = relevanceValue && relevanceValue.toLowerCase() === 'ja';
            if (filters.relevance === 'aviation relevant' && !isAircraft) return false;
            if (filters.relevance === 'not aviation relevant' && isAircraft) return false;
        }
        
        // Location filter
        if (filters.location) {
            const itemLocation = item['Einsatzort'];
            if (!itemLocation || itemLocation !== filters.location) {
                return false;
            }
        }
        
        // Processor filter
        if (filters.processor && filters.processor.length > 0) {
            const itemProcessor = (item['Bearbeiter'] || 'applicant').toLowerCase();
            if (!filters.processor.includes(itemProcessor)) {
                return false;
            }
        }
        
        // Description filter
        if (filters.description) {
            const description = item['Benennung'] || '';
            if (!this.matchesTextFilter(description, filters.description)) {
                return false;
            }
        }
        
        // Part number filter
        if (filters.partNumber) {
            const partNumber = item['Teile-nummer'] || '';
            if (!this.matchesTextFilter(String(partNumber), filters.partNumber)) {
                return false;
            }
        }
        
        // Application number filter
        if (filters.applicationNumber) {
            const appNumber = item['Antrag-Nr'] || '';
            if (!this.matchesTextFilter(String(appNumber), filters.applicationNumber)) {
                return false;
            }
        }
        
        // Department filter
        if (filters.department) {
            const department = item['Abteilung'] || '';
            if (!this.matchesTextFilter(String(department), filters.department)) {
                return false;
            }
        }
        
        // Product name filter
        if (filters.productName) {
            const productName = item['Produktname'] || '';
            if (!this.matchesTextFilter(String(productName), filters.productName)) {
                return false;
            }
        }
        
        // Applicant filter
        if (filters.applicant) {
            const applicant = item['Antragsteller'] || '';
            if (!this.matchesTextFilter(String(applicant), filters.applicant)) {
                return false;
            }
        }
        
        // Entry date range filter
        if (filters.entryDateRange) {
            const entryDate = new Date(item['Eingang'] || '1900-01-01');
            if (filters.entryDateRange.from) {
                const fromDate = new Date(filters.entryDateRange.from);
                if (entryDate < fromDate) return false;
            }
            if (filters.entryDateRange.to) {
                const toDate = new Date(filters.entryDateRange.to);
                if (entryDate > toDate) return false;
            }
        }
        
        // Completion date range filter
        if (filters.completionDateRange) {
            const completionDate = new Date(item['Abschluss'] || '1900-01-01');
            if (filters.completionDateRange.from) {
                const fromDate = new Date(filters.completionDateRange.from);
                if (completionDate < fromDate) return false;
            }
            if (filters.completionDateRange.to) {
                const toDate = new Date(filters.completionDateRange.to);
                if (completionDate > toDate) return false;
            }
        }
        
        // Processing time range filter
        if (filters.processingTimeRange) {
            const entryDate = new Date(item['Eingang'] || '1900-01-01');
            const completionDate = new Date(item['Abschluss'] || new Date());
            
            // Calculate processing time in days
            const processingTime = Math.floor((completionDate - entryDate) / (1000 * 60 * 60 * 24));
            
            if (processingTime < filters.processingTimeRange.min || 
                processingTime > filters.processingTimeRange.max) {
                return false;
            }
        }
        
        // Document availability filter
        if (filters.documents && filters.documents.length > 0) {
            let matchesAnyDocument = false;
            
            for (const docType of filters.documents) {
                let hasDocument = false;
                
                switch (docType) {
                    case 'application':
                        hasDocument = item['Antrag'] && (typeof item['Antrag'] === 'object' || item['Antrag'].length > 0);
                        break;
                    case 'datasheet':
                        hasDocument = item['Datenblatt'] && (typeof item['Datenblatt'] === 'object' || item['Datenblatt'].length > 0);
                        break;
                    case 'approval':
                        hasDocument = item['Produkt-zulassung'] && (typeof item['Produkt-zulassung'] === 'object' || item['Produkt-zulassung'].length > 0);
                        break;
                    case 'sdb':
                        hasDocument = item['SDB MSDS'] && (typeof item['SDB MSDS'] === 'object' || item['SDB MSDS'].length > 0);
                        break;
                    case 'chemscan':
                        hasDocument = item['ChemScan'] && (typeof item['ChemScan'] === 'object' || item['ChemScan'].length > 0);
                        break;
                    case 'hazard':
                        hasDocument = (item['Gefährdungsprüfungeurteilung'] && (typeof item['Gefährdungsprüfungeurteilung'] === 'object' || item['Gefährdungsprüfungeurteilung'].length > 0)) || 
                                      (item['Gefährdungsprüfung'] && (typeof item['Gefährdungsprüfung'] === 'object' || item['Gefährdungsprüfung'].length > 0));
                        break;
                    case 'misc':
                        hasDocument = item['Sonstiges'] && (typeof item['Sonstiges'] === 'object' || item['Sonstiges'].length > 0);
                        break;
                    case 'correspondence':
                        hasDocument = item['Schriftverkehr'] && (typeof item['Schriftverkehr'] === 'object' || item['Schriftverkehr'].length > 0);
                        break;
                    case 'history':
                        hasDocument = item['Änd. Historie'] && (typeof item['Änd. Historie'] === 'object' || item['Änd. Historie'].length > 0);
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
    
    getItemStatus(item) {
        // Use the exact color mapping from the JSON metadata
        const colorMapping = {
            "#FFCC99": "not approved",
            "#CCFFCC": "approved", 
            "#CCFF99": "approved for first order",
            "#FFFFFF": "processing"
        };
        
        // Get status from color mapping first (this is the authoritative source)
        const mappedStatus = colorMapping[item.color];
        if (mappedStatus) {
            // Convert to our internal status format
            switch (mappedStatus) {
                case "approved":
                    return "approved";
                case "approved for first order":
                    return "first use";
                case "not approved":
                    return "rejected";
                case "processing":
                    return "processing";
                default:
                    return "processing";
            }
        }
        
        // Fallback: if no color match, try the status field
        if (item.status) {
            // Convert the raw status to our internal format
            switch (item.status) {
                case "approved":
                    return "approved";
                case "approved for first order":
                    return "first use";
                case "not approved":
                    return "rejected";
                case "processing":
                    return "processing";
                default:
                    return "processing";
            }
        }
        
        // Final fallback to processing if no status information
        return "processing";
    }
    
    resetFilters() {
        // Reset approval status checkboxes
        document.querySelectorAll('input[name="approval-status"]').forEach(cb => {
            cb.checked = cb.value === 'all';
        });
        
        // Reset product relevance radios
        document.querySelectorAll('input[name="relevance"]').forEach(radio => {
            radio.checked = radio.value === 'all';
        });
        
        // Reset location radios
        document.querySelectorAll('input[name="location"]').forEach(radio => {
            radio.checked = radio.value === 'all';
        });
        
        // Reset processor checkboxes
        document.querySelectorAll('input[name="processor"]').forEach(cb => {
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
        
        // Reset quick date buttons
        document.querySelectorAll('.quick-date-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Reset processing time range slider
        if (document.getElementById('processing-time-min-range')) {
            document.getElementById('processing-time-min-range').value = 0;
        }
        if (document.getElementById('processing-time-max-range')) {
            document.getElementById('processing-time-max-range').value = 365;
        }
        
        // Update range slider display
        if (document.getElementById('processing-time-min') && document.getElementById('processing-time-max')) {
            document.getElementById('processing-time-min').textContent = '0 days';
            document.getElementById('processing-time-max').textContent = '365+ days';
        }
        
        // Reset range slider colored area
        const rangeSlider = document.querySelector('.range-slider');
        if (rangeSlider) {
            const rangeProgress = rangeSlider.querySelector('.range-progress');
            if (rangeProgress) {
                rangeProgress.style.left = '0%';
                rangeProgress.style.right = '0%';
            }
        }
        
        // Reset document availability checkboxes
        document.querySelectorAll('input[name^="doc-"]').forEach(cb => {
            cb.checked = false;
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
    
    updateFormControlsFromActiveFilters() {
        // First reset all controls
        this.resetFilters();
        
        // Then set controls based on active filters
        Object.entries(this.activeFilters).forEach(([key, value]) => {
            if (key === 'approval' && Array.isArray(value)) {
                // Update approval status checkboxes
                value.forEach(status => {
                    const checkbox = document.querySelector(`input[name="approval-status"][value="${status.replace(' ', '-')}"]`);
                    if (checkbox) checkbox.checked = true;
                });
                // Uncheck "all" if specific statuses are selected
                const allCheckbox = document.querySelector('input[name="approval-status"][value="all"]');
                if (allCheckbox) allCheckbox.checked = false;
            } else if (key === 'relevance' && typeof value === 'string') {
                // Update relevance radio buttons
                if (value === 'aviation relevant') {
                    const aircraftRadio = document.querySelector('input[name="relevance"][value="aircraft"]');
                    if (aircraftRadio) aircraftRadio.checked = true;
                } else if (value === 'not aviation relevant') {
                    const notAircraftRadio = document.querySelector('input[name="relevance"][value="non-aircraft"]');
                    if (notAircraftRadio) notAircraftRadio.checked = true;
                } else {
                    const allRadio = document.querySelector('input[name="relevance"][value="all"]');
                    if (allRadio) allRadio.checked = true;
                }
            } else if (key === 'location' && typeof value === 'string') {
                // Update location radio buttons
                const locationRadio = document.querySelector(`input[name="location"][value="${value.toLowerCase()}"]`);
                if (locationRadio) locationRadio.checked = true;
            } else if (key === 'processor' && Array.isArray(value)) {
                // Update processor checkboxes
                value.forEach(processor => {
                    const checkbox = document.querySelector(`input[name="processor"][value="${processor.toLowerCase()}"]`);
                    if (checkbox) checkbox.checked = true;
                });
                // Uncheck "all" if specific processors are selected
                const allCheckbox = document.querySelector('input[name="processor"][value="all"]');
                if (allCheckbox) allCheckbox.checked = false;
            } else if (key === 'description' && typeof value === 'object') {
                // Update description text filter
                const descriptionGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
                    group.querySelector('h4')?.textContent.includes('Description'));
                if (descriptionGroup) {
                    const conditionSelect = descriptionGroup.querySelector('.filter-condition');
                    const textInput = descriptionGroup.querySelector('.filter-text-input');
                    if (conditionSelect) conditionSelect.value = value.condition;
                    if (textInput) textInput.value = value.text;
                }
            } else if (key === 'partNumber' && typeof value === 'object') {
                // Update part number text filter
                const partGroup = Array.from(document.querySelectorAll('.filter-group')).find(group => 
                    group.querySelector('h4')?.textContent.includes('Part Number'));
                if (partGroup) {
                    const conditionSelect = partGroup.querySelector('.filter-condition');
                    const textInput = partGroup.querySelector('.filter-text-input');
                    if (conditionSelect) conditionSelect.value = value.condition;
                    if (textInput) textInput.value = value.text;
                }
            } else if (key === 'dateRange' && typeof value === 'object') {
                // Update date range inputs
                const fromInput = document.getElementById('date-from');
                const toInput = document.getElementById('date-to');
                if (fromInput && value.from) fromInput.value = value.from;
                if (toInput && value.to) toInput.value = value.to;
            }
        });
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
        
        // Restore default sort settings (data is already sorted)
        this.sortColumn = 'Antrag-nummer';
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
                // Handle array values (like approval, processor, documents)
                value.forEach(val => {
                    this.addFilterBadge(filtersList, key, val);
                });
            } else if (typeof value === 'object') {
                // Handle text filters and date ranges
                if (key === 'entryDateRange' || key === 'completionDateRange') {
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
                } else if (key === 'processingTimeRange') {
                    // Format processing time range
                    const rangeText = `${value.min} - ${value.max === 365 ? '365+' : value.max} days`;
                    this.addFilterBadge(filtersList, key, rangeText);
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
            case 'approval':
                return 'Approval Status';
            case 'relevance':
                return 'Product Relevance';
            case 'location':
                return 'Location';
            case 'processor':
                return 'Processor';
            case 'description':
                return 'Description';
            case 'partNumber':
                return 'Part Number';
            case 'entryDateRange':
                return 'Entry Date';
            case 'completionDateRange':
                return 'Completion Date';
            case 'processingTimeRange':
                return 'Processing Time';
            case 'applicationNumber':
                return 'Application No.';
            case 'department':
                return 'Department';
            case 'productName':
                return 'Product Name';
            case 'applicant':
                return 'Applicant';
            case 'documents':
                return 'Documents';
            default:
                return key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
        }
    }
    
    removeFilter(key, value) {
        // Get current filters
        const filters = this.getFilterValues();
        
        // Handle different filter types
        if (key in filters) {
            if (Array.isArray(filters[key])) {
                // For array filters, remove the specific value
                const index = filters[key].indexOf(value);
                if (index > -1) {
                    // Update the corresponding form control
                    if (key === 'approval') {
                        document.querySelectorAll('input[name="approval-status"]').forEach(cb => {
                            if (cb.value === value.replace(' ', '-')) {
                                cb.checked = false;
                            }
                        });
                    } else if (key === 'processor') {
                        document.querySelectorAll('input[name="processor"]').forEach(cb => {
                            if (cb.value === value) {
                                cb.checked = false;
                            }
                        });
                    } else if (key === 'documents') {
                        document.querySelectorAll(`input[name="doc-${value}"]`).forEach(cb => {
                            cb.checked = false;
                        });
                    }
                }
            } else if (typeof filters[key] === 'object') {
                // For object filters like text conditions or date ranges
                if (key === 'entryDateRange') {
                    document.getElementById('date-from').value = '';
                    document.getElementById('date-to').value = '';
                    // Reset quick date buttons
                    document.querySelectorAll('.quick-date-btn:not([data-target="completion"])').forEach(btn => {
                        btn.classList.remove('active');
                    });
                } else if (key === 'completionDateRange') {
                    document.getElementById('completion-from').value = '';
                    document.getElementById('completion-to').value = '';
                    // Reset quick date buttons
                    document.querySelectorAll('.quick-date-btn[data-target="completion"]').forEach(btn => {
                        btn.classList.remove('active');
                    });
                } else if (key === 'processingTimeRange') {
                    // Reset processing time range slider
                    document.getElementById('processing-time-min-range').value = 0;
                    document.getElementById('processing-time-max-range').value = 365;
                    document.getElementById('processing-time-min').textContent = '0 days';
                    document.getElementById('processing-time-max').textContent = '365+ days';
                    // Reset range slider colored area
                    const rangeSlider = document.querySelector('.range-slider');
                    if (rangeSlider) {
                        const rangeProgress = rangeSlider.querySelector('.range-progress');
                        if (rangeProgress) {
                            rangeProgress.style.left = '0%';
                            rangeProgress.style.right = '0%';
                        }
                    }
                } else {
                    // For text filters, find the group and reset it
                    const group = Array.from(document.querySelectorAll('.filter-group')).find(g => 
                        g.querySelector('h4')?.textContent.toLowerCase().includes(this.formatFilterLabel(key).toLowerCase()));
                    if (group) {
                        const textInput = group.querySelector('.filter-text-input');
                        if (textInput) textInput.value = '';
                    }
                }
            } else {
                // For simple values like location or relevance
                if (key === 'location') {
                    document.querySelector('input[name="location"][value="all"]').checked = true;
                } else if (key === 'relevance') {
                    document.querySelector('input[name="relevance"][value="all"]').checked = true;
                }
            }
        }
        
        // Apply the updated filters
        this.applyFilters();
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

        // Attach click handlers for document preview on the freshly rendered rows
        tbody.querySelectorAll('a.doc-icon[data-url]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const relUrl = link.getAttribute('data-url');
                if (relUrl) {
                    if (typeof window.showDocumentPreview === 'function') {
                        window.showDocumentPreview(relUrl);
                    } else {
                        const previewUrl = `/directory/document/?url=${encodeURIComponent(relUrl)}`;
                        window.open(previewUrl, '_blank');
                    }
                }
            });
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

        // Attach click handlers for card doc preview
        gridContainer.querySelectorAll('a.card-doc-icon[data-url]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const relUrl = link.getAttribute('data-url');
                if (relUrl) {
                    if (typeof window.showDocumentPreview === 'function') {
                        window.showDocumentPreview(relUrl);
                    } else {
                        const previewUrl = `/directory/document/?url=${encodeURIComponent(relUrl)}`;
                        window.open(previewUrl, '_blank');
                    }
                }
            });
        });
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
        const status = this.getItemStatus(item);
        row.className = `status-${status.replace(' ', '-')}`;
        
        row.innerHTML = `
            <td class="text-center">${item['Antrag-nummer'] || ''}</td>
            <td class="text-center">${this.formatEmptyValue(item['Teile-nummer'])}</td>
            <td class="text-center">${this.createStatusBadge(status)}</td>
            <td class="text-center">${this.createRelevanceDot(item['relevant für Luftfahrtteile'])}</td>
            <td>${this.formatEmptyValue(item['Benennung'])}</td>
            <td>${this.formatEmptyValue(item['Produktname / Normkurzbezeichnung'])}</td>
            <td>${item['Produktzulassungs-spezifikation'] || '-'}</td>
            <td>${this.formatDate(item['Eingang'])}</td>
            <td>${this.formatDate(item['Abschluss'])}</td>
            <td>${this.formatEmptyValue(item['Abteilung'])}</td>
            <td class="text-center">${this.createLocationBadge(item['Einsatzort'])}</td>
            <td>${this.formatEmptyValue(item['Antragsteller'])}</td>
            ${this.createDocumentCells(item)}
            <td class="text-center">${this.createProcessorBadge(item['Bearbeiter'])}</td>
            <td class="actions-cell">
                <a href="/directory/row/${this.getItemRowNumber(item)}/" class="action-btn" title="View"><i class="fas fa-eye"></i></a>
                <button class="action-btn" title="Edit"><i class="fas fa-edit"></i></button>
            </td>
        `;
        
        return row;
    }
    
    createCard(item) {
        const status = this.getItemStatus(item);
        const isAircraft = item['relevant für Luftfahrtteile'] && item['relevant für Luftfahrtteile'].toLowerCase() === 'ja';
        
        return `
            <div class="directory-card status-${status.replace(' ', '-')}">
                <div class="card-header">
                    <h3 class="card-application-no">${item['Antrag-nummer'] || 'N/A'}</h3>
                    <div class="card-status-container">
                        <div class="card-relevance-container">
                            <i class="fas fa-plane card-plane-icon"></i>
                            ${this.createRelevanceDot(item['relevant für Luftfahrtteile'])}
                        </div>
                        ${this.createStatusBadge(status)}
                    </div>
                </div>
                
                <div class="card-body">
                    <h4 class="card-title">${this.formatEmptyValue(item['Produktname / Normkurzbezeichnung'])}</h4>
                    <p class="card-description">${this.formatEmptyValue(item['Benennung'])}</p>
                    
                    <div class="card-details">
                        <div class="card-detail">
                            <span class="card-detail-label">Part No.</span>
                            <span class="card-detail-value">${this.formatEmptyValue(item['Teile-nummer'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Department</span>
                            <span class="card-detail-value">${this.formatEmptyValue(item['Abteilung'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Entry Date</span>
                            <span class="card-detail-value">${this.formatDate(item['Eingang'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Completion Date</span>
                            <span class="card-detail-value">${this.formatDate(item['Abschluss'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Applicant</span>
                            <span class="card-detail-value">${this.formatEmptyValue(item['Antragsteller'])}</span>
                        </div>
                        <div class="card-detail">
                            <span class="card-detail-label">Specification</span>
                            <span class="card-detail-value">${item['Produktzulassungs-spezifikation'] || '-'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-documents">
                    <div class="card-documents-title">Documents</div>
                    <div class="card-documents-grid">
                        ${this.createCardDocuments(item)}
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="card-meta">
                        <div class="card-location">${this.createLocationBadge(item['Einsatzort'])}</div>
                        <div class="card-processor">${this.createProcessorBadge(item['Bearbeiter'])}</div>
                    </div>
                    <div class="card-actions">
                        <a href="/directory/row/${this.getItemRowNumber(item)}/" class="card-action-btn" title="View">
                            <i class="fas fa-eye"></i>
                        </a>
                        <button class="card-action-btn" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    createCardDocuments(item) {
        const documentColumns = [
            { key: 'Antrag', label: 'App', icon: 'fas fa-file-pdf' },
            { key: 'Datenblatt', label: 'Data', icon: 'fas fa-file-excel' },
            { key: 'Produkt-zulassung', label: 'Appr', icon: 'fas fa-certificate' },
            { key: 'SDB MSDS', label: 'SDB', icon: 'fas fa-file-medical' },
            { key: 'Gefährdungsprüfungeurteilung', label: 'ChemScan', icon: 'fas fa-shield-alt' },
            { key: 'Gefährdungsprüfung', label: 'Hazard', icon: 'fas fa-shield-alt' },
            { key: 'Sonstiges', label: 'Misc', icon: 'fas fa-file-alt' },
            { key: 'Schriftverkehr', label: 'Corr', icon: 'fas fa-envelope' },
            { key: 'Änd. Historie', label: 'Hist', icon: 'fas fa-history' }
        ];
        
        return documentColumns.map(({ key, label, icon }) => {
            const doc = item[key];
            const hasDoc = doc && (doc.url || doc.display_text);
            const count = hasDoc && Array.isArray(doc) ? doc.length : (hasDoc ? 1 : 0);
            const countBadge = count > 1 ? `<span class="card-doc-count">${count}</span>` : '';
            
            return `
                <div class="card-doc-item">
                    <a href="#" class="card-doc-icon ${hasDoc ? 'available' : 'unavailable'}" 
                       title="${key}" data-url="${hasDoc ? (doc.url || '') : ''}">
                        <i class="${icon}"></i>
                    </a>
                    ${countBadge}
                    <span class="card-doc-label">${label}</span>
                </div>
            `;
        }).join('');
    }
    
    createStatusBadge(status) {
        const statusMap = {
            'approved': 'Approved',
            'first use': 'First Use',
            'rejected': 'Rejected',
            'processing': 'Processing'
        };
        
        return `<span class="status-badge ${status.replace(' ', '-')}">${statusMap[status] || status}</span>`;
    }
    
    createRelevanceDot(relevant) {
        const isAircraft = relevant && relevant.toLowerCase() === 'ja';
        const className = isAircraft ? 'aircraft' : 'not-aircraft';
        const title = isAircraft ? 'Aircraft Relevant' : 'Not Aircraft Relevant';
        return `<span class="status-dot ${className}" title="${title}"></span>`;
    }
    
    createLocationBadge(location) {
        if (!location) return '-';
        const className = location.toLowerCase();
        return `<span class="location-badge ${className}">${location}</span>`;
    }
    
    createProcessorBadge(processor) {
        if (!processor) return '<span class="processor-badge applicant">Applicant</span>';
        
        const processorMap = {
            'UUB': 'uub',
            'UWS': 'uws',
            'HSE': 'hse',
            'LAB': 'lab'
        };
        
        const className = processorMap[processor] || 'applicant';
        const displayName = processor || 'Applicant';
        
        return `<span class="processor-badge ${className}">${displayName}</span>`;
    }
    
    createDocumentCells(item) {
        const documentColumns = [
            'Antrag', 'Datenblatt', 'Produkt-zulassung', 'SDB MSDS',
            'Gefährdungsprüfungeurteilung', 'Gefährdungsprüfung', 'Sonstiges',
            'Schriftverkehr', 'Änd. Historie'
        ];
        
        const iconMap = {
            'Antrag': 'fas fa-file-pdf',
            'Datenblatt': 'fas fa-file-excel',
            'Produkt-zulassung': 'fas fa-certificate',
            'SDB MSDS': 'fas fa-file-medical',
            'Gefährdungsprüfungeurteilung': 'fas fa-shield-alt',
            'Gefährdungsprüfung': 'fas fa-shield-alt',
            'Sonstiges': 'fas fa-file-alt',
            'Schriftverkehr': 'fas fa-envelope',
            'Änd. Historie': 'fas fa-history'
        };
        
        return documentColumns.map(column => {
            const doc = item[column];
            if (doc && (doc.url || doc.display_text)) {
                const count = Array.isArray(doc) ? doc.length : 1;
                const countBadge = count > 1 ? `<span class="doc-count">${count}</span>` : '';
                const url = doc.url || '#';
                return `
                    <td class="document-cell attachment-column">
                        <div class="doc-container">
                            <a href="#" class="doc-icon" title="${column}" data-url="${doc ? (doc.url || '') : ''}">
                                <i class="${iconMap[column] || 'fas fa-file'}"></i>
                            </a>
                            ${countBadge}
                        </div>
                    </td>
                `;
            } else {
                return `<td class="document-cell attachment-column"><span class="doc-dash" title="No ${column}">-</span></td>`;
            }
        }).join('');
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
    
    updateStats() {
        const totalEntries = this.data.length;
        
        // Count by status
        const approvedCount = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'approved';
        }).length;
        
        const firstUseCount = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'first use';
        }).length;
        
        const processingCount = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'processing';
        }).length;
        
        const rejectedCount = this.data.filter(item => {
            const status = this.getItemStatus(item);
            return status === 'rejected';
        }).length;
        
        const aircraftCount = this.data.filter(item => {
            const relevanceValue = item['relevant für Luftfahrtteile'];
            return relevanceValue && relevanceValue.toLowerCase() === 'ja';
        }).length;
        
        // Update stat cards by class/position
        // [0] = Live status (don't update)
        // [1] = All
        // [2] = Approved 
        // [3] = First Use
        // [4] = Processing
        // [5] = Rejected
        // [6] = Aircraft Relevant
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 7) {
            // Skip [0] - that's the live status indicator
            statCards[1].querySelector('.stat-value').textContent = totalEntries.toLocaleString();
            statCards[2].querySelector('.stat-value').textContent = approvedCount.toLocaleString();
            statCards[3].querySelector('.stat-value').textContent = firstUseCount.toLocaleString();
            statCards[4].querySelector('.stat-value').textContent = processingCount.toLocaleString();
            statCards[5].querySelector('.stat-value').textContent = rejectedCount.toLocaleString();
            statCards[6].querySelector('.stat-value').textContent = aircraftCount.toLocaleString();
        }
    }

    async startStatusPolling() {
        // Poll status every 10 seconds
        this.statusPollingInterval = setInterval(() => {
            this.updateLiveStatus();
        }, 10000);
        
        // Initial status check
        this.updateLiveStatus();
    }

    async updateLiveStatus() {
        try {
            const response = await fetch('/directory/status/');
            if (response.ok) {
                const status = await response.json();
                this.updateLiveStatusIndicator(status);
            }
        } catch (error) {
            console.warn('Failed to fetch live status:', error);
        }
    }

    updateLiveStatusIndicator(status) {
        const liveCard = document.querySelector('.stat-card-live');
        if (!liveCard) return;

        const statusValue = liveCard.querySelector('.stat-value');
        const statusDot = liveCard.querySelector('.stat-live-dot');
        const statusLabel = liveCard.querySelector('.stat-label');
        
        if (!statusValue || !statusDot) return;

        // Update text and dot color based on status
        const statusText = statusValue.childNodes[2]; // Text node after icon
        if (statusText) {
            statusText.textContent = ` ${status.status_text}`;
        }

        // Update dot color
        statusDot.className = `fas fa-circle stat-live-dot ${status.status_class}`;
        
        // Update card class for styling
        liveCard.className = `stat-card stat-card-live ${status.status_class}`;

        // Update label with last update time
        if (statusLabel && status.last_update) {
            const lastUpdateDate = new Date(status.last_update * 1000);
            const timeString = lastUpdateDate.toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit'
            });
            statusLabel.textContent = `Last: ${timeString}`;
        } else if (statusLabel) {
            statusLabel.textContent = 'Online Status';
        }

        // Add title with more info
        const nextUpdate = status.next_update_in ? `Next update in ${Math.round(status.next_update_in / 60)} minutes` : '';
        const lastUpdate = status.time_since_update ? `Last updated ${Math.round(status.time_since_update / 60)} minutes ago` : '';
        const hasCompressed = status.has_compressed ? 'Compressed version available' : 'No compressed version';
        liveCard.title = [nextUpdate, lastUpdate, hasCompressed].filter(Boolean).join(' • ');
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
        
        // Count approval status filters
        const approvalCheckboxes = document.querySelectorAll('input[name="approval-status"]');
        let hasApprovalFilter = false;
        approvalCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasApprovalFilter = true;
            }
        });
        if (hasApprovalFilter) count++;
        
        // Count relevance filter
        const relevanceRadios = document.querySelectorAll('input[name="relevance"]');
        let hasRelevanceFilter = false;
        relevanceRadios.forEach(radio => {
            if (radio.checked && radio.value !== 'all') {
                hasRelevanceFilter = true;
            }
        });
        if (hasRelevanceFilter) count++;
        
        // Count location filter
        const locationRadios = document.querySelectorAll('input[name="location"]');
        let hasLocationFilter = false;
        locationRadios.forEach(radio => {
            if (radio.checked && radio.value !== 'all') {
                hasLocationFilter = true;
            }
        });
        if (hasLocationFilter) count++;
        
        // Count processor filters
        const processorCheckboxes = document.querySelectorAll('input[name="processor"]');
        let hasProcessorFilter = false;
        processorCheckboxes.forEach(cb => {
            if (cb.checked && cb.value !== 'all') {
                hasProcessorFilter = true;
            }
        });
        if (hasProcessorFilter) count++;
        
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
        
        // Count completion date filters
        const completionFromInput = document.getElementById('completion-from');
        const completionToInput = document.getElementById('completion-to');
        if ((completionFromInput && completionFromInput.value) || (completionToInput && completionToInput.value)) {
            count++;
        }
        
        // Count processing time range filter
        const minTimeRange = document.getElementById('processing-time-min-range');
        const maxTimeRange = document.getElementById('processing-time-max-range');
        if (minTimeRange && maxTimeRange && 
            (parseInt(minTimeRange.value) > 0 || parseInt(maxTimeRange.value) < 365)) {
            count++;
        }
        
        // Count document availability filters
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

    getItemRowNumber(item) {
        // Find the item's position in the search results (current view order)
        // This matches what the user sees in the table/grid
        const index = this.searchResults.findIndex(dataItem => 
            dataItem['Antrag-nummer'] === item['Antrag-nummer']
        );
        return index + 1; // Convert to 1-indexed
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
    new DirectoryManager();
});

// Lightweight modal preview utility shared by directory pages
(function() {
    function ensureStyles() {
        if (document.getElementById('doc-preview-styles')) return;
        const style = document.createElement('style');
        style.id = 'doc-preview-styles';
        style.textContent = `
        .doc-preview-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:10000;display:flex;align-items:center;justify-content:center}
        .doc-preview-modal{background:#fff;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.2);width:min(90vw,1100px);height:min(90vh,800px);display:flex;flex-direction:column;overflow:hidden}
        .doc-preview-header{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid #e8e8ed;background:#f5f5f7}
        .doc-preview-title{font-size:14px;font-weight:600;color:#1d1d1f;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
        .doc-preview-actions{display:flex;gap:8px}
        .doc-preview-actions a,.doc-preview-actions button{padding:6px 10px;border-radius:6px;border:1px solid #d2d2d7;background:#fff;cursor:pointer;font-size:12px;color:#1d1d1f;display:inline-flex;align-items:center;gap:6px}
        .doc-preview-actions a.primary{background:#0071e3;border-color:#0071e3;color:#fff}
        .doc-preview-iframe{flex:1;border:0;width:100%;height:100%;background:#fff}

        /* Dark mode for modal */
        .dark-mode .doc-preview-backdrop{background:rgba(0,0,0,0.6)}
        .dark-mode .doc-preview-modal{background:#1f1f1f;box-shadow:0 10px 30px rgba(0,0,0,.6)}
        .dark-mode .doc-preview-header{background:#222;border-bottom-color:#333}
        .dark-mode .doc-preview-title{color:#eaeaea}
        .dark-mode .doc-preview-actions a,.dark-mode .doc-preview-actions button{background:#2a2a2a;border-color:#444;color:#eaeaea}
        .dark-mode .doc-preview-actions a.primary{background:#0a84ff;border-color:#0a84ff;color:#fff}
        .dark-mode .doc-preview-actions a:hover,.dark-mode .doc-preview-actions button:hover{background:#333}
        .dark-mode .doc-preview-iframe{background:#111}
        `;
        document.head.appendChild(style);
    }

    function createModal() {
        ensureStyles();
        const backdrop = document.createElement('div');
        backdrop.className = 'doc-preview-backdrop';
        const modal = document.createElement('div');
        modal.className = 'doc-preview-modal';

        const header = document.createElement('div');
        header.className = 'doc-preview-header';
        const title = document.createElement('div');
        title.className = 'doc-preview-title';
        const actions = document.createElement('div');
        actions.className = 'doc-preview-actions';
        const openBtn = document.createElement('a');
        openBtn.innerHTML = '<i class="fas fa-external-link-alt"></i><span>Open in new tab</span>';
        openBtn.target = '_blank';
        openBtn.rel = 'noopener';
        const openFileBtn = document.createElement('a');
        openFileBtn.innerHTML = '<i class="fas fa-folder-open"></i><span>Open via file://</span>';
        openFileBtn.target = '_blank';
        openFileBtn.rel = 'noopener';
        const copyBtn = document.createElement('button');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i><span>Copy file URL</span>';
        const downloadBtn = document.createElement('a');
        downloadBtn.innerHTML = '<i class="fas fa-download"></i><span>Download</span>';
        downloadBtn.className = 'primary';
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '<i class="fas fa-times"></i><span>Close</span>';
        actions.appendChild(openBtn);
        actions.appendChild(openFileBtn);
        actions.appendChild(copyBtn);
        actions.appendChild(downloadBtn);
        actions.appendChild(closeBtn);
        header.appendChild(title);
        header.appendChild(actions);

        const iframe = document.createElement('iframe');
        iframe.className = 'doc-preview-iframe';
        modal.appendChild(header);
        modal.appendChild(iframe);
        backdrop.appendChild(modal);

        function cleanup() { document.body.removeChild(backdrop); }
        backdrop.addEventListener('click', (e) => { if (e.target === backdrop) cleanup(); });
        closeBtn.addEventListener('click', cleanup);

        return { backdrop, iframe, title, openBtn, openFileBtn, copyBtn, downloadBtn };
    }

    function buildFileUrlFromRelative(relUrl) {
        const server = 'deberdna-c010a';
        const basePath = 'GlobalDE/DocumentManagement/Ofs/obl/Dokumentenservice/TeileundStoffe';
        const cleaned = String(relUrl || '')
            .replace(/^[.\\/]+/g, '')
            .replace(/\\\\/g, '/')
            .replace(/\\/g, '/')
            .replace(/^\//, '');
        return `file://${server}/${basePath}/${cleaned}`;
    }

    window.showDocumentPreview = function(relUrl) {
        const { backdrop, iframe, title, openBtn, openFileBtn, copyBtn, downloadBtn } = createModal();
        const url = `/directory/document/?url=${encodeURIComponent(relUrl)}`;
        iframe.src = url;
        const filename = relUrl.split('\\').pop().split('/').pop();
        title.textContent = filename || 'Document preview';
        openBtn.href = url;
        const fileUrl = buildFileUrlFromRelative(relUrl);
        openFileBtn.href = fileUrl;
        copyBtn.addEventListener('click', async () => {
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(fileUrl);
                } else {
                    const tmp = document.createElement('input');
                    tmp.value = fileUrl;
                    document.body.appendChild(tmp);
                    tmp.select();
                    document.execCommand('copy');
                    document.body.removeChild(tmp);
                }
                const original = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i><span>Copied!</span>';
                copyBtn.disabled = true;
                setTimeout(() => { copyBtn.innerHTML = original; copyBtn.disabled = false; }, 1200);
            } catch (e) {
                const original = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Copy failed</span>';
                setTimeout(() => { copyBtn.innerHTML = original; }, 1500);
            }
        });
        downloadBtn.href = `${url}&download=1`;
        downloadBtn.setAttribute('download', filename || 'document');
        document.body.appendChild(backdrop);
    };

    // Generic delegation for detail page attachment links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a.doc-link[data-url]');
        if (link && link.dataset.url) {
            e.preventDefault();
            window.showDocumentPreview(link.dataset.url);
        }
    });
})();
