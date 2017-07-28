/** ##########################################################################
# Project: 	MBLogic
# Module: 	libprogcontrol.js
# Purpose: 	MBLogic program control library.
# Language:	javascript
# Date:		02-Jun-2010
# Ver:		09-Aug-2010
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBLogic.
# MBLogic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# MBLogic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with MBLogic. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################
**/


// ############################################################################
/* This controls the program view/edit page.
	Parameters: utillib (object) = The utility display library.
*/
function ProgControl(utillib) {

	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		var subrtable = document.getElementById("subrtable");
		// First, delete the table (but not the header) if it already exists.
		while (subrtable.rows.length > 1) {
			subrtable.deleteRow(-1);
		}

		this.Utils.TRowStart();
		for (subr in pageresults) {
			var trow = subrtable.insertRow(-1);
			var subrname = pageresults[subr]

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// First cell is the subroutine name.
			this.Utils.InsertTableText(trow, 0, subrname, tdclass);

			// Fourth cell is a link to editing the subroutine in ladder.
			//this.Utils.InsertTableLink(trow, 1, "laddereditor.xhtml?subrname=" + subrname, "Edit Ladder", tdclass);

			// Fifth cell is a link to editing the subroutine in IL.
			this.Utils.InsertTableLink(trow, 1, "ileditor.html?subrname=" + subrname, "Edit IL", tdclass);

			// Fifth cell is a link to a check box which selects the subroutine to delete.
			var cell = trow.insertCell(2);
			var viewlink = document.createElement("input");
			viewlink.setAttribute("type", "checkbox");
			viewlink.setAttribute("name", "deletesub");
			viewlink.setAttribute("value", subrname);
			cell.appendChild(viewlink);
			cell.setAttribute("class", tdclass);

		}
	}
	this.UpdatePageResults = _UpdatePageResults;

}
// ############################################################################


// ############################################################################
/* This displays IL for a single subroutine.
*/
function ProgILDisplay() {


	// ##################################################################
	// Populate the IL display with the IL source text.
	function _UpdatePageResults(plcsource) {

		// IL source.
		var ilblock = document.getElementById("illistblock");
		var iltext = [];
		// Accumulate all the IL text into an single block and add it to the page.
		var sourcelist = plcsource["subrdata"];
		for (var linenumb in sourcelist) {
			var iltext = iltext.concat(sourcelist[linenumb]["ildata"], ["\n"]);
		}

		var linetext = document.createTextNode(iltext.join(""));
		ilblock.appendChild(linetext);

		// Subroutine comments.
		var sbrcomments = document.getElementById("sbrcomments");
		var comments = document.createTextNode(plcsource["subrcomments"]);
		sbrcomments.appendChild(comments);
		

	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Show the subroutine name in the headings.
	function _PopulateHeadings(subrname) {


		// Heading.
		var subrtitle = document.getElementById("subrheading");
		var celltext = document.createTextNode(subrname);
		subrtitle.appendChild(celltext);
	
	}
	this.PopulateHeadings = _PopulateHeadings;

}
// ############################################################################



// ############################################################################
/* This This handles intialising the IL editor for a single subroutine.
	Parameters: utillib (object) = The utility display library.
*/
function ProgILEdit(utillib) {

	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Populate the form with the IL text and any error messages.
	function _UpdatePageResults(plcsource) {

		// Subroutine comments.
		document.forms.ileditor.subrcomments.value = plcsource["subrcomments"];


		// IL subroutine content.
		var iltext = [];
		// Accumulate all the IL text into an single block and add it to the page.
		var sourcelist = plcsource["subrdata"];
		for (var linenumb in sourcelist) {
			var iltext = iltext.concat(sourcelist[linenumb]["ildata"], ["\n"]);
		}

		document.forms.ileditor.content.value = iltext.join("");

		// Delete any existing error messages.
		var errortable = document.getElementById("errortable");
		// First, delete the table if it already exists.
		while (errortable.rows.length > 0) {
			errortable.deleteRow(-1);
		}
		
		pageresults = plcsource["plccompilemsg"];
		for (err in pageresults) {
			var trow = errortable.insertRow(-1);

			// First cell is just a counter.
			this.Utils.InsertTableText(trow, 0, err + 1, "");
			// Second cell is the error messag.
			this.Utils.InsertTableText(trow, 1, pageresults[err], "");
		}

		// Show the error table if there are any errors.
		var errordisplay = document.getElementById("pagestatus");
		if (pageresults.length > 0) {
			errordisplay.setAttribute("class", "datashow");
		} else {
			errordisplay.setAttribute("class", "datahide");
		}

	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Show the subroutine name in the headings.
	function _PopulateHeadings(subrname) {

		// Heading.
		var subrtitle = document.getElementById("subrheading");
		var celltext = document.createTextNode(subrname);
		subrtitle.appendChild(celltext);

	}
	this.PopulateHeadings = _PopulateHeadings;


	// ##################################################################
	// Format a request message to save the IL data.
	function _FormatSaveRequest(subrname) {
		var reqobj = {}
		reqobj["subrcomments"] = document.forms.ileditor.subrcomments.value;
		reqobj["subrname"] = subrname;
		reqobj["signature"] = 0;

		// This has to be formatted in a way that is compatible with 
		// the ladder editor. Therefor, we make the block of IL look 
		// like one big rung.
		reqobj["subrdata"] = [];
		ildata = document.forms.ileditor.content.value;
		reqobj["subrdata"].push({"ildata" : ildata.split("\n"), "comment" : "", "matrixdata" : [], "rungtype" : "il"});

		return reqobj;
	}
	this.FormatSaveRequest = _FormatSaveRequest;



}
// ############################################################################


// ##################################################################
/* Display edit error messages.
	Parameters:
		utillib (object) = The utility display library.
		statustexts (object) = The message definitions for status.
		datakey (string) = Key for retrieving data from object.
		messlistid (string) = Web page ID for writing data to the display table.
		sectionid (string) = Web page ID for unhiding data.
*/
function DisplayErrors(utillib, statustexts, datakey, messlistid, sectionid) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;

	// Key for retrieving data from object.
	this._DataKey = datakey;

	// Web page ID for writing data to the display table.
	this._MessageListID = messlistid;
	// Web page ID for unhiding data.
	this._ShowSectionID = sectionid;



	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {


		// Display any error messages.
		// First, delete the table if it already exists.
		var errtable = document.getElementById(this._MessageListID);
		while (errtable.rows.length > 0) {
			errtable.deleteRow(-1);
		}

		// Now, add the new table data.
		// We limit the display to no more than 100 errors. 
		for (var err=0; (err < pageresults[this._DataKey].length) && (err < 100); err++) {
			var trow = errtable.insertRow(-1);

			// Number the row.
			var cell = trow.insertCell(0);
			var celltext = document.createTextNode(parseInt(err) + 1);
			cell.appendChild(celltext);

			// Error message.
			var cell = trow.insertCell(1);
			var celltext = document.createTextNode(pageresults[this._DataKey][err]);
			cell.appendChild(celltext);
		}

		// Show the error table if there are any errors.
		var errordisplay = document.getElementById(this._ShowSectionID);
		if (pageresults[this._DataKey].length > 0) {
			errordisplay.setAttribute("class", "datashow");
		} else {
			errordisplay.setAttribute("class", "datahide");
		}

	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################




