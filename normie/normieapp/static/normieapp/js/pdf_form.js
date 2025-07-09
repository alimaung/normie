
document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('save-form');
    const viewButton = document.getElementById('view-form');
    const downloadButton = document.getElementById('download-form');
    const form = document.getElementById('pdf-edit-form');
    const alertContainer = document.getElementById('alert-container');
    
    // Track if form has been saved
    let formSaved = false;
    
    // Initialize combined field functionality
    initializeCombinedFields();
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize dynamic button state updates
    initializeDynamicButtonStates();
    
    // Track form changes to disable download when unsaved changes exist
    function trackFormChanges() {
        // Include fields outside the form element (like fields 1 and 51 in key-fields-header)
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // Only track inputs that have a field ID (form fields)
            if (input.dataset.fieldId) {
                input.addEventListener('change', function() {
                    formSaved = false;
                    updateDownloadButton();
                });
                input.addEventListener('input', function() {
                    formSaved = false;
                    updateDownloadButton();
                });
            }
        });
    }
    
    function updateDownloadButton() {
        if (formSaved) {
            viewButton.disabled = false;
            viewButton.classList.remove('btn-disabled');
            viewButton.title = '';
            
            downloadButton.disabled = false;
            downloadButton.classList.remove('btn-disabled');
            downloadButton.title = '';
        } else {
            viewButton.disabled = true;
            viewButton.classList.add('btn-disabled');
            viewButton.title = 'Please save the form first before viewing';
            
            downloadButton.disabled = true;
            downloadButton.classList.add('btn-disabled');
            downloadButton.title = 'Please save the form first before downloading';
        }
    }
    
    // Initialize form change tracking
    trackFormChanges();
    
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            // Collect all field values
            const formData = {};
            
            // Handle text inputs and textareas (search entire document to include key fields)
            const textInputs = document.querySelectorAll('input[type="text"], textarea');
            textInputs.forEach(input => {
                const fieldId = input.dataset.fieldId;
                if (fieldId) {
                    formData[fieldId] = input.value;
                }
            });
            
            // Handle checkboxes (including combined checkboxes)
            const checkboxInputs = document.querySelectorAll('input[type="checkbox"]');
            checkboxInputs.forEach(checkbox => {
                const fieldId = checkbox.dataset.fieldId;
                if (fieldId) {
                    // Try to get the dynamic label text
                    const label = checkbox.parentElement.querySelector('label');
                    let labelText = label ? label.textContent.trim() : '';
                    
                    // If the label is generic (Aktivieren, Ja, Nein), use binary values
                    if (!labelText || labelText === 'Aktivieren' || labelText === 'Ja' || labelText === 'Nein') {
                        formData[fieldId] = checkbox.checked ? 'Ja' : 'Nein';
                    } else {
                        // Use the dynamic label text as the value when checked
                        formData[fieldId] = checkbox.checked ? labelText : 'Nein';
                    }
                }
            });
            
            // Handle radio buttons
            const radioInputs = document.querySelectorAll('input[type="radio"]:checked');
            radioInputs.forEach(radio => {
                const fieldId = radio.dataset.fieldId;
                if (fieldId) {
                    formData[fieldId] = radio.value; // This will be the German display value
                }
            });
            
            // Send the data to the server
            fetch('{% url "pdf_save" form_id=form_id %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    formSaved = true;
                    updateDownloadButton();
                    showAlert('success', data.message || '{% trans "Form saved successfully! You can now view or download the PDF." %}');
                } else {
                    showAlert('danger', data.message || '{% trans "An error occurred while saving the form." %}');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', '{% trans "An error occurred while saving the form." %}');
            });
        });
    }
    
    // View button functionality
    if (viewButton) {
        viewButton.addEventListener('click', function() {
            if (!formSaved) {
                showAlert('danger', '{% trans "Please save the form before viewing." %}');
                return;
            }
            
            // Open PDF in new tab/window for viewing (not downloading)
            window.open('{% url "pdf_download" form_id=form_id %}?view=1', '_blank');
        });
    }
    
    // Download button functionality
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            if (!formSaved) {
                showAlert('danger', '{% trans "Please save the form before downloading." %}');
                return;
            }
            
            // Trigger download
            window.location.href = '{% url "pdf_download" form_id=form_id %}';
        });
    }
    
    function initializeCombinedFields() {
        // Handle combined checkbox + input fields
        const combinedCheckboxes = form.querySelectorAll('.combined-checkbox');
        combinedCheckboxes.forEach(checkbox => {
            const targetInputId = checkbox.dataset.targetInput;
            if (targetInputId) {
                const targetInput = document.querySelector(`input[data-field-id="${targetInputId}"]`);
                if (targetInput) {
                    // Set initial state
                    targetInput.style.display = checkbox.checked ? 'block' : 'none';
                    
                    // Add event listener
                    checkbox.addEventListener('change', function() {
                        targetInput.style.display = this.checked ? 'block' : 'none';
                        if (!this.checked) {
                            targetInput.value = ''; // Clear input when disabled
                        } else {
                            targetInput.focus(); // Focus the input when enabled
                        }
                    });
                }
            }
        });
        
        // Handle file upload checkboxes
        const fileUploadCheckboxes = form.querySelectorAll('.file-upload-checkbox');
        fileUploadCheckboxes.forEach(checkbox => {
            const fieldId = checkbox.dataset.fieldId;
            const uploadContainer = form.querySelector(`.file-upload-container[data-field-id="${fieldId}"]`);
            
            if (uploadContainer) {
                // Set initial state
                if (checkbox.checked) {
                    uploadContainer.classList.add('active');
                } else {
                    uploadContainer.classList.remove('active');
                }
                
                // Add event listener
                checkbox.addEventListener('change', function() {
                    if (this.checked) {
                        uploadContainer.classList.add('active');
                    } else {
                        uploadContainer.classList.remove('active');
                        // Clear any selected file
                        removeFile(fieldId);
                    }
                });
            }
        });
        
        // Handle radio activation fields
        const radioActivationInputs = form.querySelectorAll('input[type="radio"][data-target-input]');
        radioActivationInputs.forEach(radio => {
            const targetInputId = radio.dataset.targetInput;
            const activationValue = radio.dataset.activationValue;
            
            if (targetInputId) {
                const targetInput = document.querySelector(`input[data-field-id="${targetInputId}"]`);
                if (targetInput) {
                    radio.addEventListener('change', function() {
                        if (this.checked && this.value === activationValue) {
                            targetInput.style.display = 'block';
                            targetInput.focus();
                        } else if (this.checked) {
                            targetInput.style.display = 'none';
                            targetInput.value = ''; // Clear when not the activation value
                        }
                    });
                }
            }
        });
        
        // Also handle radio groups to hide input when other options are selected
        const radioGroups = {};
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            if (radio.dataset.fieldId) {
                const groupName = radio.name;
                if (!radioGroups[groupName]) {
                    radioGroups[groupName] = [];
                }
                radioGroups[groupName].push(radio);
            }
        });
        
        // Set up listeners for each radio group
        Object.values(radioGroups).forEach(group => {
            const hasActivation = group.some(radio => radio.dataset.targetInput);
            if (hasActivation) {
                group.forEach(radio => {
                    radio.addEventListener('change', function() {
                        if (this.checked) {
                            // Find all activation inputs in this group and hide them
                            group.forEach(otherRadio => {
                                const otherTargetInputId = otherRadio.dataset.targetInput;
                                if (otherTargetInputId && otherRadio !== this) {
                                    const otherTargetInput = document.querySelector(`input[data-field-id="${otherTargetInputId}"]`);
                                    if (otherTargetInput) {
                                        otherTargetInput.style.display = 'none';
                                        otherTargetInput.value = '';
                                    }
                                }
                            });
                        }
                    });
                });
            }
        });
    }
    
    function initializeDatePickers() {
        // Add date picker functionality
        const datePickerButtons = form.querySelectorAll('.date-picker-toggle');
        datePickerButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const targetFieldId = this.dataset.target;
                const targetInput = document.querySelector(`input[data-field-id="${targetFieldId}"]`);
                if (targetInput && !targetInput.disabled) {
                    // Create a temporary date input to trigger native date picker
                    const tempDateInput = document.createElement('input');
                    tempDateInput.type = 'date';
                    tempDateInput.style.position = 'fixed';
                    tempDateInput.style.top = '50%';
                    tempDateInput.style.left = '50%';
                    tempDateInput.style.zIndex = '9999';
                    tempDateInput.style.opacity = '0';
                    tempDateInput.style.pointerEvents = 'none';
                    document.body.appendChild(tempDateInput);
                    
                    // Convert existing value to date format if present
                    const currentValue = targetInput.value;
                    if (currentValue && currentValue.match(/^\d{1,2}\.\d{1,2}\.\d{4}$/)) {
                        const parts = currentValue.split('.');
                        const isoDate = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
                        tempDateInput.value = isoDate;
                    }
                    
                    tempDateInput.addEventListener('change', function() {
                        if (this.value) {
                            // Convert ISO date to German format
                            const date = new Date(this.value);
                            const day = String(date.getDate()).padStart(2, '0');
                            const month = String(date.getMonth() + 1).padStart(2, '0');
                            const year = date.getFullYear();
                            targetInput.value = `${day}.${month}.${year}`;
                        }
                        if (document.body.contains(this)) {
                            document.body.removeChild(this);
                        }
                    });
                    
                    tempDateInput.addEventListener('blur', function() {
                        setTimeout(() => {
                            if (document.body.contains(this)) {
                                document.body.removeChild(this);
                            }
                        }, 100);
                    });
                    
                    // Trigger the date picker
                    setTimeout(() => {
                        tempDateInput.focus();
                        tempDateInput.click();
                        if (tempDateInput.showPicker) {
                            tempDateInput.showPicker();
                        }
                    }, 10);
                }
            });
        });
        
        // Also add double-click functionality to date fields
        const dateFields = form.querySelectorAll('.date-field');
        dateFields.forEach(field => {
            field.addEventListener('dblclick', function() {
                if (!this.disabled) {
                    const button = this.parentElement.querySelector('.date-picker-toggle');
                    if (button) {
                        button.click();
                    }
                }
            });
        });
    }
    
    function initializeDynamicButtonStates() {
        // Update radio button states dynamically (include fields outside form)
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            if (radio.dataset.fieldId) {
                radio.addEventListener('change', function() {
                    updateButtonStateDisplay(this.name, this.value);
                });
            }
        });
        
        // Update checkbox states dynamically and set initial state (include fields outside form)
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:not(.combined-checkbox)');
        checkboxes.forEach(checkbox => {
            if (checkbox.dataset.fieldId) {
                // Set initial state for activation checkboxes
                updateCheckboxStateDisplay(checkbox);
                
                // Add change listener
                checkbox.addEventListener('change', function() {
                    updateCheckboxStateDisplay(this);
                });
            }
        });
        
        // Also handle combined checkboxes and file upload checkboxes
        const combinedCheckboxes = document.querySelectorAll('input[type="checkbox"].combined-checkbox, input[type="checkbox"].file-upload-checkbox');
        combinedCheckboxes.forEach(checkbox => {
            if (checkbox.dataset.fieldId) {
                // Set initial state
                updateCheckboxStateDisplay(checkbox);
                
                // Add change listener
                checkbox.addEventListener('change', function() {
                    updateCheckboxStateDisplay(this);
                });
            }
        });
    }
    
    function updateButtonStateDisplay(fieldName, selectedValue) {
        // Find all radio buttons in this group (search entire document)
        const radioGroup = document.querySelectorAll(`input[type="radio"][name="${fieldName}"]`);
        
        // Update any status display elements for this field
        radioGroup.forEach(radio => {
            const fieldId = radio.dataset.fieldId;
            if (fieldId) {
                // Find any status indicator for this field (could be added later)
                const statusElement = document.querySelector(`[data-status-for="${fieldId}"]`);
                if (statusElement) {
                    statusElement.textContent = radio.checked ? selectedValue : '';
                }
            }
        });
    }
    
    function updateCheckboxStateDisplay(checkbox) {
        const fieldId = checkbox.dataset.fieldId;
        if (fieldId) {
            // Get the label element
            const label = checkbox.parentElement.querySelector('label.dynamic-label');
            if (label) {
                let labelText = label.textContent.trim();
                
                // Always update activation checkboxes and standard checkboxes to show Ja/Nein
                // Only preserve meaningful custom text that isn't generic
                if (labelText === 'Ja' || labelText === 'Nein' || labelText === '' || labelText === 'Aktivieren' || 
                    checkbox.classList.contains('combined-checkbox') || checkbox.classList.contains('file-upload-checkbox')) {
                    label.textContent = checkbox.checked ? 'Ja' : 'Nein';
                }
            }
            
            // Find any status indicator for this field
            const statusElement = document.querySelector(`[data-status-for="${fieldId}"]`);
            if (statusElement) {
                statusElement.textContent = checkbox.checked ? 'Ja' : 'Nein';
            }
        }
    }
    
    function showAlert(type, message) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
                ${message}
            </div>
        `;
        
        // Auto-hide the alert after 5 seconds
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
    
    // Initialize file upload functionality
    initializeFileUploads();
});

// File upload functionality
const fileStorage = {}; // Store files for each field

function initializeFileUploads() {
    console.log('Initializing file uploads...');
    
    // Initialize file storage
    const fileInputs = document.querySelectorAll('.file-upload-input');
    fileInputs.forEach(input => {
        const fieldId = input.dataset.fieldId;
        fileStorage[fieldId] = [];
    });
    
    // Handle file input changes
    fileInputs.forEach(input => {
        console.log('Setting up file input for field:', input.dataset.fieldId);
        input.addEventListener('change', function(e) {
            const fieldId = this.dataset.fieldId;
            const files = Array.from(e.target.files);
            
            console.log('Files selected:', files.length, 'for field:', fieldId);
            
            files.forEach(file => {
                if (fileStorage[fieldId].length < 3) {
                    addFileToGrid(fieldId, file);
                }
            });
            
            // Clear the input to allow selecting the same file again
            this.value = '';
        });
    });
    
    // Handle drag and drop
    const uploadAreas = document.querySelectorAll('.file-upload-area');
    uploadAreas.forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.backgroundColor = 'rgba(26, 115, 232, 0.08)';
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '';
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '';
            
            const fieldId = this.closest('.file-upload-container').dataset.fieldId;
            const files = Array.from(e.dataTransfer.files);
            
            files.forEach(file => {
                if (fileStorage[fieldId].length < 3) {
                    addFileToGrid(fieldId, file);
                }
            });
        });
    });
    
    // Handle checkbox changes for file upload fields
    const fileUploadCheckboxes = document.querySelectorAll('.file-upload-checkbox');
    fileUploadCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const fieldId = this.dataset.fieldId;
            const container = document.querySelector(`.file-upload-container[data-field-id="${fieldId}"]`);
            
            if (this.checked) {
                container.style.display = 'block';
                container.classList.add('active');
            } else {
                container.style.display = 'none';
                container.classList.remove('active');
                // Clear all files
                clearAllFiles(fieldId);
            }
        });
    });
}

function addFileToGrid(fieldId, file) {
    console.log('Adding file to grid:', file.name, 'for field:', fieldId);
    
    // Add file to storage
    const fileId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    fileStorage[fieldId].push({ id: fileId, file: file });
    
    const grid = document.getElementById(`files-grid-${fieldId}`);
    if (!grid) {
        console.error('Grid not found for field:', fieldId);
        return;
    }
    
    // Create file slot
    const fileSlot = document.createElement('div');
    fileSlot.className = 'file-slot';
    fileSlot.id = `file-slot-${fileId}`;
    
    // Determine icon based on file type
    let iconClass = 'fas fa-file';
    if (file.type.includes('pdf')) {
        iconClass = 'fas fa-file-pdf';
    } else if (file.type.includes('word') || file.name.endsWith('.doc') || file.name.endsWith('.docx')) {
        iconClass = 'fas fa-file-word';
    }
    
    fileSlot.innerHTML = `
        <div class="file-selected">
            <div class="file-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button type="button" class="file-remove" onclick="removeFileFromGrid('${fieldId}', '${fileId}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Insert before upload slot
    const uploadSlot = document.getElementById(`upload-slot-${fieldId}`);
    grid.insertBefore(fileSlot, uploadSlot);
    
    updateGridLayout(fieldId);
    console.log('File added to grid');
}

function removeFileFromGrid(fieldId, fileId) {
    // Remove from storage
    fileStorage[fieldId] = fileStorage[fieldId].filter(f => f.id !== fileId);
    
    // Remove from DOM
    const fileSlot = document.getElementById(`file-slot-${fileId}`);
    if (fileSlot) {
        fileSlot.remove();
    }
    
    updateGridLayout(fieldId);
}

function updateGridLayout(fieldId) {
    const grid = document.getElementById(`files-grid-${fieldId}`);
    const fileCount = fileStorage[fieldId].length;
    const totalSlots = fileCount + 1; // +1 for upload slot
    
    // Update all slots - let flexbox handle equal distribution
    const slots = grid.querySelectorAll('.file-slot');
    slots.forEach(slot => {
        // Remove any custom width styling to let flex: 1 work
        slot.style.flexBasis = '';
        slot.style.maxWidth = '';
        slot.style.minWidth = '';
        
        // Add narrow class if slot is too small
        if (totalSlots >= 4) {
            slot.classList.add('narrow');
        } else {
            slot.classList.remove('narrow');
        }
    });
    
    // Hide upload slot if max files reached
    const uploadSlot = document.getElementById(`upload-slot-${fieldId}`);
    if (fileCount >= 3) {
        uploadSlot.style.display = 'none';
    } else {
        uploadSlot.style.display = 'block';
    }
}

function clearAllFiles(fieldId) {
    // Clear file storage
    fileStorage[fieldId] = [];
    
    // Remove all file slots except upload slot
    const grid = document.getElementById(`files-grid-${fieldId}`);
    const fileSlots = grid.querySelectorAll('.file-slot:not(.upload-slot)');
    fileSlots.forEach(slot => slot.remove());
    
    // Reset upload slot - let flexbox handle the sizing
    const uploadSlot = document.getElementById(`upload-slot-${fieldId}`);
    uploadSlot.style.display = 'block';
    uploadSlot.style.flexBasis = '';
    uploadSlot.style.maxWidth = '';
    uploadSlot.classList.remove('narrow');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}