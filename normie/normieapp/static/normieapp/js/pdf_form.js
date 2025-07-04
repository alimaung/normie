document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('save-form');
    const form = document.getElementById('pdf-edit-form');
    const alertContainer = document.getElementById('alert-container');
    
    saveButton.addEventListener('click', function() {
        // Collect all field values
        const formData = {};
        // Search both within the form and in the key-fields-header section
        const textInputs = document.querySelectorAll('input[type="text"], textarea');
        const checkboxInputs = document.querySelectorAll('input[type="checkbox"]');
        const radioInputs = document.querySelectorAll('input[type="radio"]:checked');
        
        textInputs.forEach(input => {
            const fieldId = input.dataset.fieldId;
            formData[fieldId] = input.value;
        });
        
        checkboxInputs.forEach(checkbox => {
            const fieldId = checkbox.dataset.fieldId;
            formData[fieldId] = checkbox.checked ? '/0' : '/1';
        });
        
        radioInputs.forEach(radio => {
            const fieldId = radio.dataset.fieldId;
            formData[fieldId] = radio.value;
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
                showAlert('success', data.message || '{% trans "Form saved successfully!" %}');
            } else {
                showAlert('danger', data.message || '{% trans "An error occurred while saving the form." %}');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', '{% trans "An error occurred while saving the form." %}');
        });
    });
    
    function showAlert(type, message) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        // Auto-hide the alert after 5 seconds
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
});