document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('pdf-file');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFile = document.getElementById('remove-file');
    const submitBtn = document.getElementById('submit-btn');
    const form = document.getElementById('upload-form');
    
    // Debug: Log form submission
    form.addEventListener('submit', function(e) {
        console.log('Form submitting...');
        console.log('File input value:', fileInput.value);
        console.log('File input files:', fileInput.files);
        console.log('Files length:', fileInput.files.length);
        if (fileInput.files.length > 0) {
            console.log('First file:', fileInput.files[0]);
            console.log('File name:', fileInput.files[0].name);
            console.log('File size:', fileInput.files[0].size);
            console.log('File type:', fileInput.files[0].type);
        } else {
            console.log('No files selected!');
            e.preventDefault(); // Prevent submission if no file
            alert('Please select a PDF file before uploading.');
            return false;
        }
    });
    
    // Click to select file
    dropArea.addEventListener('click', function() {
        console.log('Drop area clicked, opening file dialog...');
        fileInput.click();
    });
    
    // File selected via input
    fileInput.addEventListener('change', function() {
        console.log('File input changed:', this.files);
        handleFiles(this.files);
    });
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('border-primary');
    }
    
    function unhighlight() {
        dropArea.classList.remove('border-primary');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', function(e) {
        console.log('Files dropped:', e.dataTransfer.files);
        const dt = e.dataTransfer;
        const files = dt.files;
        
        // Manually set the files to the input element
        fileInput.files = files;
        
        handleFiles(files);
    });
    
    // Process the selected files
    function handleFiles(files) {
        console.log('Handling files:', files);
        if (files.length > 0) {
            const file = files[0];
            console.log('Selected file:', file.name, file.type, file.size);
            
            if (file.type === 'application/pdf') {
                fileName.textContent = file.name;
                fileInfo.style.display = 'block';
                submitBtn.disabled = false;
                console.log('PDF file accepted');
            } else {
                console.log('Invalid file type:', file.type);
                alert('Please select a PDF file.');
                resetFileInput();
            }
        } else {
            console.log('No files to handle');
        }
    }
    
    // Remove selected file
    removeFile.addEventListener('click', function() {
        console.log('Remove file clicked');
        resetFileInput();
    });
    
    function resetFileInput() {
        console.log('Resetting file input');
        fileInput.value = '';
        fileInfo.style.display = 'none';
        submitBtn.disabled = true;
    }
});