$(document).ready(function() {
    let currentQuery = '';
    let isSearching = false;

    // Initialize search functionality
    initializeSearch();

    function initializeSearch() {
        // Bind search button click
        $('#search-btn').on('click', function() {
            performSearch();
        });

        // Bind enter key on search input
        $('#search-input').on('keypress', function(e) {
            if (e.which === 13) { // Enter key
                performSearch();
            }
        });

        // Bind example query clicks
        $('.example-query').on('click', function() {
            const query = $(this).data('query');
            $('#search-input').val(query);
            performSearch();
        });

        // Focus on search input
        $('#search-input').focus();
    }

    function performSearch() {
        if (isSearching) {
            return;
        }

        const query = $('#search-input').val().trim();
        if (!query) {
            showError('Please enter a search query');
            return;
        }

        currentQuery = query;
        isSearching = true;
        
        // Update UI state
        showLoading();
        updateSearchButton(true);

        // Get pagination setting
        const hitsPerPage = $('#hits-per-page').val() || '10';
        
        // Prepare form data
        const formData = new FormData();
        formData.append('query', query);
        formData.append('hitsPerPage', hitsPerPage);
        formData.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken'));

        // Perform AJAX request
        $.ajax({
            url: '/din/search/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            timeout: 60000, // 60 seconds timeout
            success: function(response) {
                handleSearchResponse(response);
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Search request failed';
                
                if (status === 'timeout') {
                    errorMessage = 'Search request timed out. Please try again.';
                } else if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error occurred. Please try again later.';
                } else if (xhr.status === 403) {
                    errorMessage = 'Access denied. Please log in and try again.';
                }

                showError(errorMessage);
            },
            complete: function() {
                isSearching = false;
                updateSearchButton(false);
            }
        });
    }

    function handleSearchResponse(response) {
        if (response.success) {
            if (response.standards && response.standards.length > 0) {
                displayResults(response.standards, response.query, response.count);
            } else {
                showNoResults();
            }
        } else {
            showError(response.error || 'Search failed');
        }
    }

    function displayResults(standards, query, count) {
        hideAllSections();
        
        // Update results header
        $('#search-query').text(query);
        $('#results-count').text(count);
        
        // Show pagination info if we have results
        const hitsPerPage = $('#hits-per-page').val();
        if (count > 0) {
            const pageInfo = count >= parseInt(hitsPerPage) ? 
                `(showing first ${hitsPerPage} results)` : 
                `(all results)`;
            $('#results-count').text(count + ' ' + pageInfo);
        }
        
        // Clear previous results
        const resultsContainer = $('#results-container');
        resultsContainer.empty();
        
        // Render each standard
        standards.forEach(function(standard) {
            const cardElement = createStandardCard(standard);
            resultsContainer.append(cardElement);
        });
        
        // Show results section
        $('#results-section').show();
        
        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#results-section').offset().top - 100
        }, 500);
    }

    function createStandardCard(standard) {
        // Clone template
        const template = $('#standard-card-template')[0].content;
        const card = $(template.cloneNode(true));
        
        // Populate card data
        card.find('.standard-title').text(standard.title || 'No title');
        card.find('.standard-description').text(standard.description || '');
        card.find('.standard-details').text(standard.details || '');
        
        // Status and year
        if (standard.status) {
            card.find('.standard-status').text(standard.status).show();
        } else {
            card.find('.standard-status').hide();
        }
        
        if (standard.year) {
            card.find('.standard-year').text(standard.year).show();
        } else {
            card.find('.standard-year').hide();
        }
        
        // Image
        if (standard.image_url) {
            card.find('.standard-img')
                .attr('src', standard.image_url)
                .attr('alt', standard.image_alt || standard.title || '');
        } else {
            card.find('.standard-image').hide();
        }
        
        // Pricing
        if (standard.price_vat) {
            card.find('.price-vat').html(`<strong>${standard.price_vat}</strong> (VAT incl.)`);
        }
        if (standard.price_no_vat) {
            card.find('.price-no-vat').text(`${standard.price_no_vat} (VAT excl.)`);
        }
        
        // Action buttons
        if (standard.url) {
            card.find('.view-btn').attr('href', standard.url);
        } else {
            card.find('.view-btn').hide();
        }
        
        // Order button
        card.find('.order-btn').on('click', function() {
            handleOrderClick(standard);
        });
        
        return card;
    }

    function handleOrderClick(standard) {
        // Navigate to order page with standard information
        const orderUrl = `/din/order/?standard=${encodeURIComponent(JSON.stringify({
            title: standard.title,
            url: standard.url,
            price_vat: standard.price_vat,
            price_no_vat: standard.price_no_vat
        }))}`;
        
        window.location.href = orderUrl;
    }

    function showLoading() {
        hideAllSections();
        $('#loading-section').show();
    }

    function showError(message) {
        hideAllSections();
        $('#error-message').text(message);
        $('#error-section').show();
    }

    function showNoResults() {
        hideAllSections();
        $('#no-results-section').show();
    }

    function hideAllSections() {
        $('#loading-section, #results-section, #error-section, #no-results-section').hide();
    }

    function updateSearchButton(searching) {
        const button = $('#search-btn');
        const icon = button.find('i');
        
        if (searching) {
            button.prop('disabled', true);
            icon.removeClass('fa-search').addClass('fa-spinner fa-spin');
            button.find('span, text').not('i').text('Searching...');
        } else {
            button.prop('disabled', false);
            icon.removeClass('fa-spinner fa-spin').addClass('fa-search');
            button.contents().filter(function() {
                return this.nodeType === 3; // Text nodes
            }).first().replaceWith('Search');
        }
    }

    // Retry search function (called from template)
    window.retrySearch = function() {
        if (currentQuery) {
            $('#search-input').val(currentQuery);
            performSearch();
        }
    };

    // CSRF token helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // URL parameter handling
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    // Auto-search if query parameter exists
    const initialQuery = getUrlParameter('q');
    if (initialQuery) {
        $('#search-input').val(initialQuery);
        performSearch();
    }
}); 