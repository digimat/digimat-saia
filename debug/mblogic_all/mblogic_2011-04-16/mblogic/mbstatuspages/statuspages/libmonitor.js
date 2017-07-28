/** ##########################################################################
# Project: 	MBLogic
# Module: 	libmonitor.js
# Purpose: 	MBLogic status monitor library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		27-Jun-2010
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
/* This is for the soft logic run status.
	Parameters:
		utillib (object) = The utility display library.
		statustexts (object) = The message definitions for status.
*/
function PLCRunStatus(utillib, statustexts) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;

	// We use this to keep track of whether anything has changed.
	this.LastResults = {"runmode" : "",
			"plcinstrcount" : 0,
			"scancount" : 0,
			"scantime" : 0,
			"minscan" : 0,
			"maxscan" : 0,
			"plcexitcode" : "",
			"plcexitsubr" : "",
			"plcexitrung" : 0
			};

	// ##################################################################
	// Only update fields that have changed. We assume the web page id
	// is the same name as the data key.
	function _UpdateField(pageresults, key) {
		if (pageresults[key] != this.LastResults[key]) {
			this.Utils.ShowCell(key, pageresults[key]);
			pageresults[key] == this.LastResults[key];
		}
	}
	this.UpdateField = _UpdateField;



	// ##################################################################
	// Show the soft logic run status. We take some extra pains in avoiding 
	// updates on each field because some fields are more subject to change 
	// than others.
	function _UpdatePageResults(pageresults) {


		this.UpdateField(pageresults, "runmode");

		if (pageresults["runmode"] != this.LastResults["runmode"]) {
			this.Utils.TextStat("runmode", pageresults["runmode"], this.StatusTexts);
			pageresults["runmode"] == this.LastResults["runmode"];
		}

		this.UpdateField(pageresults, "plcinstrcount");

		this.UpdateField(pageresults, "scancount");
		this.UpdateField(pageresults, "scantime");
		this.UpdateField(pageresults, "minscan");
		this.UpdateField(pageresults, "maxscan");

		this.UpdateField(pageresults, "plcexitcode");
		this.UpdateField(pageresults, "plcexitsubr");
		this.UpdateField(pageresults, "plcexitrung");

	}
	this.UpdatePageResults = _UpdatePageResults;


}

// ##################################################################



// ##################################################################
/* This is for the communication status for all communications.
	Parameters:
		utillib (object) = The utility display library.
		cmdstattexts (object) = The message definitions for command status.
		constattexts (object) = The message definitions for connection status.
*/
function ComStatus(utillib, cmdstattexts, constattexts) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.CmdStatTexts = cmdstattexts;
	this.ConStatTexts = constattexts;

	// We use this to keep track of whether anything has changed.
	this.LastServerResults = [];

	// We use this to keep track of whether anything has changed.
	this.LastClientResults = [];


	// ##################################################################
	// Update the page display with the new data.
	function _UpdateServerResults(pageresults) {

		// Check to see if any data has changed.
		// If the length has changed, we have a new configuration. 
		var serverchanged = false;
		if (pageresults.length == this.LastServerResults.length) {
			// Now, check if any of the individual data have changed.
			for (server in pageresults) {
				var newserver = pageresults[server];
				var lastserver = this.LastServerResults[server];

				// Apply a bit of hysteresis to the connection rate changes.
				var requestrate = newserver["requestrate"];
				var oldreqrate = lastserver["requestrate"];
				var hysteresis = requestrate * 0.1;
				// Apply a minimum hysteresis.
				if (hysteresis < 2) {
					var hysteresis = 2;
				}

				var reqchanged = false;
				// Make sure we catch any transitions to zero.
				if ((requestrate == 0) && (oldreqrate != 0)) {
					var reqchanged = true;
				}

				if ((requestrate > (oldreqrate + hysteresis)) || (requestrate < (oldreqrate - hysteresis))) {
					var reqchanged = true;
				}
				

				// Check for changes. 
				if ((newserver["servername"] != lastserver["servername"]) ||
					(newserver["connectioncount"] != lastserver["connectioncount"]) || 
					reqchanged) {
					var serverchanged = true;
				}
			}
		} else {
			var serverchanged = true;
		}


		// If no server data has changed, then we don't need to do any updates.
		if (!serverchanged) {
			return;
		}

		// Update the last results with new data.
		this.LastServerResults = [];
		for (server in pageresults) {
			this.LastServerResults.push({"servername" : pageresults[server]["servername"], 
					"connectioncount" : pageresults[server]["connectioncount"],
					"requestrate" : pageresults[server]["requestrate"],});
		}
		

		// Sort the list of servers.
		// Create a temporary array.
		var decorated = [];

		// Create a decorated array. We set the decorator to lower case
		// to make the sort case insensitive.
		for (var sindex in pageresults) {
			var server = pageresults[sindex];
			decorated.push([server["servername"].toLowerCase(), server]);
		}
		// Sort the array of servers.
		decorated.sort();
	
		// Undecorate the list.
		var serverarray = [];
		for (var sindex in decorated) {
			serverarray.push(decorated[sindex][1]);
		}
		

		// Now, update the server table data.
		var servertable = document.getElementById("servertable");

		// First, delete the table if it already exists (but not the header).
		while (servertable.rows.length > 1) {
			servertable.deleteRow(-1);
		}

		this.Utils.TRowStart();
		for (var server in serverarray) {
			var trow = servertable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// First cell is server name.
			this.Utils.InsertTableCell(trow, 0, serverarray[server]["servername"], tdclass);

			// We show either connection count or request rate, but not both.
			// If request rate is negative, then we use connection count.
			// Otherwise, we use request rate.
			if (serverarray[server]["requestrate"] < 0) {
				var connectioncount = serverarray[server]["connectioncount"];
				var requestrate = '';
			} else {
				var connectioncount = '';
				var requestrate = serverarray[server]["requestrate"];
			}
			// Second cell is number of connections.
			this.Utils.InsertTableCell(trow, 1, connectioncount, tdclass);
			// Third cell is the request rate.
			this.Utils.InsertTableCell(trow, 2, requestrate, tdclass);
		}
	}
	this.UpdateServerResults = _UpdateServerResults;



	// ##################################################################
	// Fill the client table with data.
	function _UpdateClientResults(pageresults) {


		// Check to see if any data has changed.
		// If the length has changed, we have a new configuration. 
		var clientchanged = false;
		if (pageresults.length == this.LastClientResults.length) {
			// Now, check if any of the individual data have changed.
			for (client in pageresults) {
				var newclient = pageresults[client];
				var lastclient = this.LastClientResults[client];
				if ((newclient["connectionname"] != lastclient["connectionname"]) ||
					(newclient["constatus"] != lastclient["constatus"]) ||
					(newclient["cmdsummary"] != lastclient["cmdsummary"])) {
					var clientchanged = true;
				}
			}
		} else {
			var clientchanged = true;
		}


		// If no client data has changed, then we don't need to do any updates.
		if (!clientchanged) {
			return;
		}

		// Update the last results with new data.
		this.LastClientResults = [];
		for (client in pageresults) {
			this.LastClientResults.push({"connectionname" : pageresults[client]["connectionname"], 
					"constatus" : pageresults[client]["constatus"],
					"cmdsummary" : pageresults[client]["cmdsummary"]});
		}
		


		// Now, update the client display table.
		var clienttable = document.getElementById("clienttable");

		// First, delete the table if it already exists (but not the header).
		while (clienttable.rows.length > 1) {
			clienttable.deleteRow(-1);
		}

		// Display the new table.
		this.Utils.TRowStart();
		for (var client in pageresults) {
			var trow = clienttable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Connection name.
			var connectionname = pageresults[client]["connectionname"]
			this.Utils.InsertTableCell(trow, 0, connectionname, tdclass);

			// Connection status.
			this.Utils.TextListStat(trow, 1, pageresults[client]["constatus"], this.ConStatTexts);

			// Command status.
			this.Utils.TextListStat(trow, 2, pageresults[client]["cmdsummary"], this.CmdStatTexts);

			// View errors link.
			this.Utils.InsertTableLink(trow, 3, "statussysmoncomms.html?connection=" + connectionname, "View", tdclass);

		}

	}
	this.UpdateClientResults = _UpdateClientResults;



	// ##################################################################
	// Update the server and client results.
	function _UpdatePageResults(pageresults) {
		this.UpdateServerResults(pageresults["servers"]);
		this.UpdateClientResults(pageresults["clients"]);
	}
	this.UpdatePageResults = _UpdatePageResults;

}
// ##################################################################


