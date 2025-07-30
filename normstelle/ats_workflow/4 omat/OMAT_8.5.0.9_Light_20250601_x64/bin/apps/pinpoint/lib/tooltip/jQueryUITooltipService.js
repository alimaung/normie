var bootstrapButton = $.fn.button.noConflict();
$.fn.bootstrapBtn = bootstrapButton;
var securityBannerContent = "";

function TooltipUtil(){}

TooltipUtil.getTooltipHtmlContent =  function(tooltipTargetCss, content, anchor){
	var functionAnchor = " function scrollToAnchorIframe() {};";
	if ( anchor !=="" && anchor !== undefined ) {
	  anchor = anchor+"";
	  functionAnchor =
		" function scrollToAnchorIframe() { " +
		"    var anchorElements = null; " +
		"    anchorElements = $('#content').find('#"+anchor+"');" +
		"    if (anchorElements.length == 0) {" +
		"      anchorElements = $('#content').find(\"*[name='"+anchor+"']\");" +
		"    }" +
		"    if (anchorElements.length == 0) {" +
		"      anchorElements = $('#content').find('#KEY_" +anchor+"');" +
		"    }" +
		"    if (anchorElements.length == 0) {" +
		"      anchorElements = $('#content').find(\"*[anchor='"+anchor+"']\");" + //ICN link from AMM to AIPC"
		"    }" +
		"    if (anchorElements && anchorElements.length > 0) {" +
		"      anchorElements[0].scrollIntoView(); " +
		"    }"+
		"}";
	}
	functionAnchor = functionAnchor +
		" " +
		" function updateRefNumToXitem() { " +
		"    var iFrameDoc = window.frameElement.ownerDocument.getElementById('tooltipIframe'); " +
		"    if (iFrameDoc !== null && iFrameDoc !== undefined) {" +
		"        if (typeof parent.setRefNumbersTolXitemlist === 'function') {" +
		"      		parent.setRefNumbersTolXitemlist(iFrameDoc.contentDocument);" +
		"		 }" +
		"        if (typeof parent.setNumberingsToProceduralSteps === 'function') {" +
		"      		parent.setNumberingsToProceduralSteps(iFrameDoc.contentDocument);" +
		"		 }" +
		"        if (typeof parent.setRefNumbersToProceduralSteps === 'function') {" +
		"      		parent.setRefNumbersToProceduralSteps(iFrameDoc.contentDocument);" +
		"		 }" +
		"    }" +
		"}";

	var scriptStr = "<script>setTimeout(function() { updateRefNumToXitem(); scrollToAnchorIframe();}, 500);</script>";
    return TooltipUtil.getHtmlTemplate(tooltipTargetCss,functionAnchor,content,scriptStr);
};

TooltipUtil.getTooltipHtmlContentCSNItem = function(tooltipTargetCss, content, anchorId, anchorName, modelIdentCode, csnWithFilter){
    var functionAnchor = " function scrollToAnchorIframe() {};";
    if ( (anchorId !=="" && anchorId !== undefined) || (anchorName !=="" && anchorName !== undefined)) {
		if (isKcaPublication(modelIdentCode)) {
			functionAnchor =
				" function scrollToAnchorIframe() { " +
				"     var anchorElements = null; " +
				"     anchorElements = $('#content').find(\"*[anchor^='" + anchorName + "']\");" +
				"     if (anchorElements && anchorElements.length > 0) {" +
				"         anchorElements[0].scrollIntoView(); " +
				"         var trEle = $(anchorElements[0]);" +
				"         if (trEle && trEle.length > 0) {" +
				"             trEle.addClass(\"pp_text_highlight\");" +
				"         }" ;
			if(!csnWithFilter) {
				functionAnchor = functionAnchor +
					"         var trEle2 = $(anchorElements[0].closest(\"tr\"));" +
					"         if (trEle2 && trEle2.length > 0) {" +
					"             trEle2.addClass(\"pp-non-effective-disabled\");" +
					"         }" ;
			}
			functionAnchor = functionAnchor +
				"     }" +
				"}";
		} else {
			functionAnchor =
				" function scrollToAnchorIframe() { " +
				"     var anchorElements = null; " +
				"     anchorElements = $('#content').find(\"*[name^='" + anchorName + "']\");" +
				"     if (anchorElements && anchorElements.length > 0) {" +
				"         anchorElements[0].scrollIntoView(); " +
				"         var trEle = $(anchorElements).closest(\"tr[data-elename='itemSeqNumber']\");" +
				"         if (trEle && trEle.length > 0) {" +
				"             trEle.addClass(\"pp_text_highlight\");" +
				"         }" +
				"     } else {" +
				"         anchorElements = $('#content').find('#" + anchorId + "');" +
				"         if (anchorElements && anchorElements.length > 0) {" +
				"             anchorElements[0].scrollIntoView(); " +
				"             anchorElements.addClass(\"pp_text_highlight\");" +
				"         }" +
				"     }" +
				"}";
		}
	}
    var scriptStr = "<script>setTimeout(function() {scrollToAnchorIframe();}, 500);</script>";
    return TooltipUtil.getHtmlTemplate(tooltipTargetCss,functionAnchor,content,scriptStr);
};

TooltipUtil.setSecurityBannerHtmlContent = function (securityBanner) {
	securityBannerContent = securityBanner.replace('banner-securitycontent', "banner-securitycontent style = 'position: sticky;z-index: 100;top: 0px;'");
};

TooltipUtil.getTooltipHtmlContentCMLItem = function(tooltipTargetCss, content, anchor){
	if(anchor !== "" && anchor !== undefined) {
		var functionAnchor =
			" function scrollToAnchorIframe() { " +
			"     var anchorElements = null; " +
			"     anchorElements = $('#content').find(\".pp-cml-anchor_"+anchor+"\""+");" +
			"     if (anchorElements && anchorElements.length > 0) {" +
			"         var anchor =$(anchorElements).attr(\"KEY\");"+
			"         var anchorId = \"KEY_\"+ anchor ;"+
			"         anchorElements = $('#content').find(\"*[id=\"+anchorId+\"]\");" +
			"         anchorElements[0].scrollIntoView(); " +
			"         var trEle = $(anchorElements);" +
			"         if (trEle && trEle.length > 0) {" +
			"             trEle.addClass(\"pp_text_highlight\");" +
			"         }" +
			"     }" +
			"}";
	}
	var scriptStr = "<script>setTimeout(function() {scrollToAnchorIframe();}, 500);</script>";
	return TooltipUtil.getHtmlTemplate(tooltipTargetCss,functionAnchor,content,scriptStr);
};

TooltipUtil.getHtmlTemplate = function (tooltipTargetCss, functionAnchor, content, paramFun) {
	return "<html><head>"+
	"<link rel=\"stylesheet\" href=\"bower_components/jquery-ui/themes/smoothness/jquery-ui.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"bower_components/bootstrap/dist/css/bootstrap.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"bower_components/bootstrap/dist/css/bootstrap-theme.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"bower_components/angular-ui-tree/dist/angular-ui-tree.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"bower_components/font-awesome/css/font-awesome.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"lib/w2ui/w2ui-1.4.3.min.css\"/>"+
	"<link rel=\"stylesheet\" href=\"lib/zTree/css/zTreeStyle/zTreeStyle.css\"/>"+
	"<link rel=\"stylesheet\" href=\"lib/zoom/css/imgareaselect-default.css\"/>"+
	"<link rel=\"stylesheet\" href=\"css/app.css\"/>"+
	"<link rel=\"stylesheet\" href=\"css/global.css\"/>"+
	"<link rel=\"stylesheet\" href=\"css/pinpointStyling.css\"/>"+
	"<link rel=\"stylesheet\" href=\"widgets/widgetsCss.css\"/>"+
	"<link rel=\"stylesheet\" href=\"bower_components/ngtoast/dist/ngToast.min.css\">"+
	"<link rel=\"stylesheet\" href=\"bower_components/ngtoast/dist/ngToast-animations.min.css\">"+
	"<link rel=\"stylesheet\" href=\"bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css\" />"+
	"<style>"+ tooltipTargetCss + "</style>" +
	(TooltipUtil.customTheme ? "<style>" + TooltipUtil.customTheme + "</style>" : "") +
	"<style>a, .cirImageLink, .documentLink, .accessPointCirHtml, .circuitBreakerCirLink, .partCirLink, "+
		" .zoneCirHtml, .enterpriseCirLink, .supplyRequirementCirLink, .supplyCirLink, .toolCirLink, .FINCirLink, span[data-parameter] "+
		" {text-decoration:none !important; cursor:default !important;} .pillsNav .pills-tab {display:none;}</style>" +
	"<script src=\"bower_components/jquery/jquery.min.js\"></script> " +
	"<script src=\"bower_components/jquery-ui/jquery-ui.min.js\"></script> "+
	"<script src=\"lib/scrollto/jquery.scrollTo.min.js\"></script>" +
	"<script> " + functionAnchor + "</script>" +
		"</head><body class='previewTooltipClass'><div class='claro' id='content'>" + securityBannerContent + content + "</div> " +
     paramFun +
    "</body>" +
    "</html>";
};

TooltipUtil.customTheme = "";

TooltipUtil.preview = function(tooltipTitle, previewCloseTooltipTarget) {
    var iframeContent = "<iframe id='tooltipIframe' name='tooltipIframeName' style='position:related; margin-bottom: -1.1em' width='100%' height='100%' src='about:blank'/>";
	var tooltipDialog = $('<div id="tooltipDiv"></div>')
					.html(iframeContent)
					.dialog({
						modal: true,
						title: TooltipUtil.purifyHtmlTag(tooltipTitle),
						width: 700,
						height: 500,
						draggable:true,
						resizable:true,
						close:function(){
							$("#tooltipDiv").remove();
							previewCloseTooltipTarget();
						},
						resize: function(){
							console.log("resize ui-dialog width:"+$('.ui-dialog').width());
							$('#tooltipDiv').width($('.ui-dialog').width()-20);
							$('#tooltipDiv').height($('.ui-dialog').height()-60);
							tooltipIframeName.window.scrollToAnchorIframe();
							$('.ui-dialog :button').blur();
						}
					});
	tooltipDialog.dialog("open");
	$('#tooltipDiv').css('overflow', "hidden");
	$('#tooltipDiv').css('position', "relative");
	$('#tooltipDiv').css('margin', ".5em");
	$('#tooltipDiv').css('padding', ".1em");
	$('.ui-dialog').css('z-index', 200);
	$('.ui-widget-overlay').css('z-index', 199);
	$('.ui-dialog :button').blur();
}

TooltipUtil.fullFillContent = function(tooltipTargetCss, content, anchor){
	var contentTooltip = TooltipUtil.getTooltipHtmlContent(tooltipTargetCss, content, anchor);
	var ifrm = document.getElementById('tooltipIframe');
	ifrm.contentDocument.write(contentTooltip);
}

TooltipUtil.fullFillContentCSNItem = function(tooltipTargetCss, content, anchorId, anchorName, modelIdentCode, csnWithFilter){
    var contentTooltip = TooltipUtil.getTooltipHtmlContentCSNItem(tooltipTargetCss, content, anchorId, anchorName, modelIdentCode, csnWithFilter);
    var ifrm = document.getElementById('tooltipIframe');
    ifrm.contentDocument.write(contentTooltip);
}

TooltipUtil.fullFillContentCMLItem = function(tooltipTargetCss, content, anchor){
	var contentTooltip = TooltipUtil.getTooltipHtmlContentCMLItem(tooltipTargetCss, content, anchor);
	var ifrm = document.getElementById('tooltipIframe');
	ifrm.contentDocument.write(contentTooltip);
}

TooltipUtil.purifyHtmlTag = function(tooltipTitle){
	if (tooltipTitle === undefined) {
		return "";
	}
	tooltipTitle = tooltipTitle.replace(/<\/?[^>]*>/g,'');
    tooltipTitle = tooltipTitle.replace(/[ | ]*\n/g,'\n');
    tooltipTitle = tooltipTitle.replace(/\n[\s| | ]*\r/g,'\n');
    tooltipTitle = tooltipTitle.replace(/&nbsp;/ig,'');
    return tooltipTitle;
}
