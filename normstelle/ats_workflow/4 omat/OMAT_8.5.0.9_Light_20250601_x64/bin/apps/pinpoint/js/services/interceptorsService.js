/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
	// body...
	'use strict';

	angular.module('app').config(['$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.cache = false;
        if (!$httpProvider.defaults.headers.get) {
            $httpProvider.defaults.headers.get = {};
        }
            // disable IE ajax request caching
       // $httpProvider.defaults.headers.get['If-Modified-Since'] = 'Mon, 26 Jul 1997 05:00:00 GMT';
        //$httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
	 
            // $httpProvider.interceptors.push('interceptorService');.
            // 
        $httpProvider.interceptors.push(function($q,$cookies,$rootScope) {
			return {
				'request': validateLogin,
				'response': invalidLogin
			};

			function validateLogin(request) {
					
				request.headers.CurrentLanguage = $rootScope.currentLanguage;
				$httpProvider.defaults.headers.common["Accept-Language"] = $rootScope.currentLanguage;
				return request;
			}

			function invalidLogin(response) {
                 
				if(response.status === 401) {
	
					$rootScope.$broadcast('appLogout', {message: $rootScope.getNotSignedInMessage()});
				}

				if(response.data && response.data.error_code === "3037"){
					$rootScope.$broadcast('appLogout', {message: $rootScope.getNotSignedInMessage()});
				}
				// return $q.reject(response);
				return response;
			}

		});

		
	}]);



     

   

	
})();