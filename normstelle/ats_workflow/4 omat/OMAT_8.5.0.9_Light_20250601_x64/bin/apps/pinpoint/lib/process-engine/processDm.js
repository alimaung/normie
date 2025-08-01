/** logic engine stars here **/
function ProcessEngine() {
}
var pubId;
var method_prefix = '';
var method_suffix = '';
var resetAltsFlow = false;
var loop_suffix = 'loopCondition';
var if_suffix = 'ifcondition';
var validate_suffix = 'validateForm';
var loop_sequence = 'loopSequence';
var previous_of_first_node = -1;
var dm_then_seq = 'dmThenSeq';
var dm_else_seq = 'dmElseSeq';
var dmloop = 'dmLoop';
var dmseq_Alts = 'dmSeqAlts';
var dmnode_alts = 'dmNodeAlts';
var dialog_alts = 'dialogAlts';
var dm_seq = 'dmSeq';
var dm_If = 'dmIf';
var dm_functions = 'functions';
var dm_node = 'dmNode';
var startIndex = 0;
var VARIABLES = "variables";
var preset = 'preset';
var display = 'display';
var displayFunction = 'dispFunction';
var dm_dialog = "dialog";
var dm_menuchoice = "menuChoice";
var init_loop_suffix = "initializeLoop";
var content;
var scopeContent;
var pdmVar;

//Stack implementation
ProcessEngine.Stack = function () {

    var items = [];

    this.push = function (element) {
        items.push(element);
    };

    this.pop = function () {
        return items.pop();
    };

    this.peek = function () {
        return items[items.length - 1];
    };

    this.peekPrevious = function () {
        return items[items.length - 2];
    };

    this.print = function () {
        for(var i in items) {
            if(i < items.length) {
                console.log("**" + JSON.stringify(items[i]));
            }
        }
    };

    this.getAll = function () {
        return items;
    };

    this.isEmpty = function () {
        return items.length == 0;
    };

    this.size = function () {
        return items.length;
    };

    this.clear = function () {
        items = [];
    };

};

ProcessEngine.initializeVariables = function (stackEntry) {
    for (var key in stackEntry) {
        if(stackEntry[key] !== "" && (typeof stackEntry[key] === 'number' || !isNaN(stackEntry[key]) || typeof stackEntry[key] === 'boolean')) {
            eval(key + " = " + stackEntry[key]);
        } else {
            if(stackEntry[key].indexOf('"') === 0 || stackEntry[key].indexOf("'") === 0) {
                eval(key + " = " + stackEntry[key]);
            } else {
                eval(key + " = '" + stackEntry[key] + "'");
            }
        }
    }
};

ProcessEngine.resetVariables = function (diffJSON) {
    if(JSON.stringify(diffJSON) !== '{}') {
        for (var key in diffJSON) {
            if(typeof diffJSON[key] === 'boolean') {
                eval(key + " = false");
            } else if(typeof diffJSON[key] === 'number' || !isNaN(diffJSON[key])) {
                eval(key + " = 0");
            } else {
                eval(key + " = ''");
            }
        }
    }
};

/***
 * This function is used to navigate through all the pages in the Process DM
 * @param navigation
 * @param step
 * @param currentNode
 */
ProcessEngine.processLogicEngine = function (navigation, thisStep, thisNode) {
    var child = '';
    var parent = this;
    pdmVar[pubId + '_currentNode'] = thisNode;
    pdmVar[pubId + '_step'] = thisStep;

    var annotatorClass = document.getElementsByClassName("annotator-adder");
    for(var i = 0; i < annotatorClass.length; i++) {
        annotatorClass[i].classList.add("annotator-hide");
    }

    if (navigation === pdmVar['previous'] || navigation === pdmVar['cancel'] ) { // Delete the newly created variables for the step on going back
        var previousEntries = pdmVar[pubId + '_stack'].getAll();
        var diffJSON = ProcessEngine.compareJSON(previousEntries);
        ProcessEngine.resetVariables(diffJSON);
        pdmVar[pubId + '_stackValues'] = ProcessEngine.getPreviousSystemState();
    } else if (navigation === pdmVar['submit'] || navigation === '' || navigation === pdmVar['next'] ) {
        pdmVar[pubId + '_stackValues'] = pdmVar[pubId + '_stack'].peek();
    }
    ProcessEngine.initializeVariables(pdmVar[pubId + '_stackValues']);

    /***
     * If the current node is -1 or exceed the max limit dmnode index then Else condition will excute
     */
    if (document.getElementById(pdmVar[pubId + '_currentNode'])) {
        var reassignJSON = {};
        if (document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_step']]) {
            if (document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_step']].tagName != 'DIV') {
                pdmVar[pubId + '_step']++;
            } else {
                pdmVar[pubId + '_step'] = ProcessEngine.processDialogActions(navigation);
                ProcessEngine.hidePreviousDMNode();
                child = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_step']].id;

            }
            if (navigation === pdmVar['previous']) {
                if (ProcessEngine.checkdivElement(pdmVar[pubId + '_currentNode'], dm_node)) {
                    pdmVar[pubId + '_prevNode'] = pdmVar[pubId + '_currentNode'];
                    document.getElementById(pdmVar[pubId + '_prevNode']).style.display = "none";
                    child = ProcessEngine.goLevelUpOrDown(navigation);
                    pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
                    pdmVar[pubId + '_currentNode'] = pdmVar[pubId + '_node'];
                } else {
                    while (ProcessEngine.checkdivElement(child, dm_If)) {
                        pdmVar[pubId + '_step'] = pdmVar[pubId + '_step'] - 1;
                        child = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_step']].id;
                    }
                }
            }

            pdmVar[pubId + '_currentStep'] = pdmVar[pubId + '_step'];

        } else {
            if (pdmVar[pubId + '_currentNode'] != pdmVar[pubId + '_rootNode']) {
                pdmVar[pubId + '_step'] = ProcessEngine.processDialogActions(navigation);
                var checkLoopIsParentForCurrentNode = ProcessEngine.findParentId(pdmVar[pubId + '_currentNode']);
                if (pdmVar[pubId + '_step'] != previous_of_first_node) {
                    if (ProcessEngine.isLoopAvailable(child)) {
                        method_prefix = checkLoopIsParentForCurrentNode.split("-").join('');
                        method_suffix = loop_suffix;
                        var isEvaluateLoopCondition = ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
                        if (isEvaluateLoopCondition) {
                            pdmVar[pubId + '_step'] = startIndex;
                            child = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_step']].id;
                            ProcessEngine.processDMLoop(child);
                        } else {
                            var loopParent = ProcessEngine.findParentId(checkLoopIsParentForCurrentNode);
                            ProcessEngine.hidePreviousDMNode();
                            child = ProcessEngine.goLevelUpOrDown(loopParent, navigation);
                            pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
                            pdmVar[pubId + '_currentNode'] = pdmVar[pubId + '_node'];
                            document.getElementById(child).style.display = "block";
                            ProcessEngine.showActiveNavigationButtons();
                            ProcessEngine.processLogicEngine('', pdmVar[pubId + '_step'], pdmVar[pubId + '_currentNode']);
                        }
                    } else {
                        if (ProcessEngine.checkdivElement(pdmVar[pubId + '_currentNode'], dm_node)) {
                            pdmVar[pubId + '_prevNode'] = pdmVar[pubId + '_currentNode'];
                            document.getElementById(pdmVar[pubId + '_prevNode']).style.display = "none";
                        } else {
                            ProcessEngine.hidePreviousDMNode(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_currentStep']);
                        }

                        child = ProcessEngine.goLevelUpOrDown(pdmVar[pubId + '_currentNode'], navigation);
                        pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
                        pdmVar[pubId + '_currentNode'] = pdmVar[pubId + '_node'];

                    }
                } else {
                    ProcessEngine.hidePreviousDMNode(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_currentStep']);
                    child = ProcessEngine.goLevelUpOrDown(pdmVar[pubId + '_currentNode'], navigation);
                    pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
                    pdmVar[pubId + '_currentNode'] = pdmVar[pubId + '_node'];
                }
            }
        }
    } else {
        child = ProcessEngine.goLevelUpOrDown(pdmVar[pubId + '_currentNode'], navigation);
        pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
        pdmVar[pubId + '_currentNode'] = pdmVar[pubId + '_node'];
    }
    ProcessEngine.showAndHideDMNodeAndNavigationButtonOnThePage(navigation, child);
};

ProcessEngine.compareJSON = function(previousEntries) {
    var diffJSON = {};
    if(typeof previousEntries !== 'undefined') {
        var stackValues = pdmVar[pubId + '_stack'].pop();
        for(var prev in previousEntries) {
            for (var i in stackValues) {
                if (!previousEntries[prev].hasOwnProperty(i)) {
                    if (!diffJSON.hasOwnProperty(i)) {
                        diffJSON[i] = stackValues[i];
                    }
                }
            }
        }
    }
    console.log(JSON.stringify(diffJSON));
    return diffJSON;
};


ProcessEngine.createNodeJSON = function (currentNode, step) {
    var nodeJSON = {};
    nodeJSON["processNodeId"] = currentNode;
    nodeJSON["step"] = step;
    return nodeJSON;
};

ProcessEngine.processDialogActions = function (navigation) {
    var reassignJSON = {};
    if (navigation === pdmVar['submit']) {
        reassignJSON = ProcessEngine.evaluateMenuChoice();
        if (!ProcessEngine.validateIfDialog(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_currentStep'])) {
            pdmVar[pubId + '_hasErrors'] = true;
            pdmVar[pubId + '_step'] = pdmVar[pubId + '_currentStep'];
        }
    }
    if (navigation === pdmVar['next'] || (!pdmVar[pubId + '_hasErrors'] && navigation === pdmVar['submit'])) {
        var childNode = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_currentStep']].id;
        if(JSON.stringify(reassignJSON) !== '{}') {
            reassignJSON = ProcessEngine.jsonConcat(reassignJSON, pdmVar[pubId + '_stackValues']);
        }
        ProcessEngine.constructAndUpdateJson(reassignJSON);
    }
    pdmVar[pubId + '_hasErrors'] = false;
    return pdmVar[pubId + '_step'];
};
ProcessEngine.displayNextNode = function (currentNode, step, navigation) {
    ProcessEngine.hidePreviousDMNode(currentNode, step);
    child = ProcessEngine.goLevelUpOrDown(currentNode, step, navigation);
    currentNode = node;

    return child;
};

ProcessEngine.jsonConcat = function (o1, o2) {
    if(JSON.stringify(o1) === '{}') {
        return o2;
    } else if(JSON.stringify(o2) === '{}') {
        return o1;
    } else {
        for (var key in o2) {
            o1[key] = o2[key];
        }
        return o1;
    }
};
ProcessEngine.getPresetJSON = function (child, preset) {
    var presetJSON = {};
    var dynamicVariables;
    if(child === '') {
        if(document.getElementsByTagName(preset)) {
            dynamicVariables = document.getElementsByTagName(preset);
        }
    } else {
        dynamicVariables = document.getElementById(child).getElementsByTagName(preset);
    }
    if(dynamicVariables.length !== 0) {
        for (var i = 0; i <= dynamicVariables.length - 1; i++) {
            var preset_var_id = dynamicVariables[i].getAttribute("id");
            var preset_var_text = document.getElementById(preset_var_id).innerText.replace(/(\r\n|\n|\r)/gm, " ").replace(/ +/g, " ");
            if(preset_var_text !== null && preset_var_text !== '') {
                pdmVar[pubId + '_dyn_variables'][preset_var_id] = JSON.parse(preset_var_text);
                if (preset === 'reassign') {
                    presetJSON = ProcessEngine.jsonConcat(presetJSON, pdmVar[pubId + '_dyn_variables'][preset_var_id]);
                } else {
                    var token = preset_var_id.split("-");
                    if (token.pop().indexOf('variablePreSet') === 0) {
                        presetJSON = ProcessEngine.jsonConcat(presetJSON, pdmVar[pubId + '_dyn_variables'][preset_var_id]);
                    }
                }
            }
        }
    }
    return presetJSON;
};

ProcessEngine.getDisplayVariables = function (child) {
    var dispFunction = document.getElementById(child).getElementsByTagName(displayFunction);
    var displayElement = document.getElementById(child).getElementsByTagName(display);
    for (var j = 0; j < dispFunction.length; j++) {
        var variable = dispFunction[j].innerText;
        eval(variable);
        var variableValue = setName();
        var span = ProcessEngine.createSpanElement(variableValue);
        var currentBrowser = ProcessEngine.browserCheck();
        for (var k = 0; k < displayElement.length; k++) {
            if (displayElement[k].getElementsByTagName("span").length === 0) {
                displayElement[k].appendChild(span);
                displayElement[k].style.display = "inline";
            } else {
                currentBrowser == 'IE' ?  displayElement[k].getElementsByTagName("span")[0].replaceNode(span) : displayElement[k].getElementsByTagName("span")[0].replaceWith(span);
            }
        }
    }
};

ProcessEngine.browserCheck = function (){
    var isOpera = (!!pdmVar.opr && !!opr.addons) || !!pdmVar.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    var isFirefox = typeof InstallTrigger !== 'undefined';
    var isSafari = /constructor/i.test(pdmVar.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!pdmVar['safari'] || safari.pushNotification);
    var isIE = /*@cc_on!@*/false || !!document.documentMode;
    var isEdge = !isIE && !!pdmVar.StyleMedia;
    var isChrome = !!pdmVar.chrome && !!pdmVar.chrome.webstore;
    var isBlink = (isChrome || isOpera) && !!pdmVar.CSS;
    if(isOpera === true){ return 'Op'}
    else if(isFirefox){return 'Fire'}
    else if(isSafari){return 'Safari'}
    else if(isIE){return 'IE'}
    else if(isEdge){return 'Ed'}
    else if(isChrome){return 'Chrome'}
    else if(isBlink){return 'Blink'}
};


ProcessEngine.createSpanElement = function (innerTextValue) {
    var span = document.createElement("span");
    span.innerHTML = innerTextValue;
    span.style.display = "inline";
    return span;
};

ProcessEngine.isDisplayVariableAvailable = function (child) {
    if(document.getElementById(child)) {
        if (document.getElementById(child).hasAttribute("hasDisplayVar")) {
            return true;
        } else {
            return false;
        }
    }
};


ProcessEngine.getAllVariableDeclarations = function (Object) {
    var obj1 = {};
    if (document.getElementById(pubId + "-" + VARIABLES)) {
        var var_declare_func = document.getElementById(pubId + "-" + VARIABLES).innerHTML;
        eval(var_declare_func);
        obj1 = getDeclaredVariables();
    }
    var process_preset = ProcessEngine.getPresetJSON('', pubId + '-' + 'preset');
    ProcessEngine.pushToStack(obj1, process_preset);
};

ProcessEngine.retrieveDynamicFunctionsAndVariables = function (child, type, idType) {
    var dynamicVariables;
    var dyn_contents = {};
    if (type === 'variable' || type === 'reassign') {
        if (child === '') {
            dynamicVariables = document.getElementsByTagName(idType);
        } else {
            dynamicVariables = document.getElementById(child).getElementsByTagName(idType);
        }
    } else if (type === 'functions') {
        dynamicVariables = document.getElementsByTagName(idType);
    }
    for (var i = 0; i <= dynamicVariables.length - 1; i++) {
        var content_id = dynamicVariables[i].getAttribute("id");
        var content_text = document.getElementById(content_id).innerText.replace(/(\r\n|\n|\r)/gm, " ").replace(/ +/g, " ");
        if (idType === 'functions') {
            dyn_contents[content_id] = content_text;
        } else if (idType === 'menufunctions') {
            dyn_contents[content_id] = content_text;
        } else {
            dyn_contents[content_id] = JSON.parse(content_text);
        }
    }
    return dyn_contents;
};


ProcessEngine.showAndHideDMNodeAndNavigationButtonOnThePage = function (navigation, child) {

    //Check if preset is available
    if (ProcessEngine.isPresetAvailable(child)) {
        var presetJSON = {};
        var preset = ProcessEngine.getPresetJSON(child, "variable");

        ProcessEngine.pushToStack(pdmVar[pubId + '_prevJsonObject'], preset);
        ProcessEngine.initializeVariables(pdmVar[pubId + '_stackValues']);
    }

    if (ProcessEngine.isDisplayVariableAvailable(child)) {
        ProcessEngine.getDisplayVariables(child);
    }

    if (ProcessEngine.isConditionAvailable(child)) {
        method_prefix = child.split("-").join('');
        method_suffix = if_suffix;
        var ifConditionReturnDMSeq = ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
        pdmVar[pubId + '_currentStep'] = startIndex;
        ProcessEngine.displayCurrentNode(child);
        ProcessEngine.showActiveNavigationButtons(step, ifConditionReturnDMSeq);
        ProcessEngine.processLogicEngine('', startIndex, ifConditionReturnDMSeq);
    }
    else if (ProcessEngine.isLoopAvailable(child)) {
        method_prefix = child.split("-").join('');
        method_suffix = init_loop_suffix;
        ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
        var initVariable = pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix];
        var loopInit = initVariable.split("=");
        if(loopInit !== 'undefined' || loopInit !== '') { // Initialize the loop variable and delete all of the previous stack entries with that key.
            var initValue = loopInit[0].trim();
            var stackEntries = pdmVar[pubId + '_stack'].getAll();
            for(var entry in stackEntries) {
                if (stackEntries[entry].hasOwnProperty(initValue)) {
                    delete stackEntries[entry][initValue];
                }
            }
        }
        ProcessEngine.processDMLoop(child, step);
    }
    else if (ProcessEngine.isAltsAvailable(child)) {
        var altWorkflow = ProcessEngine.processAlts(child);
        ProcessEngine.displayCurrentNode(child);
        if (ProcessEngine.checkdivElement(child, dmseq_Alts)) {
            ProcessEngine.showActiveNavigationButtons(step, child);
            ProcessEngine.processLogicEngine('', startIndex, altWorkflow);
        } else {
            ProcessEngine.displayCurrentNode(altWorkflow);
        }
    }
    else {
        if (child === '') {
            child = currentNode;
        }
        var showButtons = true;
        if (document.getElementById(child) && document.getElementById(child).hasAttribute("hasDialog")) {
            var hasDialog = document.getElementById(child).getAttribute("hasDialog");
            if (hasDialog === 'true') {
                if (!pdmVar[pubId + '_hasErrors'] && navigation === pdmVar['next']) {
                    ProcessEngine.resetDialog(child);
                }
                showButtons = false;
            }
        }
        if (!showButtons) {
            ProcessEngine.hideNavigationButtons();
        } else {
            ProcessEngine.showActiveNavigationButtons(pdmVar[pubId + '_step'], pdmVar[pubId + '_currentNode']);
        }
        ProcessEngine.hidePreviousDMNode(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_currentStep']);
        ProcessEngine.displayCurrentNode(child);
    }
};

ProcessEngine.resetDialog = function (child) {
    var divChilds = document.getElementById(child).getElementsByTagName('span');
    var divIds = [];
    for (var spans in divChilds) {
        if (divChilds.hasOwnProperty(spans)) {
            if (divChilds[spans].id.indexOf("errorMessage") === 0) {
                document.getElementById(divChilds[spans].id).style.display = "none";
            }
        }
    }
    var inputChilds = document.getElementById(child).getElementsByTagName('input');
    for (var inputs in inputChilds) {
        if (inputChilds.hasOwnProperty(inputs)) {
            if (document.getElementById(inputChilds[inputs].id)) {
                if (document.getElementById(inputChilds[inputs].id).type === 'text'
                    || document.getElementById(inputChilds[inputs].id).type === 'number') {
                    document.getElementById(inputChilds[inputs].id).value = "";
                } else if (document.getElementById(inputChilds[inputs].id).type === 'radio') {
                    document.getElementById(inputChilds[inputs].id).checked = false;
                }
            }
        }
    }
};

ProcessEngine.validateUserEntries = function(child) {
    method_prefix = child.split("-").join('');
    method_suffix = validate_suffix;
    var isValid = true;
    var isValidUserEntry = true;
    var isValidMenuChoice = true;
    if (pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]) {
        isValid = ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
    }
    isValidMenuChoice = ProcessEngine.validateMenuChoices(child);
    if(isValidUserEntry === false || isValidMenuChoice === false){
        isValid = false;
    }
    return isValid;

};

ProcessEngine.validateMenuChoices = function(child){
    var radioflag = false;
    var textBoxflag = false;
    var allInputsValid = false;
    var radioExist = false;
    var textBoxExist = false;
    var inputChilds = document.getElementById(child).getElementsByTagName('input');

    for (var i=0 ; i< inputChilds.length; i++)
    {
        if(inputChilds[i].type === 'radio'){
            radioExist = true;
            document.getElementById(inputChilds[i].id).checked ? radioflag=true : '';
        }
        else if (inputChilds[i].type === 'text'){
            textBoxExist = true;
            document.getElementById(inputChilds[i].id).value!="" ? textBoxflag=true : textBoxflag = false;
        }

    }
    allInputsValid = (radioExist && !radioflag) ? false: ((textBoxExist && !textBoxflag) ? false : true);
    return allInputsValid;

};

//Save system state
ProcessEngine.constructAndUpdateJson = function (stackJSON) {

    if(JSON.stringify(stackJSON) === '{}' || typeof stackJSON === 'undefined' || stackJSON === '') {
        stackJSON = pdmVar[pubId + '_stack'].peek();
        var updatedJson = [];

        if(typeof stackJSON === 'undefined') {
            ProcessEngine.getAllVariableDeclarations(content);
            stackJSON = pdmVar[pubId + '_stack'].peek();
        }
        Object.keys(stackJSON).forEach(function (prop) {
            var parent_string = 'parent.';
            var jsonValue = eval(parent_string.concat(prop));
            if(typeof jsonValue !== 'undefined') {
                if (jsonValue !== "" && (typeof jsonValue === 'number' || !isNaN(jsonValue) || typeof jsonValue === 'boolean')) {
                    updatedJson[prop] = jsonValue;
                } else {
                    if (jsonValue.indexOf('"') === 0 || jsonValue.indexOf("'") === 0) {
                        updatedJson[prop] = jsonValue;
                    } else {
                        updatedJson[prop] = "'" + jsonValue + "'";
                    }
                }
            }
        });

        pdmVar[pubId + '_prevJsonObject'] = updatedJson;
        var nodeJSON = ProcessEngine.createNodeJSON(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_step']);
        pdmVar[pubId + '_prevJsonObject'] = ProcessEngine.jsonConcat(pdmVar[pubId + '_prevJsonObject'], nodeJSON);
        pdmVar[pubId + '_stack'].push(pdmVar[pubId + '_prevJsonObject']);
    } else {
        var nodeJSON = ProcessEngine.createNodeJSON(pdmVar[pubId + '_currentNode'], pdmVar[pubId + '_step']);
        stackJSON = ProcessEngine.jsonConcat(stackJSON, nodeJSON);
        pdmVar[pubId + '_stack'].push(stackJSON);
    }
};

ProcessEngine.isAssertable = function (child) {
    return ProcessEngine.checkdivElement(child, "assertion");
};

//This method checks if preset values are present or not
ProcessEngine.isPresetAvailable = function (child) {
    if (child != '' && document.getElementById(child)) {
        if (document.getElementById(child).hasAttribute("hasPreset")) {
            var hasPreset = document.getElementById(child).getAttribute("hasPreset");
            if (hasPreset === 'true') {
                return true;
            }
            else {
                return false;
            }
        }
    }
};

ProcessEngine.findParentId = function (ofThisNode) {
    return document.getElementById(ofThisNode).parentElement.id
};

ProcessEngine.displayCurrentNode = function (displayNode) {
    document.getElementById(displayNode).style.display = "block";
};

ProcessEngine.hidePreviousDMNode = function () {
    if(ProcessEngine.checkdivElement(pdmVar[pubId + '_currentNode'], dialog_alts)) {
        if(document.getElementById(pdmVar[pubId + '_currentNode']).parentElement){
            var parentOfParentNode = document.getElementById(pdmVar[pubId + '_currentNode']).parentElement.id;
            if (parentOfParentNode) {
                document.getElementById(parentOfParentNode).style.display = "none";
                var dialogAltsCount = document.getElementById(pdmVar[pubId + '_currentNode']).childElementCount

                for (var index = 0; index <= dialogAltsCount; index++) {
                    if (document.getElementById(pdmVar[pubId + '_currentNode']).children[index]) {
                        var dmnode = document.getElementById(pdmVar[pubId + '_currentNode']).children[index].id;
                        document.getElementById(dmnode).style.display = "none";
                    }
                }
            }
        }

    } else if (document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_currentStep']]) {
        pdmVar[pubId + '_prevNode'] = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_currentStep']].id;
        if (pdmVar[pubId + '_prevNode']) {
            document.getElementById(pdmVar[pubId + '_prevNode']).style.display = "none";
        }
    }
};

ProcessEngine.isThisChildPresent = function (childNode, childName, menuValue) {
    var divChilds = document.getElementById(childNode).getElementsByTagName('DIV');
    var divIds = [];
    for (var child in divChilds) {
        if (divChilds.hasOwnProperty(child)) {
            if (divChilds[child].tagName === 'DIV' && ProcessEngine.checkdivElement(divChilds[child].id, childName)) {
                divIds[divChilds[child].id] = divChilds[child].id;
            }
        }
    }
    return divIds;
};

ProcessEngine.validateIfDialog = function () {
    var childNode = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_currentStep']].id;
    if(ProcessEngine.checkdivElement(childNode, dm_dialog)){
        return ProcessEngine.validateUserEntries(childNode);
    }
    var divChilds = document.getElementById(childNode).childNodes;
    for (var child in divChilds) {
        if (divChilds.hasOwnProperty(child)) {
            if (divChilds[child].tagName === 'DIV' && ProcessEngine.checkdivElement(divChilds[child].id, dm_dialog)) {
                return ProcessEngine.validateUserEntries(divChilds[child].id);
            }
        }
    }
};

ProcessEngine.evaluateMenuChoice = function () {
    var childNode = document.getElementById(pdmVar[pubId + '_currentNode']).children[pdmVar[pubId + '_currentStep']].id;
    var reassignJSON = {};
    var menuValue = ProcessEngine.getMenuChoicesValue(childNode);
    var menuChoiceDivs = ProcessEngine.isThisChildPresent(childNode, dm_menuchoice);
    for (var radioDiv in menuChoiceDivs) {
        method_prefix = radioDiv.split("-").join('');
        method_suffix = "assertion" + menuValue;
        if (document.getElementById(method_prefix + method_suffix)) {
            ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_menuchoices'][method_prefix + method_suffix]);
            reassignJSON = ProcessEngine.getReassignment(method_prefix + method_suffix + "reassign");
            break;
        }

    }

    return reassignJSON;

};

ProcessEngine.getReassignment = function (menuReassignValue) {
    var reassignContent = {};
    if (document.getElementById(menuReassignValue)) {
        reassignContent = document.getElementById(menuReassignValue).innerText.replace(/(\r\n|\n|\r)/gm, " ").replace(/ +/g, " ");
        if(reassignContent !== '') {
            reassignContent = JSON.parse(reassignContent);
        }
    }
    return reassignContent ;
};

ProcessEngine.getMenuChoicesValue = function (childNode) {
    var radioLength = document.getElementById(childNode).getElementsByTagName('form')[childNode + '-dialogForm']['choices'].length;
    var choiceValues = document.getElementById(childNode).getElementsByTagName('form')[childNode + '-dialogForm']['choices'];
    var selectedChoice;
    for (var i=0 ; i< radioLength; i++)
    {
        if(choiceValues[i].checked)
        {
            var result = (choiceValues[i].value);
            selectedChoice = result.split(" ").join('');
        }
    }
    return selectedChoice;
};

ProcessEngine.executeFunction = function(body) {
    var functionCall = new Function(body);
    return functionCall();
};

ProcessEngine.getApplicRef = function(applic) {
    for (var key in pdmVar[pubId + '_dyn_functions']) {
        var isValid = (key.lastIndexOf(applic) == (key.length - applic.length));
        if(isValid){
            return pdmVar[pubId + '_dyn_functions'][key];
        }
    }
};

ProcessEngine.processAlts = function (child) {
    var altWorkflow = '';
    if (!ProcessEngine.checkdivElementAlts(child)) {
        pdmVar[pubId + '_currentNode'] = document.getElementById(child).children[0].id;
    }
    var altsSeqCount = document.getElementById(child).childElementCount;

    for (var index = 0; index <= altsSeqCount; index++) {
        if (!resetAltsFlow) {
            if (document.getElementById(child).children[index]) {
                var seqNode = document.getElementById(child).children[index].id;
                var seqApplic = document.getElementById(seqNode).getAttribute("applic");
                var applicRef = ProcessEngine.getApplicRef(seqApplic);
                var showSeq = ProcessEngine.executeFunction(applicRef);
                if (showSeq) {
                    resetAltsFlow = true;
                    altWorkflow = seqNode;
                }
            }
        }
    }
    resetAltsFlow = false;
    return altWorkflow;
};

/** This method checks if dialog is present or not **/
ProcessEngine.processDMLoop = function (child) {
    method_prefix = child.split("-").join('');
    method_suffix = loop_sequence;
    var loopSeq = ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
    document.getElementById(child).style.display = "block";
    ProcessEngine.showActiveNavigationButtons(pdmVar[pubId + '_step'], loopSeq);
    ProcessEngine.processLogicEngine('', startIndex, loopSeq);
};


ProcessEngine.goLevelUpOrDown = function (nodeLevelUp, navigation) {
    var childIndex;
    var levelNode;
    if (document.getElementById(nodeLevelUp)) {
        childIndex = ProcessEngine.getChildIndex(document.getElementById(nodeLevelUp).parentElement.id);
        pdmVar[pubId + '_node'] = document.getElementById(nodeLevelUp).parentElement.parentElement.id;
    } else {
        childIndex = ProcessEngine.getChildIndex(nodeLevelUp.split('-').slice(0, -1).join('-'));
        pdmVar[pubId + '_node'] = document.getElementById(nodeLevelUp.split('-').slice(0, -1).join('-')).parentElement.id;
    }
    levelNode = pdmVar[pubId + '_node'];
    while (ProcessEngine.checkdivElement(levelNode, dm_then_seq) || ProcessEngine.checkdivElement(levelNode, dm_else_seq)) {
        levelNode = document.getElementById(levelNode).parentElement.parentElement.id;
        if(ProcessEngine.checkdivElement(document.getElementById(levelNode).parentElement.id, dm_If)) {
            pdmVar[pubId + '_currentNode'] = document.getElementById(levelNode).parentElement.id;
            childIndex = ProcessEngine.getChildIndex(pdmVar[pubId + '_currentNode']);
        }
    }
    pdmVar[pubId + '_node'] = levelNode;
    if (navigation === pdmVar['previous'] || navigation === pdmVar['cancel']) {
        pdmVar[pubId + '_currentStep'] = childIndex - 1;
    } else {
        pdmVar[pubId + '_currentStep'] = childIndex + 1;
    }
    if (document.getElementById(pdmVar[pubId + '_node']).children[pdmVar[pubId + '_currentStep']]) {
        child = document.getElementById(pdmVar[pubId + '_node']).children[pdmVar[pubId + '_currentStep']].id;
    } else {
        var loopDiv = document.getElementById(pdmVar[pubId + '_node']).parentElement.id;
        if (ProcessEngine.checkdivElement(loopDiv, dmloop)) {
            method_prefix = loopDiv.split("-").join('');
            method_suffix = loop_suffix;
            var isEvaluateLoopCondition = ProcessEngine.executeFunction(pdmVar[pubId + '_dyn_functions'][method_prefix + method_suffix]);
            if (isEvaluateLoopCondition) {
                pdmVar[pubId + '_currentStep'] = 0;
                child = document.getElementById(pdmVar[pubId + '_node']).children[pdmVar[pubId + '_currentStep']].id;
            } else {
                child = ProcessEngine.goLevelUpOrDown(pdmVar[pubId + '_node'], navigation);
            }
        }
    }
    return child;
};

ProcessEngine.getChildIndex = function (child) {
    var parentNode = document.getElementById(child).parentElement.id;
    if (ProcessEngine.checkdivElement(parentNode, dm_then_seq) || ProcessEngine.checkdivElement(parentNode, dm_else_seq)) {
        child = document.getElementById(parentNode).parentElement.id;
        parentNode = document.getElementById(parentNode).parentElement.parentElement.id;
        pdmVar[pubId + '_node'] = parentNode;
    }
    var children = document.getElementById(parentNode).childElementCount;
    pdmVar[pubId + '_node'] = parentNode;
    var index = children - 1;
    for (; index >= 0; index--) {
        if (child === document.getElementById(parentNode).children[index].id) {
            break;
        }
    }
    return index;
};

ProcessEngine.isDialogAvailable = function (child) {
    return ProcessEngine.checkdivElement(child, dm_dialog);
};

ProcessEngine.checkdivElement = function (child, id) {
    var token = child.split("-");
    if (token.pop().indexOf(id) === 0) {
        return true;
    }
    else {
        return false;
    }
};

ProcessEngine.checkdivElementAlts = function (child) {
    var token = child.split("-");
    var lastElement = token.pop();
    if (lastElement.indexOf(dialog_alts) === 0 || lastElement.indexOf(dmnode_alts) === 0 || lastElement.indexOf(dmseq_Alts) === 0 ) {
        return true;
    }
    else {
        return false;
    }
}


ProcessEngine.isLoopAvailable = function (child) {
    return ProcessEngine.checkdivElement(child, dmloop);
};

ProcessEngine.isAltsAvailable = function (child) {
    if(document.getElementById(child)) {
        var dialogAlts = ProcessEngine.isChildNodeAlts(child);
        if (ProcessEngine.checkdivElement(child, dmseq_Alts) || ProcessEngine.checkdivElement(child, dmnode_alts)
            || ProcessEngine.checkdivElement(child, dialog_alts) || dialogAlts) {
            return true;
        } else {
            return false;
        }
    }
};

ProcessEngine.isChildNodeAlts = function (child) {
    var childern = document.getElementById(child).children[0].id;
    if (childern !== 'undefined') {
        if (this.checkdivElement(childern, dialog_alts)) {
            return true;
        }
    }
    return false;
}

ProcessEngine.isSeqAvailable = function (child) {
    return ProcessEngine.checkdivElement(child, dm_seq);
}

ProcessEngine.isConditionAvailable = function (child) {
    return ProcessEngine.checkdivElement(child, dm_If);
}

/** This method hides the navigation buttons when dialog appears **/
ProcessEngine.hideNavigationButtons = function () {
    document.getElementById(pdmVar[pubId + '_navigation_button']).style.display = "none";
}

/** This method dynamically creates and shows the navigation buttons **/
ProcessEngine.showActiveNavigationButtons = function () {
    var nav_buttons = "<div id='" + pdmVar[pubId + '_navigation_buttons'] + "'>" ;
    var previousStep = (pdmVar[pubId + '_step']) - 1;
    var nextStep = (pdmVar[pubId + '_step']) + 1;
    var rootNodeChildCount = document.getElementById(pdmVar[pubId + '_rootNode']).childElementCount;
    if (!(pdmVar[pubId + '_currentNode'] === pdmVar[pubId + '_rootNode'] && previousStep === -1)) {
        if (previousStep === -1) {
        }
        nav_buttons += "<button type='submit' class=\"btn-success\" onclick=ProcessEngine.processLogicEngine('"+pdmVar['previous'] + "'" + "," + previousStep + "," + "'" + pdmVar[pubId + '_currentNode'] + "')>Previous</button>&nbsp;&nbsp;&nbsp;&nbsp;";
    }

    if (!(pdmVar[pubId + '_currentNode'] === pdmVar[pubId + '_rootNode'] && nextStep >= rootNodeChildCount)) {
        nav_buttons += "<button type='submit' class=\"btn-success\" onclick=ProcessEngine.processLogicEngine('"+ pdmVar['next'] + "'" + "," + nextStep + "," + "'" + pdmVar[pubId + '_currentNode'] + "')>Next</button>"
    }
    nav_buttons += "</div>";

    document.getElementById(pdmVar[pubId + '_navigation_button']).innerHTML = nav_buttons;
    document.getElementById(pdmVar[pubId + '_navigation_button']).style.display = "block";
};

/** This method retrieves the previous system state **/
ProcessEngine.getPreviousSystemState = function () {
    if(pdmVar[pubId + '_stack'].size() > 1) {
        pdmVar[pubId + '_previous_step'] = pdmVar[pubId + '_stack'].pop();
        return pdmVar[pubId + '_stack'].peek();
    } else {
        pdmVar[pubId + '_previous_step'] = pdmVar[pubId + '_stack'].pop();
        return pdmVar[pubId + '_previous_step'];
    }
};

ProcessEngine.setupView = function (contentData) {
    scopeContent = angular.element("#content").scope();
    pdmVar = scopeContent.processVariables;
    console.log("*************"+JSON.stringify(pdmVar));
    pubId = contentData.publication.id.split("-").join('');
    content = contentData.content;
    ProcessEngine.getAllVariableDeclarations(content);
    pdmVar[pubId + '_dyn_functions'] = ProcessEngine.retrieveDynamicFunctionsAndVariables('', dm_functions, 'functions');
    pdmVar[pubId + '_dyn_menuchoices'] = ProcessEngine.retrieveDynamicFunctionsAndVariables('', dm_functions, 'menufunctions');
};

ProcessEngine.processAllPresetAndPostset = function (Object1, Object2) {
    if (Object1.length === 0) {
        Object1 = pdmVar[pubId + '_prevJsonObject'];
    }
    ProcessEngine.pushToStack(Object1, Object2);
};

/**This method pushes the json object to stack by comparing with the prev json and current preset value**/
ProcessEngine.pushToStack = function (Object1, Object2) {
    var target = [];
    var temp_map = new Map();
    var jsonObjectOfMap = {};

    for (var key in Object1) {
        if(JSON.stringify(Object2) === '{}') {
            jsonObjectOfMap = Object1;
        } else {
            for (var obj_k in Object2) {
                if (key === obj_k) {
                    jsonObjectOfMap[key] =  Object2[key];
                }
                else (key !== obj_k)
                {
                    jsonObjectOfMap[obj_k] = Object2[obj_k];
                    //check for other key's in base json
                    if (!Object2.hasOwnProperty(key)) {
                        jsonObjectOfMap[key] = Object1[key];
                    }
                }
            }
        }
    }
    pdmVar[pubId + '_prevJsonObject'] = jsonObjectOfMap;
    var nodeJSON = ProcessEngine.createNodeJSON(pdmVar[pubId + '_rootNode'], 0);
    pdmVar[pubId + '_prevJsonObject'] = ProcessEngine.jsonConcat(pdmVar[pubId + '_prevJsonObject'], nodeJSON);
    pdmVar[pubId + '_stack'].push(pdmVar[pubId + '_prevJsonObject']);
};
//logic engine ends here