/**
 * @copyright (c) 2016 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

/**
 * The user opens the URL of page in pop-up dialog by Ctrl-Alt-C keys. GOTO Service parses the URL 
 * fetched from the window in browser, and then it requests additional information from the server. 
 * When the GOTO Service receives the response then it broadcasts message to other widgets. 
 * The URL <optional> format: <protocol>//<hostname>:<port>/<path>/#/main/goto?<params>
 **/

/**
 * GotoService
 * @requires $rootScope
 * @requires $location
 * @requires $timeout
 * @requires DataService
 **/
angular.module('app').service('GotoService', function($rootScope, $location, $timeout, DataService, $translate, $window) {

    var urlObject = null;
    var gotoResourcePathUrl = "";
    var invalidPublication="app.error.invalidPublication";
    var bbHandlerShowRevision='button[data-bb-handler=showRevision]';
    var bbHandlerUseIds='button[data-bb-handler=useIds]';
    var bbHandlerUsePath='button[data-bb-handler=usePath]';
    var gotoUrlId='#GoToURLContent';
    var gotoUrlContentTextId='#gotoUrlContentText';
    var RESTRICTEDFRAGMENT = 'restrictedfragment';

    var self = this;
    /**
     * Parse navigation query string from the browser.
     */
     this.getRouteParameters = function () {
        self.params = $location.search();
        self.absUrl = $location.absUrl();
        self.url = $location.url();
        urlObject = sanityCheck(self.params);
        if (urlObject === null) {
            return;
        }
        urlObject.incomplete = true;
        this.setParams(self.params);
    };

    this.setParams = function() {
        if (urlObject && urlObject.incomplete) {
            setLibraryAndPublication(self.params);
            setNewViewerProperty(self.params);
            delete(urlObject.incomplete);
            $rootScope.topLibraryId = urlObject.library;
            $rootScope.gotoSource = "URL";
            if (self.params.module === RESTRICTEDFRAGMENT) {
                $rootScope.display = "iframe";
            } else if (self.params.display) {
                $rootScope.display = self.params.display;
            }
        }
    };
  
    
    var sanityCheck = function(params) {
        if(!isNotNull(params) || $.isEmptyObject(params)) {
            return null;
        }
        var errorConditions = [
            // This allows "library=&libraryName=something" because library is given a falsy value: ""
            {
                "message": $translate.instant("app.error.libraryIDAndNameCoexist"),
                "condition": Boolean(params.library && params.libraryName)
            },{
                "message": $translate.instant("app.error.invalidLibraryPublication"),
                "condition": Boolean(!params.library && !params.libraryName && !params.publicationID && !params.publicationName && !params.resourcePath)
            },{
                "message": $translate.instant("app.error.invalidLibrary"),
                "condition": Boolean(!params.library && !params.libraryName && !params.resourcePath)
            },{
                "message": $translate.instant("app.error.publicationAndNameCoexist"),
                "condition": Boolean(params.publicationID && params.publicationName)
            },{
                "message": $translate.instant("app.error.documentIDAndNameCoexist"),
                "condition": Boolean(params.documentID && params.documentCode)
            },{
                "message": $translate.instant("app.error.invalidDocument"),
                "condition": Boolean((params.documentID || params.documentCode) && !(params.publicationName || params.publicationID || params.sourcePublicationId) && !(params.isExternalDoc))
            },{
                "message": $translate.instant(invalidPublication),
                "condition": Boolean(params.filterAttr && !(params.publicationName || params.publicationID))
            },{
                "message": $translate.instant(invalidPublication),
                "condition": Boolean(params.filterAttr) !== Boolean(params.filterAttrValues)
            },{
                "message": $translate.instant("app.error.invalidResourcePath"),
                "condition": Boolean(params.resourcePath && (params.library || params.libraryName ||
                    params.publicationID || params.publicationName || params.filterAttrValues ||
                    params.filterAttr || params.documentID || params.documentCode || params.searchTerm))
            }
        ];
        var i;
        for (i = 0; i < errorConditions.length; i++) {
            if (errorConditions[i].condition) {
                alert(errorConditions[i].message);
                return null;
            }
        }
        return {};
    };

    var setLibraryAndPublication = function(params) {
        if (params.library) {
            urlObject.library = params.library;
        } else if (params.libraryName) {
            urlObject.libraryName = params.libraryName;
        } 
        if (params.publicationID) {
            urlObject.publicationID = params.publicationID;
        } else if (params.publicationName) {
            urlObject.publicationName = params.publicationName;
        }
        if (params.revision) {
            urlObject.revision = params.revision;
        }
        if (params.documentID) {
            urlObject.documentID = params.documentID;
        }else if (params.documentCode) {
            urlObject.documentCode = params.documentCode;
        }
        if (params.filterAttr && params.filterAttrValues) {
            urlObject.filterAttr = params.filterAttr;
            urlObject.filterAttrValues = params.filterAttrValues;
        }
        if(params.filterConditions) {
            urlObject.selectedConditions = params.filterConditions;
        }
        if(params.resourcePath){
            urlObject.resourcePath = params.resourcePath;
        }
        if(params.isExternalDoc){
            urlObject.externalDoc = params.isExternalDoc;
        }

        if(params.searchDocNumber){
            urlObject.searchDocNumber = params.searchDocNumber;
        }
        if (params.documentTitle) {
            urlObject.documentTitle = params.documentTitle;
        }
        if(params.publicationTitle){
            urlObject.publicationTitle = params.publicationTitle;
        }
        if(params.isPubTitleMatch){
            urlObject.pubTitleMatch = params.isPubTitleMatch;
        }
        if (params.module) {
            urlObject.module = params.module;
            $rootScope.isRestrictedFragment = isRestrictedFragment(params.module);
        }
        if(params.sourceDocumentId){
            urlObject.sourceDocumentId = params.sourceDocumentId;
        }
        if(params.sourcePublicationId){
            urlObject.sourcePublicationId = params.sourcePublicationId;
        }
        if(params.anchor){
            urlObject.anchorId = params.anchor;
        }
    };

    /**
     * Clear navigation query string in the browser.
     */
    this.clearRouteParameters = function () {
            var libPubParam = getLibPubParams($location.$$search);
            self.params = $location.$$search;
            self.originalUrl = $location.$$absUrl;
            $location.$$search = {};
            $location.$$compose();
            $location.path('/main').search(libPubParam);
        
    };
    
    function setNewViewerProperty(params) {
        if (params && params.newViewer && params.newViewer === 'true') {
        	$rootScope.showEulaPopup = false;
        }
    }

    this.updateSelectedCategoryFilter = function (responses) {
        var categoryFilterMap = {};
        for (var categoryIndex in $rootScope.selectedCategoryFilter) {
            for (var filterObject in $rootScope.selectedCategoryFilter[categoryIndex]) {
                categoryFilterMap[filterObject] = $rootScope.selectedCategoryFilter[categoryIndex];
            }
        }
        var publicationFilterCategory = isNotNull(responses[0].publication) && isNotEmpty(responses[0].publication.filterCategory) ? responses[0].publication.filterCategory : "ALL";
        var doesResponseContainFilterData = isNotNull(responses[0].filter.filterRowId);
        if (doesResponseContainFilterData){
            if (!categoryFilterMap.hasOwnProperty(publicationFilterCategory)){
                var newFilterObject = {};
                newFilterObject[publicationFilterCategory] = null;
                $rootScope.selectedCategoryFilter.push(newFilterObject);
                categoryFilterMap[publicationFilterCategory] = newFilterObject;
            }
            categoryFilterMap[publicationFilterCategory][publicationFilterCategory] = $rootScope.selectedFilter;
        }
        // If preselected filter values matched with different publications in the same library while switching from one
        // publication to another with a Cors reference link displaying filter text will be updated with current publication selected filter text.
        // this if condition for validate to Goto URL with preselected filter values and without filter values in URL.
        if($rootScope.selectedFilter.filterAttrValues&&self.params){
            var library = isNotNull(self.params.library)?{"id":self.params.library}:{"id":responses[0].library.id};
            var publication = isNotNull(self.params.publicationID)?{"id":self.params.publicationID,"filterCategory":publicationFilterCategory}:{"id":responses[0].publication.id,"filterCategory":publicationFilterCategory};
            DataService.updatePublicationFilters(library,publication, $rootScope.selectedFilter.filterAttr, $rootScope.selectedFilter.filterAttrValues);
        }
    }

    /**
     * Receiving the JSON response from the server.
     */
    function getGotoResponse(responses) {
        var message = {};
        if (isNotNull(responses) && isNotNull(responses[0])) {
            if(self.params && isRestrictedFragment(self.params.module)){
                if (isNotNull(responses[0].library)) {
                    var message = { responses: responses };
                    $rootScope.$broadcast("viewRestrictedFragmentContent", message);
                }
            } else {
                if (isNotNull(responses[0].library)) {
                    message.library = responses[0].library;
                    $rootScope.modelIdentCode = responses[0].library.modelIdentCode;
                }

            if(isNotNull(responses[0].publication)) {
                message.publication = responses[0].publication;
                message.publication.showPublicationLandingPage = true;
                message.publication.mfrname = isNotNull(message.publication.metadata)? message.publication.metadata.mfrname:"";
                message.publication.revision = isNotNull(message.publication.metadata)? message.publication.metadata.release:"";
                message.publication.current = responses[0].publication.metadata.current;
            }

            if(isNotNull(responses[0].page)) {
                message.page = {};
                message.page.source = "GOTO";

                if(isNotNull(responses[0].page.refkey) && !isBlank(responses[0].page.refkey)) {
                    message.page.refkey = encodeSpecialRefkey(responses[0].page.refkey);
                    message.publication.showPublicationLandingPage = false;
                }

                if (isNotNull(responses[0].page.refcode) && !isBlank(responses[0].page.refcode)) {
                    message.page.refcode  = responses[0].page.refcode;
                    message.publication.showPublicationLandingPage = false;
                }

                if(isNotNull(responses[0].page.type)) {
                    message.page.type = responses[0].page.type;
                }

                if(isNotNull(responses[0].page.title)) {
                    message.page.title = responses[0].page.title;
                }
                if(isNotNull(self.params) && self.params.anchor){
                    message.page.anchor = self.params.anchor;
                }
            }

            if (isNotNull(self.params) && self.params.searchTerm) {
                message.search = {};
                message.search.searchTerm = self.params.searchTerm;
                message.page.keyword = self.params.searchTerm;
                if (self.params.searchIndex) {
                    message.page.searchIndex = self.params.searchIndex;
                }
                if (message.publication) {
                    message.search.publication = message.publication;
                }
            }

            if(isNotNull(self.params) && self.params.searchDocNumber){
                message.docId = self.params.searchDocNumber;
            }

            if(isNotNull(self.params) && !self.params.publicationID){
               if(self.params.anchor){
                    message.anchorKey =  self.params.anchor;
                }
            }

            if(isNotNull(self.params) && self.params.preSelectedAttachment){
                message.preSelectedAttachment = self.params.preSelectedAttachment;
            }

            if(isNotNull(self.params) && self.params.search) {
                var search = JSON.parse(self.params.search);
                if(isNotNull(message.page)) {
                    message.page.source = search.source;
                    message.page.keyword = search.keyword;
                    message.page.isMatchWholeWord = search.isMatchWholeWord;
                }
            }

            //Do not refresh filter for bookmark goto
            if($rootScope.gotoSource !== "BOOKMARK"){
                $rootScope.selectedFilter = {};
                $rootScope.selectedFilter.filterId = responses[0].filter.filterId;
                $rootScope.selectedFilter.filterAttr = responses[0].filter.filterAttr;
                $rootScope.selectedFilter.filterAttrValues = responses[0].filter.filterAttrValues;
                $rootScope.selectedFilter.filterRowId = responses[0].filter.filterRowId;
                $rootScope.selectedFilter.filterType = responses[0].filter.filterType;
                $rootScope.selectedFilter.selectedConditions = responses[0].filter.selectedConditions;
                if(responses[0].filter.showIdentifier && responses[0].filter.selectedFilterValues) {
                    $rootScope.selectedFilter.readableFilterAttrValues = getTitleFromSelectedFilter(responses[0].filter.showIdentifier, responses[0].filter.selectedFilterValues, responses[0].filter.filterType);
                }
                else {
                    $rootScope.selectedFilter.readableFilterAttrValues = getTitleFromSelectedFilter(responses[0].filter.filterAttr, responses[0].filter.filterAttrValues, responses[0].filter.filterType);
                }
                if (responses[0].filter.selectedPrimaryAttribute && responses[0].filter.selectedRows) {
                    $rootScope.selectedFilter.selectedPrimaryAttribute = responses[0].filter.selectedPrimaryAttribute;
                    $rootScope.selectedFilter.selectedRows = responses[0].filter.selectedRows;
                }
                self.updateSelectedCategoryFilter(responses);
            }
                if( $rootScope.appConfiguration &&
                    $rootScope.appConfiguration.publicationLockDuration &&
                $rootScope.appConfiguration.publicationLockDuration > -1) {
                $rootScope.$broadcast("lockPublication",{});
            } else if (message && message.publication && message.publication.current && 'false' === message.publication.current && $rootScope.appConfiguration.isServer === false) {
                bootbox.confirm({
                    message: $translate.instant("app.alert.currentRevisionOnly"),
                    buttons: {
                        confirm: {
                            label: $translate.instant("app.title.sync"),
                            className: 'btn-primary'
                        },
                        cancel: {
                            label: $translate.instant("app.title.cancel"),
                        }
                    },
                    callback: function (result) {
                        if (result) {
                            var message = { type: 'ImportStatusTab' };
                            $rootScope.$broadcast("importStatus", message);
                        }
                    },
                    className: 'cRevisionConfirmDialog'
                });
            } else {
                $rootScope.$broadcast("gotoUpdated", message);
            }
        }
        }

        responses = null;
    }

    /**
     * Request URL parameters information from the server in payload.
     */
    function setGotoRequest(message) {
        var actions = [];
        if(!message.topLibraryId && $rootScope.topLibraryId){
            message.topLibraryId = $rootScope.topLibraryId;
        }
        var library = {id: message.topLibraryId};
        if(urlObject.module){
            for(var i=0;i<$rootScope.baseActions.length;i++){
                if($rootScope.baseActions[i].type === 'PINPOINT'){
                   library.baseAction = $rootScope.baseActions[i];
                }
            }
        }

        if (!isBlank(library.id) && isNotNull(urlObject)) {
            if(urlObject.resourcePath){
                urlObject.library = message.library;
                urlObject.publicationID = message.publicationID;
                if(message.documentID && message.documentID.toLowerCase() === 'pdf'){
                    urlObject.documentID = message.documentID;
                }
            }
            if (self.params && self.params.revision) {
                urlObject.revision = self.params.revision;
            }

            var action = DataService.generateWidgetAction(library, "/goto", "POST", urlObject);
            $rootScope.baseAction = library.baseAction;
            if (isNotNull(action)) {
                actions.push(action);
                DataService.actionsDriver(actions, getGotoResponse,null,$);
            }
        }
        urlObject = null;
    }

    /**
     * Decide when user can view revision params.
     */
    this.canViewRevision = function () {
        return $rootScope.gotoParams.library.isPinpoint;
    };

    this.generateGoToUrl = function(params) {

        var paramsUrl = "";
        var gotoUrl = "";
        var resourcePathParam = "";

        if (isNotNull(params)) {
            if (isNotNull(params.content)){
                paramsUrl += isBlank(params.content.libraryID) ? "" : "library=" + params.content.libraryID;
                paramsUrl += isBlank(params.content.publicationID) ? "" : "&publicationID=" + params.content.publicationID;
                paramsUrl += isBlank(params.content.documentID) ? "" : "&documentID=" + encodeSpecialRefkey(params.content.documentID);
                paramsUrl += isBlank(params.content.revision)? "" : "&revision=" + params.content.revision;
                paramsUrl +=isBlank(params.content.title)? "":"&documentTitle="+encodeSpecialRefkey(params.content.title);
            } else if (isNotNull(params.library) && isNotNull(params.library.libraryID) && isNotNull(params.library.publicationID)) {
                paramsUrl += isBlank(params.library.libraryID) ? "" : "library=" + params.library.libraryID;
                paramsUrl += isBlank(params.library.publicationID) ? "" : "&publicationID=" + params.library.publicationID;
                if (isNotNull(params.library.publicationRevision) && !isBlank(params.library.publicationRevision)) {
                    paramsUrl += "&revision=" + params.library.publicationRevision;
                }
            }
            if (!isBlank(paramsUrl)) {
                if (params.filter && !isBlank(params.filter.filterAttr) && !isBlank(params.filter.filterAttrValues)) {
                    paramsUrl += "&filterAttr=" + params.filter.filterAttr + "&filterAttrValues=" + params.filter.filterAttrValues;
                }
                if(params.filter && isNotEmptyArray(params.filter.selectedConditions)) {
                    paramsUrl += "&filterConditions=" + encodeURIComponent(this.getSelectedConditions(params.filter.selectedConditions));
                }
                if(isNotNull(params.search) && !isJsonObjectEmpty(params.search)) {
                    paramsUrl += "&search=" + encodeURIComponent(JSON.stringify(params.search));
                }
                if(isNotEmpty(params.searchDocNumber)) {
                    paramsUrl += "&searchDocNumber=" + encodeURIComponent(params.searchDocNumber);
                }
                if(isNotEmpty(params.anchor)){
                    paramsUrl += "&anchor=" +params.anchor;
                }
                if (!isBlank(params.sourcePublicationId)){
                    paramsUrl += "&sourcePublicationId=" + params.sourcePublicationId;
                }
                if(params.isExternalDoc && params.isExternalDoc === true){
                    paramsUrl += "&isExternalDoc=true";
                    if (isNotNull(params.sourceDocumentId)){
                        paramsUrl += "&sourceDocumentId=" + params.sourceDocumentId;
                    }
                }
                if(isNotEmpty(params.publicationTitle)) {
                    paramsUrl += "&publicationTitle=" + encodeURIComponent(params.publicationTitle);
                }
                if(params.isPubTitleMatch && params.isPubTitleMatch === true) {
                    paramsUrl += "&isPubTitleMatch=true";
                }
                paramsUrl += "&newViewer=true";
            }
            if(isNotNull($rootScope.gotoResourcePath)){
                resourcePathParam = isBlank($rootScope.gotoResourcePath) ? "" : "resourcePath=" + encodeURIComponent($rootScope.gotoResourcePath);

                // PORTALMIG-1018 spaces and forward slashes should not be uri encoded
                resourcePathParam = resourcePathParam.replace(/%2F/g, '/').replace(/%20/g, ' ');
            }
        }
        if(!isBlank(paramsUrl)){
            gotoUrl = $location.absUrl().replace($location.url(),"/main/goto?" + paramsUrl);
        }
        if(!isBlank(resourcePathParam)){
            gotoResourcePathUrl = $location.absUrl().replace($location.url(),"/main/goto?" + resourcePathParam);
        }
        if (isNotNull(params.content) && isNotEmpty(params.content.anchor)){
            gotoUrl += "&anchor=" + params.content.anchor;
        }
        return gotoUrl;
    };

    this.getSelectedConditions = function (selectedCondition) {
        var selectedConditionIdValue = "";
        selectedCondition.forEach(function (condition) {
            if(isNotEmpty(selectedConditionIdValue)) {
                selectedConditionIdValue += ",";
            }
            selectedConditionIdValue += condition.id + "=" + condition.selected;
        });
        return selectedConditionIdValue;
    };

    this.addViewRevisionParam = function (gotoUrl, params, fromUseIDs) {
        if (self.canViewRevision()) {
            if (params.content.publicationRevision) {
                gotoUrl += "&revision=" + params.content.publicationRevision;
            }
            if (fromUseIDs && gotoUrl.indexOf("documentTitle") === -1 && params.content.title) {
                gotoUrl += "&documentTitle=" + encodeURIComponent(params.content.title);
            }
        }
        return gotoUrl;
    };

    this.onGoToDialog = function(event) {
        event.stopPropagation();
        if (event.ctrlKey && event.altKey && (String.fromCharCode(event.which) === 'c' || String.fromCharCode(event.which) === 'C')) {
            self.openGoToLinkDialog();
        }

        return false;
    };
    
    this.openGoToLinkDialog = function() {
            $rootScope.gotoParams = {"filter": angular.copy($rootScope.selectedFilter)};
            $rootScope.$broadcast("gotoUpdate", {});

            $timeout(function() {

                var gotoIdsURL = self.generateGoToUrl($rootScope.gotoParams);
                var gotoURL = gotoIdsURL;
                var showRevisionLabel = $translate.instant("app.title.showRevision");
                var buttonLabel = $translate.instant("app.title.copy");
                var useIdsLabel = $translate.instant("app.title.useIds");
                var usePathLabel = $translate.instant("app.title.usePath");

                var buttons = {};

                if(!isBlank(gotoResourcePathUrl)){
                    if (self.canViewRevision()) {
                        buttons.showRevision = {
                            label: '<i class="fa fa-square-o"></i> ' + showRevisionLabel,
                            className: "btn-white",
                            callback: function () {
                                if ($(bbHandlerShowRevision).hasClass('checked')) {
                                    $(bbHandlerShowRevision).removeClass('checked').html('<i class="fa fa-square-o"></i> ' + showRevisionLabel);
                                    gotoURL = $(bbHandlerUseIds).hasClass('btn-info') ? gotoIdsURL : gotoResourcePathUrl;
                                } else {
                                    $(bbHandlerShowRevision).addClass('checked').html('<i class="fa fa-check-square"></i> ' + showRevisionLabel);
                                    gotoURL = $(bbHandlerUseIds).hasClass('btn-info') ? self.addViewRevisionParam(gotoIdsURL, $rootScope.gotoParams, true) : self.addViewRevisionParam(gotoResourcePathUrl, $rootScope.gotoParams, false);
                                }
                                $(gotoUrlId).html(gotoURL);
                                $(gotoUrlContentTextId).html(gotoURL);
                                return false;
                            }
                        };
                    }
                    buttons.useIds = {
                        label: useIdsLabel,
                        className: "btn-info",
                        callback: function () {
                            if (!$(bbHandlerUseIds).hasClass('btn-info')) {
                                gotoURL = $(bbHandlerShowRevision).hasClass('checked') ? self.addViewRevisionParam(gotoIdsURL, $rootScope.gotoParams, true) : gotoIdsURL;
                                $(bbHandlerUsePath).attr('class','btn btn-secondary');
                                $(bbHandlerUseIds).attr('class','btn btn-info');
                                $(gotoUrlId).html(gotoURL);
                                $(gotoUrlContentTextId).html(gotoURL);
                            }
                            return false;

                        }
                    };

                    buttons.usePath = {
                        label: usePathLabel,
                        className: "btn-secondary",
                        callback: function () {
                            if (!$(bbHandlerUsePath).hasClass('btn-info')) {
                                gotoURL = $(bbHandlerShowRevision).hasClass('checked') ? self.addViewRevisionParam(gotoResourcePathUrl, $rootScope.gotoParams, false) : gotoResourcePathUrl;
                                $(bbHandlerUsePath).attr('class','btn btn-info');
                                $(bbHandlerUseIds).attr('class','btn btn-secondary');
                                $(gotoUrlId).html(gotoURL);
                                $(gotoUrlContentTextId).html(gotoURL);
                            }
                            return false;
                        }
                    };
                }

                buttons.ok = {
                    label: buttonLabel,
                    className: "btn-primary",
                    callback: function () {
                        var pathParseRegex = RegExp("(.*/)?(.*)/(.*)");
                        var libraryName = $rootScope.gotoParams.content.libraryID;
                        var publicationName = $rootScope.gotoParams.content.publicationID;
						if(isNotEmpty($rootScope.gotoResourcePath)){
							libraryName = $rootScope.gotoResourcePath.replace(pathParseRegex,"$2");
							publicationName = $rootScope.gotoResourcePath.replace(pathParseRegex,"$3");
						}
                        $rootScope.lastCopiedGotoUrl = {
                            title : [libraryName,publicationName,$rootScope.gotoParams.content.title].join('/'),
                            url: gotoURL
                        };
                        angular.element("#gotoUrlContentText").select();
                        document.execCommand("copy");
                    }
                };

                if(!isBlank(gotoURL)) {
                    var box = bootbox.dialog({
                        title: 'URL',
                        size: 'large',
                        message: '<div id="GoToURLContent">' + gotoURL + '</div> <textarea id="gotoUrlContentText">' + gotoURL +'</textarea>',
                        buttons: buttons
                    }); 
                }
            },100);
    };

    this.openContentInNewTabOrWindow = function (params, isOpenNewWindow) {
        if(!isNotEmptyArray(params)){
            $rootScope.gotoParams = {"filter": angular.copy($rootScope.selectedFilter)};
            $rootScope.$broadcast("gotoUpdate", {});
        }
        var gotoURL = isNotNull(params) ? self.generateGoToUrl(params) : self.generateGoToUrl($rootScope.gotoParams);

        if($rootScope.gotoParams && $rootScope.gotoParams.acknowledgedAttachments && Object.keys($rootScope.gotoParams.acknowledgedAttachments).length > 0){
            gotoURL +="&preSelectedAttachment=" + encodeURIComponent(this.getAcknowledgedAttachmentsID($rootScope.gotoParams.acknowledgedAttachments));
        }
        if(isNotNull($rootScope.openDocumentInNewTabOrWindow) && $rootScope.openDocumentInNewTabOrWindow.enabled && $rootScope.openDocumentInNewTabOrWindow.forceIFrameMode){
           gotoURL += "&display=iframe";
        }

        $timeout(function(){
            if(isOpenNewWindow){
                $window.open(gotoURL, "_blank", "menubar=yes,statusbar=yes,toolbar=yes,resizable=yes");
            }else{
                $window.open(gotoURL);
            }
        }, 100);
    }

    this.getAcknowledgedAttachmentsID = function (acknowledgedAttachments) {
        var attachmentsId = "";
        if(Object.keys(acknowledgedAttachments).length > 0) {
            for(var acknowledgedAttachmentsId in acknowledgedAttachments){
                if(isNotEmpty(attachmentsId)){
                    attachmentsId += ",";
                }
                attachmentsId += acknowledgedAttachmentsId;
            }

        }
        return attachmentsId;
    };

    /**
     * Set urlObject value for urlObject
     *
     */
    this.setUrlObjectValue = function (value) {
        urlObject = value;
    };

    /**
     * Call gotoResponse with responseData
     */
    this.setGotoResponse = function (responseData) {
        getGotoResponse(responseData);
    };

    /**
     * Event handler for gotoInit event
     * @function onGotoInit
     * @param {Object} event
     * @param {Object} message
     * @listens app:gotoInit
     */
    var onGotoInit = function(event, message)
    {
        if(isNotNull(urlObject)) {
            setGotoRequest(message);
        }
    };

    var onOpenBookmark = function(event, message){
        $rootScope.gotoSource = "BOOKMARK";
        urlObject = {};
        urlObject.library = message.libraryId;
        urlObject.publicationID = message.publicationId;
        //Here decode first is because currently we didn't do any decode thing at pp server side when save bookmark, so the key stored in db is encoded one for special key
        if(message.targetType !== "PUB"){
            urlObject.documentID = encodeSpecialRefkey(decodeURIComponent(message.refkey));
        }
        onGotoInit(event, message);
    };

    var onOpenPublication = function(event, message){
        self.params = message;
        $rootScope.gotoSource = !isBlank(message.source)? message.source.toUpperCase() : "UNKNOWN";
        urlObject = {};
        urlObject.library = message.library.id;
        urlObject.libraryName = message.library.name;
        if(message.publication.id){
            urlObject.publicationID = message.publication.id;
        }else if(message.publication.name){
            urlObject.publicationName = message.publication.name;
        }
        if(message.publication.revision){
            urlObject.revision = message.publication.revision;
        }
        //When open PDF publication, need to close read and sign tab as pdf publication do not have toc
        if(message.publication.type && message.publication.type.toUpperCase() === "PDF") {
            urlObject.documentID = "PDF";
        }else{
            if(!isBlank(message.documentID)){
                urlObject.documentID = message.documentID;
            }else if(!isBlank(message.refkey)){
                urlObject.documentID = encodeSpecialRefkey(decodeURIComponent(message.refkey));
            }
            if(message.filterAttr && message.filterAttrValues){
                urlObject.filterAttr = message.filterAttr;
                urlObject.filterAttrValues = message.filterAttrValues;
            }
        }
        onGotoInit(event, message);
    };

    $rootScope.$on("gotoInit",onGotoInit);

    $rootScope.$on("openBookmark", onOpenBookmark);

    $rootScope.$on("openPublicationReady", onOpenPublication);

});