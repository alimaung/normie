
var metadata = {
    companyTitle : "${COMPANY_TITLE}",
    libraryName : "${LIBRARY_NAME}",
    publicationTitle : "${PUBLICATION_TITLE}",
    revisionNumber : "${REVISION_NUMBER}",
    releaseDate : "${RELEASE_DATE}",
    archiveDate : "${ARCHIVE_DATE}",
    archiveNumberingStyle : "${PINPOINT_NUMBERING_STYLE}",
    numberingPattern : "${NUMBERING_PATTERN}"
}

window.onload = function (){
    writeMetaData(document)
}

function writeMetaData(document){
    var attributes = ["libraryName","publicationTitle","revisionNumber","releaseDate","archiveDate","companyTitle"]
    attributes.forEach(attribute => {
        document.querySelectorAll(`[data-attr="${attribute}"]`).forEach(element => {
            element.innerHTML = metadata[attribute]
        })
    })
}