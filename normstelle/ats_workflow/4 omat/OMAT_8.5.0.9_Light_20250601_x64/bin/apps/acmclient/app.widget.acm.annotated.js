/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users')
        .controller('UserModalController', UserModalController);

    UserModalController.$inject = ['$rootScope', '$scope', '$uibModalInstance', 'userService','userGroupNcage'];

    /* @ngInject */
    function UserModalController($rootScope, $scope, $uibModalInstance, userService,userGroupNcage) {
        var vm = this;
        vm.cancel = cancel;
        vm.saveUser = saveUser;

        vm.selectUsers = selectUsers;
        vm.retrieveUsers = retrieveUsers;
        vm.setData = setData;

        vm.limit = 10;
        vm.totalSize = 0;
        vm.currentPage = 1;

        vm.orderBy = 'name';
        vm.sortAscending = true;
        vm.includeInactive = false;

        vm.searchText = '';
        vm.prevSearchText = null;
        vm.users = [];
        vm.userNameSelectedUser = [];

        retrieveUsers();

        $scope.$on('refreshUsers', retrieveUsers);

        function retrieveUsers() {
            var isNewSearch = vm.searchText !== vm.prevSearchText;
            if (isNewSearch) {
                vm.currentPage = 1;
            }

            var offset = (vm.currentPage-1) * vm.limit;

            userService.getUsers(vm.searchText, offset, vm.limit, vm.orderBy, vm.sortAscending, vm.includeInactive,userGroupNcage)
                .then(function (data) {
                    setData(data);
                    vm.orderBy = data.orderBy;
                    vm.sortAscending = data.sortAscending;

                    if (isNewSearch) {
                        vm.prevSearchText = vm.searchText;
                        $rootScope.$broadcast('updateStatusText', data.totalSize + ' user(s) found.');
                    }
                });
        }

        function selectUsers() {
            vm.userNameSelectedUser = [];
            $('#userModalSelect option:selected').each(function() {
                var obj = $.parseJSON($( this ).val());
                vm.userNameSelectedUser.push(obj);
            });
        }

        function setData(data) {
            vm.users = data.users;
            vm.totalSize = data.totalSize;
        }

        function cancel() {
            $uibModalInstance.dismiss();
        }

        function saveUser() {
            var result = vm.userNameSelectedUser;

            $uibModalInstance.close(result);

            vm.userNameSelectedUser = [];
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users')
        .directive('userList', userList);

    userList.$inject = [];

    /* @ngInject */
    function userList()
    {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/users/userList/userList.html',
            controller: 'UserListController',
            controllerAs: 'vm'
        };
    }
})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users')
        .controller('UserListController', UserListController);

    UserListController.$inject = ['$rootScope', '$scope', '$stateParams', 'userService'];

    /* @ngInject */
    function UserListController($rootScope, $scope, $stateParams, userService) {
        var vm = this;
        vm.selectUser = selectUser;
        vm.retrieveUsers = retrieveUsers;
        vm.sort = sort;
        vm.setData = setData;

        ////////////////////////////////////////////////

        vm.limit = 10;
        vm.totalSize = 0;
        vm.currentPage = 1;

        vm.orderBy = 'name';
        vm.sortAscending = true;
        vm.includeInactive = false;

        vm.searchText = '';
        vm.prevSearchText = null;
        vm.users = [];
        vm.userNameSelectedUser = null;

        retrieveUsers();

        $scope.$on('refreshUsers', retrieveUsers);
        $scope.$on('userSelected', userSelected);

        function sort(field) {
            if (vm.orderBy === field) {
                vm.sortAscending = !vm.sortAscending;
            }

            vm.orderBy = field;
            retrieveUsers();
        }

        function retrieveUsers() {
            var isNewSearch = vm.searchText !== vm.prevSearchText;
            if (isNewSearch) {
                vm.currentPage = 1;
            }

            var offset = (vm.currentPage-1) * vm.limit;
            var ncage = '';

            userService.getUsers(vm.searchText, offset, vm.limit, vm.orderBy, vm.sortAscending, vm.includeInactive,ncage)
                .then(function (data) {
                    setData(data);
                    vm.orderBy = data.orderBy;
                    vm.sortAscending = data.sortAscending;

                    if (isNewSearch) {
                        vm.prevSearchText = vm.searchText;
                        $rootScope.$broadcast('updateStatusText', data.totalSize + ' user(s) found.');
                    }
                });
        }

        function selectUser(user) {
            var node =  {id: 'userSelected', value: user.userName};
            $rootScope.$broadcast('userSelected', node);
        }

        function userSelected(event, node) {
            vm.userNameSelectedUser = node.value;
        }

        function setData(data) {
            vm.users = data.users;
            vm.totalSize = data.totalSize;
            vm.usernameSelectedUser = $stateParams.userName;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users')
        .directive('userDetails', userDetails);

    userDetails.$inject = [];

    /* @ngInject */
    function userDetails() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/users/userDetails/userDetails.html',
            controller: 'UserDetailsController',
            controllerAs: 'vm'
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.users')
            .controller('UserDetailsController', UserDetailsController);

    UserDetailsController.$inject = ['$http', '$rootScope', '$stateParams', '$state', 'userService', 'userGroupService', '$scope', '$uibModal', '$window', 'privilegeService', '$transitions', 'flatironsAppConfigService'];

    /* @ngInject */
    function UserDetailsController($http, $rootScope, $stateParams, $state, userService, userGroupService, $scope, $uibModal, $window, privilegeService, $transitions, flatironsAppConfigService) {
        var vm = this;
        vm.retrieveUser = retrieveUser;
        vm.openOrganizationsModal = openOrganizationsModal;
        vm.toggleEdit = toggleEdit;
        vm.deleteUser = deleteUser;
        vm.saveUser = saveUser;
        vm.cancel = cancel;

        vm.editable = false;
        vm.isEditModeActivated = false;

        vm.user = {};
        vm.userDisplayRoles = [];
        vm.userDisplayGroups = [];

        retrieveUser();

        vm.userPermissions = {};

        vm.currentUserName = $stateParams.userName;
        vm.deleteAccessKey = deleteAccessKey;
        vm.updateAccessKey = updateAccessKey;
        vm.accessKeys = [];
        vm.enableApprovalBtn = false;
        vm.resetApprovalButton = resetApprovalButton;
        vm.showGenerateSecretKey = false;
        vm.userLoadingOverlayPromise = {};

        retriveUserDetails();

        privilegeService.getPermissionTypesForResource($state.current.accessResource)
        .then(function(data) {
            vm.userPermissions = data;
        });

        flatironsAppConfigService.getAppConfig().then(function(config) {
            vm.showGenerateSecretKey = config.showGenerateSecretKey;
        });

        (function () {
            $window.onbeforeunload = beforeUnload;
            var locationChangeStartOff = $transitions.onStart( {} , beforeStateChange);
            $scope.$on('$destroy', function() {
                locationChangeStartOff();
                $window.onbeforeunload = null;
            });

            function beforeStateChange(transitions) {
                if (!transitions._aborted && vm.userDetailsForm.$dirty) {
                    transitions.abort();
                    showResetConfirmation().then(function() {
                        locationChangeStartOff();
                        $state.go(transitions.to(), transitions.params());
                    }, function() {
                        broadcastUserSelected(vm.user.userName);
                    });
                }
            }

            function beforeUnload() {
                if (vm.userDetailsForm.$dirty) {
                    return 'All changes will be lost.';
                }
            }
        })();

        function retrieveUser() {
            vm.userLoadingOverlayPromise = userService.getUser($stateParams.userName || null)
                    .then(function (data) {
                            vm.user = data;
                            vm.userDisplayRoles.length=0;
                            vm.userDisplayGroups.length=0;
                            vm.user.userGroups.forEach(function(userGroup) {
                                retrieveUserGroupDetails(userGroup.userGroupId);
                            });
                            broadcastUserSelected(data.userName);
                    });
            $rootScope.$broadcast('resolveLoadingOverlayPromise', vm.userLoadingOverlayPromise);
        }

        function retriveUserDetails(){
            userService.getUserDetails().then(function(data) {
                vm.userInfo = data;
                if (vm.currentUserName !== null && vm.userInfo && vm.currentUserName === vm.userInfo.sub) {
                    userService.getAccessKeys(vm.currentUserName).then(
                        function (data) {
                            if (data.accessKeys) {
                                vm.accessKeys = data.accessKeys;
                                resetApprovalButton();
                            }
                        }
                    );
                } else {
                    vm.accessKeys = [];
                }
            });
        }

        function retrieveUserGroupDetails(userGroupId) {
            userGroupService.getUserGroup(userGroupId)
            .then(function (data) {
                if (data.type === 'role') {
                  vm.userDisplayRoles.push(data);
                } else {
                  vm.userDisplayGroups.push(data);
                }
            });
        }

        function broadcastUserSelected(userName) {
            var node =  {id: 'userSelected', value: userName};
            $rootScope.$broadcast('userSelected', node);
        }

        function openOrganizationsModal() {
            $uibModal.open({
                        template: '<div style="height:600px"><organization-list modal="this"></organization-list></div>',
                        size: 'lg'
                    }).result.then(function(organization) {
                vm.user.organizationNcage = organization.ncage;
                vm.user.organizationName = organization.name;
                vm.userDetailsForm.$setDirty();
            });
        }

        function saveUser() {
            userService.saveUser(vm.user)
                .then(function (data) {
                    vm.user = data;
                    vm.userDetailsForm.$setPristine();
                    $rootScope.$broadcast('updateStatusText', 'User saved.');
                    toggleEdit();
                });
        }

        function cancel() {
            if (vm.userDetailsForm.$dirty) {
                showResetConfirmation().then(function(){
                    vm.userDetailsForm.$setPristine();
                    retrieveUser();
                    toggleEdit();
                });
            } else {
                toggleEdit();
            }
        }

        function showResetConfirmation() {
            return $uibModal.open({
                templateUrl: '/templates/core/modal/simpleModal.html',
                controller: 'SimpleModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: 'All changes will be lost.'
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
        }

        function deleteUser() {
            userService.deleteUser(vm.user)
                .then(function() {
                    var node = {id: 'userDeleted'};
                    $rootScope.$emit('userDeleted', node);
                    $rootScope.$emit('updateStatusText', 'User deleted.');
                });
        }

        function deleteAccessKey(accessKey) {
            return deleteAccessKeyFromServer().then(removeAccessKeyFromTable).then(deletedStatusForAccessKey);

            function deleteAccessKeyFromServer() {
                return userService.deleteAccessKey(accessKey);
            }

            function removeAccessKeyFromTable() {
                var index = vm.accessKeys.indexOf(accessKey);
                vm.accessKeys.splice(index, 1);
            }

            function deletedStatusForAccessKey() {
                resetApprovalButton();
                $rootScope.$emit('updateStatusText', 'Access key deleted.');
            }
        }

        function updateAccessKey(accessKey) {
            return updateAccessKeyToServer().then(updateAccessKeyToTable).then(updateAccessKeyStatus);

            function updateAccessKeyToServer() {
                return userService.updateAccessKey(accessKey);
            }

            function updateAccessKeyToTable(data) {
                var index = vm.accessKeys.indexOf(accessKey);
                vm.accessKeys[index] = angular.copy(data);
            }

            function updateAccessKeyStatus() {
                resetApprovalButton();
                $rootScope.$emit('updateStatusText', 'Access key updated.');
            }
        }

        function resetApprovalButton() {
            vm.enableApprovalBtn = false;
            for (var keyCount = 0; keyCount < vm.accessKeys.length; keyCount++) {
                if (vm.accessKeys[keyCount].approvedDate !== null) {
                    vm.enableApprovalBtn = true;
                    break;
                }
            }
        }

    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .controller('UserGroupModalController', UserGroupModalController);

    UserGroupModalController.$inject = ['$rootScope', '$scope', '$uibModalInstance', 'userGroupService'];

    /* @ngInject */
    function UserGroupModalController($rootScope, $scope, $uibModalInstance, userGroupService) {
        var vm = this;
        vm.cancel = cancel;
        vm.saveUserGroup = saveUserGroup;

        vm.selectUserGroups = selectUserGroups;
        vm.retrieveUserGroups = retrieveUserGroups;
        vm.setData = setData;

        vm.limit = 10;
        vm.totalSize = 0;
        vm.currentPage = 1;

        vm.orderBy = 'name';
        vm.sortAscending = true;

        vm.searchText = '';
        vm.prevSearchText = null;
        vm.userGroups = [];
        vm.groupNameSelectedUserGroups = [];

        retrieveUserGroups();

        function retrieveUserGroups() {
            var isNewSearch = vm.searchText !== vm.prevSearchText;
            if (isNewSearch) {
                vm.currentPage = 1;
            }

            var offset = (vm.currentPage-1) * vm.limit;

            var type='';

            userGroupService.getUserGroups(vm.searchText, type, offset, vm.limit, vm.orderBy, vm.sortAscending)
                .then(function (data) {
                    setData(data);
                    vm.orderBy = data.orderBy;
                    vm.sortAscending = data.sortAscending;

                    if (isNewSearch) {
                        vm.prevSearchText = vm.searchText;
                        $rootScope.$broadcast('updateStatusText', data.totalSize + ' user group(s) found.');
                    }
                });
        }

        function selectUserGroups() {
            vm.groupNameSelectedUserGroups = [];
                $('#userGroupModalSelect option:selected').each(function() {
                var obj = $.parseJSON($( this ).val());
                vm.groupNameSelectedUserGroups.push(obj);
            });
        }

        function setData(data) {
            vm.userGroups = data.userGroups;
            vm.totalSize = data.totalSize;
        }

        function cancel() {
            $uibModalInstance.dismiss();
        }

        function saveUserGroup() {
            var result = vm.groupNameSelectedUserGroups;
            $uibModalInstance.close(result);
            vm.groupNameSelectedUserGroups = [];
        }

    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .directive('userGroupList', userGroupList);

    userGroupList.$inject = [];

    /* @ngInject */
    function userGroupList()
    {
        return {
            restrict: 'E',
            scope: {
                eventname: '@eventname',
                enablecreatenew: '=enablecreatenew',
                selectfirst: '=selectfirst'
            },
            templateUrl: '/templates/usergroups/userGroupList/userGroupList.html',
            controller: 'UserGroupListController',
            controllerAs: 'vm'
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .controller('UserGroupListController', UserGroupListController);

    UserGroupListController.$inject = ['$rootScope', '$scope', '$stateParams', 'userGroupService', 'privilegeService', '$state', '$uibModal','acmConstants'];

    /* @ngInject */
    function UserGroupListController($rootScope, $scope, $stateParams, userGroupService, privilegeService, $state, $uibModal, acmConstants) {
        var vm = this;
        vm.groupOrRoleTypes = [
            {name: 'User Groups', value: 'User Groups'},
            {name: 'User Roles', value: 'User Roles'}];
        vm.currentGroupRole = 'User Groups';
        vm.toggleGroupsRoles = toggleGroupsRoles;
        vm.selectUserGroup = selectUserGroup;
        vm.sendGroupsToDetails = sendGroupsToDetails;
        vm.selectedGroupList = [];
        vm.currentGroupListItem = {};
        vm.isGroupSelected = isGroupSelected;
        vm.retrieveUserGroups = retrieveUserGroups;
        vm.retrieveUserGroup = retrieveUserGroup;
        vm.toggleMultiSelect = toggleMultiSelect;
        vm.multiSelectMode = false;
        vm.sort = sort;
        vm.setData = setData;
        vm.createUserGroup = createUserGroup;
        vm.openCSVModal = openCSVModal;
        vm.addGroup = addGroup;
        vm.addAllGroups = addAllGroups;
        vm.removeGroup = removeGroup;
        vm.removeAllGroups = removeAllGroups;
        vm.organizationResource = acmConstants.ORGANIZATIONS_RESOURCE;
        vm.copyUserGroupPrivileges = copyUserGroupPrivileges;
        vm.pasteUserGroupPrivileges = pasteUserGroupPrivileges;
        vm.isPrivileges = false;
        vm.copiedUserGroup = null;
        vm.copiedTargetUserGroup = null;


        ////////////////////////////////////////////////
        vm.selectedGroupIDs = [];
        vm.eventName = $scope.eventname;
        vm.enableCreateNew = $scope.enablecreatenew;
        vm.selectFirst = $scope.selectfirst;

        vm.limit = 10;
        vm.totalSize = 0;
        vm.currentPage = 1;

        vm.orderBy = 'name';
        vm.sortAscending = true;

        vm.searchText = '';
        vm.prevSearchText = null;
        vm.userGroups = [];
        vm.selectedUserGroupId = null;

        retrieveUserGroups();

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
            .then(function (data) {
                vm.userPermissions = data;
            });

        if ($state.current.accessResource === acmConstants.PRIVILEGES_RESOURCE) {
            privilegeService.getPermissionTypesForResource(acmConstants.CAN_SHARE_CONTENT)
                .then(function (data) {
                    if (data.Read) {
                        vm.groupOrRoleTypes.push({'name':'Organizations', 'value': 'Organizations'});
                    }
                });
        }

        var refreshUserGroupsOff = $scope.$on('refreshUserGroups', retrieveUserGroups);
        var selectUserGroupOff = $scope.$on('selectUserGroup', userGroupSelected);
        var userGroupSelectedOff = $scope.$on('userGroupSelected', userGroupSelected);
        var setGroupListReadyOff = $scope.$on('userGroupListReady', setGroupsOrRolesUI);

        $rootScope.$broadcast('userGroupListReady', '');

        function openCSVModal() {
            $uibModal.open({
                size: 'lg',
                templateUrl: '/templates/csv/upload/csvUpload.html',
                controller: 'CsvUploadController',
                controllerAs: 'vm'
            });
        }

        function sort(field) {
            if (vm.orderBy === field) {
                vm.sortAscending = !vm.sortAscending;
            }

            vm.orderBy = field;
            retrieveUserGroups();
        }

        function toggleGroupsRoles() {

            vm.selectFirst = true;

            retrieveUserGroups();

            setGroupsOrRolesUI();

            $rootScope.$broadcast('groupRolesChanged');
        }

        function retrieveUserGroups() {
            var isNewSearch = vm.searchText !== vm.prevSearchText;
            if (isNewSearch) {
                vm.currentPage = 1;
            }

            var offset = (vm.currentPage - 1) * vm.limit;

            var type;

            if (vm.currentGroupRole === acmConstants.USER_ROLES_RESOURCE) {
                type = 'role';
            }

            else if(vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE) {
                type = 'group';
            }

            else if(vm.currentGroupRole === acmConstants.ORGANIZATIONS_RESOURCE) {
                type = 'organization';
            }

            userGroupService.getUserGroups(vm.searchText, type, offset, vm.limit, vm.orderBy, vm.sortAscending)
                .then(function (data) {
                    setData(data);
                    vm.orderBy = data.orderBy;
                    vm.sortAscending = data.sortAscending;

                    if (isNewSearch) {
                        vm.prevSearchText = vm.searchText;
                        $rootScope.$broadcast('updateStatusText', data.totalSize + ' user group(s) found.');
                    }

                    if (vm.selectFirst && vm.userGroups.length > 0) {
                        vm.selectFirst = false;
                        vm.selectedGroupIDs.push(vm.userGroups[0].userGroupId);
                        vm.selectedUserGroupId = vm.userGroups[0].userGroupId;
                        selectUserGroup(vm.userGroups[0]);
                    }

                    vm.userGroups.forEach(function (userGroup, index, groups) {
                        retrieveUserGroup(userGroup.userGroupId, index, groups);
                    });
                    vm.copiedUserGroup = null;
                    vm.copiedTargetUserGroup = null;
                });
        }

        function retrieveUserGroup(userGroupId, index, groups) {

            var DELIMITER = ' | ';
            var ELLIPSIS = '...';
            var VISIBLE_CHARS = 60;
            var AVAILABLE_CHARS = 55;

            userGroupService.getUserGroup(userGroupId)
                .then(function (data) {
                    groups[index].displayName = data.name;
                    if (data.description && data.description.length > 0) {
                        var displayName = data.name + DELIMITER + data.description;
                        if (displayName.length > VISIBLE_CHARS) {
                            displayName = displayName.substring(0, AVAILABLE_CHARS) + ELLIPSIS;
                        }
                        groups[index].displayName = displayName;
                    }
                });
        }

        function setGroupsOrRolesUI() {

            if ($state.current.accessResource === acmConstants.USER_GROUPS_RESOURCE || vm.currentGroupRole === acmConstants.USER_ROLES_RESOURCE) {
                $('button#btnToggleMultiSelect').hide();
            } else {
                $('button#btnToggleMultiSelect').show();
            }

            if (w2ui.userGroupListTableLayout) {
                w2ui.userGroupListTableLayout.hide('right');
                vm.multiSelectMode = false;
            }

            if (vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE) {
                $('button#btnUploadCSVFile').show();
                $('button#btnUploadCSVFile').prop('disabled', !vm.userPermissions.Write);

            } else {
                $('button#btnUploadCSVFile').hide();
                $('button#btnUploadCSVFile').prop('disabled', true);
            }
        }

        function toggleMultiSelect() {

            w2ui.userGroupListTableLayout.toggle('right');
            vm.multiSelectMode = !vm.multiSelectMode;

            if (vm.multiSelectMode) {
                w2ui.acmlayout.sizeTo('left', 650);
            } else {
                w2ui.acmlayout.sizeTo('left', 500);
            }
        }

        function selectUserGroup(userGroup) {

            vm.selectedUserGroupId = userGroup.userGroupId;

            if (!vm.multiSelectMode) {
                vm.selectedGroupIDs = [];
            }

            var node = {
                id: vm.eventName,
                value: {
                    userGroupId: userGroup.userGroupId,
                    userGroupIDs: vm.selectedGroupIDs,
                    currentGroupRole: vm.currentGroupRole
                }
            };

            if (!vm.multiSelectMode) {
                broadcastGroupSelection(node);
            }
        }

        function broadcastGroupSelection(node) {

            switch($state.current.accessResource) {

                case 'User Groups':
                    vm.isPrivileges = false;
                    broadcastEvent($rootScope.userGroupDetails, "usergroup-details", node);
                    break;

                case 'Privileges':
                    vm.isPrivileges = true;
                    broadcastEvent($rootScope.privilegeDetails, "privilege-details", node);
                    break;

                default:
            }
        }

        function broadcastEvent(detailsExists, event, node) {
            if (detailsExists) {
                $rootScope.$broadcast(event, node);
            } else {
                $rootScope.$broadcast(vm.eventName, node);
            }
        }

        function isGroupSelected(groupId) {
            return vm.selectedGroupIDs.indexOf(groupId) > -1;
        }

        function userGroupSelected(event, node) {

            if (node.value.userGroupId) {
                vm.selectedUserGroupId = node.value.userGroupId;
            }
            else {
                //Otherwise reset to NULL, so that it re-enables the creation of a new group after cancel.
                vm.selectedUserGroupId = null;
            }
            if (node.value.userGroupIDs) {
                vm.selectedGroupIDs = node.value.userGroupIDs;
            }
            if (node.value.currentGroupRole) {
                vm.currentGroupRole = node.value.currentGroupRole;
            }
        }

        function setData(data) {
            vm.userGroups = data.userGroups;
            vm.totalSize = data.totalSize;
            vm.selectedUserGroupId = parseInt($stateParams.userGroupId);
        }

        function createUserGroup() {
            var node = {id: 'userGroupSelected', value: {userGroupId: 'new', currentGroupRole: vm.currentGroupRole}};
            broadcastGroupSelection(node);
            vm.selectedUserGroupId = 'new';
        }

        function copyUserGroupPrivileges(userGroup) {
            vm.copiedUserGroup = userGroup;
        }

        function pasteUserGroupPrivileges(userGroup) {
            vm.copiedTargetUserGroup = userGroup;
            var isOrganization = false;
            if (vm.currentGroupRole === acmConstants.ORGANIZATIONS_RESOURCE) {
                isOrganization = true;
            }
            userGroupService.pasteUserGroupPrivileges(userGroup, vm.copiedUserGroup, isOrganization)
                .then(function (data) {
                    vm.copiedTargetUserGroup = null;
                }).catch(function () {
                    vm.copiedTargetUserGroup = null;
                });
        }

        function addGroup() {
            if (vm.selectedUserGroupId) {
                vm.userGroups.forEach(function (userGroup, index, groups) {
                    if (userGroup.userGroupId === vm.selectedUserGroupId) {
                        if (!contains(vm.selectedGroupList, userGroup)) {
                            vm.selectedGroupList.push(userGroup);
                        }
                        groups.splice(index, 1);
                    }
                });
            }
            $('button#btnToggleMultiSelect').css('color', 'orange');
            sendGroupsToDetails();
        }

        function addAllGroups() {
            vm.userGroups.forEach(function (userGroup) {
                if (!contains(vm.selectedGroupList, userGroup)) {
                    vm.selectedGroupList.push(userGroup);
                }
            });
            vm.userGroups.length = 0;
            $('button#btnToggleMultiSelect').css('color', 'orange');
            sendGroupsToDetails();
        }

        function removeGroup() {
            if (vm.currentGroupListItem && vm.currentGroupListItem.length > 0) {
                vm.selectedGroupList.forEach(function (userGroup, index, groups) {
                    if (userGroup.userGroupId === vm.currentGroupListItem[0].userGroupId) {
                        if (!contains(vm.userGroups, userGroup)) {
                            vm.userGroups.push(userGroup);
                        }
                        groups.splice(index, 1);
                    }
                });
            }
            if (vm.selectedGroupList.length <= 0) {
                $('button#btnToggleMultiSelect').css('color', 'inherit');
            }
            sendGroupsToDetails();
        }

        function removeAllGroups() {
            vm.selectedGroupList.forEach(function (userGroup) {
                if (!contains(vm.userGroups, userGroup)) {
                    vm.userGroups.push(userGroup);
                }
            });
            vm.selectedGroupList.length = 0;
            $('button#btnToggleMultiSelect').css('color', 'inherit');
            sendGroupsToDetails();
        }

        function contains(groupArray, userGroup) {
            var found = false;
            groupArray.forEach(function (ug) {
                if (ug.userGroupId === userGroup.userGroupId) {
                    found = true;
                }
            });
            return found;
        }

        function sendGroupsToDetails() {

            if (vm.selectedGroupList.length > 0) {

                vm.selectedGroupIDs.length = 0;

                vm.selectedGroupList.forEach(function (userGroup) {
                    vm.selectedGroupIDs.push(userGroup.userGroupId);
                });

                vm.selectedUserGroupId = vm.selectedGroupIDs[0].userGroupId;

                var node = {
                    id: vm.eventName,
                    value: {
                        userGroupId: vm.selectedGroupIDs[0],
                        userGroupIDs: vm.selectedGroupIDs,
                        currentGroupRole: vm.currentGroupRole
                    }
                };

                $rootScope.$broadcast(vm.eventName, node);
            }
        }

        (function () {
            $scope.$on('$destroy', function () {
                refreshUserGroupsOff();
                selectUserGroupOff();
                userGroupSelectedOff();
                setGroupListReadyOff();
            });
        })();
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .directive('userGroupDetails', userGroupDetails);

    userGroupDetails.$inject = [];

    /* @ngInject */
    function userGroupDetails() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/usergroups/userGroupDetails/userGroupDetails.html',
            controller: 'UserGroupDetailsController',
            controllerAs: 'vm'
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .controller('UserGroupDetailsController', UserGroupDetailsController);

    UserGroupDetailsController.$inject = ['$q', '$rootScope', '$scope', 'userService','$stateParams', '$state', 'userGroupService', 'modalService', '$window', 'privilegeService', '$transitions', '$uibModal', 'flatironsAppConfigService','acmConstants'];

    /* @ngInject */
    function UserGroupDetailsController($q, $rootScope, $scope, userService, $stateParams, $state, userGroupService, modalService, $window, privilegeService , $transitions, $uibModal, flatironsAppConfigService,acmConstants) {
        var vm = this;
        $rootScope.userInfoDetails = [];
        retrieveUserDetails();
        $rootScope.userGroupDetails = this;

        vm.retrieveUserGroup = retrieveUserGroup;
        vm.getUserGroupMembers = localGetUserGroupMembers;

        vm.selectUsers = selectUsers;
        vm.selectMgrs = selectMgrs;
        vm.openAddUser = openAddUser;
        vm.removeUsers = removeUsers;
        vm.assignUsersRole = assignUsersRole;
        vm.unassignUsersRole = unassignUsersRole;
        vm.removeFromUsersList = removeFromUsersList;
        vm.openOrganizationsModal = openOrganizationsModal;

        vm.saveUserGroup = save;
        vm.cancel = cancel;
        vm.deleteUserGroup = deleteUserGroup;
        vm.toggleEdit = toggleEdit;

        vm.isEditModeActivated = false;
        vm.isNew = $stateParams.userGroupId === 'new';
        vm.currentGroupRole = $stateParams.currentGroupRole;
        vm.roleManagerActive = false;
        vm.groupManagerActive = false;
        vm.showManagersRow = showManagersRow;

        vm.currentUserGroupId = $stateParams.userGroupId;
        vm.createAnother = false;
        vm.usersDirty = false;
        vm.dataModelProperties = {};
        vm.showMgr = true;

        vm.userGroup = {};
        vm.userGroupMembers = {};
        vm.selectedUsers = [];
        vm.selectedMgrs = [];
        vm.removedUsers = [];
        vm.managers = [];
        vm.members = [];
        vm.addedUsers = [];
        vm.limit = 20;
        vm.currentPage = 1;
        vm.headerIfo=[];
        vm.changeTitlesToCurrentGroupRole = changeTitlesToCurrentGroupRole;

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
            .then(function(data) {
                vm.userPermissions = data;
            });
        flatironsAppConfigService.getAppConfig().then(function(config) {
            if(config.roleManagerActive) {
                vm.roleManagerActive = true;
            }
            if(config.groupManagerActive) {
                vm.groupManagerActive = true;
            }
        });

        setupDataModelProperties();

        $scope.$on('refreshUserGroupMembers', localGetUserGroupMembers);

        changeTitlesToCurrentGroupRole();

        if (!vm.isNew) {
            retrieveUserGroup();
        } else {
            vm.isEditModeActivated = true;
            broadcastUserGroupSelected('new');
        }

        function openOrganizationsModal() {
            $uibModal.open({
                template: '<div style="height:600px"><organization-list modal="this"></organization-list></div>',
                size: 'lg'
            }).result.then(function (organization) {
                vm.currentNcage = vm.userGroup.ncage;
                vm.currentOrgName = vm.userGroup.organizationName;
                if (vm.userGroupMembers.users !== undefined && vm.userGroupMembers.users.length > 0) {
                    modalService.showMemberDeletionConfirmation('Changing the group to a different organization will' +
                        ' remove all existing members from the group. Do you want to continue?')
                        .then(function () {
                            vm.usersList = vm.userGroupMembers.users;
                            for (var i = 0; i < vm.usersList.length;) {
                                removeFromUsersList(vm.usersList[i].userName);
                            }
                        }).catch(function () {
                            vm.userGroup.ncage = vm.currentNcage;
                            vm.userGroup.organizationName = vm.currentOrgName;
                        });
                }
                vm.userGroup.ncage = organization.ncage;
                vm.userGroup.organizationName = organization.name;
            });
        }

        function openAddUser() {
            $uibModal.open({
                size: 'lg',
                templateUrl: '/templates/users/userModal/userModal.html',
                controller: 'UserModalController',
                controllerAs: 'vm',
                resolve: {
                    userGroupNcage : function(){
                        if (vm.currentUserGroupId === 'new' && (vm.userGroup.ncage === '' || vm.userGroup.ncage === undefined)) {
                            vm.userGroup.ncage = vm.userInfo.ncage
                        }
                        return vm.userGroup.ncage;
                    }
                }

            }).result.then(function (result) {

                if (!vm.userGroupMembers.users) {
                    vm.userGroupMembers.users = [];
                }

                var userAlreadyExists = [];
                vm.addedUsers = [];

                result.forEach(function(res){
                    if (checkIfExists(vm.userGroupMembers.users, res.userName)){
                        userAlreadyExists.push(res.userName);
                    } else {
                        res.userRole = 'User';
                        vm.userGroupMembers.users.push(res);
                        vm.addedUsers.push(res.userName);
                    }
                });

                if (userAlreadyExists.length > 0){
                    modalService.showConfirmationModal('The following user(s) are already members of the group, and will not be added.\n'+userAlreadyExists.join('\n'));
                }

                vm.userGroupDetailsForm.$setDirty();
                vm.selectedUsers = [];
            });
        }

        vm.toggleMin = function() {
            vm.minDate = vm.minDate ? null : new Date();
        };
        vm.toggleMin();

        vm.datepicker = {
            opened: false
        };

        vm.toggleDatepicker = function() {
            vm.datepicker.opened = !vm.datepicker.opened;
        };

        function changeTitlesToCurrentGroupRole() {
            $scope.userGroupType = 'Role';
            if (vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE) {
                $scope.userGroupType = 'Group';
            }
           return $scope.userGroupType;
        }

        function setupDataModelProperties() {
            userGroupService.getDataModelProperties().then(function(data) {
                vm.dataModelProperties = data;
            });
        }

        function retrieveUserGroup() {
            if (vm.currentUserGroupId) {
                vm.isNew = false;
                userGroupService.getUserGroup(vm.currentUserGroupId)
                .then(function (data) {
                    vm.userGroup = data;
                    vm.userGroupMembers = {};
                    vm.userGroupDetailsForm.$setPristine();

                    $scope.$broadcast('refreshUserGroupMembers');
                });
            }
        }
        function retrieveUserDetails() {
            userService.getUserDetails()
                .then(function (data) {
                    vm.userInfo = data;
           });
        }
        function localGetUserGroupMembers() {
            var offset = (vm.currentPage - 1) * vm.limit;
            userGroupService.getUserGroupMembers(vm.userGroup.userGroupId, offset, vm.limit).then(function (data) {
                vm.userGroupMembers = data;
                if (!vm.isEditModeActivated) {
                    vm.userGroupDetailsForm.$setPristine();
                }
            });
        }

        function showManagersRow() {
            if ((vm.roleManagerActive && vm.currentGroupRole === acmConstants.USER_ROLES_RESOURCE) || (vm.groupManagerActive && vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE))
            {
                return true;
            }
            return false;
        }

        function save() {
            if (vm.isNew) {
                if (vm.currentGroupRole === acmConstants.USER_ROLES_RESOURCE) {
                    vm.userGroup.type = 'role';
                }

                else if(vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE) {
                    vm.userGroup.type = 'group';
                }
                userGroupService.createUserGroup(vm.userGroup)
                    .then(function (data) {

                        vm.userGroup = data;

                        updateUserGroupMembers().then(function (data) {

                            vm.userGroupDetailsForm.$setPristine();
                            $rootScope.$broadcast('refreshUserGroups');
                            if(vm.createAnother) {
                                vm.userGroup = {};
                                vm.addedUsers.length = 0;
                                vm.removedUsers.length = 0;
                                vm.userGroupMembers.users = [];
                            } else {
                                broadcastUserGroupSelected(data.userGroupId);
                            }
                            $rootScope.$broadcast('updateStatusText', 'User group created.');
                        });
                    });
            } else {

                if (vm.managers.length > 0){
                    userGroupService.addUserGroupMemberRole(vm.userGroup, vm.managers, 'Manager');
                }
                if (vm.members.length > 0){
                    userGroupService.addUserGroupMemberRole(vm.userGroup, vm.members, 'User');
                }
                userGroupService.saveUserGroup(vm.userGroup)
                    .then(function (data) {
                        updateUserGroupMembers();
                        vm.userGroup = data;
                        vm.userGroupDetailsForm.$setPristine();
                        $rootScope.$broadcast('refreshUserGroups');
                        $rootScope.$broadcast('updateStatusText', 'Usergroup saved.');
                        toggleEdit();
                    });
            }
        }

        function updateUserGroupMembers() {

            var deferred = $q.defer();
            var promises = [];

            if ((vm.addedUsers.length > 0) || (vm.removedUsers.length > 0)) {

                if (vm.addedUsers.length > 0) {
                    promises.push(userGroupService.addUserGroupMember(vm.userGroup, vm.addedUsers));
                }

                if (vm.removedUsers.length > 0){
                    promises.push(userGroupService.deleteUserGroupMembers(vm.userGroup, vm.removedUsers));
                }
                vm.addedUsers = [];
                vm.removedUsers = [];
                $q.all(promises).then(function(data) {
                    deferred.resolve(data);
                });

            } else {
                deferred.resolve({});
            }

            return deferred.promise;
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
            vm.usersDirty = false;
        }

        function deleteUserGroup() {
            userGroupService.deleteUserGroup(vm.userGroup)
                .then(function() {
                    var node = {id: 'userGroupDeleted'};
                    $rootScope.$broadcast('userGroupDeleted', node);
                    $rootScope.$broadcast('updateStatusText', 'User group deleted.');
                });
        }

        function cancel() {
            if (vm.userGroupDetailsForm.$dirty) {
                modalService.showConfirmationModal('All changes will be lost.')
                    .then(function(){
                        if (vm.isNew) {
                            vm.userGroup = {};
                            vm.userGroupDetailsForm.$setPristine();
                            broadcastUserGroupSelected(null);
                        } else {
                            retrieveUserGroup();
                        }
                        toggleEdit();
                    });
            } else if (vm.isNew) {
                broadcastUserGroupSelected(null);
            } else {
                toggleEdit();
            }
        }

        function selectUsers() {
            vm.selectedUsers = [];
            $('#userInGroupList option:selected').each(function() {
                var obj = $.parseJSON($( this ).val());
                vm.selectedUsers.push(obj);
            });
        }

        function selectMgrs() {
            vm.selectedMgrs = [];
            $('#mgrInGroupList option:selected').each(function() {
                var obj = $.parseJSON($( this ).val());
                vm.selectedMgrs.push(obj);
            });
        }

        function removeUsers() {
            var selectedUserNames = vm.selectedUsers.map(function (member) {
                return member.userName;
            });
            modalService.showConfirmationModal('Are you sure you want to delete the user(s)?\n'+selectedUserNames.join('\n'))
                .then(function() {
                    vm.removedUsers = [];
                    vm.addedUsers = [];
                    selectedUserNames.forEach(function(userName) {
                        removeFromUsersList(userName);
                    });

                    vm.selectedUsers = [];
                    vm.usersDirty = true;
                });
        }

        function assignUsersRole() {
            var selectedUserNames = vm.selectedUsers.map(function (member) {
                return member.userName;
            });
            modalService.showConfirmationModal('Are you sure you want to upgrade the following user(s) to managers?\n'+selectedUserNames.join('\n'))
                .then(function() {
                    vm.managers = [];
                    selectedUserNames.forEach(function(userName) {
                        processUser(vm.userGroupMembers.users, vm.managers, userName, 'Manager');

                        if(vm.members.indexOf(userName) > -1){
                            vm.members.splice(vm.members.indexOf(userName), 1);
                        }
                    });

                    vm.selectedUsers = [];
                    vm.usersDirty = true;
                    vm.userGroupDetailsForm.$setDirty();
                });
        }

        function unassignUsersRole() {
            var selectedMgrNames = vm.selectedMgrs.map(function (member) {
                return member.userName;
            });
            modalService.showConfirmationModal('Are you sure you want to remove the manager role from the following user(s)?\n'+selectedMgrNames.join('\n'))
                .then(function() {
                    vm.members = [];
                    selectedMgrNames.forEach(function(userName) {
                        processUser(vm.userGroupMembers.users, vm.members, userName, 'User');

                        if(vm.managers.indexOf(userName) > -1){
                            vm.managers.splice(vm.managers.indexOf(userName), 1);
                        }
                    });

                    vm.selectedMgrs = [];
                    vm.usersDirty = true;
                    vm.userGroupDetailsForm.$setDirty();
                });
        }

        function removeFromUsersList(userName) {
            remove(vm.userGroupMembers.users, vm.userGroupDetailsForm, userName);
        }

        function processUser(users, list, userName, role) {
            for (var i = 0; i < users.length; i++) {
                if (users[i].userName === userName) {
                    users[i].userRole = role;
                    list.push(userName);
                    break;
                }
            }
        }

        function broadcastUserGroupSelected(userGroupId) {
            var node =  {id: 'userGroupSelected',
                         value: {userGroupId: userGroupId,
                                 currentGroupRole: vm.currentGroupRole} };

            $rootScope.$broadcast('userGroupSelected', node);
        }

        function remove(users, form, userName) {
            for (var i = 0; i < users.length; i++) {
                if (users[i].userName === userName) {
                    users.splice(i, 1);
                    vm.removedUsers.push(userName);
                    form.$setDirty();
                }
            }
            for (var j = 0; j < vm.addedUsers.length; j++) {
                if (vm.addedUsers[j] === userName) {
                    vm.addedUsers.splice(j, 1);
                }
            }
        }

        function checkIfExists(users, userName) {
            for (var i = 0; i < users.length; i++) {
                if (users[i].userName === userName) {
                    return true;
                }
            }
            return false;
        }

        var userGroupDetailsOff = $rootScope.$on('usergroup-details', function(event, node) {
            vm.isNew = vm.isNew || node.value.userGroupId === 'new';

            if ($rootScope.userGroupDetails && !vm.isNew) {
                vm = $rootScope.userGroupDetails;
            }

            vm.isNew = vm.isNew || node.value.userGroupId === 'new';

            if (vm.isNew) {
                vm.currentUserGroupId = node.value.userGroupId;
                vm.userGroup.ncage = '';
                vm.userGroup.organizationName = '';
                if (vm.userGroupDetailsForm.$dirty) {
                    broadcastUserGroupSelected(node.value.userGroupId);
                } else {

                    vm.isEditModeActivated = true;
                    vm.userGroup.name = '';
                    vm.userGroup.description = '';
                    vm.selectedUsers = [];
                    vm.userGroupMembers = {};
                    vm.userGroupDetailsForm.$setPristine();
                }

            } else {
                vm.currentGroupRole = node.value.currentGroupRole;
                vm.currentUserGroupId = node.value.userGroupId;
                retrieveUserGroup();
            }

            changeTitlesToCurrentGroupRole();

        });

        (function () {
            $window.onbeforeunload = beforeUnload;
            var locationChangeStartOff = $transitions.onStart( {} , beforeStateChange);

            $scope.$on('$destroy', function() {
                locationChangeStartOff();
                userGroupDetailsOff();
                $window.onbeforeunload = null;
                $rootScope.userGroupDetails = null;
            });

            function beforeStateChange(transitions) {
                if (!transitions._aborted && vm.userGroupDetailsForm.$dirty) {
                    transitions.abort();
                    modalService.showConfirmationModal('All changes will be lost.')
                        .then(function() {
                            locationChangeStartOff();
                            $state.go(transitions.to(), transitions.params());
                        }, function() {
                            var userGroupId;
                            if (vm.isNew) {
                                userGroupId = 'new';
                            } else {
                                userGroupId = vm.userGroup.userGroupId;
                            }
                            broadcastUserGroupSelected(userGroupId);
                        });
                }
            }

            function beforeUnload() {
                if (vm.userGroupDetailsForm.$dirty) {
                    return 'All changes will be lost.';
                }
            }
        })();
    }

})();


/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.privileges', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.privileges')
        .controller('GroupPrivilegeModalController', GroupPrivilegeModalController);

    GroupPrivilegeModalController.$inject = ['$uibModalInstance', 'groups', 'permissionType', '$scope'];

    /* @ngInject */
    function GroupPrivilegeModalController($uibModalInstance, groups, permissionType, $scope) {

        var vm = this;
        vm.cancel = cancel;
        vm.ok = ok;
        vm.retrieveGroupsWithPrivilege = retrieveGroupsWithPrivilege;
        vm.limit = 10;
        vm.currentPage = 1;
        vm.groupsWithPrivilege = groups;
        retrieveGroupsWithPrivilege();
        vm.permissionType = permissionType;
        vm.totalSize = vm.groupsWithPrivilege.length;
        vm.uibModalInstance = $uibModalInstance;

        function retrieveGroupsWithPrivilege() {
            var pagedData = vm.groupsWithPrivilege.slice(
                (vm.currentPage - 1) * vm.limit,
                vm.currentPage * vm.limit
            );
            vm.pagedGroupsWithPrivilege = pagedData;
        }

        function cancel() {
            vm.uibModalInstance.dismiss();
        }

        function ok() {
            vm.uibModalInstance.close();
        }

    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.privileges')
        .directive('privilegeDetails', privilegeDetails);

    privilegeDetails.$inject = [];

    /* @ngInject */
    function privilegeDetails() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/privileges/privilegeDetails/privilegeDetails.html',
            controller: 'PrivilegeDetailsController',
            controllerAs: 'vm'
        };
    }
})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.privileges')
            .controller('PrivilegeDetailsController', PrivilegeDetailsController);

    PrivilegeDetailsController.$inject = ['privilegeService', 'userGroupService', '$rootScope', '$q', '$uibModal', '$window', '$scope', '$state', '$stateParams', '$transitions','acmConstants'];

    /* @ngInject */
    function PrivilegeDetailsController(privilegeService, userGroupService, $rootScope, $q, $uibModal, $window, $scope, $state, $stateParams, $transitions,acmConstants) {
        var vm = this;

        $rootScope.privilegeDetails = this;

        vm.cancel = cancel;
        vm.savePrivileges = savePrivileges;
        vm.toggleEdit = toggleEdit;
        vm.showGroupPrivilegeModal = showGroupPrivilegeModal;
        vm.applyToDescendantsToggle = applyToDescendantsToggle;
        vm.permissionsSelect = permissionsSelect;
        vm.permissionsDeselect = permissionsDeselect;
        vm.numberOfGroupsWithRead = '-';
        vm.numberOfGroupsWithWrite = '-';
        vm.numberOfGroupsWithDelete = '-';
        vm.numberOfGroupsWithDefaultRead = '-';
        vm.numberOfGroupsWithDefaultWrite = '-';
        vm.numberOfGroupsWithDefaultDelete = '-';

        vm.isCurrentPermissions = true;
        vm.isSchemeNode = false;
        vm.isEditModeActivated = false;
        vm.saveInProgress = false;
        vm.resetTree = resetTree;

        vm.resourceSearchText = '';
        vm.scheme = '';
        vm.schemes = [];
        vm.selectedPermissionTypes = {};
        vm.selectedDefaultPermissionTypes = {};
        vm.selectedPermissionTypesOriginal = {};
        vm.selectedDefaultPermissionTypesOriginal = {};
        vm.selectPermissionType = selectPermissionType;
        vm.selectDefaultPermissionType = selectDefaultPermissionType;
        vm.permissionTypes = [];
        vm.selectedPermissionDisplayType = '*';
        vm.permissionDisplayTypes = [];
        vm.applyToDescendants = false;

        vm.treeNodes = [];
        vm.selectedNode = null;
        vm.selectedNodes = [];
        vm.selectedUserGroupId = $stateParams.userGroupId;
        vm.selectedUserGroupIDs = $stateParams.userGroupIDs;
        vm.privilegeChanges = [];
        vm.defaultPrivilegeChanges = [];
        vm.getChildNodes = getChildNodes;
        vm.showNotSavedConfirmation = showNotSavedConfirmation;
        vm.hasPermissionTypeChanged = hasPermissionTypeChanged;
        vm.hasDefaultPermissionTypeChanged = hasDefaultPermissionTypeChanged;
        vm.isDirty = isDirty;
        vm.isPermissionsEditable = isPermissionsEditable;
        vm.currentGroupRole = $stateParams.currentGroupRole;

        vm.resourceTreeDelegate = {
                getChildNodes: getChildNodes,
                getOverrideSettings: getOverrideSettings
        };

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
        .then(function(data) {
            vm.userPermissions = data;
        });
        vm.applyPrivilegesPromise = {};

        vm.nodeChanges = [];
        vm.prefixUpdateQueue = [];
        vm.prefixUpdateCallsAvail = 5;
        if ('IntersectionObserver' in window) {
            vm.nodeObserver = new IntersectionObserver(nodeVisible);
        }

        //////////////////////////////////////

        retrieveSchemes();
        retrievePermissionTypes();

        function getOverrideSettings() {
            return { view : { selectedMulti : true, fontCss: getFont, nameIsHTML: true, addDiyDom: observeNode },
                data : { key : { title : 'baseName'} } };
        }

        function getFont(treeId, node) {
            return node.font ? node.font : {};
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
            if (vm.isEditModeActivated) {
                vm.applyToDescendants = false;
            }
        }

        function retrieveSchemes() {
            privilegeService.getSchemes()
                    .then(function (data) {
                        vm.schemes = data;
                    });
        }

        function retrievePermissionTypes() {
            //Get permission types with empty scope.
            var scope = '';
            privilegeService.getPermissionTypes(scope)
                    .then(function (data) {
                        data.permissionTypes.forEach(function(permissionType) {
                            var displayName = {};
                            vm.permissionTypes.push(permissionType.name);
                            displayName.name = 'Show ' + permissionType.name + ' permissions';
                            displayName.value = permissionType.name;
                            vm.permissionDisplayTypes.push(displayName);
                        });
                    });
        }

        function getChildNodes(treeNode) {
            var deferred = $q.defer();

            if (!treeNode) {
                if (vm.scheme) {
                    var schemeObjects = [];
                    schemeObjects.push(privilegeService.createRootNode(vm.scheme));
                    deferred.resolve(schemeObjects);
                } else {
                    deferred.resolve(privilegeService.getSchemes());
                }
            } else {
                if (!vm.resourceSearchText) {
                    var groupType = getSelectedGroupType();
                    var resourceObjects = privilegeService.getChildNodes(treeNode, vm.selectedUserGroupId, vm.selectedPermissionDisplayType, groupType);
                    deferred.resolve(resourceObjects);
                } else {
                    deferred.resolve();
                }
            }

            return deferred.promise;
        }

        function cancel() {
            if (isDirty()) {
                vm.showNotSavedConfirmation()
                .then(function() {
                    vm.toggleEdit();
                    updateNavigationTree(false);
                    resetPrivilegesView();
                    resetPermissionDisplayValues();
                    vm.applyToDescendants = false;
                });
            } else {
                vm.toggleEdit();
                updateNavigationTree(false);
                resetPrivilegesView();
                resetPermissionDisplayValues();
                vm.applyToDescendants = false;
            }
        }

        function isDirty() {
            return vm.privilegeChanges.length > 0 || vm.defaultPrivilegeChanges.length > 0;
        }

        function resetPrivilegesView() {
            vm.privilegeChanges = [];
            vm.defaultPrivilegeChanges = [];
            vm.selectedNode = null;
            vm.selectedNodes = [];
        }

        function resetTree() {
            var groupType = getSelectedGroupType();
            if (vm.resourceSearchText) {
                privilegeService.getAllTreeNodes(vm.resourceSearchText, vm.scheme, groupType)
                    .then(function(data) {
                        vm.treeNodes = data;
                        resetPrefixUpdates();
                        $rootScope.$broadcast('resetTree');
                    });
            } else {
                vm.treeNodes = [];
                resetPrefixUpdates();
                $rootScope.$broadcast('resetTree');
            }

            vm.selectedNode = null;
            vm.selectedNodes = [];
            vm.selectedPermissionTypes = {};
            vm.selectedDefaultPermissionTypes = {};
        }

        function setApplyToDescendantsForPrivilegeChanges() {

            vm.privilegeChanges.forEach(function (privilegeChange) {
                privilegeChange.applyToDescendants = vm.applyToDescendants;
            });
        }

        function savePrivileges() {
            vm.saveInProgress = true;

            setApplyToDescendantsForPrivilegeChanges();

            if (vm.selectedUserGroupIDs.length === 0) {
                vm.selectedUserGroupIDs.push(vm.selectedUserGroupId);
            }

            var userGroupPrivilegeChanges = {
                userGroupPrivilegeChanges: vm.privilegeChanges.concat(vm.defaultPrivilegeChanges)
            };

            privilegeService.savePrivileges(vm.selectedUserGroupIDs, userGroupPrivilegeChanges)
            .then(function() {
                $rootScope.$broadcast('updateStatusText',
                                      'Privileges have been saved successfully.');
                vm.toggleEdit();
                vm.privilegeChanges = [];
                vm.defaultPrivilegeChanges = [];
                updatePrivileges();
                updateGroupsWithPrivileges();
                updateNavigationTree(true);
                vm.nodeChanges = [];
                vm.saveInProgress = false;
                vm.applyToDescendants = false;
            }).catch(function () {
                vm.saveInProgress = false;
            });

        }

        function showGroupPrivilegeModal(permissionType, defaultPermissions) {

            if (!(vm.selectedNode && vm.selectedNode.uri && vm.selectedNode.uri.length > 0)) {
                return;
            }

            var groups = [];

            switch(permissionType) {
                case 'Read':
                            if (defaultPermissions === false) {
                                groups = vm.groupsWithRead;
                            } else {
                                groups = vm.groupsWithDefaultRead;
                            }
                            break;
                case 'Write':
                            if (defaultPermissions === false) {
                                groups = vm.groupsWithWrite;
                            } else {
                                groups = vm.groupsWithDefaultWrite;
                            }
                            break;
                case 'Delete':
                            if (defaultPermissions === false) {
                                groups = vm.groupsWithDelete;
                            } else {
                                groups = vm.groupsWithDefaultDelete;
                            }
                            break;
                default:
            }

            $uibModal.open({
                size: 'md',
                templateUrl: '/templates/privileges/privilegeModal/groupPrivilegeModal.html',
                controller: 'GroupPrivilegeModalController',
                controllerAs: 'vm',
                resolve: {
                    groups: function () {
                        return groups;
                    },
                    permissionType: function () {
                        return permissionType;
                    }
                }

            });
        }

        function showNotSavedConfirmation() {
            return $uibModal.open({
                templateUrl: '/templates/core/modal/simpleModal.html',
                controller: 'SimpleModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: 'All changes will be lost.'
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function legalNodeSelected() {
            var legal = false;
            if (vm.selectedNode && !isSelectedNodeSchemeNode()) {
                legal = true;
            }

            return legal;
        }

        function isSelectedNodeSchemeNode() {
            vm.isSchemeNode = false;
            vm.schemes.forEach(function(scheme) {
                if (vm.selectedNode.uri === scheme.uri) {
                    vm.isSchemeNode = true;
                }
            });

            return vm.isSchemeNode;
        }

        function selectPermissionType(permissionTypeName) {
            var newValue = vm.selectedPermissionTypes[permissionTypeName];
            var operation = newValue ? 'add' : 'remove';

            vm.selectedNodes.forEach(function(selectedNode) {
                var privilegeChange = {
                    'userGroupPrivilege': {
                        'uri': selectedNode.uri,
                        'permissionType': [permissionTypeName],
                        'defaultForDescendants': false

                    },
                    'operation': operation,
                    'applyToDescendants': vm.applyToDescendants
                };
                vm.privilegeChanges.push(privilegeChange);
                var nodeChange = {
                    node: selectedNode,
                    applyToDescendants: vm.applyToDescendants
                };
                if (!vm.nodeChanges.includes(nodeChange)) {
                    vm.nodeChanges.push(nodeChange);
                }
                updateNodePrefix(selectedNode, vm.applyToDescendants, false);
            });

            var alreadyIncluded = isPrivilegeAlreadyIncluded(permissionTypeName);

            if (newValue && vm.applyToDescendants && !alreadyIncluded) {
              $('#permissionTypeCheckbox'.concat(permissionTypeName)).prop('indeterminate', true);
            } else {
              $('#permissionTypeCheckbox'.concat(permissionTypeName)).prop('indeterminate', false);
            }
        }

        function selectDefaultPermissionType(permissionTypeName) {
            var newValue = vm.selectedDefaultPermissionTypes[permissionTypeName];
            var operation = newValue ? 'add' : 'remove';

            vm.selectedNodes.forEach(function(selectedNode) {
                var privilegeChange = {
                    'userGroupPrivilege': {
                        'uri': selectedNode.uri,
                        'permissionType': [permissionTypeName],
                        'defaultForDescendants': true

                    },
                    'operation': operation,
                    'applyToDescendants': false
                };
                vm.defaultPrivilegeChanges.push(privilegeChange);
            });
        }

        function isPrivilegeAlreadyIncluded(permissionTypeName) {

            var includes = false;

            vm.privilegeChanges.forEach(function (privilegeChange) {
                if (privilegeChange.userGroupPrivilege.permissionType[0] === permissionTypeName) {
                    includes = true;
                }
            });

            return includes;
        }

        function applyToDescendantsToggle() {

            vm.permissionTypes.forEach(function (permissionType) {
                 if (vm.selectedPermissionTypes[permissionType] === true) {
                     $('#permissionTypeCheckbox'.concat(permissionType)).prop('indeterminate', vm.applyToDescendants);
                 }
            });
        }

        function permissionsSelect(toggleState) {
           if (toggleState === 'current') {
              vm.isCurrentPermissions = true;
              $('#defaultPermissions').hide();
              $('#currentPermissions').show();
           } else {
              vm.isCurrentPermissions = false;
              $('#currentPermissions').hide();
              $('#defaultPermissions').show();
           }
        }

        function permissionsDeselect(toggleState) {
           vm.isCurrentPermissions = toggleState !== 'current';
        }

        function resetPermissionDisplayValues() {
            vm.permissionTypes.forEach(function (permissionType) {
                $('#permissionTypeCheckbox'.concat(permissionType)).prop('indeterminate', false);
            });
        }

        var privilegeDetailsOff = $rootScope.$on('privilege-details', function(event, node) {
            if ($rootScope.privilegeDetails) {
                vm = $rootScope.privilegeDetails;
            }
            vm.selectedUserGroupId = node.value.userGroupId;
            vm.selectedUserGroupIDs = node.value.userGroupIDs;
            if ((vm.currentGroupRole !== node.value.currentGroupRole) || (vm.selectedPermissionDisplayType !== '*')) {
                resetTree();
            }
            vm.currentGroupRole = node.value.currentGroupRole;
            updatePrivileges();
            updateGroupsWithPrivileges();
            updateNodePrefix(null, true, true);
        });

        var navigationTreeNodeSelectedOff = $rootScope.$on('navigationTreeNodeSelected', function(event, treeNode) {
                vm.selectedNode = treeNode;
                vm.selectedNodes.push(treeNode);
                updatePrivileges();
                updateGroupsWithPrivileges();
        });

        var navigationTreeNodeUnSelectedOff = $rootScope.$on('navigationTreeNodeUnSelected', function() {
                vm.selectedNode = null;
                vm.selectedNodes = [];
                vm.selectedPermissionTypes = {};
                vm.selectedDefaultPermissionTypes = {};
        });

        function isPermissionsEditable() {
            return vm.isEditModeActivated && vm.selectedUserGroupId && legalNodeSelected();
        }

        function updatePrivileges() {
            resetPermissionDisplayValues();
            if (vm.selectedNode && vm.selectedNode.uri) {
                vm.applyPrivilegesPromise = privilegeService.getPrivileges(vm.selectedUserGroupId, vm.selectedNode.uri)
                .then(function (data) {

                    vm.selectedPermissionTypes = {};

                    data.userGroupPrivileges.forEach(function (privilege) {
                        var defaultForDescendants = privilege.defaultForDescendants;
                        privilege.permissionType.forEach(function (permissionTypeName) {
                            if (defaultForDescendants === true) {
                                vm.selectedDefaultPermissionTypes[permissionTypeName] = true;
                            } else {
                                vm.selectedPermissionTypes[permissionTypeName] = true;
                            }
                        });
                    });

                    vm.selectedPermissionTypesOriginal = $.extend({}, vm.selectedPermissionTypes);
                    vm.selectedDefaultPermissionTypesOriginal = $.extend({}, vm.selectedDefaultPermissionTypes);

                    vm.privilegeChanges.forEach(function (privilegeChange) {
                        if (isChangeApplicableToSelectedNode(privilegeChange)) {
                            var permissionTypeName = privilegeChange.userGroupPrivilege.permissionType[0];
                            if(privilegeChange.operation === 'add') {
                                vm.selectedPermissionTypes[permissionTypeName] = true;
                            } else if(privilegeChange.operation === 'remove') {
                                vm.selectedPermissionTypes[permissionTypeName] = false;
                            }
                        }
                    });

                    applyToDescendantsToggle();

                    vm.defaultPrivilegeChanges.forEach(function (defaultPrivilegeChange) {
                        if (isChangeApplicableToSelectedNode(defaultPrivilegeChange)) {
                            var permissionTypeName = defaultPrivilegeChange.userGroupPrivilege.permissionType[0];
                            if(defaultPrivilegeChange.operation === 'add') {
                                vm.selectedDefaultPermissionTypes[permissionTypeName] = true;
                            } else if(defaultPrivilegeChange.operation === 'remove') {
                                vm.selectedDefaultPermissionTypes[permissionTypeName] = false;
                            }
                        }
                    });
                });
            }
        }

        function updateGroupsWithPrivileges() {
            if (vm.selectedNode && vm.selectedNode.uri) {
                var groupType = getSelectedGroupType();
                privilegeService.getGroupsWithPrivileges(vm.selectedNode.uri, vm.permissionTypes, groupType, false)
                .then(function (data) {
                    setModalProperties(data);
                });

                privilegeService.getGroupsWithPrivileges(vm.selectedNode.uri, vm.permissionTypes, groupType, true)
                .then(function (data) {
                    setModalDefaultProperties(data);
                });
            }
        }

        function getSelectedGroupType(){
            var groupType = '' ;
            if(vm.currentGroupRole === acmConstants.USER_ROLES_RESOURCE) {
                groupType = 'role';
            }
            else if(vm.currentGroupRole === acmConstants.USER_GROUPS_RESOURCE) {
                groupType = 'group';
            }
            else if (vm.currentGroupRole === acmConstants.ORGANIZATIONS_RESOURCE) {
                groupType = 'organization';
            }
            return groupType;
        }

        function setModalProperties(data) {

            vm.permissionTypes.forEach(function (permissionType, index) {

                addGroupDetails(data[index].userGroups);

                switch(permissionType) {
                    case 'Read':
                        vm.numberOfGroupsWithRead = data[index].userGroups.length;
                        vm.groupsWithRead = data[index].userGroups;
                        break;
                    case 'Write':
                        vm.numberOfGroupsWithWrite = data[index].userGroups.length;
                        vm.groupsWithWrite = data[index].userGroups;
                        break;
                    case 'Delete':
                        vm.numberOfGroupsWithDelete = data[index].userGroups.length;
                        vm.groupsWithDelete = data[index].userGroups;
                        break;
                    default:
                }
            });
        }

        function setModalDefaultProperties(data) {

            vm.permissionTypes.forEach(function (permissionType, index) {

                addGroupDetails(data[index].userGroups);

                switch(permissionType) {
                    case 'Read':
                        vm.numberOfGroupsWithDefaultRead = data[index].userGroups.length;
                        vm.groupsWithDefaultRead = data[index].userGroups;
                        break;
                    case 'Write':
                        vm.numberOfGroupsWithDefaultWrite = data[index].userGroups.length;
                        vm.groupsWithDefaultWrite = data[index].userGroups;
                        break;
                    case 'Delete':
                        vm.numberOfGroupsWithDefaultDelete = data[index].userGroups.length;
                        vm.groupsWithDefaultDelete = data[index].userGroups;
                        break;
                    default:
                }
            });
        }

        function addGroupDetails(userGroups) {

            userGroups.forEach(function (userGroup, index, groups) {
                retrieveUserGroup(userGroup.userGroupId, index, groups);
            });
        }

        function retrieveUserGroup(userGroupId, index, groups) {

            var DELIMITER = ' | ';
            var ELLIPSIS = '...';
            var VISIBLE_CHARS = 100;
            var AVAILABLE_CHARS = 95;

            userGroupService.getUserGroup(userGroupId)
                .then(function (data) {
                    groups[index].displayName = data.name;
                    if (data.description && data.description.length > 0) {
                        var displayName = data.name + DELIMITER + data.description;
                        if (displayName.length > VISIBLE_CHARS) {
                            displayName = displayName.substring(0, AVAILABLE_CHARS) + ELLIPSIS;
                        }
                        groups[index].displayName = displayName;
                    }
                });
        }

        function hasPermissionTypeChanged(permissionTypeName) {
            var originalValue = !!vm.selectedPermissionTypesOriginal[permissionTypeName];
            var changed = false;
            if (vm.selectedNode) {
                vm.privilegeChanges.forEach(function (privilegeChange) {
                    var changedPermissionTypeName = privilegeChange.userGroupPrivilege.permissionType[0];
                    if (isChangeApplicableToSelectedNode(privilegeChange) && changedPermissionTypeName === permissionTypeName) {
                        var newValue = privilegeChange.operation === 'add';
                        changed = originalValue !== newValue;
                    }
                });
            }
            return changed;
        }

        function hasDefaultPermissionTypeChanged(permissionTypeName) {
            var originalValue = !!vm.selectedDefaultPermissionTypesOriginal[permissionTypeName];
            var changed = false;
            if (vm.selectedNode) {
                vm.defaultPrivilegeChanges.forEach(function (defaultPrivilegeChange) {
                    var changedPermissionTypeName = defaultPrivilegeChange.userGroupPrivilege.permissionType[0];
                    if (changedPermissionTypeName === permissionTypeName) {
                        var newValue = defaultPrivilegeChange.operation === 'add';
                        changed = originalValue !== newValue;
                    }
                });
            }
            return changed;
        }

        function isChangeApplicableToSelectedNode(privilegeChange) {
            var selectedNodeUri = vm.selectedNode.uri;
            var privilegeChangeUri = privilegeChange.userGroupPrivilege.uri;
            var isApplicable;
            if(privilegeChange.applyToDescendants) {
                isApplicable = selectedNodeUri.lastIndexOf(privilegeChangeUri) === 0;
            } else {
                isApplicable = selectedNodeUri === privilegeChangeUri;
            }
            return isApplicable;
        }

        function broadcastUserGroupSelected(userGroupId, userGroupIDs) {
            var node =  {id: 'selectUserGroup',
                         value: { userGroupId: userGroupId,
                                  userGroupIDs: userGroupIDs,
                                  currentGroupRole: vm.currentGroupRole}};

            $rootScope.$broadcast('selectUserGroup', node);
        }

        var resourcesUserGroupSelectedOff = $rootScope.$on('resourcesUserGroupSelected', function (event, node) {
            if( (node.value.userGroupId !== vm.selectedUserGroupId) ||
                (vm.selectedUserGroupIDs.length > 1) ) {
                if(isDirty()) {
                    vm.showNotSavedConfirmation().
                        then(function() {
                            resetPrivilegesView();
                            vm.selectedUserGroupId = node.value.userGroupId;
                            vm.selectedUserGroupIDs = node.value.userGroupIDs;
                            broadcastUserGroupSelected(vm.selectedUserGroupId, vm.selectedUserGroupIDs);
                    });
                } else {
                    resetPrivilegesView();
                    vm.selectedUserGroupId = node.value.userGroupId;
                    vm.selectedUserGroupIDs = node.value.userGroupIDs;
                    broadcastUserGroupSelected(vm.selectedUserGroupId, vm.selectedUserGroupIDs);
                }
            }
        });


        $scope.$on('groupRolesChanged', function () {
            if( vm.isEditModeActivated ) {
                vm.toggleEdit();
            }
            permissionsSelect('current');
            resetPrivilegesView();
            resetPermissionDisplayValues();
            vm.applyToDescendants = false;
            vm.numberOfGroupsWithRead = '-';
            vm.numberOfGroupsWithWrite = '-';
            vm.numberOfGroupsWithDelete = '-';
            vm.numberOfGroupsWithDefaultRead = '-';
            vm.numberOfGroupsWithDefaultWrite = '-';
            vm.numberOfGroupsWithDefaultDelete = '-';
        });

        (function () {
            $window.onbeforeunload = beforeUnload;
            var stateChangeStartOff = $transitions.onStart( {} , beforeStateChange);

            $scope.$on('$destroy', function() {
                stateChangeStartOff();
                navigationTreeNodeSelectedOff();
                navigationTreeNodeUnSelectedOff();
                resourcesUserGroupSelectedOff();
                privilegeDetailsOff();
                $window.onbeforeunload = null;
                $rootScope.privilegeDetails = null;
            });

            broadcastUserGroupSelected(vm.selectedUserGroupId, vm.selectedUserGroupIDs);
            function beforeStateChange(transitions) {

                if (!transitions._aborted && isDirty()) {
                    transitions.abort();
                    vm.showNotSavedConfirmation().then(function() {
                        stateChangeStartOff();
                        $state.go(transitions.to(), transitions.params());
                    });
                }
            }

            function beforeUnload() {
                if (vm.organizationDetailsForm.$dirty) {
                    return 'All changes will be lost.';
                }
            }
        })();

        function resetPrefixUpdates() {
            if (vm.nodeObserver) {
                vm.nodeObserver.disconnect();
            }
            vm.prefixUpdateQueue = [];
        }

        function nodeVisible(entries) {
            entries.filter(function(entry) {
                return entry.isIntersecting;
            }).forEach(function(entry) {
                processPrefixUpdateQueue(getNodeFromElement(entry.target));
            });
        }

        function getNodeElement(treeNode) {
            return $('#' + treeNode.tId + '_a')[0];
        }

        function getNodeFromElement(element) {
            var zTree = $.fn.zTree.getZTreeObj($scope.treeId);
            var id = $(element).closest('li').attr('id');
            return zTree.getNodeByTId(id);
        }

        function observeNode(treeId, node) {
            $scope.treeId = treeId;
            if (!node.isRoot) {
                var nodeElement = getNodeElement(node);
                if (vm.nodeObserver) {
                    vm.nodeObserver.observe(nodeElement);
                } else {
                    processPrefixUpdateQueue(node);
                }
            }
        }

        function updateNodePrefix(node, recurse, reloadPrivileges) {
            var zTree = $.fn.zTree.getZTreeObj($scope.treeId);

            if (node === null) {
                resetPrefixUpdates();
            } else {
                if (reloadPrivileges) {
                    node.basePrefix = null;
                }
                observeNode($scope.treeId, node);
            }

            var childNodes = node === null ? zTree.getNodes() : node.children;
            if (recurse && childNodes) {
                childNodes.forEach(function(child) {
                    updateNodePrefix(child, true, reloadPrivileges);
                });
            }
        }

        function processPrefixUpdateQueue(node) {
            $rootScope.$broadcast('updateLoadingStatus', true, node);
            var nodeElement = getNodeElement(node);
            if (isElementInViewport(nodeElement)) {
                if (vm.prefixUpdateCallsAvail > 0) {
                    vm.prefixUpdateCallsAvail--;
                    getNodePrefix(node).then(function(prefix) {
                        if (typeof node.baseName === 'undefined') {
                            node.baseName = node.name;
                        }
                        node.name = prefix + node.baseName;
                    }).finally(function() {
                        vm.prefixUpdateCallsAvail++;
                        $rootScope.$broadcast('updateLoadingStatus', false, node);
                        if (vm.nodeObserver) {
                            vm.nodeObserver.unobserve(nodeElement);
                        }
                        if (vm.prefixUpdateQueue.length > 0) {
                            processPrefixUpdateQueue(vm.prefixUpdateQueue.shift());
                        }
                    });
                } else {
                    if (!vm.prefixUpdateQueue.includes(node)) {
                        vm.prefixUpdateQueue.push(node);
                    }
                }
            } else if (vm.prefixUpdateQueue.length > 0) {
                processPrefixUpdateQueue(vm.prefixUpdateQueue.shift());
            }
        }

        function isElementInViewport(el) {
            var rect = el.getBoundingClientRect();
            return rect.top >= 0 && rect.left >= 0 &&
                  rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                  rect.right <= (window.innerWidth || document.documentElement.clientWidth);
        }

        function updateNavigationTree(reloadPrivileges) {
            vm.nodeChanges.forEach(function(changedNode) {
                updateNodePrefix(changedNode.node, changedNode.applyToDescendants, reloadPrivileges);
            });
        }

        function getPrivilegePrefixWithChanges(node) {
            var changedPrefix = '';
            var prefixChanges = vm.privilegeChanges.filter(isNodeChanged).reduce(function(acc, change) {
                var permissionType = change.userGroupPrivilege.permissionType[0];
                var index = vm.permissionTypes.indexOf(permissionType);
                if (index > -1) {
                    acc[index] = change.operation === 'add' ? permissionType.charAt(0) : '-';
                }
                return acc;
                }, Array(vm.permissionTypes.length));

            for (var i = 0; i <= vm.permissionTypes.length; i++) {
                changedPrefix += prefixChanges[i] && prefixChanges[i] !== node.basePrefix.charAt(i) ? '<span style="font-family: monospace; color: red; margin: 0">' + prefixChanges[i] + '</span>' : node.basePrefix.charAt(i);
            }

            return '<span style="font-family: monospace">(' + changedPrefix + ') - </span>';

            function isNodeChanged(privilegeChanges) {
                return privilegeChanges.userGroupPrivilege.uri === node.uri || node.uri.startsWith(privilegeChanges.userGroupPrivilege.uri) && privilegeChanges.applyToDescendants;
            }
        }

        function getNodePrefix(node) {
            if (node.basePrefix) {
                var changedPrefix = getPrivilegePrefixWithChanges(node);
                return $q.when(changedPrefix);
            } else {
                return privilegeService.getPermissionPrefix(vm.selectedUserGroupId, node.uri, vm.permissionTypes).then(function(prefix) {
                    node.basePrefix = prefix;
                    return getPrivilegePrefixWithChanges(node);
                });
            }
        }

    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations', []);
})();

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations')
        .directive('selectLogo', selectLogo);

    selectLogo.$inject = [];

    /* @ngInject */
    function selectLogo() {
        return {
            restrict: 'E',
            scope: {
                editMode: '=',
                logo: '=',
                form: '=',
                height: '@',
                width: '@'
            },
            templateUrl: '/templates/organizations/selectLogo/selectLogo.html',
            controller: 'SelectLogoController',
            controllerAs: 'vm',
            bindToController: true
        };
    }

})();
(function () {
    'use strict';

    angular
            .module('app.widget.acm.organizations')
            .controller('SelectLogoController', SelectLogoController);

    SelectLogoController.$inject = ['$scope', 'ngToast'];

    /* @ngInject */
    function SelectLogoController($scope, ngToast) {
        var vm = this;
        vm.clearLogo = clearLogo;
        vm.addLogo = addLogo;

        function clearLogo() {
            vm.logo = null;
            vm.form.$setDirty();
        }

        function addLogo(flow, flowFile) {
            var fileName = flowFile.file.name;
            var fileExt = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();

            if (['png', 'jpg', 'jpeg'].indexOf(fileExt) === -1) {
                ngToast.create({
                    className: 'danger',
                    content: 'Only PNG and JPEG files are allowed',
                    dismissOnTimeout: false,
                    dismissButton: true,
                    dismissOnClick: false
                });
            } else {
                var fileReader = new FileReader();
                fileReader.onload = function (event) {
                    var base64 = event.target.result;
                    vm.logo = base64;
                    flow.files.pop(); // Leaving the file in ng-flow causes issues
                    vm.form.$setDirty();
                    $scope.$apply();
                };
                fileReader.readAsDataURL(flowFile.file);
            }
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations')
        .directive('organizationList', organizationList);

    organizationList.$inject = [];

    /* @ngInject */
    function organizationList()
    {
        return {
            restrict: 'E',
            scope: {
                modal: '=modal',
                noorg: '=noorg'
            },
            templateUrl: '/templates/organizations/organizationList/organizationList.html',
            controller: 'OrganizationListController',
            controllerAs: 'vm'
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.organizations')
            .controller('OrganizationListController', OrganizationListController);

    OrganizationListController.$inject = ['$rootScope', '$scope', '$stateParams', '$state', 'organizationService', 'privilegeService'];

    /* @ngInject */
    function OrganizationListController($rootScope, $scope, $stateParams, $state, organizationService, privilegeService) {
        var vm = this;
        vm.selectOrganization = selectOrganization;
        vm.createOrganization = createOrganization;
        vm.retrieveOrganizations = retrieveOrganizations;
        vm.setData = setData;
        vm.sort = sort;
        ////////////////////////////////////////////////
        vm.limit = 10;
        vm.totalSize = 0;
        vm.currentPage = 1;

        vm.orderBy = 'name';
        vm.sortAscending = true;
        vm.modal = $scope.modal;
        vm.noorg = $scope.noorg;

        vm.searchText = '';
        vm.prevSearchText = null;
        vm.organizations = [];
        vm.ncageSelectedOrganization = null;

        retrieveOrganizations();

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
        .then(function(data) {
            vm.userPermissions = data;
        });


        var refreshOrganizationsOff = $scope.$on('refreshOrganizations', retrieveOrganizations);
        var organizationSelectedOff = $scope.$on('organizationSelected', organizationSelected);

        function sort(field) {
            if (vm.orderBy === field) {
                vm.sortAscending = !vm.sortAscending;
            }

            vm.orderBy = field;
            retrieveOrganizations();
        }

        function retrieveOrganizations() {
            var isNewSearch = vm.searchText !== vm.prevSearchText;
            if (isNewSearch) {
                vm.currentPage = 1;
            }

            var offset = (vm.currentPage-1) * vm.limit;

            organizationService.getOrganizations(vm.searchText, offset, vm.limit, vm.orderBy, vm.sortAscending)
                .then(function (data) {

                    setData(data);
                    vm.orderBy = data.orderBy;
                    vm.sortAscending = data.sortAscending;

                    if (isNewSearch) {
                        vm.prevSearchText = vm.searchText;
                        $rootScope.$broadcast('updateStatusText', data.totalSize + ' organization(s) found.');
                    }
                });
        }

        function selectOrganization(organization) {
            if (vm.modal) {
                vm.modal.$close(organization);
            } else {
                var node =  {id: 'organizationSelected', value: organization.ncage};
                $rootScope.$broadcast('organizationSelected', node);
            }
        }

        function organizationSelected(event, node) {
            vm.ncageSelectedOrganization = node.value;
        }

        function createOrganization() {
            var node =  {id: 'organizationSelected', value: 'new'};
            $rootScope.$broadcast('organizationSelected', node);
            vm.ncageSelectedOrganization = 'new';
        }

        function setData(data) {
            vm.organizations = data.organizations;
            if (vm.noorg) {
                vm.organizations.unshift({'name' : '( No organization )', 'ncage':''});
            }
            vm.totalSize = data.totalSize;
            vm.ncageSelectedOrganization = $stateParams.ncage;
        }

        (function () {
            $scope.$on('$destroy', function() {
                refreshOrganizationsOff();
                organizationSelectedOff();
            });
        })();
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations')
        .directive('organizationDetails', organizationDetails);

    organizationDetails.$inject = [];

    /* @ngInject */
    function organizationDetails() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/organizations/organizationDetails/organizationDetails.html',
            controller: 'OrganizationDetailsController',
            controllerAs: 'vm'
        };
    }

})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.organizations')
            .controller('OrganizationDetailsController', OrganizationDetailsController);

    OrganizationDetailsController.$inject = ['countryISOCodes', '$rootScope', '$stateParams', '$state', 'organizationService', 'modalService', '$scope', '$window', 'privilegeService'];

    /* @ngInject */
    function OrganizationDetailsController(countryISOCodes, $rootScope, $stateParams, $state, organizationService, modalService, $scope, $window, privilegeService) {
        var vm = this;
        vm.retrieveOrganization = retrieveOrganization;
        vm.saveOrganization = saveOrganization;
        vm.deleteOrganization = deleteOrganization;
        vm.checkNcageLength = checkNcageLength;
        vm.cancel = cancel;
        vm.toggleEdit = toggleEdit;

        vm.organization = {};
        vm.dataModelProperties = {};
        vm.isNew = $stateParams.ncage === 'new';
        vm.organization.canTrackAudits = vm.isNew;
        vm.createAnother = false;
        vm.isEditModeActivated = false;
        vm.countries = countryISOCodes;

        setupDataModelProperties();

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
        .then(function(data) {
            vm.userPermissions = data;
        });

        (function () {
            $window.onbeforeunload = beforeUnload;
            var locationChangeStartOff = $rootScope.$on('$stateChangeStart', beforeStateChange);

            $scope.$on('$destroy', function() {
                locationChangeStartOff();
                $window.onbeforeunload = null;
            });

            function beforeStateChange(event, toState, toParams) {
                if (!event.defaultPrevented && vm.organizationDetailsForm.$dirty) {
                    event.preventDefault();
                    modalService.showConfirmationModal('All changes will be lost.')
                        .then(function() {
                            locationChangeStartOff();
                            $state.go(toState, toParams);
                        }, function() {
                            var ncage;
                            if (vm.isNew) {
                                ncage = 'new';
                            } else {
                                ncage = vm.organization.ncage;
                            }
                            broadcastOrganizationSelected(ncage);
                        });
                }
            }

            function beforeUnload() {
                if (vm.organizationDetailsForm.$dirty) {
                    return 'All changes will be lost.';
                }
            }
        })();

        if (!vm.isNew) {
            retrieveOrganization();
        } else {
            vm.isEditModeActivated = true;
            broadcastOrganizationSelected('new');
        }

        function setupDataModelProperties() {
            organizationService.getDataModelProperties().then(function(data) {
                vm.dataModelProperties = data;
            });
        }

        function retrieveOrganization() {
            if ($stateParams.ncage) {
                vm.isNew = false;
                organizationService.getOrganization($stateParams.ncage)
                    .then(function (data) {
                        vm.organization = data;
                        vm.organizationDetailsForm.$setPristine();
                        broadcastOrganizationSelected(data.ncage);
                    });
            }
        }

        function broadcastOrganizationSelected(ncage) {
            var node =  {id: 'organizationSelected', value: ncage};
            $rootScope.$broadcast('organizationSelected', node);
        }

        function cancel() {
            if (vm.organizationDetailsForm.$dirty) {
                modalService.showConfirmationModal('All changes will be lost.')
                    .then(function(){
                        if (vm.isNew) {
                            vm.organization = {};
                            vm.organizationDetailsForm.$setPristine();
                            $state.go('^');
                            broadcastOrganizationSelected(null);
                        } else {
                            retrieveOrganization();
                        }
                        toggleEdit();
                    });
            } else if (vm.isNew) {
                $state.go('^');
                broadcastOrganizationSelected(null);
            } else {
                toggleEdit();
            }
        }

        function saveOrganization() {
            if (vm.isNew) {
                organizationService.createOrganization(vm.organization)
                    .then(function (data) {
                        vm.organizationDetailsForm.$setPristine();
                        $rootScope.$broadcast('refreshOrganizations');
                        if(vm.createAnother) {
                            vm.organization = {};
                        } else {
                            broadcastOrganizationSelected(data.ncage);
                        }
                        $rootScope.$broadcast('updateStatusText', 'Organization created.');
                    });
            } else {
                organizationService.saveOrganization(vm.organization)
                    .then(function (data) {
                        vm.organization = data;
                        vm.organizationDetailsForm.$setPristine();
                        $rootScope.$broadcast('refreshOrganizations');
                        $rootScope.$broadcast('updateStatusText', 'Organization saved.');
                        toggleEdit();
                    });
            }
        }

        function deleteOrganization() {
            organizationService.deleteOrganization(vm.organization)
                .then(function() {
                    var node = {id: 'organizationDeleted'};
                    $rootScope.$broadcast('organizationDeleted', node);
                    $rootScope.$broadcast('updateStatusText', 'Organization deleted.');
                });
        }

        function checkNcageLength() {
            if (vm.organization.ncage && vm.organization.ncage.length > 5) {
                vm.organization.ncage = vm.organization.ncage.substring(0, 5);
            }
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
        }
    }
})();

/* jshint -W100 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations')
        .constant('countryISOCodes', [{'name': '', 'alpha2code': ''},
                {'name': 'Afghanistan', 'alpha2code': 'AF'},
                {'name': 'Åland Islands', 'alpha2code': 'AX'},
                {'name': 'Albania', 'alpha2code': 'AL'},
                {'name': 'Algeria', 'alpha2code': 'DZ'},
                {'name': 'American Samoa', 'alpha2code': 'AS'},
                {'name': 'Andorra', 'alpha2code': 'AD'},
                {'name': 'Angola', 'alpha2code': 'AO'},
                {'name': 'Anguilla', 'alpha2code': 'AI'},
                {'name': 'Antarctica', 'alpha2code': 'AQ'},
                {'name': 'Antigua and Barbuda', 'alpha2code': 'AG'},
                {'name': 'Argentina', 'alpha2code': 'AR'},
                {'name': 'Armenia', 'alpha2code': 'AM'},
                {'name': 'Aruba', 'alpha2code': 'AW'},
                {'name': 'Australia', 'alpha2code': 'AU'},
                {'name': 'Austria', 'alpha2code': 'AT'},
                {'name': 'Azerbaijan', 'alpha2code': 'AZ'},
                {'name': 'Bahamas', 'alpha2code': 'BS'},
                {'name': 'Bahrain', 'alpha2code': 'BH'},
                {'name': 'Bangladesh', 'alpha2code': 'BD'},
                {'name': 'Barbados', 'alpha2code': 'BB'},
                {'name': 'Belarus', 'alpha2code': 'BY'},
                {'name': 'Belgium', 'alpha2code': 'BE'},
                {'name': 'Belize', 'alpha2code': 'BZ'},
                {'name': 'Benin', 'alpha2code': 'BJ'},
                {'name': 'Bermuda', 'alpha2code': 'BM'},
                {'name': 'Bhutan', 'alpha2code': 'BT'},
                {'name': 'Bolivia (Plurinational State of)', 'alpha2code': 'BO'},
                {'name': 'Bonaire, Sint Eustatius and Saba', 'alpha2code': 'BQ'},
                {'name': 'Bosnia and Herzegovina', 'alpha2code': 'BA'},
                {'name': 'Botswana', 'alpha2code': 'BW'},
                {'name': 'Bouvet Island', 'alpha2code': 'BV'},
                {'name': 'Brazil', 'alpha2code': 'BR'},
                {'name': 'British Indian Ocean Territory', 'alpha2code': 'IO'},
                {'name': 'Brunei Darussalam', 'alpha2code': 'BN'},
                {'name': 'Bulgaria', 'alpha2code': 'BG'},
                {'name': 'Burkina Faso', 'alpha2code': 'BF'},
                {'name': 'Burundi', 'alpha2code': 'BI'},
                {'name': 'Cabo Verde', 'alpha2code': 'CV'},
                {'name': 'Cambodia', 'alpha2code': 'KH'},
                {'name': 'Cameroon', 'alpha2code': 'CM'},
                {'name': 'Canada', 'alpha2code': 'CA'},
                {'name': 'Cayman Islands', 'alpha2code': 'KY'},
                {'name': 'Central African Republic', 'alpha2code': 'CF'},
                {'name': 'Chad', 'alpha2code': 'TD'},
                {'name': 'Chile', 'alpha2code': 'CL'},
                {'name': 'China', 'alpha2code': 'CN'},
                {'name': 'Christmas Island', 'alpha2code': 'CX'},
                {'name': 'Cocos (Keeling) Islands', 'alpha2code': 'CC'},
                {'name': 'Colombia', 'alpha2code': 'CO'},
                {'name': 'Comoros', 'alpha2code': 'KM'},
                {'name': 'Congo', 'alpha2code': 'CG'},
                {'name': 'Congo (Democratic Republic of the)', 'alpha2code': 'CD'},
                {'name': 'Cook Islands', 'alpha2code': 'CK'},
                {'name': 'Costa Rica', 'alpha2code': 'CR'},
                {'name': 'Côte d\'Ivoire', 'alpha2code': 'CI'},
                {'name': 'Croatia', 'alpha2code': 'HR'},
                {'name': 'Cuba', 'alpha2code': 'CU'},
                {'name': 'Curaçao', 'alpha2code': 'CW'},
                {'name': 'Cyprus', 'alpha2code': 'CY'},
                {'name': 'Czech Republic', 'alpha2code': 'CZ'},
                {'name': 'Denmark', 'alpha2code': 'DK'},
                {'name': 'Djibouti', 'alpha2code': 'DJ'},
                {'name': 'Dominica', 'alpha2code': 'DM'},
                {'name': 'Dominican Republic', 'alpha2code': 'DO'},
                {'name': 'Ecuador', 'alpha2code': 'EC'},
                {'name': 'Egypt', 'alpha2code': 'EG'},
                {'name': 'El Salvador', 'alpha2code': 'SV'},
                {'name': 'Equatorial Guinea', 'alpha2code': 'GQ'},
                {'name': 'Eritrea', 'alpha2code': 'ER'},
                {'name': 'Estonia', 'alpha2code': 'EE'},
                {'name': 'Ethiopia', 'alpha2code': 'ET'},
                {'name': 'Falkland Islands (Malvinas)', 'alpha2code': 'FK'},
                {'name': 'Faroe Islands', 'alpha2code': 'FO'},
                {'name': 'Fiji', 'alpha2code': 'FJ'},
                {'name': 'Finland', 'alpha2code': 'FI'},
                {'name': 'France', 'alpha2code': 'FR'},
                {'name': 'French Guiana', 'alpha2code': 'GF'},
                {'name': 'French Polynesia', 'alpha2code': 'PF'},
                {'name': 'French Southern Territories', 'alpha2code': 'TF'},
                {'name': 'Gabon', 'alpha2code': 'GA'},
                {'name': 'Gambia', 'alpha2code': 'GM'},
                {'name': 'Georgia', 'alpha2code': 'GE'},
                {'name': 'Germany', 'alpha2code': 'DE'},
                {'name': 'Ghana', 'alpha2code': 'GH'},
                {'name': 'Gibraltar', 'alpha2code': 'GI'},
                {'name': 'Greece', 'alpha2code': 'GR'},
                {'name': 'Greenland', 'alpha2code': 'GL'},
                {'name': 'Grenada', 'alpha2code': 'GD'},
                {'name': 'Guadeloupe', 'alpha2code': 'GP'},
                {'name': 'Guam', 'alpha2code': 'GU'},
                {'name': 'Guatemala', 'alpha2code': 'GT'},
                {'name': 'Guernsey', 'alpha2code': 'GG'},
                {'name': 'Guinea', 'alpha2code': 'GN'},
                {'name': 'Guinea-Bissau', 'alpha2code': 'GW'},
                {'name': 'Guyana', 'alpha2code': 'GY'},
                {'name': 'Haiti', 'alpha2code': 'HT'},
                {'name': 'Heard Island and McDonald Islands', 'alpha2code': 'HM'},
                {'name': 'Holy See', 'alpha2code': 'VA'},
                {'name': 'Honduras', 'alpha2code': 'HN'},
                {'name': 'Hong Kong', 'alpha2code': 'HK'},
                {'name': 'Hungary', 'alpha2code': 'HU'},
                {'name': 'Iceland', 'alpha2code': 'IS'},
                {'name': 'India', 'alpha2code': 'IN'},
                {'name': 'Indonesia', 'alpha2code': 'ID'},
                {'name': 'Iran (Islamic Republic of)', 'alpha2code': 'IR'},
                {'name': 'Iraq', 'alpha2code': 'IQ'},
                {'name': 'Ireland', 'alpha2code': 'IE'},
                {'name': 'Isle of Man', 'alpha2code': 'IM'},
                {'name': 'Israel', 'alpha2code': 'IL'},
                {'name': 'Italy', 'alpha2code': 'IT'},
                {'name': 'Jamaica', 'alpha2code': 'JM'},
                {'name': 'Japan', 'alpha2code': 'JP'},
                {'name': 'Jersey', 'alpha2code': 'JE'},
                {'name': 'Jordan', 'alpha2code': 'JO'},
                {'name': 'Kazakhstan', 'alpha2code': 'KZ'},
                {'name': 'Kenya', 'alpha2code': 'KE'},
                {'name': 'Kiribati', 'alpha2code': 'KI'},
                {'name': 'Korea (Democratic People\'s Republic of)', 'alpha2code': 'KP'},
                {'name': 'Korea (Republic of)', 'alpha2code': 'KR'},
                {'name': 'Kuwait', 'alpha2code': 'KW'},
                {'name': 'Kyrgyzstan', 'alpha2code': 'KG'},
                {'name': 'Lao People\'s Democratic Republic', 'alpha2code': 'LA'},
                {'name': 'Latvia', 'alpha2code': 'LV'},
                {'name': 'Lebanon', 'alpha2code': 'LB'},
                {'name': 'Lesotho', 'alpha2code': 'LS'},
                {'name': 'Liberia', 'alpha2code': 'LR'},
                {'name': 'Libya', 'alpha2code': 'LY'},
                {'name': 'Liechtenstein', 'alpha2code': 'LI'},
                {'name': 'Lithuania', 'alpha2code': 'LT'},
                {'name': 'Luxembourg', 'alpha2code': 'LU'},
                {'name': 'Macao', 'alpha2code': 'MO'},
                {'name': 'Macedonia (the former Yugoslav Republic of)', 'alpha2code': 'MK'},
                {'name': 'Madagascar', 'alpha2code': 'MG'},
                {'name': 'Malawi', 'alpha2code': 'MW'},
                {'name': 'Malaysia', 'alpha2code': 'MY'},
                {'name': 'Maldives', 'alpha2code': 'MV'},
                {'name': 'Mali', 'alpha2code': 'ML'},
                {'name': 'Malta', 'alpha2code': 'MT'},
                {'name': 'Marshall Islands', 'alpha2code': 'MH'},
                {'name': 'Martinique', 'alpha2code': 'MQ'},
                {'name': 'Mauritania', 'alpha2code': 'MR'},
                {'name': 'Mauritius', 'alpha2code': 'MU'},
                {'name': 'Mayotte', 'alpha2code': 'YT'},
                {'name': 'Mexico', 'alpha2code': 'MX'},
                {'name': 'Micronesia (Federated States of)', 'alpha2code': 'FM'},
                {'name': 'Moldova (Republic of)', 'alpha2code': 'MD'},
                {'name': 'Monaco', 'alpha2code': 'MC'},
                {'name': 'Mongolia', 'alpha2code': 'MN'},
                {'name': 'Montenegro', 'alpha2code': 'ME'},
                {'name': 'Montserrat', 'alpha2code': 'MS'},
                {'name': 'Morocco', 'alpha2code': 'MA'},
                {'name': 'Mozambique', 'alpha2code': 'MZ'},
                {'name': 'Myanmar', 'alpha2code': 'MM'},
                {'name': 'Namibia', 'alpha2code': 'NA'},
                {'name': 'Nauru', 'alpha2code': 'NR'},
                {'name': 'Nepal', 'alpha2code': 'NP'},
                {'name': 'Netherlands', 'alpha2code': 'NL'},
                {'name': 'New Caledonia', 'alpha2code': 'NC'},
                {'name': 'New Zealand', 'alpha2code': 'NZ'},
                {'name': 'Nicaragua', 'alpha2code': 'NI'},
                {'name': 'Niger', 'alpha2code': 'NE'},
                {'name': 'Nigeria', 'alpha2code': 'NG'},
                {'name': 'Niue', 'alpha2code': 'NU'},
                {'name': 'Norfolk Island', 'alpha2code': 'NF'},
                {'name': 'Northern Mariana Islands', 'alpha2code': 'MP'},
                {'name': 'Norway', 'alpha2code': 'NO'},
                {'name': 'Oman', 'alpha2code': 'OM'},
                {'name': 'Pakistan', 'alpha2code': 'PK'},
                {'name': 'Palau', 'alpha2code': 'PW'},
                {'name': 'Palestine, State of', 'alpha2code': 'PS'},
                {'name': 'Panama', 'alpha2code': 'PA'},
                {'name': 'Papua New Guinea', 'alpha2code': 'PG'},
                {'name': 'Paraguay', 'alpha2code': 'PY'},
                {'name': 'Peru', 'alpha2code': 'PE'},
                {'name': 'Philippines', 'alpha2code': 'PH'},
                {'name': 'Pitcairn', 'alpha2code': 'PN'},
                {'name': 'Poland', 'alpha2code': 'PL'},
                {'name': 'Portugal', 'alpha2code': 'PT'},
                {'name': 'Puerto Rico', 'alpha2code': 'PR'},
                {'name': 'Qatar', 'alpha2code': 'QA'},
                {'name': 'Réunion', 'alpha2code': 'RE'},
                {'name': 'Romania', 'alpha2code': 'RO'},
                {'name': 'Russian Federation', 'alpha2code': 'RU'},
                {'name': 'Rwanda', 'alpha2code': 'RW'},
                {'name': 'Saint Barthélemy', 'alpha2code': 'BL'},
                {'name': 'Saint Helena, Ascension and Tristan da Cunha', 'alpha2code': 'SH'},
                {'name': 'Saint Kitts and Nevis', 'alpha2code': 'KN'},
                {'name': 'Saint Lucia', 'alpha2code': 'LC'},
                {'name': 'Saint Martin (French part)', 'alpha2code': 'MF'},
                {'name': 'Saint Pierre and Miquelon', 'alpha2code': 'PM'},
                {'name': 'Saint Vincent and the Grenadines', 'alpha2code': 'VC'},
                {'name': 'Samoa', 'alpha2code': 'WS'},
                {'name': 'San Marino', 'alpha2code': 'SM'},
                {'name': 'Sao Tome and Principe', 'alpha2code': 'ST'},
                {'name': 'Saudi Arabia', 'alpha2code': 'SA'},
                {'name': 'Senegal', 'alpha2code': 'SN'},
                {'name': 'Serbia', 'alpha2code': 'RS'},
                {'name': 'Seychelles', 'alpha2code': 'SC'},
                {'name': 'Sierra Leone', 'alpha2code': 'SL'},
                {'name': 'Singapore', 'alpha2code': 'SG'},
                {'name': 'Sint Maarten (Dutch part)', 'alpha2code': 'SX'},
                {'name': 'Slovakia', 'alpha2code': 'SK'},
                {'name': 'Slovenia', 'alpha2code': 'SI'},
                {'name': 'Solomon Islands', 'alpha2code': 'SB'},
                {'name': 'Somalia', 'alpha2code': 'SO'},
                {'name': 'South Africa', 'alpha2code': 'ZA'},
                {'name': 'South Georgia and the South Sandwich Islands', 'alpha2code': 'GS'},
                {'name': 'South Sudan', 'alpha2code': 'SS'},
                {'name': 'Spain', 'alpha2code': 'ES'},
                {'name': 'Sri Lanka', 'alpha2code': 'LK'},
                {'name': 'Sudan', 'alpha2code': 'SD'},
                {'name': 'Suriname', 'alpha2code': 'SR'},
                {'name': 'Svalbard and Jan Mayen', 'alpha2code': 'SJ'},
                {'name': 'Swaziland', 'alpha2code': 'SZ'},
                {'name': 'Sweden', 'alpha2code': 'SE'},
                {'name': 'Switzerland', 'alpha2code': 'CH'},
                {'name': 'Syrian Arab Republic', 'alpha2code': 'SY'},
                {'name': 'Taiwan, Province of China', 'alpha2code': 'TW'},
                {'name': 'Tajikistan', 'alpha2code': 'TJ'},
                {'name': 'Tanzania, United Republic of', 'alpha2code': 'TZ'},
                {'name': 'Thailand', 'alpha2code': 'TH'},
                {'name': 'Timor-Leste', 'alpha2code': 'TL'},
                {'name': 'Togo', 'alpha2code': 'TG'},
                {'name': 'Tokelau', 'alpha2code': 'TK'},
                {'name': 'Tonga', 'alpha2code': 'TO'},
                {'name': 'Trinidad and Tobago', 'alpha2code': 'TT'},
                {'name': 'Tunisia', 'alpha2code': 'TN'},
                {'name': 'Turkey', 'alpha2code': 'TR'},
                {'name': 'Turkmenistan', 'alpha2code': 'TM'},
                {'name': 'Turks and Caicos Islands', 'alpha2code': 'TC'},
                {'name': 'Tuvalu', 'alpha2code': 'TV'},
                {'name': 'Uganda', 'alpha2code': 'UG'},
                {'name': 'Ukraine', 'alpha2code': 'UA'},
                {'name': 'United Arab Emirates', 'alpha2code': 'AE'},
                {'name': 'United Kingdom of Great Britain and Northern Ireland', 'alpha2code': 'GB'},
                {'name': 'United States Minor Outlying Islands', 'alpha2code': 'UM'},
                {'name': 'United States of America', 'alpha2code': 'US'},
                {'name': 'Uruguay', 'alpha2code': 'UY'},
                {'name': 'Uzbekistan', 'alpha2code': 'UZ'},
                {'name': 'Vanuatu', 'alpha2code': 'VU'},
                {'name': 'Venezuela (Bolivarian Republic of)', 'alpha2code': 'VE'},
                {'name': 'Viet Nam', 'alpha2code': 'VN'},
                {'name': 'Virgin Islands (British)', 'alpha2code': 'VG'},
                {'name': 'Virgin Islands (U.S.)', 'alpha2code': 'VI'},
                {'name': 'Wallis and Futuna', 'alpha2code': 'WF'},
                {'name': 'Western Sahara', 'alpha2code': 'EH'},
                {'name': 'Yemen', 'alpha2code': 'YE'},
                {'name': 'Zambia', 'alpha2code': 'ZM'},
                {'name': 'Zimbabwe', 'alpha2code': 'ZW'}
]);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';
    angular
        .module('app.widget.acm.csv', []);
})();

    /**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.csv')
        .controller('CsvUploadController', CsvUploadController);

    CsvUploadController.$inject = ['$scope' ,'flowFactory', 'urlBuilderService', 'ngToast', '$uibModalInstance'];

    /* @ngInject */
    function CsvUploadController($scope, flowFactory, urlBuilderService, ngToast, $uibModalInstance) {
        var vm = this;
        vm.upload = upload;
        vm.uploadUrl = uploadUrl;
        vm.success = success;
        vm.error = error;
        vm.flowObj = flowFactory.create();
        vm.uploading = false;
        vm.fileName = "";
        vm.uploadFinished = false;
        var validFormats = ['csv'];

        function upload($files, $event, $flow) {
            vm.fileName = $files[0].file.name;
            var fileExt = vm.fileName.substring(vm.fileName.lastIndexOf('.') + 1).toLowerCase();

            if (validFormats.indexOf(fileExt) !== -1) {
                vm.uploading = true;
                urlBuilderService.upload()
                    .then(function(url) {
                        $flow.opts.target = url;
                        $flow.upload();
                    });
            } else {
                createErrorToast('Only CSV files are allowed');
                $flow.cancel();
            }
        }

        function uploadUrl() {
            return urlBuilderService.upload()
                .then(function(url) {
                    return url;
                });
        }

        function success($file, $message) {
            vm.uploading = false;
            var usergroupsJSON = angular.fromJson($message);
            var usergroupsCreated = usergroupsJSON.userGroups.length;
            $uibModalInstance.close();
            ngToast.create({
                className: 'success',
                content: 'Created ' + usergroupsCreated + ' User Group(s) from CSV file',
                timeOut: 5000,
                dismissOnTimeout: true,
                dismissButton: true,
                dismissOnClick: false
            });
        }

        function error($file, $message, $flow) {
            $flow.cancel();
            vm.uploading = false;
            var usergroupsJSON = angular.fromJson($message);
            if (usergroupsJSON && usergroupsJSON.error) {
                createErrorToast(usergroupsJSON.error);
            }
        }

        function createErrorToast(msg) {
            ngToast.create({
                className: 'danger',
                content: msg,
                dismissOnTimeout: false,
                dismissButton: true,
                dismissOnClick: false
            });
        }


    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('samlConfiguration', samlConfiguration);

    samlConfiguration.$inject = [];

    /* @ngInject */
    function samlConfiguration() {
        return {
            restrict: 'E',
            scope: {
                init: '=init'
            },
            templateUrl: '/templates/configuration/samlConfiguration/samlConfiguration.html',
            controller: 'SamlConfigurationController',
            controllerAs: 'vm'
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .controller('SamlConfigurationController', SamlConfigurationController);

    SamlConfigurationController.$inject = ['$rootScope', '$scope', 'samlService', '$uibModal'];

    /* @ngInject */
    function SamlConfigurationController($rootScope, $scope, samlService, $uibModal) {
        var vm = this;
        vm.openCertificateModal = openCertificateModal;
        vm.toggleEdit = toggleEdit;
        vm.cancel = cancel;
        vm.saveSAMLConfiguration = saveSAMLConfiguration;
        vm.retrieveSAMLConfiguration = retrieveSAMLConfiguration;
        vm.deleteCertificates = deleteCertificates;
        vm.selectCertificate = selectCertificate;

        vm.editable = true;
        vm.isEditModeActivated = false;
        vm.certificatesDirty = false;
        vm.samlConfiguration = {};
        vm.selectedCertificates = [];

        vm.userPermissions = $scope.init.permissions;
        vm.samlConfiguration = $scope.init.samlconfig;

        function retrieveSAMLConfiguration() {
            samlService.retrieveSAMLConfiguration()
                .then(function (data) {
                    vm.samlConfiguration = data;
                });
        }

        function openCertificateModal(certificate) {
            $uibModal.open({
                size: 'lg',
                templateUrl: '/templates/certificates/certificateModal/certificateModal.html',
                controller: 'CertificateModalController',
                controllerAs: 'vm',
                resolve: {
                    certificateHolder: function () {
                        return {
                            certificate: certificate,
                            existingCertificates: vm.samlConfiguration.certificates
                        };
                    }
                }
            }).result.then(function (result) {
                if (result.update) {
                    removeFromCertificateList(certificate.description);
                }

                if (!vm.samlConfiguration.certificates) {
                    vm.samlConfiguration.certificates = [];
                }

                vm.samlConfiguration.certificates.push(result.certificate);
                vm.samlConfigurationForm.$setDirty();
                vm.selectedCertificates = [];
            });
        }

        function cancel() {
            if (vm.samlConfigurationForm.$dirty) {
                getResetConfirmation($uibModal).then(function () {
                    retrieveSAMLConfiguration();
                    toggleEdit();
                    vm.samlConfigurationForm.$setPristine();
                });
            } else {
                    toggleEdit();
            }
        }

        function selectCertificate() {
            vm.selectedCertificates = [];
            $('#certificateList option:selected').each(function() {
                var obj = $.parseJSON($( this ).val());
                vm.selectedCertificates.push(obj);
            });
        }

        function deleteCertificates() {
            vm.selectedCertificates.forEach(function(certificate) {
                removeFromCertificateList(certificate.description);
            });

            vm.selectedCertificates = [];
            vm.certificatesDirty = true;
        }

        function removeFromCertificateList(description) {
            remove(vm.samlConfiguration.certificates, vm.samlConfigurationForm, description);
        }

        function saveSAMLConfiguration() {
            samlService.saveSAMLConfiguration(vm.samlConfiguration)
                .then(function (data) {
                    vm.samlConfiguration = data;
                    vm.samlConfigurationForm.$setPristine();
                    $rootScope.$broadcast('updateStatusText', 'SAML configuration saved.');
                    toggleEdit();
                });
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
            vm.certificatesDirty = false;
        }
    }

    function remove(certificates, form, description) {
        for (var i = 0; i < certificates.length; i++) {
            if (certificates[i].description === description) {
                certificates.splice(i, 1);
                form.$setDirty();
            }
        }
    }

    function getResetConfirmation(modal) {
        return modal.open({
            templateUrl: '/templates/core/modal/simpleModal.html',
            controller: 'SimpleModalController',
            controllerAs: 'vm',
            resolve: {
                info: function () {
                    return {
                        message: 'All changes will be lost.'
                    };
                }
            },
            size: 'sm'
        }).result;
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .factory('samlService', SamlServiceFactory);

    SamlServiceFactory.$inject = ['$q', '$http', 'urlBuilderService'];

    /* @ngInject */
    function SamlServiceFactory($q, $http, urlBuilderService) {

        var service = {
            retrieveSAMLConfiguration: retrieveSAMLConfiguration,
            saveSAMLConfiguration: saveSAMLConfiguration
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function retrieveSAMLConfiguration() {
            return urlBuilderService.samlConfiguration().then(function (url) {
                return $http.get(url)
                    .then(function (httpObj) {
                        var data = httpObj.data;

                        return data;
                    })
                    .catch(rejectError);
            });
        }

        function saveSAMLConfiguration(samlConfiguration) {
            return urlBuilderService.samlConfiguration().then(function (url) {
                return $http.put(url, samlConfiguration)
                    .then(function (httpObj) {
                        var data = httpObj.data;
                        return data;
                    })
                    .catch(rejectError);
            });
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .factory('permissionTypesService', PermissionTypesServiceFactory);

    PermissionTypesServiceFactory.$inject = ['$q', '$http', 'urlBuilderService'];

    /* @ngInject */
    function PermissionTypesServiceFactory($q, $http, urlBuilderService) {

        var service = {
                getPermissionTypes: getPermissionTypes,
                savePermissionType: savePermissionType,
                createPermissionType: createPermissionType,
                deletePermissionType: deletePermissionType
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function deletePermissionType(permissionType) {
            return urlBuilderService.permissionType(permissionType).then(function(url) {
                return $http.delete(url)
                .then(function() {
                    return permissionType;
                })
                .catch(rejectError);
            });
        }

        function getPermissionTypes(scope) {
            return urlBuilderService.permissionTypes(scope).then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function savePermissionType(oldName, permissionType) {
            return urlBuilderService.permissionType(oldName).then(function(url) {
                return $http.put(url, permissionType)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function createPermissionType(permissionType) {
            var permissionTypes = {
                permissionTypes: [permissionType]
            };
            return urlBuilderService.permissionTypes().then(function(url) {
                return $http.post(url, permissionTypes)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('permissionTypes', permissionTypes);

    permissionTypes.$inject = [];

    /* @ngInject */
    function permissionTypes() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/configuration/permissiontypes/permissionTypes.html',
            controller: 'PermissionTypesController',
            controllerAs: 'vm'
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.configuration')
            .controller('PermissionTypesController', PermissionTypesController);

    PermissionTypesController.$inject = ['$rootScope', '$state', 'permissionTypesService', '$scope', '$uibModal', '$window', '$timeout','privilegeService', '$transitions'];

    /* @ngInject */
    function PermissionTypesController($rootScope, $state, permissionTypesService, $scope, $uibModal, $window, $timeout, privilegeService, $transitions) {
        var vm = this;
        vm.cancel = cancel;
        vm.savePermissionType = savePermissionType;
        vm.getPermissionTypes = getPermissionTypes;
        vm.selectPermissionType = selectPermissionType;
        vm.permissionTypeSelect = permissionTypeSelect;
        vm.deletePermissionType = deletePermissionType;
        vm.createPermissionType = createPermissionType;
        vm.createNew = createNew;
        vm.isSaveable = isSaveable;
        vm.getDescription = getDescription;

        vm.isEditing = false;
        vm.haveReadAccess = false;

        vm.permissionType = {};
        vm.editorValue = {};
        vm.editorScope = {};
        vm.permissionTypes = {};

        getPermissionTypes();

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
        .then(function(data) {
            vm.userPermissions = data;
        });

        $scope.$on('permissionTypeSelect', permissionTypeSelect);

        (function () {
            $window.onbeforeunload = beforeUnload;
            var locationChangeStartOff = $transitions.onStart( {} , beforeStateChange);

            $scope.$on('$destroy', function() {
                locationChangeStartOff();
                $window.onbeforeunload = null;
            });

            function beforeStateChange(transitions) {
                if (!transitions._aborted && vm.permissionTypesForm.$dirty && (vm.permissionType.name !== vm.editorValue || vm.permissionType.scope !== vm.editorScope)) {
                    transitions.abort();
                    showResetConfirmation('All changes will be lost.').then(function() {
                        locationChangeStartOff();
                        $state.go(transitions.to(), transitions.params());
                    }, function(){
                        var node =  {id: 'permissiontypes'};
                        $rootScope.$broadcast('configurationSelected', node);
                    });
                }
            }

            function beforeUnload() {
                if (vm.permissionTypesForm.$dirty) {
                    return 'All changes will be lost.';
                }
            }
        })();

        function isSaveable() {
            return vm.editorValue && (vm.editorValue !== vm.permissionType.name || vm.editorScope !== vm.permissionType.scope);
        }

        function createNew() {
            vm.isEditing = true;
            vm.permissionTypesForm.$setDirty();
            $timeout(function(){
                $('#permissionTypeInput').focus();
            }, 1);
        }

        function getPermissionTypes() {
            permissionTypesService.getPermissionTypes()
                    .then(function (data) {
                            vm.permissionTypes = data.permissionTypes;
                            vm.isEditing = false;
                            $rootScope.$broadcast('permissionTypeSelected', {});
                            vm.permissionTypesForm.$setPristine();
                            $rootScope.$broadcast('updateStatusText', 'You have ' + vm.permissionTypes.length + ' Permission Types.');
                    });
        }

        function createPermissionType() {
            var permissionType = {
                name: vm.editorValue,
                scope: vm.editorScope
            };
            permissionTypesService.createPermissionType(permissionType)
                .then(function () {
                    vm.permissionTypesForm.$setPristine();
                    getPermissionTypes();
                    $rootScope.$broadcast('updateStatusText', 'Permission Type created.');
                });
        }

        function deletePermissionType() {
            showResetConfirmation(vm.permissionType.name + ' will be deleted.').then(function(){
                permissionTypesService.deletePermissionType(vm.permissionType.name)
                .then(function () {
                    vm.permissionTypesForm.$setPristine();
                    getPermissionTypes();
                    $rootScope.$broadcast('updateStatusText', 'Permission Type deleted.');
                });
            });
        }

        function selectPermissionType() {
            vm.isEditing = true;
            vm.permissionTypesForm.$setDirty();
            $('#permissionTypesList option:selected').each(function () {
                var name = $(this).val();
                vm.permissionTypes.forEach(function (permissionType) {
                    if (permissionType.name === name) {
                        vm.permissionType = permissionType;
                    }
                });
            });

            $rootScope.$broadcast('permissionTypeSelected', vm.permissionType);

            $timeout(function(){
                $('#permissionTypeInput').focus();
            }, 1);
        }

        function permissionTypeSelect(event, node) {
            vm.permissionType = node;
            vm.editorValue = node.name;
            vm.editorScope = node.scope;
        }

        function cancel() {
            if (vm.permissionType.name !== vm.editorValue || vm.permissionType.scope !== vm.editorScope) {
                showResetConfirmation('All changes will be lost.').then(function() {
                    getPermissionTypes();
                });
            } else {
                getPermissionTypes();
            }
        }

        function savePermissionType() {
            if (vm.permissionType.name) {
                if(vm.permissionType.name !== vm.editorValue) {
                    showResetConfirmation('\"' + vm.permissionType.name + '\" will be renamed to \"' + vm.editorValue + '\". This will affect all resources with this permission type.' ).then(function(){
                        saveAndRenamePermissionType();
                    });
                } else {
                    saveAndRenamePermissionType();
                }
            } else {
                createPermissionType();
            }
        }

        function saveAndRenamePermissionType() {
            var permissionType = angular.copy(vm.permissionType);
            permissionType.name = vm.editorValue;
            permissionType.scope = vm.editorScope;
            permissionTypesService.savePermissionType(vm.permissionType.name, permissionType)
                .then(function() {
                    getPermissionTypes();
                    $rootScope.$broadcast('updateStatusText', 'Permission Type Saved');
                });
        }

        function showResetConfirmation(messageText) {
            return $uibModal.open({
                templateUrl: '/templates/core/modal/simpleModal.html',
                controller: 'SimpleModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: messageText
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function getDescription(permissionType) {
            var decription = permissionType.name;
            if(permissionType.scope) {
                decription += ' (' + permissionType.scope + ')';
            }
            return decription;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('ldapConfiguration', ldapConfiguration);

    ldapConfiguration.$inject = [];

    /* @ngInject */
    function ldapConfiguration() {
        return {
            restrict: 'E',
            scope: {
                init: '=init'
            },
            templateUrl: '/templates/configuration/ldapConfiguration/ldapConfiguration.html',
            controller: 'LdapConfigurationController',
            controllerAs: 'vm'
        };
    }

})();

    /**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.configuration')
            .controller('LdapConfigurationController', LdapConfigurationController);

    LdapConfigurationController.$inject = ['$rootScope', '$scope', 'ldapService', '$uibModal'];

    /* @ngInject */
    function LdapConfigurationController($rootScope, $scope, ldapService, $uibModal) {
        var vm = this;
        vm.openOrganizationsModal = openOrganizationsModal;
        vm.toggleEdit = toggleEdit;
        vm.cancel = cancel;
        vm.saveLDAPConfiguration = saveLDAPConfiguration;
        vm.synchronize = synchronize;
        vm.authProviderIsLDAP = authProviderIsLDAP;

        vm.editable = true;
        vm.isEditModeActivated = false;
        vm.ldapConfiguration = $scope.init.ldapconfig;
        vm.startDate = null;
        vm.authProvider = $scope.init.authprovider;
        vm.userPermissions = $scope.init.permissions;
        vm.syncBtnTitle = getSyncBtnTitle();

        init();

        function init() {
            if (vm.ldapConfiguration) {
                vm.startDate = convertDateToDateTimeObject(vm.ldapConfiguration.startDate);
            }
        }

        vm.toggleMin = function() {
            vm.minDate = vm.minDate ? null : new Date();
        };
        vm.toggleMin();

        vm.datepicker = {
            opened: false
        };

        vm.toggleDatepicker = function() {
            vm.datepicker.opened = !vm.datepicker.opened;
        };

        function authProviderIsLDAP() {
            return vm.authProvider === 'LDAP';
        }

        function getSyncBtnTitle() {
            var title = 'Synchronize';
            if (!authProviderIsLDAP()) {
                title = 'Synchronize is disabled because LDAP is not selected as the current authentication provider';
            } else if (!vm.userPermissions.Write) {
                title = 'No write privilege on LDAP configuration';
            }
            return title;
        }

        function retrieveLDAPConfiguration() {
            ldapService.retrieveLDAPConfiguration()
                .then(function (data) {
                    vm.ldapConfiguration = data;
                    init();
                });
        }

        function openOrganizationsModal() {
            $uibModal.open({
                            template: '<div style="height:600px"><organization-list modal="this" noorg="true"></organization-list></div>',
                            size: 'lg'
                        }).result.then(function(organization) {
                    vm.ldapConfiguration.organizationNcage = organization.ncage;
                    vm.ldapConfiguration.organizationName = organization.name;
                    vm.ldapConfigurationForm.$setDirty();
                });
        }

        function cancel() {
            if (vm.ldapConfigurationForm.$dirty) {
                showResetConfirmation($uibModal).then(function(){
                    retrieveLDAPConfiguration();
                    toggleEdit();
                    vm.ldapConfigurationForm.$setPristine();
                });
            } else {
                toggleEdit();
            }
        }

        function saveLDAPConfiguration() {
            vm.ldapConfiguration.startDate = convertToDateString(vm.startDate);
            ldapService.saveLDAPConfiguration(vm.ldapConfiguration)
                    .then(function (data) {
                        vm.ldapConfiguration = data;
                        vm.ldapConfigurationForm.$setPristine();
                        $rootScope.$broadcast('updateStatusText', 'LDAP configuration saved.');
                        toggleEdit();
                    });
        }

        function toggleEdit() {
            vm.isEditModeActivated = !vm.isEditModeActivated;
        }

        function synchronize() {
            $rootScope.$broadcast('updateStatusText', 'Synchronize requested.');
            ldapService.synchronize()
            .then(function (data) {
                vm.ldapConfiguration = data;
            $rootScope.$broadcast('updateStatusText', 'Synchronize completed.');
            })
            .catch(function() {
                $rootScope.$broadcast('updateStatusText', 'Synchronize failed.');
            });
        }
    }

    function convertToDateString(dateTimeObject) {
        var dateString;

        if (dateTimeObject) {
            var month = ('0' + (dateTimeObject.getMonth() + 1)).slice(-2);
            var date = ('0' + dateTimeObject.getDate()).slice(-2);

            dateString = dateTimeObject.getFullYear() + '-' + month + '-' + date;
        }

        return dateString;
    }

    function convertDateToDateTimeObject(dateString) {
        var date = null;

        if (dateString) {
            date = new Date(Date.parse(dateString));
        }

        return date;
    }

    function showResetConfirmation(uibModal) {
        return uibModal.open({
            templateUrl: '/templates/core/modal/simpleModal.html',
            controller: 'SimpleModalController',
            controllerAs: 'vm',
            resolve: {
                info: function () {
                    return {
                        message: 'All changes will be lost.'
                    };
                }
            },
            size: 'sm'
        }).result;
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .factory('ldapService', LdapServiceFactory);

    LdapServiceFactory.$inject = ['$q', '$http', 'urlBuilderService'];

    /* @ngInject */
    function LdapServiceFactory($q, $http, urlBuilderService) {

        var service = {
            retrieveLDAPConfiguration: retrieveLDAPConfiguration,
            saveLDAPConfiguration: saveLDAPConfiguration,
            synchronize: synchronize
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function retrieveLDAPConfiguration() {
            return urlBuilderService.ldapConfiguration().then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;

                    return data;
                })
                .catch(rejectError);
            });
        }

        function saveLDAPConfiguration(ldapConfiguration) {
            return urlBuilderService.ldapConfiguration().then(function(url) {
                return $http.put(url, ldapConfiguration)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function synchronize() {
            return urlBuilderService.ldapConfiguration().then(function(url) {
                return $http.post(url)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

    }

})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */
/*global JSEncrypt */
(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .factory('encryptionService', EncryptionServiceFactory);

    EncryptionServiceFactory.$inject = ['$q', '$http', 'urlBuilderService'];

    /* @ngInject */
    function EncryptionServiceFactory($q, $http, urlBuilderService) {

        var publicKey;
        var service = {
                encryptStringRSA: encryptStringRSA,
                encryptStringJasypt: encryptStringJasypt
        };

        return service;

        ////////////////

        function encryptStringJasypt(password) {
            var deferred = $q.defer();

            encryptStringRSA(password)
                .then(function(encryptedPassword) {
                    return urlBuilderService.authEncryptedJasypt().then(function(authEncryptedJasypt) {
                        $http.post(authEncryptedJasypt, {'data': encryptedPassword})
                        .then(function (httpObj) {
                            deferred.resolve(httpObj.data);
                        });
                    });
                }).catch(rejectError);

            return deferred.promise;
        }

        function encryptStringRSA(string) {
            return urlBuilderService.authEncrypted().then(function(authEncrypted) {
                return $http.get(authEncrypted)
                .then(function (httpObj) {
                    var jsEncrypt = new JSEncrypt();

                    if (!publicKey) {
                        publicKey = httpObj.data.base64;
                    }

                    jsEncrypt.setPublicKey(publicKey);

                    return jsEncrypt.encrypt(string);

                }).catch(rejectError);
            });
        }

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

    }

})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('encryption', encryption);

    encryption.$inject = [];

    /* @ngInject */
    function encryption() {
        return {
            restrict: 'E',
            scope: {},
            templateUrl: '/templates/configuration/encryption/encryption.html',
            controller: 'EncryptionController',
            controllerAs: 'vm'
        };
    }

})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */
/*global Clipboard */
(function () {
    'use strict';

    angular
            .module('app.widget.acm.configuration')
            .controller('EncryptionController', EncryptionController);

    EncryptionController.$inject = ['encryptionService'];

    /* @ngInject */
    function EncryptionController(encryptionService) {
        var vm = this;
        vm.encryptString = encryptString;

        vm.encryptedStringRSA = '';
        vm.encryptedStringJasypt = '';
        vm.inputString = '';
        vm.clipboard = new Clipboard('.copy-to-clipboard');

        function  encryptString() {
            if (vm.inputString) {
                encryptStringRSA();
                encryptStringJasypt();
            }
        }

        function encryptStringRSA() {
            encryptionService.encryptStringRSA(vm.inputString)
                .then(function(encryptedStringRSA) {
                    vm.encryptedStringRSA = wrapStringRSA(encryptedStringRSA);

                });
        }

        function encryptStringJasypt() {
            encryptionService.encryptStringJasypt(vm.inputString)
                .then(function(jasypt) {
                    vm.encryptedStringJasypt = jasypt.encrypted;
                });
        }

        function wrapStringRSA(encryptedStringRSA) {
            var prefix = 'RSA(';
            var suffix = ')';
            return prefix + encryptedStringRSA + suffix;
        }


    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('configurationList', configurationList);

    configurationList.$inject = [];

    /* @ngInject */
    function configurationList()
    {
        return {
            restrict: 'E',
            scope: {
                permissions: '=permissions'
            },
            templateUrl: '/templates/configuration/configurationList/configurationList.html',
            controller: 'ConfigurationListController',
            controllerAs: 'vm'
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .controller('ConfigurationListController', ConfigurationListController);

    ConfigurationListController.$inject = ['$rootScope', '$scope'];

    /* @ngInject */
    function ConfigurationListController($rootScope, $scope) {
        var vm = this;
        vm.selectConfiguration = selectConfiguration;
        vm.configurationSelected = configurationSelected;
        vm.isDisabled = isDisabled;
        vm.selectedConfiguration = null;

        vm.permissionTypePath = 'Configuration/Permission Types';
        vm.authProviderPath = 'Configuration/Authentication Provider';
        vm.ldapConfigPath = 'Configuration/LDAP Configuration';
        vm.samlConfigPath = 'Configuration/SAML Configuration';
        vm.encryptionPath = 'Configuration/Encryption';

        vm.permissions = $scope.permissions;

        $scope.$on('configurationSelected', configurationSelected);

        function isDisabled(configResource) {
            var disabled = true;
            vm.permissions.forEach(function(permission){
                if(permission === configResource) {
                    disabled = false;
                }
            });
            return disabled;
        }

        function selectConfiguration(configuration) {
            var node =  {id: configuration};
            $rootScope.$broadcast('configurationSelected', node);
        }

        function configurationSelected(event, node) {
            vm.selectedConfiguration = node.id;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .directive('authProvConfiguration', authProvConfiguration);

    authProvConfiguration.$inject = [];

    /* @ngInject */
    function authProvConfiguration() {
        return {
            restrict: 'E',
            scope: {
            },
            templateUrl: '/templates/configuration/authenticationProvider/authProvConfiguration.html',
            controller: 'AuthProvConfigurationController',
            controllerAs: 'vm'
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .controller('AuthProvConfigurationController', AuthProvConfigurationController);

    AuthProvConfigurationController.$inject = ['$rootScope', '$state', 'authProvService', 'privilegeService'];

    /* @ngInject */
    function AuthProvConfigurationController($rootScope, $state, authProvService, privilegeService) {
        var vm = this;
        vm.save = save;
        vm.retrieveAuthProvConfiguration = retrieveAuthProvConfiguration;

        vm.authProvider = {};

        retrieveAuthProvConfiguration();

        vm.userPermissions = {};
        privilegeService.getPermissionTypesForResource($state.current.accessResource)
            .then(function (data) {
                vm.userPermissions = data;
            });

        function retrieveAuthProvConfiguration() {
            authProvService.retrieveAuthProvConfiguration()
                .then(function (data) {
                    vm.authProvider = data;
                });
        }

        function save() {
            authProvService.saveAuthProvConfiguration(vm.authProvider)
                .then(function (data) {
                    vm.authProvider = data;
                    vm.authProvConfigurationForm.$setPristine();
                    $rootScope.$broadcast('updateStatusText', 'Authentication Provider Configuration saved.');
                });
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.configuration')
        .factory('authProvService', AuthProvServiceFactory);

    AuthProvServiceFactory.$inject = ['$q', '$http', 'urlBuilderService'];

    /* @ngInject */
    function AuthProvServiceFactory($q, $http, urlBuilderService) {

        var service = {
            retrieveAuthProvConfiguration: retrieveAuthProvConfiguration,
            saveAuthProvConfiguration: saveAuthProvConfiguration
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function retrieveAuthProvConfiguration() {
            return urlBuilderService.authProvConfiguration().then(function (url) {
                return $http.get(url)
                    .then(function (httpObj) {
                        var data = httpObj.data;

                        return data;
                    })
                    .catch(rejectError);
            });
        }

        function saveAuthProvConfiguration(authProvConfiguration) {
            return urlBuilderService.authProvConfiguration().then(function (url) {
                return $http.put(url, authProvConfiguration)
                    .then(function (httpObj) {
                        var data = httpObj.data;
                        return data;
                    })
                    .catch(rejectError);
            });
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .controller('UserProfileInfoController', UserProfileInfoController);

    UserProfileInfoController.$inject = ['$uibModalInstance', 'info'];

    /* @ngInject */
    function UserProfileInfoController($uibModalInstance, info) {
        var vm = this;
        var message = info.message;

        vm.userInfo = message.userInfo;
        vm.userGroups = message.userGroups;
        vm.userRoles = message.userRoles;

        vm.infoDetails = vm.userGroups >= vm.userRoles ?  vm.userGroups : vm.userRoles;

        vm.close = close;


        function close() {
            $uibModalInstance.close();
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .controller('SimpleModalController', SimpleModalController);

    SimpleModalController.$inject = ['$uibModalInstance', 'info'];

    /* @ngInject */
    function SimpleModalController($uibModalInstance, info) {
        /* jshint validthis: true */
        var vm = this;

        vm.message = info.message;

        vm.cancel = cancel;
        vm.ok = ok;

        function cancel() {
            $uibModalInstance.dismiss();
        }

        function ok() {
            $uibModalInstance.close();
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .controller('DeleteModalController', DeleteModalController);

    DeleteModalController.$inject = ['$uibModalInstance', 'info'];

    /* @ngInject */
    function DeleteModalController($uibModalInstance, info) {
        /* jshint validthis: true */
        var vm = this;

        vm.message = info.message;
        vm.objectType = info.objectType;
        vm.objectsToBeDeleted = info.objectsToBeDeleted;

        vm.cancel = cancel;
        vm.submit = submit;

        function cancel() {
            $uibModalInstance.dismiss();
        }

        function submit() {
            $uibModalInstance.close();
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.constants', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.constants')
        .constant('httpCodes', {
            ok: 200,
            noContent: 204,
            badRequest: 400,
            notFound: 404,
            conflict: 409,
            internalServerError: 500
        });
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.certificates', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.certificates')
        .controller('CertificateModalController', CertificateModalController);

    CertificateModalController.$inject = ['$uibModalInstance', 'certificateHolder', 'ngToast'];

    /* @ngInject */
    function CertificateModalController($uibModalInstance, certificateHolder, ngToast) {
        var vm = this;
        vm.isEditMode = false;
        vm.certificate = angular.copy(certificateHolder.certificate);
        vm.existingCertificates = angular.copy(certificateHolder.existingCertificates);


        vm.cancel = cancel;
        vm.saveCertificate = saveCertificate;


        if (vm.certificate) {
            vm.isEditMode = true;
        }

        function cancel() {
            $uibModalInstance.dismiss();
        }

        function saveCertificate() {
            var result = {
                certificate: vm.certificate,
                update: vm.isEditMode
            };

            if (!checkForDuplicate()) {
                $uibModalInstance.close(result);
            } else {
                ngToast.create({
                    className: 'danger',
                    content: 'Duplicate not allowed',
                    timeOut: 3000,
                    dismissOnTimeout: true,
                    dismissButton: true,
                    dismissOnClick: false
                });
            }
        }

        function checkIfDescriptionNotChanged() {
            var isEqual = false;
            if (certificateHolder.certificate && vm.certificate.description === certificateHolder.certificate.description) {
                isEqual = true;
            }
            return isEqual;
        }

        function checkForDuplicate() {
            var found = false;
            if (vm.existingCertificates) {
                vm.existingCertificates.forEach(function (crt) {
                    if (crt.description === vm.certificate.description) {
                        found = true;
                        if (checkIfDescriptionNotChanged()) {
                            found = false;
                        }
                    }
                });
            }
            return found;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.welcome', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.welcome')
        .directive('welcomePage', welcomePage);

    welcomePage.$inject = [];

    /* @ngInject */
    function welcomePage()
    {
        return {
            restrict: 'E',
            scope: {
                appconfig: '=appconfig'
            },
            templateUrl: '/templates/welcome/welcome.html',
            controller: 'WelcomeController',
            controllerAs: 'vm'
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.welcome')
        .controller('WelcomeController', WelcomeController);

    WelcomeController.$inject = ['$scope', 'loginService', 'acmConstants'];

    /* @ngInject */
    function WelcomeController($scope, loginService) {
        var vm = this;
        vm.appconfig = $scope.appconfig;
        loginService.getGuestAccessMode().then(function(guestaccessmode){
            vm.isGuestFeatureEnabled = guestaccessmode.isGuestFeatureEnabled;
            vm.isGuestSwitchAccountsAllowed = guestaccessmode.isGuestSwitchAccountsAllowed;
        });
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.users')
        .factory('userService', UserServiceFactory);

    UserServiceFactory.$inject = ['$q', '$http', 'urlBuilderService', 'modalService'];

    /* @ngInject */
    function UserServiceFactory($q, $http, urlBuilderService, modalService) {

        var service = {
            getUsers: getUsers,
            getUser: getUser,
            deleteUser: deleteUser,
            saveUser: saveUser,
            getAccessKeys: getAccessKeys,
            deleteAccessKey: deleteAccessKey,
            updateAccessKey: updateAccessKey,
            getUserDetails: getUserDetails
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function getUserDetails(){
            return urlBuilderService.userDetails().then(function(url) {
                return $http.get(url)
                    .then(function (httpObj) {
                        return httpObj.data;
                    })
                    .catch(rejectError);
            });
        }

        function getUsers(searchText, offset, limit, orderBy, sortAscending, includeInactive, ncage) {
            if (searchText) {
                searchText = searchText.replace(new RegExp('%','g'), '*');
            }
            return urlBuilderService.searchUsers(searchText || '*', offset, limit, orderBy, sortAscending, includeInactive, ncage).then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;

                    return data;
                })
                .catch(rejectError);
            });
        }

        function getUser(userName) {
            return urlBuilderService.user(userName || '').then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;

                    return data;
                })
                .catch(rejectError);
            });
        }

        function deleteUser(user) {
            return modalService.showDeletionConfirmation(user.userName)
                .then(deleteUserFromServer);

            function deleteUserFromServer() {
                return urlBuilderService.user(user.userName).then(function(url) {
                    return $http.delete(url)
                        .then(function() {
                            return user;
                        })
                        .catch(rejectError);
                });
            }
        }

        function saveUser(user) {
            return urlBuilderService.user(user.userName).then(function(url) {
                return $http.put(url, user)
                .then(function (httpObj) {
                    var data = httpObj.data;

                    return data;
                })
                .catch(rejectError);
            });
        }

        function getAccessKeys(currentUserName) {
            return urlBuilderService.accessKeysUrl().then(function (url) {
                return $http.get(url + '/user/' + currentUserName).then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                    .catch(rejectError);
            });
        }


        function deleteAccessKey(accessKey) {

            if (accessKey.approvedDate) {
                return modalService.showDeletionConfirmation('approved access Key')
                    .then(deleteAccessKeyFromServer);
            } else {
                return deleteAccessKeyFromServer();
            }

            function deleteAccessKeyFromServer() {
                return urlBuilderService.accessKeysUrl().then(function (url) {
                    return $http.delete(url + '/key/' + accessKey.hashKey).then(function (httpObj) {
                        var data = httpObj.data;
                        return data;
                    })
                        .catch(rejectError);
                });
            }
        }

        function updateAccessKey(accessKey) {
            return urlBuilderService.accessKeysUrl().then(function (url) {
                return $http.put(url + '/key/' + accessKey.hashKey, accessKey).then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                    .catch(rejectError);
            });
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.usergroups')
        .factory('userGroupService', UserGroupServiceFactory)
        .factory('dataModelPropertyCache', ['$cacheFactory', function($cacheFactory) {
            return $cacheFactory('dataModelPropertyCache');
        }]);


    UserGroupServiceFactory.$inject = ['$q', '$http', 'urlBuilderService', 'dataModelPropertyCache', 'modalService'];

    /* @ngInject */
    function UserGroupServiceFactory($q, $http, urlBuilderService, dataModelPropertyCache, modalService) {

        var service = {
                getUserGroups: getUserGroups,
                getUserGroup: getUserGroup,
                getUserGroupMembers: getUserGroupMembers,
                getDataModelProperties: getDataModelProperties,
                createUserGroup: createUserGroup,
                deleteUserGroup: deleteUserGroup,
                saveUserGroup: saveUserGroup,
                addUserGroupMember: addUserGroupMember,
                addUserGroupMemberRole: addUserGroupMemberRole,
                deleteUserGroupMembers: deleteUserGroupMembers,
                deleteUserGroupMember: deleteUserGroupMember,
                fetchUsersForUserGroup: fetchUsersForUserGroup,
                pasteUserGroupPrivileges: pasteUserGroupPrivileges
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function pasteUserGroupPrivileges(userGroup, copiedUserGroup, isOrganization) {
            if (copiedUserGroup.userGroupId != null && userGroup.userGroupId != null) {
                var message = 'This will clear all current and default permissions for ' + userGroup.type + ' ' +
                    userGroup.name + ' and copy all current and default permissions from ' + userGroup.type + ' ' +
                    copiedUserGroup.name + ' to ' + userGroup.name + '. Continue?';
                return modalService.showConfirmationModal(message)
                    .then(pasteUserGroupPrivileges);
            } else {
                return '';
            }

            function pasteUserGroupPrivileges() {
                return urlBuilderService.copyUserGroupPrivilegesUrl(userGroup.userGroupId, copiedUserGroup.userGroupId, isOrganization).then(function (url) {
                    return $http.put(url).then(function (httpObj) {
                        return httpObj;
                    })
                        .catch(rejectError);
                });
            }
        }

        function saveUserGroup(userGroup) {
            return urlBuilderService.userGroup(userGroup.userGroupId)
                .then(function(url) {
                    return $http.put(url, userGroup)
                        .then(function (httpObj) {
                            var data = httpObj.data;
                            return data;
                        })
                        .catch(rejectError);
            });
        }
        
        function deleteUserGroupMembers(userGroup, removedUsers) {
            var deferred = $q.defer();
            var promises = [];
            if (removedUsers.length > 0) {
                removedUsers.forEach(function(removedUser) {
                    promises.push(deleteUserGroupMember(userGroup, removedUser));
                });
                $q.all(promises).then(function(data) {
                    deferred.resolve(data);
                });
            }

            return deferred.promise;
        }

        function deleteUserGroupMember(userGroup, removedUser) {
            return urlBuilderService.userGroupMembers(userGroup.userGroupId)
                .then(function(url) {
                    return $http.delete(url + '/' + removedUser.toString())
                        .then(function() {
                            return userGroup;
                        })
                        .catch(rejectError);
            });
        }
        
        function addUserGroupMember(userGroup, addUser) {
            return urlBuilderService.userGroupMembers(userGroup.userGroupId)
                .then(function(url) {
                    return $http.post(url, addUser)
                        .then(function() {
                            return userGroup;
                        })
                        .catch(rejectError);
            });
        }
        
        function addUserGroupMemberRole(userGroup, groupMember, userRole) {
            return urlBuilderService.userGroupRoles(userGroup.userGroupId)
                .then(function(url) {
                    return $http.put(url + userRole, groupMember)
                        .then(function() {
                            return userGroup;
                        })
                        .catch(rejectError);
            });
        }

        function deleteUserGroup(userGroup) {
            return modalService.showDeletionConfirmation(userGroup.name)
                .then(deleteUserGroupFromServer);

            function deleteUserGroupFromServer() {
                return urlBuilderService.userGroup(userGroup.userGroupId).then(function(url) {
                    return $http.delete(url)
                        .then(function() {
                            return userGroup;
                        })
                        .catch(rejectError);
                });
            }
        }

        function createUserGroup(userGroup) {
            return urlBuilderService.usergroups().then(function(url) {
                return $http.post(url, userGroup)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function getUserGroups(searchText, type, offset, limit, orderBy, sortAscending) {
            if (searchText) {
                searchText = searchText.replace(new RegExp('%','g'), '*');
            }
            return urlBuilderService.searchUserGroups(searchText || '*', type, offset, limit, orderBy, sortAscending).then(function(url) {
                return $http.get(url)
                    .then(function (httpObj) {
                        var data = httpObj.data;
                        return data;
                    })
                    .catch(rejectError);
            });
        }

        function getUserGroup(userGroupId) {
            return urlBuilderService.userGroup(userGroupId).then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function getUserGroupMembers(userGroupId, offset, limit) {
            return urlBuilderService.userGroupMembers(userGroupId).then(function(url) {
                var params = '?orderBy=firstName';
                if(offset) {
                    params += '&offset=' + offset;
                }
                if(limit) {
                    params += '&limit=' + limit;
                }
                return $http.get(url + params)
                    .then(function (httpObj) {
                        var data = httpObj.data;
                        return data;
                    })
                    .catch(rejectError);
            });
        }

        function fetchUsersForUserGroup(userGroupId){
            return urlBuilderService.userGroupMembers(userGroupId).then(function(url){
                return $http.get(url).then(function (httpObj){
                    var data = httpObj.data;
                    return data;
                })
                    .catch(rejectError);
            });
        }


        function getDataModelProperties() {
            return urlBuilderService.schema('usergroup').then(function(dataModelPropertiesUrl) {
                var deferred = $q.defer();
                var data = dataModelPropertyCache.get(dataModelPropertiesUrl);

                if (data) {
                    deferred.resolve(data);
                } else {
                    $http.get(dataModelPropertiesUrl)
                    .then(function(httpObj) {
                        dataModelPropertyCache.put(dataModelPropertiesUrl, httpObj.data);
                        deferred.resolve(httpObj.data);
                    })
                    .catch(rejectError);
                }

                return deferred.promise;
            });
        }
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */
/*global KJUR, b64utoutf8 */
(function () {
    'use strict';

    angular
        .module('app.widget.acm', [
            'ui.router',
            'ui.bootstrap',
            'ngClipboard',
            'ngToast',
            'ngMessages',
            'ngAnimate',
            'ngSanitize',
            'ngCookies',
            'flow',
            'app.widget.status',
            'app.core.event',
            'app.widget.navigationTree',
            'app.widget.acm.core',
            'app.widget.acm.organizations',
            'app.widget.acm.certificates',
            'app.widget.acm.csv',
            'app.widget.acm.users',
            'app.widget.acm.usergroups',
            'app.widget.acm.configuration',
            'app.widget.acm.welcome',
            'app.widget.acm.modal',
            'app.widget.flatironsLogout',
            'app.widget.flatironsHeader',
            'app.widget.acm.header',
            'app.widget.flatironsFooter',
            'app.widget.acm.footer',
            'app.widget.acm.privileges',
            'app.widget.login',
            'app.widget.authInterceptor',
            'app.widget.acm.constants',
            'app.widget.acm.urlBuilder',
            'app.widget.flatironsAppConfig',
            'app.widget.flatironsLoadingIndicator',
            'pascalprecht.translate'

        ]).constant('acmConstants', {
            'LDAP_CONFIGURATION_RESOURCE': 'Configuration/LDAP Configuration',
            'ORGANIZATIONS_RESOURCE': 'Organizations',
            'USERS_RESOURCE': 'Users',
            'CONFIGURATION_RESOURCE': 'Configuration',
            'SAML_CONFIGURATION_RESOURCE': 'Configuration/SAML Configuration',
            'PERMISSION_TYPES_RESOURCE': 'Configuration/Permission Types',
            'AUTHENTICATION_PROVIDER_RESOURCE': 'Configuration/Authentication Provider',
            'ENCRYPTION_RESOURCE': 'Configuration/Encryption',
            'PRIVILEGES_RESOURCE': 'Privileges',
            'USER_GROUPS_RESOURCE': 'User Groups',
            'USER_ROLES_RESOURCE': 'User Roles',
            'CAN_SHARE_CONTENT':'Privileges/Can share content with other organizations',
            'GUEST_ACCESS_WITH_SWITCH_ACCOUNTS_DISABLED': 'guestAccess_withSwitchAccountsDisabled',
            'GUEST_ACCESS_WITH_SWITCH_ACCOUNTS_ENABLED': 'guestAccess_withSwitchAccountsEnabled',
            'SYSTEM':'SYS'
        }).config(['ngToastProvider', function(ngToast) {
            ngToast.configure({
                verticalPosition: 'top',
                horizontalPosition: 'center',
                maxNumber: 1
            });
        }]).config(['$translateProvider', function($translateProvider) {
            $translateProvider.useStaticFilesLoader({
                prefix: 'translate/lang_',
                suffix: '.json'
            });
            $translateProvider.registerAvailableLanguageKeys(['en','fr'], {
                'en*': 'en',
                'fr*': 'fr',
                '*'  : 'en'
            });
            $translateProvider.determinePreferredLanguage();
            $translateProvider.fallbackLanguage('en');
            // sanitize strategy should be null to escape html in translations
            $translateProvider.useSanitizeValueStrategy(null);
            $translateProvider.addInterpolation('$translateMessageFormatInterpolation');
        }]).config(['$httpProvider', function($httpProvider) {
            $httpProvider.defaults.cache = false;
            if (!$httpProvider.defaults.headers.get) {
                $httpProvider.defaults.headers.get = {};
            }
            $httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
        }]).config(['$provide', function($provide) {
               $provide.decorator('$exceptionHandler', ["$delegate", "$injector", function($delegate, $injector) {
                   return function(exception, cause) {
                       var exceptionStr = exception.toString().toLowerCase();
                       if (exceptionStr.indexOf('possibly unhandled rejection') !== -1) {
                           // log the unhandled rejection to console but don't pass it to the original exception handler
                           console.error(exception, cause);
                       } else {
                           // call the original exception handler ($exceptionHandler)
                           $delegate(exception, cause);
                       }
                   }
               }])
           }]).run(['$rootScope', 'flatironsAppConfigService', 'redirectService', '$window', '$location',
            function($rootScope, flatironsAppConfigService, redirectService, $window, $location ) {

                $rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState) {
                    var inStateChange = redirectService.getInStateChange();
                    if (!inStateChange && toState.name !== 'login') {
                        redirectService.checkPrivilegesAndRedirect(event, toState, toParams, fromState);

                    } else if(!inStateChange && toState.name === 'login' && !$location.search().logout) {
                        flatironsAppConfigService.getAppConfig()
                            .then(function (config) {
                                $window.location.href = config.acmClient + 'login';
                            });

                    }
                });

            }]);

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    var inStateChange = false;
    var toStateGlobal;
    var toParamsGlobal;
    var setGlobalState = true;

    angular
        .module('app.widget.acm')
        .factory('redirectService', RedirectServiceFactory);

    RedirectServiceFactory.$inject = ['privilegeService', '$state', 'flatironsLogoutService', 'ngToast'];

    /* @ngInject */
    function RedirectServiceFactory(privilegeService, $state, flatironsLogoutService, ngToast) {

        var service = {
            checkPrivilegesAndRedirect: checkPrivilegesAndRedirect,
            getInStateChange: getInStateChange

        };

        return service;

        ////////////////

        function getInStateChange() {
            return inStateChange;
        }

        function checkPrivilegesAndRedirect(event, toState, toParams, fromState) {
            event.preventDefault();
            if (setGlobalState) {
                toStateGlobal = toState;
                toParamsGlobal = toParams;
                setGlobalState = false;
            }

            if (toState.name !== 'app.default') {
                privilegeService.getPermissionTypesForResource(toStateGlobal.accessResource)
                    .then(function(data) {
                        if(data.Read) {
                            stateGo($state, toStateGlobal.name, toParamsGlobal);
                        } else {
                            // If it ends up here, a token must exist. This is to send the user to the default page if redirected to a page without read privileges.
                            if (fromState.name === 'login' || fromState.name === '') {
                                stateGo($state, 'app.default', null);
                            }

                            var errorMessage = 'No privileges to view ' + toStateGlobal.accessResource;
                            ngToast.create({
                                className: 'danger',
                                content: errorMessage,
                                timeOut: 3000,
                                dismissOnTimeout: true,
                                dismissButton: true,
                                dismissOnClick: true
                            });

                            setGlobalState = true;
                        }
                    });

            } else {
                stateGo($state, toStateGlobal.name, toParams);
            }

        }
    }

    function stateGo(stateService, state, params) {
        inStateChange = true;
        stateService.go(state, params);
        inStateChange = false;
        setGlobalState = true;
    }

})();


/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.privileges')
            .factory('privilegeService', PrivilegeService);

    PrivilegeService.$inject = ['$q', '$http', 'urlBuilderService', '$timeout'];

    /* @ngInject */
    function PrivilegeService($q, $http, urlBuilderService, $timeout) {

        var service = {
                getSchemes: getSchemes,
                getChildNodes: getChildNodes,
                getAllTreeNodes: getAllTreeNodes,
                getPermissionTypes: getPermissionTypes,
                createRootNode: createRootNode,
                getGroupsWithPrivileges: getGroupsWithPrivileges,
                getGroupsWithPrivilege: getGroupsWithPrivilege,
                getPrivileges: getPrivileges,
                savePrivileges: savePrivileges,
                savePrivilege: savePrivilege,
                deletePrivilege: deletePrivilege,
                getPrivilegesOnResources: getPrivilegesOnResources,
                getPermissionTypesForResource: getPermissionTypesForResource,
                getPermissionTypesForResources: getPermissionTypesForResources,
                getPermissionPrefix: getPermissionPrefix
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
                return $q.reject(httpErrorObj.status);
        }

        function ascendingCompare(a, b) {
             var nameA = a.baseName.toLowerCase();
            var nameB = b.baseName.toLowerCase();
            var result = 0;
            if (nameA < nameB){
                result = -1;
            } if (nameA > nameB){
                result = 1;
            }
            return result;
        }

        function getSchemes() {
            return urlBuilderService.schemes().then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data.schemes;
                    var schemeObjects = [];

                    for(var i = 0; i < data.length; i++) {
                        var scheme = data[i];

                        schemeObjects.push(createRootNode(scheme));
                    }

                    return schemeObjects.sort(ascendingCompare);
                })
                .catch(rejectError);
            });
        }

        function createRootNode(name) {
            return {
                name: name,
                baseName: name,
                uri: name + '://',
                isParent: true,
                isRoot: true,
                icon: './assets/diy/1_open.png'
            };
        }

        function getChildNodes(node, userGroupId, permissionType, groupType) {
            var deferred = $q.defer();
            var explicitResources = null;

            if(node.children) {
                var resourceObjects = node.children;
                delete node.children;
                $timeout(function(){
                    deferred.resolve(resourceObjects);
                }, 1);
            } else {
                var encodedUri = encodeURIComponent(encodeURIComponent(node.uri));
                urlBuilderService.resourceChildren(encodedUri,userGroupId,permissionType,groupType).then(function(url) {
                    $http.get(url, {cache: false})
                        .then(function (httpObj) {
                            explicitResources = httpObj.data.resources;
                            if (permissionType === '*' || groupType !== 'group') {
                                var resourceObjects = createChildTreeNodes(explicitResources, node, false, null);
                                resourceObjects.sort(ascendingCompare);
                                deferred.resolve(resourceObjects);
                            } else {
                                // Look for nodes that require traverse access
                                urlBuilderService.resourceChildrenWithTraverse(encodedUri,userGroupId,permissionType,groupType).then(function(url) {
                                    $http.get(url, {cache: false})
                                        .then(function (httpObj) {
                                            var resources = httpObj.data.resources;
                                            var resourceObjects = createChildTreeNodes(resources, node, false, explicitResources);
                                            resourceObjects.sort(ascendingCompare);
                                            deferred.resolve(resourceObjects);
                            });
                                });
                            }
                        })
                        .catch(rejectError);
                });
            }
            return deferred.promise;
        }

        function addMissingParentResources(resources) {
            var resourceUris = [];
            resources.sort(function (a, b) {
                return a.uri.toLowerCase().localeCompare(b.uri.toLowerCase());
            });
            for (var i = 0; i < resources.length; i++) {
                var resource = resources[i];
                resourceUris.push(resource.uri);
                var resourceLevels = splitResourceURI(resource.uri);
                resourceLevels.pop();
                var parentUri = joinResourceURI(resourceLevels);
                while (resourceLevels.length > 1 && !includes(resourceUris,parentUri)) {
                    var parentResource = {
                        uri: parentUri,
                        leaf: true
                    };
                    resourceUris.push(parentUri);
                    resources.push(parentResource);
                    resourceLevels.pop();
                    parentUri = joinResourceURI(resourceLevels);
                }
            }
        }

        //This a helper function that replaces a .includes call on resourcesUris as IE doesn't support it
        function includes(resourceUris,parentUri) {
            for (var i = 0; i < resourceUris.length; i++){
                if(resourceUris[i] === parentUri){
                    return true;
                }
            }
            return false;
        }

        function getAllTreeNodes(searchText, scheme, groupType) {
            searchText = searchText.replace( /%/g , '*');
            if (scheme) {
                searchText = scheme + '*' + searchText + '*';
            } else {
                searchText = '*' + searchText + '*';
            }
            searchText = checkSearchText(searchText);
            var encodedUri = encodeURIComponent(encodeURIComponent(searchText));
            return urlBuilderService.resources(encodedUri, groupType).then(function(url) {
                return $http.get(url, {cache: false})
                .then(function (httpObj) {
                    var resources = httpObj.data.resources;
                    addMissingParentResources(resources);

                    var treeNodes = findRootNodes(resources);
                    treeNodes.sort(ascendingCompare);

                    buildTree(treeNodes, resources, true);

                    return treeNodes;
                })
                .catch(rejectError);
            });
        }


        function checkSearchText(searchText) {
            if (searchText.indexOf("/") > -1) {
                return searchText.replaceAll("/", "&sol;");
            } else {
                return searchText;
            }
        }

        function buildTree(nodes, resources, open) {
            nodes.forEach(function(currentNode) {
                // Handle child resources of current node
                var filteredResources = getChildResources(currentNode, resources);
                if (filteredResources.length > 0) {
                    currentNode.isParent = true;
                    var children = createChildTreeNodes(filteredResources, currentNode, open, null);
                    children.sort(ascendingCompare);
                    currentNode.children = children;

                    // Handle grand child resources of current node recursively
                    if (filteredResources.length > children.length) {
                        buildTree(children, resources, open);
                    }
                }
            });
        }

        function getChildResources(currentNode, resources) {
            var pattern;
            if (currentNode.isRoot) {
                pattern = new RegExp(currentNode.uri);
            } else {
                pattern = new RegExp(currentNode.uri + '\/');
            }

            return resources.filter(function (obj) {
                return pattern.test(obj.uri) ;
            });
        }

        function findRootNodes(resources) {
            var resourceObjects = [];

            var resourceLevelNames = [];
            for (var i = 0; i < resources.length; i++) {
                var resourceLevels = splitResourceURI(resources[i].uri);
                var currentLevelName = resourceLevels[0];
                if (resourceLevelNames.indexOf(currentLevelName) === -1) {
                    var rootNode = createRootNode(currentLevelName);
                    rootNode.open = true;

                    resourceObjects.push(rootNode);
                    resourceLevelNames.push(currentLevelName);
                }
            }

            return resourceObjects;
        }

        function splitResourceURI(resourceUri) {
            var splitResourceUri = [];
            var splitUri = resourceUri.split('://');

            var scheme = splitUri[0];
            splitResourceUri.push(scheme);

            var path = splitUri[1];
            if(path !== '') {
                var resourceLevels = path.split('/');
                splitResourceUri.push.apply(splitResourceUri, resourceLevels);
            }

            return splitResourceUri;
        }

        function joinResourceURI(resourceLevels) {
            var uri = resourceLevels[0];
            for (var i = 1; i < resourceLevels.length; i++) {
                var separator = i === 1 ? '://' : '/';
                uri += separator + resourceLevels[i];
            }
            return uri;
        }

        function isNodeTraverse( uri, resources) {
            var retVal = false;
            if (resources !== null) {
                retVal = true;
                for (var i = 0; i < resources.length; i++) {
                    var resource = resources[i];
                    if (resource.uri === uri) {
                        retVal = false;
                        break;
                    }
                }
            }
            return retVal;
        }

        function createChildTreeNodes(resources, parent, open, explicitPermits) {
            var resourceObjects = [];
            var parentResourceLevels = splitResourceURI(parent.uri);

            var createChildren = parent.isRoot || parent.isParent;
            if (createChildren) {
                resources.forEach(function(resource) {
                    var resourceLevels = splitResourceURI(resource.uri);
                    var isChild = parentResourceLevels.length + 1 === resourceLevels.length;
                    if (isChild) {
                        var currentLevelName = resourceLevels[parentResourceLevels.length].replaceAll('&sol;','/');
                        var fontStyle = isNodeTraverse(resource.uri, explicitPermits) ? { 'color': '#c0c0c0'} : '';
                        var node = {
                            name: currentLevelName,
                            baseName: currentLevelName,
                            title: currentLevelName,
                            font: fontStyle,
                            uri: resource.uri,
                            id: resource.uri,
                            isParent: !resource.leaf,
                            open: open,
                            icon: './assets/diy/2.png'
                        };
                        resourceObjects.push(node);
                    }
                });
            }

            return resourceObjects;
        }



        function getPermissionPrefix(userGroupId, resourceUri, permissionTypes) {
            return getPrivileges(userGroupId, resourceUri).then(function(data) {
                return permissionTypes.map(function(p) {
                    return (data.userGroupPrivileges.length > 0 && data.userGroupPrivileges[0].permissionType.includes(p))?p.substring(0, 1):'-';
                }).join('');
            });
        }

        function getPermissionTypes(scope) {
            return urlBuilderService.permissionTypes(scope).then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    return httpObj.data;
                })
                .catch(rejectError);
            });
        }

        function getGroupsWithPrivileges(uri, permissionTypes, groupType, defaultForDescendants) {
            var deferred = $q.defer();
            var promises = [];
            if (permissionTypes.length > 0) {
                permissionTypes.forEach(function(permissionType) {
                    promises.push(getGroupsWithPrivilege(uri, permissionType, groupType, defaultForDescendants));
                });
                $q.all(promises).then(function(data) {
                    deferred.resolve(data);
                });
            }

            return deferred.promise;
        }

        function getGroupsWithPrivilege(uri, permissionType, groupType, defaultForDescendants) {
            var doubleEncodedUri = encodeURIComponent(encodeURIComponent(uri));
            return urlBuilderService.groupsWithPrivilege(doubleEncodedUri, permissionType, groupType, defaultForDescendants).then(function(url) {
                return $http.get(url).then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function getPrivileges(userGroupId, uri) {
            var doubleEncodedUri = encodeURIComponent(encodeURIComponent(uri));
            return urlBuilderService.privilegesUri(userGroupId, doubleEncodedUri).then(function(url) {
                return $http.get(url).then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function savePrivileges(userGroupIDs, privilegeChanges) {
            var deferred = $q.defer();
            var promises = [];
            if (userGroupIDs.length > 0) {
                userGroupIDs.forEach(function(userGroupId) {
                    promises.push(savePrivilege(userGroupId, privilegeChanges));
                });
                $q.all(promises).then(function(data) {
                    deferred.resolve(data);
                });
            }

            return deferred.promise;
        }

        function savePrivilege(userGroupId, privileges) {
            return urlBuilderService.privileges(userGroupId).then(function(url) {
                return $http.put(url, privileges)
                .catch(rejectError);
            });
        }

        function deletePrivilege(userGroupId, privileges) {
            var config = {
                    data: privileges,
                    headers: {
                        'Content-Type' : 'application/json'
                    }
                };

            return urlBuilderService.privileges(userGroupId).then(function(url) {
                return $http.delete(url, config)
                .catch(rejectError);
            });
        }


        function getPrivilegesOnResources(resources) {
            var jsonObject = {
                    'resources' : resources
                };
            return urlBuilderService.userPrivileges().then(function(url) {
                return $http.put(url, jsonObject)
                .then(function(httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function getPermissionTypesForResource(resource) {
            var fullUri = getFullUri(resource);
            var resourceArray = [fullUri];
            return getPrivilegesOnResources(resourceArray)
                .then(function(data) {
                    var permissionTypes = {};

                    data.userPrivileges.forEach(function(privilege){
                        privilege.permissionType.forEach(function(permissionTypeName){
                            permissionTypes[permissionTypeName] = true;
                        });
                    });
                    return permissionTypes;
                });
        }

        function getPermissionTypesForResources(resources) {
            var resourceArray = [];
            resources.forEach(function(resource){
                resourceArray.push(getFullUri(resource));
            });

            return getPrivilegesOnResources(resourceArray)
                .then(function(data) {
                     var resourcesWithRead = [];
                     data.userPrivileges.forEach(function(userPrivilege){
                         userPrivilege.permissionType.forEach(function(permissionTypeName){
                             if(permissionTypeName === 'Read') {
                                 var resourceWithoutScheme = userPrivilege.uri.split('://');
                                 resourcesWithRead.push(resourceWithoutScheme[1]);
                             }
                         });
                     });
                    return resourcesWithRead;
                });
        }

        function getFullUri(resource) {
            var schema = 'Access Control';
            var uri = schema + '://'+ resource;
            return uri;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.organizations')
        .factory('organizationService', OrganizationServiceFactory)
        .factory('dataModelPropertyCache', ['$cacheFactory', function($cacheFactory) {
            return $cacheFactory('dataModelPropertyCache');
        }]);

    OrganizationServiceFactory.$inject = ['$q', '$http', 'dataModelPropertyCache', 'urlBuilderService', 'modalService'];

    /* @ngInject */
    function OrganizationServiceFactory($q, $http, dataModelPropertyCache, urlBuilderService, modalService) {

        var service = {
            getOrganizations: getOrganizations,
            getOrganization: getOrganization,
            saveOrganization: saveOrganization,
            deleteOrganization: deleteOrganization,
            createOrganization: createOrganization,
            getDataModelProperties : getDataModelProperties
        };

        return service;

        ////////////////

        function rejectError(httpErrorObj) {
            return $q.reject(httpErrorObj.status);
        }

        function getOrganizations(searchText, offset, limit, orderBy, sortAscending) {
            if (searchText) {
                searchText = searchText.replace(new RegExp('%','g'), '*');
            }
            return urlBuilderService.searchOrganizations(searchText || '*', offset, limit, orderBy, sortAscending).then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function getOrganization(ncage) {
            return urlBuilderService.organization(ncage || '').then(function(url) {
                return $http.get(url)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function saveOrganization(organization) {
            return urlBuilderService.organization(organization.ncage).then(function(url) {
                return $http.put(url, organization)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function createOrganization(organization) {
            return urlBuilderService.organizations().then(function(url) {
                return $http.post(url, organization)
                .then(function (httpObj) {
                    var data = httpObj.data;
                    return data;
                })
                .catch(rejectError);
            });
        }

        function deleteOrganization(organization) {
            return modalService.showDeletionConfirmation(organization.ncage)
                .then(deleteOrganizationFromServer);

            function deleteOrganizationFromServer() {
                return urlBuilderService.organization(organization.ncage).then(function(url) {
                    return $http.delete(url)
                    .then(function() {
                        return organization;
                    })
                    .catch(rejectError);
                });
            }
        }

        function getDataModelProperties() {
            return urlBuilderService.schema('organization').then(function(dataModelPropertiesUrl) {

                var deferred = $q.defer();
                var data = dataModelPropertyCache.get(dataModelPropertiesUrl);

                if (data) {
                    deferred.resolve(data);
                } else {
                    $http.get(dataModelPropertiesUrl)
                    .then(function(httpObj) {
                        dataModelPropertyCache.put(dataModelPropertiesUrl, httpObj.data);
                        deferred.resolve(httpObj.data);
                    })
                    .catch(rejectError);
                }

                return deferred.promise;
            });
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.modal', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.modal')
        .factory('modalService', ModalServiceFactory);

    ModalServiceFactory.$inject = ['$uibModal'];

    /* @ngInject */
    function ModalServiceFactory($uibModal) {

        var service = {
            showDeletionConfirmation : showDeletionConfirmation,
            showMemberDeletionConfirmation: showMemberDeletionConfirmation,
            showConfirmationModal : showConfirmationModal,
            showUserProfileInfo: showUserProfileInfo
        };

        return service;

        ////////////////

        function showDeletionConfirmation(id) {
            return $uibModal.open({
                templateUrl: '/templates/core/modal/deleteModal.html',
                controller: 'DeleteModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: 'Do you really want to delete ' + id + '?'
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function showMemberDeletionConfirmation(message) {
            return $uibModal.open({
                templateUrl: '/templates/core/modal/deleteModal.html',
                controller: 'DeleteModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: message
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function showConfirmationModal(message){
            'use strict';

            return $uibModal.open({
                templateUrl: '/templates/core/modal/simpleModal.html',
                controller: 'SimpleModalController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: message
                        };
                    }
                },
                size: 'sm'
            }).result;
        }

        function showUserProfileInfo(message){
            'use strict';

            $uibModal.open({
                templateUrl: '/templates/core/modal/userProfileInfoModal.html',
                controller: 'UserProfileInfoController',
                controllerAs: 'vm',
                resolve: {
                    info: function () {
                        return {
                            message: message
                        };
                    }
                },
                size: 'lg'
            });
        }
    }


})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.header', []);

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.header')
        .directive('acmHeader', AcmHeaderDirective);

    AcmHeaderDirective.$inject = [];

    function AcmHeaderDirective () {
        return {
            restrict: 'AE',
            scope: {},
            templateUrl: '/templates/header/header.html',
            controller: 'AcmHeaderController',
            controllerAs: 'vm'
        };
    }


})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons
 *            Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA
 *            92614-6078, USA
 */

(function() {
    'use strict';

    angular.module('app.widget.acm.header').controller('AcmHeaderController',
            AcmHeaderController);

    AcmHeaderController.$inject = [ '$state', '$window', 'flatironsAppConfigService', 'userService', 'privilegeService'];

    /* @ngInject */
    function AcmHeaderController($state, $window, flatironsAppConfigService, userService, privilegeService) {
        var vm = this;
        userService.getUserDetails().then(function (data) {
            vm.token = data;
            if(vm.token) {
                vm.flatironsHeaderConfig.guestAccessMode = vm.token.guestaccessmode;
            }
        });

        vm.flatironsHeaderConfig = {
            homeState : 'app.default',
            logoSrc : './assets/FS-Logo-White.svg',
            modules : {
                ppClient : {
                    name : 'Pinpoint Viewer',
                    iconCssClass : 'icon-globe',
                    visible: false
                },
                dmgrClient : {
                    name : 'Data Manager',
                    iconCssClass : 'icon-database-gear',
                    visible: false
                },
                acm : {
                    name: 'Access Control Manager',
                    iconCssClass: 'icon-lock',
                    value: 'Access Control',
                    visible: true,
                    isCurrentModule: true,
                    clickAction: function () {}
                },
                amClient : {
                    name : 'Audit Manager',
                    iconCssClass : 'icon-chart',
                    visible: false
                }},

            common : {
                configuration : {
                    name : 'Configuration',
                    iconCssClass : 'icon-gear',
                    clickAction : function() {
                        $state.go('app.configuration');
                }},
                help : {
                    name : 'Help',
                    iconCssClass : 'icon-book',
                    clickAction : function() {
                        $window.open('webhelp', '_blank');
                }}
            },

            shortcuts : {
                privileges : {
                    name : 'Privileges',
                    iconCssClass: 'icon-person-gear',
                    clickAction : function() {
                        $state.go('app.privileges');
                }},
                users : {
                    name : 'Users',
                    iconCssClass : 'icon-person',
                    clickAction : function() {
                        $state.go('app.users');
                }},
                usergroups : {
                    name : 'User Groups',
                    iconCssClass : 'icon-person-group',
                    clickAction : function() {
                        $state.go('app.usergroups');
                }},
                organizations : {
                    name : 'Organizations',
                    iconCssClass : 'icon-building',
                    clickAction : function() {
                        $state.go('app.organizations');
                }}
            }
        };

        flatironsAppConfigService.getAppConfig().then(function(config) {
            var ppClient = vm.flatironsHeaderConfig.modules.ppClient;
            if(config.ppClient) {
                ppClient.visible = true;
                ppClient.clickAction = function () {
                    $window.open(config.ppClient, '_blank');
                };
            }

            var dmgrClient = vm.flatironsHeaderConfig.modules.dmgrClient;
            if(config.dmgrClient) {
                dmgrClient.visible = true;
                dmgrClient.clickAction = function () {
                    $window.open(config.dmgrClient, '_blank');
                };
            }

            var amClient = vm.flatironsHeaderConfig.modules.amClient;
            if(config.amClient) {
                amClient.visible = true;
                amClient.clickAction = function () {
                    $window.open(config.amClient, '_blank');
                };
            }
        });

        updatePermissionForShortcut(privilegeService, vm.flatironsHeaderConfig.common.configuration);

        for(var n in vm.flatironsHeaderConfig.shortcuts) {
            if (vm.flatironsHeaderConfig.shortcuts[n]) {
                var shortcut = vm.flatironsHeaderConfig.shortcuts[n];
                updatePermissionForShortcut(privilegeService, shortcut);
            }
        }
    }

    function updatePermissionForShortcut(privilegeService, shortcut) {
        privilegeService.getPermissionTypesForResource(shortcut.name)
            .then(function (data) {
                if (!data.Read) {
                    shortcut.disabled = true;
                    shortcut.tooltip = '\nYou do not have permission to view this';
                }
            });
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.footer', []);

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 *
 * Insert <status-widget></status-widget> where you want the status message to appear.
 *
 * If you want the text to disappear after X milliseconds, add this attribute:
 * <status-widget timeout="X milliseconds"></status-widget>
 *
 * To update the status test: $rootScope.$broadcast('updateStatusText', 'new text');
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.footer')
        .directive('userinfoWidget', UserInfoWidget);

    UserInfoWidget.$inject = [];

    function UserInfoWidget () {
        return {
            restrict: 'AE',
            templateUrl: '/templates/footer/userInfo.html',
            controller: 'UserInfoFooterController',
            controllerAs: 'vm'
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.footer')
        .controller('UserInfoFooterController', UserInfoFooterController);

    UserInfoFooterController.$inject = ['modalService','userService'];

    /* @ngInject */
    function UserInfoFooterController(modalService, userService) {
        var vm = this;

        vm.versionLoaded = false;

        userService.getUserDetails().then(function(data) {
            vm.userInfo = data;
        });

        vm.openUserProfile = function () {
            if (vm.userInfo && (vm.userInfo.groups || vm.userInfo.roles)) {
                var message = {};
                message.userInfo = vm.userInfo;
                message.userGroups = vm.userInfo.groups;
                message.userRoles = vm.userInfo.roles;
                modalService.showUserProfileInfo(message);
            }
        };

        vm.getFooterText = function() {
            if(vm.userInfo !== undefined){
                var result = vm.userInfo.firstname + ' ' + vm.userInfo.lastname;

                // Add the first role the user belongs to, if it exists
                if(vm.userInfo.roles && vm.userInfo.roles.length > 0) {
                    result += ' - ' + vm.userInfo.roles[0].name;
                }

                return result;
            }
            return '';
        };
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.footer')
        .directive('acmFooter', AcmFooterDirective);

    AcmFooterDirective.$inject = [];

    function AcmFooterDirective () {
        return {
            restrict: 'AE',
            scope: {},
            template: '<flatirons-footer>' +
                        '<status-widget timeout="5000"></status-widget>' +
                        '<userinfo-widget></userinfo-widget>' +
                      '</flatirons-footer>'
        };
    }

})();
/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.core.event', [])
        .run(EventMapper);

    EventMapper.$inject = ['$rootScope', 'eventService'];

    /* @ngInject */
    function EventMapper($rootScope, eventService) {
        eventService.runMapper($rootScope);
    }
})();

(function () {
    'use strict';

    angular
        .module('app.core.event')
        .factory('eventService', EventServiceFactory);

    EventServiceFactory.$inject = ['eventsSeq'];

    /* @ngInject */
    function EventServiceFactory(eventsSeq)
    {
        var service = {
            runMapper: runMapper
        };

        return service;

        ////////////////

        function runMapper(rootScope) {
            for (var i=0; i<eventsSeq.length; i++) {
                var eventSeq = eventsSeq[i];

                var eventHandler = createEventHandler(eventSeq, rootScope);
                rootScope.$on(eventSeq.sourceEvent, eventHandler);
            }
        }

        function createEventHandler (eventSeq, rootScope) {
            return function() {
                var eventArguments =  Array.prototype.slice.call(arguments, 0);
                for (var i=0; i<eventSeq.targets.length; i++) {

                    eventArguments[0] = eventSeq.targets[i].targetEvent;
                    rootScope.$broadcast.apply(rootScope, eventArguments);
                }
            };
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .filter('localDateTime', localDateTime);

    localDateTime.$inject = ['$filter'];

    function localDateTime($filter) {
        return function (isoTime) {
            if (isoTime === undefined || isoTime === null) {
                return '';
            } else {
                var location = isoTime.indexOf('[');
                var angularDateFilter = $filter('date');

                return angularDateFilter(isoTime.slice(0, location), 'medium');
            }
        };
    }

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */



(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .directive('layoutInjector', layoutInjector);

    /* @ngInject */
    function layoutInjector() {
        return {
            restrict: 'E',
            link: function(scope, element, attrs) {
                element.css('width','100%');
                element.css('height','100%');
                element.css('display','block');

                var mainContent = angular.element($('#' + attrs.maincontentid));
                mainContent.detach();

                var panels = [ {
                    type : 'main',
                    minSize : 500,
                    content : mainContent
                } ];

                if (attrs.topcontentid) {
                    var topContent = angular.element($('#' + attrs.topcontentid));
                    var topContentHeight = topContent.outerHeight();

                    panels.push({
                        type : 'top',
                        size : topContentHeight,
                        minSize : 38,
                        overflow : 'visible',
                        content : topContent
                    });

                    topContent.detach();
                }

                if (attrs.rightcontentid) {
                    var rightContent = angular.element($('#' + attrs.rightcontentid));
                    panels.push({
                        type : 'right',
                        size: attrs.rightcontentsize || 400,
                        hidden: 'true' === attrs.rightcontenthidden,
                        minSize : 120,
                        content : rightContent,
                        resizable: true
                    });

                    rightContent.detach();
                }

                element.w2layout({
                    name: attrs.layoutname,
                    resizer: 2,
                    padding: 0,
                    panels: panels
                });

                scope.$on('$destroy', function() {
                    w2ui[attrs.layoutname].destroy();
                });

            }
        };
    }
})();



/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.core')
        .factory('errorHttpInterceptor', errorHttpInterceptor);

    errorHttpInterceptor.$inject = ['$q', '$sce', 'ngToast'];

    /* @ngInject */
    function errorHttpInterceptor($q, $sce, ngToast)
    {
        var interceptor = {
            'responseError': requestError
        };

        return interceptor;

        ///////////////////

        function requestError(rejection) {

            var message = '';

            if (angular.isArray(rejection.data) && rejection.data.length > 0 && rejection.status !== 403) {
                message = getErrorMessage(rejection);
            } else if(rejection.status === 403) {
                message = 'Access denied';
            } else {
                message = generateUnknownErrorHtml(rejection);
            }

            ngToast.create({
                className: 'danger',
                content: $sce.trustAsHtml(message),
                dismissOnTimeout: false,
                dismissButton: true,
                dismissOnClick: false
            });

            return $q.reject(rejection);
        }

        function getErrorMessage(rejection) {
            var message = '';
            for (var i = 0; i < rejection.data.length; ++i) {
                var errorMessage = rejection.data[i].error_message; // jshint ignore:line
                if (errorMessage) {
                    message += errorMessage;

                    if (i !== (rejection.data.length - 1)) {
                        message += '\n\n';
                    }
                } else {
                    message = generateUnknownErrorHtml(rejection);
                }
            }
            return message;
        }
        
        function generateUnknownErrorHtml(rejection) {
            var elementId = 'rejection-details-' + new Date().getTime();
            var errorMessage = 'Something went wrong.<button data-target="#' + elementId + '" data-toggle="collapse">View details...</button>';
            var details = '<div id="' + elementId + '" class="collapse">' + getErrorText(rejection) + '</div>';
            
            return errorMessage + details;
        }
        
        function getErrorText(rejection) {
            // First line is the HTTP status
            var statusCode = 'Status Code: ' + rejection.status + '<br/>';
            
            // If the response is JSON, this will convert it to a string
            // If it is anything else, this will leave it alone
            var content = JSON.stringify(rejection.data);
            
            // If the response is HTML, this will escape it
            // If it is anything else, this will leave it alone
            var escapedContent = $('<div>').text(content).html();
            
            return statusCode + escapedContent;
        }
    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm.urlBuilder', []);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
            .module('app.widget.acm.urlBuilder')
            .factory('urlBuilderService', UrlBuilderService);

    UrlBuilderService.$inject = ['$q', '$http', 'flatironsAppConfigService'];

    /* @ngInject */
    function UrlBuilderService($q, $http, flatironsAppConfigService) {

        return {
            baseUrl: baseUrl,
            organizations: organizations,
            organization: organization,
            searchOrganizations: searchOrganizations,

            users: users,
            user: user,
            searchUsers: searchUsers,
            userDetails: userDetails,
            searchUserGroups: searchUserGroups,
            userGroup: userGroup,
            usergroups: usergroups,
            userGroupMembers: userGroupMembers,
            userGroupRoles: userGroupRoles,
            ldapConfiguration: ldapConfiguration,

            permissionTypes: permissionTypes,
            permissionType: permissionType,

            schemes: schemes,

            schema: schema,

            resources: resources,
            resourceChildren: resourceChildren,
            resourceChildrenWithTraverse: resourceChildrenWithTraverse,

            privileges: privileges,
            privilegesUri: privilegesUri,
            groupsWithPrivilege: groupsWithPrivilege,
            userPrivileges: userPrivileges,

            auth: auth,
            authEncrypted: authEncrypted,
            authEncryptedJasypt: authEncryptedJasypt,

            saml: saml,
            samlRequest: samlRequest,
            samlConfiguration: samlConfiguration,
            authProvConfiguration: authProvConfiguration,
            upload: upload,
            accessKeysUrl: accessKeysUrl,
            cookieConfiguration: cookieConfiguration,
            copyUserGroupPrivilegesUrl: copyUserGroupPrivilegesUrl
        };

        ////////////////

        function baseUrl() {
            return flatironsAppConfigService.getAppConfig()
                .then(function(config) {
                    return config.acmServer;
                });
        }

        function upload() {
            return usergroups()
                .then(function(url) {
                    return url + 'upload/';
                });
        }

        function authProvConfiguration() {
            return baseUrl().then(function(url) {
                return url + 'authproviderconfig/';
            });
        }
        function saml() {
            return baseUrl().then(function(url) {
                return url + 'saml/';
            });
        }

        function samlRequest() {
            return saml().then(function(url) {
                return url + 'request';
            });
        }

        function samlConfiguration() {
            return saml().then(function(url) {
                return url + 'configuration/';
            });
        }

        function organizations() {
            return baseUrl().then(function(url) {
                return url + 'organizations/';
            });
        }

        function usergroups() {
            return baseUrl().then(function(url) {
                return url + 'usergroups/';
            });
        }

        function schema(schemaName) {
            return baseUrl().then(function(url) {
                return url + 'schema/' + schemaName + '/';
            });
        }

        function organization(ncage) {
            return organizations().then(function(url) {
                return url + ncage;
            });
        }

        function searchOrganizations(searchText, offset, limit, orderBy, sortAscending) {
            return baseUrl().then(function(url) {
                return url + 'searchOrganizations/' + searchText + '/?limit=' + limit + '&offset=' + offset + '&orderBy=' + orderBy + '&sortAscending=' + sortAscending;
            });
        }

        function users() {
            return baseUrl().then(function(url) {
                return url + 'users/';
            });
        }

        function user(userName) {
            return users().then(function(url) {
                return url + userName;
            });
        }

        function searchUsers(searchText, offset, limit, orderBy, sortAscending, includeInactive, orgFilter) {
            return baseUrl().then(function(url) {
                return url + 'searchUsers/' + searchText + '/?limit=' + limit + '&offset=' + offset + '&orderBy=' + orderBy + '&sortAscending=' + sortAscending + '&includeInactive=' + includeInactive + '&orgFilter=' + orgFilter;
            });
        }

        function userDetails() {
            return baseUrl().then(function(url) {
                return url + 'auth/userdetails';
            });
        }

        function searchUserGroups(searchText, type, offset, limit, orderBy, sortAscending) {
            return baseUrl().then(function(url) {

                var uri = url + 'searchUserGroups/' + searchText;
                var prefix = '/?';

                if (type) {
                    uri += prefix + 'type=' + type;
                    prefix = '&';
                }

                if (offset) {
                    uri += prefix + 'offset=' + offset;
                    prefix = '&';
                }

                if (limit) {
                    uri += prefix + 'limit=' + limit;
                    prefix = '&';
                }

                if (orderBy) {
                    uri += prefix + 'orderBy=' + orderBy;
                    prefix = '&';
                }

                if (sortAscending !== null || sortAscending !== undefined) {
                    uri += prefix + 'sortAscending=' + sortAscending;
                }
                uri += prefix + 'isAcmClient=' + true;
                return uri;
            });
        }

        function cookieConfiguration() {
            return baseUrl().then(function (url) {
                return url + 'auth/cookie';
            });
        }

        function copyUserGroupPrivilegesUrl(userGroupId, sourceUserGroupId, isOrganization) {
            return userGroup(userGroupId).then(function (url) {
                return url + '/copy/privileges/' + sourceUserGroupId + "?isOrganization=" + isOrganization;
            });
        }

        function userGroup(userGroupId) {
            return baseUrl().then(function(url) {
                return url + 'usergroups/' + userGroupId;
            });
        }

        function userGroupMembers(userGroupId) {
            return userGroup(userGroupId).then(function(url) {
                return url + '/members';
            });
        }

        function userGroupRoles(userGroupId) {
            return userGroup(userGroupId).then(function(url) {
                return url + '/roles/';
            });
        }

        function ldapConfiguration() {
            return baseUrl().then(function(url) {
                return url + 'ldapconfiguration/';
            });
        }

        function permissionTypes(scope) {
            return baseUrl().then(function(url) {
                var uri = url + 'permissiontypes/';
                if(scope !== null && scope !== undefined) {
                    uri += '?scope=' + scope;
                }
                return uri;
            });
        }

        function permissionType(permissionTypeName) {
            return permissionTypes().then(function(url) {
                return url + permissionTypeName;
            });
        }

        function schemes() {
            return baseUrl().then(function(url) {
                return url + 'schemes/';
            });
        }

        function resources(uri, groupType) {
            return baseUrl().then(function(url) {
                return url + 'resources?uri=' + uri + '&actions=false' + '&groupType=' + groupType;
            });
        }

        function resourceChildren(uri,userGroupId,permissionType,groupType) {
            return baseUrl().then(function(url) {
                if ((userGroupId === undefined) || (permissionType === undefined)) {
                    return url + 'resources/' + uri + '/children?actions=false';
                } else {

                    return url + 'resources/' + uri + '/' + userGroupId + '/' + permissionType + '/' + groupType + '/children?actions=false';
                }
            });
        }

        function resourceChildrenWithTraverse(uri,userGroupId,permissionType,groupType) {
            return baseUrl().then(function(url) {
                if ((userGroupId === undefined) || (permissionType === undefined)) {
                    return url + 'resources/' + uri + '/children?actions=false';
                } else {

                    return url + 'resources/' + uri + '/' + userGroupId + '/' + permissionType + '/' + groupType + '/traverse?actions=false';
                }
            });
        }

        function privileges(userGroupId) {
            return userGroup(userGroupId).then(function(url) {
                return url + '/privileges?actions=false';
            });
        }

        function privilegesUri(userGroupId, uri) {
            return userGroup(userGroupId).then(function(url) {
                return url + '/privileges/' + uri + '?actions=false';
            });
        }

        function groupsWithPrivilege(uri, permissionType, groupType, defaultForDescendants) {
            return usergroups().then(function(url) {
                return url + uri + '/' + permissionType + '?groupType=' +groupType+ '&defaultForDescendants=' + defaultForDescendants;
            });
        }

        function userPrivileges() {
            return baseUrl().then(function(url) {
                return url + 'auth/privileges';
            });
        }

        function auth() {
            return baseUrl().then(function(url) {
                return url + 'auth';
            });
        }

        function authEncrypted() {
            return auth().then(function(url) {
                return url + '/encrypted';
            });
        }

        function authEncryptedJasypt() {
            return auth().then(function(url) {
                return url + '/jasypt';
            });
        }

        function accessKeysUrl() {
            return baseUrl(). then(function (url) {
                return url + 'accesskeys';
            });
        }

    }
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm')
        .config(["$stateProvider", "$urlRouterProvider", "$urlMatcherFactoryProvider", "acmConstants", "$locationProvider", function ($stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider, acmConstants, $locationProvider) {
            $urlMatcherFactoryProvider.strictMode(false);
            $urlRouterProvider.otherwise('');
            $locationProvider.hashPrefix('');

            $stateProvider
                .state('login', {
                    url: '/login',
                    template: '<login></login>'
                })
                .state('app', {
                    abstract: true,
                    template: '<toast></toast><div class="acmlayout acm-view" id="acmlayout"</div>',
                    controller: 'AcmController',
                    contollerAs: 'vm'
                })
                .state('app.default', {
                    url: '',
                    views: {
                        'mainView@app': {
                            template: '<welcome-page appconfig="acmappconfig"></welcome-page>',
                            controller: ["$scope", "acmappconfig", function($scope, acmappconfig) {
                                $scope.acmappconfig = acmappconfig;
                            }]
                        }
                    },
                    resolve:{
                        acmappconfig:["flatironsAppConfigService", function(flatironsAppConfigService){
                            return flatironsAppConfigService.getAppConfig();
                        }]
                    }
                })
                .state('app.organizations', {
                    url: '/organizations',
                    views: {
                        'leftView@app': {
                            template: '<organization-list></organization-list>'
                        }
                    },
                    accessResource: acmConstants.ORGANIZATIONS_RESOURCE

                })
                .state('app.organizations.organization', {
                    url: '/:ncage',
                    views: {
                        'mainView@app': {
                            template: '<organization-details></organization-details>'
                        }
                    },
                    accessResource: acmConstants.ORGANIZATIONS_RESOURCE
                })
                .state('app.users', {
                    url: '/users',
                    views: {
                        'leftView@app': {
                            template: '<user-list></user-list>'
                        }
                    },
                    accessResource: acmConstants.USERS_RESOURCE
                })
                .state('app.users.user', {
                    url: '/:userName',
                    views: {
                        'mainView@app': {
                            template: '<user-details></user-details>'
                        }
                    },
                    accessResource: acmConstants.USERS_RESOURCE
                })
                .state('app.configuration', {
                    url: '/configuration',
                    views: {
                        'leftView@app': {
                            template: '<configuration-list permissions="configuriationListPermissions"></configuration-list>',
                            controller: ["$scope", "configuriationListPermissions", function($scope, configuriationListPermissions){
                                $scope.configuriationListPermissions = configuriationListPermissions;
                            }]
                        }
                    },
                    resolve:{
                        configuriationListPermissions:["privilegeService", function(privilegeService){
                            var configurationResources = ['Configuration/Permission Types', 'Configuration/LDAP Configuration', 'Configuration/SAML Configuration', 'Configuration/Authentication Provider', 'Configuration/Encryption'];
                            return privilegeService.getPermissionTypesForResources(configurationResources);
                        }]
                    },
                    accessResource: acmConstants.CONFIGURATION_RESOURCE
                })
                .state('app.configuration.ldapconfiguration', {
                    url: '/ldapconfiguration',
                    views: {
                        'mainView@app': {
                            template: '<ldap-configuration init="initLDAPConfiguration"></ldap-configuration>',
                            controller: ["$scope", "authProviderConfig", "ldapConfiguration", "ldapConfigurationPermissions", function($scope, authProviderConfig, ldapConfiguration, ldapConfigurationPermissions) {
                                var initLDAPConfiguration = {};
                                initLDAPConfiguration.authprovider = authProviderConfig.value;
                                initLDAPConfiguration.ldapconfig = ldapConfiguration;
                                initLDAPConfiguration.permissions = ldapConfigurationPermissions;
                                $scope.initLDAPConfiguration = initLDAPConfiguration;
                            }]
                        }
                    },
                    resolve:{
                        authProviderConfig:["authProvService", function(authProvService) {
                            return authProvService.retrieveAuthProvConfiguration();
                        }],
                        ldapConfiguration:["ldapService", function(ldapService) {
                            return ldapService.retrieveLDAPConfiguration();
                        }],
                        ldapConfigurationPermissions:["privilegeService", function(privilegeService) {
                            return privilegeService.getPermissionTypesForResource(acmConstants.LDAP_CONFIGURATION_RESOURCE);
                        }]
                    },
                    accessResource: acmConstants.LDAP_CONFIGURATION_RESOURCE
                })
                .state('app.configuration.samlconfiguration', {
                    url: '/samlconfiguration',
                    views: {
                        'mainView@app': {
                            template: '<saml-configuration init="initSAMLConfiguration"></saml-configuration>',
                            controller: ["$scope", "samlConfiguration", "samlConfigurationPermissions", function($scope, samlConfiguration, samlConfigurationPermissions) {
                                var initSAMLConfiguration = {};
                                initSAMLConfiguration.samlconfig = samlConfiguration;
                                initSAMLConfiguration.permissions = samlConfigurationPermissions;
                                $scope.initSAMLConfiguration = initSAMLConfiguration;
                            }]
                        }
                    },
                    resolve:{
                        samlConfiguration:["samlService", function(samlService) {
                            return samlService.retrieveSAMLConfiguration();
                        }],
                        samlConfigurationPermissions:["privilegeService", function(privilegeService) {
                            return privilegeService.getPermissionTypesForResource(acmConstants.SAML_CONFIGURATION_RESOURCE);
                        }]
                    },
                    accessResource: acmConstants.SAML_CONFIGURATION_RESOURCE
                })
                .state('app.configuration.authprovider', {
                    url: '/authprovider',
                    views: {
                        'mainView@app': {
                            template: '<auth-prov-configuration></auth-prov-configuration>'
                        }
                    },
                    accessResource: acmConstants.AUTHENTICATION_PROVIDER_RESOURCE
                })
                .state('app.configuration.permissiontypes', {
                    url: '/permissiontypes',
                    views: {
                        'mainView@app': {
                            template: '<permission-types></permission-types>'
                        }
                    },
                    accessResource: acmConstants.PERMISSION_TYPES_RESOURCE
                })
                .state('app.configuration.encryption', {
                    url: '/encryption',
                    views: {
                        'mainView@app': {
                            template: '<encryption></encryption>'
                        }
                    },
                    accessResource: acmConstants.ENCRYPTION_RESOURCE
                })
                .state('app.privileges', {
                    url: '/privileges',
                    views: {
                        'leftView@app': {
                            template: '<user-group-list eventname="resourcesUserGroupSelected" enableCreateNew="false" selectfirst="true"></user-group-list>'
                        }
                    },
                    accessResource: acmConstants.PRIVILEGES_RESOURCE
                })
                .state('app.privileges.usergroup', {
                    views: {
                        'mainView@app': {
                            template: '<privilege-details>/<privilege-details>'
                        }
                    },
                    params: {userGroupIDs: [], userGroupId: null, currentGroupRole: 'User Groups'},
                    accessResource: acmConstants.PRIVILEGES_RESOURCE
                })
                .state('app.usergroups', {
                    url: '/usergroups',
                    views: {
                        'leftView@app': {
                            template: '<user-group-list eventname="userGroupSelected" enablecreatenew="true"</user-group-list>'
                        }
                    },
                    accessResource: acmConstants.USER_GROUPS_RESOURCE
                })
                .state('app.usergroups.usergroup', {
                    url: '/:userGroupId',
                    views: {
                        'mainView@app': {
                            template: '<user-group-details></user-group-details>'
                        }
                    },
                    params: {userGroupIDs: [], userGroupId: null, currentGroupRole: 'User Groups'},
                    accessResource: acmConstants.USER_GROUPS_RESOURCE
                });
        }]);
})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm')
        .config(['ngClipProvider', function(ngClipProvider) {
            ngClipProvider.setPath('./swf/ZeroClipboard.swf');
        }]);

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm')
        .config(["$httpProvider", function ($httpProvider) {
            $httpProvider.interceptors.push('errorHttpInterceptor');
            $httpProvider.interceptors.push('authInterceptor');
        }]);

})();

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */

(function () {
    'use strict';

    angular
        .module('app.widget.acm')
        .constant('eventsSeq', [
            {
                'sourceEvent': 'organizationSelected',
                'sourceWidget': 'organizationList',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'organizationDeleted',
                'sourceWidget': 'organizationDetails',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    },
                    {
                        'targetEvent': 'refreshOrganizations',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'userSelected',
                'sourceWidget': 'userList',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'configurationSelected',
                'sourceWidget': 'configurationList',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'userGroupSelected',
                'sourceWidget': 'userGroupList',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'userDeleted',
                'sourceWidget': 'userDetails',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    },
                    {
                        'targetEvent': 'refreshUsers',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'userGroupDeleted',
                'sourceWidget': 'userGroupDetails',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    },
                    {
                        'targetEvent': 'refreshUserGroups',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'resourcesUserGroupSelected',
                'sourceWidget': 'userGroupList',
                'targets': [
                    {
                        'targetEvent': 'changeMainAreaState',
                        'targetWidget': 'acm'
                    }
                ]
            },
            {
                'sourceEvent': 'permissionTypeSelected',
                'sourceWidget': 'permissionTypes',
                'targets': [
                    {
                        'targetEvent': 'permissionTypeSelect',
                        'targetWidget': 'acm'
                    }
                ]
            }
        ]
    );
})();


/**
 * @function isNotNull
 * @param {Object} data
 * @returns {boolean} is null or not
 */
function isNotNull(data) {
    return data !== null && data !== undefined;
}

/**
 * @copyright (c) 2015 Flatirons Solutions Inc., All Rights Reserved. Flatirons Solutions, Inc., 17671 Cowan Ave., Suite 200, Irvine CA 92614-6078, USA
 */


(function () {
    'use strict';

    angular
        .module('app.widget.acm')
        .controller('AcmController', AcmController);

    AcmController.$inject = ['$scope', '$state', '$compile', '$rootScope'];

    /* @ngInject */
    function AcmController($scope, $state, $compile, $rootScope) {
        $scope.$on('changeMainAreaState', handleChangeMainAreaStateEvent);
        $scope.globalLoadingOverlayPromise = {};
        setUpAcmLayout($compile, $scope);

        $rootScope.$on("resolveLoadingOverlayPromise", function (event, message) {
            $scope.globalLoadingOverlayPromise = message;
        });

        function handleChangeMainAreaStateEvent(event, node) {
            var id = node.id;
            var value = node.value;

            if (id === 'organizationSelected') {
                $state.go('app.organizations.organization', {ncage: value});
            } else if (id === 'userSelected') {
                $state.go('app.users.user', {userName: value});
            } else if (id === 'ldap') {
                $state.go('app.configuration.ldapconfiguration');
            } else if (id === 'saml') {
                $state.go('app.configuration.samlconfiguration');
            } else if (id === 'authProv') {
                $state.go('app.configuration.authprovider');
            } else if (id === 'permissiontypes') {
                $state.go('app.configuration.permissiontypes');
            } else if (id === 'encryption') {
                $state.go('app.configuration.encryption');
            } else if (id === 'userGroupSelected') {
                $state.go('app.usergroups.usergroup', value);
            } else if (id === 'resourcesUserGroupSelected') {
                $state.go('app.privileges.usergroup', value);
            } else if (id === 'organizationDeleted') {
                $state.go('app.organizations');
            } else if (id === 'userDeleted') {
                $state.go('app.users');
            } else if (id === 'userGroupDeleted') {
                $state.go('app.usergroups');
            } else if (id === 'login') {
                $state.go('login');
            }
        }

        $scope.$on('$viewContentLoaded', function () {
            var isHidden = w2ui.acmlayout.get('left').hidden;
            var hasContent = $('#leftView').children().length > 0;
            if (hasContent) {
                if (isHidden) {
                    w2ui.acmlayout.show('left', true);
                }
            } else if (!isHidden) {
                w2ui.acmlayout.hide('left', true);
            }
        });

        $scope.$on('$destroy', function () {
            w2ui.acmlayout.destroy();
        });
    }
    function setUpAcmLayout(compile, scope) {
        setUpMainLayout();
        compileLayouts();

        function setUpMainLayout() {
            $('#acmlayout').w2layout({
                name: 'acmlayout',
                resizer: 8,
                padding: 0,
                panels: [
                    {
                        type: 'top',
                        size: 44,
                        overflow: 'visible',
                        content: '<acm-header></acm-header>'
                    },
                    {
                        type: 'left',
                        size: 500,
                        minSize: 120,
                        resizable: true,
                        content: '<div ui-view="leftView" class="acm-view" id="leftView"></div>'
                    },
                    {
                        type: 'main',
                        minSize: 500,
                        content: '<div ui-view="mainView" class="acm-view"></div>'
                    },
                    {
                        type: 'bottom',
                        size: 20,
                        overflow: 'hidden',
                        content: '<acm-footer></acm-footer>'
                    }
                ]
            });
        }

        function compileLayouts() {
            $(w2ui.acmlayout.el('left')).addClass('acmlayout_left');
            $(w2ui.acmlayout.el('main')).addClass('acmlayout_main');

            compile($(w2ui.acmlayout.el('top')).contents())(scope);
            compile($(w2ui.acmlayout.el('main')).contents())(scope);
            compile($(w2ui.acmlayout.el('left')).contents())(scope);
            compile($(w2ui.acmlayout.el('bottom')).contents())(scope);
        }
    }
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/core/messages.html',
    '<span ng-message="required">This field is required</span> <span ng-message="maxlength">This field is too long</span>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/footer/userInfo.html',
    '<style type="text/css">.userInfo-container {\n' +
    '	padding-left: 10px;\n' +
    '    text-decoration-line: underline;\n' +
    '    cursor: pointer;\n' +
    '	}</style><div class="userInfo-container" ng-click="vm.openUserProfile()">{{vm.getFooterText()}}</div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/header/header.html',
    '<flatirons-header config="vm.flatironsHeaderConfig"></flatirons-header>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/welcome/welcome.html',
    '<div class="center-block welcome"><h2>Welcome to Access Control Manager</h2><div><h3><strong>Please select one of the following on the menu bar:</strong></h3><br><h4><table><tr><td><i class="icon-person-gear"></i></td><td>Manage privileges</td></tr><tr><td><i class="icon-person"></i></td><td>Manage users</td></tr><tr><td><i class="icon-person-group"></i></td><td>Manage user groups</td></tr><tr><td><i class="icon-building"></i></td><td>Manage organizations</td></tr><tr><td><br></td></tr><tr ng-show="vm.appconfig.ppClient"><td><i class="icon-globe"></i></td><td>Pinpoint - Viewer</td></tr><tr ng-show="vm.appconfig.dmgrClient"><td><i class="icon-database-gear"></i></td><td>Data Manager</td></tr><tr ng-show="vm.appconfig.acmClient"><td><i class="icon-lock"></i></td><td>Access Control Manager</td></tr><tr ng-show="vm.appconfig.amClient"><td><i class="icon-chart"></i></td><td>Pinpoint - Audit Manager</td></tr><tr><td><br></td></tr><tr><td><i class="icon-gear"></i></td><td>Configuration (Permission Types, Authentication Provider, LDAP, SAML, Encryption)</td></tr><tr><td><i class="icon-book"></i></td><td>Online help</td></tr><tr ng-if="vm.isGuestSwitchAccountsAllowed"><td><i class="icon-arrow-box rotate-180"></i></td><td>Log in</td></tr><tr ng-if="!vm.isGuestFeatureEnabled && !vm.isGuestSwitchAccountsAllowed"><td><i class="icon-arrow-box"></i></td><td>Log out</td></tr></table></h4></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/certificates/certificateModal/certificateModal.html',
    '<div class="ui-widget"><div class="acm-ui-widget-header"><span class="title">Add certificate</span> <button id="btnSaveSelectCertificate" title="Save selection" ng-disabled="vm.certificateForm.$invalid " ng-click="vm.saveCertificate()"><span class="fa fa-check"></span></button> <button id="btnCancelSelectCertificate" title="Cancel selection" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div><div id="certificateModalMainContent" class="widget-content acm-view layout-content-div"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><form name="vm.certificateForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-3 acm-field-name">Certificate description</td><td ng-class="{ \'has-error\' : vm.certificateForm.certificateDescription.$invalid && !vm.certificateForm.$pristine }"><input class="form-control" required name="certificateDescription" type="text" ng-model="vm.certificate.description"></td></tr><tr><td class="col-md-3 acm-field-name">Certificate</td><td><textarea class="form-control" name="certificateValue" type="text" ng-model="vm.certificate.value" rows="22" style="resize: none">\n' +
    '                            </td>\n' +
    '                        </tr>\n' +
    '                    </table>\n' +
    '                </form>\n' +
    '            </div>\n' +
    '        </div>\n' +
    '    </div>\n' +
    '</div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/authenticationProvider/authProvConfiguration.html',
    '<div class="ui-widget"><layout-injector layoutname="authProvConfigurationLayout" topcontentid="authProvConfigurationHeaderContent" maincontentid="authProvConfigurationMainContent"></layout-injector><div id="authProvConfigurationHeaderContent" class="acm-ui-widget-header"><span class="title">Authentication Provider Configuration</span></div><div id="authProvConfigurationMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.authProvConfigurationForm" novalidate class="simple-form acm-details-form" title="{{vm.userPermissions.Write ? \'\' : \'No Write privilege on Authentication Provider\'}}"><table class="table"><tr><td class="col-md-2 acm-field-name"><strong>Authentication Provider</strong></td><td class="col-md-1"><label title="LDAP"><input type="radio" ng-model="vm.authProvider.value" ng-change="vm.save()" name="ldap" value="LDAP" checked ng-disabled="!vm.userPermissions.Write"> <span>LDAP</span></label></td><td class="col-md-9"><label title="SAML"><input type="radio" ng-model="vm.authProvider.value" ng-change="vm.save()" name="saml" value="SAML" ng-disabled="!vm.userPermissions.Write"> <span>SAML</span></label></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/configurationList/configurationList.html',
    '<div class="ui-widget"><layout-injector layoutname="configurationListLayout" topcontentid="configurationListHeaderContent" maincontentid="configurationListMainContent"></layout-injector><div id="configurationListHeaderContent"><div class="acm-ui-widget-header"><span class="title">Configuration</span></div></div><div id="configurationListMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><layout-injector layoutname="configurationListTableLayout" topcontentid="configurationListTableHeader" maincontentid="configurationListTableContent"></layout-injector><div id="configurationListTableHeader" class="layout-header-div"><table class="table table-hover"><thead><tr><th id="thConfigurationListName" class="col-md-12">Configuration</th></tr></thead></table></div><div id="configurationListTableContent" class="layout-content-div"><table id="ConfigurationListTable" class="table table-hover"><tr id="PermissionTypesRow" ng-click="vm.isDisabled(vm.permissionTypePath) || vm.selectConfiguration(\'permissiontypes\')" class="config-row" ng-disabled="vm.isDisabled(vm.permissionTypePath)" title="{{vm.isDisabled(vm.permissionTypePath) ? \'No Read privilege on Permission Types.\' : \'\'}}" ng-class="{selected: vm.selectedConfiguration == \'permissiontypes\'}"><td class="col-md-12">Permission Types</td></tr><tr id="AuthProvConfigurationRow" ng-click="vm.isDisabled(vm.authProviderPath) || vm.selectConfiguration(\'authProv\')" class="config-row" ng-disabled="vm.isDisabled(vm.authProviderPath)" title="{{vm.isDisabled(vm.authProviderPath) ? \'No Read privilege on Authentication Provider.\' : \'\'}}" ng-class="{selected: vm.selectedConfiguration  == \'authProv\'}"><td class="col-md-12">Authentication Provider Configuration</td></tr><tr id="LdapConfigurationRow" ng-click="vm.isDisabled(vm.ldapConfigPath) || vm.selectConfiguration(\'ldap\')" class="config-row" ng-disabled="vm.isDisabled(vm.ldapConfigPath)" title="{{vm.isDisabled(vm.ldapConfigPath) ? \'No Read privilege on LDAP Configuration.\' : \'\'}}" ng-class="{selected: vm.selectedConfiguration  == \'ldap\'}"><td class="col-md-12">LDAP Configuration</td></tr><tr id="SamlConfigurationRow" ng-click="vm.isDisabled(vm.samlConfigPath) || vm.selectConfiguration(\'saml\')" class="config-row" ng-disabled="vm.isDisabled(vm.samlConfigPath)" title="{{vm.isDisabled(vm.samlConfigPath) ? \'No Read privilege on SAML Configuration.\' : \'\'}}" ng-class="{selected: vm.selectedConfiguration  == \'saml\'}"><td class="col-md-12">SAML Configuration</td></tr><tr id="encryptionRow" ng-click="vm.isDisabled(vm.encryptionPath) || vm.selectConfiguration(\'encryption\')" class="config-row" ng-disabled="vm.isDisabled(vm.encryptionPath)" title="{{vm.isDisabled(vm.encryptionPath) ? \'No Read privilege on Encryption.\' : \'\'}}" ng-class="{selected: vm.selectedConfiguration  == \'encryption\'}"><td class="col-md-12">Encryption</td></tr></table></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/encryption/encryption.html',
    '<div class="ui-widget"><layout-injector layoutname="ldapConfigurationLayout" topcontentid="encryptionHeaderContent" maincontentid="encryptionMainContent"></layout-injector><div id="encryptionHeaderContent" class="acm-ui-widget-header"><span class="title">Encryption</span></div><div id="encryptionMainContent" class="widget-content"><div class="panel panel-body panel-default"><form name="vm.encryptionForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name">Input string</td><td><input class="form-control" placeholder="Enter string to be encrypted" name="inputString" type="text" ng-model="vm.inputString" ng-keypress="$event.keyCode == 13 && vm.encryptString()"></td><td class="col-md-2"><button class="button-align" id="btnEncryptString" ng-click="vm.encryptString()" title="Encrypt string"><span class="fa fa-lock"></span></button></td></tr><tr><td class="col-md-2 acm-field-name">RSA</td><td><input id="encryptedStringRSA" class="form-control" name="rsa" type="text" ng-model="vm.encryptedStringRSA"></td><td class="col-md-2"><button class="button-align copy-to-clipboard" readonly data-clipboard-target="#encryptedStringRSA" id="btnCopyEncryptedStringRSAToClipBoard" ng-click="vm.copyToClipBoard(vm.encryptedStringRSA)" title="Copy to clipboard"><span class="fa fa-clipboard"></span></button></td></tr><tr><td class="col-md-2 acm-field-name">Jasypt</td><td><input id="encryptedStringJasypt" class="form-control" name="jasypt" type="text" ng-model="vm.encryptedStringJasypt"></td><td class="col-md-2"><button class="button-align copy-to-clipboard" data-clipboard-target="#encryptedStringJasypt" id="btnCopyEncryptedStringJasyptToClipBoard" ng-click="vm.copyToClipBoard(vm.encryptedStringJasypt)" title="Copy to clipboard"><span class="fa fa-clipboard"></span></button></td></tr></table></form></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/ldapConfiguration/ldapConfiguration.html',
    '<div class="ui-widget"><layout-injector layoutname="ldapConfigurationLayout" topcontentid="ldapConfigurationHeaderContent" maincontentid="ldapConfigurationMainContent"></layout-injector><div id="ldapConfigurationHeaderContent" class="acm-ui-widget-header"><span class="title">LDAP Configuration</span> <button id="btnSynchronizeLDAPConfiguration" title="{{vm.syncBtnTitle}}" ng-click="vm.synchronize()" ng-disabled="!vm.userPermissions.Write || !vm.authProviderIsLDAP() || vm.isEditModeActivated"><span class="fa fa-refresh"></span></button> <button id="btnSaveLDAPConfiguration" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="vm.ldapConfigurationForm.$invalid || !vm.isEditModeActivated || vm.ldapConfigurationForm.$pristine" ng-click="vm.saveLDAPConfiguration()"><span class="fa fa-check"></span></button> <button id="btnEditLDAPConfiguration" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on LDAP configuration\'}}" ng-hide="vm.isEditModeActivated" ng-click="vm.toggleEdit()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-edit"></span></button> <button id="btnCancelLDAPConfiguration" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div><div id="ldapConfigurationMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.ldapConfigurationForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name"><strong>Scheme mapping class *</strong></td><td class="col-md-8" ng-class="{ \'has-error\' : !vm.ldapConfiguration.schemeMappingClass.length && vm.isEditModeActivated}"><input class="form-control" name="schemeMappingClass" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.ldapConfiguration.schemeMappingClass"><p class="help-block" ng-show="!vm.ldapConfiguration.schemeMappingClass.length">LDAP integration will not work without this value.</p></td><td class="col-md-2"></tr><tr><td class="col-md-2 acm-field-name">Organization Mapping</td><td><input class="form-control" type="text" name="organizationMapping" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.organizationMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Default organization</td><td><input class="form-control" type="button" name="organizationName" value="{{vm.ldapConfiguration.organizationName}}" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.organizationNcage" ng-click="vm.openOrganizationsModal()"></td></tr><tr><td class="col-md-2 acm-field-name">Start date</td><td ng-class="{ \'has-error\' : vm.ldapConfigurationForm.startDate.$invalid && vm.isEditModeActivated}"><input uib-datepicker-popup name="startDate" type="text" class="form-control" ng-disabled="!vm.isEditModeActivated" ng-change="vm.toggleDatepicker()" ng-model="vm.startDate" is-open="vm.datepicker.opened" min-date="vm.minDate" close-text="Close" placeholder="yyyy-mm-dd" maxlength="10"><p ng-show="vm.ldapConfigurationForm.startDate.$invalid" class="help-block">Please use the correct date format (yyyy-mm-dd).</p></td></tr><tr><td class="col-md-2 acm-field-name">Start time</td><td ng-class="{ \'has-error\' : vm.ldapConfigurationForm.startTime.$invalid && vm.isEditModeActivated}"><input class="form-control" name="startTime" ng-model="vm.ldapConfiguration.startTime" ng-disabled="!vm.isEditModeActivated" ng-pattern="/([01]{1}[0-9]|2[0-3]):[0-5][0-9]/" placeholder="hh:mm" maxlength="5"><p ng-show="vm.ldapConfigurationForm.startTime.$invalid" class="help-block">Please use the correct time format (hh:mm).</p></td></tr><tr><td class="col-md-2 acm-field-name">Interval</td><td><select type="text" class="form-control" name="interval" ng-model="vm.ldapConfiguration.interval" ng-disabled="!vm.isEditModeActivated"><option value=""></option><option value="3600000">Every hour</option><option value="7200000">Every second hour</option><option value="86400000">Every day</option><option value="172800000">Every second day</option><option value="604800000">Every week</option><option value="1209600000">Every second week</option></select></td></tr><tr><td class="col-md-2 acm-field-name">Delete users</td><td><select type="text" class="form-control" name="deletedUsers" ng-model="vm.ldapConfiguration.deletedUsers" ng-disabled="!vm.isEditModeActivated"><option value=""></option><option value="delete">Users who are deleted from LDAP will be removed from ACM</option><option value="disable">Users who are deleted from LDAP will be kept and disabled in ACM</option></select></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Base DN *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.baseDn.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="baseDn" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.baseDn"><p class="help-block" ng-show="!vm.ldapConfiguration.baseDn.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Group prefix *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.groupPrefix.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="groupPrefix" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.groupPrefix"><p class="help-block" ng-show="!vm.ldapConfiguration.groupPrefix.length">LDAP integration will not work without this value.</p></td></tr><tr><td id="secureLdapBox" class="col-md-2 acm-field-name"><strong>Secure LDAP</strong></td><td><input type="checkbox" name="secureLdap" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.secureLdap"></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Server port *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.serverPort.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="serverPort" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.serverPort"><p class="help-block" ng-show="!vm.ldapConfiguration.serverPort.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Server name FQDN *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.serverNameFQDN.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="serverNameFQDN" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.serverNameFQDN"><p class="help-block" ng-show="!vm.ldapConfiguration.serverNameFQDN.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Context factory *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.contextFactory.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="contextFactory" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.contextFactory"><p class="help-block" ng-show="!vm.ldapConfiguration.contextFactory.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Server authentication type *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.serverAuthType.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="serverAuthType" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.serverAuthType"><p class="help-block" ng-show="!vm.ldapConfiguration.serverAuthType.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Username *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.userName.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="userName" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.userName"><p class="help-block" ng-show="!vm.ldapConfiguration.userName.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Password *</strong></td><td ng-class="{ \'has-error\' : !vm.ldapConfiguration.password.length && vm.isEditModeActivated}"><input class="form-control" type="text" name="password" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.password"><p class="help-block" ng-show="!vm.ldapConfiguration.password.length">LDAP integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name">Highest committed USN</td><td><input class="form-control" type="text" name="highestCommittedUsn" ng-disabled="!vm.isEditModeActivated" ng-model="vm.ldapConfiguration.highestCommittedUsn"></td></tr><tr><td class="col-md-2 acm-field-name">Last synchronization</td><td><input class="form-control" type="text" name="lastSynchTime" ng-disabled="true" ng-model="vm.ldapConfiguration.lastSynchTime"></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/permissiontypes/permissionTypes.html',
    '<div class="ui-widget"><layout-injector layoutname="permissionTypesLayout" topcontentid="permissionTypesHeaderContent" maincontentid="permissionTypesMainContent"></layout-injector><div id="permissionTypesHeaderContent" class="acm-ui-widget-header"><span class="title">Permission Types</span></div><div id="permissionTypesMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.permissionTypesForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name">Add/Edit Permission Type</td><td><table class="table"><tr><td class="col-md-2 acm-field-name">Name</td><td><input class="form-control" onfocus="this.select()" ng-disabled="!vm.isEditing" autocomplete="off" id="permissionTypeInput" type="text" ng-model="vm.editorValue"></td></tr><tr><td class="col-md-2 acm-field-name">Scope</td><td><input class="form-control" ng-disabled="!vm.isEditing" autocomplete="off" id="permissionTypeScopeInput" type="text" ng-model="vm.editorScope"></td></tr></table></td><td><button id="btnCreateNewPermissionType" class="button-align" ng-disabled="!vm.userPermissions.Write || vm.permissionTypesForm.$dirty" title="Create" ng-click="vm.createNew()"><span class="fa fa-plus"></span></button> <button id="btnSavePermissionType" class="button-align" title="{{vm.userPermissions.Write ? \'Save\' : \'No write privilege on permission types\'}}" ng-disabled="!vm.isSaveable() || !vm.userPermissions.Write" ng-click="vm.savePermissionType()"><span class="fa fa-check"></span></button> <button id="btnCancelPermissionType" title="Cancel" class="button-align" ng-click="vm.cancel()" ng-disabled="!vm.isEditing"><span class="fa fa-remove"></span></button> <button id="btnDeletePermissionType" title="{{vm.userPermissions.Delete ? \'Delete\' : \'No delete privilege on permission types\'}}" class="button-align" ng-disabled="!vm.permissionType.name || !vm.userPermissions.Delete" ng-click="vm.deletePermissionType()"><span class="fa fa-trash"></span></button></td></tr><tr><td class="col-md-2 acm-field-name">Permission Types</td><td><select ng-disabled="permissionType.name != vm.editorValue" id="permissionTypesList" type="text" name="permissionTypes" size="10" ng-click="vm.selectPermissionType()"><option ng-repeat="permissionType in vm.permissionTypes | orderBy:\'name\'" value="{{permissionType.name}}">{{vm.getDescription(permissionType)}}</option></select></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/configuration/samlConfiguration/samlConfiguration.html',
    '<div class="ui-widget"><layout-injector layoutname="samlConfigurationLayout" topcontentid="samlConfigurationHeaderContent" maincontentid="samlConfigurationMainContent"></layout-injector><div id="samlConfigurationHeaderContent" class="acm-ui-widget-header"><span class="title">SAML Configuration</span> <button id="btnSaveSAMLConfiguration" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="!vm.isEditModeActivated || vm.samlConfigurationForm.$pristine" ng-click="vm.saveSAMLConfiguration()"><span class="fa fa-check"></span></button> <button id="btnEditSAMLConfiguration" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on SAML configuration\'}}" ng-hide="vm.isEditModeActivated" ng-click="vm.toggleEdit()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-edit"></span></button> <button id="btnCancelSAMLConfiguration" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div><div id="samlConfigurationMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.samlConfigurationForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name">Create missing user groups</td><td><input name="createUserGroups" ng-disabled="!vm.isEditModeActivated" type="checkbox" ng-model="vm.samlConfiguration.createUserGroups" title="Create all missing usergroups from SAML response on user login. This could create several unwanted groups in ACM."></td></tr><tr><td class="col-md-2 acm-field-name">Keep existing User Group Memberships</td><td><input name="keepExistingUserGroupMemberships" ng-disabled="!vm.isEditModeActivated" type="checkbox" ng-model="vm.samlConfiguration.keepExistingUserGroupMemberships" title="Keep exisitng User Group Memberships. If unchecked, the existing user groups will be removed."></td></tr><tr><td class="col-md-2 acm-field-name"><strong>SAML SSOS *</strong></td><td ng-class="{ \'has-error\' : !vm.samlConfiguration.samlsinglesignonservice.length && vm.isEditModeActivated}"><input class="form-control" name="samlSsos" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.samlsinglesignonservice"><p class="help-block" ng-show="!vm.samlConfiguration.samlsinglesignonservice.length">SAML integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name">Username mapping</td><td ng-class="{ \'has-error\' : !vm.samlConfiguration.usernameMapping.length && vm.isEditModeActivated}"><input class="form-control" name="userName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.usernameMapping"><p class="help-block" ng-show="!vm.samlConfiguration.usernameMapping.length">If this value is not mapped, ACM will use the subject nameID from the SAML response to create the username.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>First Name mapping *</strong></td><td ng-class="{ \'has-error\' : !vm.samlConfiguration.firstnameMapping.length && vm.isEditModeActivated}"><input class="form-control" name="firstName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.firstnameMapping"><p class="help-block" ng-show="!vm.samlConfiguration.firstnameMapping.length">SAML integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name">Middle Name mapping</td><td><input class="form-control" name="middleName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.middlenameMapping"></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Last Name mapping *</strong></td><td ng-class="{ \'has-error\' : !vm.samlConfiguration.lastnameMapping.length && vm.isEditModeActivated}"><input class="form-control" name="lastName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.lastnameMapping"><p class="help-block" ng-show="!vm.samlConfiguration.lastnameMapping.length">SAML integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>User group name mapping *</strong></td><td ng-class="{ \'has-error\' : !vm.samlConfiguration.usergroupnameMapping.length && vm.isEditModeActivated}"><input class="form-control" name="usergroupName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.usergroupnameMapping"><p class="help-block" ng-show="!vm.samlConfiguration.usergroupnameMapping.length">SAML integration will not work without this value.</p></td></tr><tr><td class="col-md-2 acm-field-name">Email address mapping</td><td><input class="form-control" name="emailAddress" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.emailMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Phone number mapping</td><td><input class="form-control" name="phoneNumber" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.phonenumberMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Organization name mapping</td><td><input class="form-control" name="organizationName" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.organizationnameMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Department mapping</td><td><input class="form-control" name="department" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.departmentMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Title mapping</td><td><input class="form-control" name="title" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.titleMapping"></td></tr><tr><td class="col-md-2 acm-field-name">Add User to groups only on</td><td><input class="form-control" name="addUserToGroupOn" ng-disabled="!vm.isEditModeActivated" type="text" ng-model="vm.samlConfiguration.addUserToGroupOn"></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Trusted certificates *</strong></td><td ng-class="{ \'has-error\' : vm.isEditModeActivated && !vm.samlConfiguration.certificates.length && vm.isEditModeActivated}"><select class="form-control" type="text" name="certificates" multiple ng-disabled="!vm.isEditModeActivated" id="certificateList" size="10" ng-click="vm.selectCertificate()"><option ng-repeat="certificate in vm.samlConfiguration.certificates | orderBy:\'description\'" value="{{certificate}}">{{certificate.description}}</option></select><p ng-show="!vm.samlConfiguration.certificates.length" class="help-block">SAML integration will not work without this value.</p></td><td class="col-md-2"><button id="btnEditCertificate" title="Edit" class="button-align" ng-disabled="!(vm.isEditModeActivated && (vm.selectedCertificates.length === 1))" ng-click="vm.openCertificateModal(vm.selectedCertificates[0])"><span class="fa fa-edit"></span></button> <button id="btnCreateNewCertificate" class="button-align" ng-disabled="!vm.isEditModeActivated" title="Create" ng-click="vm.openCertificateModal()"><span class="fa fa-plus"></span></button> <button id="btnDeleteCertificate" title="Delete" class="button-align" ng-disabled="!(vm.isEditModeActivated && (vm.selectedCertificates.length >= 1))" ng-click="vm.deleteCertificates()"><span class="fa fa-trash"></span></button></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/core/modal/deleteModal.html',
    '<div class="modal-header"><div><h4 class="modal-title">Delete Confirmation</h4></div></div><div class="modal-body"><p ng-show="vm.message">{{vm.message}}</p><div ng-show="vm.objectType && vm.objectsToBeDeleted"><p>The following {{vm.objectType}} will be deleted:</p><ul><li ng-repeat="objectToBeDeleted in vm.objectsToBeDeleted">{{objectToBeDeleted.name}}</li></ul></div></div><div class="modal-footer"><button id="btnDeleteModalOk" class="btn btn-danger" ng-click="vm.submit()">Delete</button> <button id="btnCancelModalOk" class="btn btn-default" ng-click="vm.cancel()">Cancel</button></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/core/modal/simpleModal.html',
    '<div class="modal-header"><div><h4 class="modal-title">Please Confirm</h4></div></div><div class="modal-body"><p ng-show="vm.message">{{vm.message}}</p></div><div class="modal-footer"><button id="btnOk" class="btn btn-danger" ng-click="vm.ok()">OK</button> <button id="btnCancel" class="btn btn-default" ng-click="vm.cancel()">Cancel</button></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/core/modal/userProfileInfoModal.html',
    '<style type="text/css">.modal-header {\n' +
    'background-color: #f8f8f8;\n' +
    'border-radius: 7px 7px 0px 0px;\n' +
    'background-image: url(assets/graphiclist-header-bg-icon.png);\n' +
    'background-repeat: no-repeat;\n' +
    'background-position: 10px 2px;\n' +
    'padding-left: 50px;\n' +
    'text-align: left;\n' +
    '}\n' +
    '\n' +
    '.modal-title {\n' +
    'font-weight: bold;\n' +
    '}\n' +
    '\n' +
    '.modal-body {\n' +
    'max-height: 600px;\n' +
    'overflow: auto;\n' +
    '}\n' +
    '\n' +
    '.close-button {\n' +
    'font-size: xx-large;\n' +
    'position: absolute;\n' +
    'right: 10px;\n' +
    'top: 5px;\n' +
    '}\n' +
    '\n' +
    '.capitalize {\n' +
    '    text-transform: capitalize;\n' +
    '}</style><div class="modal-header"><button class="close-button" type="button" ng-click="vm.close()" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title">About</h4></div><div class="modal-body"><div><table class="table table-striped table-hover fixed-table"><thead><tr style="border-style:hidden"><th class="column15">User ID</th><th class="column15">First/Last Name</th></tr><tr><td class="column15">{{vm.userInfo.sub}}</td><td class="column15 capitalize">{{vm.userInfo.firstname}} {{vm.userInfo.lastname}}</td></tr></thead><thead><tr><th class="column15">Group(s)</th><th class="column15">Role(s)</th></tr></thead><tbody style="overflow: auto"><tr ng-repeat="userInfodetails in vm.infoDetails track by $index" style="border-style:hidden"><td class="column15"><span class="capitalize">{{ vm.userGroups[$index]? vm.userGroups[$index].name:""}}</span><br><span>{{ vm.userGroups[$index]? vm.userGroups[$index].description:""}}</span></td><td class="column15"><span class="capitalize">{{ vm.userRoles[$index]?vm.userRoles[$index].name:""}}</span><br><span>{{ vm.userRoles[$index]? vm.userRoles[$index].description:""}}</span></td></tr></tbody></table></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/csv/upload/csvUpload.html',
    '<div class="ui-widget"><div flow-init="{testChunks: false, singleFile: true, chunkSize: 1000000000, allowDuplicateUploads: true}"><div flow-drop ng-show="!vm.uploading" flow-btn flow-btn-enabled="!vm.uploading" flow-drop-enabled="!vm.uploading" flow-files-submitted="vm.upload($files, $event, $flow)" flow-file-success="vm.success($file, $message)" flow-file-error="vm.error($file, $message, $flow)" flow-error="vm.error($file, $message, $flow)" flow-drag-enter="style={color: \'black\'}" flow-drag-leave="style={color: \'gray\'}" style="color: gray" ng-style="style"><div class="drop-zone"><div class="text-container"><strong>Click or Drop CSV File here</strong></div></div></div><div ng-show="vm.uploading" class="drop-zone"><div class="text-container"><strong class="upload-modal-text" ng-show="vm.uploading"><i class="fa fa-spinner fa-pulse"></i> Uploading file: {{vm.fileName}}</strong></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/organizations/organizationDetails/organizationDetails.html',
    '<div class="ui-widget" flow-prevent-drop><layout-injector layoutname="organizationDetailsLayout" topcontentid="organizationDetailsHeaderContent" maincontentid="organizationDetailsMainContent"></layout-injector><div id="organizationDetailsHeaderContent" class="acm-ui-widget-header"><span class="title">Organization Details</span><label id="labelCreateAnotherOrganization" ng-show="vm.isNew"><input id="inputCreateAnotherOrganization" type="checkbox" title="Create another" ng-model="vm.createAnother"> Create another</label><button id="btnSaveOrganization" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="vm.organizationDetailsForm.$invalid || !vm.isEditModeActivated || vm.organizationDetailsForm.$pristine" ng-click="vm.saveOrganization()"><span class="fa fa-check"></span></button> <button id="btnEditOrganization" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on organizations\'}}" ng-hide="vm.isEditModeActivated" ng-click="vm.toggleEdit()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-edit"></span></button> <button id="btnCancelOrganization" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button> <button id="btnDeleteOrganization" title="{{vm.userPermissions.Delete ? \'Delete\' : \'No delete privilege on organizations\'}}" ng-disabled="vm.isNew || vm.isEditModeActivated || !vm.userPermissions.Delete" ng-click="vm.deleteOrganization()"><span class="fa fa-trash"></span></button></div><div id="organizationDetailsMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.organizationDetailsForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name"><strong>Name *</strong></td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.orgName.$invalid && vm.isEditModeActivated}"><input class="form-control" name="orgName" type="text" required ng-maxlength="vm.dataModelProperties.nameSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.name"><p ng-show="vm.organizationDetailsForm.orgName.$error.maxlength" class="help-block">Name cannot exceed {{vm.dataModelProperties.nameSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Short Name</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.shortName.$invalid && vm.isEditModeActivated}"><input class="form-control" type="text" name="shortName" ng-maxlength="vm.dataModelProperties.shortNameSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.shortName"><p ng-show="vm.organizationDetailsForm.shortName.$error.maxlength" class="help-block">Short Name cannot exceed {{vm.dataModelProperties.shortNameSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>NCAGE *</strong></td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.ncage.$invalid && vm.isEditModeActivated}"><input class="form-control" ng-disabled="!vm.isNew || !vm.isEditModeActivated" name="ncage" type="text" required ng-minlength="5" ng-change="vm.checkNcageLength()" ng-model="vm.organization.ncage"><p ng-show="vm.organizationDetailsForm.ncage.$error.minlength || vm.organizationDetailsForm.ncage.$error.maxlength" class="help-block">NCAGE must be 5 characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Type</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.type.$invalid && vm.isEditModeActivated}"><select class="form-control" name="type" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.type"><option>VENDOR</option><option>CUSTOMER</option><option>OWNER</option><option>PARTNER</option></select></td></tr><tr><td class="col-md-2 acm-field-name">Track audits <span><i class="fa fa-info-circle track-audit-info" aria-hidden="true" title="Determine whether to track Organization events in Audit Manager."></i></span></td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.canTrackAudits.$invalid && vm.isEditModeActivated}"><input name="trackAuditscheckbox" type="checkbox" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.canTrackAudits" ng-checked="vm.organization.canTrackAudits" class="ng-pristine ng-untouched ng-valid ng-not-empty" disabled style=""></td></tr></table><strong>Organization logos</strong><table class="table"><tr><td class="col-md-2 acm-field-name">Full size logo</td><td><select-logo edit-mode="vm.isEditModeActivated" logo="vm.organization.fullSizeLogo" form="vm.organizationDetailsForm" height="44" width="250"></select-logo></td></tr><tr><td class="col-md-2 acm-field-name">Small logo</td><td><select-logo edit-mode="vm.isEditModeActivated" logo="vm.organization.smallLogo" form="vm.organizationDetailsForm" height="39" width="104"></select-logo></td></tr></table><strong>Address</strong><table class="table"><tr><td class="col-md-2 acm-field-name">Street</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.street.$invalid && vm.isEditModeActivated}"><input class="form-control" name="street" type="text" ng-maxlength="vm.dataModelProperties.streetSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.street"><p ng-show="vm.organizationDetailsForm.street.$error.maxlength" class="help-block">Street cannot exceed {{vm.dataModelProperties.streetSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">P.O Box</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.poBox.$invalid && vm.isEditModeActivated}"><input class="form-control" name="poBox" type="text" ng-maxlength="vm.dataModelProperties.poBoxSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.poBox"><p ng-show="vm.organizationDetailsForm.poBox.$error.maxlength" class="help-block">P.O Box cannot exceed {{vm.dataModelProperties.poBoxSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Zip</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.zipCode.$invalid && vm.isEditModeActivated}"><input class="form-control" name="zipCode" type="text" ng-maxlength="vm.dataModelProperties.zipCodeSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.zipCode"><p ng-show="vm.organizationDetailsForm.zipCode.$error.maxlength" class="help-block">Zip cannot exceed {{vm.dataModelProperties.zipCodeSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>City *</strong></td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.city.$invalid && vm.isEditModeActivated}"><input class="form-control" name="city" type="text" required ng-maxlength="vm.dataModelProperties.citySize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.city"><p ng-show="vm.organizationDetailsForm.city.$error.maxlength" class="help-block">City cannot exceed {{vm.dataModelProperties.citySize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name"><strong>Country *</strong></td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.country.$invalid && vm.isEditModeActivated}"><select class="form-control" name="country" type="text" required ng-maxlength="vm.dataModelProperties.countrySize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.country"><option ng-repeat="country in vm.countries" value="{{country.alpha2code}}">{{country.name}}</option></select><p ng-show="vm.organizationDetailsForm.country.$error.maxlength" class="help-block">Country cannot exceed {{vm.dataModelProperties.countrySize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">State</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.state.$invalid && vm.isEditModeActivated}"><input class="form-control" name="state" type="text" ng-maxlength="vm.dataModelProperties.stateSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.state"><p ng-show="vm.organizationDetailsForm.state.$error.maxlength" class="help-block">State cannot exceed {{vm.dataModelProperties.stateSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">County</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.county.$invalid && vm.isEditModeActivated}"><input class="form-control" name="county" type="text" ng-maxlength="vm.dataModelProperties.countySize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.county"><p ng-show="vm.organizationDetailsForm.county.$error.maxlength" class="help-block">County cannot exceed {{vm.dataModelProperties.countySize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Building</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.building.$invalid && vm.isEditModeActivated}"><input class="form-control" name="building" type="text" ng-maxlength="vm.dataModelProperties.buildingSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.building"><p ng-show="vm.organizationDetailsForm.building.$error.maxlength" class="help-block">Building cannot exceed {{vm.dataModelProperties.buildingSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Room</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.room.$invalid && vm.isEditModeActivated}"><input class="form-control" name="room" type="text" ng-maxlength="vm.dataModelProperties.roomSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.room"><p ng-show="vm.organizationDetailsForm.room.$error.maxlength" class="help-block">Room cannot exceed {{vm.dataModelProperties.roomSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Phone</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.phoneNumber.$invalid && vm.isEditModeActivated}"><input class="form-control" name="phoneNumber" type="text" ng-maxlength="vm.dataModelProperties.phoneNumberSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.phoneNumber"><p ng-show="vm.organizationDetailsForm.phoneNumber.$error.maxlength" class="help-block">Phone Number cannot exceed {{vm.dataModelProperties.phoneNumberSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Fax</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.faxNumber.$invalid && vm.isEditModeActivated}"><input class="form-control" name="faxNumber" type="text" ng-maxlength="vm.dataModelProperties.faxNumberSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.faxNumber"><p ng-show="vm.organizationDetailsForm.faxNumber.$error.maxlength" class="help-block">Fax Number cannot exceed {{vm.dataModelProperties.faxNumberSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">E-mail</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.email.$invalid && vm.isEditModeActivated}"><input class="form-control" name="email" type="email" class="form-control" ng-maxlength="vm.dataModelProperties.emailAddressSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.emailAddress"><p ng-show="vm.organizationDetailsForm.email.$error.email" class="help-block">Please enter a valid E-mail.</p><p ng-show="vm.organizationDetailsForm.email.$error.maxlength" class="help-block">E-mail cannot exceed {{vm.dataModelProperties.emailAddressSize}} characters.</p></td></tr><tr><td class="col-md-2 acm-field-name">Webpage</td><td ng-class="{ \'has-error\' : vm.organizationDetailsForm.internetAddress.$invalid && vm.isEditModeActivated}"><input class="form-control" name="internetAddress" type="text" ng-maxlength="vm.dataModelProperties.internetAddressSize" ng-disabled="!vm.isEditModeActivated" ng-model="vm.organization.internetAddress"><p ng-show="vm.organizationDetailsForm.internetAddress.$error.maxlength" class="help-block">Webpage cannot exceed {{vm.dataModelProperties.internetAddressSize}} characters.</p></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/organizations/organizationList/organizationList.html',
    '<div class="ui-widget"><layout-injector layoutname="organizationListLayout" topcontentid="organizationListHeaderContent" maincontentid="organizationListMainContent"></layout-injector><div id="organizationListHeaderContent"><div class="acm-ui-widget-header"><span class="title">Organizations</span> <button id="btnCancelSelectOrganization" ng-show="{{vm.modal}}" title="Cancel selection" ng-click="vm.modal.$dismiss()"><span class="fa fa-remove"></span></button> <button id="btnCreateNewOrganization" ng-show="{{!vm.modal}}" title="{{vm.userPermissions.Write ? \'Create new\' : \'No write privilege on organizations\'}}" ng-click="vm.createOrganization()" ng-disabled="vm.ncageSelectedOrganization === \'new\' || !vm.userPermissions.Write"><span class="fa fa-plus"></span></button></div></div><div id="organizationListMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><layout-injector layoutname="organizationListTableLayout" topcontentid="organizationsListTableHeader" maincontentid="organizationsListTableContent"></layout-injector><div id="organizationsListTableHeader" class="layout-header-div"><input id="txtOrganizationSearchBox" class="searchBox" placeholder="Search" ng-model="vm.searchText" ng-keypress="$event.keyCode == 13 && vm.retrieveOrganizations()"> <button id="btnSearchOrganization" ng-click="vm.retrieveOrganizations()"><span class="fa fa-search"></span></button><table class="table table-hover"><thead><tr><th id="thOrganizationListName" ng-click="vm.sort(\'name\')" class="col-md-6">Name <span ng-show="vm.orderBy === \'name\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thOrganizationListNcage" ng-click="vm.sort(\'ncage\')" class="col-md-3">NCAGE <span ng-show="vm.orderBy === \'ncage\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thOrganizationListType" ng-click="vm.sort(\'type\')" class="col-md-3">Type <span ng-show="vm.orderBy === \'type\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th></tr></thead></table></div><div id="organizationsListTableContent" class="layout-content-div"><table id="OrganizationListTable" class="table table-hover"><tr ng-repeat="organization in vm.organizations | filter:vm.search" ng-click="vm.selectOrganization(organization)" ng-class="{selected: organization.ncage === vm.ncageSelectedOrganization}"><td class="col-md-6">{{organization.name}}</td><td class="col-md-3">{{organization.ncage}}</td><td class="col-md-3">{{organization.type}}</td></tr></table><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveOrganizations()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/organizations/selectLogo/selectLogo.html',
    '<div flow-init="{singleFile: true}"><div ng-show="!vm.logo" class="flow-drop-wrapper" ng-class="vm.editMode ? \'flow-drop-wrapper-enabled\' : \'flow-drop-wrapper-disabled\'"><div ng-class="{\'flow-drop-disabled\': !vm.editMode}" class="flow-drop" flow-btn flow-drop flow-drag-enter="style={color: \'black\'}" flow-drag-leave="style={color: \'#666\'}" flow-files-submitted="vm.addLogo($flow, $files[0])" ng-style="style" flow-attrs="{accept:\'image/png, image/jpeg\'}"><span>Select or Drop File</span> <span class="logo-help-text">Minimum logo size is {{vm.width}} x {{vm.height}}px (keep aspect ratio)</span></div></div><div ng-show="vm.logo" class="logo-preview"><img class="logo-preview-img" ng-src="{{vm.logo}}" height="{{vm.height}}" width="{{vm.width}}" alt="Logo preview"> <button class="btn btn-default" ng-show="vm.editMode" title="Clear logo" ng-click="vm.clearLogo()"><span class="fa fa-remove"></span></button></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/privileges/privilegeDetails/privilegeDetails.html',
    '<div class="ui-widget" flatirons-loading-indicator="vm.applyPrivilegesPromise"><layout-injector layoutname="privilegeDetailsLayout" topcontentid="privilegeDetailsHeaderContent" maincontentid="privilegeDetailsMainContent"></layout-injector><div id="privilegeDetailsHeaderContent" class="acm-ui-widget-header"><span class="title">Privileges</span></div><div id="privilegeDetailsMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><layout-injector layoutname="privilegeDetailsMainContentLayout" topcontentid="privilegeResourceHeader" maincontentid="privilegeResourceContent"></layout-injector><div id="privilegeResourceHeader" class="layout-header-div privilege-resource-header"><input id="txtResourceSearchBox" ng-disabled="vm.isEditModeActivated" class="col-sm-11" placeholder="Search" ng-model="vm.resourceSearchText" ng-keypress="$event.keyCode == 13 && vm.resetTree()"> <button id="btnSearchResource" ng-disabled="vm.isEditModeActivated" class="col-sm-1 button-align" ng-click="vm.resetTree()"><span class="fa fa-search"></button><select id="schemeSelector" ng-disabled="vm.isEditModeActivated" name="options" class="col-sm-11" name="context" type="text" ng-model="vm.scheme" ng-change="vm.resetTree()"><option value="" default>Show all contexts</option><option ng-repeat="scheme in vm.schemes | orderBy:\'name\'" value="{{scheme.name}}">{{scheme.name}}</option></select><div id="privilegeResourceHeader2" class="privilege-resource-header2"><select id="permissionTypeSelector" ng-disabled="vm.isEditModeActivated" name="options" class="col-sm-11" name="context" type="text" ng-model="vm.selectedPermissionDisplayType" ng-change="vm.resetTree()"><option value="*" default>Show all</option><option ng-repeat="permissionType in vm.permissionDisplayTypes" value="{{permissionType.value}}">{{permissionType.name}}</option></select></div><hr style="clear: left"></div><div id="privilegeResourceContent" class="layout-content-div"><layout-injector layoutname="privilegeResourceLayout" maincontentid="resourceTree" rightcontentid="permissionTypes"></layout-injector><div id="resourceTree" class="layout-content-div"><div class="layout-content-div"><ul navigation-tree id="resourceNavigationTree" navigation-tree-delegate="vm.resourceTreeDelegate" nodes="vm.treeNodes" class="ztree"></ul></div></div><div id="permissionTypes" class="layout-content-div permission-types"><div><h4 class="col-md-8"><strong>Permissions</strong></h4><div class="col-md-4"><button id="btnSavePrivileges" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="!vm.isEditModeActivated || vm.saveInProgress" ng-click="vm.savePrivileges()"><span class="fa fa-check"></span></button> <button id="btnEditPrivileges" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on privileges\'}}" ng-hide="vm.isEditModeActivated" ng-disabled="!vm.userPermissions.Write" ng-click="vm.toggleEdit()"><span class="fa fa-edit"></span></button> <button id="btnCancelPrivileges" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()" ng-disabled="vm.saveInProgress"><span class="fa fa-remove"></span></button></div></div><hr style="clear: left"><div id="userGroups"><uib-tabset ng-hide="vm.currentGroupRole === \'User Roles\'" active="activeJustified" justified="true" class="custom-tab-style"><uib-tab class="tab-current" index="0" heading="Current Permissions" select="vm.permissionsSelect(\'current\')" deselect="vm.permissionsDeselect(\'current\')"></uib-tab><uib-tab class="tab-default" index="1" heading="Default Permissions" select="vm.permissionsSelect(\'default\')" deselect="vm.permissionsDeselect(\'default\')"></uib-tab></uib-tabset><div class="{{vm.isCurrentPermissions? \'current-permissions-content\' : \'default-permissions-content\'}} {{vm.currentGroupRole === \'User Roles\'? \'current-permissions-content-notabs\':\'\'}} permission-relative"><div class="{{vm.currentGroupRole === \'User Roles\'? \'content-offset-notabs\':\'content-offset\'}}"><div id="currentPermissions" class="permission-show"><div ng-repeat="permissionType in vm.permissionTypes"><label title="{{\n' +
    '                        !vm.isEditModeActivated ? \'Press Edit\' :\n' +
    '                        vm.selectedNode && vm.isSchemeNode ?\n' +
    '                        \'Permissions cannot be set on the context. Please choose another node.\' :\n' +
    '                        !vm.selectedNode ? \'Select a node\' : \'Set/clear permission\'\n' +
    '                                    }}"><input id="permissionTypeCheckbox{{permissionType}}" type="checkbox" ng-model="vm.selectedPermissionTypes[permissionType]" value="{{permissionType}}" ng-change="vm.selectPermissionType(permissionType)" ng-disabled="!vm.isPermissionsEditable() || vm.saveInProgress"> <span id="permissionType{{permissionType}}" ng-class="{changed: vm.hasPermissionTypeChanged(permissionType)}">{{permissionType}}</span> <a ng-click="vm.showGroupPrivilegeModal(permissionType,false)"><span id="permissionLink{{permissionType}}">({{permissionType == \'Read\'? vm.numberOfGroupsWithRead: (permissionType == \'Write\'? vm.numberOfGroupsWithWrite: (permissionType == \'Delete\'? vm.numberOfGroupsWithDelete: \'0\'))}})</span></a></label></div></div><div id="defaultPermissions" class="permission-hide"><div ng-repeat="permissionType in vm.permissionTypes"><label title="{{\n' +
    '                        !vm.isEditModeActivated ? \'Press Edit\' :\n' +
    '                        vm.selectedNode && vm.isSchemeNode ?\n' +
    '                        \'Permissions cannot be set on the context. Please choose another node.\' :\n' +
    '                        !vm.selectedNode ? \'Select a node\' : \'Set/clear permission\'\n' +
    '                                    }}"><input id="defaultPermissionTypeCheckbox{{permissionType}}" type="checkbox" ng-model="vm.selectedDefaultPermissionTypes[permissionType]" value="{{permissionType}}" ng-change="vm.selectDefaultPermissionType(permissionType)" ng-disabled="!vm.isPermissionsEditable() || vm.saveInProgress"> <span id="defaultPermissionType{{permissionType}}" ng-class="{changed: vm.hasDefaultPermissionTypeChanged(permissionType)}">{{permissionType}}</span> <a ng-click="vm.showGroupPrivilegeModal(permissionType,true)"><span id="defaultPermissionLink{{permissionType}}">({{permissionType == \'Read\'? vm.numberOfGroupsWithDefaultRead: (permissionType == \'Write\'? vm.numberOfGroupsWithDefaultWrite: (permissionType == \'Delete\'? vm.numberOfGroupsWithDefaultDelete: \'0\'))}})</span></a></label></div></div></div><hr ng-hide="!vm.isEditModeActivated || !vm.isCurrentPermissions" style="clear: left"><span ng-hide="!vm.isEditModeActivated || !vm.isCurrentPermissions" class="ng-hide permission-pad-left"><input type="checkbox" id="checkBoxApplyToDescendants" name="applyToDescendants" ng-model="vm.applyToDescendants" ng-change="vm.applyToDescendantsToggle()" ng-hide="!vm.isEditModeActivated" ng-disabled="!vm.isPermissionsEditable() || vm.saveInProgress" title="When checked, changed permissions will be applied to descendants of the current node. Apply to descendants must be checked before any permissions are changed in order for descendants to inherit the changes. Changed permissions have italic text format"> Apply to descendants</span><hr style="clear: left"><div ng-hide="!vm.isCurrentPermissions || vm.currentGroupRole === \'User Roles\'" class="permission-pad-bottom">Mode: Current Permissions - this mode is used to define the permissions for the currently selected node(s) and optionally its decendants.</div><div ng-hide="vm.isCurrentPermissions || vm.currentGroupRole === \'User Roles\'" class="permission-pad-left">Mode: Default Permissions - this mode does not set permissions for the selected node(s). This mode is used to define the default permissions assigned to any future descendants. These permissions will be used when a new node is created and can be individually overwritten if needed.</div></div></div></div></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/privileges/privilegeModal/groupPrivilegeModal.html',
    '<div class="ui-widget"><div id="groupPrivilegesModalHeaderContent"><div class="modal-header acm-ui-widget-header"><span class="title">Group(s) with {{vm.permissionType}} Privilege</span> <button id="btnCancelGroups" title="Cancel selection" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div></div><div id="groupPrivilegesModalMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="modal-body panel-body acm-view"><div id="groupPrivilegesModalTableHeader" class="layout-header-div"></div><div id="groupPrivilegesModalTableContent" class="layout-content-div" style="margin-top: 10px;height: 250px"><select multiple id="groupPrivilegesModalSelect" ng-multiple="true" type="text" name="groupsWithPrivilege" size="{{vm.limit}}" ng-click="" style="width: 100%;height: 100%;overflow: scroll"><option ng-repeat="group in vm.groupsWithPrivilege | filter:vm.search" value="{{group}}">{{group.displayName}}</option></select></div><div><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveGroupsWithPrivilege()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/usergroups/userGroupDetails/userGroupDetails.html',
    '<div class="ui-widget"><layout-injector layoutname="userGroupDetailsLayout" topcontentid="userGroupDetailsHeaderContent" maincontentid="userGroupDetailsMainContent"></layout-injector><div id="userGroupDetailsHeaderContent" class="acm-ui-widget-header"><span class="title">User {{userGroupType}} Details</span><label id="labelCreateAnotherUserGroup" ng-show="vm.isNew"><input id="inputCreateAnotherUserGroup" type="checkbox" title="Create another" ng-model="vm.createAnother"> Create another</label><button id="btnSaveUserGroup" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="vm.userGroupDetailsForm.$invalid || !vm.isEditModeActivated || vm.userGroupDetailsForm.$pristine" ng-click="vm.saveUserGroup()"><span class="fa fa-check"></span></button> <button id="btnEditOrganization" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on user groups\'}}" ng-hide="vm.isEditModeActivated" ng-click="vm.toggleEdit()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-edit"></span></button> <button id="btnCancelUserGroup" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button> <button id="btnDeleteUsergroup" title="{{vm.userPermissions.Delete ? \'Delete\' : \'No delete privilege on user groups\'}}" ng-disabled="vm.isNew || vm.isEditModeActivated || !vm.userPermissions.Delete" ng-click="vm.deleteUserGroup()"><span class="fa fa-trash"></span></button></div><div id="userGroupDetailsMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.userGroupDetailsForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-2 acm-field-name">Synchronized with LDAP</td><td ng-class="{ \'has-error\' : vm.userGroupDetailsForm.synchronizeCheckbox.$invalid}"><input name="synchronizeCheckbox" type="checkbox" ng-disabled="!vm.isEditModeActivated" ng-model="vm.userGroup.synchronize" ng-checked="vm.userGroup.synchronize"></td></tr><tr><td class="col-md-2 acm-field-name"><strong>{{userGroupType}} Name *</strong></td><td ng-class="{ \'has-error\' : vm.userGroupDetailsForm.userGroupName.$invalid && vm.isEditModeActivated}"><input class="form-control" required name="userGroupName" type="text" ng-disabled="!vm.isEditModeActivated" ng-model="vm.userGroup.name" ng-maxlength="vm.dataModelProperties.nameSize"></td></tr><tr><td class="col-md-2 acm-field-name">Description</td><td ng-class="{ \'has-error\' : vm.userGroupDetailsForm.userGroupDescription.$invalid && !vm.userGroupDetailsForm.$pristine }"><input class="form-control" type="text" name="userGroupDescription" ng-disabled="!vm.isEditModeActivated" ng-model="vm.userGroup.description" ng-maxlength="vm.dataModelProperties.descriptionSize"></td></tr><tr ng-show="vm.userInfo.ncage === \'SYS\'"><td class="col-md-2 acm-field-name"><strong>Organization *</strong></td><td ng-class="{ \'has-error\' : vm.userGroupDetailsForm.organizationName.$invalid && !vm.userGroupDetailsForm.$pristine }"><input class="form-control" ng-required="vm.userInfo.ncage === \'SYS\'" type="button" name="organizationName" value="{{vm.userGroup.organizationName}}" ng-disabled="!vm.isEditModeActivated" ng-model="vm.userGroup.ncage" ng-click="vm.openOrganizationsModal()"></td></tr><tr ng-show="vm.showMgr && vm.showManagersRow()"><td class="col-md-2 acm-field-name">Managers</td><td><select multiple id="mgrInGroupList" ng-multiple="true" type="text" name="usersInGroup" ng-click="vm.selectMgrs()"><option ng-repeat="member in vm.userGroupMembers.users | orderBy:\'name\'" ng-if="member.userRole == \'Manager\'" value="{{member}}">{{member.name}} ({{member.userName}})</option></select></td><td class="col-md-1"><button id="btnUnassignUsersRole" title="{{vm.isEditModeActivated ? \'Unassign User(s) Roll\' : \'Can only unassign role to user(s) in edit mode\'}}" class="button-align" ng-disabled="!(vm.isEditModeActivated && (vm.selectedMgrs.length >= 1))" ng-click="vm.unassignUsersRole()"><span class="fa fa-level-down"></span></button></td></tr><tr><td class="col-md-2 acm-field-name2">Users</td><td><select multiple id="userInGroupList" ng-multiple="true" type="text" name="usersInGroup" size="{{vm.limit}}" ng-click="vm.selectUsers()"><option ng-repeat="member in vm.userGroupMembers.users | orderBy:\'name\'" ng-if="!(member.userRole == \'Manager\' && vm.showManagersRow()) && member.isInactive == false" value="{{member}}">{{member.name}} ({{member.userName}})</option><option disabled ng-repeat="member in vm.userGroupMembers.users | orderBy:\'name\'" ng-if="!(member.userRole == \'Manager\' && vm.showManagersRow()) && member.isInactive == true" value="{{member}}">{{member.name}} ({{member.userName}}) Inactive</option></select><uib-pagination total-items="vm.userGroupMembers.totalSize" ng-change="vm.getUserGroupMembers()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></td><td class="col-md-1"><button id="btnAddNewUsers" class="button-align" ng-disabled="!vm.isEditModeActivated" title="{{vm.isEditModeActivated ? \'Add User(s)\' : \'Can only add user(s) in edit mode\'}}" ng-click="vm.openAddUser()"><span class="fa fa-user-plus"></span></button> <button id="btnDeleteUsers" title="{{vm.isEditModeActivated ? \'Remove User(s)\' : \'Can only remove user(s) in edit mode\'}}" class="button-align" ng-disabled="!(vm.isEditModeActivated && (vm.selectedUsers.length >= 1))" ng-click="vm.removeUsers()"><span class="fa fa-user-times"></span></button> <button id="btnAssignUsersRole" title="{{vm.isEditModeActivated ? \'Assign User(s) Roll\' : \'Can only assign role to user(s) in edit mode\'}}" class="button-align" ng-disabled="!(vm.isEditModeActivated && (vm.selectedUsers.length >= 1))" ng-show="vm.showMgr && vm.showManagersRow()" ng-click="vm.assignUsersRole()"><span class="fa fa-level-up"></span></button></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/usergroups/userGroupList/userGroupList.html',
    '<div class="ui-widget"><layout-injector layoutname="userGroupListLayout" topcontentid="userGroupListHeaderContent" maincontentid="userGroupListMainContent"></layout-injector><div id="userGroupListHeaderContent"><div class="acm-ui-widget-header"><div id="groupOrRoleHeader" class="group-or-role-header"><select id="groupOrRoleSelector" ng-disabled="false" class="select-group-role" name="groupOrRole" type="text" ng-model="vm.currentGroupRole" ng-change="vm.toggleGroupsRoles()"><option ng-repeat="groupOrRole in vm.groupOrRoleTypes" value="{{groupOrRole.value}}">{{groupOrRole.name}}</option></select></div><button id="btnUploadCSVFile" ng-show="{{vm.enableCreateNew}}" title="{{vm.userPermissions.Write ? \'Upload CSV file\' : \'No write privilege on user group\'}}" ng-click="vm.openCSVModal()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-upload"></span></button> <button id="btnCreateNewUserGroup" ng-show="{{vm.enableCreateNew}}" title="{{vm.userPermissions.Write ? \'Create new\' : \'No write privilege on user group\'}}" ng-click="vm.createUserGroup()" ng-disabled="vm.selectedUserGroupId === \'new\' || vm.currentGroupRole === \'Organizations\' || !vm.userPermissions.Write"><span class="fa fa-plus"></span></button></div></div><div id="userGroupListMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><layout-injector layoutname="userGroupListTableLayout" topcontentid="userGroupListTableHeader" maincontentid="userGroupListTableContent" rightcontentid="userGroupListSelectedContent" rightcontentsize="300" rightcontenthidden="true"></layout-injector><div id="userGroupListTableHeader" class="layout-header-div"><input id="txtUserGroupSearchBox" class="searchBox" placeholder="Search" ng-model="vm.searchText" ng-keypress="$event.keyCode == 13 && vm.retrieveUserGroups()"> <button id="btnSearchUserGroup" ng-click="vm.retrieveUserGroups()"><span class="fa fa-search"></span></button> <button id="btnToggleMultiSelect" ng-click="vm.toggleMultiSelect()" title="Select multiple groups"><span class="fa fa-list-alt"></span></button><table class="table table-hover"><thead><tr><th id="thUserGroupListName" ng-hide="vm.currentGroupRole === \'User Roles\'|| vm.currentGroupRole === vm.organizationResource" ng-click="vm.sort(\'name\')" class="col-md-2">User Groups <span id="caret" ng-show="vm.orderBy === \'name\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thUserRoleListName" ng-hide="vm.currentGroupRole === \'User Groups\'|| vm.currentGroupRole === vm.organizationResource" ng-click="vm.sort(\'name\')" class="col-md-2">User Roles <span id="caret" ng-show="vm.orderBy === \'name\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thOranizationListName" ng-hide="vm.currentGroupRole === \'User Groups\' || vm.currentGroupRole === \'User Roles\'" ng-click="vm.sort(\'name\')" class="col-md-2">Organizations <span id="caret" ng-show="vm.orderBy === \'name\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th></tr></thead></table></div><div id="userGroupListTableContent" class="layout-content-div"><table id="userGroupListTable" class="table table-hover"><tr ng-repeat="userGroup in vm.userGroups | filter:vm.search" ng-click="vm.selectUserGroup(userGroup)" ng-class="{selected: userGroup.userGroupId === vm.selectedUserGroupId}"><td class="col-md-2">{{userGroup.displayName}} <button class="pull-right copy-paste-padding-offset" ng-click="vm.pasteUserGroupPrivileges(userGroup)" ng-show="vm.isPrivileges" ng-disabled="vm.copiedUserGroup === null || vm.copiedUserGroup.userGroupId === userGroup.userGroupId || vm.copiedTargetUserGroup !== null" title="Paste" ng-class="vm.copiedTargetUserGroup.userGroupId === userGroup.userGroupId? \'fa fa-spinner\' : \'fa fa-paste\'"></button> <button class="pull-right copy-paste-padding-offset" ng-click="vm.copyUserGroupPrivileges(userGroup)" ng-show="vm.isPrivileges" title="Copy"><span class="fa fa-copy"></span></button></td></tr></table><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveUserGroups()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div><div id="userGroupListSelectedContent" class="layout-content-div"><div class="col-md-2"></div><div class="col-md-10"><h4><strong>Selections</strong></h4></div><div class="col-md-2"><button id="btnAddAllGroups" class="button-align" ng-click="vm.addAllGroups()"><span class="fa fa-angle-double-right"></span></button> <button id="btnAddGroup" class="button-align" ng-click="vm.addGroup()"><span class="fa fa-angle-right"></span></button> <button id="btnRemoveGroups" class="button-align" ng-click="vm.removeGroup()"><span class="fa fa-angle-left"></span></button> <button id="btnRemoveAllGroups" class="button-align" ng-click="vm.removeAllGroups()"><span class="fa fa-angle-double-left"></span></button></div><div class="col-md-10 group-selections"><select class="group-selections" multiple id="selectedGroupList" type="text" name="selectedGroupList" ng-click="" ng-model="vm.currentGroupListItem"><option ng-repeat="group in vm.selectedGroupList | orderBy:\'name\'" ng-value="{{group}}">{{group.displayName}}</option></select></div></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/usergroups/userGroupModal/userGroupModal.html',
    '<div class="ui-widget"><div id="groupModalHeaderContent"><div class="acm-ui-widget-header"><span class="title">Add User Group(s)</span> <button id="btnSaveSelectUserGroup" title="Save selection" ng-disabled="!(vm.groupNameSelectedUserGroups.length >= 1)" ng-click="vm.saveUserGroup()"><span class="fa fa-check"></span></button> <button id="btnCancelSelectUserGroup" title="Cancel selection" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div></div><div id="groupModalMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><div id="groupModalTableHeader" class="layout-header-div"><input id="txtUserGroupModalSearchBox" class="searchBox" placeholder="Search" ng-model="vm.searchText" ng-keypress="$event.keyCode == 13 && vm.retrieveUserGroups()"> <button id="btnSearchUserGroup" ng-click="vm.retrieveUserGroups()"><span class="fa fa-search"></span></button></div><div id="groupModalTableContent" class="layout-content-div" style="margin-top: 10px"><select multiple id="userGroupModalSelect" ng-multiple="true" type="text" name="userGroupModal" size="{{vm.limit}}" style="width: 80%"><option ng-repeat="group in vm.userGroups" value="{{group}}">{{group.name}}</option></select></div><div><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveUserGroups()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/users/userDetails/userDetails.html',
    '<div class="ui-widget"><layout-injector layoutname="userDetailsLayout" topcontentid="userDetailsHeaderContent" maincontentid="userDetailsMainContent"></layout-injector><div id="userDetailsHeaderContent" class="acm-ui-widget-header"><span class="title">User Details</span> <button id="btnSaveUser" title="{{vm.isEditModeActivated ? \'Save\' : \'Can only save in edit mode\'}}" ng-disabled="!vm.isEditModeActivated || vm.userDetailsForm.$pristine" ng-click="vm.saveUser()"><span class="fa fa-check"></span></button> <button id="btnEditUser" title="{{vm.userPermissions.Write ? \'Edit\' : \'No write privilege on users\'}}" ng-hide="vm.isEditModeActivated" ng-click="vm.toggleEdit()" ng-disabled="!vm.userPermissions.Write"><span class="fa fa-edit"></span></button> <button id="btnCancelUser" title="Cancel" ng-hide="!vm.isEditModeActivated" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button> <button id="btnDeleteUser" title="{{vm.userPermissions.Delete ? \'Delete\' : \'No delete privilege on user groups\'}}" ng-disabled="vm.isNew || vm.isEditModeActivated || !vm.userPermissions.Delete" ng-click="vm.deleteUser()"><span class="fa fa-trash"></span></button></div><div id="userDetailsMainContent" class="widget-content"><div class="panel panel-default"><div class="panel-body"><form name="vm.userDetailsForm" novalidate class="simple-form acm-details-form"><table class="table"><tr><td class="col-md-1 acm-field-name">Synchronized with LDAP</td><td style="text-align:right; vertical-align:middle"><input name="synchronizeCheckbox" type="checkbox" ng-disabled="!vm.isEditModeActivated" ng-model="vm.user.synchronize"></td><td></tr><tr><td class="col-md-1 acm-field-name">Inactive</td><td style="text-align:right; vertical-align:middle"><input name="inactiveCheckbox" type="checkbox" ng-disabled="!vm.isEditModeActivated" ng-model="vm.user.inactive"></td><td></tr><tr><td class="col-md-1 acm-field-name">Absent</td><td style="text-align:right; vertical-align:middle"><input name="absentCheckbox" type="checkbox" ng-disabled="!vm.isEditModeActivated" ng-model="vm.user.absent"></td><td><input class="form-control" name="absenceDetails" type="text" ng-disabled="!vm.isEditModeActivated" ng-model="vm.user.absenceDetails"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2"><strong>Username *</strong></td><td><input class="form-control" name="userName" type="text" ng-disabled="!vm.editable" ng-model="vm.user.userName"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2"><strong>First Name *</strong></td><td><input class="form-control" type="text" name="firstName" ng-disabled="!vm.editable" ng-model="vm.user.firstName"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2">Middle Name</td><td><input class="form-control" type="text" name="middleName" ng-disabled="!vm.editable" ng-model="vm.user.middleName"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2"><strong>Last Name *</strong></td><td><input class="form-control" type="text" name="lastName" ng-disabled="!vm.editable" ng-model="vm.user.lastName"></td></tr><tr ng-show="vm.userInfo.ncage === \'SYS\'"><td class="acm-field-name" colspan="2"><strong>Organization *</strong></td><td><input class="form-control" type="button" name="organizationName" value="{{vm.user.organizationName}}" ng-disabled="!vm.isEditModeActivated" ng-model="vm.user.organizationNcage" ng-click="vm.openOrganizationsModal()"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2">Department</td><td><input class="form-control" type="text" name="department" ng-disabled="!vm.editable" ng-model="vm.user.department"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2">Title</td><td><input class="form-control" type="text" name="title" ng-disabled="!vm.editable" ng-model="vm.user.title"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2">E-mail</td><td><input class="form-control" type="text" name="emailAddress" ng-disabled="!vm.editable" ng-model="vm.user.emailAddress"></td></tr><tr><td class="col-md-1 acm-field-name" colspan="2">Phone</td><td><input class="form-control" type="text" name="phoneNumber" ng-disabled="!vm.editable" ng-model="vm.user.phoneNumber"></td></tr><tr><td class="col-md-2 acm-field-name" colspan="2">User role(s)</td><td><select multiple id="userRoleList" ng-multiple="true" type="text" name="userRoles" size="5"><option ng-repeat="(key, value) in vm.userDisplayRoles | orderBy">{{value.name}}</option></select></td></tr><tr><td class="col-md-2 acm-field-name" colspan="2">User group(s)</td><td><select multiple id="userGroupList" ng-multiple="true" type="text" name="userGroups" size="5"><option ng-repeat="(key, value) in vm.userDisplayGroups | orderBy">{{value.name}}</option></select></td></tr></table><table class="table table-bordered" ng-if="vm.showGenerateSecretKey && vm.accessKeys.length > 0 "><tr><th id="keyLabel" style="text-align: center">KEY LABEL</th><th id="keyStatus" style="text-align: center">KEY STATUS</th><th id="keyExpirationDate" style="text-align: center">EXPIRATION DATE</th><th id="keyApprovedDate" style="text-align: center">APPROVAL DATE</th><th id="keyActions" class="col-md-2 acm-field-name" style="text-align: center" colspan="2">ACTIONS</th></tr><tr ng-repeat="accessKey in vm.accessKeys | orderBy:\'approvedDate\'"><td style="text-align: center">{{accessKey.userName}}</td><td style="text-align: center">{{accessKey.approvedDate != null ? \'Approved\' : \'In Progress\'}}</td><td style="text-align: center">{{accessKey.expiryDate}}</td><td style="text-align: center">{{accessKey.approvedDate}}</td><td style="text-align: center"><button id="btnDeleteAccessKey{{accessKey.hashKey}}" title="{{\'Delete\'}}" ng-disabled="vm.isNew" ng-click="vm.deleteAccessKey(accessKey)"><span class="fa fa-trash"></span></button></td><td style="text-align: center"><button id="btnSaveAccessKey{{accessKey.hashKey}}" title="{{accessKey.approvedDate == null ? \'Approve\' : \'Can only renewal\'}}" ng-hide="accessKey.approvedDate != null" ng-disabled="vm.enableApprovalBtn" ng-click="vm.updateAccessKey(accessKey)"><span class="fa fa-check-circle-o"></span></button> <button id="btnRenewalAccessKey{{accessKey.hashKey}}" title="{{accessKey.approvedDate != null ? \'Renewal\' : \'Can only approve\'}}" ng-hide="accessKey.approvedDate == null" ng-click="vm.updateAccessKey(accessKey)"><span class="fa fa-repeat"></span></button></td></tr></table></form></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/users/userList/userList.html',
    '<div class="ui-widget"><layout-injector layoutname="userListLayout" topcontentid="userListHeaderContent" maincontentid="userListMainContent"></layout-injector><div id="userListHeaderContent"><div class="acm-ui-widget-header"><span class="title">Users</span></div></div><div id="userListMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><layout-injector layoutname="userListTableLayout" topcontentid="userListTableHeader" maincontentid="userListTableContent"></layout-injector><div id="userListTableHeader" class="layout-header-div"><input id="txtUserSearchBox" class="searchBox" placeholder="Search" ng-model="vm.searchText" ng-keypress="$event.keyCode == 13 && vm.retrieveUsers()"> <button id="btnSearchUser" ng-click="vm.retrieveUsers()"><span class="fa fa-search"></span></button><table class="table table-hover"><thead><tr><th id="thUserListName" ng-click="vm.sort(\'name\')" class="col-md-5">Name <span ng-show="vm.orderBy === \'name\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thUserListUserName" ng-click="vm.sort(\'userName\')" class="col-md-3">Username <span ng-show="vm.orderBy === \'userName\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th><th id="thUserListOrganization" ng-click="vm.sort(\'organizationName\')" class="col-md-4">Organization <span ng-show="vm.orderBy === \'organizationName\'" ng-class="{\'dropup\': vm.sortAscending}"><span class="caret"></span></span></th></tr></thead></table></div><div id="userListTableContent" class="layout-content-div"><table id="userListTable" class="table table-hover"><tr ng-repeat="user in vm.users | filter:vm.search" ng-click="vm.selectUser(user)" ng-class="{selected: user.userName === vm.userNameSelectedUser}"><td class="col-md-5">{{user.name}}</td><td class="col-md-3">{{user.userName}}</td><td class="col-md-4">{{user.organizationName}}</td></tr></table><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveUsers()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/users/userModal/userModal.html',
    '<div class="ui-widget"><div id="userModalHeaderContent"><div class="acm-ui-widget-header"><span class="title">Add User(s)</span> <button id="btnSaveSelectUser" title="Save selection" ng-disabled="!(vm.userNameSelectedUser.length >= 1)" ng-click="vm.saveUser()"><span class="fa fa-check"></span></button> <button id="btnCancelSelectUser" title="Cancel selection" ng-click="vm.cancel()"><span class="fa fa-remove"></span></button></div></div><div id="userModalMainContent" class="widget-content acm-view"><div class="panel panel-default acm-view"><div class="panel-body acm-view"><div id="userModalTableHeader" class="layout-header-div"><input id="txtUserModalSearchBox" class="searchBox" placeholder="Search" ng-model="vm.searchText" ng-keypress="$event.keyCode == 13 && vm.retrieveUsers()"> <button id="btnSearchUser" ng-click="vm.retrieveUsers()"><span class="fa fa-search"></span></button></div><div id="userModalTableContent" class="layout-content-div layout-margin"><select multiple id="userModalSelect" ng-multiple="true" type="text" name="usersInGroup" size="{{vm.limit}}" ng-click="vm.selectUsers()"><option ng-repeat="user in vm.users | filter:vm.search" value="{{user}}">{{user.name}} ({{user.userName}}) {{user.organizationName}}</option></select></div><div><uib-pagination total-items="vm.totalSize" ng-change="vm.retrieveUsers()" ng-model="vm.currentPage" max-size="3" items-per-page="vm.limit" class="pagination-sm" boundary-links="true" rotate="false" direction-links="false" num-pages="numPages"></uib-pagination></div></div></div></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/acmloginwidget/template/login.html',
    '<style type="text/css">@font-face {\n' +
    '        font-family: \'ProximaNova-Regular\';\n' +
    '        src: url("assets/proximanova-regular-webfont.eot");\n' +
    '        src: url("assets/proximanova-regular-webfont.eot?#iefix") format("embedded-opentype"), url("assets/proximanova-regular-webfont.woff") format("woff"), url("assets/proximanova-regular-webfont.ttf") format("truetype"), url("assets/proximanova-regular-webfont.svg#proxima_nova_rgregular") format("svg");\n' +
    '    }\n' +
    '\n' +
    '    #login_page {\n' +
    '        background-image: url({{vm.background}});\n' +
    '    }\n' +
    '\n' +
    '    #login_page .bg-cloud {\n' +
    '        background-image: url({{vm.cloud}});\n' +
    '    }\n' +
    '\n' +
    '    /*\n' +
    '        product-name class name is not updated - but it will display the company logo.\n' +
    '    */\n' +
    '    #login_page .login_form h1 .product-name {\n' +
    '        background-image: url({{vm.companyLogo}});\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .copyright_logo {\n' +
    '        background-image: url({{vm.companyLogo}});\n' +
    '    }\n' +
    '\n' +
    '    #login_page {\n' +
    '        background-position: center, top;\n' +
    '        -webkit-background-size: cover;\n' +
    '        -moz-background-size: cover;\n' +
    '        background-size: cover;\n' +
    '        width: 100%;\n' +
    '        height: 100%;\n' +
    '        display: block;\n' +
    '        position: absolute;\n' +
    '        font-family: "ProximaNova-Regular";\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form {\n' +
    '        width: 500px;\n' +
    '        margin: 15% auto auto;\n' +
    '        padding: 15px;\n' +
    '        position: relative;\n' +
    '        background-image: url(assets/login/loginformbg.jpg);\n' +
    '        /* Styles */\n' +
    '        background-color: #ffffff;\n' +
    '        border-radius: 4px;\n' +
    '        color: #7e7975;\n' +
    '        box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2), 0 1px 5px rgba(0, 0, 0, 0.2), 0 0 0 12px rgba(255, 255, 255, 0.4);\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form h1 {\n' +
    '        font-size: 15px;\n' +
    '        font-weight: bold;\n' +
    '        color: #bdb5aa;\n' +
    '        padding-bottom: 8px;\n' +
    '        border-bottom: 1px solid #EBE6E2;\n' +
    '        text-shadow: 0 2px 0 rgba(255, 255, 255, 0.8);\n' +
    '        box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form h1 .log-in,\n' +
    '    #login_page .login_form h1 .sign-up {\n' +
    '        display: inline-block;\n' +
    '        text-transform: uppercase;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login-text-right {\n' +
    '        float: right;\n' +
    '        display: inline;\n' +
    '        margin-top: 15px;\n' +
    '    }\n' +
    '\n' +
    '    login_page .login-text-left {\n' +
    '        float: left;\n' +
    '        display: inline;\n' +
    '        margin-top: 15px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form h1 .log-in {\n' +
    '        color: #6c6763;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form h1 .sign-up {\n' +
    '        color: #5285B8;\n' +
    '        padding-left: 2px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form h1 .product-name {\n' +
    '        color: #6c6763;\n' +
    '        font-size: 28pt;\n' +
    '        display: inline-block;\n' +
    '        height: 36px;\n' +
    '        width: 150px;\n' +
    '        background-position: -12px -12px;\n' +
    '        background-size: cover;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .float {\n' +
    '        width: 50%;\n' +
    '        float: left;\n' +
    '        padding-top: 15px;\n' +
    '        border-top: 1px solid white;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .float:first-of-type {\n' +
    '        padding-right: 5px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .float:last-of-type {\n' +
    '        padding-left: 5px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form label {\n' +
    '        display: block;\n' +
    '        padding: 0 0 5px 2px;\n' +
    '        cursor: pointer;\n' +
    '        text-transform: uppercase;\n' +
    '        font-weight: 400;\n' +
    '        text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);\n' +
    '        font-size: 11px;\n' +
    '        width: auto;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form label i {\n' +
    '        margin-right: 5px;\n' +
    '        /* Gap between icon and text */\n' +
    '        display: inline-block;\n' +
    '        width: 10px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form input[type=text],\n' +
    '    #login_page .login_form input[type=password] {\n' +
    '        font-family: "ProximaNova-Regular";\n' +
    '        font-size: 13px;\n' +
    '        font-weight: 400;\n' +
    '        display: block;\n' +
    '        width: 100%;\n' +
    '        padding: 5px;\n' +
    '        margin-bottom: 5px;\n' +
    '        border: 3px solid #EBE6E2;\n' +
    '        border-radius: 5px;\n' +
    '        -webkit-transition: all 0.3s ease-out;\n' +
    '        -moz-transition: all 0.3s ease-out;\n' +
    '        -ms-transition: all 0.3s ease-out;\n' +
    '        -o-transition: all 0.3s ease-out;\n' +
    '        transition: all 0.3s ease-out;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form input[type=text]:hover,\n' +
    '    #login_page .login_form input[type=password]:hover {\n' +
    '        border-color: #CCC;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form label:hover ~ input {\n' +
    '        border-color: #CCC;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form input[type=text]:focus,\n' +
    '    #login_page .login_form input[type=password]:focus {\n' +
    '        border-color: #BBB;\n' +
    '        outline: none;\n' +
    '        /* Remove Chrome\'s outline */\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form button[type=submit],\n' +
    '    #login_page .login_form button[type=button],\n' +
    '    #login_page .login_form .log-twitter {\n' +
    '        /* Size and position */\n' +
    '        width: 49%;\n' +
    '        height: 38px;\n' +
    '        float: right;\n' +
    '        position: relative;\n' +
    '        /* Styles */\n' +
    '        box-shadow: inset 0 1px rgba(255, 255, 255, 0.3);\n' +
    '        border-radius: 3px;\n' +
    '        cursor: pointer;\n' +
    '        padding: 0px;\n' +
    '        /* Font styles */\n' +
    '        font-family: "ProximaNova-Regular";\n' +
    '        font-size: 14px;\n' +
    '        line-height: 38px;\n' +
    '        /* Same as height */\n' +
    '        text-align: center;\n' +
    '        font-weight: bold;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form button[type=submit],\n' +
    '    #login_page .login_form button[type=button] {\n' +
    '        margin-left: 1%;\n' +
    '        background: #6895C1;\n' +
    '        /* Fallback */\n' +
    '        background: -moz-linear-gradient(#6895C1, #5285B8);\n' +
    '        background: -ms-linear-gradient(#6895C1, #5285B8);\n' +
    '        background: -o-linear-gradient(#6895C1, #5285B8);\n' +
    '        background: -webkit-gradient(linear, 0 0, 0 100%, from(#6895C1), to(#5285B8));\n' +
    '        background: -webkit-linear-gradient(#6895C1, #5285B8);\n' +
    '        background: linear-gradient(#6895C1, #5285B8);\n' +
    '        border: 1px solid #0B83A4;\n' +
    '        color: #ffffff;\n' +
    '        text-shadow: 0 1px rgba(255, 255, 255, 0.3);\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form button[type=submit]:hover,\n' +
    '    #login_page .login_form button[type=button]:hover {\n' +
    '        box-shadow: inset 0 1px rgba(255, 255, 255, 0.3), inset 0 20px 40px rgba(255, 255, 255, 0.15);\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form button[type=submit]:active,\n' +
    '    #login_page .login_form button[type=button]:active,\n' +
    '    #login_page .login_form .log-twitter:active {\n' +
    '        top: 1px;\n' +
    '    }\n' +
    '\n' +
    '    /* Fallback fro broswers that don\'t support box shadows */\n' +
    '    #login_page .no-boxshadow .login_form button[type=submit]:hover,\n' +
    '    #login_page .no-boxshadow .login_form button[type=button]:hover {\n' +
    '        background: #5285B8;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .no-boxshadow .login_form {\n' +
    '        background: #2a8ac4;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form p:last-of-type {\n' +
    '        clear: both;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .opt {\n' +
    '        text-align: right;\n' +
    '        margin-right: 3px;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form label[for=showPassword] {\n' +
    '        display: inline-block;\n' +
    '        margin-bottom: 0px;\n' +
    '        font-size: 11px;\n' +
    '        font-weight: 400;\n' +
    '        text-transform: capitalize;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form input[type=checkbox] {\n' +
    '        vertical-align: middle;\n' +
    '        margin: -1px 5px 0 1px;\n' +
    '        width: auto;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .copyright {\n' +
    '        font-size: 6pt;\n' +
    '        text-align: right;\n' +
    '        margin: 0px;\n' +
    '        overflow: hidden;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .copyright_logo {\n' +
    '        display: inline-block;\n' +
    '        width: 100px;\n' +
    '        height: 30px;\n' +
    '        -webkit-background-size: cover;\n' +
    '        -moz-background-size: cover;\n' +
    '        background-size: cover;\n' +
    '        float: left;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .project_label, #login_page .login_form .project_select {\n' +
    '        display: inline-block;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .login_form .project_select {\n' +
    '        font-family: "ProximaNova-Regular";\n' +
    '        font-size: 13px;\n' +
    '        font-weight: 400;\n' +
    '    }\n' +
    '\n' +
    '    #login_page .cr-text {\n' +
    '        float: right;\n' +
    '        display: inline-block;\n' +
    '        height: 28px;\n' +
    '        padding-top: 8px;\n' +
    '    }\n' +
    '\n' +
    '    .showPasswordValue {\n' +
    '        float: right;\n' +
    '    }\n' +
    '    .errorMsg {\n' +
    '        color: red;\n' +
    '    }\n' +
    '\n' +
    '    .login_form button i{\n' +
    '        margin-top: 4px;\n' +
    '    }\n' +
    '\n' +
    '    @media screen and (max-height: 639px) {\n' +
    '        #login_page .login_form{\n' +
    '            margin-top: 10vh;\n' +
    '            max-height: 80vh;\n' +
    '            overflow: auto;\n' +
    '        }\n' +
    '    }\n' +
    '    @media screen and (max-width: 767px) {\n' +
    '        #login_page .login_form{\n' +
    '            width: 70% !important;\n' +
    '        }\n' +
    '        #btnLogin {\n' +
    '            width: 30% !important;\n' +
    '        }\n' +
    '    }</style><div ng-show="vm.showLogin" id="login_page" data-theme="b"><form name="vm.loginForm" class="login_form" id="login_form" flatirons-loading-indicator="vm.loginPromise"><h1><div><span class="product-name"></span><div class="test login-text-right"><span class="log-in"></span><span>&nbsp;</span><span class="sign-up">{{\'app.login.loginBtn\' | translate}}</span></div></div></h1><p class="float"><label for="username"><i class="fa fa-user"></i>{{\'app.login.username\' | translate}}</label><input type="text" id="username" name="username" placeholder="{{\'app.login.username\' | translate}}" ng-model="vm.userName" next-input-on-enter="passwordholder" autofocus autocapitalize="none" autocomplete="off" autocorrect="off"></p><p class="float" id="passwordholder"><label for="password"><i class="fa fa-lock"></i>{{\'app.login.password\' | translate}}</label><input type="password" id="password" name="password" placeholder="{{\'app.login.password\' | translate}}" class="showpassword" ng-keypress="$event.keyCode == 13 && vm.doLogin()" ng-model="vm.password" autocapitalize="none" autocomplete="off" autocorrect="off"><label class="showPasswordValue" value="{{\'app.login.showPassword\' | translate}}\'" hidden>{{\'app.login.showPassword\' | translate}}</label></p><p class="clearfix"><label for="languagei18n"><i class="fa fa-user"></i>{{\'app.language.selector\' | translate}}</label><select id="languagei18n" ng-model="vm.selectorValue" ng-change="vm.doChangeLanguage()"><option value="" style="display:none" selected disabled hidden></option><option value="{{\'app.language.en\' | translate}}" ng-model="vm.en">{{\'app.language.en\' | translate}}</option><option value="{{\'app.language.fr\' | translate}}" ng-model="vm.fr">{{\'app.language.fr\' | translate}}</option></select><label for="btnLogin"></label><button type="button" name="btnLogin" id="btnLogin" ng-click="vm.doLogin()"><span>{{\'app.login.loginBtn\' | translate}}</span></button> <button type="button" name="btnGuestLogin" id="btnGuestLogin" ng-click="vm.loginAsGuest()" ng-if="vm.guestlogin"><span>CONTINUE AS GUEST</span></button></p><div><label id="lblLoginMessage" class="errorMsg">{{vm.errorMessage}}</label></div><p class="copyright"><span class="cr-text">Copyright © 2024 Flatirons Solutions, Inc.</span></p></form></div><script type="text/javascript">$(function(){\n' +
    '    \'use strict\';\n' +
    '\n' +
    '    $(\'.showpassword\').each(function(index, input) {\n' +
    '        var $input = $(input);\n' +
    '        $(\'.showPasswordValue\').append(\n' +
    '            $(\'<input type="checkbox" class="showpasswordcheckbox" id="showPassword" />\').click(function() {\n' +
    '                var change = $(this).is(\':checked\') ? \'text\' : \'password\';\n' +
    '                var rep = $input\n' +
    '                    .attr(\'id\', $input.attr(\'id\'))\n' +
    '                    .attr(\'name\', $input.attr(\'name\'))\n' +
    '                    .attr(\'class\', $input.attr(\'class\'))\n' +
    '                    .attr(\'type\', change)\n' +
    '                    .val($input.val())\n' +
    '                    .insertBefore($input);\n' +
    '                $input = rep;\n' +
    '            })\n' +
    '        ).insertAfter($input.parent());\n' +
    '    });\n' +
    '\n' +
    '    $(\'#showPassword\').click(function(){\n' +
    '        if($(\'#showPassword\').is(\':checked\')) {\n' +
    '            $(\'.fa-lock\').addClass(\'fa-unlock\');\n' +
    '            $(\'.fa-unlock\').removeClass(\'fa-lock\');\n' +
    '        } else {\n' +
    '            $(\'.fa-unlock\').addClass(\'fa-lock\');\n' +
    '            $(\'.fa-lock\').removeClass(\'fa-unlock\');\n' +
    '        }\n' +
    '    });\n' +
    '});</script>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/flatironsfooterwidget/template/flatironsFooter.html',
    '<style type="text/css">.footer-container {\n' +
    '        height: 100%;\n' +
    '        background: #333333;\n' +
    '        color: #fff;\n' +
    '        text-align: center;\n' +
    '        padding-left: 10px;\n' +
    '        padding-right: 10px;\n' +
    '        font-size: 12px;\n' +
    '    }\n' +
    '    .custom-container {\n' +
    '        text-align: left;\n' +
    '        float: left;\n' +
    '        width: 33.33333%;\n' +
    '    }\n' +
    '    .copyright-container {\n' +
    '        text-align: right;\n' +
    '        float: left;\n' +
    '        width: 33.33333%;\n' +
    '    }\n' +
    '    .version-container {\n' +
    '        text-align: center;\n' +
    '        float: left;\n' +
    '        width: 33.33333%;\n' +
    '    }</style><div class="footer-container"><ng-transclude class="aligner-item custom-container"></ng-transclude><div class="aligner-item version-container" ng-attr-title="Build Time: {{vm.buildDate}}"><span ng-show="vm.versionLoaded">{{vm.product}} - {{vm.version}}</span></div><div class="aligner-item copyright-container"><img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDI2LjAuMywgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPgo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4IgoJIHZpZXdCb3g9IjAgMCAyNTYgMjU2IiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAyNTYgMjU2OyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+CjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+Cgkuc3Qwe2ZpbGw6I0ZGRkZGRjt9Cgkuc3Qxe2ZpbGwtcnVsZTpldmVub2RkO2NsaXAtcnVsZTpldmVub2RkO2ZpbGw6I0ZGRkZGRjt9Cjwvc3R5bGU+CjxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0yMDAuNCwxNTIuM2MtOC41LDM0LjMtMzcuOCw2MC4xLTc0LjgsNjAuMWMtNDQuOSwwLTc4LjEtMzYuNy03OC4xLTgwLjlzMzMuMi04MC45LDc4LjEtODAuOQoJYzE3LjUsMCwzMy4yLDYsNDUuOSwxNS43bDI4LjctMjhjLTIwLjItMTUuNS00Ni0yNC44LTc0LjktMjQuOGMtNjkuMiwwLTEyMC41LDUyLjYtMTIwLjUsMTE4YzAsNjUuNyw1MS4yLDExOCwxMjAuNSwxMTgKCWM2OS4yLDAsMTIwLjUtNTIuMywxMjAuNS0xMThjMC0xOC45LTQuNC0zNi43LTEyLjItNTIuNkwyMDAuNCwxNTIuM3oiLz4KPHBvbHlnb24gY2xhc3M9InN0MSIgcG9pbnRzPSI3NC45LDE4MC42IDE3My4zLDE4MC43IDI1MS4yLDggIi8+Cjwvc3ZnPgo=" style="width: 14px;height: 11px"> Copyright &#169 2024 Flatirons Solutions, Inc.</div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/flatironsheaderwidget/template/flatironsHeader.html',
    '<style type="text/css">.header-container {\n' +
    '        height: 100%;\n' +
    '        background: #333333;\n' +
    '        padding: 8px;\n' +
    '        display: -ms-flexbox;\n' +
    '        display: flex;\n' +
    '        flex-wrap: nowrap;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut button {\n' +
    '        -webkit-appearance: none;\n' +
    '        outline: none;\n' +
    '        border: 0;\n' +
    '        background: transparent;\n' +
    '        padding-right: 0;\n' +
    '        padding-left: 0;\n' +
    '        height: auto;\n' +
    '        width: 44px;\n' +
    '    }\n' +
    '\n' +
    '    .flatirons-header-icon i {\n' +
    '    vertical-align:middle;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-unlock-alt{\n' +
    '    height: 26px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-user{\n' +
    '    height: 30px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-users{\n' +
    '    height: 34px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-sitemap{\n' +
    '    height: 30px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-globe{\n' +
    '        height: 30px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-download{\n' +
    '    height: 26px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-lock{\n' +
    '    height: 26px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-bar-chart{\n' +
    '        height: 26px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-cogs{\n' +
    '    height: 34px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-question-circle{\n' +
    '    height: 30px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .fa-sign-out{\n' +
    '    height: 28px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut .icon-key{\n' +
    '    height: 32px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut button:disabled .flatirons-header-icon {\n' +
    '        color: #5B5C5D;\n' +
    '    }\n' +
    '\n' +
    '    .header-button-last {\n' +
    '        padding-right: 0;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcuts-container {\n' +
    '        margin-left: auto;\n' +
    '		position: absolute;\n' +
    '		right: 6px;\n' +
    '		top: 0px;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut {\n' +
    '        display: inline;\n' +
    '    }\n' +
    '\n' +
    '    .v-separator {\n' +
    '        background: #ccc;\n' +
    '        display: inline-block;\n' +
    '        height: 15px;\n' +
    '        width: 2px;\n' +
    '        margin-left: 5px;\n' +
    '        margin-right: 5px;\n' +
    '    }\n' +
    '\n' +
    '    .logo-link:active, .logo-link:focus {\n' +
    '        border: none;\n' +
    '        outline: none;\n' +
    '    }\n' +
    '\n' +
    '    .logo-img {\n' +
    '        width: 119px;\n' +
    '        height: 45px;\n' +
    '        margin: -8px;\n' +
    '    }\n' +
    '\n' +
    '    .flatirons-header-icon {\n' +
    '        font-size: 24px;\n' +
    '        color: #FFFFFF;\n' +
    '    }\n' +
    '\n' +
    '    .flatirons-header-icon:hover {\n' +
    '        color: #006EEE;\n' +
    '    }\n' +
    '\n' +
    '    .flatirons-header-current {\n' +
    '        color: #006EEE;\n' +
    '        cursor: default;\n' +
    '    }\n' +
    '\n' +
    '    .header-shortcut button.flatirons-top-border-current {\n' +
    '        border-top: 3px solid #006EEE;\n' +
    '    }\n' +
    '\n' +
    '    .header-modules-container {\n' +
    '        display: inline-block;\n' +
    '        background-color: rgba(0, 0, 0, 0.3);\n' +
    '        position: relative;\n' +
    '        height: 45px;\n' +
    '    }\n' +
    '\n' +
    '    .rotate-180 {\n' +
    '        transform: rotate(180deg);\n' +
    '        -ms-transform: rotate(180deg); /* IE 9 */\n' +
    '        -moz-transform: rotate(180deg); /* Firefox */\n' +
    '        -webkit-transform: rotate(180deg); /* Safari and Chrome */\n' +
    '        -o-transform: rotate(180deg); /* Opera */\n' +
    '        display: inline-block;\n' +
    '    }</style><nav class="header-container"><a class="logo-link" ui-sref="{{config.homeState}}" ui-sref-opts="{reload: true, inherit: false}" title="Home"><img ng-src="{{config.logoSrc}}" class="logo-img"></a><ng-transclude></ng-transclude><div class="header-shortcuts-container"><div class="header-shortcut" ng-repeat="shortcut in config.shortcuts"><button ng-hide="shortcut.hidden" ng-disabled="shortcut.disabled" ng-class="{\'header-button-last\':$last}" ng-click="shortcut.clickAction()" title="{{shortcut.name}}{{shortcut.tooltip}}"><span class="flatirons-header-icon"><i ng-class="class=\'{{shortcut.fontAwesomeClass ? \'fa \' + shortcut.fontAwesomeClass : shortcut.iconCssClass}}\'"></i></span></button></div><div class="header-modules-container"><div class="header-shortcut" ng-repeat="module in config.modules"><button ng-show="module.visible" ng-class="{\'header-button-last\':$last, \'flatirons-top-border-current\': module.isCurrentModule}" ng-click="module.clickAction()" title="{{module.name}}{{module.tooltip}}"><span ng-class="{\'flatirons-header-icon\': true, \'flatirons-header-current\': module.isCurrentModule}"><i ng-class="class=\'{{module.fontAwesomeClass ? \'fa \' + module.fontAwesomeClass : module.iconCssClass}}\'"></i></span></button></div></div><div class="header-shortcut" ng-repeat="common in config.common"><button ng-disabled="common.disabled" ng-class="{\'header-button-last\':$last}" ng-click="common.clickAction()" title="{{common.name}}{{common.tooltip}}"><span class="flatirons-header-icon"><i ng-class="class=\'{{common.fontAwesomeClass ? \'fa \' + common.fontAwesomeClass : common.iconCssClass}}\'"></i></span></button></div><div ng-if="config.guestAccessMode === \'guestAccess_withSwitchAccountsEnabled\'" class="header-shortcut flatirons-header-icon"><flatirons-logout icon-class="icon-arrow-box rotate-180" title="Log In"></flatirons-logout></div><div ng-if="!config.guestAccessMode" class="header-shortcut flatirons-header-icon"><flatirons-logout icon-class="icon-arrow-box" title="Log Out" click-action="config.logoutClickAction"></flatirons-logout></div></div></nav>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/flatironsloadingindicator/template/flatironsLoadingIndicator.html',
    '<style type="text/css">.flatirons-loading-indicator {\n' +
    '        position:absolute;\n' +
    '        top:0;\n' +
    '        left:0;\n' +
    '        right:0;\n' +
    '        bottom:0;\n' +
    '        z-index:1001;\n' +
    '        background-color:white;\n' +
    '        opacity:.7;\n' +
    '        text-align: center;\n' +
    '    }\n' +
    '\n' +
    '    .flatirons-loading-indicator .fa-spin {\n' +
    '        position: absolute;\n' +
    '        top: 40%;\n' +
    '        left: 50%;\n' +
    '        transform: translate(-50%, -50%);\n' +
    '    }</style><div ng-show="showLoading" class="flatirons-loading-indicator"><i class="fa fa-2x fa-circle-o-notch fa-spin"></i></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/flatironslogoutwidget/template/flatironsLogout.html',
    '<button id="btnLogout" ng-click="vm.doLogout()"><span class="flatirons-header-icon"><i ng-class="class=\'{{iconClass}}\'"></i></span></button>');
}]);
})();

(function(module) {
try {
  module = angular.module('app.widget.acm');
} catch (e) {
  module = angular.module('app.widget.acm', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('/templates/statuswidget/template/statusWidget.html',
    '<style type="text/css">.status-container {\n' +
    '	padding-left: 10px;\n' +
    '	}</style><div class="status-container">{{vm.status}}</div>');
}]);
})();
