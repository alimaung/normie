//# sourceURL=lib/cortonasolo_prop.js
/** This file should be kept in sync for both Mobile and PP7, since any change is probably need in both apps. */
var propBackground3DColor = "#FFFFFF";
var propTableColor = "#000000";
var propTableBackgroundColor = "#FFFFFF";
var propTableSelectedColor = "#000000";
var propTableSelectedBackgroundColor = "#FFFFA0";

var propMessageBodyColor = "#FFFFFF";
var propMessageBodyBackgroundColor = "#808080";
var propMessageTextAreaColor = "#000000";
var propMessageTextAreaBackgroundColor = "#FFFFFF";

var propHideActions = false;
var propShowSubsteps = false;
var propAutoNumbering = true;
var propHihlightParents = true;
var propHihlightNumbers = true;

var propMuteSound = false;
var propShowMuteSoundCheckBox = false;
var propIsActiveFocus = true;
var propIsMessageboxEnabled = false;
var prop3DFrameSize = 60;
var prop3DFramePosition = "Right";

var propBOMStyle = "0";

//var resFolder = "res/";
var resFolder = "";
var forceDirectX = true;
//var helpFile = "en/help.html";
var helpFile = "";
var propUpRight = false;
var skinID = "{7F82003E-34AE-4F5A-9470-4891DC8FDFCB}";
var smoothcontrol_flag = true;
var axis_flag = true;
var vcr_flag = false;
var zoom_flag = false;
var isShowNavigationBar = false;
var warningbox_checked = true;
var pmibox_checked = true;

var exporterVersion = "9.0.0.455 (64-bit)";

var iLoadingMessage = "Loading...";

var iWarningErrorOnVRMLLoading = "VRML Loading error.";
var iWarningUnsupportedFile = "Error: The specified file cannot be identified as a supported type.";

var iWarningIsoViewNotFound = "IsoView ActiveX component not found in the registry.";
var iWarningIsoViewLoadingError = "2D Viewer Error - File was not loaded:";
var iWarningNoAppropriateViewerInstalled = "Can't show files of this type. No appropriate viewer installed.";

var iContextMenuCortonaProperties = "Properties";
var iContextMenuAbout = "About";

var iCaptionCortonaNotFound = "Cortona3D Viewer cannot be loaded.<br>Please make sure that <a href=\"http://www.cortona3d.com/cortona3d-viewer-download\" target=\"_blank\">Cortona3D Viewer</a> is installed and enabled in your current web browser.<br><a href=\"http://www.cortona3d.com/allow-plugin\" target=\"_blank\">Enable plugin in your browser</a>.";
var iWarningCortonaOldVersion = "Outdated version of the Cortona3D Viewer is found on your computer. This cannot render 3D scenes. Update Cortona3D Viewer to the latest version.";

var iCaptionRapid2DViewerNotFound = "Cortona2D Viewer cannot be loaded.<br>Please make sure that <a href=\"http://www.cortona3d.com/cortona2d-viewer-download\" target=\"_blank\">Cortona2D Viewer</a> is installed and enabled in your current web browser.<br><a href=\"http://www.cortona3d.com/allow-plugin\" target=\"_blank\">Enable plugin in your browser</a>.";

var iMessageCloseButton = "Close";

var TXT_ABOUT_DOCUMENT = "Document Version:";
var TXT_ABOUT_CORTONA = "3D Viewer Version:";
var TXT_ABOUT_CGM = "2D Viewer Version:";

var iGenericErrorMessage = "Oops, something went wrong... :(. Check [this page|http://support.cortona3d.com/viewing-publications] for possible causes and solutions of the problem.";
var iCortonaOldVersion = "";
var iViewerUnavailable = "Viewer is not available";

var iMsgInspect = "Inspection required.";
var iInspectPrefix = "Inspected: ";
var iSignOffPrefix = "Sign off: ";

var eventsArray = new Array();

var procId = "r607980b6-4222-4f9e-814e-70990f166958";

var steps_list = [];
var items_list = [];
var actions_list = [];

var imgArray = [];
var prtArray = [];
var inspArray = [];
var dplTable = null;

var pmiArray = [];
var docItems = [];

var graphics_list = [];

var isBlocked = true;

var usePlugins = false;

var prefixUrl = "widgets/graphic/lib/cortona-solo/";

// Total memory in MB
// var totalMemory = 128;

var TRANSPARENT = 0.8;
var totalMemory = 512;
var waitingForLoadedSheetInterval = null;
var cortona3dIsLoadingSheet = false;


function getDeviceType() {
    var deviceType = navigator.userAgent;
    if (navigator.userAgent.match(/iPad/i) == "iPad")
        return "iPad";
    else if (navigator.userAgent.match(/iPhone/i) == "iPhone")
        return "iPhone";
    else if (navigator.userAgent.match(/Android/i) == "Android")
        return "Android";
    else if (navigator.userAgent.match(/BlackBerry/i) == "BlackBerry")
        return "BlackBerry";
    else if (navigator.userAgent.match(/MSIE/i) == "MSIE")
        return "IE";
    else if (navigator.userAgent.match(/Trident/i) == "Trident")
        return "IE";
    else if (navigator.userAgent.match(/Chrome/i) == "Chrome")
        return "Chrome";
    else if (navigator.userAgent.match(/Firefox/i) == "Firefox")
        return "Firefox";
    else
        return null;
}

if (window.parent.highlightTextHotspot) {
    //This is mobile
    prefixUrl  = "lib/cortona/cortona-solo/";
}

function isTouchEvent(event) {
    var result = false;
    switch (getDeviceType()) {
        case "iPhone":
        case "iPad":
        case "Android":
            result = true;
            break;
        default:
            result = event.type.indexOf('touch') >= 0;
    }
    return result;
}

function show3D() {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.procedure.show3D.apply(this, arguments);
}

function play() {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.procedure.play.apply(this, arguments);
}

function selectSheet(ev) {
   if(window.parent.changeGraphicSheet){
       var sheetExistsIn3DModel = Cortona3DSolo.app.getDocumentInfo().sheets.length > 0 && Cortona3DSolo.app.getDocumentInfo().sheets[ev.selectedIndex] != null;
       window.parent.changeGraphicSheet(ev.selectedIndex, sheetExistsIn3DModel);
       selectSheetByIndex(ev.selectedIndex) // this will call the respective sheet by index if the changeGraphicSheet doesn't display the corresponding sheet
   }
}

function selectSheetByIndex(sheetIdx) {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    var selectedSheet = Cortona3DSolo.app.getDocumentInfo().sheets[sheetIdx].id;
    cortona3d.app.ipc.setCurrentSheet(selectedSheet);
    var sheetSelect = document.getElementById("choice_sheet");
    if (sheetSelect.value !== selectedSheet){
        sheetSelect.value = selectedSheet
    }
}

function pause() {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.procedure.pause.apply(this, arguments);
}

function stop() {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.procedure.stop.apply(this, arguments);
}

function setSpeedRatio(param) {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.procedure.setPlaybackSpeed(param);
}

function findRowByItem(cortona3d, itemNum) {
    var result = -1;
    var ixml = cortona3d.app.ipc.interactivity;
    ixml.json.$('ipc/figure/dplist/item').forEach(function (item, row) {
        for(var i=0; i < item.$('metadata/value').length; i++) {
            var itemNumber = item.$('metadata/value')[i].$text();
            var itemNumberPresent;
            if(parseInt(itemNumber) === 'NaN') {
                itemNumberPresent = item.$('metadata/value')[i].$text() === itemNum;
            } else {
                itemNumberPresent = parseInt(item.$('metadata/value')[i].$text()) === parseInt(itemNum);
            }

            if(item.$('metadata/value')[i].$attr && item.$('metadata/value')[i].$attr('name')?.toUpperCase() === 'ITEM' && itemNumberPresent) {
                result = row;
            }
        }
    });
    return result;
}

function findRowByPartNbr(cortona3d, partnbr) {
    var result = -1;
    var ixml = cortona3d.app.ipc.interactivity;
    var part = ixml.json.$('ipc/parts/part').filter(function (node) {
        var foundmd = node.$('metadata/value').filter(function (mdnode) {
            if (mdnode.$text() === partnbr || mdnode.$text().match(partnbr)) {
                return true;
            }
        });
        //console.log("Filter parts", foundmd);
        return foundmd.length > 0	;
    });
    if (part.length > 0) {
        ixml.json.$('ipc/figure/dplist/item').forEach(function (item, row) {
            if (item.$attr("refPart") === part[0].$attr("id")) {
                console.log("Found item", row, item);
                result = row;
            }
        });
    }
    return result;
}
function highlight3DItem(param) {
    var partnbr = param.hotspotValue;
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    var row = (partnbr?.toUpperCase() === 'NO-NUMBER') ? -1 : findRowByPartNbr(cortona3d, partnbr);
    if (row >= 0) {
        highlightItemByRow(cortona3d, row);
    } else {
        var row = findRowByItem(cortona3d, param.itemNumber);
        if(row >= 0){
            highlightItemByRow(cortona3d, row);
        } else {
            console.log("Part not found, using backup find", partnbr);
            row = findDPLRowByPartNbr(cortona3d, partnbr);
            highlightItemByRow(cortona3d, row);
        }
    }
}

function findDPLRowByPartNbr(cortona3d, val) {
    var row = -1;
    row = getRow(cortona3d, val);
    return row;
}

function highlightItemByRow(cortona3d, row) {
    if (row >= 0) {
        var ixml = cortona3d.app.ipc.interactivity;
        var itemInfo = ixml.getItemInfo(row);
        var useSheet = itemInfo.sheetId;

        if (useSheet === "") {
            var sheets = cortona3d.app.getDocumentInfo().sheets;
            useSheet = sheets[0].id;
            for (var i = 1; i < sheets.length; i++) {
                var sheet = sheets[i];
                var items = sheet.items;
                //  console.log(sheet, row, items);
                for (var x = 0; x < items.length; x++) {
                    if (items[x] === row) {
                        useSheet = sheet.id;
                        break;
                    }
                }
                if (useSheet === sheet.id) break;
            }
        }
        if (cortona3d.app.ipc.currentSheetInfo.id !== useSheet) {
            document.getElementById("choice_sheet").value = useSheet;
            cortona3d.app.ipc.setCurrentSheet(useSheet);
            cortona3dIsLoadingSheet = true; //global variable accessible from both highlightItemByRow and didSelectSheet functions
            if (waitingForLoadedSheetInterval != null){ //global variable, since we need to ensure that we do not create multiple interval for each highlightItemByRow call
                clearTimeout(waitingForLoadedSheetInterval); //clear any intervals before creating a new one to avoid mem leaks
            }
            waitingForLoadedSheetInterval = setInterval(function(remainingIterations) {
                if (remainingIterations <= 0){
                    clearInterval(waitingForLoadedSheetInterval); //clear interval when it is no longer needed
                }
                if (!cortona3dIsLoadingSheet){
                    //after the sheet is loaded, then
                    var index = ixml.getIndexByRow(row);
                    didFinishCortona3DSoloLoad.selectedIndex = index;
                    cortona3d.app.ipc.selectItem(index, false);
                    cortona3d.app.fitSelectedObjectsInView(true, 0.6);
                    clearInterval(waitingForLoadedSheetInterval); //clear interval when it is no longer needed
                }
                remainingIterations--;
            }, 10, 20)
        }
        else {
            var index = ixml.getIndexByRow(row);
            didFinishCortona3DSoloLoad.selectedIndex = index;
            cortona3d.app.ipc.selectItem(index, false);
            cortona3d.app.fitSelectedObjectsInView(true, 0.6);
        }
    }
}

function getRow(cortona3d, val) {
    var row = -1;
    var tbody;
    var dplTable = cortona3d.app.dplTable;
    if (dplTable == null || dplTable === "")
        return row;
    var root = document.createElement("div");
    root.innerHTML = dplTable;
    tbody = root.getElementsByTagName("tbody")[0];
    if (tbody == null)
        return row;
    // Get list of rows (<tr>)
    var rows = tbody.getElementsByTagName("tr");
    // Find the row where the value of part number is located
    var rowText;
    var rowId;
    for (var i = 0; i < rows.length; i++) {
        rowText = rows[i].textContent;
        if (rowText.indexOf(val) !== -1) {
            // Get row id
            rowId = rows[i].getAttribute("id");
            // Get row number
            if (rowId != null && rowId.length > 3)
                row = rowId.substr(3);
            break;
        }
    }
    return parseInt(row);
}

function resetGraphic() {
    var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
    cortona3d.app.ipc.resetCurrentSheet(true);
}

function responseHotspotItem(param) {
    if (didFinishCortona3DSoloLoad && didFinishCortona3DSoloLoad.modelIsReady) {
        var cortona3d = didFinishCortona3DSoloLoad.fetchCortona3DSolo();
        if (param.hotspotValue) {
            didFinishCortona3DSoloLoad.highlightHotspotItem(param);
        }
    } else {
        setTimeout(responseHotspotItem, 100, param);
    }
}

function showObjectWithChildren(Cortona3DSolo, obj) {
    Cortona3DSolo.app.restoreObjectProperty(obj, Cortona3DSolo.app.PROPERTY_VISIBILITY, false);

    var cObjs = [];
    cObjs = Cortona3DSolo.app.getChildObjects(obj);
    if (cObjs != null && cObjs.length > 0)
        for (var k in cObjs)
            showObjectWithChildren(Cortona3DSolo, cObjs[k]);
}

function showObject(Cortona3DSolo, partname, objs) {

    for (var k in objs)
    {

        var objName = Cortona3DSolo.app.getObjectName(objs[k]);
        if (objName === partname) {
            showObjectWithChildren(Cortona3DSolo, objs[k]);
            return true;
        }
        var cObjs = [];
        cObjs = Cortona3DSolo.app.getChildObjects(objs[k]);
        if (cObjs != null && cObjs.length > 0){
            if(showObject(Cortona3DSolo, partname, cObjs)) {
                Cortona3DSolo.app.restoreObjectProperty(objs[k], Cortona3DSolo.app.PROPERTY_VISIBILITY, false);
                return true;
            }
        }
    }
    return false;
}

function showAvailableObjects(Cortona3DSolo, parts) {
    // Traverse 3D objects from the root of the objects hierarchy to determine their visibility
    var rootObjs = Cortona3DSolo.app.getChildObjects();
    if (rootObjs && rootObjs.length > 0) {
        // For each part in the parts array, make the corresponding 3D object (and all parent/ancestor objects in the traverse path) visible.
        for (var i in parts) {
            showObject(Cortona3DSolo, parts[i], rootObjs);
        }
    }
}


function hideAllObjects(Cortona3DSolo, objs)
{
    // Hide all objects in the object tree, do it recursively
    var cObjs;
    for (var k in objs)
    {
        Cortona3DSolo.app.setObjectPropertyf(objs[k], Cortona3DSolo.app.PROPERTY_VISIBILITY, false, 0);
        cObjs = Cortona3DSolo.app.getChildObjects(objs[k]);
        if (cObjs != null && cObjs.length > 0)
            hideAllObjects(Cortona3DSolo, cObjs);
    }
}

// Do not show the items (graphical objects ) in the 3D graphic
// if they are not listed in the DM DPL table
//
function hideItemsNotAvailableInDPLTable(Cortona3DSolo, doctype, hotspotList) {
    // Show only items listed in DM DPL table
    //
    console.log("hideItemsNotAvailableInDPLTable");
    console.log(hotspotList);
    if (hotspotList === null || !hotspotList || hotspotList.length === 0) {
        return;
    }
    if(doctype === "ipc"){
    var ixml = Cortona3DSolo.app.ipc.interactivity;
    if (ixml && ixml.json) {
        ixml.json.$('ipc/figure/dplist/item').forEach(function (item, row) {

            var itemRow = row;
            var partnbr = getPartNbrFromItem(ixml, item.$attr('refPart'));
            try {
                if (!partnbr || partnbr === "") {
                    partnbr = ixml.getScreenTip(ixml.getIndexByRow(row));
                }
            } catch (ex) {
                console.log("Cortona3D Solor Error " + ex);
                partnbr = null;
            }
            // console.log("Use PNR", partnbr);
            ixml.getObjectsNamesByRow(row).forEach(function (name) {
                var handle = Cortona3DSolo.app.getObjectWithName(name);
                if (partnbr !== null) {
//					console.log("Show ",itemRow, " is defined", hotspotList.indexOf (partnbr), " item ",Cortona3DSolo.app.ipc.interactivity.getItemByRow(itemRow));
                    if (hotspotList.indexOf(partnbr) > -1 || Cortona3DSolo.app.ipc.interactivity.getItemByRow(itemRow) < 1) {
                        //					console.log("SHOW");
                        Cortona3DSolo.app.setObjectPropertyf(handle, Cortona3DSolo.app.PROPERTY_VISIBILITY, false, 0);
                    } else {
                        //				console.log("HIDE");
                        Cortona3DSolo.app.setObjectPropertyf(handle, Cortona3DSolo.app.PROPERTY_VISIBILITY, false, 1);
                    }
                }
            });

        });
    }
    }else if(doctype === "generic"){
        // Get all available parts from DPL table in the corresponding DM
       // var availParts = getAvailablePartsInDPLTable();

        // Traverse 3D objects from the root of the objects hierarchy to determine their visibility
        var rootObjs = Cortona3DSolo.app.getChildObjects();

        // Set visibility flag to hide all 3D objects
        hideAllObjects(Cortona3DSolo, rootObjs);
        // Restore visibility flag for all 3D objects available in DM DPL table
        showAvailableObjects(Cortona3DSolo, hotspotList);
        // Get all 3D objects that need to be removed
        var dirtyObjs = Cortona3DSolo.app.getObjectsWithDirtyProperty(Cortona3DSolo.app.PROPERTY_VISIBILITY);
        Cortona3DSolo.app.removeObjects(dirtyObjs);
    }
}

function getPartNbrFromItem(ixml, partRef) {
    var partnbr = null;
    var part = ixml.json.$('ipc/parts/part').filter(function (node) {
        if (node.$attr("id") === partRef) return true;
    });
    if (part && part.length === 1) {
        var pnr = part[0].$("metadata/value").filter(function (node) {
            if (node.$attr("name") === "PARTNUMBER") return true;
        });
        if (pnr && pnr.length === 1) {
            partnbr = pnr[0].$text();
        }
    }
    return partnbr;
}

function getItemNbrFromItem(ixml, item) {
    var itemNumber = null;
    var itemAttribute = ixml.json.$('ipc/figure/dplist/item').filter(function (node) {
        return node.$attr("id") === item.id;

    });
    if (itemAttribute && itemAttribute.length === 1) {
        var itemNode = itemAttribute[0].$("metadata/value").filter(function (node) {
            return node.$attr("name")?.toUpperCase() === "ITEM";

        });
        if (itemNode && itemNode.length === 1) {
            itemNumber = itemNode[0].$text();
        }
    }
    return itemNumber;
}
function getItemNbrFromRow(index){
    var ixml = Cortona3DSolo.app.ipc.interactivity;
    var row = ixml.getRowByIndex(index);
    var item = ixml.getItemInfo(row);
    return getItemNbrFromItem(ixml, item);
}

function getPartNbrFromRow(index) {
    var ixml = Cortona3DSolo.app.ipc.interactivity;
    var row = ixml.getRowByIndex(index);
    var item = ixml.getItemInfo(row);
    return getPartNbrFromItem(ixml, item.part.id);
}

function popupItemWhenHover(screenTip, hotspotList) {
    if (hotspotList === null || hotspotList.length === 0) {
        return;
    }
    document.body.title = screenTip;
}

function postHotspotMessage(param) {
    if (window.parent.listenWrlHotspot) {
        window.parent.listenWrlHotspot(param);
    } else if (window.parent.highlightTextHotspot) {
        window.parent.highlightTextHotspot(param);
    }
}

function showWrlLoader() {
    var loader = document.getElementById("wrlLoader");
    if (loader) {
        loader.style.display = 'inline-block';
    } else if (window.parent.showLoading) {
        window.parent.showLoading()
    }
}

function hideWrlLoader() {
    document.getElementById("wrlLoader").style.display = 'none';
    var loader = document.getElementById("wrlLoader");
    if (loader) {
        loader.style.display = 'none';
    } else if (window.parent.hideLoading) {
        window.parent.hideLoading();
    }
}


function didFinishCortona3DSoloLoad(Cortona3DSolo, graphicData, simicImage, hotspotList) {
    var figureType;
    var wrlCanvas = document.getElementById("wrlCanvas");
    var partList = [];
    var currentGraphicData = {};
    var constNotFound = "NOTFOUND";
	var m_played = false;
    var m_range = document.getElementById('toolbar-range-input');
	var canvas = document.getElementById('canvas');
	var counter = 0;
    var navigation = true;

    showWrlLoader();

    var defaultFeatures = Cortona3DSolo.app.DISABLE_DISCARDABLE_GEOMETRY_DATA |
        Cortona3DSolo.app.ENABLE_NAVIGATION_FIT_TO_OBJECT | Cortona3DSolo.app.ENABLE_GLES3;
    var dataURL = "";
    if(simicImage && simicImage.content){
        dataURL = URL.createObjectURL(new Blob(["#VRML V2.0 utf8\nWorldInfo{}"], {
            type: "model/vrml"
        }));
        defaultFeatures = Cortona3DSolo.app.DISABLE_DISCARDABLE_GEOMETRY_DATA |
        Cortona3DSolo.app.ENABLE_NAVIGATION_FIT_TO_OBJECT ;
    }


    if (getDeviceType() === "IE") {
        totalMemory = 64;
        // defaultFeatures = Cortona3DSolo.app.DISABLE_DISCARDABLE_GEOMETRY_DATA |
        //     Cortona3DSolo.app.ENABLE_NAVIGATION_FIT_TO_OBJECT;
    }

    // var dataURL = URL.createObjectURL(new Blob(["#VRML V2.0 utf8"], {
    //         type: "model/vrml"
    // }));
    Cortona3DSolo.use('core', {
        prefixURL: prefixUrl,
        totalMemory: totalMemory,
        src : dataURL,
        features: defaultFeatures,
        canvas: wrlCanvas


    });




    //Cortona3DSolo.use("drawing");


    //  window.parent.showLoading();

    //  var s = 0;
    //  "object" == typeof window.chrome && "win" === window.navigator.platform.substr(0, 3).toLowerCase() && (s |= Cortona3DSolo.app.DISABLE_VERTEX_ARRAY_OBJECT_OES),
    //  Cortona3DSolo.core.arguments = Cortona3DSolo.core.arguments.concat(["features", s.toString()])


    didFinishCortona3DSoloLoad.fetchCortona3DSolo = fetchCortona3DSolo;
    didFinishCortona3DSoloLoad.highlightHotspotItem = highlightHotspotItem;
    didFinishCortona3DSoloLoad.getCurrentGraphicData = getCurrentGraphicData;
    didFinishCortona3DSoloLoad.modelIsLoaded = false;
    didFinishCortona3DSoloLoad.modelIsReady = false;
    function fetchCortona3DSolo() {

        return Cortona3DSolo;
    }

    function getCurrentGraphicData() {
        return currentGraphicData;
    }


    function highlightHotspotItem(param) {
        if (figureType === "generic") {
            var handle = Cortona3DSolo.app.getObjectWithName(param.hotspotValue);
            Cortona3DSolo.app.setSelectedObjects([handle], true);
            Cortona3DSolo.app.fitSelectedObjectsInView([handle], true);
        } else if (figureType === "ipc") {
            highlight3DItem(param);
        } else if (figureType === "procedure") {
            var stepId = param.hotspotValue;
            var procedure = Cortona3DSolo.app.procedure;
            procedure.stop();
            procedure.setPlayRange();
            procedure.seekToSubstep(stepId);
            procedure.setPlayRange("%%CURRENT_STEP%%", null, procedure.RANGE_FLAGS_REQUEST_NOTIFICATION | procedure.RANGE_FLAGS_DO_NOT_RECALCULATE_POSITION);
            procedure.play();
        }
    }

    function fetchPartNbrByHandle(handle) {

        for (var i = 0; i < partList.length; i++) {
            var partDetail = partList[i];
            if (partDetail.handle === handle) {
                return partDetail.partnbr
            }
        }
        return null;
    }

     function queryPartnbrFromClickEvent(event, needFocus) {
        var target = event.target || event.srcElement,
            rect = target.getBoundingClientRect(),
            offsetX = event.clientX - rect.left,
            offsetY = event.clientY - rect.top,
            picked = Cortona3DSolo.app.pickObjectChain(offsetX, offsetY);
        var selectedObject = "";
        if (picked) {
            selectedObject = constNotFound;
            for (var i=0;i<picked.chain.length;i++){
                var handle = picked.chain[i];

                if(fetchPartNbrByHandle(handle)){
                    selectedObject = fetchPartNbrByHandle(handle);
                    if(selectedObject.length>0 && selectedObject !== constNotFound && needFocus){
                            Cortona3DSolo.app.setSelectedObjects([handle], true);
                            Cortona3DSolo.app.fitSelectedObjectsInView([handle], true);
                    }
                }
            }
        } 
        return selectedObject;
    }

    function collectandHideParts(hotspotList) {
        if(hotspotList === null || hotspotList.length ===0 ){return;}
        for(var i=0;i<hotspotList.length;i++){
            var handle = Cortona3DSolo.app.getObjectWithName(hotspotList[i]);
            var partDetail = {
                handle : handle,
                partnbr: hotspotList[i]
            };
            partList.push(partDetail);
        }
        return;

    }

    function fetchPartDetailsByHandle(handle) {

        for (var i = 0; i < partList.length; i++) {
            var partDetail = partList[i];
            if (partDetail.handle === handle) {
                return partDetail;
            }
        }
        return null;
    }

    function fetchHandlesByGroup(groupId) {
        var handles = [];
        for (var i = 0; i < partList.length; i++) {
            var partDetail = partList[i];
            if (partDetail.group === groupId) {
                handles.push(partDetail.handle);
            }
        }
        return handles;
    }
    // Get the position of a touch relative to the canvas
    function getTouchPos(canvasDom, touchEvent) {
        var rect = canvasDom.getBoundingClientRect();
        return {
            x: touchEvent.touches[0].clientX - rect.left,
            y: touchEvent.touches[0].clientY - rect.top
        };
    }

    // Get the position of a mouse relative to the canvas
    function getMousePos(canvasDom, mouseEvent) {
        var rect = canvasDom.getBoundingClientRect();
        return {
            x: mouseEvent.clientX - rect.left,
            y: mouseEvent.clientY - rect.top
        };
    }

    function collectandHideParts(hotspotList) {
        if (hotspotList === null || hotspotList.length === 0) {
            return;
        }
        for (var i = 0; i < hotspotList.length; i++) {
            var objects = hotspotList[i].split(",");
            for (index in objects) {
                var handle = Cortona3DSolo.app.getObjectWithName(objects[index]);
                if (handle !== "" && handle > 0) {
                    var partDetail = {
                        handle: handle,
                        partnbr: objects[index],
                        group: i
                    };
                    partList.push(partDetail);
                }
            }

        }

    }

    function getPartNbr(rowNbr) {
		var pn = "";
		var tbody;
		var pnCol;
		if (dplTable === null || dplTable === "") {
            return pn;
        }
		var root = document.createElement("div");
		root.innerHTML = dplTable;
		tbody = root.getElementsByTagName("tbody")[0];
		if (tbody === null) {
            return pn;
        }
		// Get list of rows (<tr>)
		var rows = tbody.getElementsByTagName("tr");
		// Get the row with id is equal "row" + rowNbr
		var rowId;
		var selectedRow = "row" + rowNbr;
		for (var i = 0; i < rows.length; i++) {
			rowId= rows[i].getAttribute("id");
			if (rowId === selectedRow) {
				// Found row, try to get the part number (located at column 3)
				// rowText = rows[i].textContent;
				pnCol = rows[i].getElementsByTagName("td")[2];
				if (pnCol !== null) {
					pn = pnCol.textContent;
				}
			}
		}
		return pn;
	}

    function getPartNbrByDPLRow(row) {
		var partnbr = "";
		if (row >= 0) {
            partnbr = getPartNbr(row);
        }
		return partnbr;
	}

    Cortona3DSolo.app.didFinishLoadDocument = function (doc) {
        //window.parent.hideLoading($);
        currentGraphicData = graphicData;

        figureType = doc.type;
        hideWrlLoader();
        var el = document.getElementById("control_bar");
       // Cortona3DSolo.app.setRotationCenterVisibility(true);
        if (doc.type === "procedure") {
            el.style.display = '';
			m_range.min = 0;
			m_range.max = doc.duration;
			m_range.step = (m_range.max - m_range.min) / 1000;
			m_range.value = 0;
			m_range.onchange = m_range.oninput = function () {
				Cortona3DSolo.app.procedure.setPlayPosition(this.value, false);
			};
            // console.log(this.procedure); see procedue function
            //  this.procedure.play();
            Cortona3DSolo.app.procedure.didEnterSubstepWithName = function (index) {
                var param = {};
                param.hotspotType = "INTERNALREF";
                param.hotspotLinkType = "hotspotInternalLink";
                param.hotspotValue = index;
                param.figureICN = currentGraphicData.imageID.substr(0, currentGraphicData.imageID.indexOf('.'));
                if (param.hotspotValue !== null) {
                    postHotspotMessage(param);
                }
            };
            Cortona3DSolo.app.procedure.didEnterSubstep = function (path) {
                console.log("didEnterSubstep", path);
            }
        } else if (doc.type === "ipc") {
            el.style.display = 'none';
            var elipc = document.getElementById("control_bar_ipc");
            if (elipc) {
                elipc.style.display = '';
                var sheets = Cortona3DSolo.app.getDocumentInfo().sheets;
                for (var index in sheets) {
                    if (sheets.hasOwnProperty(index)) {
                        var sheet = Cortona3DSolo.app.getDocumentInfo().sheets[index];
                        var o = new Option(sheet.description, sheet.id);
                        // console.log(sheet, o);
                        var select = document.getElementById("choice_sheet");
                        select.appendChild(o);
                    }
                }
            }
            Cortona3DSolo.app.ipc.didHoverItem = function (index) {
                if (Cortona3DSolo.app.ipc.interactivity) {
                    if (index >= 0) {
                        var screenTip = Cortona3DSolo.app.ipc.interactivity.getScreenTip(index);
                        if(screenTip === "") {
                            screenTip = getPartNbrByDPLRow(index);
                        }
                        popupItemWhenHover(screenTip, hotspotList);
                    }
                }
            };
            Cortona3DSolo.app.ipc.didSelectItem = function (index) {
                didFinishCortona3DSoloLoad.selectedIndex = index;
                var param = {};
                param.hotspotType = "PARTNUMBER_HOTSPOT";

                if (index >= 0) {
                    var screenTip = Cortona3DSolo.app.ipc.interactivity.getScreenTip(index);
                    if (screenTip === "") {
                        screenTip = getPartNbrByDPLRow(index);
                        param.hotspotValue = screenTip;
                    }
                }
                try {
                    param.hotspotValue = getPartNbrFromRow(index);
                    param.itemNumber = getItemNbrFromRow(index);
                } catch (ex) {
                    console.log("Cortona3D Solor Error " + ex);
                    param.hotspotValue = null;
                }
                if (param.hotspotValue !== null || param.itemNumber != null) {
                    postHotspotMessage(param);

                }
            };
            Cortona3DSolo.app.ipc.didSelectSheet = function(sheet) {
                console.log("didSelectSheet",sheet);
                dplTable = sheet.dplTable;
                setTimeout(function() {
                    Cortona3DSolo.app.fitSceneInView(false);
                    cortona3dIsLoadingSheet = false; //reset this back to false after the sheet is loaded and fitted to scene.
                },100);
                document.getElementById('printPdfButton').onclick = function () {
                    var img = document.getElementById('wrlCanvas');
                    var dimen = img.getAttribute("dimensions").split(',');
                    if (dimen[0] !==''  && dimen[1] !=='') {
                        Cortona3DSolo.app.resize(dimen[0], dimen[1]);
                    } else {
                        Cortona3DSolo.app.resize(1024, 1024);
                    }
                    Cortona3DSolo.once("core.didDrawAnimationFrame", function () {
                        img.src = Cortona3DSolo.core.canvas.toDataURL('image/png');
                        printGraphic(img.src);
                        Cortona3DSolo.core.didChangeLayout();
                    })
                }
            }
        } else if (doc.type === "generic") {
            Cortona3DSolo.app.jumpToStandardView("isometric", true);
            Cortona3DSolo.app.centerRotationCenterInView(true);
            var el  = document.getElementById("control_bar");
            el.style.display = 'none';

        }
        didFinishCortona3DSoloLoad.modelIsLoaded = true;
    };


    Cortona3DSolo.app.firstFrameDidArrive = function () {
        Cortona3DSolo.app.ui.showCanvas(true);
        didFinishCortona3DSoloLoad.modelIsReady = true;
        console.log("firstFrameDidArrive", Cortona3DSolo.app);
        var useClick = false;
        if (figureType === 'ipc') {
            hideItemsNotAvailableInDPLTable(Cortona3DSolo, hotspotList);
            if (graphicData.sheetId) {
                var selectedSheet = Cortona3DSolo.app.getDocumentInfo().sheets[graphicData.sheetId].id;
                Cortona3DSolo.app.ipc.setCurrentSheet(selectedSheet);
                document.getElementById("choice_sheet").value = selectedSheet;
            } else {
                Cortona3DSolo.app.ipc.setCurrentSheet(Cortona3DSolo.app.getDocumentInfo().sheets[0].id);
            }
            return;
        }
        if (figureType === 'procedure') {
            document.body.classList.add('ready');
            Cortona3DSolo.app.procedure.play();
            return;
        }
        if (figureType === 'generic') {
            //Cortona3DSolo.app.fitSceneInView(false);
            //URL.revokeObjectURL(dataURL);
            if(simicImage && simicImage.content){
                    Cortona3DSolo.app.createObjectsFromURL(graphicData.resource).then(function (hdles) {
                    Cortona3DSolo.app.addObjects(hdles);
                    var positions = simicImage.xyzPosition.split(",");
					var translationValue = simicImage.translationValue;
                    hdles.forEach(function (handle) {
                        Cortona3DSolo.app.setObjectPropertyf(handle, Cortona3DSolo.app.PROPERTY_TRANSLATION, true, 0-parseFloat(positions[0]-translationValue), 0-parseFloat(positions[1]), 0-parseFloat(positions[2]));
                    });
                    collectandHideParts(hotspotList);
                    hideItemsNotAvailableInDPLTable(Cortona3DSolo, figureType, hotspotList);
                    //hideItemsNotAvailableInDPLTable();
                    // Cortona3DSolo.app.jumpToStandardView("isometric", true);
                    // Cortona3DSolo.app.centerRotationCenterInView(true);

                    Cortona3DSolo.app.createObjectsFromURL(simicImage.content).then(function (hdles) {
                        Cortona3DSolo.app.addObjects(hdles);
                        hdles.forEach(function (handle) {
                            Cortona3DSolo.app.setObjectPropertyf(handle, Cortona3DSolo.app.PROPERTY_TRANSPARENCY, true, TRANSPARENT);
                            Cortona3DSolo.app.setObjectIgnorableByPicker(handle, true);
                        });
                        setTimeout(Cortona3DSolo.app.fitSceneInView, 500);
                    }).catch(console.error.bind(console));
                }).catch(console.error.bind(console));





            }

            // else{
            //         Cortona3DSolo.app.createObjectsFromURL(graphicData.resource).then(function (hdles) {

            //             Cortona3DSolo.app.addObjects(hdles);


            //             //hideItemsNotAvailableInDPLTable();
            //             Cortona3DSolo.app.jumpToStandardView("isometric", true);
            //             Cortona3DSolo.app.centerRotationCenterInView(true);
            //             collectandHideParts(hotspotList);
            //             hideItemsNotAvailableInDPLTable(Cortona3DSolo, figureType, hotspotList);
            //         }).catch(console.error.bind(console));

            //     }




        }

        // processing mouse movement over a 3D object
        Cortona3DSolo.core.canvas.addEventListener('mousemove', function (event) {
            var selectedObject = queryPartnbrFromClickEvent(event,false);
            if(selectedObject && selectedObject !== constNotFound){
                document.body.title = selectedObject;
            }else{
                document.body.title = "";
            }

        });

        // processing of a click on a 3D object

        Cortona3DSolo.core.canvas.addEventListener('click', function (event) {
            // prevent clicks processing during navigation in the 3D scene
            var selectedObject = queryPartnbrFromClickEvent(event,true);
            if(selectedObject && partList.length >0){
                var param = {};
                param.hotspotType = "PARTNUMBER_HOTSPOT";
                param.hotspotValue = selectedObject
                postHotspotMessage(param);

            }

        });
    };

	Cortona3DSolo.expand(Cortona3DSolo.app.procedure, {
                didChangePlayerState: function (position, state) {
                     m_played = !!(state & 1);
					 document.getElementById('btn_play').style.display = m_played ? 'none' : '';
					 document.getElementById('btn_pause').style.display = m_played ? '' : 'none';
                     m_range.value = position;
                }
    });

    Cortona3DSolo.app.ipc.didSelectSheet = function (sheet) {
        Cortona3DSolo.app.dplTable = sheet.dplTable;
    };
    function precisionRound(number, precision) {
        var factor = Math.pow(10, precision);
        return Math.round(number * factor) / factor;
    }

    function printGraphic(base64){
       if(window.parent.printGraphic){
           window.parent.printGraphic(base64)
       }
    }

    Cortona3DSolo.app.onProgress = function(position, total) {
        //  console.log("onProgress", position, total);
        var progressEle = document.getElementById("wrlProgressCurrent");
        var totalEle = document.getElementById("wrlProgressTotal");

        if(!totalEle) return;
        if (total > 0) {
            totalEle.innerText = precisionRound(total / 1048576, 1);
            totalEle.style.display = '';
        } else {
            totalEle.style.display = 'none';
        }
        if (position > 0) {
            progressEle.innerText = precisionRound(position / 1048576, 1);
            progressEle.style.display = '';
        } else {
            progressEle.style.display = 'none';
        }
    };


     if(!(simicImage && simicImage.content)){
        Cortona3DSolo.app.initialize(graphicData.resource);
     }else{
        Cortona3DSolo.app.initialize();
     }

}
