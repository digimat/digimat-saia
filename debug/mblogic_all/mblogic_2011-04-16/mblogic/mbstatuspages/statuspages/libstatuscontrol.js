/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatuscontrol.js
# Purpose: 	MBLogic status display library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		21-Jun-2010
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

// ##################################################################
/* This is for the system control page - communications status. This is
slightly different from the other sub-systems.
	Parameters:
		utillib (object) = The utility display library.
		statustexts (object) = The message definitions for status.
*/
function SysCommControlStat(utillib, statustexts) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;

	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		// Communications errors.
		// Set the data and status colour indicators.
		if (pageresults.length == 0) {
			stat = this.StatusTexts["ok"][1];
			displaytext = this.StatusTexts["ok"][0];
		} else {
			stat = this.StatusTexts["error"][1];
			displaytext = this.StatusTexts["error"][0] + ": " + pageresults.length;
		}
		this.Utils.TextStatMsg("commerrors", displaytext, stat);	

		// Display any error messages.

		// First, delete the table if it already exists.
		var errtable = document.getElementById("commerrortable");
		while (errtable.rows.length > 0) {
			errtable.deleteRow(-1);
		}

		// Now, add the new table data.
		// We limit the display to no more than 100 errors. 
		for (var err=0; (err < pageresults.length) && (err < 100); err++) {
			var trow = errtable.insertRow(-1);

			// Number the row.
			var cell = trow.insertCell(0);
			var celltext = document.createTextNode(parseInt(err) + 1);
			cell.appendChild(celltext);

			// Error message.
			var cell = trow.insertCell(1);
			var celltext = document.createTextNode(pageresults[err]);
			cell.appendChild(celltext);
		}

		// Show the error table if there are any errors.
		var errordisplay = document.getElementById("commerrordisplay");
		if (pageresults.length > 0) {
			errordisplay.setAttribute("class", "datashow");
		} else {
			errordisplay.setAttribute("class", "datahide");
		}

	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################



// ##################################################################
/* This is for the system control page - common status display.
	Parameters:
		utillib (object) = The utility display library.
		statustexts (object) = The message definitions for status.
		datakey (string) = Key for retrieving data from object.
		statusid (string) = Web page ID for writing data.
		messlistid (string) = Web page ID for writing data to the display table.
		sectionid (string) = Web page ID for unhiding data.
*/
function SysControlStat(utillib, statustexts, datakey, statusid, messlistid, sectionid) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;

	// Key for retrieving data from object.
	this._DataKey = datakey;
	// Web page ID for writing data.
	this._StatusID = statusid;

	// Web page ID for writing data to the display table.
	this._MessageListID = messlistid;
	// Web page ID for unhiding data.
	this._ShowSectionID = sectionid;



	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		// Set the data and status colour indicators.
		if (pageresults[this._DataKey].length == 0) {
			stat = this.StatusTexts["ok"][1];
			displaytext = this.StatusTexts["ok"][0];
		} else {
			stat = this.StatusTexts["error"][1];
			displaytext = pageresults[this._DataKey].length + " errors";
		}
		this.Utils.TextStatMsg(this._StatusID, displaytext, stat);	

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



