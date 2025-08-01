(function () {
    'use strict';

    angular
        .module('app')
        .constant('appMetadata', {
            "version": "8.5.0.9",
            "copyright": "Copyright © 2024 Flatirons Solutions, Inc.",
            "buildDate": "2024-Oct-31 11:24"
        })
        .constant('appConf', {
            "isGreyOutInvalidToc": true,
            "isHideInvalidContent": false,
            "dateFormat": "MMM-dd-yyyy",
            "timeFormat": "hh:mm A",
            "tocTitle": "{title} {dmc}",
            "tocTitleSeparator": " ",
            "embeddedRefDocTitle": "@DMC",
            "howToShowPublication": {
               "splitWindow": ["AIPC", "EIPC", "IPC", "IPD", "IPDP", "SSRM"],
                "fullGraphicWindow": ["WM", "WDM", "SSM", "AWM", "ASM", "ASDP", "AWDP"]
            },
            "externalPublish": [
                {
                    "libraryID": "PROCEDURE_MANUALS",
                    "publicationID": "GPM",
                    "externalURL": "http://192.168.5.97/ppa66/exec/manual.aspx?VERSION=current&MODEL=PROCEDURE_MANUALS&DOCTYPE=AIRBOOK&DOCNBR=GPM&ISESSION=1"
                }
            ],
            "printSheetNumLimitation": 40,
            "howToShowSearch": {
                "popup": ["TSM", "WIRING", "FRMFIM"],
                "silent": ["FTS", "FIN"]
            },
			"isSplitFaultCodeChapter" : "false",
			"toggleAtaNumbering": true
        })
        .constant('eventsSeq', [
                {
                    "sourceEvent": "libraryReady",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "libraryInit",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryLoaded",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "gotoInit",
                            "targetWidget": "goto"
                        }
                    ]
                },
                {
                    "sourceEvent": "librarySelected",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "appLogout",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "headerReset",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "tocReset",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentReset",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "graphicDiagramsReset",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "fulltextsearchReset",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "footerReset",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "filterReset",
                            "targetWidget": "filter"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryUpdated",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "tocInit",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "fimsearchInit",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchInit",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        },
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        },
                        {
                            "targetEvent": "wiringSearchInit",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "externalTOCLink",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "libraryRefresh",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "fimsearchInit",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchInit",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        },
                        {
                            "targetEvent": "wiringSearchInit",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        },
                        {
                            "targetEvent": "tocRefresh",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryOpen",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "initTOCRefresh",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "tocRefresh",
                            "targetWidget": "toc"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryExpanded",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryOpenAll",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "fulltextsearchAllInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "headerRefresh",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryOpenWithoutReset",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryClose",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "headerRefresh",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryCloseAll",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "fulltextsearchAllInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "headerRefresh",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "libraryRevisionChange",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "tocInit",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "attachmentsReset",
                            "targetWidget": "attachments"
                        },
                        {
                            "targetEvent": "contentReset",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "fimsearchReset",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchReset",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "headerRevisionChange",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "graphicDiagramsReset",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "annotationsReset",
                            "targetWidget": "annotations"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "tocUpdated",
                    "sourceWidget": "toc",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "headerUpdated",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        }
                    ]
                },
                {
                    "sourceEvent": "fimsearchUpdated",
                    "sourceWidget": "fimsearch",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "headerFinSearchFin",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "headerFinSearch",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "ftsFinSearchInit",
                            "targetWidget": "fulltextsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openEINSearch",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "ftsFinSearchInit",
                            "targetWidget": "fulltextsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openLinkSearch",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "ftsLinkSearchInit",
                            "targetWidget": "fulltextsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "headerFtsSearch",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "ftsSearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "hideSearchSuggestionDropdown",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openAcknowledgePublication",
                    "sourceWidget": "readSign",
                    "targets": [
                        {
                            "targetEvent": "acknowledgePublicationSync",
                            "targetWidget": "library"
                        }
                    ]
                },
                {
                    "sourceEvent": "openLandingHotspotLink",
                    "sourceWidget": "landingPage",
                    "targets": [
                        {
                            "targetEvent": "landingHotspotLinkPublicationSync",
                            "targetWidget": "library"
                        }
                    ]
                },
                {
                    "sourceEvent": "contentUpdated",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "graphicInit",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "attachmentsInit",
                            "targetWidget": "attachments"
                        },
                        {
                            "targetEvent": "authoringInit",
                            "targetWidget": "authoring"
                        },
                        {
                            "targetEvent": "graphicDiagramsInit",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "tocRefresh",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "librarySync",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "historyInit",
                            "targetWidget": "visualHistory"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "annotationsInit",
                            "targetWidget": "annotations"
                        },
                        {
                            "targetEvent": "bookmarkInit",
                            "targetWidget": "bookmark"
                        },
                        {
                            "targetEvent": "acknowledgeInit",
                            "targetWidget": "readSign"
                        },
                        {
                            "targetEvent": "printInit",
                            "targetWidget": "print"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "addPartOrder",
                            "targetWidget": "pinpointcomponent"
                        },
                        {
                            "targetEvent": "resetThumbnails",
                            "targetWidget": "thumbnailGallery"
                        }
                    ]
                },
				{
                    "sourceEvent": "contentUpdatedByTR",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "graphicInit",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "attachmentsInit",
                            "targetWidget": "attachments"
                        },
                        {
                            "targetEvent": "graphicDiagramsInit",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "annotationsInit",
                            "targetWidget": "annotations"
                        },
                        {
                            "targetEvent": "bookmarkInit",
                            "targetWidget": "bookmark"
                        },
                        {
                            "targetEvent": "acknowledgeInit",
                            "targetWidget": "readSign"
                        },
                        {
                            "targetEvent": "printInit",
                            "targetWidget": "print"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        }
                    ]
                },
                {
                    "sourceEvent": "annotationGraphicUpdated",
                    "sourceWidget": "AnnotationGraphic",
                    "targets": [
                        {
                            "targetEvent": "annotationsInit",
                            "targetWidget": "annotations"
                        },
                    ]
                },
                {
                    "sourceEvent": "annotationGraphicClicked",
                    "sourceWidget": "annotations.panel.controller",
                    "targets": [
                        {
                            "targetEvent": "annotationGraphicOpen",
                            "targetWidget": "AnnotationGraphic"
                        },
                    ]
                },
                {
                    "sourceEvent": "contentSwitched",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "graphicInit",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "attachmentsInit",
                            "targetWidget": "attachments"
                        },
                        {
                            "targetEvent": "authoringInit",
                            "targetWidget": "authoring"
                        },
                        {
                            "targetEvent": "graphicDiagramsInit",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "tocRefresh",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "annotationsInit",
                            "targetWidget": "annotations"
                        },
                        {
                            "targetEvent": "bookmarkInit",
                            "targetWidget": "bookmark"
                        },
                        {
                            "targetEvent": "acknowledgeInit",
                            "targetWidget": "readSign"
                        },
                        {
                            "targetEvent": "headerRefresh",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "librarySync",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "printInit",
                            "targetWidget": "print"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "resetThumbnails",
                            "targetWidget": "thumbnailGallery"
                        }
                    ]
                },
                {
                    "sourceEvent": "openGraphicSheet",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "showSheet",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "openGraphicDialog",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "openGraphicDialog",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "fulltextsearchUpdated",
                    "sourceWidget": "fulltextsearch",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        }
                    ]
                },
            {
                "sourceEvent": "ftsSearchReset",
                "sourceWidget": "fulltextsearch",
                "targets": [
                    {
                        "targetEvent": "headerftsReset",
                        "targetWidget": "header"
                    },
                    {
                        "targetEvent": "contentftsReset",
                        "targetWidget": "content"
                    }
                ]
            },
                {
                    "sourceEvent": "annotationsupplementsearchUpdated",
                    "sourceWidget": "annotationsupplementsearch",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "openSupplementFromSearch",
                    "sourceWidget": "annotationsupplementsearch",
                    "targets": [
                        {
                            "targetEvent": "openSupplementSearch",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "openPrint",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "openPrintPreview",
                            "targetWidget": "print"
                        }
                    ]
                },
                {
                    "sourceEvent": "filterUpdated",
                    "sourceWidget": "filter",
                    "targets": [
                        {
                            "targetEvent": "filterToc",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "filterContent",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicFilter",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "fimsearchReset",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchReset",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "updateFilterAttrValues",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "publicationUpdated",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "clearAnnotationSupplementSearch",
                            "targetWidget": "annotationsupplementsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openGraphicDiagrams",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "showGraphicDiagrams",
                            "targetWidget": "graphicDiagrams"
                        }
                    ]
                },
                {
                    "sourceEvent": "openWiringSearch",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openWiringSearchFromZone",
                    "sourceWidget": "zoneSearch",
                    "targets": [
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openFinSearch",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "finsearchReset",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "executeFinSearch",
                    "sourceWidget": "finserach",
                    "targets": [
                        {
                            "targetEvent": "searchFinClickEvents",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "graphicUpdated",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "highlightItemNum",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "hightlightItemNumber",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "contentHotspotHighlighted",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "graphicHotspotHighlight",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContent",
                    "sourceWidget": "wiringSearch",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContentFin",
                    "sourceWidget": "FinSearch",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "highlightGraphicDiagrams",
                    "sourceWidget": "graphicDiagrams",
                    "targets": [
                        {
                            "targetEvent": "highlightGraphic",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "gotoUpdated",
                    "sourceWidget": "goto",
                    "targets": [
                        {
                            "targetEvent": "libraryRefresh",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "tocInit",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "graphicFilter",
                            "targetWidget": "graphic"
                        },

                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "fimsearchInit",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchInit",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "wiringSearchInit",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        },
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        }
                    ]
                },
                {
                    "sourceEvent": "gotoUpdate",
                    "sourceWidget": "app",
                    "targets": [
                        {
                            "targetEvent": "contentGotoUpdated",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "libraryGotoUpdated",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "attachmentsGotoUpdated",
                            "targetWidget": "attachments"
                        }
                    ]
                },
                {
                    "sourceEvent": "annotationsReceived",
                    "sourceWidget": "annotations.service",
                    "targets": [
                        {
                            "targetEvent": "annotationsControllerUpdate",
                            "targetWidget": "annotations.controller"
                        },
                        {
                            "targetEvent": "annotationsPanelUpdate",
                            "targetWidget": "annotations.panel.controller"
                        },
                        {
                            "targetEvent": "annotationGraphicUpdate",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "annotationsOpen",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "annotationsOrganize",
                            "targetWidget": "annotations"
                        }
                    ]
                },
                {
                    "sourceEvent": "reloadLibrary",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "libraryReload",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "tocReset",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentReset",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "graphicDiagramsReset",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "fulltextsearchReset",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "fimsearchReset",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "tsmSearchReset",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "finsearchReset",
                            "targetWidget": "finsearch"
                        },
                        {
                            "targetEvent": "footerReset",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "filterReset",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "permissionReset",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "headerInit",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "tocReset",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentReset",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "graphicDiagramsReset",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "fulltextsearchReset",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "fimsearchReset",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "tsmSearchReset",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "finsearchReset",
                            "targetWidget": "finsearch"
                        },
                        {
                            "targetEvent": "footerReset",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "filterReset",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "publicationRelease",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "restrictedFragment",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "restrictedFragment",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "License",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "showUserProfileInfo",
                    "sourceWidget": "footer",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "importStatus",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "manageCurrentRevision",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "showBookmarkList",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "resetPublicationReversion",
                    "sourceWidget": "release",
                    "targets": [
                        {
                            "targetEvent": "tocInit",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "fulltextsearchInit",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "annotationsupplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "supplementsearchInit",
                            "targetWidget": "annotationsupplementsearch"
                        },
                        {
                            "targetEvent": "fimsearchInit",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "tsmSearchInit",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "filterInit",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "headerRevisionChange",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "footerInit",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "wiringSearchInit",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "resetManageRevision",
                    "sourceWidget": "manageCurrentRevision",
                    "targets": [
                        {
                            "targetEvent": "headerReset",
                            "targetWidget": "header"
                        },
                        {
                            "targetEvent": "libraryReload",
                            "targetWidget": "library"
                        },
                        {
                            "targetEvent": "tocReset",
                            "targetWidget": "toc"
                        },
                        {
                            "targetEvent": "contentReset",
                            "targetWidget": "content"
                        },
                        {
                            "targetEvent": "graphicReset",
                            "targetWidget": "graphic"
                        },
                        {
                            "targetEvent": "graphicDiagramsReset",
                            "targetWidget": "graphicDiagrams"
                        },
                        {
                            "targetEvent": "fulltextsearchReset",
                            "targetWidget": "fulltextsearch"
                        },
                        {
                            "targetEvent": "fimsearchReset",
                            "targetWidget": "fimsearch"
                        },
                        {
                            "targetEvent": "wiringSearchReset",
                            "targetWidget": "wiringSearch"
                        },
                        {
                            "targetEvent": "tsmSearchReset",
                            "targetWidget": "tsmSearch"
                        },
                        {
                            "targetEvent": "footerReset",
                            "targetWidget": "footer"
                        },
                        {
                            "targetEvent": "filterReset",
                            "targetWidget": "filter"
                        },
                        {
                            "targetEvent": "finsearchInit",
                            "targetWidget": "finsearch"
                        }
                    ]
                },
                {
                    "sourceEvent": "openAcmGroupsSelector",
                    "sourceWidget": "readSign",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "acmUserGroupSelected",
                    "sourceWidget": "readSign",
                    "targets": [
                        {
                            "targetEvent": "acmGroupSelected",
                            "targetWidget": "readSign"
                        }
                    ]
                },
                {
                    "sourceEvent": "showPublicationMetadata",
                    "sourceWidget": "toc",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "showDocumentMetadata",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "popupDialog",
                            "targetWidget": "popup"
                        }
                    ]
                },
                {
                    "sourceEvent": "openAnnotationExport",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "annotationsExport",
                            "targetWidget": "annotations"
                        }
                    ]
                },
                {
                    "sourceEvent": "openAnnotationImport",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "annotationsImport",
                            "targetWidget": "annotations"
                        }
                    ]
                },
                {
                    "sourceEvent": "openImportPinpointNeutralPackages",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "importPpNeutralPackages",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "openLandingPage",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "landPageOpen",
                            "targetWidget": "landingPage"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContentLandingPage",
                    "sourceWidget": "fulltextsearch",
                    "targets": [
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        }
                    ]
                },
                {
                    "sourceEvent": "openInLandingPage",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "publicationLandingCheck",
                            "targetWidget": "landingPage"
                        }
                    ]
                },
                {

                    "sourceEvent": "cancelFeedback",
                    "sourceWidget": "feedback",
                    "targets": [
                        {
                            "targetEvent": "FeedbackPageCancel",
                            "targetWidget": "content"
                        }
                    ]

                },
                {

                    "sourceEvent": "graphicStateChange",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "graphicStateUpdate",
                            "targetWidget": "header"
                        }
                    ]
                },
                {

                    "sourceEvent": "contentScrollChange",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "contentScrollUpdate",
                            "targetWidget": "header"
                        }
                    ]
                },
                {

                    "sourceEvent": "graphicS1000DHotspot",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "contentS1000DHotspot",
                            "targetWidget": "content"
                        }
                    ]
                },
                {

                    "sourceEvent": "closeGraphicHotspotListDialog",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "closeGraphicHotspotListDialog",
                            "targetWidget": "graphic"
                        }
                    ]
                },
                {
                    "sourceEvent": "clearHotspotHighLightText",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "clearHotspotHighLightText",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "addShoppingCartForParts",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "addShoppingCart",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "updateShoppingBasketCounter",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "shoppingBasketCounterUpdated",
                            "targetWidget": "header"
                        }
                    ]
                },
                {
                    "sourceEvent": "openShoppingBasket",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "openShoppingBasketFromHeader",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "initContentFromGraphic",
                    "sourceWidget": "graphic",
                    "targets": [
                        {
                            "targetEvent": "contentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "onFTSInputChange",
                    "sourceWidget": "header",
                    "targets": [
                        {
                            "targetEvent": "ftsInputChange",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openExportControl",
                    "sourceWidget": "library",
                    "targets": [
                        {
                            "targetEvent": "exportControlInit",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openPublication",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "publicationInit",
                            "targetWidget": "library"
                        }
                    ]
                },
                {
                    "sourceEvent": "openExportControlFromSearch",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "exportControlInit",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContentPane",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "loadContentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
            {
                "sourceEvent": "viewRestrictedFragmentContent",
                "sourceWidget": "goto",
                "targets": [
                    {
                        "targetEvent": "viewDraftContent",
                        "targetWidget": "content"
                    }
                ]
            },
                {
                    "sourceEvent": "openPublication",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "publicationInit",
                            "targetWidget": "library"
                        }
                    ]
                },
                {
                    "sourceEvent": "openExportControlFromSearch",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "exportControlInit",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContentPane",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "loadContentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "openUnlockPublicationsPane",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "showUnlockPublications",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openPublication",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "publicationInit",
                            "targetWidget": "library"
                        }
                    ]
                },
                {
                    "sourceEvent": "openExportControlFromSearch",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "exportControlInit",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openContentPane",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "loadContentInit",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "openUnlockPublicationsPane",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "showUnlockPublications",
                            "targetWidget": "pinpointcomponent"
                        }
                    ]
                },
                {
                    "sourceEvent": "openDocumentLink",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "onContentInit",
                            "targetWidget": "content"
                        }
                    ]
                }, 
    			{
                    "sourceEvent": "supplementMarginOpened",
                    "sourceWidget": "pinpointcomponent",
                    "targets": [
                        {
                            "targetEvent": "adjustEmbeddedWindow",
                            "targetWidget": "content"
                        }
                    ]
                },
                {
                    "sourceEvent": "isATANumberStyle",
                    "sourceWidget": "content",
                    "targets": [
                        {
                            "targetEvent": "ataStyleInit",
                            "targetWidget": "print"
                        },
                        {
                            "targetEvent": "ataStyleInit",
                            "targetWidget": "toc"
                        }
                    ]
                }
            ]
        );
})();
