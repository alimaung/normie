/**
 * @copyright (c) 2016 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 300 Spectrum Center Drive, Suite 700, Irvine, CA 92618, USA
 */

(function () {
    'use strict';

    angular
        .module('app')
        .controller('MainContentController', MainContentController);

    function MainContentController($rootScope) {
        var vm = this;

        vm.showConfiguration = false;
        vm.showLandingPage = false;
        vm.showContent = true;
        vm.closeLandPage = closeLandPage;
        vm.showReadAndSign = false;
        vm.goToHomePage = goToHomePage;
        vm.closeMergeTab = closeMergeTab;

        //showLandingPage();

        $rootScope.$on('contentUpdated', showContent);
        $rootScope.$on('openConfiguration', openConfiguration);
        $rootScope.$on('landingPageOpened', showLandingPage);
        $rootScope.$on('closeMergeTab', closeMergeTab);
        $rootScope.$on('finPopup', showFinPopup);
        $rootScope.$on('showReadAndSignList', showReadAndSignList);
        $rootScope.$on('closeReadSignPage', onCloseReadSignPage);
        $rootScope.$on('tocParentSelected', HideContent);
        $rootScope.$on('publicationChanged', HideContent);
        $rootScope.$on('openGraphicSheet', showContent);
		$rootScope.$on('loadingContent', showContent);
		$rootScope.$on('openAuthoringMerge', showAuthoringMerge);

		function closeMergeTab() {
            vm.showAuthoringMerge = false;
            vm.showLandingPage = true;
        }

        function showAuthoringMerge(event, message) {
            if (!vm.showAuthoringMerge) {
                vm.showAuthoringMerge = true;
                vm.showConfiguration = false;
                vm.showReadAndSign = false;
                vm.showLandingPage = false;
                vm.showContent = false;
            }
            hideGraphicPane();
        }

        function showReadAndSignList(){
            if (!vm.showReadAndSign) {
                hideGraphicPane();
                vm.showLandingPage = false;
                vm.showReadAndSign = true;
                vm.showConfiguration = false;
                vm.showContent = false;
            }
        }
        
        function HideContent() {
            hideGraphicPane();
            vm.showContent = false;
        }

        function showContent() {
            if (!vm.showContent) {
                showGraphicPane();
                vm.showContent = true;
                vm.showReadAndSign = false;
                vm.showLandingPage = false;
                vm.showConfiguration = false;
                vm.showAuthoringMerge = false;
            }
        }

        function showFinPopup(event,message){
            showContent();
            $rootScope.$broadcast('showFinPopup', message);
            
        }

        function showLandingPage(event,message) {
            if (!vm.showLandingPage) {
                hideGraphicPane();

                vm.showLandingPage = true;
                vm.showReadAndSign = false;
                vm.showConfiguration = false;
                vm.showContent = false;
                $rootScope.showSplashPage = true;
                vm.showAuthoringMerge = false;
            }

            if(message.showHome && message.showHome === true) {
                vm.publication = message.publication;
                vm.library = message.library;
                vm.showHome = message.showHome;
            } else {
                vm.publication = null;
                vm.library = null;
                vm.showHome = false;
            }
        }

        function openConfiguration() {
            if (!vm.showConfiguration) {
                hideGraphicPane();

                vm.showConfiguration = true;
                vm.showReadAndSign = false;
                vm.showLandingPage = false;
                vm.showContent = false;
                vm.showAuthoringMerge = false;
            }
        }

        function hideGraphicPane() {
            w2ui.layout.hide("right", true);
            setTimeout(function () {
                $("#layout_layout_resizer_right").hide();
            },3000);
        }

        function showGraphicPane() {
            w2ui.layout.show("right", true);
            $("#layout_layout_resizer_right").show();
        }

        function closeLandPage() {
            showContent();
        }

        function onCloseReadSignPage(){
            vm.showReadAndSign = false;
        }

        function goToHomePage() {
            $rootScope.$broadcast("publicationLandingCheck", {library: vm.library, publication: vm.publication});
        }
    }




})();
