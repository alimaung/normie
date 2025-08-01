function postClickMsg(link) {
    var parentWindow = window.parent;
    parentWindow.postMessage(link, "*");
}

window.onload = function() {
    let tocFolders = document.getElementsByClassName("toc-folder");
    for (let i = 0; i < tocFolders.length; i++) {
        tocFolders[i].addEventListener("click", function () {
            // Display the contents of the folder
            this.parentElement
                .querySelector(".nested")
                .classList.toggle("active");

            // Change the folder
            let folder = this.querySelector(".icon-folder,.icon-folder-open")
            folder.classList.toggle("icon-folder");
            folder.classList.toggle("icon-folder-open");
        });
    }
}

window.addEventListener("message", (event) => {
    if(event.data.action === 'select-document') {
        selectDocument(event.data.value)
    }
});

function selectDocument(name) {
    // Remove the "selected" class from elements in the TOC
    clearCurrentlySelected();

    // Get the element that was just selected
    let id = `toc-${name}`;
    let tocElement = document.getElementById(id);

    // Expand the TOC to the selected element
    expandTocElement(tocElement);

    // Add the "selected" class to the selected element
    tocElement.classList.add("selected");

    // Scroll through the TOC to the selected element
    tocElement.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });

    function clearCurrentlySelected() {
        let selectedDocuments = document.querySelectorAll("span.selected");
        for(const selectedDocument of selectedDocuments) {
            selectedDocument.classList.remove("selected");
        }
    }

    function expandTocElement(element) {
        let parent = element.parentElement;
        //Expand self
        if (parent.nodeName.toUpperCase() === "LI") {
            const nestedList = parent.querySelector("UL.nested");
            if (nestedList != null){
                nestedList.classList.add("active");
            }
        }
        //Expand ancestors
        while(parent !== null) {
            if(parent.nodeName.toUpperCase() === "UL") {
                parent.classList.add("active");
            }
            else if (parent.nodeName.toUpperCase() === "LI") {
                const spanContainer = parent.children[0]
                const iconSpan = spanContainer.children[0]
                iconSpan.classList.replace("icon-folder", "icon-folder-open")
            }
            parent = parent.parentElement;
        }
    }
}
