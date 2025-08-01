
(function () {
    'use strict';

    angular
        .module('app')
        .directive('mainContent', mainContent);

    function mainContent()
    {
        return {
            restrict: 'AE',
            scope: {},
            templateUrl: 'views/mainContent.html',
            controller: 'MainContentController',
            controllerAs: 'vm'
        };
    }
})();
