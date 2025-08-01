/**
 * This service is introduced to call '/print/searchresult' end point to print search results.
 **/
 
 angular.module('app').service('PrintService', function($rootScope, DataService, $translate, $q) {

   this.printSearchResults = function (content, title, message) {
      var defer = $q.defer();
      var param = {
          content: content,
          printoutTitle: title,
          printFilter: this.getPrintFilter(),
          printDateTime: this.getFormatedHeaderDate(),
          displayLabels: this.getDisplayLabels(),
          printSearchModel: message
        };
        var actions = [];
        var action = DataService.generateWidgetActionWithUrl($rootScope.basePinpointAction, "/print/searchresult", "POST", param, null);
        action.responseType = "arraybuffer";
        actions.push(action);
        DataService.showMessage($translate.instant('app.alert.printProgressMessage'), "success", 5000);
        DataService.actionsDriverPromise(actions, -1).then(function (response) {
                if (response) {
                    var fileName = title.replace(" ","") + "_" + generateUniqueId() + ".pdf";
                    openPdf(response, fileName);
                    defer.resolve(response);
                }
            }
        );
        return defer.promise;
   };

     this.printHtml = function (printHtml, message) {
         var defer = $q.defer();
         var param = this.getParams(printHtml,message);
         var actions = [];
         var action = DataService.generateWidgetActionWithUrl($rootScope.basePinpointAction, "/print/selectedTable", "POST", param, null);
         action.responseType = "arraybuffer";
         actions.push(action);
         DataService.actionsDriver(actions, function (responses) {
             if (isNotNull(responses)) {
                 var fileName = message.library.name + "-" + "[" + message.publication.description + "]" + "[" + message.page.title + "]" + ".pdf";
                 openPdf(responses, fileName);
                 defer.resolve(responses);
             }
         }, -1, $);
         return defer.promise;
     }

   this.generateTablesForPrint = function (tables, message){
       var defer = $q.defer();
       //Filter table which has row selection
       var filteredTable = tables.filter(function(index, table){
           var tableElement = angular.element(table);
           var checkedTr = tableElement.find('.pp-checked-row');
           if(checkedTr.length !== 0){
               return table;
           }
       });

       var tablesHtml = "";
       for(var i =0; i<filteredTable.length; i++){
           var sourceTable = angular.element(filteredTable[i]);
           //Remove ng-transclude from table
           sourceTable.find('ng-transclude').children().unwrap();

           //Normalize table and generate row/col span only when partial selection of the table is made.
           if(!this.isSelectAllCheckBoxEnabled(sourceTable)){
               var normalizedTableAsList = this.normalizeTable(sourceTable[0]);
               var tBodyRows = sourceTable.find('> tbody > tr');
               //Remove all the tbody rows
               tBodyRows.remove();

               //Re-construct table based on the normalized table data and also filter the selected rows
               for(var index=0; index<normalizedTableAsList.length; index++) {
                   var normalizedRow = normalizedTableAsList[index];
                   var tr = angular.element(normalizedRow.row);
                   //Check if the row is selected
                   if (tr.hasClass("pp-checked-row")){
                       tr.find("> td").remove();
                       for (var key in normalizedRow) {
                           if (normalizedRow.hasOwnProperty(key) && key !== "row") {
                               var td = $(normalizedRow[key]).clone();
                               td.removeAttr("rowspan");
                               td.removeAttr("colspan");
                               tr.append(td);
                           }
                       }
                       sourceTable.find("> tbody").append(tr);
                   }
               }
               this.generateSpan(sourceTable);
           }
           sourceTable.find(".checkBoxCell").remove();
           tablesHtml = tablesHtml.concat("<div class=\"content-margin-offset\">" + sourceTable[0].outerHTML + "<br></div>");
       }

       var param = this.getParams(tablesHtml,message);
       var actions = [];
       var action = DataService.generateWidgetActionWithUrl($rootScope.basePinpointAction, "/print/selectedTable", "POST", param, null);
       action.responseType = "arraybuffer";
       actions.push(action);
       DataService.actionsDriver(actions, function (responses) {
           if (isNotNull(responses)){
               defer.resolve(responses);
           }
       }, -1, $);
       return defer.promise;
   }

     this.isSelectAllCheckBoxEnabled = function(sourceTable){
         var thead = sourceTable.find("thead");
         if(thead.length !== 0){
             var firstTr = thead.find("tr:first");
             if(firstTr.length !==0){
                 return firstTr.find(".checkBoxCell input").prop("checked");
             }
         }
         return false;
     }

     /**
      * Normalize given table to equal rows and columns based on row/col span
      * @param table
      * @returns {*[]}
      */
     this.normalizeTable = function (table) {
         var res = [];
         var trs = table.querySelectorAll(':scope > tbody > tr')
         for(var rowIndex=0; rowIndex<trs.length; rowIndex++){
             var row = trs[rowIndex];
             var tds = trs[rowIndex].querySelectorAll(':scope > td');
             for(var cellIndex=0; cellIndex<tds.length; cellIndex++){
                 var cell = tds[cellIndex];
                 var rowspan = Number(cell.getAttribute('rowspan') || 1);
                 var colspan = Number(cell.getAttribute('colspan') || 1);
                 var tempCellIndex = cellIndex;
                 while (res[rowIndex] && res[rowIndex][tempCellIndex]) {
                     tempCellIndex++;
                 }
                 for (var yy = rowIndex; yy < rowIndex + rowspan; yy++) {
                     var resRow ={};
                     if (isNotNull(res[yy])) {
                         resRow = res[yy];
                     }else{
                         resRow = res[yy] = [];
                     }
                     for (var j = 0; j < colspan; j++) {
                         resRow.row = row;
                         resRow[tempCellIndex + j] = cell;
                     }
                 }
             }
         }
         return res.filter(function (row) {
             return row.length > 0;
         });
     };

     /**
      * Generate row/col span for the given table based on that table data
      * @param table
      */
     this.generateSpan = function(table){
         var i = 0;
         var trs = table.find('> tbody > tr');
         trs.each(function(index,tr) {
             var tds = $(tr).find('> td');
             var width = tds.length;
             for(i = width - 2; i >= 0; i--) {
                 if($(tds[i]).html() === $(tds[i + 1]).html() && $(tds[i]).html() !== ""){
                     $(tds[i]).prop('colspan', $(tds[i + 1]).prop('colspan') + 1);
                     $(tds[i + 1]).remove();
                 }
             }
             tds = $(tr).find('> td');
             width = tds.length;
             $(tds[0]).attr('seq', 0);
             for(i = 1; i < width; i++) {
                 $(tds[i]).attr('seq', parseInt($(tds[i - 1]).attr('seq')) + $(tds[i - 1]).prop('colspan'));
             }
         });

         var height = trs.length;
         for(i = height - 2; i >= 0; i--){
             $(trs[i]).find('> td').each(function(index,td) {
                 var seq = parseInt($(td).attr('seq'));
                 var tdUnder = $(trs[i + 1]).find('td[seq="' + seq + '"]');
                 if(tdUnder.length && (tdUnder.html() !== "") && (tdUnder.html() === $(td).html()) && (tdUnder.prop('colspan') === $(td).prop('colspan'))) {
                     $(td).prop('rowspan', tdUnder.prop('rowspan') + 1);
                     tdUnder.remove();
                 }
             });
         }
     };

     this.getPrintFilter = function (){
         var printFilter = null;
         if (isNotNull($rootScope.selectedFilter) && isNotNull($rootScope.selectedFilter.readableFilterAttrValues)) {
             printFilter = this.getMaxCount($rootScope.selectedFilter.readableFilterAttrValues, $rootScope.selectedFilter.selectedRows);

             if (printFilter.match(".*=ALL")) {
                 printFilter = "ALL";
             }
         }
         if(!isNotNull(printFilter))
             printFilter = "";

         return printFilter;
     }

     this.getMaxCount = function (printFilter, selectedRows) {
         var splitArr = printFilter.split(",");
         var maxCount = "";

         //Check configured number as the maximum length to show effectivity in print footer
         for (var i = 0; i < splitArr.length; i++) {
             var currentStr = splitArr[i].trim();

             if (maxCount.length + currentStr.length <= $rootScope.maximumLengthForPrintingEffectivity) {
                 maxCount += currentStr + ", ";
             } else {
                 maxCount = maxCount.substr(0, maxCount.length - 2) + " (of " + selectedRows.length + " selected)";
                 return maxCount;
             }
         }
         maxCount = maxCount.substr(0, maxCount.length - 2);
         return maxCount;
     }

     this.getDisplayLabels = function () {
         var revisionDateLabel = $translate.instant(geti18nKey('app.title.revisionDate', $rootScope.i18nKeyOverrides));
         return {"revisionDateLabel": revisionDateLabel};
     }

     this.getParams = function (content,message){
         return {
             content: content,
             publicationId: message.publication.id,
             sourceDocumentId: message.page.sourceDocumentId,
             revision: message.publication.revision,
             printFilter : this.getPrintFilter(),
             printDateTime: this.getFormatedHeaderDate(),
             displayLabels: this.getDisplayLabels()
         };
     }

     this.getFormatedHeaderDate = function () {
         var dateFormat = $rootScope.dateFormat.toUpperCase();
         var dateAndTimeFormat = dateFormat + " " + $rootScope.timeFormat;
         return moment(new Date()).format(dateAndTimeFormat);
     }
 });
