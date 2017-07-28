/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatusconfigure.js
# Purpose: 	MBLogic status status configure screen library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		20-Nov-2010
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
/* Generic summary display. This handles data from different sub-systems
table cells by initialising it with different web page id strings.
	Parameters:
		utillib (object) = The utility display library.
		statustexts (object) = The message definitions for status.
		errorstatid: (string) = ID for cell holding status text and colour.
		timeid: (string) = ID for cell holding time.
		sigid: (string) = ID for cell holding has signature.
*/
function SummaryMonitor(utillib, statustexts, errorstatid, timeid, sigid) {

	// Utility library
	this.Utils = utillib;
	// Message texts.
	this.StatusTexts = statustexts;

	this._ErrorStatID = errorstatid;
	this._TimeID = timeid;
	this._SigID = sigid;

	// We use this to keep track of whether anything has changed.
	this.ScanList = ["configstat", "starttime", "signature"];
	this.LastResults = [];
	for (var index in this.ScanList) {
		this.LastResults[index] = null;
	}

	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		// Check to see if anything has changed since the last scan.
		var updated = false;
		for (var index in this.ScanList) {
			if (pageresults[this.ScanList[index]] != this.LastResults[index]) {
				this.LastResults[index] = pageresults[this.ScanList[index]];
				var updated = true;
			}
		}

		// Only update the screen if any data has changed. 
		if (updated) {
			// We have data.
			if (pageresults["configstat"] != null) {
				// Set the data and status colour indicators.
				this.Utils.TextStat(this._ErrorStatID, pageresults["configstat"], this.StatusTexts);	

				// Set the start time.
				var startdate = new Date(pageresults["starttime"] * 1000.0);
				this.Utils.ShowCell(this._TimeID, startdate.toLocaleString());

				// Set the file signature data.
				this.Utils.ShowCell(this._SigID, pageresults["signature"]);

			// We don't have valid data.
			} else {
				// Set the data and status colour indicators.
				this.Utils.TextStat(this._ErrorStatID, "nodata", this.StatusTexts);	

				// Set the start time.
				this.Utils.ShowCell(this._TimeID, "");

				// Set the file signature data.
				this.Utils.ShowCell(this._SigID, "");
			}
		}

	}
	this.UpdatePageResults = _UpdatePageResults;

}

// ##################################################################


// ##################################################################
/* This is for the HMI web page information.
	Parameters: utillib (object) = The utility display library.
*/
function HMIWebPageInfo(utillib) {


	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		var hmipagefiletable = document.getElementById("hmipagefiletable");
		var paglist = pageresults["hmipageinfo"];
		
		// The host and port information common to all HMI pages.
		var pagehost = "http://" + window.location.hostname + ":" + pageresults["port"] + "/";

		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (hmipagefiletable.rows.length > 1) {
			hmipagefiletable.deleteRow(-1);
		}

		// Display the table data.
		for (var pageindex in paglist) {
			var page = paglist[pageindex];

			var trow = hmipagefiletable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// HMI file name.
			this.Utils.InsertTableLink(trow, 0, pagehost + page["hmipage"], page["hmipage"], tdclass);

			// File signature.
			this.Utils.InsertTableCell(trow, 1, page["signature"], tdclass);

		}


	}
	this.UpdatePageResults = _UpdatePageResults;

}

// ##################################################################

