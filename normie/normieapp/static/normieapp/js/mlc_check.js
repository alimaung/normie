// MLC Check JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchQuery');
    const searchBtn = document.getElementById('searchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSection = document.getElementById('loadingSection');
    const resultsTable = document.getElementById('resultsTable');
    const resultsBody = document.getElementById('resultsBody');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsCount = document.getElementById('resultsCount');
    const noResults = document.getElementById('noResults');
    
    // SDS Upload elements
    const sdsDropArea = document.getElementById('sds-drop-area');
    const sdsFileInput = document.getElementById('sds-file');
    const sdsFileInfo = document.getElementById('sds-file-info');
    const sdsFileName = document.getElementById('sds-file-name');
    const sdsFileSize = document.getElementById('sds-file-size');
    const removeSdsFile = document.getElementById('remove-sds-file');
    const sdsSubmitBtn = document.getElementById('sds-submit-btn');
    const sdsUploadForm = document.getElementById('sds-upload-form');
    const sdsProcessingSection = document.getElementById('sdsProcessingSection');
    const sdsResultsSection = document.getElementById('sdsResultsSection');
    
    // Initialize
    init();
    
    function init() {
        // Check if elements exist
        console.log('SDS Drop Area:', sdsDropArea);
        console.log('SDS File Input:', sdsFileInput);
        
        // Manual search event listeners
        searchBtn.addEventListener('click', performManualSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performManualSearch();
            }
        });
        
        // Auto-search as user types (with debounce)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            if (this.value.trim().length >= 2) {
                searchTimeout = setTimeout(() => {
                    performManualSearch();
                }, 500);
            } else if (this.value.trim().length === 0) {
                hideResults();
            }
        });
        
        // SDS Upload event listeners
        if (sdsDropArea && sdsFileInput) {
            initializeUploadEvents();
        } else {
            console.error('Upload elements not found!');
        }
    }
    
    function initializeUploadEvents() {
        console.log('Initializing upload events...');
        
        // Drag and drop events
        sdsDropArea.addEventListener('dragover', handleDragOver);
        sdsDropArea.addEventListener('dragleave', handleDragLeave);
        sdsDropArea.addEventListener('drop', handleDrop);
        
        // Click event for upload area - simplified and reliable
        sdsDropArea.addEventListener('click', function(e) {
            console.log('Upload area clicked');
            e.preventDefault();
            e.stopPropagation();
            
            if (sdsFileInput) {
                console.log('Triggering file input click');
                try {
                    sdsFileInput.click();
                    console.log('File input click triggered successfully');
                } catch (error) {
                    console.error('Error triggering file input:', error);
                    // Fallback: create a new file input
                    const newInput = document.createElement('input');
                    newInput.type = 'file';
                    newInput.accept = '.pdf';
                    newInput.style.display = 'none';
                    document.body.appendChild(newInput);
                    newInput.addEventListener('change', function(e) {
                        if (e.target.files[0]) {
                            // Copy the file to the original input
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(e.target.files[0]);
                            sdsFileInput.files = dataTransfer.files;
                            handleFileSelect(e);
                        }
                        document.body.removeChild(newInput);
                    });
                    newInput.click();
                }
            } else {
                console.error('File input not found');
            }
        });
        
        // File input change - prevent double triggering
        sdsFileInput.addEventListener('change', function(e) {
            console.log('File input changed:', e.target.files);
            e.stopPropagation();
            handleFileSelect(e);
        });
        
        // Remove file
        if (removeSdsFile) {
            removeSdsFile.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                clearSelectedFile();
            });
        }
        
        // Form submission
        if (sdsUploadForm) {
            sdsUploadForm.addEventListener('submit', handleSdsUpload);
        }
    }
    
    function handleDragOver(e) {
        e.preventDefault();
        sdsDropArea.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        sdsDropArea.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        e.preventDefault();
        sdsDropArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                setSelectedFile(file);
            }
        }
    }
    
    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file && validateFile(file)) {
            setSelectedFile(file);
        }
    }
    
    function validateFile(file) {
        // Check file type
        if (file.type !== 'application/pdf') {
            showMessage('Please select a PDF file', 'error');
            return false;
        }
        
        // Check file size (limit to 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showMessage('File size must be less than 10MB', 'error');
            return false;
        }
        
        return true;
    }
    
    function setSelectedFile(file) {
        try {
            // For drag & drop files, we need to create a new FileList and assign it
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            sdsFileInput.files = dataTransfer.files;
            
            console.log('File set:', file.name, 'Files in input:', sdsFileInput.files.length);
            
            // Update UI
            sdsFileName.textContent = file.name;
            sdsFileSize.textContent = formatFileSize(file.size);
            sdsFileInfo.style.display = 'flex';
            sdsSubmitBtn.disabled = false;
            
            // Hide upload area and show file info
            sdsDropArea.style.display = 'none';
        } catch (error) {
            console.error('Error setting file:', error);
            // Fallback: just update UI without setting files
            sdsFileName.textContent = file.name;
            sdsFileSize.textContent = formatFileSize(file.size);
            sdsFileInfo.style.display = 'flex';
            sdsSubmitBtn.disabled = false;
            sdsDropArea.style.display = 'none';
            
            // Store file reference for manual form creation
            window.selectedFile = file;
        }
    }
    
    function clearSelectedFile() {
        sdsFileInput.value = '';
        sdsFileInfo.style.display = 'none';
        sdsSubmitBtn.disabled = true;
        sdsDropArea.style.display = 'block';
        
        // Clear stored file reference
        window.selectedFile = null;
        
        // Hide processing and results sections
        sdsProcessingSection.style.display = 'none';
        sdsResultsSection.style.display = 'none';
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function handleSdsUpload(e) {
        e.preventDefault();
        
        // Check if file is selected (either through input or stored reference)
        const hasInputFile = sdsFileInput.files && sdsFileInput.files.length > 0;
        const hasStoredFile = window.selectedFile;
        
        if (!hasInputFile && !hasStoredFile) {
            showMessage('Please select a file first', 'warning');
            return;
        }
        
        // Create form data manually if needed
        const formData = new FormData(sdsUploadForm);
        
        // If we have a stored file but not in input, add it manually
        if (!hasInputFile && hasStoredFile) {
            formData.set('sds_file', window.selectedFile);
        }
        
        console.log('Submitting form with file:', hasInputFile ? sdsFileInput.files[0].name : window.selectedFile?.name);
        
        // Show processing section
        showSdsProcessing();
        
        // Start SDS processing
        processSdsDocument(formData);
    }
    
    function showSdsProcessing() {
        sdsProcessingSection.style.display = 'block';
        sdsSubmitBtn.disabled = true;
        sdsSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        // Hide other sections
        hideResults();
        sdsResultsSection.style.display = 'none';
        
        // Reset all steps
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed', 'error');
        });
        
        // Smooth scroll to processing section
        sdsProcessingSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function processSdsDocument(formData) {
        // Step 1: SDS Detection
        updateProcessingStep('step-detection', 'active', 'Analyzing document structure...');
        
        fetch('/mlc-check/process-sds/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                handleSdsProcessingSuccess(data);
            } else {
                handleSdsProcessingError(data.error || 'Processing failed');
            }
        })
        .catch(error => {
            console.error('SDS processing error:', error);
            handleSdsProcessingError('An error occurred during processing. Please try again.');
        });
    }
    
    function updateProcessingStep(stepId, status, message = '') {
        const step = document.getElementById(stepId);
        if (step) {
            // Remove existing status classes
            step.classList.remove('active', 'completed', 'error');
            
            // Add new status
            step.classList.add(status);
            
            // Update status message
            const statusEl = step.querySelector('.step-status');
            if (statusEl && message) {
                statusEl.textContent = message;
            }
            
            // Update icon based on status
            const icon = step.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-spin');
                if (status === 'active') {
                    icon.classList.add('fa-spin');
                } else if (status === 'completed') {
                    icon.className = 'fas fa-check';
                } else if (status === 'error') {
                    icon.className = 'fas fa-times';
                }
            }
        }
    }
    
    function handleSdsProcessingSuccess(data) {
        // Complete step 1
        updateProcessingStep('step-detection', 'completed', 
            `${data.sds_detection.confidence_level} confidence (${data.sds_detection.total_score}/100)`);
        
        // Step 2: Extraction
        updateProcessingStep('step-extraction', 'active', 'Extracting chemical identifiers...');
        
        setTimeout(() => {
            updateProcessingStep('step-extraction', 'completed', 
                `Found ${data.extraction_result.unique_cas_count} CAS, ${data.extraction_result.unique_ec_count} EC numbers`);
            
            // Step 3: Search
            updateProcessingStep('step-search', 'active', 'Searching MLC database...');
            
            setTimeout(() => {
                updateProcessingStep('step-search', 'completed', 
                    `${data.search_results.length} substances found in MLC database`);
                
                // Show results
                displaySdsResults(data);
                
                // Re-enable form
                sdsSubmitBtn.disabled = false;
                sdsSubmitBtn.innerHTML = '<i class="fas fa-upload"></i> Process SDS Document';
            }, 500);
        }, 1000);
    }
    
    function handleSdsProcessingError(error) {
        // Mark current active step as error
        const activeStep = document.querySelector('.step.active');
        if (activeStep) {
            updateProcessingStep(activeStep.id, 'error', error);
        }
        
        showMessage(error, 'error');
        
        // Re-enable form
        sdsSubmitBtn.disabled = false;
        sdsSubmitBtn.innerHTML = '<i class="fas fa-upload"></i> Process SDS Document';
    }
    
    function displaySdsResults(data) {
        // Show SDS results section
        sdsResultsSection.style.display = 'block';
        
        // Make CAS and EC numbers unique
        const uniqueCasNumbers = removeDuplicateIdentifiers(data.extraction_result.cas_numbers);
        const uniqueEcNumbers = removeDuplicateIdentifiers(data.extraction_result.ec_numbers);
        
        // Update summary stats with unique counts
        const summaryStats = document.getElementById('sdsSummaryStats');
        summaryStats.innerHTML = `
            <div class="stat-item">
                <div class="stat-icon"><i class="fas fa-file-alt"></i></div>
                <div class="stat-content">
                    <div class="stat-value">${data.sds_detection.total_score}</div>
                    <div class="stat-label">SDS Score /100</div>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-icon"><i class="fas fa-flask"></i></div>
                <div class="stat-content">
                    <div class="stat-value">${uniqueCasNumbers.length}</div>
                    <div class="stat-label">Unique CAS Numbers</div>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-icon"><i class="fas fa-tag"></i></div>
                <div class="stat-content">
                    <div class="stat-value">${uniqueEcNumbers.length}</div>
                    <div class="stat-label">Unique EC Numbers</div>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-icon"><i class="fas fa-database"></i></div>
                <div class="stat-content">
                    <div class="stat-value">${data.search_results.length}</div>
                    <div class="stat-label">MLC Matches</div>
                </div>
            </div>
        `;
        
        // Create a map of found MLC results for quick lookup
        const mlcResultsMap = new Map();
        data.search_results.forEach(result => {
            if (result.CAS_No) {
                mlcResultsMap.set(result.CAS_No, result);
            }
            if (result.EC_No) {
                mlcResultsMap.set(result.EC_No, result);
            }
            if (result.Substance_Name) {
                mlcResultsMap.set(result.Substance_Name.toLowerCase(), result);
            }
        });
        
        // Display extracted identifiers with MLC status
        const extractedIdentifiers = document.getElementById('extractedIdentifiers');
        let identifiersHtml = '';
        
        // CAS Numbers section - always show, even if empty
        identifiersHtml += `
            <div class="identifier-section">
                <h5><i class="fas fa-flask"></i> CAS Numbers (${uniqueCasNumbers.length} found)</h5>
        `;
        
        if (uniqueCasNumbers.length > 0) {
            identifiersHtml += `<div class="identifier-list">`;
            uniqueCasNumbers.forEach(cas => {
                const mlcResult = mlcResultsMap.get(cas.number);
                const hasHit = !!mlcResult;
                const statusClass = hasHit ? 'has-mlc-hit' : 'no-mlc-hit';
                const statusIcon = hasHit ? '✓' : '✗';
                const statusTitle = hasHit ? `MLC Hit: ${mlcResult.MLC132_Status_by_ROW}` : 'No MLC match found';
                
                identifiersHtml += `
                    <div class="identifier-tag clickable ${statusClass}" 
                         onclick="searchIdentifier('${cas.number}', 'cas')"
                         title="${statusTitle}">
                        <span class="status-indicator">${statusIcon}</span>
                        ${cas.number}
                        ${cas.substance_name ? ` (${cas.substance_name})` : ''}
                    </div>
                `;
            });
            identifiersHtml += `</div>`;
        } else {
            identifiersHtml += `<div class="no-identifiers">No CAS numbers found in the document</div>`;
        }
        identifiersHtml += `</div>`;
        
        // EC Numbers section - always show, even if empty
        identifiersHtml += `
            <div class="identifier-section">
                <h5><i class="fas fa-tag"></i> EC Numbers (${uniqueEcNumbers.length} found)</h5>
        `;
        
        if (uniqueEcNumbers.length > 0) {
            identifiersHtml += `<div class="identifier-list">`;
            uniqueEcNumbers.forEach(ec => {
                const mlcResult = mlcResultsMap.get(ec.number);
                const hasHit = !!mlcResult;
                const statusClass = hasHit ? 'has-mlc-hit' : 'no-mlc-hit';
                const statusIcon = hasHit ? '✓' : '✗';
                const statusTitle = hasHit ? `MLC Hit: ${mlcResult.MLC132_Status_by_ROW}` : 'No MLC match found';
                
                identifiersHtml += `
                    <div class="identifier-tag clickable ${statusClass}" 
                         onclick="searchIdentifier('${ec.number}', 'ec')"
                         title="${statusTitle}">
                        <span class="status-indicator">${statusIcon}</span>
                        ${ec.number}
                        ${ec.substance_name ? ` (${ec.substance_name})` : ''}
                    </div>
                `;
            });
            identifiersHtml += `</div>`;
        } else {
            identifiersHtml += `<div class="no-identifiers">No EC numbers found in the document</div>`;
        }
        identifiersHtml += `</div>`;
        
        // Substances section
        if (data.extraction_result.detected_substances.length > 0) {
            const uniqueSubstances = [...new Set(data.extraction_result.detected_substances)];
            identifiersHtml += `
                <div class="identifier-section">
                    <h5><i class="fas fa-atom"></i> Substances (${uniqueSubstances.length} found)</h5>
                    <div class="identifier-list">
                        ${uniqueSubstances.map(substance => {
                            const mlcResult = mlcResultsMap.get(substance.toLowerCase());
                            const hasHit = !!mlcResult;
                            const statusClass = hasHit ? 'has-mlc-hit' : 'no-mlc-hit';
                            const statusIcon = hasHit ? '✓' : '✗';
                            const statusTitle = hasHit ? `MLC Hit: ${mlcResult.MLC132_Status_by_ROW}` : 'No MLC match found';
                            
                            return `
                                <div class="identifier-tag clickable ${statusClass}" 
                                     onclick="searchIdentifier('${substance}', 'substance')"
                                     title="${statusTitle}">
                                    <span class="status-indicator">${statusIcon}</span>
                                    ${substance}
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        
        extractedIdentifiers.innerHTML = identifiersHtml;
        
        // Always display comprehensive results - including those with no MLC hits
        displayComprehensiveResults(uniqueCasNumbers, uniqueEcNumbers, data.search_results, mlcResultsMap);
        
        // Smooth scroll to results
        sdsResultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function removeDuplicateIdentifiers(identifiers) {
        const seen = new Set();
        return identifiers.filter(identifier => {
            if (seen.has(identifier.number)) {
                return false;
            }
            seen.add(identifier.number);
            return true;
        });
    }
    
    function displayComprehensiveResults(casNumbers, ecNumbers, mlcResults, mlcResultsMap) {
        // Create comprehensive results that include ALL extracted identifiers
        const allResults = [];
        
        // Add all CAS numbers with their MLC status
        casNumbers.forEach(cas => {
            const mlcResult = mlcResultsMap.get(cas.number);
            if (mlcResult) {
                // Has MLC hit - add the actual result
                allResults.push(mlcResult);
            } else {
                // No MLC hit - create a placeholder result
                allResults.push({
                    CAS_No: cas.number,
                    EC_No: '-',
                    Substance_Name: cas.substance_name || 'Unknown',
                    MLC132_Entry: 'Not found in MLC database',
                    MLC132_Status_by_ROW: 'No regulatory information',
                    MLC132_Details: 'This substance was not found in the MLC database',
                    'Policy Specific Requirements': 'No specific requirements available',
                    _no_mlc_hit: true // Flag to style differently
                });
            }
        });
        
        // Add EC numbers that don't have corresponding CAS entries
        ecNumbers.forEach(ec => {
            const mlcResult = mlcResultsMap.get(ec.number);
            // Only add if we don't already have this via CAS
            const alreadyAdded = allResults.some(r => r.EC_No === ec.number);
            if (!alreadyAdded) {
                if (mlcResult) {
                    allResults.push(mlcResult);
                } else {
                    allResults.push({
                        CAS_No: '-',
                        EC_No: ec.number,
                        Substance_Name: ec.substance_name || 'Unknown',
                        MLC132_Entry: 'Not found in MLC database',
                        MLC132_Status_by_ROW: 'No regulatory information',
                        MLC132_Details: 'This substance was not found in the MLC database',
                        'Policy Specific Requirements': 'No specific requirements available',
                        _no_mlc_hit: true
                    });
                }
            }
        });
        
        if (allResults.length > 0) {
            displayResults(allResults, 'SDS extraction (including non-matches)');
        } else {
            showNoResults();
        }
    }
    
    function searchIdentifier(identifier, type) {
        // Fill in the search input with the selected identifier
        searchInput.value = identifier;
        
        // Set appropriate filter
        const checkboxes = document.querySelectorAll('input[name="searchFields"]');
        checkboxes.forEach(cb => {
            cb.checked = cb.value === type;
        });
        
        // Perform search
        performManualSearch();
        
        // Scroll to search section
        document.querySelector('.search-section').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function performManualSearch() {
        const query = searchInput.value.trim();
        
        if (!query) {
            showMessage('Please enter a search term', 'warning');
            return;
        }
        
        if (query.length < 2) {
            showMessage('Please enter at least 2 characters', 'warning');
            return;
        }
        
        // Get selected search fields
        const searchFields = getSelectedSearchFields();
        if (searchFields.length === 0) {
            showMessage('Please select at least one search field', 'warning');
            return;
        }
        
        showLoading();
        
        // Make AJAX request to search
        fetch('/mlc-check/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                query: query,
                search_fields: searchFields
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                displayResults(data.results, query);
            } else {
                showMessage(data.error || 'Search failed', 'error');
                hideResults();
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Search error:', error);
            showMessage('An error occurred during search. Please try again.', 'error');
            hideResults();
        });
    }
    
    function getSelectedSearchFields() {
        const checkboxes = document.querySelectorAll('input[name="searchFields"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }
    
    function displayResults(results, query) {
        if (!results || results.length === 0) {
            showNoResults();
            return;
        }
        
        // Update results header
        resultsTitle.textContent = `Search Results for "${query}"`;
        resultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;
        
        // Clear existing results
        resultsBody.innerHTML = '';
        
        // Add results to table
        results.forEach(result => {
            const row = createResultRow(result);
            resultsBody.appendChild(row);
        });
        
        // Show results
        showResults();
    }
    
    function createResultRow(result) {
        const row = document.createElement('tr');
        
        // Add special styling for non-MLC hits
        if (result._no_mlc_hit) {
            row.classList.add('no-mlc-hit-row');
        }
        
        // Create cells
        const casCell = document.createElement('td');
        casCell.textContent = result.CAS_No || '-';
        
        const ecCell = document.createElement('td');
        ecCell.textContent = result.EC_No || '-';
        
        const nameCell = document.createElement('td');
        nameCell.textContent = result.Substance_Name || '-';
        
        const entryCell = document.createElement('td');
        entryCell.textContent = result.MLC132_Entry || '-';
        
        const statusCell = document.createElement('td');
        const status = result.MLC132_Status_by_ROW || '-';
        statusCell.innerHTML = formatStatus(status, result._no_mlc_hit);
        
        const detailsCell = document.createElement('td');
        detailsCell.textContent = result.MLC132_Details || '-';
        
        const policyCell = document.createElement('td');
        policyCell.textContent = result['Policy Specific Requirements'] || '-';
        
        // Append cells to row
        row.appendChild(casCell);
        row.appendChild(ecCell);
        row.appendChild(nameCell);
        row.appendChild(entryCell);
        row.appendChild(statusCell);
        row.appendChild(detailsCell);
        row.appendChild(policyCell);
        
        return row;
    }
    
    function formatStatus(status, isNoHit = false) {
        if (!status || status === '-') {
            return '-';
        }
        
        if (isNoHit) {
            return `<span class="status-no-info">${status}</span>`;
        }
        
        const statusLower = status.toLowerCase();
        let className = '';
        
        if (statusLower.includes('prohibited')) {
            className = 'status-prohibited';
        } else if (statusLower.includes('restricted') || statusLower.includes('limited')) {
            className = 'status-restricted';
        } else {
            className = 'status-allowed';
        }
        
        return `<span class="${className}">${status}</span>`;
    }
    
    function showResults() {
        resultsSection.style.display = 'block';
        resultsTable.style.display = 'table';
        noResults.style.display = 'none';
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function showNoResults() {
        resultsSection.style.display = 'block';
        resultsTable.style.display = 'none';
        noResults.style.display = 'block';
        
        // Update results count
        resultsCount.textContent = '0 results';
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    function hideResults() {
        resultsSection.style.display = 'none';
    }
    
    function showLoading() {
        loadingSection.style.display = 'block';
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
        hideResults();
    }
    
    function hideLoading() {
        loadingSection.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
    }
    
    function showMessage(message, type = 'info') {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${type}`;
        
        const iconClass = {
            'error': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation-circle',
            'success': 'fa-check-circle',
            'info': 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        messageEl.innerHTML = `
            <i class="fas ${iconClass}"></i>
            <div class="message-text">${message}</div>
            <button class="message-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to messages container or create one
        let messagesContainer = document.querySelector('.messages');
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages';
            document.body.appendChild(messagesContainer);
        }
        
        messagesContainer.appendChild(messageEl);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageEl.parentElement) {
                messageEl.remove();
            }
        }, 5000);
    }
    
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Try to get from form
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
    
    // Export functions for testing
    window.MLCCheck = {
        performManualSearch,
        displayResults,
        showMessage,
        searchIdentifier
    };
}); 