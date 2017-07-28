/** ##########################################################################
# Project: 	MBLogic
# Module: 	libsysstatus.js
# Purpose: 	MBLogic status display library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		01-Jun-2010
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
/* This controls the system status summary page. This is split over two
	classes because the data comes from more than one source.
Parameters: utillib (object) = The utility display library.
*/
function SysStatSummary(utillib) {

	// Utility library
	this.Utils = utillib;


	this.CheckList = ["servername", "softname", "softversion", "starttime"];
	this.LastResult = [];

	for (var index in this.CheckList) {
		this.LastResult[index] = null;
	}

	this.StartDate = 0.0;
	this.LastTime = null;

	// ##################################################################
	// Update the page results.
	function _UpdatePageResults(pageresults) {
		// Check to see if there have been any changes since the last scan.
		var updated = false;
		for (var index in this.CheckList) {
			if (this.LastResult[index] != pageresults[this.CheckList[index]]) {
				this.LastResult[index] = pageresults[this.CheckList[index]];
				var updated = true;
			}
		}

		// Only update data that changes.
		if (updated) {
			// Fill the tables with data only.
			this.Utils.ShowCell("servername", pageresults["servername"]);
			this.Utils.ShowCell("softname", pageresults["softname"]);
			this.Utils.ShowCell("softversion", pageresults["softversion"]);

			// We need to format the date.
			this.StartDate = new Date(pageresults["starttime"] * 1000.0);
			this.Utils.ShowCell("starttime", this.StartDate.toLocaleString());
		}

		// Check to see if the uptime calculation has changed.
		try {var newtime = (parseInt(pageresults["uptime"]) / 3600.0).toFixed(2); }
			catch (e) {var newtime = e; }
		if (newtime != this.LastTime) {
			this.Utils.ShowCell("uptime", newtime);
			this.LastTime = newtime;
		}
	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################
/* Parameters: utillib (object) = The utility display library.
	statustexts (object) = The message definitions for status.
	plcstattexts (object) = The message definitions for soft logic status.
*/
function SubSysStatSummary(utillib, statustexts, plcstattexts) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;
	this.PLCStatTexts = plcstattexts;

	this.CheckList = ["tcpservercount", "tcpserverstat", 
			"tcpclientcount", "tcpclientstat", 
			"genclientcount", "genclientstat",  
			"hmistat", "plciostat", "plcrunmode"];

	this.LastResult = [];

	for (var index in this.CheckList) {
		this.LastResult[index] = null;
	}


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
		cellref.setAttribute("class", status);
	}
	this.SetCellDataAndStatus = _SetCellDataAndStatus;


	// ##################################################################
	// Update the page results.
	function _UpdatePageResults(pageresults) {

		// Check to see if there have been any changes since the last scan.
		var updated = false;
		for (var index in this.CheckList) {
			if (this.LastResult[index] != pageresults[this.CheckList[index]]) {
				this.LastResult[index] = pageresults[this.CheckList[index]];
				var updated = true;
			}
		}

		// Only update on change.
		if (updated) {

			// These ones display a number with a status colour.
			// Set the data and status colour indicators.
			this.SetCellDataAndStatus("servercount", pageresults["tcpservercount"], 
							this.StatusTexts[pageresults["tcpserverstat"]][1]);	
			// Set the data and status colour indicators.
			this.SetCellDataAndStatus("tcpclienterrors", pageresults["tcpclientcount"], 
							this.StatusTexts[pageresults["tcpclientstat"]][1]);	
			this.SetCellDataAndStatus("genclienterrors", pageresults["genclientcount"], 
							this.StatusTexts[pageresults["genclientstat"]][1]);	

			// These ones display the more conventional Ok or other code.
			this.Utils.TextStat("hmiconfigerrors", pageresults["hmistat"], this.StatusTexts);
			this.Utils.TextStat("plcconfigerrors", pageresults["plciostat"], this.StatusTexts);
			this.Utils.TextStat("plcrunmode", pageresults["plcrunmode"],  this.PLCStatTexts);
		} 
	}
	this.UpdatePageResults = _UpdatePageResults;
}
// ##################################################################




