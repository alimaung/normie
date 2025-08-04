// Main search functionality - redirects to DIN Standards search
// This file can be extended for other search features in the future

$(document).ready(function() {
    // Redirect generic search to DIN search for now
    // This can be expanded to include multiple search types
    
    function redirectToDinSearch(query) {
        const searchUrl = '/din/' + (query ? '?q=' + encodeURIComponent(query) : '');
        window.location.href = searchUrl;
    }
    
    // Global search functionality can be added here
    // For now, we focus on DIN standards search
    
    // Export function for use in other scripts
    window.performGlobalSearch = redirectToDinSearch;
});

// Legacy compatibility - can be used by other components
function performSearch(query) {
    if (window.performGlobalSearch) {
        window.performGlobalSearch(query);
    }
}
