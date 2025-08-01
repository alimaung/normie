(function(){
    if (window.addEventListener) {
        window.addEventListener("DOMContentLoaded", function() { respondToHashChange(location.hash) }, false); // For navigating to an anchor in a new document
    }
})();

const MD_STEP_CONTENT = "md-step-content";
const MD_STEP_ITEM = "md-step-item";
const ARIA_CONTROLS = "aria-controls";

function respondToHashChange(hash) {
    if(hash) {
        // Remove the '#' from the beginning of the hash string
        if(hash.startsWith('#')) {
            hash = hash.substring(1);
        }
        let anchorElement = getAnchor(hash);
        if(anchorElement) {
            scrollToAnchor(anchorElement);
        }
    }
}

function scrollToAnchor(anchor) {
    anchor.scrollIntoView({ behavior: "instant", block: "start"});
}

function getAnchor(id) {
    let anchorElements = null;
    if (id) {
        id = CSS.escape(id);
        anchorElements = document.querySelectorAll("#" +  id);
        if (anchorElements.length === 0) {
            anchorElements = document.querySelectorAll("*[name='" + id + "']");
        }
        if (anchorElements.length === 0) {
            anchorElements = document.querySelectorAll("#KEY_" + id);
        }
        if (anchorElements.length === 0) { //look for pp-data-anchor
            anchorElements = document.querySelectorAll(".pp-data-anchor_" +id);
        }
        if(anchorElements.length === 0) {
            anchorElements = document.querySelectorAll("*[thumbnailFileName='" + id + "']");
        }
        if(anchorElements.length === 0) { //look for pp-cml-anchor
            anchorElements = document.querySelectorAll(".pp-cml-anchor_" +id);
            if(anchorElements && anchorElements.length > 0){
                var anchor = anchorElements.item(0).getAttribute("KEY");
                var anchorId = "KEY_"+""+anchor;
                anchorElements = document.querySelectorAll("*[id=" + anchorId + "]");
            }
        }
        if (anchorElements.length === 0) {//ICN link from AMM to AIPC
            anchorElements = document.querySelectorAll("*[anchor='" + id + "']");
        }
        if (anchorElements.length === 0) {//For OMAT & Other Link
            anchorElements = document.querySelectorAll("*[id=\"_anchorTarget_" + id + "\"]");
        }
        if (anchorElements.length === 0) {//For EIPC Link
            anchorElements = document.querySelectorAll("*[id=\"_anchorTarget_part-" + id + "\"]");
        }
        if (anchorElements.length === 0) {//For SPM Link
            anchorElements = document.querySelectorAll("*[id=\"_anchorTarget_task-" + id + "\"]");
        }
        if (anchorElements.length === 0) {//scroll to the annotation
            anchorElements = document.querySelectorAll("*[data-annotation-id=" + id + "]");
            if (anchorElements && anchorElements.length > 0 && document.querySelectorAll("[id*='stepperView']").length > 0 && !document.querySelectorAll("[id*='stepperView']").hasClass('hidden'))
            {
                var stepIndex = anchorElements.item(0).closest(MD_STEP_CONTENT).getAttribute('id');
                if (!document.querySelectorAll(MD_STEP_ITEM + "[" + ARIA_CONTROLS + "=" + stepIndex + "]").item(0).classList.contains("md-active")){
                    document.querySelectorAll(MD_STEP_ITEM + "[" + ARIA_CONTROLS + "=" + stepIndex + "]").click();
                }
            }
        }
    }

    if (anchorElements && anchorElements.length > 0) {
        return anchorElements.item(0);
    } else {
        return null;
    }
}