/** ##########################################################################
# Project: 	MBLogic
# Module: 	libhmimsgsmon.js
# Purpose: 	MBLogic HMIServer protocol message display library.
# Language:	javascript
# Date:		16-Nov-2010
# Ver:		16-Nov-2010
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
/* This controls the HMI message monitor page. 
Parameters: utillib (object) = The utility display library.
*/
function HMIMsgDisplay(utillib) {

	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Update the page results.
	function _UpdatePageResults(pageresults) {

		var msghmitable = document.getElementById("msghmitable");
		var reqdata = pageresults["req"];
		var respdata = pageresults["resp"];
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (msghmitable.rows.length > 1) {
			msghmitable.deleteRow(-1);
		}


		// Display the table data.
		for (var msgindex in reqdata) {
			var reqmsg = reqdata[msgindex];
			var respmsg = respdata[msgindex];

			var trow = msghmitable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Request.
			this.Utils.InsertTableCell(trow, 0, String(reqmsg).replace(/,"/g, ", \""), tdclass);
			// Response.
			this.Utils.InsertTableCell(trow, 1, String(respmsg).replace(/,"/g, ", \""), tdclass);
		}
	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################



// ##################################################################
/* This controls the field device message monitor page. 
Parameters: utillib (object) = The utility display library.
*/
function FieldMsgDisplay(utillib) {

	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Update the page results.
	function _UpdatePageResults(pageresults) {

		var msghmitable = document.getElementById("msgfieldtable");
		var reqdata = pageresults["req"];
		var respdata = pageresults["resp"];
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (msghmitable.rows.length > 1) {
			msghmitable.deleteRow(-1);
		}


		// Display the table data.
		for (var msgindex in reqdata) {
			var reqmsg = reqdata[msgindex];
			var respmsg = respdata[msgindex];

			var trow = msghmitable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Request.
			this.Utils.InsertTableCell(trow, 0, String(reqmsg).replace(/,"/g, ", \""), tdclass);
			// Response.
			this.Utils.InsertTableCell(trow, 1, String(respmsg).replace(/,"/g, ", \""), tdclass);
		}
	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################



