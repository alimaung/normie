(function(){

    window.addEventListener("message", (event)=>{
        console.log(event.data);
        if(event.data.action === 'update-toc') {
            sendUpdateTocEvent(event.data.value);
        } else if(event.data.action !== 'update-printPage'){
            loadDocument(event.data);
        }
    });

    function loadDocument(documentPath) {
        if(documentPath.startsWith("media/")){
            window.open(documentPath ,"_blank");
        } else if(document.getElementById('pp-content').src && document.getElementById('pp-content').src.indexOf(documentPath) == -1) {
            // Open the document
            document.getElementById('pp-content').src = documentPath;

            // Update the TOC
            sendUpdateTocEvent(documentPath);

            let message = {
                action: 'update-printPage',
                value: documentPath
            };
            window.parent.postMessage(message, "*");
        }
    }

    function sendUpdateTocEvent(path) {
        let childWindow = document.getElementById("pp-toc");
        let filename = path.replace(/^.*[\/\\]/, "").replace(/.html(#.*)?$/, ".html");
        let message = {
            action: 'select-document',
            value: filename
        };
        childWindow.contentWindow.postMessage(message, "*");
    }
})();