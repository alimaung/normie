/**
 * @copyright (c) 2016 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

/**
 * GotoService
 * @requires $rootScope
 * @requires $location
 * @requires $timeout
 * @requires DataService
 **/
 (function() {
angular.module('app').service('ExtResourceService', function($window, appConf) {

	this.isExtResourcePublication = function (libraryID,publicationID) {
		// body...
		
		var extResources = appConf.externalPublish;
		if(extResources && Array.isArray(extResources)){
			for(var i=0;i<extResources.length;i++){
				if(extResources[i].libraryID === libraryID && extResources[i].publicationID === publicationID){
					return extResources[i].externalURL;
				}
			}

		}


		return "";
	};

	this.openExtResourceUrl = function(extResourceUrl){
		$window.open(extResourceUrl);
	};

	this.openExtResourceUrlInNewTab = function(extResourceUrl){
		$window.open(extResourceUrl,'_blank');
	};


});

})();
