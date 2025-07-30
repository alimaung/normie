
(function(){

    function init() {
        if (typeof updateNumbering === "function") {
            updateNumbering(metadata.numberingPattern);
        }
        if(metadata.archiveNumberingStyle.toUpperCase() == "ATA"){
            var selectorElement = document.body.querySelector("div[class^=corena-s1000d]");
            if(selectorElement && selectorElement. length > 0){
                selectorElement.classList.add("ata");
            }
        };
        updateToc(window.location.href);
        var graphicElements = document.querySelectorAll('.graphicSheetLink, .graphicsLinkText, .openGraphicLink, .multimediaLink, .refGraphicHotspotLink');
        for (let i = 0; i < graphicElements.length; i++) {
            if (window.addEventListener) { //Firefox, Chrome, Safari, IE 10
                graphicElements[i].addEventListener('click', (event)=>{

                    var parentWindow = window.parent;
                    parentWindow.postMessage(event.currentTarget.attributes.href.value, "*");

                    event.preventDefault(event);//stop normal navigation
                }, false);
            }
        }
        var cirLinkCandidates = document.querySelectorAll('.cirLinkCandidate');
        for (let i = 0; i < cirLinkCandidates.length; i++) {
            if (window.addEventListener) { //Firefox, Chrome, Safari, IE 10
                cirLinkCandidates[i].addEventListener('click', (event)=>{
                    openCirLinkCandidate(event.currentTarget);
                }, false);
            }
        }
        var undeterminedSupportLinks = document.querySelectorAll('.undeterminedSupportLink');
        for (let i = 0; i < undeterminedSupportLinks.length; i++) {
            let undeterminedSupportLink = undeterminedSupportLinks[i];
            let anchorElement = getAnchor(undeterminedSupportLink.getAttribute('data-link-key'));
            if(anchorElement) {
                undeterminedSupportLink.classList.remove('undeterminedSupportLink');
                undeterminedSupportLink.classList.add('documentLink');
                undeterminedSupportLink.addEventListener('click', (event)=>{
                    scrollToAnchor(anchorElement);
                }, false);
            }
        }
        const isPrint = getQueryParamValue(window.location.search, 'isPrint');
        if(isPrint)
            printDocument();
    };

    function getQueryParamValue(query, paramName) {
        if(query == null) {
            return null;
        }

        const urlSearchParams = new URLSearchParams(query);
        return urlSearchParams.get(paramName);
    }

    function getTargetCirElement(parent) {
        if(parent) {
            const cirSelector = '.toolCirLink, .FINCirLink, .vendorCodeLink, .supplyCirLink, .supplyRequirementCirLink, .enterpriseCirLink, .zoneCirHtml, .partCirLink, .circuitBreakerCirLink, .accessPointCirHtml';
            let cirElement = parent.querySelector(cirSelector);
            if(cirElement) {
                return cirElement;
            } else if(parent.parent) {
                // Look for the CIR element again at a higher level
                return parent.parent.querySelector(cirSelector);
            }
        }

        return null;
    }

    function openCirLinkCandidate(currentTarget) {
        let dataParameter = currentTarget.attributes['data-parameter'].nodeValue;
        let anchor = getQueryParamValue(dataParameter, "anchor");
        if(anchor) {
            let anchorElement = document.querySelector("[name=" + anchor + "]");
            let targetElement = getTargetCirElement(anchorElement);
            if (targetElement) {
                targetElement.click();
            } else if(anchorElement) {
                // The anchor element exists, but isn't associated with a CIR
                // In this case, scroll the user to that element
                anchorElement.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
            }
        }
    }

    function expandSpareItems(originalBody) {
        var elements = originalBody.getElementsByClassName("pp-element-expandable");
        for (let i = 0; i < elements.length; i++) {
            var element = elements[i];
            var dataParameter = element.attributes.getNamedItem('data-parameter');
            var spareItemId = dataParameter.nodeValue.split('=')[1];
            var spareItem = document.getElementById(spareItemId);
            spareItem.style.display = 'block';
            element.innerHTML = '[-]';
        }
    }

    function printDocument() {
        var originalBody = document.getElementsByTagName("BODY")[0];
        expandSpareItems(originalBody);
        var printBody = document.createElement("BODY");
        printBody.innerHTML = `
            <TABLE id="print-table">
                <THEAD style="height: 60px;"></THEAD>
                <TBODY>
                    <TR>
                        <TD id='PLACEHOLDER'></TD>
                    </TR>
                </TBODY>
                <TFOOT style="height: 52px;"></TFOOT>
            </TABLE>
            <div class="onPrintOnly print-header">
                <div id="nameInformation">
                    <div data-attr="libraryName"></div>
                    <div data-attr="publicationTitle"></div>
                </div>
                <div id="dateInformation">
                    <div><span data-attr="companyTitle"></span></div>
                    <div>Revision: <span data-attr="revisionNumber"></span></div>
                    <div>Release Date: <span data-attr="releaseDate"></span></div>
                 </div>
            </div>
            <div class="onPrintOnly print-footer">
                <div style="padding:4px;" id="footerData"></div>
            </div>
        `;
        writeMetaData(printBody)
        var placeholder = printBody.querySelector(`[id='PLACEHOLDER']`);
        var htmlBodyContent ="";
        for (var i = 0; i < originalBody.children.length; i++) {
            htmlBodyContent+= originalBody.children[i].outerHTML;
        }
        placeholder.innerHTML = htmlBodyContent;
        document.body.innerHTML = printBody.outerHTML;
        document.getElementById("footerData").innerText = document.title;
        setTimeout(function() {
            document.title = metadata.libraryName + "_" + metadata.publicationTitle + "_" + document.getElementById("footerData").innerText;
            window.print();
        }, 500);
    }

    if (window.addEventListener) { //when document is loaded initiate init
        document.addEventListener("DOMContentLoaded", init, false);
    }

    function updateToc(href) {
        let message = {
            action: 'update-toc',
            value: href
        };
        window.parent.postMessage(message, "*");
    }
})();

function postClickMsg(link) {
    window.parent.postMessage(link, "*");
    respondToHashChange(link.substring(link.indexOf('#')));
}

function openModal(dialogId) {
    document.getElementById(dialogId).showModal();
}

function closeModal(dialogId) {
    document.getElementById(dialogId).close();
}

function openWebLink(link) {
    window.open(link, "_blank");
}

function selectedRow() {
    // There is a function with this name in Pinpoint Client
    // Adding it here to prevent console errors when the page loads
}

function mouseOver() {
    // There is a function with this name in Pinpoint Client
    // Adding it here to prevent console errors when the page loads
}

function mouseOut() {
    // There is a function with this name in Pinpoint Client
    // Adding it here to prevent console errors when the page loads
}
