"use strict";

if (window.addEventListener) {
    document.addEventListener("DOMContentLoaded", init, false);
}

// Parse search results into HTML
function parseLunrResults(results) {
    var html = [];
    for (var i = 0; i < results.length; i++) {
        var id = results[i]["ref"];
        var item = PREVIEW_LOOKUP[id];
        var title = item["t"];
        var link = item["l"].replace("\\", "/");
        var result = `
            <tr onclick="postClickMsg('${link}')">
                <td>${title}</td>
            </tr>
        `;
        html.push(result);
    }

    if (html.length) {
        let tableEntries = html.join("");
        return `
            <table>
                <thead>
                    <th scope="col">Name</th>
                </thead>
                <tbody>
                    ${tableEntries}
                </tbody>
            </table>
        `;
    } else {
        return "<p>Your search returned no results.</p>";
    }
}

function postClickMsg(link) {
    var parentWindow = window.parent;
    parentWindow.postMessage(link, "*");
}

function escapeHtmlCharacters(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showDialog() {
    let dialog = document.getElementById("search-help-dialog");
    dialog.showModal();
    
    // This ensures that the modal opens at the top (by default the button at the bottom gets focus)
    let firstHelpElement = document.getElementById("first-help-item");
    firstHelpElement.scrollIntoView(false);
    document.body.style.overflow = "hidden";
}

function closeDialog() {
    collapseStopWords();
    let dialog = document.getElementById("search-help-dialog");
    dialog.close();
    document.body.style.overflow = "auto";
}

function showResultCount(query, total, domElementId) {
    var element = document.getElementById(domElementId);

    if (total == 0) {
        element.innerHTML = "";
        return;
    }

    const plural = total > 1 ? "s" : "";
    const prettyQuery = query
        ? `for <span class="result-query">${escapeHtmlCharacters(query)}</span>`
        : "";
    const html = `<p>Found ${total} result${plural} ${prettyQuery}</p>`;

    element.innerHTML = html;
}

function searchLunr() {
    // Hide the search results
    let searchResultDiv = document.getElementById("i-results");
    searchResultDiv.style.display = "none";

    if(!isScriptLoaded()) {
        setSearchStatusText('Loading Search Index...');
        setTimeout(() => { // setTimeout allows the DOM to be updated
            loadScript('lunr_index.js')
                .then(() => {
                    runSearch();
                })
                .catch((err) => {
                    alert(`Loading the search index failed. Error: ${err}`);
                });
        });
    } else {
        runSearch();
    }
}

function runSearch() {
    // Get search term
    let searchEl = document.getElementById("search-input");
    let query = searchEl.value;

    if(query === "") {
        setSearchStatusText('Please input keyword before search.');
        return;
    } 

    if(STOP_WORDS[query.toLowerCase()]) {
        setSearchStatusText('Search for "' + query + '" is too generic. Please refine your search.');
        return;
    }

    setSearchStatusText('Searching...');
    setTimeout(() => { // setTimeout allows the DOM to be updated
        // Run search
        try {
            let idx = lunr.Index.load(LUNR_DATA);
            let results = idx.search(query);

            // Display results
            let searchResultDiv = document.getElementById("i-results");
            searchResultDiv.style.display = "";
            let resultHtml = parseLunrResults(results);
            document.getElementById("searchResults").innerHTML = resultHtml;

            var count = results.length;
            showResultCount(query, count, "result-count");
        } catch(error) {
            alert(`Failed to search on '${query}'. Error: ${error}`);
        }

        // Hide searching text
        setSearchStatusText("");
        checkQueryForStopWords(query);
    });
}

function setSearchStatusText(str) {
    let searchingText = document.getElementById("i-searching");
    if(str) {
        searchingText.innerHTML = `<p>${str}</p>`;
        searchingText.style.display = "";
    } else {
        // If no text is passed, then hide the element
        searchingText.style.display = "none";
    }
}

function loadScript(src) {
    return new Promise(function (resolve, reject) {
        var s;
        s = document.createElement('script');
        s.src = src;
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
    });
}

function isScriptLoaded() {
    return typeof LUNR_DATA !== "undefined";
}

function toggleStopWords(element) {
    element.classList.toggle("active");
    var content = element.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
}

function collapseStopWords() {
    let stopWords = document.getElementById("toggle-stop-words");
    stopWords.classList.remove("active");
    var content = document.getElementById("stop-word-content");
    content.style.display = "none";
}

function checkQueryForStopWords(query) {
    let stopWords = [];
    // Use Lunr to get a list of tokens from the query
    lunr.tokenizer(query).forEach((token) => {
        // Remove lunr search modifiers from the token
        let cleanToken = token.str
            .replace(/^\+/, "")
            .replace(/^-/, "");
        if(STOP_WORDS[cleanToken.toLowerCase()]) {
            stopWords.push(cleanToken);
        }
    });

    if(stopWords.length > 0) {
        let message = "The following terms are stop words and could cause unexpected results. Please remove them from your query.<i>";
        stopWords.forEach((stopWord) => {
            message =  message + "<br>" + stopWord;
        });
        message = message + "</i>"
        setSearchStatusText(message);
    }
}

function init() {
    // Configure lunr
    let separatorRegex = /\s+/;
    lunr.QueryLexer.termSeparator = separatorRegex; // Used when searching
    lunr.tokenizer.separator = separatorRegex; // Used when checking tokens for stop words
    
    injectStopWordHtml();
}

function injectStopWordHtml() {
    let stopWordText = "";
    Object.keys(STOP_WORDS).forEach(function(key) {
        stopWordText = stopWordText.concat(key, ", ");
    });

    stopWordText = stopWordText.substring(0, stopWordText.length -2); // trim final comma

    let element = document.getElementById("stop-word-content");
    element.innerHTML = stopWordText;
}