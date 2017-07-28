/** ##########################################################################
# Project: 	MBLogic
# Module: 	ladmonitor.js
# Purpose: 	MBLogic ladder monitor library.
# Language:	javascript
# Date:		24-Aug-2010
# Ver:		24-Aug-2010
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
/* Monitor the soft logic data table to update the live ladder display.
*/
function LadderMonitor() {

	this.MonitorList = null;

	// ##################################################################
	// Set the new live ladder monitor data access.
	function _SetMonitorList(monitordata) {
		this.MonitorList = monitordata;
	}
	this.SetMonitorList = _SetMonitorList;



	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		// Go through the list of monitored items and update the instruction display.
		for (var i in this.MonitorList) {

			// The data specifying how to monitor this item.
			var monitoritem = this.MonitorList[i]["monitor"];
			var monitortype = monitoritem[0];
			var displaystate = false;

			// This should cover all boolean data.
			if (monitortype in {"bool" : 0, "booln" : 0}) {
				// The data we want to check.
				var primarydata = pageresults[monitoritem[1]];

				// Find out what type of monitoring is required.
				switch (monitortype) {
					// Is it a boolean instruction?
					case "bool" : { var displaystate = primarydata; break; }
					// Is it a boolean instruction with negative logic?
					case "booln" : { var displaystate = !primarydata; break; }
				}
			}

			// This should cover compares. 
			if (monitortype in {"=" : 0, "!=" : 0, ">" : 0, "<" : 0, ">=" : 0, "<=" : 0}) {
				if (monitoritem[1] != "") {
					var primarydata = pageresults[monitoritem[1]];
				} else {
					var primarydata = monitoritem[3];
				}
				if (monitoritem[2] != "") {
					var secondarydata = pageresults[monitoritem[2]];
				} else {
					var secondarydata = monitoritem[4];
				}
				// Find out what type of monitoring is required.
				switch (monitortype) {
					// These are compare of two words.
					case "=" : {var displaystate = (primarydata == secondarydata); break; }
					case "!=" : {var displaystate = (primarydata != secondarydata); break; }
					case ">" : {var displaystate = (primarydata > secondarydata); break; }
					case "<" : {var displaystate = (primarydata < secondarydata); break; }
					case ">=" : {var displaystate = (primarydata >= secondarydata); break; }
					case "<=" : {var displaystate = (primarydata <= secondarydata); break; }
				}
			}


			// This is the "id" of the page element that we will update.
			var instrref = document.getElementById(this.MonitorList[i]["id"]);

			// Update the element according to the data.
			if (displaystate) {
				instrref.setAttribute("class", "MB_ladderon");
			} else {
				instrref.setAttribute("class", "MB_ladderoff");
			}
		}
	}
	this.UpdatePageResults = _UpdatePageResults;


}

// ##################################################################

