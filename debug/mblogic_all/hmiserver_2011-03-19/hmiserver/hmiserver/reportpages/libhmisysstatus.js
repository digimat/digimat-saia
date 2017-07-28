/** ##########################################################################
# Project: 	MBLogic
# Module: 	libhmisysstatus.js
# Purpose: 	MBLogic HMIServer status display library.
# Language:	javascript
# Date:		14-Nov-2010
# Ver:		14-Nov-2010
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
/* This controls the system status summary page. 
Parameters: utillib (object) = The utility display library.
	wdid (string) = The watchdog table id.
	wdlimit (number) = The watchdog time limit (in milliseconds).
*/
function HMIStatSummary(utillib, wdid, wdlimit) {

	// Utility library
	this.Utils = utillib;

	// Watchdog limit.
	this.WDLimit = wdlimit;
	// Watchdog display id.
	this.WDid = wdid;


	// Server communications watchdog timer start time.
	var wdstart = new Date();
	this.WatchDogTime = wdstart.getTime();
	// True if the watchdog was tripped.
	this.WDTripped = false;
	// Initialise the display.
	this.Utils.TextStatMsg(this.WDid, "OK", "statusok");


	this.CheckList = ["serverid", "softname", "softversion", "starttime", 
				"configok", "commsok", "port", "timeout"];
	this.LastResult = [];

	for (var index in this.CheckList) {
		this.LastResult[index] = null;
	}

	this.StartDate = 0.0;
	this.LastTime = null;


	// ##################################################################
	// Check the watchdog.
	function _CheckWatchDog() {
		var wdnew = new Date();
		var currentime = wdnew.getTime();

		// Has the watchdog timed out?
		var wastripped = this.WDTripped;
		this.WDTripped = (currentime - this.WatchDogTime) > this.WDLimit;

		// Only update the display on a change of state.
		if (this.WDTripped && !wastripped) {
			this.Utils.TextStatMsg(this.WDid, "Time Out", "statusalert");
		}
		if (!this.WDTripped && wastripped) {
			this.Utils.TextStatMsg(this.WDid, "OK", "statusok");
		}
	}
	this.CheckWatchDog = _CheckWatchDog;



	// ##################################################################
	// Update the page display with the new list of HMI files.
	function _UpdateHMIFileList(pageresults) {

		var hmipagefiletable = document.getElementById("hmipagefiletable");
		var pagelist = pageresults["hmifilelist"];
		
		// The host and port information common to all HMI pages.
		var pagehost = "http://" + window.location.hostname + ":" + pageresults["port"] + "/";

		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (hmipagefiletable.rows.length > 1) {
			hmipagefiletable.deleteRow(-1);
		}

		// Display the table data.
		for (var pageindex in pagelist) {
			var page = pagelist[pageindex];

			var trow = hmipagefiletable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// HMI file name.
			this.Utils.InsertTableLink(trow, 0, pagehost + page, page, tdclass);
		}


	}
	this.UpdateHMIFileList = _UpdateHMIFileList;


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
			this.Utils.ShowCell("serverid", pageresults["serverid"]);
			this.Utils.ShowCell("softname", pageresults["softname"]);
			this.Utils.ShowCell("softversion", pageresults["softversion"]);

			// We need to format the date.
			this.StartDate = new Date(pageresults["starttime"] * 1000.0);
			this.Utils.ShowCell("starttime", this.StartDate.toLocaleString());

			// We display the status as text and as a colour.
			this.Utils.TextStatMsg("configok", pageresults["configok"], pageresults["configcolour"]);
			this.Utils.TextStatMsg("commsok", pageresults["commsok"], pageresults["commscolour"]);

			
			// The start parameters displayed depend on the program version.
			// If the field protocol port is specified, we assume it is a server version.
			if (pageresults["fport"] != "") {
				this.Utils.ShowCell("sport", pageresults["port"]);
				this.Utils.ShowCell("fport", pageresults["fport"]);
				this.Utils.ShowPageArea("serverstattable");
				this.Utils.HidePageArea("clientstattable");
			} else {
				this.Utils.ShowCell("cport", pageresults["port"]);
				this.Utils.ShowCell("remotehost", pageresults["remotehost"]);
				this.Utils.ShowCell("remoteport", pageresults["remoteport"]);
				this.Utils.ShowCell("timeout", pageresults["timeout"]);
				this.Utils.ShowCell("unitid", pageresults["unitid"]);
				this.Utils.HidePageArea("serverstattable");
				this.Utils.ShowPageArea("clientstattable");
			}

			// List of HMI file names.
			this.UpdateHMIFileList(pageresults);

		}

		// Check to see if the uptime calculation has changed.
		try {var newtime = pageresults["uptime"]; }
			catch (e) {var newtime = e; }
		if (newtime != this.LastTime) {
			this.Utils.ShowCell("uptime", newtime);
			this.LastTime = newtime;
		}

		// Reset the watchdog timer.
		var wdstart = new Date();
		this.WatchDogTime = wdstart.getTime();

	}
	this.UpdatePageResults = _UpdatePageResults;
}

// ##################################################################



