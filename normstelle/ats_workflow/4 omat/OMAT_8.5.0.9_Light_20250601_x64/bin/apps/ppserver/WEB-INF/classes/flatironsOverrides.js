/**
 * Saving the parent object in iframeParent variable inorder to use it in viewExtRef method below.
 * @type {Window}
 */
var iframeParent = window.parent;
var parent = {}

/**
 * Onclick function for opening document reference in iFim manual
 * @param erMan
 * @param targetId
 * @param linkObj
 * @param calledBy
 */
function viewExtRef(erMan, targetId, linkObj, calledBy){
    iframeParent.postMessage({pubType:erMan,ataCode:targetId}, '*');
}

