Document Author: Roberto Del Angel
Last Updated: August 9th, 2017

This library is the Mozilla PDF.js library available from github at this location:
https://github.com/mozilla/pdf.js

The instructions on their Wiki page "Setup PDF.js in a website" were used to externalize and invoke their 
PDF.js Viewer as an independent component:
https://github.com/mozilla/pdf.js/wiki/Setup-PDF.js-in-a-website

Extract:
	When the source code of PDF.js changes, the online demo is automatically updated. The 
	source of all demo files can easily be accessed at https://github.com/mozilla/pdf.js/tree/gh-pages. 
	These files can also be uploaded to your server to use PDF.js to display PDF files from your 
	website.

	Download https://github.com/mozilla/pdf.js/archive/gh-pages.zip.

	Extract the ZIP file (a directory called "pdf.js-gh-pages" will be created).

	Copy the following directories to your website:

	pdf.js-gh-pages/build/
	pdf.js-gh-pages/web/
	The web/ directory contains a 1 MB PDF file called "compressed.tracemonkey-pldi-09.pdf". This 
	file is only used as an example for the demo and can safely be removed.
	If you want to open a PDF from your website with PDF.js, simply link to the viewer and pass the 
	location of the PDF file. For example:

	<a href="/web/viewer.html?file=%2Fyourpdf.pdf">Open yourpdf.pdf with PDF.js</a>
	The viewer is built on the display layer and is the UI for PDF viewer in Firefox and the other 
	browser extensions within the project. It can be a good starting point for building your own viewer. 
	However, we do ask if you plan to embed the viewer in your own site, that it not just be an unmodified 
	version. Please re-skin it or build upon it.

We are using this component as an independent component to render PDF content in Pinpoint Mobile. When
rendering PDF content and the application is configured to use the "Advanced Viewer", the Pinpoint 
Mobile application will either embed the viewer.html page within an IFRAME element or open the viewer.html
page as an external window. 

Note that for iOS, displaying this version of the Advanced Viewer embedded will hijack user-input even after
the viewer is closed. This seems to be a problem with how iOS handles this IFRAME. For iOS, the code will 
always open the Advanced Viewer as an external window.

The original PDF.js Viewer was modified from the one provided by Mozilla. We have customized the sizing of
the toolbars, icons, and text to be about 50% larger to provide better usability on smaller devices. The 
styling changes for this were done in a newly created viewer-mobile-overrides.css file that is now being 
included into the viewer.html file after the original CSS so that it can override the necessary styling.
Furthermore, we have also made a small modification to viewer.js to include the "outlineItemsHidden" className
on all table of content (TOC) togglers so that all expandable TOC nodes will be collapsed when the PDF loads:
    toggler.className = 'outlineItemToggler outlineItemsHidden';

RRATPCS-3802 updated pdf.js to the latest stable version (pdfjs-3.0.279-dist)
Update made to the following files, to include changes made to the previous version
1. Pinpoint Client/lib/adv_pdfviewer/build/pdf.worker.js
2. Pinpoint Client/lib/adv_pdfviewer/web/viewer.*