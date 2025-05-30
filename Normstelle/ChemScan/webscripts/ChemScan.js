// ==UserScript==
// @name         ChemScan
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

    function checkGridBody() {
        if (document.querySelector('.grid-body')) {
            console.log("Table exists!");
        } else {
            console.log("No table found.");
        }

        const rowItems = document.querySelectorAll('.grid-row.row-9cells');
        console.log(`Number of rows found: ${rowItems.length}`);
    }

    // Run check on page load
    window.addEventListener('load', checkGridBody);

    // Optional: Observe changes in the DOM and check dynamically
    const observer = new MutationObserver(checkGridBody);
    observer.observe(document.body, { childList: true, subtree: true });

})();