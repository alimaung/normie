/*
 *
 * To apply applicability to the document,
 * send in a list of strings to: Applicability.apply([])
 *
 * By default it will apply dynamic list numbering.
 * If you want to use static numbering: Applicability.apply([], false)
 *
 * To show display text: Applicability.showDisplayText()
 * To hide display text: Applicability.hideDisplayText()
 *
 */

var Applicability = new function () {

    this.apply = function (applicRefIdList, dynamicListNumbering) {
        dynamicListNumbering = typeof dynamicListNumbering !== 'undefined' ? dynamicListNumbering : true;

        $('[applicid]').each(function () {
            var currentApplicRefId = $(this).attr('applicid');

            if (applicRefIdListIsEmpty(applicRefIdList) || applicRefIdIsInArray(currentApplicRefId, applicRefIdList)) {
                showApplicable(this, dynamicListNumbering);
            } else {
                hideNonApplicable(this, dynamicListNumbering);
            }
        });
        postApplicability();
    };

    function applicRefIdIsInArray(currentApplicRefId, applicRefIdList) {
        return ($.inArray(currentApplicRefId, applicRefIdList) != -1);
    }

    function applicRefIdListIsEmpty(applicRefIdList) {
        return (typeof applicRefIdList === 'undefined' || applicRefIdList.length === 0);
    }

    function showApplicable(applicElement, dynamicListNumbering) {
        if ($(applicElement).attr('hiddenByApplic') == 'true') {
            var elementToApplyOn = getElementsToHide(applicElement, dynamicListNumbering);
            $(elementToApplyOn).show();
            $(applicElement).attr('hiddenByApplic', 'false');

            if($(applicElement).is('div') && (dynamicListNumbering === false)) {
                $(applicElement).parent().removeClass('invisible');
            }
        }
    }

    function hideNonApplicable(applicElement, dynamicListNumbering) {
        if (($(applicElement).parent().css('display') !== 'none')) {
            var elementToApplyOn = getElementsToHide(applicElement, dynamicListNumbering);

            $(elementToApplyOn).hide();
            $(applicElement).attr('hiddenByApplic', 'true');

            if($(applicElement).is('div') && (dynamicListNumbering === false)) {
                $(applicElement).parent().addClass('invisible');
                // Show the Figure title, to get the counting of elements right.
                $(applicElement).parent().find('.figTitle').show();
            }
        }
    }

    function getElementsToHide (applicElement, dynamicListNumbering) {
        var elements = applicElement;

        if ($(applicElement).is('div')) {
            if(isListOrFigure(applicElement) && (dynamicListNumbering === false)) {
                elements = $(applicElement).siblings();
            } else {
                elements = $(applicElement).parent();
            }
        }
        return elements;
    }

    function isListOrFigure(element) {
        return ($(element).parent().is('li')
        || $(element).parent().hasClass('multimedia')
        || $(element).parent().hasClass('graphic')
        || $(element).parent().hasClass('figure'));
    }

    function postApplicability() {
        countTotalSheetsInFigures();
    }

    this.showDisplayText = function () {
        $('div[applicid]').each(function () {
            $(this).show();
        });
    };

    this.hideDisplayText = function () {
        $('div[applicid]').each(function () {
            $(this).hide();
        });
    };
}();$(document).ready(function(){
    countTotalSheetsInFigures();
});

function countTotalSheetsInFigures () {
    $('.figure:visible').each( function(index, figure) {

        var sheets = $(figure).find(".graphic-total:visible");

        sheets.each(function(index, sheet) {
            $(sheet).text(sheets.length.toString());
        });
    });
}
setPolyfills();

// These will only be used by wkhtmltopdf. They can be removed when support for that is dropped.
function setPolyfills() {

    /**
     * Element.closest() polyfill
     * https://developer.mozilla.org/en-US/docs/Web/API/Element/closest#Polyfill
     */
    if (!Element.prototype.closest) {
        if (!Element.prototype.matches) {
            Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
        }
        Element.prototype.closest = function (s) {
            var el = this;
            var ancestor = this;
            if (!document.documentElement.contains(el)) return null;
            do {
                if (ancestor.matches(s)) return ancestor;
                ancestor = ancestor.parentElement;
            } while (ancestor !== null);
            return null;
        };
    }

    /**
     * String.prototype.includes() polyfill
     * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/includes#Polyfill
     */
    if (!String.prototype.includes) {
        String.prototype.includes = function(search, start) {
            'use strict';

            if (search instanceof RegExp) {
                throw TypeError('first argument must not be a RegExp');
            }
            if (start === undefined) { start = 0; }
            return this.indexOf(search, start) !== -1;
        };
    }

    /**
     * Array.filter() polyfill
     */
    // From https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter
    if (!Array.prototype.filter) {
        Array.prototype.filter = function(func, thisArg) {
            'use strict';
            if ( ! ((typeof func === 'Function' || typeof func === 'function') && this) )
                throw new TypeError();

            var len = this.length >>> 0,
                res = new Array(len), // preallocate array
                t = this, c = 0, i = -1;
            if (thisArg === undefined)
            while (++i !== len)
                // checks to see if the key was set
                if (i in this)
                if (func(t[i], i, t))
                    res[c++] = t[i];
            else
            while (++i !== len)
                // checks to see if the key was set
                if (i in this)
                if (func.call(thisArg, t[i], i, t))
                    res[c++] = t[i];

            res.length = c; // shrink down array to proper size
            return res;
        };
    }
}

function funcToBeCalledBeforeScroll(scrollToNode, settings) {
    //check for pinpoint client
    var tab = scrollToNode.parents("#tab-content");
    var scrollParent;
    var isMobile = false;
    if (tab.length == 0) {
        //Mobile
        isMobile = true;
        tab = scrollToNode.parents("#contentPage #content");
        scrollParent = $(window);
    } else {
        tab = scrollToNode.parents("[class^=corena-s1000d]").parent().parent();
        scrollParent = tab.parent();
    }
    var pillsDiv = scrollToNode.parents(".pills-toggle");
    if (scrollToNode.is(":visible") == false && pillsDiv.length > 0) {
        var eventData = {tab:tab, scrollp:scrollParent, tabContent: tab};
        pillsDiv.find("[href=#" + pillsDiv.find(scrollToNode.parents(".tab-pane:first")[0]).attr("id") + "]").click();
        if (!isMobile) {
            handleScrollDone(eventData);
        }
    } else if ( pillsDiv.length > 0 && (scrollToNode.offset().top < 0 || pillsDiv.offset().top < 0)) {
        //If the pill is active, make sure it is in view 
        var eventData = {tab:tab, scrollp:scrollParent, tabContent: tab};
        if (!isMobile) {
            handleScrollDone(eventData);
        }
    }
    if (scrollToNode.length > 0 && scrollToNode.hasClass("hotspot")) {
        console.log("Prevent Hotspot Scroll",settings);
        settings.preventScroll = true;
    } else if (scrollToNode.length > 0 && tab.children().find(".pillsNav").length > 0) {
        if (scrollToNode.parents(".pillsNav").length == 0) {
            // Target is outside the Pills section
            var navbar = tab.children().find(".pillsNav");
            settings.offset = {top: -(navbar[0].offsetTop + navbar.height())};
            settings.duration=200;
        } else if (!isPillsFixedOff()) {
            // Target is in the Pills section
            settings.preventScroll = true;
            console.log("Prevent Scroll",settings);
        }
    } else {
        console.log("No Pills",scrollToNode,tab);
    }
}

function funcToBeCalledByPinpointOnEachDocumentLoad(documentId, publicationId,isEmbedded) {
    //check for pinpoint client
    var tab;
    if ($("#html-content").length > 0) {
        if(isEmbedded){
            tab = $("#div_"+documentId);
            documentId = tab.attr("embedded-refkey");
        }
        else {
            tab = $("#" + publicationId + "TabContent");
        }
        onLoadClient(tab, documentId, publicationId,isEmbedded);
        tab = $("#AuthoringTabContent ."+"publication_"+publicationId);
        if(tab.length>0){
          onLoadClient(tab, documentId, publicationId,isEmbedded);
        }
        //check for pinpoint mobile
    } else if ($("#html-div").length > 0) {
        if(isEmbedded){
            tab = $("#content-embedded-div_"+documentId);
            documentId = tab.attr("embedded-refkey");
        }
        else {
            tab = $("#contentPage #content");
        }
        onLoadMobile(tab,documentId,isEmbedded);
    }
}

function getTopOfObject( object ) {
    return object.offset().top - parseInt( object.css( "margin-top" ) );
}

function addCloseToPills(tab, eventData, isMobile) {
    tab.children().on("click", ".pills-toggle li.active", eventData, function (e) {
        e.stopPropagation();
        e.preventDefault();
        $(e.target).closest(".pills-toggle").find(".active").removeClass("active");
    });
    if(!isMobile) {
		tab.children().on("click", ".pillsNav li", eventData, function (e) {
		handleScrollResizeMobile(e);
		setTimeout(function () {
			handleScrollResizeMobile(e);
		}, 200);
	});
	}
}
function getStoredPillsMode() {
    var mode = null;
    if (typeof(Storage) !== "undefined") {
        mode = localStorage.getItem("pillsMode");
    } else {
        console.log("No local storage");
    }
    if (mode == null) {
        //Default to auto
        mode = "auto";
    }
    return mode;
}
function setStoredPillsMode(mode) {
    if (typeof(Storage) !== "undefined") {
        localStorage.setItem("pillsMode",mode);
    } else {
        console.log("No local storage");
    }
}
function isPillsFixedOn() {
    return getStoredPillsMode() == "fixedon";
}
function isPillsAuto() {
    return getStoredPillsMode() == "auto";
}
function isPillsFixedOff() {
    return getStoredPillsMode() == "fixedoff";
}
function improvePills(tab, isEmbedded) {
    var scrollParent = tab.parents("#tab-content");
    if(!isEmbedded) {
        scrollParent.scrollTop(0);
    }
    var navbar = tab.children().find(".pillsNav");
    tab.data("pillsoffsettop",getTopOfObject(tab.scrollParent()));
    tab.data("pillsmode");
    var eventData = {tab:tab, scrollp:scrollParent, tabContent: tab};

    tab.children().off("click.dmcontent");
    scrollParent.off("scroll.dmcontent");
    $(document.body).off("touchmove.dmcontent");

    addCloseToPills(tab, eventData, false);

    if (tab.parent()[0].resizeListener) {
        w2ui['layout'].off("resize",tab.resizeListener);
    }
    if (tab.children().find(".pillsNav").length > 0) {
        scrollParent.on("scroll.dmcontent", null, eventData, handleScrollResizeMobile);
        scrollParent.on("touchmove.dmcontent", null, eventData, handleScrollResizeMobile);
        tab.parent()[0].resizeListener = function(target, data) {
            // Use setTimeout since onComplete does not work,.
            setTimeout(function () {
                handleScrollDone(eventData);
            }, 100);
        };
        w2ui['layout'].on('resize', tab.parent()[0].resizeListener);
    }

}

function changeColspanForApplicabilityInfo(tab) {
    var rowsWithApplicText = $('.applicColspan');
    if (rowsWithApplicText !== null) {
        rowsWithApplicText.each(function (index, element) {
            if ($(element).next().find("td").length > 0) {
                $(element).children().attr("colspan", $(element).next().find("td").length);

            }
            var nextRowToApplicText = $(element).next("tr");
            if (nextRowToApplicText !== null) {
                nextRowToApplicText.css("border-bottom", "1px solid black");
            }
        });
    }

}
function improvePillsMobile(tab, isMobile) {
    var scrollParent = $(window);
    //scrollParent.scrollTop(0);	
    tab.data("pillsoffsettop",53);
    var eventData = {tab:tab, scrollp:scrollParent, tabContent: tab};

    tab.children().off("click.dmcontent");
    $(window).off("scroll.dmcontent");
    $(window).off("resize.dmcontent");
    $(document.body).off("touchmove.dmcontent");

    addCloseToPills(tab, eventData, true);

    if (tab.children().find(".pillsNav").length > 0 && !isMobile) {
        $(window).on("scroll.dmcontent", null, eventData, handleScrollResizeMobile);
        $(window).on("resize.dmcontent", null, eventData, handleScrollResizeMobile);
        $(document.body).on("touchmove.dmcontent", null, eventData, handleScrollResizeMobile);
        handleScrollDone(eventData);
    }
}
function getBottomOfObject( object ) {
    return object.offset().bottom;
}
function handleScrollResizeMobile(event) {
    var scrollTimeout;
    if (event.type == "scroll" && event.data) {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(handleScrollDone.bind(this), 10, event.data, event);
    } else if (event.data) {
        handleScrollDone(event.data,event);
    }
}


function shouldUseFixedPills(tab, scrollParent, navbar, currentWidth, useoffset) {
    var result = false;
    if (isPillsFixedOn()) {
        result = true;
    } else if (isPillsAuto()) {
        var scroll = scrollParent.scrollTop();
        var elementOffset = Math.min(navbar.offset().top,navbar.next() ? navbar.next().offset().top : useoffset);
        if (scroll > 0 && scroll >= (elementOffset-useoffset) && currentWidth > 10) {
            result = true;
            currentOffset = elementOffset;
        }
    } else if (isPillsFixedOff()) {
        result = false;
    }
    return result;
}

function browserSupportsSticky() {
  return typeof(CSS) !== 'undefined'  && "supports" in CSS && CSS.supports("position: sticky");
}

function handleScrollDone(data, event) {
    if (data && data.tab) {
        var tab = data.tab;
        var scrollParent = data.scrollp;
        var navbar = tab.children().find(".pillsNav");
        var ipcGraphic = tab.children().find(".ipc-data-with-fixed-header");
        var ipcTable = tab.children().find(".ipc-table-with-fixed-header");
        var isEmbedded  = ipcTable.parents(".embededContainer");
        var isSecurityClassificationEnabled = document.querySelectorAll("#tab-content #banner-securitycontent").length > 0;
        if (navbar.length > 0) {
            var currentWidth = navbar.parent().width();
            var useoffset = tab.data("pillsoffsettop");
            useoffset = isSecurityClassificationEnabled ? parseInt(useoffset) + 41: useoffset;
            if (shouldUseFixedPills(tab, scrollParent, navbar, currentWidth, useoffset)) {
                var isFixed = navbar.css("position") == "fixed";
                if ($("#html-div").length > 0) {
                    useoffset = "5.5rem";
                }
                if (!isFixed) {
                    tab.children().find(".pillsNav .active").removeClass("active");
                    navbar.css({
                        "position": "fixed",
                        "top": useoffset,
                        opacity: 0.97,
                        "background-color": "white",
                        "z-index": 99,
                        //"left": scrollParent.offset().left+15,
                        "width": currentWidth,
                        "max-height": "0px"
                    });
                    var useHeight = navbar.children().outerHeight();
                    navbar.parent().css("padding-top", useHeight + 15);
                } else {
                    if (event && event.type == "scroll" && event.data) {
                        tab.children().find(".pillsNav .active").removeClass("active");
                    }
                    navbar.css({
                        "width": currentWidth,
                        "max-height": "350px"
                    });
                }

                var st = scrollParent.scrollTop();
                var contentDataOffset = navbar.height() + 3;
                var condition = contentDataOffset;
                if (false) { // TODO: to enable in 7.12 release, see PPINV-3638, was 'isEmbedded.length < 1 && ipcGraphic.length > 0'
                    $('.ipc-data-with-fixed-header').each(function () {
                        var curWidth = $(this).parent().width();
                        condition = condition - $(this).height();
                        if (st > condition && st > 10) {
                            if (scrollParent.offset()) {
                                $(this).css({"left": scrollParent.offset().left + 20});
                            }
                            $(this).css({
                                "position": "fixed",
                                "top": useoffset + contentDataOffset,
                                "background-color": "white",
                                "z-index": 1,
                                "width": curWidth
                            });
                        } else {
                            $(this).css({"position": "static "});
                        }
                        contentDataOffset = contentDataOffset + $(this).height();
                        condition = condition + $(this).height();
                    });
                }
                if (isEmbedded.length < 1 && ipcTable.length > 0) {
                    if (browserSupportsSticky()) {
                        if (ipcTable.offset().top < contentDataOffset+useoffset) {
                            contentDataOffset = isSecurityClassificationEnabled ? parseInt(contentDataOffset) + 41 : contentDataOffset;
                            ipcTable.css({ "border-collapse": "separate", "border-top": "none" });
                            ipcTable.find("thead").css({"border-bottom":"1px solid #000000" });
                            ipcTable.find("thead>tr>th,thead>tr>td").css({
                                "position": "sticky",
                                "top": contentDataOffset-3,
                                "border-bottom":"2px solid #000000",
                                "background-color": "white"
                            });
                        }  else {
                            ipcTable.find("thead>tr>th,thead>tr>td").css({"position": "static", "top":"", "width": "","border-bottom":"1px solid #000000","background-color": "transparent"});   
                        }
                    } 
                    //IE browser and table's header is scrolled to and it is not yet "position": "fixed" and false staticalay for 7.11 release			
                    else if (false && $(".ipc-table-with-fixed-header").offset().top <= contentDataOffset+$(".pillsNav").offset().top && tab.children().find(".ipc-table-with-fixed-header>thead>tr").css("position") !== "fixed") {
                         tab.children().find(".ipc-table-with-fixed-header>thead>tr>th").each(function (index, element) {
                             $(element).css("width",(($(element).width()/$(element).parent().width())*100)+"%");
                         });
                         $(tab.children().find(".ipc-table-with-fixed-header tr[data-elename='itemSeqNumber']")[0]).find("td").each(function (index, element) {
                             $(element).css("width",(($(element).width()/$(element).parent().width())*100)+"%");
                         });

                         tab.children().find(".ipc-table-with-fixed-header>thead>tr").css({
                            "position": "fixed",
                            "top": contentDataOffset+$(".pillsNav").offset().top,
                            "width": $(".ipc-table-with-fixed-header tbody").width(),
                            "display": "inline-table",
                            "background-color": $(".ipc-table-with-fixed-header>thead>tr").css("background-color") !== "transparent" ? $(".ipc-table-with-fixed-header>thead>tr").css("background-color") : "white"
                         });
                    } else if ($(".ipc-table-with-fixed-header").offset().top > contentDataOffset+$(".pillsNav").offset().top) {
                         //IE browser but table's header is scrolled back to top
                         tab.children().find(".ipc-table-with-fixed-header>thead>tr").css({
                             "position": "",
                             "top": "",
                             "display": "",
                             "background-color": "transparent"
                         });

                         tab.children().find(".ipc-table-with-fixed-header>thead>tr>th").each(function (index, element) {
                             $(element).css("background-color","");
                         });
                    } else if (!browserSupportsSticky()) {
                        //IE browser 
                        tab.children().find(".ipc-table-with-fixed-header>thead>tr").css({
                            "position": "",
                            "top": "",
                            "display": "",
                            "background-color": "transparent"
                        });
                    }
                }
            } else {
                if (navbar.css("position") !== "sticky") {
                    navbar.css({"position": "static", "width": "", "top": "", "max-height": "350px"});
                }
                navbar.parent().css("padding-top", "");
                if (ipcGraphic.length > 0) {
                    ipcGraphic.css({"position": "static", "width": "", "top": "", "max-height": "350px"});
                }
            }
        }
    }
}


function onLoadClient(tab, documentId, publicationId,isEmbedded) {
    try {
        $("[data-toggle=tooltip]").tooltip({html: true});
        $("[data-toggle=tooltip]").each(function(index, tooltip) {
            var mc = new Hammer(this);
            mc.on("press", function(e) {
                console.log('Press',e);
                if($(e.target).tooltip instanceof Function) {
                    $(e.target).tooltip('show');
                }
                return false;
            });
        });
        if (!hasBeenAcknowledged(documentId, publicationId)) {
            tab.children().find(".S1000DIssue4_x_attention_check").show();
            tab.children().find(".need-signing-content").addClass("not-yet-signed-off-on");
            tab.children().on('change', 'input[type=checkbox][data-wc-preq]', function () {

                if (tab.children().find('input:checkbox').is(':checked')) {
                    tab.children().find(".S1000DIssue4_x_attention_check").hide();
                    tab.children().find('.acknowledged-check-mark.before-acknowledge').removeClass('before-acknowledge');
                    tab.children().find('.need-signing-content').addClass('has-signed-off-on').removeClass('not-yet-signed-off-on');

                    var acknowledgedDocument = {
                        documentId: documentId,
                        publicationId: publicationId
                    };
                    if (!window.acknowledgedDocument) {
                        window.acknowledgedDocument = [];
                    }
                    window.acknowledgedDocument.push(acknowledgedDocument);
                }
            });
        } else {
            tab.children().find('.S1000DIssue4_x_attention_check').hide();
            tab.children().find('.acknowledged-check-mark.before-acknowledge').removeClass('before-acknowledge');
        }
        improvePills(tab, isEmbedded);
        changeColspanForApplicabilityInfo(tab);
    } catch (error) {
        console.error(error.message, error);
    }
}

function onLoadMobile(tab,documentId,isEmbedded) {
    try {
        if (!hasBeenAcknowledgedInMobile(documentId)) {
            tab.children().find(".S1000DIssue4_x_attention_check").show();
            tab.children().find(".need-signing-content").addClass("not-yet-signed-off-on");
            tab.children().on('change', 'input[type=checkbox][data-wc-preq]', function () {

                if (tab.children().find('input:checkbox').is(':checked')) {
                    tab.children().find(".S1000DIssue4_x_attention_check").hide();
                    tab.children().find('.acknowledged-check-mark.before-acknowledge').removeClass('before-acknowledge');
                    tab.children().find('.need-signing-content').addClass('has-signed-off-on').removeClass('not-yet-signed-off-on');
                    if (!window.latestDocumentId) {
                        window.latestDocumentId = [];
                    }
                    window.latestDocumentId.push(documentId);
                }
            });
        } else {
            tab.children().find('.S1000DIssue4_x_attention_check').hide();
            tab.children().find('.acknowledged-check-mark.before-acknowledge').removeClass('before-acknowledge');
        }
        improvePillsMobile(tab, true);
    } catch (error) {
        console.error(error.message, error);
    }
}

function hasBeenAcknowledged(documentId, publicationId) {
    var hasBeenAcknowledged = false;
    if (typeof window.acknowledgedDocument !== 'undefined') {
        for (var i = 0; i < window.acknowledgedDocument.length; i++) {
            if (window.acknowledgedDocument[i].publicationId === publicationId && window.acknowledgedDocument[i].documentId === documentId) {
                hasBeenAcknowledged = true;
            }

        }
    }
    return hasBeenAcknowledged;
}

function createNewElement(document, className, style, numbers) {
    var element = document.createElement('span');
    element.setAttribute('class', className);
    element.setAttribute('style', style);
    var text = document.createTextNode(numbers);
    element.appendChild(text);
    return element;
}

function insertAnNumberingElement(listContentElm, insertElementInto, isProceduralStepTitle){
    var ataNum = listContentElm ? listContentElm.dataset ? listContentElm.dataset.itemNumber:undefined:undefined;
    var s1000dNum = listContentElm ? listContentElm.dataset ? listContentElm.dataset.itemRaw:undefined:undefined;
    if (ataNum && s1000dNum && insertElementInto){
        if (isProceduralStepTitle){
            var element = createNewElement(document, 'ataToc', 'left: -50px; margin-right: 100%; position: absolute;', ataNum);
        } else {
            var element = createNewElement(document, 'ataToc', 'left: -15px; margin-right: 100%; position: absolute;', ataNum);
        }
        var element1 = createNewElement(document, 's1000dToc', 'left: -70px; margin-right: 100%; position: absolute;', s1000dNum);
        insertElementInto.insertBefore(element, insertElementInto.firstChild);
        insertElementInto.insertBefore(element1, insertElementInto.firstChild);
    }
}
function setNumberingsToProceduralSteps(activePublicationTab){
    var listElements = activePublicationTab.querySelectorAll('li.list-element');
    if (listElements.length>0){
        for (var i=0;i<listElements.length;i++){
            var proceduralStepListElement = listElements[i].querySelector('div.proceduralStep-list-element');
            var listContent = listElements[i].querySelector('div.list-content') != null ? listElements[i].querySelector('div.list-content').getElementsByTagName('div')[0] : null;
            var proStepTitleElement = listElements[i].querySelector('h4.S1000DIssueCommon_proceduralStep_title span') ? listElements[i].querySelector('h4.S1000DIssueCommon_proceduralStep_title span'):listElements[i].querySelector('span.S1000DIssueCommon_proceduralStep_title div');
            if (proStepTitleElement){
                insertAnNumberingElement(proceduralStepListElement, proStepTitleElement, true);
            } else {
                if (proceduralStepListElement!==null && proceduralStepListElement.getElementsByTagName('div')[0].className == 'list-content') {
                    insertAnNumberingElement(proceduralStepListElement,listContent, false);
                }
                else if (listElements[i].querySelector('div.S1000DIssueCommon_attention')) {
                    insertAnNumberingElement(proceduralStepListElement, listElements[i].querySelector('div.S1000DIssueCommon_attention').parentElement, false);
                } else {
                    insertAnNumberingElement(proceduralStepListElement, listContent, false);
                }
            }
        }
    }
}

function updateRef(el, activeTabElement) {
    var refId = el.dataset.parameter;
    if (refId) {
        var refIdSplitByAnchor = refId.split('ANCHOR=');
        if(refIdSplitByAnchor.length > 1) {
            refId = refIdSplitByAnchor[1].split('&')[0];
            var element = activeTabElement.querySelector('#'+refId);
            var refElement,ppArticleClass;
            if(element){
                ppArticleClass = element.closest('.pp-article');
                var refElements =element.querySelectorAll('[data-item-number]');
                refElement  = refElements.length > 0? refElements[0]:undefined;
            }
            var s1000dSelector = el.querySelector('.s1000dToc');
            var ataSelector = el.querySelector('.ataToc');
            if (refElement && refElement.dataset) {
                if(refElement.dataset.itemNumber && refElement.dataset.itemNumberRaw) {
                    var s1000dRefNumber = refElement.dataset.itemNumberRaw;
                    var ataRefNumber = refElement.dataset.itemNumberFull;
                    if (s1000dRefNumber && ataRefNumber && s1000dSelector && ataSelector) {
                        s1000dSelector.textContent = s1000dRefNumber;
                        ataSelector.textContent = ataRefNumber;
                    }
                }
            }
        }
    }
}

function setRefNumbersToProceduralSteps(activeTabElement){
    if (activeTabElement.getElementsByClassName("documentLink")) {
        var docLinks = activeTabElement.getElementsByClassName("documentLink");
        for (var i = 0; i < docLinks.length; i++) {
            if (docLinks[i] && docLinks[i].getElementsByClassName("stepNumbering").length>0){
                updateRef(docLinks[i],activeTabElement);
            }
        }
    }
}

function hasBeenAcknowledgedInMobile(documentId) {
    var hasBeenAcknowledgedInMobile = false;
    if (window.latestDocumentId && window.latestDocumentId.length>0) {
        for (var i = 0; i < window.latestDocumentId.length; i++) {
            if (window.latestDocumentId[i] === documentId) {
                hasBeenAcknowledgedInMobile = true;
            }

        }
    }
    return hasBeenAcknowledgedInMobile;
}

    function updateNumbering(numberingFormatParam, documentClass) {
        var NUMBERING_UNDERLINE = "underline";
        var documentClass = documentClass;
        var elem,format;
        var query = ".pp-root-numbering";
        var articleClass = ".pp-article";
        if(documentClass) {
            query = documentClass +' ' +query;
            articleClass = documentClass + ' '+articleClass;
        }

        var articleFlags = Array.prototype.slice.call(document.querySelectorAll(articleClass));
        var dataContentFlag = (articleFlags && articleFlags.length>0) ? Array.prototype.slice.call(document.querySelectorAll(articleClass))[0].getAttribute('data-content-flags') : undefined;

        // Using 'slice.call' instead of 'from' to support wkhtmltopdf
        var matchingElements = Array.prototype.slice.call(document.querySelectorAll(query)).filter(function(elem) {
            // Only match visible elements
            // We cannot use jquery while printing; instead this is the logic that jquery :visible uses
            return !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );
        });

        var sbContents = matchingElements.filter(function(item) { return item.classList.contains('src-sbTopicContent') });
        if((!dataContentFlag || dataContentFlag.length == 0) && sbContents.length > 0){
            for(var i=0; i < sbContents.length; i++){
                elem = sbContents[i];
                getTheFormatAndAddItemNumbering(elem, numberingFormatParam);
            }
        } else if(matchingElements.length > 0) {
            for(var j = 0; j < matchingElements.length; j++) {
                getTheFormatAndAddItemNumbering(matchingElements[j], numberingFormatParam);
            }
        }
        return;

        function getTheFormatAndAddItemNumbering(elem, numberingFormatParam){
            var fullCobaltNum = '';
            if (!elem) {
                return;
            }
            var stepTitleClass= ".stepTitle";
            if(documentClass){
                stepTitleClass = documentClass + ' ' + stepTitleClass;
            }
            var proceduralSeps = Array.prototype.slice.call(elem.children).filter(function(item){return item.classList.contains('src-proceduralStep');})
            var stepTitle = Array.prototype.slice.call(document.querySelectorAll(stepTitleClass));
            format = (numberingFormatParam) ? numberingFormatParam : elem.getAttribute("data-item-format");
            if(format && hasAltProcNumsFlag(elem)){
                if(!isSbElement(elem)) {
                    if (stepTitle && stepTitle.length > 0) {
                        format = format.substring(3);
                        for(var j = 0; j < stepTitle.length; j++) {
                            stepTitle[j].classList.add('numberSix');
                            fullCobaltNum = '6.'
                        }
                    }
                }
                else if(isSbElement(elem)){
                    if (proceduralSeps.length > 0 && stepTitle && stepTitle.length > 0) {
                        format = format.substring(3);
                        for(var k = 0; k < stepTitle.length; k++) {
                            stepTitle[k].classList.add('hideProcedure');
                        }
                    }
                }
            }
            var splitFormat = format ? format.split("|") : [];
            var formatArray = [];
            for(var i = 0; i < splitFormat.length; i++) {
              formatArray.push(parseFormat(splitFormat[i]));
            }

            if(formatArray.length > 0) {
                addItemNumbering(elem, 0, 0, formatArray, fullCobaltNum);
            }
            else{
                console.error("Numbering format missing!!!");
            }
        }

        function addItemNumbering(elem, prefix, counter, formatArray, fullCobaltNum) {
            if (isElementNumbered(elem)) {
                prefix = processNumberedItem(elem, prefix, counter, formatArray, fullCobaltNum);
                fullCobaltNum = prefix.substring(prefix.indexOf('#')+1);
                prefix = prefix.substring(0,prefix.indexOf('#'));
            }
            var numberedChildren = getNumberedChildren(elem);
            // Alternative procedures shouldn't count towards numbering because they use the same number as the procedure they are an alternate for
            var encounteredAlts = 0;
            for (var i = 0; i < numberedChildren.length; i++) {
                var childElement = numberedChildren[i];

                if(isElementHavingAlts(childElement)) {
                    encounteredAlts = encounteredAlts + 1;
                }

                if(isElementNumbered(elem)) {
                    // altProcNums flag: do not increment the counter for alternative procedures
                    counter = hasAltProcNumsFlag(elem) ? (i + 1 - encounteredAlts) : (i + 1);
                }

                if(isElementRoot(elem) && (!hasAltProcNumsFlag(elem) || !isElementHavingAlts(childElement))) {
                    // altProcNums flag: do not increment the prefix for child alternative procedures
                    prefix = prefix + 1;
                }

                addItemNumbering(childElement, prefix, counter, formatArray, fullCobaltNum);
            }
        }

        function processNumberedItem(elem, prefix, counter, formatArray, fullCobaltNum) {
            var filterClassListForNumbering = ['applicDisplayText', 'applicability-padding', 'excludeNumbering', 'frontmatter-content','list-element-manual-numbering'];
            var numberedItem;
            /*
            This assumes the first child is where the number goes
            There may be items that go before like applic display text,
            but we'd just need to filter that out.
            */
            numberedItem = elem.children[0];
            //Below code will add a child div to parent div with pp-numbered-item in authoring mode.
            if (!numberedItem) {
                const divNode = document.createElement("div");
                const textNode = document.createTextNode(elem.innerText);
                elem.innerHTML = "";
                divNode.appendChild(textNode);
                elem.appendChild(divNode);
                numberedItem = elem.children[0];
            }
            for (var j = 0; j < elem.children.length - 1; j++) {
                var result = filterClassListForNumbering.filter(function (item) {
                    return elem.children[j].classList.contains(item)
                });
                if (result.length > 0) {
                    numberedItem = elem.children[j + 1];
                } else {
                    break;
                }
            }
            //Below code will remove duplicate numbering while hitting enter key in authoring editor.
            for(var y = 1;y <= elem.children.length  - 1; y++ ){
                if(elem.children[y].getAttribute("data-item-number") != null){
                    elem.children[y].removeAttribute("data-item-number");
                }
                if(elem.children[y].getAttribute("data-item-number-raw") != null){
                    elem.children[y].removeAttribute("data-item-number-raw");
                }
            }
            var newPrefix = counter > 0 ? prefix + "." + counter : prefix;
            newPrefix = addAlternateStepSuffix(elem, newPrefix);
            numberedItem.setAttribute("data-item-number-raw", newPrefix);
            if (formatArray.length > 0) {
                // The prefix contains ".A", ".B", etc for alternate procedures. Remove that when calculating the numbering level
                var prefixWithoutAlts = String(newPrefix).replace(/\.[A-Z]+/g, "");
                var num = String(prefixWithoutAlts).includes('.') ? Number(counter) : prefixWithoutAlts;
                // The prefix will look like "2.1.1". We can use the length of the prefix to determine which format to use
                var numberingLevel = prefixWithoutAlts.split(".").length; 
                // The remainder operator is for numbering levels beyond the length of the format array
                var format = formatArray[(numberingLevel - 1) % formatArray.length];

                if(format.decoration && format.decoration === NUMBERING_UNDERLINE) {
                    numberedItem.classList.add("pp-numbering-underline");
                }

                var renderedNumber = renderSingleNumber(num, format);
                renderedNumber = addAlternateStepSuffix(elem, renderedNumber);
                numberedItem.setAttribute("data-item-number", renderedNumber);
                /*
                  We have also had 'data-item-number-full' which is the full
                  path to this number, eg "II.1.A.". We could recompute the
                  whole path each time or else pass it as renderedContext.

                  But do we really need that? The point seems to be to support
                  ATA internal links to particular steps, and I don't know if
                  we do that.
                */
                fullCobaltNum = fullCobaltNum.toString().concat(renderedNumber);
                numberedItem.setAttribute("data-item-number-full", fullCobaltNum);
            }
            return newPrefix + '#' + fullCobaltNum;
        }

        function addAlternateStepSuffix(elem, number) {
            if(hasAltProcNumsFlag(elem)) {
                var parentElem = elem.parentElement;
                if(parentElem.classList.contains("src-proceduralStepAlts")) {
                    // Sometimes there are multiple alternative procedures, each one should get a different letter
                    var altProcedureNumber = getAlternateStepNumber(parentElem);
                    var altProcedureAlpha = numberToAlpha(altProcedureNumber);
                    if(number.toString().match(/\.$/)) { // Checking if the number ends with a period, endsWith() is not supported by wkhtmltopdf
                        number = number + altProcedureAlpha;
                    } else {
                        number = number + "." + altProcedureAlpha;
                    }
                }
            }

            return number;
        }

        function getAlternateStepNumber(alternateStepElem) {
            var result = 1;
            
            // Determine how many alternative procedures precede this one
            var currentElem = alternateStepElem.previousElementSibling;
            while(currentElem) {
                if(currentElem.classList.contains("src-proceduralStep")) {
                    // We've found the step that this is an alternate for
                    break;
                } else if(currentElem.classList.contains("src-proceduralStepAlts")) {
                    result = result + 1;
                }
                currentElem = currentElem.previousElementSibling;
            }


            return result;
        }

        function hasAltProcNumsFlag(elem) {
            return hasFlag(elem, "altProcNums");
        }

        function hasFlag(elem, flagName) {
            var articleElement = elem.closest(".pp-article");
            var dataContentFlags = (articleElement) ? articleElement.getAttribute("data-content-flags") : undefined;
            return dataContentFlags && "," + dataContentFlags + ",".includes("," + flagName + ","); // Commas ensure we are exactly matching a single flag
        }

    function getNumberedChildren(elem) {
        var kids = elem.children,
            numberedChildren = [];
        if(kids) {
            for (var i = 0; i < kids.length; i++) {
                if (isElementNumbered(kids[i]) || isElementHavingAlts(kids[i])) {
                    numberedChildren.push(kids[i]);
                } else {
                    numberedChildren.concat(getNumberedChildren(kids[i]));
                }
            }
        }
        return numberedChildren;
    }

    function isSbElement(element){
            return element.classList ? element.classList.contains('src-sb') || element.classList.contains('src-sbTopicContent') : false;
    }

    function isElementNumbered(elem) {
        return elem.classList ? elem.classList.contains("pp-numbered-item") : false;
    }

    function isElementRoot(elem) {
        return elem.classList ? elem.classList.contains("pp-root-numbering") : false;
    }

    function isElementHavingAlts(elem) {
        return elem.classList ? elem.classList.contains("src-proceduralStepAlts") || elem.classList.contains("src-levelledParaAlts") : false;
    }

    function parseFormat(formatString) {
        var validStyles = "1IiAaBb",
            style,
            styleLocation;
        var formatObject = {};
        if (null == formatString) return formatObject;
        for (var i = 0; i < validStyles.length; i++) {
            style = validStyles[i];
            styleLocation = formatString.indexOf(style);
            if (styleLocation >= 0) {
                formatObject.prefix = formatString.slice(0, styleLocation);
                formatObject.style = style;
                formatObject.suffix = formatString.slice(styleLocation + 1);
                applyDecoration(formatObject, "_", NUMBERING_UNDERLINE); // Handle numbers that should be underlined
                return formatObject;
            }
        }
        formatObject.prefix = formatString; // eg: may not number, just have bullets
        return formatObject;
    }

    function applyDecoration(formatObject, signifier, decoration) {
        if(formatObject.prefix.includes(signifier) && formatObject.suffix.includes(signifier)) {
            formatObject.prefix = formatObject.prefix.replace(signifier, "");
            formatObject.suffix = formatObject.suffix.replace(signifier, "");
            formatObject.decoration = decoration;
        }
    }

    function renderSingleNumber(num, format) {
        var output = format.prefix,
            s = format.style;
        switch (format.style) {
            case "1":
                output += num;
                break;
            case "A":
                output += numberToAlpha(num);
                break;
            case "a":
                output += numberToAlpha(num).toLowerCase();
                break;
            case "B":
                output += numberToAlphaUnambiguous(num);
                break;
            case "b":
                output += numberToAlphaUnambiguous(num).toLowerCase();
                break;
            case "I":
                output += numberToRoman(num);
                break;
            case "i":
                output += numberToRoman(num).toLowerCase();
                break;
            default:
                output += num;
        }
        output += format.suffix;
        return output;
    }

    function numberToRoman(num) {
        // Adapted from https://stackoverflow.com/questions/9083037
        var i,
            roman = "",
            lookup = [
                [1000, "M"],
                [900, "CM"],
                [500, "D"],
                [400, "CD"],
                [100, "C"],
                [90, "XC"],
                [50, "L"],
                [40, "XL"],
                [10, "X"],
                [9, "IX"],
                [5, "V"],
                [4, "IV"],
                [1, "I"]
            ];
        if (num === 0) return "_";
        for (i = 0; i < lookup.length; i++) {
            while (num >= lookup[i][0]) {
                roman += lookup[i][1];
                num -= lookup[i][0];
            }
        }
        return roman;
    }

    function numberToAlpha(num) {
        return _numberToAlpha(num, "ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    }

    function numberToAlphaUnambiguous(num) {
        return _numberToAlpha(num, "ABCDEFGHJKLMNPQRSTUVWXYZ");
    }

    function _numberToAlpha(num, lookup) {
        if (num < 1) return "〇"; // Shouldn't happen, but for debugging
        var alpha = "",
            particle = 0,
            base = lookup.length;
        particle = Math.floor(num - 1) % base; // floor to handle bad input; -1 for 0/1-indexing (26 is Z)
        alpha = lookup[particle] + alpha;
        num = Math.floor((num - 1) / base); // floor to handle bad input;
        while (num > 0) {
            particle = (num - 1) % base;
            alpha = lookup[particle] + alpha;
            num = Math.floor(num / base); // floor to avoid subtracting particle (off by 1 errors)
        }
        return alpha;
    }
}
