// ==UserScript==
// @name         ChemScan Init
// @namespace    http://tampermonkey.net/
// @version      2025-02-12
// @description  try to take over the world!
// @author       You
// @match        https://app.chemscan.de/*
// @include      https://app.chemscan.de/*
// @icon         https://app.chemscan.de/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    document.querySelectorAll('div.filter-box.clearfix').forEach(e => e.removeAttribute("style"));

    const DEBUG = true;

    function log(message, data = null) {
        if (DEBUG) {
            if (data) {
                console.log(`[Details Copy Script] ${message}`, data);
            } else {
                console.log(`[Details Copy Script] ${message}`);
            }
        }
    }

    function processTable() {
        log('Starting to process table cells');

        // Find all table cells that contain the dropdown
        const cells = document.querySelectorAll('td.action-cell.grid-cell');
        log(`Found ${cells.length} action cells`);

        cells.forEach((cell, index) => {
            // Check if we've already processed this cell
            if (cell.getAttribute('data-processed-details') === 'true') {
                log(`Cell ${index} already processed, skipping`);
                return;
            }

            // Find the "Detaillierte Ansicht" element inside the dropdown
            const detailsView = cell.querySelector('.launcher-item a[title="Detaillierte Ansicht"]');

            if (detailsView) {
                log(`Found details view in cell ${index}`);

                // Clone the parent li element
                const detailsViewItem = detailsView.closest('.launcher-item').cloneNode(true);

                // Append it to the td
                cell.appendChild(detailsViewItem);

                // Mark as processed
                cell.setAttribute('data-processed-details', 'true');

                log(`Successfully copied details view for cell ${index}`);
            } else {
                log(`No details view found in cell ${index}`);
            }
        });
    }

    // Function to handle dynamic content
    function setupObserver() {
        log('Setting up mutation observer');

        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length) {
                    log('New nodes detected, processing table');
                    processTable();
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        log('Mutation observer setup complete');
    }

    // Initial processing
    if (document.readyState === 'loading') {
        log('Document still loading, adding DOMContentLoaded listener');
        document.addEventListener('DOMContentLoaded', () => {
            processTable();
            setupObserver();
        });
    } else {
        log('Document already loaded, processing immediately');
        processTable();
        setupObserver();
    }

    // Additional processing after window load
    window.addEventListener('load', () => {
        log('Window load event fired, running final check');
        processTable();
    });
})();