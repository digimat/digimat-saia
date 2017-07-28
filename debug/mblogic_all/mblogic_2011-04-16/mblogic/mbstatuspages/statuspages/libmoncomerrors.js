/** ##########################################################################
# Project: 	MBLogic
# Module: 	libmoncomerrors.js
# Purpose: 	MBLogic status monitor comm errors library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		18-Jun-2010
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
/* This is for communications errors details.
Parameters: utillib (object) = The utility display library.
	constatusmsg (object) = The message definitions for connections status.
	cmdstatusmsg (object) = The message definitions for command status.
*/
function ComMonErrors(utillib, constatusmsg, cmdstatusmsg) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.ConStatusMsg = constatusmsg;
	this.CmdStatusMsg = cmdstatusmsg;


	// We use these to keep track of whether anything has changed.
	this.LastSumResults = {"constatus" : "", "cmdsummary" : ""};
	this.LastCmdResults = {};
	this.LastCmdKeys = [];

	// Last connection and command events.
	this.LastConnectionEvent = 0;
	this.LastCommandEvent = 0;

	// If true, the connection name has already been displayed.
	this.NameDisplayed = false;

	// Last client messge displayed.
	this.LastCMessage = ''


	// ##################################################################
	// Display the summary values.
	function _DisplaySummary(pageresults) {
		// Check to see if there are any changes.
		if ((pageresults["constatus"] != this.LastSumResults["constatus"]) ||
				(pageresults["cmdsummary"] != this.LastSumResults["cmdsummary"])) {

			this.LastSumResults["constatus"] = pageresults["constatus"];
			this.LastSumResults["cmdsummary"] = pageresults["cmdsummary"];


			// Update the display.
			this.Utils.TextStat("constatus", pageresults["constatus"], this.ConStatusMsg);
			this.Utils.TextStat("cmdsummary", pageresults["cmdsummary"], this.CmdStatusMsg);
		}
	}
	this.DisplaySummary = _DisplaySummary;


	// ##################################################################
	function _DisplayCommandStatus(pageresults) {


		// Get the data keys and sort them.
		var cmdstat = pageresults["cmdstatus"];
		// Sort the keys before displaying the data.
		var statkeys = [];
		for (var cmd in cmdstat) {
			statkeys.push(cmd);
		}
		statkeys.sort();


		// Check to see if anything has changed.
		var cmdchanged = false;
		// First check to see if the properties are the same.
		if (statkeys != this.LastCmdKeys) {
			var cmdchanged = true;
		} else {
			// Now check to see if the values have changed.
			for (var cmd in cmdstat) {
				if (cmdstat[cmd] != this.LastCmdResults) {
					var cmdchanged = true;
				}
			}
		}


		// Something has changed. Save the results for the next cycle.
		this.LastCmdKeys = statkeys;
		this.LastCmdResults = cmdstat;


		// Delete the table if it already exists.
		var cmdtable = document.getElementById("commandstatus");
		while (cmdtable.rows.length > 1) {
			cmdtable.deleteRow(-1);
		}

		// Display the new data.
		this.Utils.TRowStart();
		for (var cmdindex in statkeys) {
			var cellstype = this.Utils.TRowAlternate();
			var cmd = statkeys[cmdindex];
			var trow = cmdtable.insertRow(-1);
			this.Utils.InsertTableCell(trow, 0, cmd, cellstype);
			this.Utils.TextListStat(trow, 1, cmdstat[cmd][1], this.CmdStatusMsg);
		}

		
	}
	this.DisplayCommandStatus = _DisplayCommandStatus;



	// ##################################################################
	// Display the client connection log.
	function _DisplayConnectionLog(pageresults) {

		// This is a reference to the data we want.
		var loglist = pageresults["coneventbuff"];

		// Check to see if the data has changed since the last time. We
		// Check the last time stamp to see if it is newer.
		if (loglist.length > 0) {
			var newdate = loglist[loglist.length - 1][0];
			if (this.LastConnectionEvent == newdate) {
				return;
			} else {
				this.LastConnectionEvent = newdate;
			}
		}


		// First, delete the table if it already exists.
		var logtable = document.getElementById("connectionlog");
		while (logtable.rows.length > 1) {
			logtable.deleteRow(-1);
		}


		// Now, display the data in a table.
		for (var msgindex in loglist) {
			var trow = logtable.insertRow(-1);
			var msg = loglist[msgindex];

			// Date.
			var cell = trow.insertCell(0);
			var date = new Date(msg[0] * 1000.0);
			var celltext = document.createTextNode(date.toLocaleString());
			cell.appendChild(celltext);

			// Message.
			var cell = trow.insertCell(1);
			var celltext = document.createTextNode(this.ConStatusMsg[msg[1]][0]);
			cell.setAttribute("class", this.ConStatusMsg[msg[1]][1]);
			cell.appendChild(celltext);
		}

	}
	this.DisplayConnectionLog = _DisplayConnectionLog;



	// ##################################################################
	// Display the client command log.
	function _DisplayCommandLog(pageresults) {

		// This is a reference to the data we want.
		var loglist = pageresults["cmdeventbuff"];

		// Check to see if the data has changed since the last time. We
		// Check the last time stamp to see if it is newer.
		if (loglist.length > 0) {
			var newdate = loglist[loglist.length - 1][0];
			if (this.LastCommandEvent == newdate) {
				return;
			} else {
				this.LastCommandEvent = newdate;
			}
		}


		// First, delete the table if it already exists.
		var logtable = document.getElementById("commandlog");
		while (logtable.rows.length > 1) {
			logtable.deleteRow(-1);
		}


		// Now, display the data in a table.
		for (var msgindex in loglist) {
			var trow = logtable.insertRow(-1);
			var msg = loglist[msgindex];

			// Date.
			var cell = trow.insertCell(0);
			var date = new Date(msg[0] * 1000.0);
			var celltext = document.createTextNode(date.toLocaleString());
			cell.appendChild(celltext);

			// Command name.
			var cell = trow.insertCell(1);
			var celltext = document.createTextNode(msg[1]);
			cell.appendChild(celltext);

			// Message.
			var cell = trow.insertCell(2);
			var celltext = document.createTextNode(this.CmdStatusMsg[msg[3]][0]);
			cell.setAttribute("class", this.CmdStatusMsg[msg[3]][1]);
			cell.appendChild(celltext);
		}

	}
	this.DisplayCommandLog = _DisplayCommandLog;



	// ##################################################################
	// Display the client message log.
	function _DisplayClientMessageLog(pageresults) {

		// This is a reference to the data we want.
		var loglist = pageresults["clientmsgs"];

		// Check to see if the data has changed since the last time. We
		// Check the last time stamp to see if it is newer.
		if (loglist.length > 0) {
			var newmessage = loglist[loglist.length - 1];
			if (this.LastCMessage == newmessage) {
				return;
			} else {
				this.LastCMessage = newmessage;
			}

		}

		// Anything after this point assumes the table needs updating.

		// Decide whether to show or hide the table. 
		var tableshow = document.getElementById("clientmsgsdisplay");
		if (loglist.length > 0) {
			tableshow.setAttribute("class", "datashow");
		} else {
			tableshow.setAttribute("class", "datahide");
		}



		// First, delete the table if it already exists.
		var logtable = document.getElementById("messagelog");
		while (logtable.rows.length > 1) {
			logtable.deleteRow(-1);
		}


		// Now, display the data in a table.
		for (var msgindex in loglist) {
			var trow = logtable.insertRow(-1);
			var msg = loglist[msgindex];

			var cell = trow.insertCell(0);
			var celltext = document.createTextNode(msg);
			cell.appendChild(celltext);
		}

	}
	this.DisplayClientMessageLog = _DisplayClientMessageLog;



	// ##################################################################
	// Display the connection name.
	function _DisplayName(pageresults) {
		if (!this.NameDisplayed) {
			var heading = document.getElementById("clientlogheadingname");
			heading.appendChild(document.createTextNode(pageresults["connectionname"]));
			this.NameDisplayed = true;
		}
	}
	this.DisplayName = _DisplayName;

	// ##################################################################
	// Update the server and client results.
	function _UpdatePageResults(pageresults) {
		// Display the connection name.
		this.DisplayName(pageresults);
		// Display the summary.
		this.DisplaySummary(pageresults);
		// Show the command status.
		this.DisplayCommandStatus(pageresults);
		// Display the connection log.
		this.DisplayConnectionLog(pageresults);
		// Display the command log.
		this.DisplayCommandLog(pageresults);
		// Display the client message log.
		this.DisplayClientMessageLog(pageresults);

	}
	this.UpdatePageResults = _UpdatePageResults;

}
// ##################################################################


