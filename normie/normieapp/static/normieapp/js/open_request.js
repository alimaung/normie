document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('open-request-form');
    const alertContainer = document.getElementById('alert-container');
    
    // Form validation rules - comprehensive rules for all fields except 2d, 4, 8, 7
    const validationRules = {
        'field_2a': { required: true, message: 'Antragsteller Name ist erforderlich' },
        'field_2b': { required: true, message: 'Antragserstellungsdatum ist erforderlich' },
        'field_2c': { required: true, message: 'Antragsteller Abteilung ist erforderlich' },
        'field_3': { required: true, message: 'Benennung ist erforderlich' },
        'field_5': { required: true, message: 'Kennzeichnung des Bedarfs muss ausgewählt werden' },
        'field_6': { required: true, message: 'Kennzeichnung des Produkts muss ausgewählt werden' },
        'field_9': { required: true, message: 'Hersteller ist erforderlich' },
        'field_10': { required: true, message: 'Verwendungszweck ist erforderlich' },
        'field_11': { required: true, message: 'Triebwerksprogramm ist erforderlich' },
        'field_12a': { required: false, message: 'Einsatzort / Standort ist erforderlich' },
        'field_12b': { required: false, message: 'Bereich Teamleiter*innen ist erforderlich' },
        'field_13': { required: true, message: 'Erzeugnisrelevanz muss ausgewählt werden' },
        'field_14': { required: true, message: 'Nutzung muss ausgewählt werden' },
        'field_15a': { required: false, message: 'Lagerhaltig Auswahl ist erforderlich' },
        'field_15b': { required: false, message: 'SAP Bestellung Auswahl ist erforderlich' },
        'field_16': { required: false, message: 'Basismengeneinheit SAP ist erforderlich' },
        'field_17a': { required: false, message: 'Monatlicher Bedarf ist erforderlich' },
        'field_17b': { required: false, message: 'Häufigkeit der Anwendung ist erforderlich' },
        'field_17c': { required: false, message: 'Menge pro Anwendung ist erforderlich' },
        'field_18a': { required: false, message: 'EU-Sicherheitsdatenblatt Auswahl ist erforderlich' },
        'field_18b': { required: false, message: 'Technisches Datenblatt Auswahl ist erforderlich' },
        'field_18c': { required: false, message: 'Gefährdungsbeurteilung Auswahl ist erforderlich' },
        'field_18d': { required: false, message: 'Produktzulassung Auswahl ist erforderlich' },
        'field_18e': { required: false, message: 'Produktzulassung Spezifikation ist erforderlich' },
        'field_19': { required: false, message: 'Erläuterungen sind erforderlich' },
        'field_20': { required: false, message: 'Verweis auf vergangene Anträge ist erforderlich' },
        'field_21': { required: false, message: 'Wunschtermin für Produkteinsatz ist erforderlich' }
    };
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Clear error styling
    function clearError(element) {
        element.classList.remove('field-error');
        
        // Handle different container types
        const container = element.closest('.column-field') || element.closest('.field-input') || element.parentElement;
        if (container) {
            container.classList.remove('has-error');
            const errorMsg = container.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.style.display = 'none';
            }
        }
        
        // Handle radio groups specifically
        if (element.type === 'radio') {
            const radioContainer = element.closest('.radio-group');
            if (radioContainer) {
                radioContainer.classList.remove('radio-group-error');
            }
        }
    }
    
    // Show error styling
    function showError(element, message) {
        element.classList.add('field-error');
        
        // Handle different container types
        const container = element.closest('.column-field') || element.closest('.field-input') || element.parentElement;
        if (container) {
            container.classList.add('has-error');
            const errorMsg = container.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.querySelector('.error-text').textContent = message;
                errorMsg.style.display = 'flex';
            }
        }
        
        // Handle radio groups specifically
        if (element.type === 'radio') {
            const radioContainer = element.closest('.radio-group');
            if (radioContainer) {
                radioContainer.classList.add('radio-group-error');
            }
        }
        
        // Scroll to first error if not visible
        const rect = element.getBoundingClientRect();
        if (rect.top < 0 || rect.bottom > window.innerHeight) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    // Show error for radio group
    function showRadioGroupError(fieldName, message) {
        const radioGroup = form.querySelectorAll(`[name="${fieldName}"]`);
        if (radioGroup.length > 0) {
            const firstRadio = radioGroup[0];
            const container = firstRadio.closest('.column-field-input') || firstRadio.closest('.field-input');
            if (container) {
                const errorMsg = container.querySelector('.error-message');
                if (errorMsg) {
                    errorMsg.querySelector('.error-text').textContent = message;
                    errorMsg.style.display = 'flex';
                }
                
                const radioContainer = firstRadio.closest('.radio-group');
                if (radioContainer) {
                    radioContainer.classList.add('radio-group-error');
                }
            }
        }
    }
    
    // Clear error for radio group
    function clearRadioGroupError(fieldName) {
        const radioGroup = form.querySelectorAll(`[name="${fieldName}"]`);
        if (radioGroup.length > 0) {
            const firstRadio = radioGroup[0];
            const container = firstRadio.closest('.column-field-input') || firstRadio.closest('.field-input');
            if (container) {
                const errorMsg = container.querySelector('.error-message');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
                
                const radioContainer = firstRadio.closest('.radio-group');
                if (radioContainer) {
                    radioContainer.classList.remove('radio-group-error');
                }
            }
        }
    }
    
    // Validate single field
    function validateField(fieldName, value) {
        const rule = validationRules[fieldName];
        if (!rule) return true;
        
        // Required field check
        if (rule.required && (!value || value.trim() === '')) {
            return { valid: false, message: rule.message };
        }
        
        // Date format validation for date fields
        if (fieldName === 'field_2b' || fieldName === 'field_21') {
            if (value && !value.match(/^\d{1,2}\.\d{1,2}\.\d{4}$/)) {
                return { valid: false, message: 'Bitte verwenden Sie das Format DD.MM.YYYY' };
            }
        }
        
        return { valid: true };
    }
    
    // Validate form
    function validateForm() {
        let isValid = true;
        const formData = new FormData(form);
        let firstErrorElement = null;
        
        // Clear all previous errors
        form.querySelectorAll('.field-error').forEach(element => {
            clearError(element);
        });
        form.querySelectorAll('.radio-group-error').forEach(element => {
            element.classList.remove('radio-group-error');
        });
        form.querySelectorAll('.has-error').forEach(element => {
            element.classList.remove('has-error');
        });
        form.querySelectorAll('.error-message').forEach(element => {
            element.style.display = 'none';
        });
        
        // Validate each field
        for (const [fieldName, rule] of Object.entries(validationRules)) {
            let value = formData.get(fieldName);
            const element = form.querySelector(`[name="${fieldName}"]`);
            
            if (!element) continue;
            
            // Handle radio buttons
            if (element.type === 'radio') {
                const radioGroup = form.querySelectorAll(`[name="${fieldName}"]`);
                const checked = Array.from(radioGroup).some(radio => radio.checked);
                value = checked ? formData.get(fieldName) : '';
            }
            
            const validation = validateField(fieldName, value);
            if (!validation.valid) {
                // For radio buttons, apply error to the group
                if (element.type === 'radio') {
                    showRadioGroupError(fieldName, validation.message);
                } else {
                    showError(element, validation.message);
                }
                isValid = false;
                
                // Remember first error for scrolling
                if (!firstErrorElement) {
                    firstErrorElement = element;
                }
            }
        }
        
        // Scroll to first error
        if (!isValid && firstErrorElement) {
            setTimeout(() => {
                firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
        
        return isValid;
    }
    
    // Real-time validation
    form.addEventListener('input', function(e) {
        const fieldName = e.target.name;
        if (validationRules[fieldName]) {
            clearError(e.target);
        }
    });
    
    form.addEventListener('change', function(e) {
        const fieldName = e.target.name;
        if (validationRules[fieldName]) {
            if (e.target.type === 'radio') {
                clearRadioGroupError(fieldName);
            } else {
                clearError(e.target);
            }
        }
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            showAlert('danger', 'Bitte korrigieren Sie die markierten Fehler und versuchen Sie es erneut.');
            return;
        }
        
        // Collect form data
        const formData = new FormData(form);
        const requestData = {};
        
        // Convert FormData to object
        for (const [key, value] of formData.entries()) {
            requestData[key] = value;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Wird eingereicht...';
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        
        // Send data to server
        fetch('{% url "open_request" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', `Antrag erfolgreich eingereicht! Antragsnummer: ${data.antragnummer || 'Wird generiert'}`);
                // Reset form
                form.reset();
                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                showAlert('danger', data.message || 'Fehler beim Einreichen des Antrags. Bitte versuchen Sie es erneut.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Fehler beim Einreichen des Antrags. Bitte versuchen Sie es erneut.');
        })
        .finally(() => {
            // Reset button state
            submitBtn.innerHTML = originalContent;
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
        });
    });
    
    function showAlert(type, message) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
                ${message}
            </div>
        `;
        
        // Auto-hide success alerts after 8 seconds
        if (type === 'success') {
            setTimeout(() => {
                alertContainer.innerHTML = '';
            }, 8000);
        }
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
    
    // Set today's date as default for field 2b (Antragserstellungsdatum)
    const dateField = form.querySelector('[name="field_2b"]');
    if (dateField) {
        const today = new Date();
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const year = today.getFullYear();
        dateField.value = `${day}.${month}.${year}`;
    }
});