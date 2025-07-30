var activePage = "documents/coverpage.html";

function handleClick() {
    window.open(activePage + "?isPrint=true", "_blank");
}

function openModal() {
    var openElement = document.getElementById("pp-toc-header");
    openElement.getElementsByTagName("dialog")[0].showModal();
}

function closeModal() {
    var closeElement = document.getElementById("pp-toc-header");
    closeElement.getElementsByTagName("dialog")[0].close();
}

window.addEventListener("message", (event) => {
    if (event.data.action === "update-printPage") {
        activePage = event.data.value;
    }
});