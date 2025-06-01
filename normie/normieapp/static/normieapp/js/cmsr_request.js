/**
 * CMSR Request Form JavaScript
 * Handles multi-step form navigation, validation, and user interactions
 */

$(document).ready(function() {
    let currentSection = 0;
    const sections = ['applicant', 'product', 'usage', 'documentation', 'review'];
    const totalSections = sections.length;

    // Initialize form
    initializeForm();

    // Event listeners
    $('#next-section').on('click', nextSection);
    $('#prev-section').on('click', prevSection);
    $('#save-draft').on('click', saveDraft);
    $('#preview-form').on('click', previewForm);
    $('#cmsr-form').on('submit', submitForm);

    // Progress step navigation
    $('.progress-step').on('click', function() {
        const targetSection = $(this).data('section');
        const targetIndex = sections.indexOf(targetSection);
        if (targetIndex !== -1) {
            goToSection(targetIndex);
        }
    });

    // Document upload
    $('#add-document').on('click', addDocument);

    function initializeForm() {
        // Show only the first section
        $('.form-section').removeClass('active');
        $('#section-' + sections[0]).addClass('active');
        
        // Update progress indicator
        updateProgressIndicator();
        
        // Update navigation buttons
        updateNavigationButtons();
        
        // Populate review section if we're on the last step
        if (currentSection === totalSections - 1) {
            populateReviewSection();
        }
    }

    function nextSection() {
        if (validateCurrentSection()) {
            if (currentSection < totalSections - 1) {
                currentSection++;
                showSection(currentSection);
            }
        }
    }

    function prevSection() {
        if (currentSection > 0) {
            currentSection--;
            showSection(currentSection);
        }
    }

    function goToSection(index) {
        if (index >= 0 && index < totalSections) {
            currentSection = index;
            showSection(currentSection);
        }
    }

    function showSection(index) {
        // Hide all sections
        $('.form-section').removeClass('active');
        
        // Show target section
        $('#section-' + sections[index]).addClass('active');
        
        // Update progress indicator
        updateProgressIndicator();
        
        // Update navigation buttons
        updateNavigationButtons();
        
        // Populate review section if we're on the last step
        if (index === totalSections - 1) {
            populateReviewSection();
        }
        
        // Scroll to top
        $('html, body').animate({
            scrollTop: $('.form-section.active').offset().top - 100
        }, 300);
    }

    function updateProgressIndicator() {
        $('.progress-step').each(function(index) {
            const $step = $(this);
            if (index < currentSection) {
                $step.addClass('completed').removeClass('active');
            } else if (index === currentSection) {
                $step.addClass('active').removeClass('completed');
            } else {
                $step.removeClass('active completed');
            }
        });
    }

    function updateNavigationButtons() {
        const $prevBtn = $('#prev-section');
        const $nextBtn = $('#next-section');
        
        // Show/hide previous button
        if (currentSection === 0) {
            $prevBtn.hide();
        } else {
            $prevBtn.show();
        }
        
        // Update next button text and behavior
        if (currentSection === totalSections - 1) {
            $nextBtn.hide();
        } else {
            $nextBtn.show().html('Next <i class="fas fa-arrow-right"></i>');
        }
    }

    function validateCurrentSection() {
        const currentSectionElement = $('#section-' + sections[currentSection]);
        let isValid = true;
        
        // Clear previous errors
        currentSectionElement.find('.field-errors').remove();
        currentSectionElement.find('.form-control').removeClass('error');
        
        // Validate required fields in current section
        currentSectionElement.find('input[required], select[required], textarea[required]').each(function() {
            const $field = $(this);
            const value = $field.val().trim();
            
            if (!value) {
                showFieldError($field, 'This field is required.');
                isValid = false;
            }
        });
        
        // Section-specific validation
        switch (sections[currentSection]) {
            case 'product':
                isValid = validateProductSection() && isValid;
                break;
            case 'usage':
                isValid = validateUsageSection() && isValid;
                break;
            case 'documentation':
                isValid = validateDocumentationSection() && isValid;
                break;
        }
        
        return isValid;
    }

    function validateProductSection() {
        let isValid = true;
        
        // Validate product name
        const productName = $('#id_product_name').val().trim();
        if (productName.length < 3) {
            showFieldError($('#id_product_name'), 'Product name must be at least 3 characters long.');
            isValid = false;
        }
        
        return isValid;
    }

    function validateUsageSection() {
        let isValid = true;
        
        // Validate usage purpose
        const usagePurpose = $('#id_usage_purpose').val().trim();
        if (usagePurpose.length < 10) {
            showFieldError($('#id_usage_purpose'), 'Please provide a detailed usage purpose (at least 10 characters).');
            isValid = false;
        }
        
        return isValid;
    }

    function validateDocumentationSection() {
        let isValid = true;
        
        // Check if at least one document type is selected
        const hasAnyDocument = $('#id_has_safety_datasheet').is(':checked') ||
                              $('#id_has_technical_datasheet').is(':checked') ||
                              $('#id_has_risk_assessment').is(':checked') ||
                              $('#id_has_product_approval').is(':checked');
        
        if (!hasAnyDocument) {
            showMessage('Please select at least one document type.', 'warning');
            isValid = false;
        }
        
        return isValid;
    }

    function showFieldError($field, message) {
        $field.addClass('error');
        const $errorDiv = $('<div class="field-errors">' + message + '</div>');
        $field.closest('.form-group').append($errorDiv);
    }

    function populateReviewSection() {
        const reviewContent = $('#review-content');
        reviewContent.empty();
        
        // Applicant Information
        addReviewSection(reviewContent, 'Applicant Information', {
            'Department': $('#id_applicant_department').val(),
            'Phone': $('#id_applicant_phone').val()
        });
        
        // Product Information
        addReviewSection(reviewContent, 'Product Information', {
            'Product Name': $('#id_product_name').val(),
            'Foreign Part Number': $('#id_foreign_part_number').val(),
            'Need Classification': $('#id_need_classification option:selected').text(),
            'Product Classification': $('#id_product_classification option:selected').text(),
            'REACh Code': $('#id_reach_code').val(),
            'Supplier': $('#id_supplier').val(),
            'Manufacturer': $('#id_manufacturer').val()
        });
        
        // Usage Information
        addReviewSection(reviewContent, 'Usage Information', {
            'Usage Purpose': $('#id_usage_purpose').val(),
            'Engine Program': $('#id_engine_program').val(),
            'Location/Site': $('#id_location_site').val(),
            'Product Relevant': $('#id_product_relevant').is(':checked') ? 'Yes' : 'No',
            'Usage Duration': $('#id_usage_duration option:selected').text(),
            'Monthly Demand': $('#id_monthly_demand').val(),
            'Usage Frequency': $('#id_usage_frequency').val()
        });
        
        // Documentation
        const documentTypes = [];
        if ($('#id_has_safety_datasheet').is(':checked')) documentTypes.push('Safety Datasheet');
        if ($('#id_has_technical_datasheet').is(':checked')) documentTypes.push('Technical Datasheet');
        if ($('#id_has_risk_assessment').is(':checked')) documentTypes.push('Risk Assessment');
        if ($('#id_has_product_approval').is(':checked')) documentTypes.push('Product Approval');
        
        addReviewSection(reviewContent, 'Documentation', {
            'Document Types': documentTypes.join(', ') || 'None selected',
            'Additional Explanations': $('#id_additional_explanations').val(),
            'Reference Past Applications': $('#id_reference_past_applications').val(),
            'Desired Implementation Date': $('#id_desired_implementation_date').val()
        });
    }

    function addReviewSection(container, title, data) {
        const section = $('<div class="review-section"></div>');
        section.append('<h5>' + title + '</h5>');
        
        const list = $('<dl class="review-list"></dl>');
        
        Object.keys(data).forEach(key => {
            const value = data[key];
            if (value && value.trim() !== '') {
                list.append('<dt>' + key + '</dt>');
                list.append('<dd>' + value + '</dd>');
            }
        });
        
        section.append(list);
        container.append(section);
    }

    function saveDraft() {
        showMessage('Draft saved successfully!', 'success');
        // TODO: Implement actual draft saving
    }

    function previewForm() {
        // Open preview in new window/modal
        showMessage('Preview functionality coming soon!', 'info');
        // TODO: Implement preview functionality
    }

    function addDocument() {
        const documentType = $('#id_document_type').val();
        const file = $('#id_file')[0].files[0];
        const description = $('#id_description').val();
        
        if (!file) {
            showMessage('Please select a file to upload.', 'warning');
            return;
        }
        
        // Add document to the list (visual feedback)
        const documentItem = $(`
            <div class="document-item">
                <div class="document-info">
                    <i class="fas fa-file"></i>
                    <span class="document-name">${file.name}</span>
                    <span class="document-type">(${$('#id_document_type option:selected').text()})</span>
                </div>
                <button type="button" class="btn btn-sm btn-outline remove-document">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `);
        
        $('#uploaded-documents').append(documentItem);
        
        // Clear form
        $('#id_file').val('');
        $('#id_description').val('');
        
        showMessage('Document added successfully!', 'success');
    }

    // Remove document
    $(document).on('click', '.remove-document', function() {
        $(this).closest('.document-item').remove();
        showMessage('Document removed.', 'info');
    });

    function submitForm(e) {
        e.preventDefault();
        
        if (!validateCurrentSection()) {
            return false;
        }
        
        // Show loading state
        const $submitBtn = $('button[type="submit"]');
        const originalText = $submitBtn.html();
        $submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Submitting...').prop('disabled', true);
        
        // Submit the form
        setTimeout(() => {
            $('#cmsr-form')[0].submit();
        }, 1000);
    }

    function showMessage(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const iconClass = type === 'success' ? 'fa-check-circle' : 
                         type === 'warning' ? 'fa-exclamation-triangle' : 
                         type === 'error' ? 'fa-times-circle' : 'fa-info-circle';
        
        const alert = $(`
            <div class="alert ${alertClass}">
                <i class="fas ${iconClass}"></i>
                ${message}
                <button type="button" class="alert-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `);
        
        $('.container').prepend(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.fadeOut(() => alert.remove());
        }, 5000);
    }

    // Close alert
    $(document).on('click', '.alert-close', function() {
        $(this).closest('.alert').fadeOut(() => $(this).closest('.alert').remove());
    });

    // Form field change handlers
    $('input, select, textarea').on('change', function() {
        // Remove error styling when user starts typing
        $(this).removeClass('error');
        $(this).closest('.form-group').find('.field-errors').remove();
    });

    // Auto-save functionality (optional)
    let autoSaveTimeout;
    $('input, select, textarea').on('input change', function() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            // Auto-save logic here
            console.log('Auto-saving form data...');
        }, 2000);
    });
}); 