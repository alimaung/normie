/**
 * @copyright (c) 2020 Flatirons Solutions Inc., All Rights Reserved.
 */

/**
 * ContextService
 * This service stores information about the current context of the application.
 * It is used to share state between widgets and reduce redundant information
 * coming from the server.
 **/
(function() {
    angular.module('app').service('ContextService', function() {

        var selectedNode;
        
        this.setSelectedNode = function(node) {
            selectedNode = node;
        };
        
        this.getSelectedNode = function() {
            return selectedNode;
        };
        
        this.getPublicationsInSelectedNode = function() {
            if(_.has(selectedNode, 'children')) {
                // The selected node has an array of children.
                // These children include libraries and publications.
                // We only want the publications, so filter out the libraries.
                var publications = selectedNode.children.filter(function(child) {
                    return !child.isParent;
                });
                
                var selectedNodeId = selectedNode.id;
                publications = publications.map(function(node) {
                    // We need to determine whether these publications are direct
                    // descendants of the currently selected node.
                    // If it is not, we will capture the name of the parent library.
                    if(node.pId !== selectedNodeId && _.has(node, 'getParentNode')) {
                        node.groupByLibraryTitle = node.getParentNode().name;
                    }
                    
                    return node;
                });
                
                return publications;
            } else {
                return [];
            }
        };
    });
})();