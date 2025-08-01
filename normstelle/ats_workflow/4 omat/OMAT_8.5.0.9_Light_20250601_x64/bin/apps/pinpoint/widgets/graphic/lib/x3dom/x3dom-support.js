//# sourceURL=x3dom-support.js
if (!String.prototype.startsWith) {
    String.prototype.startsWith = function (search, pos) {
        return this.substr(!pos || pos < 0 ? 0 : +pos, search.length) === search;
    };
}

function matchRuleShort(str, rule) {
	rule = rule.split("(").join("\\(");
	rule = rule.split(")").join("\\)");
    return new RegExp("^" + rule.split("*").join(".*") + "$").test(str);
}

function X3DSupport(x3dnode, X3DConfig, isLandingpage, allX3dConfigs) {
    this.resetX3DSupport = function (x3dnode, X3DConfig, isLandingpage, allX3dConfigs) {
        this.selectedObjects = null;
        this.highlightedObjects = null;
        this.highlightedObject = null;
        this.hiddenComponents = null;
        this.menuSelItem = null;
        this.focusNode = null;
        this.zoomStep = 0.15;
        this.x3dNode = x3dnode;
        this.centerX = 0;
        this.defMapping = null;
        this.x3DConfig = X3DConfig;
        if (this.x3DConfig)
            this.timeoutInterval = this.x3DConfig.timeoutInterval ? this.x3DConfig.timeoutInterval : 30000;
        this.DEFDomObjectMapping = {};
        this.defMapping = null;
        this.hiddenComponentsByRightClick = [];
        this.hiddenItemsToDisplay = [];
        this.historyFocusNode = [];
        this.lastMouseEvent = null;
        this.isLandingPage = isLandingpage;
        this.lastExplodeFactor = null;
        this.defaulttransparencyFactor = 0.9;
        this.selectedObject = [];
        this.parentNode = [];
		this.currentInlineNodes = 0;
        this.allX3dConfigData = allX3dConfigs || [];
        if (this.isLandingPage)
            this.createX3dLoadTimeout();
    };

    this.createX3dLoadTimeout = function () {
        this.isX3DLoaded = false;
        if (this.x3dTimeoutObject) {
            clearTimeout(this.x3dTimeoutObject);
        }
        this.x3dTimeout = function () {
            return setTimeout($.proxy(this.handleTimeout, this), this.timeoutInterval);
        };
        this.x3dTimeoutObject = this.x3dTimeout();
    };

    this.handleTimeout = function () {
        if (this.isX3DLoaded || $('.x3dom-progress').css('display') === "none") {
            clearTimeout(this.x3dTimeoutObject)
        } else {
            this.getX3DNode().scope().alertSlowNetwork(this.createX3dLoadTimeout, this.x3dTimeoutObject);
        }
    };

    this.handleX3DLoaded = function () {
        this.isX3DLoaded = true;
    };

    this.resetX3DSupport(x3dnode, X3DConfig, isLandingpage, allX3dConfigs);

    this.updateFromTocTree = function (nodeTitle, skipAddHistory, tocTree) {
        this.allX3dConfigData.some((element) => {
            let isElementFound = false;
            element.structure.some((value) => {
                if (value === nodeTitle) {
                    this.x3DConfig = element;
                    this.renderX3D(this.x3DConfig);
                    this.resetZoom();
                    isElementFound = true;
                }
            });
            return isElementFound;
        });
        if (!this.x3DConfig) {
            return;
        }
        var foundNode = this.recursiveFindNode(nodeTitle, this.x3DConfig.mapping);
        var self = this;
        this.renderAll();
        this.focusNode = null;
        this.activateView(null);
        this.defMapping = this.x3DConfig.mapping;
        this.getInlineNode().find("inline").attr("render", "false");
        if (!foundNode && tocTree) {
            var tocTreeWithTitle = [];
            // convert tocTree(zTree obj) to tocTreeWithTitle array
            if (tocTree.getParentNode) {
                while (tocTree && tocTree.getParentNode()) {
                    tocTreeWithTitle.unshift(tocTree.getParentNode().title);
                    tocTree = tocTree.getParentNode();
                }
                tocTree = tocTreeWithTitle;
            }
            for (var i = 0 ; i < tocTree.length; i++) {
                var foundNodeForTitle = this.recursiveFindNode(tocTree[i], this.x3DConfig.mapping);
                if (foundNodeForTitle) {
                    foundNode = foundNodeForTitle;
                    nodeTitle = tocTree[i];
                }
            }
        }

        if (!foundNode) {
            this.resetTransparency();
        } else {
            this.currentInlineNodes = this.initializeCurrentInlineNodes();
            $.each(foundNode, function (index, val) {
                if (val.x3dfile) {
                    return self.loadSubComponent(val.name, val).done(function () {
                        self.showOnlyInlineNode(val.inlineNode);
                        self.focusNode = val.inlineNode.parent()[0];
                        var mappedNode = [];
                        var nodes = self.getAllWithEqualStructure(nodeTitle, self.x3DConfig.mapping, mappedNode);
                        self.setAllToTransparent();
                        self.selectedObject = [];
                        for (element in nodes) {
                            $(nodes[element].matchedNode).find("Material").attr("transparency", 0);
                            self.selectedObject.push(nodes[element].matchedNode);
                        }
                    });
                }
            });
            if (foundNode.length <= 1) {
                var mappedNode = [];
                var nodes = self.getAllWithEqualStructure(nodeTitle, self.x3DConfig.mapping, mappedNode);
                self.setAllToTransparent();
                self.selectedObject = [];
                $(".goback-button").addClass("active").removeClass("reduce-opacity").removeClass("disabled");
                $(".goback-button").parent().css("pointer-events", "auto");
                for (element in nodes) {
                    $(nodes[element].matchedNode).find("Material").attr("transparency", 0);
                    self.selectedObject.push(nodes[element].matchedNode);
                }
            }

            if (!skipAddHistory && foundNode.length > 0 && !self.arrayContainsElement(self.historyFocusNode, foundNode.slice(-1)[0].matchedNode)) {
                self.historyFocusNode.push($(foundNode.slice(-1)[0].matchedNode));
                if (foundNode.length > 1) {
                    self.focusNode = foundNode.slice(0, -1).reverse()[0].matchedNode[0];
                }
            }
        }
        setTimeout(function (runtime) {
	        runtime.resetView();
			runtime.fitAll(true);		
        }, 10, this.getX3DRuntime());
    };

    this.setAllToTransparent = function () {
        if (this.transparencyFactor) {
            this.getX3DNode().find("Material").attr("transparency", this.transparencyFactor);
        } else {
            this.getX3DNode().find("Material").attr("transparency", this.defaulttransparencyFactor);
        }
    }

    if (this.isLandingPage) {
        getNodeClickBus().setCallback($.proxy(this.updateFromTocTree, this));
    }

    this.recursiveFindNode = function (nodeTitle, currentMapping) {
        var mappedNode = [];
        for (var property in currentMapping) {
            if (currentMapping.hasOwnProperty(property)) {
                var mapping = currentMapping[property];
                if (mapping.structure) {
                    var structure = mapping.structure;
                    var leafNode = structure[structure.length - 1];
                    if (nodeTitle === leafNode || nodeTitle === leafNode + " ") {
                        mappedNode.push(mapping);
                        return mappedNode;

                    }
                }
                if (mapping.mapping && mapping.x3dfile) {
                    var childMappedNode = this.recursiveFindNode(nodeTitle, mapping.mapping);
                    if (childMappedNode) {
                        mappedNode.push(mapping);
                        return mappedNode.concat(childMappedNode);
                    }
                }
            }
        }
    };

    this.getAllWithEqualStructure = function (nodeTitle, currentMapping, mappedNode) {
        for (var property in currentMapping) {
            if (currentMapping.hasOwnProperty(property)) {
                var mapping = currentMapping[property];
                if (mapping.structure) {
                    var structure = mapping.structure;
                    var leafNode = structure[structure.length - 1];
                    if (nodeTitle === leafNode || nodeTitle === leafNode + " ") {
                        mappedNode.push(mapping);

                    }
                }
                if (mapping.mapping && mapping.x3dfile) {
                    var childMappedNode = this.getAllWithEqualStructure(nodeTitle, mapping.mapping, mappedNode);
                }
            }
        }
        return mappedNode;
    };

    this.setSelectedObject = function (x3dnode, mappedObj, zoomTo) {
        var self = this;
        if (!x3dnode) {
            x3dnode = mappedObj.matchedNode;
        }
        var x3dShapes = $(x3dnode);
        if (!self.selectedObject || x3dnode !== self.selectedObject.shape) {
            this.resetSelected();
            var apperanceNodes = x3dShapes.find("appearance[use]");
            apperanceNodes.each(function () {
                var $this = $(this);
                var appearanceNode = $("appearance[def=" + $this.attr("use") + "]");
                $this.replaceWith(appearanceNode.clone());
            });
            var shapeNodes = x3dShapes.find("shape[use]");
            shapeNodes.each(function () {
                $this = $(this);
                var appearanceNode = $("shape[def=" + $this.attr("use") + "]");
                $this.replaceWith(appearanceNode.clone());
            });
            self.selectedObjects = x3dShapes.find("Material");
            self.selectedObjects.each(function () {
                self.saveOrigColors(this);
                this.setAttribute("emissiveColor", "0.8 1 0.8");
                this.setAttribute("diffuseColor", "0 0 0");
                this.setAttribute("specularColor", "0 0 0");
            });
            self.selectedObject = [];
            self.selectedObject.push(mappedObj);
            if (zoomTo && zoomTo === true && x3dShapes.length > 0) {
                this.getX3DRuntime().fitObject(x3dShapes[0]);
            }
        }
    };

    this.handleRightClickSearch = function (shape) {
        var mappedObj = this.findMappedNode(shape);
        var searchCriteria = "";
        if (mappedObj.mapping && mappedObj.mapping.pnr) {
            searchCriteria = mappedObj.mapping.pnr;
        } else {
            searchCriteria = this.getNodeID(shape);
            if (!searchCriteria) {
                searchCriteria = this.getNodeID(shape.parentNode);
            }
        }
        if ($('[ng-model="searchInput"]').is(":visible")) {
            angular.element('[ng-model="searchInput"]').scope().searchInput = searchCriteria;
            $("span[ng-click='searchAction()']").click();
        }

    };

    this.findCenterX = function (translateNodes) {
        var minX = 100000;
        var maxX = -100000;
        this.getX3DRuntime().canvas.doc._scene.updateVolume();
        translateNodes.each(function (index, node) {
            if (node._x3domNode && node._x3domNode.getVolume) {
                var vol = node._x3domNode.getVolume();
                if (vol) {
                    if (vol.min.x < minX) {
                        minX = vol.min.x;
                    }
                    if (vol.max.x > maxX) {
                        maxX = vol.max.x;
                    }
                }
            }
        });
        return (maxX + minX) / 2;
    };

    this.findCenterY = function (translateNodes) {
        var minY = 100000;
        var maxY = -100000;
        this.getX3DRuntime().canvas.doc._scene.updateVolume();
        translateNodes.each(function (index, node) {
            if (node._x3domNode && node._x3domNode.getVolume) {
                var vol = node._x3domNode.getVolume();
                if (vol) {
                    if (vol.min.y < minY) {
                        minY = vol.min.y;
                    }
                    if (vol.max.y > maxY) {
                        maxY = vol.max.y;
                    }
                }
            }
        });
        return (maxY + minY) / 2;
    };

    this.findCenterZ = function (translateNodes) {
        var minZ = 100000;
        var maxZ = -100000;
        this.getX3DRuntime().canvas.doc._scene.updateVolume();
        translateNodes.each(function (index, node) {
            if (node._x3domNode && node._x3domNode.getVolume) {
                var vol = node._x3domNode.getVolume();
                if (vol) {
                    if (vol.min.z < minZ) {
                        minZ = vol.min.z;
                    }
                    if (vol.max.z > maxZ) {
                        maxZ = vol.max.z;
                    }
                }
            }
        });
        return (maxZ + minZ) / 2;
    };

    this.findTopNodes = function (fromNode) {
        var childNodes = fromNode.children("transform, group, cadlayer, cadassembly, Transform, Group, CADLayer, CADAssembly");

        if (childNodes.length < 3 && childNodes.length > 0) {
            var subChildNodes = this.findTopNodes(childNodes);
            if (subChildNodes.length > 2) {
                childNodes = subChildNodes;
            }
        }
        return childNodes;
    };
    this.findOrCreateTranslateNodes = function (childNodes) {
        var promise = $.Deferred();
        var translateNodes = $([]);
        var self = this;
        childNodes.each(function (index, node) {
            if (!self.getX3DRuntime().isA(node, 'Transform')) {
                var transform = $("<Transform/>", node.document);
                var keep = node._x3domNode;
                node._x3domNode = null;
                transform.insertAfter(node);
                $(node).appendTo(transform);
                node._x3domNode = keep;
                translateNodes = translateNodes.add(transform);
            } else {
                translateNodes = translateNodes.add($(node));
            }
        });
        // Delay 10ms to allow X3D to refresh
        setTimeout(function () {
            promise.resolve(translateNodes);
        }, 10);
        return promise;
    };
    this.explode = function (factor) {
        var inlineNode = this.focusNode ? $(this.focusNode).find("inline:first") : this.getInlineNode();
        var childNodes = this.findTopNodes(inlineNode);
        var self = this;
        if (childNodes && childNodes.length === 0) {
            return;
        }
        this.findOrCreateTranslateNodes(childNodes).then(function (translateNodes) {
            if (!inlineNode.centerX || inlineNode.centerX === 0) {
                inlineNode.centerX = self.findCenterX(translateNodes);
            }

            if (!inlineNode.centerY || inlineNode.centerY === 0) {
                inlineNode.centerY = self.findCenterY(translateNodes);
            }

            if (!inlineNode.centerZ || inlineNode.centerZ === 0) {
                inlineNode.centerZ = self.findCenterZ(translateNodes);
            }
            return translateNodes;
        }).then(function (translateNodes) {
            translateNodes.each(function (index, node) {
                if (node && node.requestFieldRef) {
                    var field = node.requestFieldRef('translation');
                    var vol = node._x3domNode.getVolume();
                    if (!$(node).data("origTranslate")) {
                        $(node).data("origTranslate", field.copy());
                        node.distanceFromCenterX = Math.abs(vol.center.x - inlineNode.centerX);
                        node.distanceFromCenterY = Math.abs(vol.center.y - inlineNode.centerY);
                        node.distanceFromCenterZ = Math.abs(vol.center.z - inlineNode.centerZ);
                    } else {
                        field.setValues($(node).data("origTranslate"));
                    }

                    var distance = (node.distanceFromCenterX / 2) * factor;
                    if (vol.center.x > inlineNode.centerX) {
                        field.x = field.x + distance;
                    } else if (vol.center.x < inlineNode.centerX) {
                        field.x = field.x - distance;
                    }

                    var distanceY = (node.distanceFromCenterY / 2) * factor;
                    if (vol.center.y > inlineNode.centerY) {
                        field.y = field.y + distanceY;
                    } else if (vol.center.y < inlineNode.centerY) {
                        field.y = field.y - distanceY;
                    }

                    var distanceZ = (node.distanceFromCenterZ / 2) * factor;
                    if (vol.center.z > inlineNode.centerZ) {
                        field.z = field.z + distanceZ;
                    } else if (vol.center.z < inlineNode.centerZ) {
                        field.z = field.z - distanceZ;
                    }

                    node.releaseFieldRef('translation');
                }
            });
            return translateNodes;
        }).then(function (translateNodes) {
            self.centerOnNode(self.focusNode);
            self.lastExplodeFactor = factor;
        });
    };

    //Override resetExplode, resetZoom and resetTransparency to set correct scope id for selector
    this.resetExplode = function () {
        this.explode(0);
        $("#explodeSld_" + self.scope.id).bootstrapSlider('setValue', 0);
    };
    this.resetZoom = function () {
        if (this.origFieldOfView && this.getX3DRuntime().viewpoint()._xmlNode) {
            this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", this.origFieldOfView);
            $("#zoomSld").bootstrapSlider('setValue', 0);
        }
    };
    this.resetTransparency = function () {
        this.selectedObject = null;
        this.transparency(null);
    }

    this.resetTransparencyAndSlider = function() {
        this.resetTransparency();
        $("#transSld_" + self.scope.id).bootstrapSlider('setValue', 0.9);
    }

    this.dumpObjectsX = function (indent, recursiveLevel, node) {
        var children = $(node).children();
        var self = this;
        children.each(function (index, childNode) {
            if (recursiveLevel < 3) {
                self.dumpObjectsX(indent + "  ", recursiveLevel + 1, childNode);
            }
        });
    };
    this.dumpObjectsY = function (indent, recursiveLevel, node) {
        var children = $(node).children();
        var self = this;
        children.each(function (index, childNode) {
            if (recursiveLevel < 3) {
                self.dumpObjectsY(indent + "  ", recursiveLevel + 1, childNode);
            }
        });
    };
    this.dumpObjectsZ = function (indent, recursiveLevel, node) {
        var children = $(node).children();
        var self = this;
        children.each(function (index, childNode) {
            if (recursiveLevel < 3) {
                self.dumpObjectsZ(indent + "  ", recursiveLevel + 1, childNode);
            }
        });
    };

    this.zoomIn = function () {
        var fieldOfView = parseFloat(this.getX3DRuntime().viewpoint().getFieldOfView());
        this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", fieldOfView - this.zoomStep);
    };

    this.zoomOut = function () {
        var fieldOfView = parseFloat(this.getX3DRuntime().viewpoint().getFieldOfView());
        this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", fieldOfView + this.zoomStep);
    };
    this.zoom = function (steps) {
        this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", this.origFieldOfView - (this.zoomStep * steps));
    };
    this.activateView = function (viewpointNode) {
        var currBind = this.getX3DRuntime().getActiveBindable('viewpoint');
        if (currBind) {
            currBind.setAttribute('set_bind', 'false');
        }
        if (!viewpointNode) {
            viewpointNode = this.getX3DNode().find("Viewpoint[def='default'], viewpoint[def='default'], viewpoint[description=\'default\'], Viewpoint[description='default']");
        }
        $(viewpointNode).attr('set_bind', 'true');

        var inlineNode = $(viewpointNode).parentsUntil(this.getX3DNode(), 'inline');
        if (inlineNode.length === 0) {
            inlineNode = this.getInlineNode();
        }
        this.centerOnNode(inlineNode[0]);
        this.getX3DRuntime().resetView();

    };
    this.centerOnNode = function (node) {
        if (node) {
            this.getX3DRuntime().canvas.doc._scene.updateVolume();
            var center = node._x3domNode.getVolume().center;
            var view = $(this.getX3DRuntime().viewpoint()._xmlNode);
            view.attr("centerOfRotation", center.x + " " + center.y + " " + center.z);
        }
    };
    this.getOrgEvent = function (event) {
        var orgEvent;
        if (event.originalEvent) {
            orgEvent = event.originalEvent;
        } else if (event.srcEvent) {
            orgEvent = event.srcEvent;
            if (!orgEvent.clientX) {
                orgEvent.clientX = event.center.x;
                orgEvent.clientY = event.center.y;
            }
        } else {
            orgEvent = $.event.fix(event || window.event);
        }
        this.lastMouseEvent = orgEvent;
        return orgEvent;
    };
    this.onComponentSelect = function (event, mapping) {
        //Override this method, to get other select behaviour;
        if (mapping.structure) {
            this.openTocNode(mapping.structure);
        }
    };
    this.onTopModelLoaded = function (mapping) {
        //Override this method, to handle the onload of top model
    };
    //Handle click on a shape
    this.handleCompClick = function (event) {
        var shape = this.getShapeFromMousePos(event);


        var mappedOjb = this.findMappedNode(shape);
        var mapping = mappedOjb.mapping;
        var currShape = mappedOjb.shape;

        this.resetOutline();

        if (mapping) {
            this.onComponentSelect(event, mapping);
            shape = currShape;
        }
        var self = this;
        if (shape) {
            //this.setSelectedObject(shape, mappedOjb, false);
            this.selectedObject = [];
            this.selectedObject.push(shape);
            this.setAllToTransparent();
            $(shape).find("Material").attr("transparency", 0);
        } else {
            this.resetTransparency();
        }
    };

    this.saveOrigColors = function (node) {
        if (!$(node).data("prevEmissiveColor")) {
            $(node).data("prevEmissiveColor", node.getAttribute("emissiveColor"));
            $(node).data("prevDiffuseColor", node.getAttribute("diffuseColor"));
            $(node).data("prevSpecularColor", node.getAttribute("specularColor"));
        }
    };
    this.restoreOrigColors = function (node) {
        node.setAttribute("emissiveColor", $(node).data("prevEmissiveColor"));
        node.setAttribute("diffuseColor", $(node).data("prevDiffuseColor"));
        node.setAttribute("specularColor", $(node).data("prevSpecularColor"));
    };

    this.getShapeFromMousePos = function (event) {
        var orgEvent = this.getOrgEvent(event);

        var pos = this.getX3DRuntime().mousePosition(orgEvent, 0);

        var shape = this.getX3DRuntime().pickRect(pos[0], pos[1], pos[0], pos[1])[0];
        return shape;
    };

    this.highlighObject = function (x3dNode) {
        this.saveOrigColors(x3dNode);
        x3dNode.setAttribute("emissiveColor", "0.7 0.7 1");
        x3dNode.setAttribute("diffuseColor", "0 0 0");
        x3dNode.setAttribute("specularColor", "0 0 0");
    };

    //Handle click on a shape
    this.handleMouseOver = function (event) {
        var self = this;
        var shape = this.getShapeFromMousePos(event);

        if (shape) {
            try {
                var mappedOjb = this.findMappedNode(shape);
                var currShape = mappedOjb.shape;

                if (this.highlightedObject === null || currShape !== this.highlightedObject.shape) {
                    this.resetOutline();
                    if (mappedOjb.mapping && currShape) {
                        this.highlightedObjects = $(currShape).find("Material");
                        this.highlightedObjects = this.highlightedObjects.filter(function () {
                            if (self.selectedObjects === null || !self.selectedObjects.is(this)) {
                                self.highlighObject(this);
                                return true;
                            } else {
                                return false;
                            }
                        });
                        this.highlightedObject = mappedOjb;

                    }
                }
            } catch (e) {
                console.error("Failed in handleMouseOver", e);
            }
        } else {
            this.resetOutline();
        }
    };
    this.resetOutline = function () {
        if (this.highlightedObjects !== null) {
            var self = this;
            self.highlightedObjects.each(function () {
                if (self.selectedObjects === null || !self.selectedObjects.is(this)) {
                    self.restoreOrigColors(this);
                }
            });
            self.highlightedObjects = null;
            self.highlightedObject = null;
        }
    };
    this.resetSelected = function () {
        if (this.selectedObjects !== null) {
            var self = this;
            this.selectedObjects.each(function () {
                self.restoreOrigColors(this);
            });
            this.selectedObjects = null;
            this.selectedObject = null;
        }
    };
    this.renderAll = function () {
        if (this.hiddenComponents !== null) {
            var self = this;
            self.hiddenComponents.each(function () {
                try {
                    this.setAttribute("render", true);
                } catch (e) {
                    console.error("Could not show ", this);
                }
            });
        }
        this.hiddenComponents = $([]);
    };

    this.renderComponentsHiddenByRightClick = function () {
        if (this.hiddenComponentsByRightClick !== null) {
            for (var i = 0; i < this.hiddenComponentsByRightClick.length; i++) {
                this.hiddenComponentsByRightClick[i].shape.setAttribute("render", "true");
            }
        }
        this.hiddenComponentsByRightClick = [];
    };

    this.resetX3DNav = function () {
        this.resetExplode();
        this.resetOutline();
        this.resetSelected();
        this.renderAll();
        this.resetZoom();
        this.resetTransparencyAndSlider();
        this.renderComponentsHiddenByRightClick();
        this.defMapping = this.x3DConfig.mapping;
        this.getX3DRuntime().resetExamin();
        this.activateView(null);
        this.getX3DRuntime().fitAll(true);
        this.initiateTocNodeForLandingPage();

        if (!this.origFieldOfView) {
            this.origFieldOfView = parseFloat(this.getX3DRuntime().viewpoint().getFieldOfView());
        } else {
            if (this.getX3DRuntime().viewpoint()._xmlNode) {
                this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", this.origFieldOfView);
            }
        }
        this.selectedObjects = null;
        this.highlightedObjects = null;
        this.highlightedObject = null;
        this.hiddenComponents = $([]);
        this.menuSelItem = null;
        this.focusNode = null;
        this.transparencyFactor = null;
        this.historyFocusNode = [];
        var inlineNode = this.getInlineNode();
        inlineNode.find("inline").attr("render", "false");
        $(".goback-button").addClass("disabled").addClass("reduce-opacity").removeClass("active");
        if ($(".goback-button").parent("button").length > 0) {
            $(".goback-button").parent().css("pointer-events", "none");
        }

    };

    this.initiateTocNodeForLandingPage = function () {
        if (this.isLandingPage){
            if (this.x3DConfig && this.x3DConfig.structure) {
                this.openTocNode(this.x3DConfig.structure);
                this.parentNode.push(this.x3DConfig.structure);
            } else {
                this.collapseTocNode();
            }
        }
    };

    this.resetFocusNode = function () {
        this.resetOutline();
        this.resetSelected();
        this.renderComponentsHiddenByRightClick();
        this.getX3DRuntime().resetExamin();
        if (!this.origFieldOfView) {
            this.origFieldOfView = parseFloat(this.getX3DRuntime().viewpoint().getFieldOfView());
        } else {
            this.getX3DRuntime().viewpoint()._xmlNode.setAttribute("fieldOfView", this.origFieldOfView);
        }
        this.selectedObjects = null;
        this.highlightedObjects = null;
        this.highlightedObject = null;
        this.focusNode = null;
    };

    this.getNodeID = function (currNode) {
        var id = null;
        if (currNode && currNode.hasAttribute) {
            if (currNode.hasAttribute("def")) {
                id = currNode.getAttribute("def");
            } else if (currNode.hasAttribute("DEF")) {
                id = currNode.getAttribute("DEF");
            }
        }
        return id;
    };
    this.handleFocusEvent = function (event) {
        var shape = this.getShapeFromMousePos(event);
        var mappedObj = this.findMappedNode(shape);
        this.focusOnComponent((mappedObj && mappedObj.shape) ? mappedObj.shape : shape);
    };

    this.loadSubComponent = function (nodeid, mapping) {
        var deferred = jQuery.Deferred();
        var inlineNode = $("#Inline" + nodeid.replace(/\*/g, ''));
        if (inlineNode.length === 0) {
			this.currentInlineNodes++;
            this.createX3dLoadTimeout();
            this.bindInlineNode(inlineNode, nodeid.replace(/\*/g, ''), mapping).then(function () {
                var inlineNode = $("#Inline" + nodeid);
                if ($(inlineNode).children().length > 0) {
                    deferred.resolve(inlineNode);
                } else {
                    setTimeout(function () {
                        if ($(inlineNode).children().length > 0) {
                            deferred.resolve(inlineNode);
                        }
                    }, 200);
                }
            }).always(function (e) {
                console.info("INLINE BOUND", e);
            });
        } else {
            this.focusNode = inlineNode.parent()[0];
            // Just switch to sub mapping
            this.defMapping = mapping.mapping;
            deferred.resolve(inlineNode);
        }
        return deferred.promise();
    };
    this.focusOnComponent = function (shape) {
        this.focusNode = shape;
        var self = this;
        this.resetExplode();
        this.resetZoom();
        this.resetTransparency();
        var nodeid = this.getNodeID(shape);
        var mapping = this.getMapping(nodeid);
        if (this.shapeHasSubComponent(shape)) {
			this.currentInlineNodes = this.initializeCurrentInlineNodes();
            this.loadSubComponent(nodeid, mapping).then(function (inlineNode) {
                self.showOnlyInlineNode(inlineNode);
                var inlineNode = $("#Inline" + nodeid);
                self.focusNode = inlineNode.parent()[0];
            });

        } else {
            this.recursiveHideSiblings(shape);
            this.defMapping = null;
            setTimeout($.proxy(this.defaultView, this), 300);
        }
        if (mapping && this.isLandingPage){
            this.openTocNode(mapping.structure);
        }
        if (this.focusNode && !this.arrayContainsElement(this.historyFocusNode, this.focusNode)) {
            this.historyFocusNode.push($(this.focusNode));
        }
        $(".goback-button").addClass("active").removeClass("reduce-opacity").removeClass("disabled");
        $(".goback-button").parent().css("pointer-events", "auto");
        this.resetExplode();
    };

    this.setCurrentMapping = function (mapping, inlineNode) {
        this.defMapping = mapping.mapping;
        if (this.historyFocusNode.length > 0) {
            this.historyFocusNode[this.historyFocusNode.length - 1].mapping = mapping.mapping;
        }
        this.waitAndMap(inlineNode);
    };

    this.bindInlineNode = function (inlineNode, nodeid, mapping) {
        var promise = $.Deferred();
        var transform = $("<Transform/>", window.document);
        var useNode = $(mapping.matchedNode || this.focusNode);
        transform.insertAfter(useNode);
        useNode.appendTo(transform);
        transform.attr("DEF", nodeid);
        transform.attr("id", "Transform_" + nodeid);
        // useNode.removeAttr("DEF");
        this.focusNode = transform[0];
        mapping.matchedNode = transform;

        var inlineStr = "<inline mapdeftoid='true' id='Inline" + nodeid + "' nameSpaceName='" + nodeid + "Space' url=\"" + mapping.x3dfile + "\" DEF=" + nodeid + "></inline>";
        var inlineNode = $(inlineStr, window.document);
        inlineNode.appendTo(transform[0]);
        mapping.inlineNode = inlineNode;
        this.getX3DRuntime().canvas.doc.downloadCount = this.currentInlineNodes;
        var self = this;
        inlineNode.bind("load", function () {
            if (mapping.mappingfile && mapping.mappingfile.length > 0) {
                var loadPromise = $.getJSON(self.x3DConfig.baseURL + "/" + mapping.mappingfile, function (data) {
                    mapping.mapping = data.mapping;
                    promise.resolve(mapping, inlineNode);
                }).fail(function (jqxhr, textStatus, error) {
                    var err = textStatus + ", " + error;
                    console.error("Request Failed: " + err);
                    promise.fail(jqxhr, textStatus, error);
                });
            } else {
                promise.resolve(mapping, inlineNode);
            }

        });
        var returnpromise = promise.then(function (mapping, inlineNode) {
            self.setCurrentMapping(mapping, inlineNode);
        });
        return returnpromise;
    };

    this.shapeHasSubComponent = function (shape) {
        var hasSubComponent = false;
        if (this.defMapping && shape && shape.getAttribute("DEF")) {
            this.defMapping.forEach(function (element) {
                if (matchRuleShort(shape.getAttribute("DEF").toLowerCase(), element.name.toLowerCase())) {
                    hasSubComponent = element.hasOwnProperty("x3dfile");
                }
            });
        }
        return hasSubComponent;
    };

    this.containsNode = function (arrayOfNodes, node) {
        var containsNode = false;
        for (var i = 0; i < arrayOfNodes.length; i++) {
            if (arrayOfNodes[i] === node) {
                containsNode = true;
            }
        }
        return containsNode;
    };

    this.prevFocusNode = function () {
        var inlineNode = null;

        this.historyFocusNode.pop();
        this.resetExplode();
        this.resetTransparency();
        if (this.historyFocusNode.length <= 0) {
            this.renderAll();
            this.focusNode = null;
            this.activateView(null);
            this.defMapping = this.x3DConfig.mapping;
            inlineNode = this.getInlineNode();
            inlineNode.find("inline").attr("render", "false");
            $(".goback-button").addClass("disabled").addClass("reduce-opacity").removeClass("active");
            if ($(".goback-button").parent("button").length > 0){
                $(".goback-button").parent().css("pointer-events", "none");
            }
            if(this.parentNode.length === 1){
                this.openTocNode(this.parentNode[0]);
            }
        } else {
            var newFocusNode = this.historyFocusNode[this.historyFocusNode.length - 1];
            var nodeid = this.getNodeID(newFocusNode[0]);
            var parentNode = this.getParent(this.x3DConfig, nodeid);

            if (parentNode) {
                this.defMapping = parentNode.mapping;
                this.updateTocForPrevNode(parentNode.structure);
                this.updateFromTocTree(parentNode.structure[parentNode.structure.length - 1], true, parentNode.structure);
            }

            if (!newFocusNode.has("inline").length > 0) {
                newFocusNode.find("[render=false]").attr("render", "true");
            }

            this.focusNode = newFocusNode[0];
        }
        this.hideHiddenComponents();
        this.resetExplode();
        if (inlineNode) {
            this.useInlineViewpoint(inlineNode);
        } else {
            this.getX3DRuntime().fitAll(true);
        }
    };

    this.transparency = function (value) {
        if (value === null) {
            this.getX3DNode().find("Material").attr("transparency", 0);
            for (element in this.selectedObject) {
                $(this.selectedObject[element]).find("Material").attr("transparency", 0);
            }
        } else {
            this.transparencyFactor = value;
            this.getX3DNode().find("Material").attr("transparency", value);
            for (element in this.selectedObject) {
                $(this.selectedObject[element]).find("Material").attr("transparency", value);
            }
        }
    }

    this.hideHiddenComponents = function () {
        for (var i = 0; i < this.hiddenComponentsByRightClick.length; i++) {
            $(this.hiddenComponentsByRightClick[i].shape).attr("render", "false");
        }
    };
    this.getParent = function (tree, nodeid) {
        var i, res;
        if (!tree || !tree.mapping) {
            return null;
        }
        if (Object.prototype.toString.call(tree.mapping) === '[object Array]') {
            for (i in tree.mapping) {
                if (matchRuleShort(nodeid, tree.mapping[i].name)) {
                    return tree.mapping[i];
                }
                res = this.getParent(tree.mapping[i], nodeid);
                if (res) {
                    return res;
                }
            }
            return null;
        } else {
            if (matchRuleShort(nodeid, tree.mapping.name)) {
                return tree;
            }
            return this.getParent(tree.mapping, nodeid);
        }
    };


    this.arrayContainsElement = function (array, element) {
        var containsElement = false;
        for (var i = 0; i < array.length; i++) {
            if (array[i].is(element)) {
                containsElement = true;
            }
        }
        return containsElement;
    };

    this.showOnlyInlineNode = function (inputInline) {
        var inlineNode = $(inputInline);

        $(".goback-button").addClass("active").removeClass("reduce-opacity").removeClass("disabled");
        $(".goback-button").parent().css("pointer-events", "auto");
        this.recursiveHideSiblings(inlineNode[0]);
        this.recursiveShowNode(inlineNode[0]);
        this.showInlineParentNodes(inlineNode)
        this.hideInlineChildren(inlineNode[0]);
        this.useInlineViewpoint(inlineNode);
    };

    this.hideInlineChildren = function (inlineNode) {
        $(inlineNode).find("inline").attr("render", false);
    }

    this.showInlineParentNodes = function (inlineNode) {

        inlineNode.parents("inline").attr("render", "true");

    }

    this.useInlineViewpoint = function (inlineNode) {
        var viewPoint = inlineNode.find('Viewpoint, viewpoint').filter(function () {
            if ($(this).parentsUntil(inlineNode, "inline").length > 0) {
                return false;
            } else {
                return true;
            }
        });
        if (viewPoint.length > 0) {
            this.activateView(viewPoint[0]);
        } else {
            this.centerOnNode(inlineNode[0]);
            this.getX3DRuntime().fitAll();
        }
    };

    this.waitAndMap = function (inlineNode) {
        var self = this;
        if ($(inlineNode).children().length > 0) {
            $(inlineNode).find("[DEF],CADAssembly[Name]").each(function () {
                self.mapNodes(this);
            });
        } else {
            setTimeout($.proxy(this.waitAndMap, this, inlineNode), 200);
        }
    };
    this.recursiveHideSiblings = function (node) {
        var parent = $(node).parent();
        var self = this;
        parent.children().each(function () {
            if (node !== this) {
                self.hiddenComponents = self.hiddenComponents.add($(this));
                this.setAttribute("render", "false");
            }
        });

        if (parent.length > 0 && parent[0].nodeName.toLowerCase() !== "x3d") {
            this.recursiveHideSiblings(parent[0]);
        }
    };
    this.recursiveShowNode = function (node) {
        var self = this;
        $(node).find("[render=false]").filter(function (index, node) {
            if (!self.getX3DRuntime().isA(node, 'inline')) {
                return true;
            }
        }).attr("render", "true");
        $(node).attr("render", "true");
        for (var i = 0; i < this.hiddenComponentsByRightClick.length; i++) {
            $(this.hiddenComponentsByRightClick[i].shape).attr("render", "false");
        }
    };
    this.hideComponent = function (shape) {
        if (shape && shape.getAttribute("id") != undefined) {
            shape.setAttribute("render", "false");
            var object = {
                shape: shape,
                id: shape.id,
                def: shape.getAttribute("DEF")
            };
            this.hiddenComponentsByRightClick.push(object);
        } else if ($(shape.parentNode).is("[id]")) {
            shape.parentNode.setAttribute("render", "false");
            var parentObject = {
                shape: shape.parentNode,
                id: shape.parentNode.id,
                def: shape.parentNode.getAttribute("DEF")
            };
            this.hiddenComponentsByRightClick.push(parentObject);
        } else if (shape.getAttribute("id") == undefined && $(".alert").length <= 0) {
            $(".camera_buttons").next().append('<div class="alert alert-danger alert-dismissible alert-hidden-elements" role="alert">' +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span>' +
                '</button>' +
                'We are not able to hide this element' +
                '</div>');
        }
    };

    this.renderComponent = function (selectedModelId) {
        for (var i = 0; i < this.hiddenComponentsByRightClick.length; i++) {
            if (this.hiddenComponentsByRightClick[i].$$hashKey === selectedModelId) {
                this.getX3DNode().find(this.hiddenComponentsByRightClick[i].shape)[0].setAttribute("render", "true");
                this.hiddenComponentsByRightClick.splice(i, 1);
            }
        }
    };

    this.x3dMenu = function (element) {
        var searchFunc = $.proxy(this.handleRightClickSearch, this);
        var focusFunc = $.proxy(this.focusOnComponent, this);
        var hideFunc = $.proxy(this.hideComponent, this);
        var self = this;
        this.contentMenuElement = $(element).parent();
        this.contentMenuElement.contextMenu('destroy');
        this.contentMenuElement.contextMenu({
            // define which elements trigger this menu
            selector: "x3d",
            zIndex: 10,
            // define the elements of the menu
            items: {
                search: {
                    name: "Search", callback: function () {
                        searchFunc(self.menuSelItem);
                    }
                },
                focus: {
                    name: "Focus", callback: function () {
                        focusFunc(self.menuSelItem);
                    },
                    disabled: function () {
                        if (self.focusNode) {
                            if ($(self.focusNode).find("Shape").length <= 0) {
                                return true;
                            } else if (self.getX3DRuntime().isA(self.focusNode, "Transform") && $(self.focusNode).find("Shape").length <= 1) {
                                return true;
                            }
                        }
                        return false;
                    }
                },
                hide: {
                    name: "Hide", callback: function () {
                        hideFunc(self.menuSelItem);
                    }
                }
            }
        });

    };
    this.findMappedNode = function (shape) {
        var mapping = null;
        var currShape = shape;
        while (mapping === null && currShape && currShape !== this.focusNode) {
            if (currShape.getAttribute) {
                var def = this.getNodeID(currShape);
                var isMapped = this.DEFDomObjectMapping[def];
                if (isMapped) {
                    mapping = this.getMapping(def);
                }
            }
            if (mapping === null) {
                currShape = currShape.parentNode;
            }
        }
        return {mapping: mapping, shape: mapping ? currShape : null};
    };
    this.menuEvent = function (event) {
        var orgEvent = this.getOrgEvent(event);
        var pos = this.getX3DRuntime().mousePosition(orgEvent, 0);
        var shape = this.getX3DRuntime().pickRect(pos[0], pos[1], pos[0], pos[1])[0];
        var mappedNode = this.findMappedNode(shape);
        if (mappedNode.mapping) {
            this.menuSelItem = mappedNode.shape;
        } else {
            this.menuSelItem = shape;
        }
        var position = {
            x: orgEvent.clientX,
            y: orgEvent.clientY
        };
        if (typeof shape !== 'undefined') {
            $(shape).contextMenu(position);
        }
    };
    this.getX3DNode = function () {
        return this.x3dNode;
    };
    this.getX3DRuntime = function () {
        return this.getX3DNode()[0].runtime;
    };
    this.getInlineNode = function () {
        return this.getX3DNode().find("inline:first, MultiPart:first");
    };
    this.getMapping = function (def) {
        var defMap = null;
        if (this.defMapping) {
            $.each(this.defMapping, function (index, value) {
                if (def && matchRuleShort(def.toUpperCase(), value.name.toUpperCase())) {
                    defMap = value;
                    return false;
                }
            });
        }
        return defMap;
    };

    this.setupListener = function () {
        if (this.getInlineNode().children().length === 0) {
            setTimeout($.proxy(this.setupListener, this), 200);
            return;
        }
        try {
            var x3dNode = this.getX3DNode();
            this.createX3dLoadTimeout();

            // create a simple instance
            // by default, it only adds horizontal recognizers
            //var mc = new Hammer(x3dNode);
            // We create a manager object, which is the same as Hammer(), but without the presetted recognizers.
            this.mc = new Hammer.Manager(x3dNode[0]);
            var singleTap = new Hammer.Tap({event: 'singletap'});
            var doubleTap = new Hammer.Tap({event: 'doubletap', taps: 2});
            this.mc.add([doubleTap, singleTap]);
            doubleTap.recognizeWith(singleTap);
            singleTap.requireFailure(doubleTap);

            this.mc.add(new Hammer.Press({event: 'press', time: 500}));
            this.mc.add(new Hammer.Pan({event: 'pan', direction: Hammer.DIRECTION_ALL}));
            // listen to events...
            var self = this;
            this.mc.on("press tap singletap doubletap", function (ev) {
                try {
                    if (ev.type === "press" && ev.pointerType !== 'mouse') {
                        self.menuEvent(ev);
                    }
                    if (ev.type === "tap" || ev.type === "singletap") {
                        self.handleCompClick(ev);
                    } else if (ev.type === "doubletap") {
                        if(!self.getShapeFromMousePos(ev)){
                            return;
                        }
                        var disabled = false;

                        /* when on the top level the focusNode is null/not defined.
                        disabled will be false by default.
                        If the focusNode is a transform we need to check if there is only one shape as children.
                        Since the focusNode will be the transform node instead of shape node when its transform is defined */
                        if (self.focusNode) {
                            if ($(self.focusNode).find("Shape").length <= 0) {
                                disabled = true;
                            } else if (self.getX3DRuntime().isA(self.focusNode, "Transform") && $(self.focusNode).find("Shape").length <= 1) {
                                disabled = true;
                            }
                        }
                        if (!disabled) {
                            self.handleFocusEvent(ev);
                        }
                    }
                } catch (e) {
                    console.error("Failed in touch event", e);
                }
            });
            x3dNode.mousedown(function (event) {
                if (event.button === 2) {
                    self.menuEvent(event);
                }

            });
            //Disable the default, set rotation point
            self.getX3DRuntime().canvas.onDoubleClick = function () {
            };

            x3dNode[0].addEventListener("mousemove", $.proxy(self.handleMouseOver, self), true);

            self.resetX3DNav();

            this.getInlineNode().find("[DEF],CADAssembly[name]").each(function () {
                self.mapNodes(this);
            });
            this.onTopModelLoaded(this.x3DConfig);

            if (!this.viewpointExists()) {
                this.getInlineNode().parent().append("<Viewpoint id='generatedView'></Viewpoint>");
                this.getX3DRuntime().fitAll();
            }

            $('x3d')[0].addEventListener("downloadsfinished", $.proxy(self.handleX3DLoaded, self), true);
        } catch (e) {
            console.error("Failed to start X3D", e);
        }
    };

    this.destroyX3DomSupport = function() {
        if (this.x3dNode) {
            this.x3dNode.remove();
        }
        if (this.mc) {
            this.mc.destroy();
        }
        if (this.contentMenuElement) {
            this.contentMenuElement.contextMenu('destroy');
        }
        this.resetX3DSupport(null, null, false, null);

    };
    this.mapNodes = function (x3dNode) {
        var def = this.getNodeID(x3dNode);
        var thisNode = $(x3dNode);
        var defMap = this.getMapping(def);
        if (defMap && (thisNode.parentsUntil(this.focusNode, "[isMapped]").length === 0)) {
            this.DEFDomObjectMapping[def] = thisNode.get(0);
            defMap.matchedDef = def;
            defMap.matchedNode = thisNode;
            thisNode.attr("isMapped", "true");
        }
    };

    this.closeSidebar = function () {
        var element = document.getElementById("rightMenu");
        if (!this.isSidebarOpen) {
            $(element).css("width", "300px");
            this.isSidebarOpen = true;
            $(element).find(".fa-angle-double-left").addClass("fa-angle-double-right");
            $(element).find(".fa-angle-double-left").removeClass("fa-angle-double-left");
            $(element).find(".sidebar-side-footer").addClass("hide-sidebar-footer");
            $(element).find(".tabs").removeClass("tabs-hide-content");
            $(element).find(".sidebar-footer-info").removeClass("sidebar-footer-info-hide");
        } else {
            $(element).css("width", "35px");
            this.isSidebarOpen = false;
            $(element).find(".fa-angle-double-right").addClass("fa-angle-double-left");
            $(element).find(".fa-angle-double-right").removeClass("fa-angle-double-right");
            $(element).find(".sidebar-side-footer").removeClass("hide-sidebar-footer");
            $(element).find(".tabs").addClass("tabs-hide-content");
            $(element).find(".sidebar-footer-info").addClass("sidebar-footer-info-hide");
        }
    };

    this.closeSidebarGraphic = function () {
        var element = document.getElementById("leftMenuGraphic");
        if (!this.isSidebarOpen) {
            $(element).css("width", "300px");
            this.isSidebarOpen = true;
            $(element).find(".fa-angle-double-left").addClass("fa-angle-double-right");
            $(element).find(".fa-angle-double-left").removeClass("fa-angle-double-left");
            $(element).find(".sidebar-side-footer").addClass("hide-sidebar-footer");
            $(element).find(".tabs").removeClass("tabs-hide-content");
            $(element).find(".sidebar-footer-info").removeClass("sidebar-footer-info-hide");
        } else {
            $(element).css("width", "0px");
            this.isSidebarOpen = false;
            $(element).find(".fa-angle-double-right").addClass("fa-angle-double-left");
            $(element).find(".fa-angle-double-right").removeClass("fa-angle-double-right");
            $(element).find(".sidebar-side-footer").removeClass("hide-sidebar-footer");
            $(element).find(".tabs").addClass("tabs-hide-content");
            $(element).find(".sidebar-footer-info").addClass("sidebar-footer-info-hide");
        }
    };

    this.defaultView = function (id) {
        this.activateView(null);
        this.getX3DRuntime().fitAll(true);
    };

    this.topView = function () {
        this.getX3DRuntime().showAll('negY');
    }

    this.bottomView = function () {
        this.getX3DRuntime().showAll('posY');
    }

    this.leftView = function () {
        this.getX3DRuntime().showAll('posZ');
    }

    this.rightView = function () {
        this.getX3DRuntime().showAll('negZ');
    }

    this.openTocNode = function (structure) {
        var tocTree = $.fn.zTree.getZTreeObj("tocTree");
        var previousNode = null;

        loadTocNodesAsync(0);

        function loadTocNodesAsync(structureIndex) {
            if (structureIndex < structure.length) {
                setTimeout(function () {
                    var nodeTitle = structure[structureIndex];
                    var node = tocTree.getNodeByParam("title", nodeTitle, previousNode);
                    if (!node) {
                        node = tocTree.getNodeByParam("title", nodeTitle + " ", previousNode);
                    }

                    if ((node && node.isAjaxing) || (previousNode && previousNode.isAjaxing)) {
                        loadTocNodesAsync(structureIndex);
                    } else if (node) {
                        // DM node
                        if (node.leaf) {
                            tocTree.setting.callback.onClick(null, "tocTree", node);
                        } else {
                            tocTree.expandNode(node, true);
                        }

                        if (structureIndex + 1 === structure.length) {
                            tocTree.selectNode(node);
                        }

                        previousNode = node;
                        loadTocNodesAsync(++structureIndex);
                    }

                }, 50);
            }
        }
    };

    this.collapseTocNode = function(){
        var tocTree = $.fn.zTree.getZTreeObj("tocTree");
        tocTree.expandAll(false);
        tocTree.cancelSelectedNode();
    };

    this.updateTocForPrevNode =function (structure) {
        if (structure)
            this.openTocNode(structure);
    };

    this.viewpointExists = function () {
        var viewpointExists = false;
        if (this.getX3DNode().find("Viewpoint, viewpoint").length > 0) {
            viewpointExists = true;
        }
        return viewpointExists;
    }
    // Trigger the top 3D.
    this.renderX3D = function(X3DConfig) {
        this.getInlineNode().attr("url", X3DConfig.baseURL + "/" + X3DConfig.x3dfile).promise().done(function () {
            var target = $("#loading-x3d");
            setTimeout(function () {
                hideLoading(target);
                target.remove();
            }, 250);
        });
        this.getInlineNode().attr("load", "true");
    }
    this.renderX3D(X3DConfig);
    // Setup the x3Dom listeners
    this.setupListener();
	
	this.initializeCurrentInlineNodes = function()
	{
		return 0;
	}
}

// module "x3dom-support.js"