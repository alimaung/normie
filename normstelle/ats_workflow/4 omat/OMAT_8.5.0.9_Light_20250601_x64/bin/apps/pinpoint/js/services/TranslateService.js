/*
 (c) 2016 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
*/
angular.module("app").service("TranslateService",["$rootScope","$translate",function($rootScope,$translate){var mf=new MessageFormat("en");this.$translate=$translate;this.translate=function(defaultValue,translateKey,interpolateParams){var value;if(isNotNull($rootScope)&&$rootScope.env==="pinpoint7"&&isNotNull(translateKey))if(isNotNull(interpolateParams))value=$translate.instant(translateKey,interpolateParams,"messageformat");else value=$translate.instant(translateKey);else{value=defaultValue;if(isNotNull(interpolateParams))value=
mf.compile(value)(interpolateParams)}return value};this.onReady=function(callbackFn){if(isNotNull($rootScope)&&$rootScope.env==="pinpoint7")$translate.onReady(function(){callbackFn()});else callbackFn()}}]);
