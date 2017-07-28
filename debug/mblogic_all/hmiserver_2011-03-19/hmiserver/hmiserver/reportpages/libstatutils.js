/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatutils.js
# Purpose: 	MBLogic utility library.
# Language:	javascript
# Date:		02-Jun-2010
# Ver:		03-Jun-2010
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

/*

This contains functions and data which are used in a number of different status
control libraries.

*/

// ##################################################################
// Get the subroutine name from a query string. This assumes the url is in the
// form of something like this:
// http://localhost:8080/statuspages/ildisplay.html?subrname=Alarms
function GetSubrnameFromQueryString(qstring) {
	// Get the URL string from the web page and convert it to a string.
	var pageurl = document.location.toString();
	// Split the string into path and query options.
	var urlsegs = pageurl.split("?");
	// Split the subroutine name from the query string.
	var querysegs = urlsegs[1].split("=");
	var subrname = querysegs[1];

	return subrname
}



// ##################################################################
function libstatutils() {

	// This is used to give table rows alternating colours.
	this.TRowCounter = 0;
	this.TRowColours = ["t1", "t2"];

	// ##################################################################
	// Resets the alternating row colour counter to the initialised value.
	function _TRowStart() {
		this.TRowCounter = 0;
	}
	this.TRowStart = _TRowStart;

	// ##################################################################
	// Returns the next value for an alternating row CSS style.
	function _TRowAlternate() {
		if (this.TRowCounter == 0) {
			this.TRowCounter = 1;
			return this.TRowColours[0];
		} else {
			this.TRowCounter = 0;
			return this.TRowColours[1];
		}
	}
	this.TRowAlternate = _TRowAlternate;


	// ##################################################################
	// Display a status inside an existing table cell, replacing any existing text.
	// This will insert a standard text description and set the background colour
	// to one appropriate for the status. The message and style are lookedup
	// from a supplied object using "stat" as a key.
	// Parameters: id (string) = The id of a page element.
	//	stat (string) = The status key.
	//	statmsg (object) = An object literal to use to look up the text message
	//		and CSS style to use. 
	function _TextStat(id, stat, statmsg) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 
		try {var msg = statmsg[stat][0]; }
			catch (e) {var msg = e; }
		try {var colour = statmsg[stat][1]; }
			catch (e) {var colour = ""; }
		// Set the background colour.
		cellref.setAttribute("class", colour);
		// Add the text and insert it in the page. 
		cellref.appendChild(document.createTextNode(msg));
	}
	this.TextStat = _TextStat;


	// ##################################################################
	// Display a status inside an existing table cell, replacing any existing text.
	// This will insert a standard text description and set the background colour
	// to one appropriate for the status. 
	// Parameters: id (string) = The id of a page element.
	//	msg (string) = The message to display.
	//	statstyle (object) = The CSS style to apply.
	function _TextStatMsg(id, msg, statstyle) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 

		// Set the background colour.
		cellref.setAttribute("class", statstyle);
		// Add the text and insert it in the page. 
		cellref.appendChild(document.createTextNode(msg));
	}
	this.TextStatMsg = _TextStatMsg;


	// ##################################################################
	/* Add a row to a table and insert a text message and background colour.
	 This will insert a standard text description and set the background colour
	 to one appropriate for the status. The message and style are lookedup
	 from a supplied object using "stat" as a key.
	 Parameters: trow (object) = The table row to insert into.
	 	cellcolum (integer) = The cell column to create.
		stat (string) = The status key.
		statmsg (object) = An object literal to use to look up the text message
			and CSS style to use. 
	*/
	function _TextListStat(trow, cellcolum, stat, statmsg) {
		var cellref = trow.insertCell(cellcolum);

		try {var msg = statmsg[stat][0]; }
			catch (e) {var msg = e; }
		try {var colour = statmsg[stat][1]; }
			catch (e) {var colour = ""; }
		// Set the background colour.
		cellref.setAttribute("class", colour);
		// Add the text and insert it in the page. 
		cellref.appendChild(document.createTextNode(msg));
	}
	this.TextListStat = _TextListStat;








	
	// ##################################################################
	// This is used to insert new information into a table which 
	// is allowed to grow in length.
	function _InsertTableStatus(trow, cellcolum, stat, statmsg) {
			var cell = trow.insertCell(cellcolum);
			var celltext = document.createTextNode(statmsg[stat][0]);
			cell.setAttribute("class", statmsg[stat][1]);
			cell.appendChild(celltext);
	}
	this.InsertTableStatus = _InsertTableStatus;


	// ##################################################################
	// This is used to insert new information into a table which 
	// is allowed to grow in length.
	function _InsertTableCell(trow, cellcolum, text, tdclass) {
			var cell = trow.insertCell(cellcolum);
			var celltext = document.createTextNode(text);
			if (tdclass != "") {
				cell.setAttribute("class", tdclass);
			}
			cell.appendChild(celltext);
	}
	this.InsertTableCell = _InsertTableCell;

	// ##################################################################
	// Update the contents of a table cell. This is for tables
	// with a fixed number of cells and ids for each addressable cell.
	function _ShowCell(id, text){
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 

		// Add the new cell text.
		cellref.appendChild(document.createTextNode(text));
	}
	this.ShowCell = _ShowCell;


	// ##################################################################
	// This inserts links into the table, instead of just text.
	function _InsertTableLink(trow, cellcolum, linkname, title, tdclass) {
			var cell = trow.insertCell(cellcolum);
			var viewlink = document.createElement("a");
			viewlink.setAttribute("href", linkname);
			var actionname = document.createTextNode(title);
			viewlink.appendChild(actionname);
			cell.setAttribute("class", tdclass);
			cell.appendChild(viewlink);
	}
	this.InsertTableLink = _InsertTableLink;






	// ##################################################################
	// This is used to insert new text information into a table which 
	// is allowed to grow in length.
	function _InsertTableText(trow, cellcolum, text, tdclass) {
			var cell = trow.insertCell(cellcolum);
			var celltext = document.createTextNode(text);
			if (tdclass.length > 0) {
				cell.setAttribute("class", tdclass);
			}
			cell.appendChild(celltext);
	}
	this.InsertTableText = _InsertTableText;




	// ##################################################################
	// Set the appropriate cell data and status for each cell.
	function _SetCellDataAndStatus(cellid, celldata, status) {
		var cellref = document.getElementById(cellid);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 

		cellref.appendChild(document.createTextNode(celldata));
		cellref.setAttribute("class", StatusStyle[status]);
	}
	this.SetCellDataAndStatus = _SetCellDataAndStatus;


	// ##################################################################
	// Set the display attribute of a section of a web page to display
	// a hidden area of the page. This relies on the CSS class for "datashow".
	function _ShowPageArea(id) {
		document.getElementById(id).setAttribute("class", "datashow");
	}
	this.ShowPageArea = _ShowPageArea;

	// ##################################################################
	// Set the display attribute of a section of a web page to hide
	// a hidden area of the page.This relies on the CSS class for "datahide".
	function _HidePageArea(id) {
		document.getElementById(id).setAttribute("class", "datahide");
	}
	this.HidePageArea = _HidePageArea;


	// ##################################################################
	// Set the CSS style attribute of a list of tables to show 
	// special effects when in edit mode.
	// Parameters: (array) = An array of ids corresponding to each table.
	function _SetTableListToEditEffects(idlist) {
		for (var i in idlist) {
			var id = idlist[i];
			document.getElementById(id).setAttribute("class", "edittable");
		}
	}
	this.SetTableListToEditEffects = _SetTableListToEditEffects;

	// ##################################################################
	// Set the CSS style attribute of a list of tables to normal display mode.
	// (e.g. when the table are not editable).
	// Parameters: (array) = An array of ids corresponding to each table.
	function _SetTableListToNormalEffects(idlist) {
		for (var i in idlist) {
			var id = idlist[i];
			document.getElementById(id).setAttribute("class", "displaytable");
		}
	}
	this.SetTableListToNormalEffects = _SetTableListToNormalEffects;

}
// ##################################################################
