/** ##########################################################################
# Project: 	HMIServer
# Module: 	libhmistatushmi.js
# Purpose: 	MBLogic status display library. Derived from the MBLogic
#		soft logic version.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		15-Nov-2010
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
/* This is for the HMI status.
	Parameters: utillib (object) = The utility display library.
*/
function HMIStatus(utillib) {

	// Utility library
	this.Utils = utillib;

	this.hmidata = null;

	// List of tag names which has been sanitised.
	this.TagNames = [];
	// Sorted list of tags.
	this.SortedTags = [];
	// Sorted list of alarm addresses.
	this.SortedAlarms = [];
	// Sorted list of event addresses.
	this.SortedEvents = [];


	// ##################################################################
	// Create the list of address tag names.
	// clientversion and serverid do not belong in this list.
	function _CleanTagNames() {
		var tagdata = this.hmidata["addrtags"]
		this.TagNames = [];
		for (var tag in tagdata) {
			if ((tag != 'clientversion') && (tag != 'serverid')) {
				this.TagNames.push(tag);
			}
		}
	}
	this.CleanTagNames = _CleanTagNames;



	// ##################################################################
	// Sort the table by tag name.
	function _SortTagNames() {
		// Clear the tag list.
		this.SortedTags = [];

		for (var tagindex in this.TagNames) {
			this.SortedTags.push(this.TagNames[tagindex]);
		}
		// Sort the array of tags.
		this.SortedTags.sort();
	}
	this.SortTagNames = _SortTagNames;



	// ##################################################################
	// Sort the table by a selected alphabetic field.
	function _SortAlpha(field) {
		var tagdata = this.hmidata["addrtags"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tagindex in this.TagNames) {
			var tag = this.TagNames[tagindex];
			tagarray.push([tagdata[tag][field], tag]);
		}
		// Sort the array of tags.
		tagarray.sort();

		// Clear the tag list.
		this.SortedTags = [];
		// Create the list of tags.
		for (var tag in tagarray) {
			this.SortedTags.push(tagarray[tag][1]);
		}
	}
	this.SortAlpha = _SortAlpha;



	// ##################################################################
	// Sort the table by data table memory address.
	function _SortMemAddr() {
		var tagdata = this.hmidata["addrtags"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tagindex in this.TagNames) {
			var tag = this.TagNames[tagindex];
			// If the data type is string, the address includes
			// an address and length as an array.
			if (tagdata[tag]["datatype"] == "string") {
				var memaddr = tagdata[tag]["memaddr"][0];
			} else {
				var memaddr = tagdata[tag]["memaddr"];
			}

			tagarray.push([memaddr, tag]);
		}
		// Sort the array of tags.
		tagarray.sort(function(a, b) {return a[0] - b[0];});

		// Clear the tag list.
		this.SortedTags = [];
		// Create the list of tags.
		for (var tag in tagarray) {
			this.SortedTags.push(tagarray[tag][1]);
		}
	}
	this.SortMemAddr = _SortMemAddr;


	// ##################################################################
	// Sort the table numerically on a selected field.
	function _SortNumeric(field) {
		var tagdata = this.hmidata["addrtags"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tagindex in this.TagNames) {
			var tag = this.TagNames[tagindex];
			
			// If a value is null, convert it to a numeric value to 
			// make the comparison valid. We use positive infinity
			// because that pushes nulls to the bottom of the table.
			if (tagdata[tag][field] == null) {
				var numvalue = Infinity;
			} else {
				var numvalue = tagdata[tag][field];
			}

			tagarray.push([numvalue, tag]);
		}

		// Sort the array of tags.
		tagarray.sort(function(a, b) {return a[0] - b[0];});

		// Clear the tag list.
		this.SortedTags = [];
		// Create the list of tags.
		for (var tag in tagarray) {
			this.SortedTags.push(tagarray[tag][1]);
		}
	}
	this.SortNumeric = _SortNumeric;


	// ##################################################################
	// Sort the main tag display table according to a specified field
	// and then re-display the sorted table.
	function _SortTagTable(field) {
		// Sort the data.
		switch(field) {
		case "tagname" : { this.SortTagNames(); break;}
		case "addrtype" : { this.SortAlpha("addrtype"); break;}
		case "datatype" : { this.SortAlpha("datatype"); break;}
		case "memaddr" : { this.SortMemAddr(); break;}
		case "minrange" : { this.SortNumeric("minrange"); break;}
		case "maxrange" : { this.SortNumeric("maxrange"); break;}
		case "scaleoffset" : { this.SortNumeric("scaleoffset"); break;}
		case "scalespan" : { this.SortNumeric("scalespan"); break;}
		}

		// Re-display the data.
		this.UpdateAddressTags();

	}
	this.SortTagTable = _SortTagTable;



	// ##################################################################
	// Fill the address tag table with the tag info.
	function _UpdateAddressTags() {
		var tagtable = document.getElementById("addresstagtable");
		var tagdata = this.hmidata["addrtags"]
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (tagtable.rows.length > 1) {
			tagtable.deleteRow(-1);
		}


		// Display the table data.
		for (var tagindex in this.SortedTags) {
			var tag = this.SortedTags[tagindex];
			var datarecord = tagdata[tag];

			var trow = tagtable.insertRow(-1);
			// This adds an onclick event to allow editing of that record.
			trow.setAttribute("onclick", "AddrTagEdit('" + tag + "')");

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Tag name.
			this.Utils.InsertTableCell(trow, 0, tag, tdclass);
			// Address type.
			this.Utils.InsertTableCell(trow, 1, datarecord["addrtype"], tdclass);
			// Data type.
			this.Utils.InsertTableCell(trow, 2, datarecord["datatype"], tdclass);
			// Memory address.
			this.Utils.InsertTableCell(trow, 3, datarecord["memaddr"], tdclass);
			// Minimum range.
			var cell = datarecord["minrange"];
			if (cell == null) {var cell = "";}
			this.Utils.InsertTableCell(trow, 4, cell, tdclass);
			// Maximum range.
			var cell = datarecord["maxrange"];
			if (cell == null) {var cell = "";}
			this.Utils.InsertTableCell(trow, 5, cell, tdclass);
			// Scale offset.
			var cell = datarecord["scaleoffset"];
			if (cell == null) {var cell = "";}
			this.Utils.InsertTableCell(trow, 6, cell, tdclass);
			// Scale span.
			var cell = datarecord["scalespan"];
			if (cell == null) {var cell = "";}
			this.Utils.InsertTableCell(trow, 7, cell, tdclass);

		}
	}
	this.UpdateAddressTags = _UpdateAddressTags;


	// ##################################################################
	// Show server ID and client version.
	function _ShowServerID() {
		this.Utils.ShowCell("serverid", this.hmidata["serverid"]);
		this.Utils.ShowCell("clientversion", this.hmidata["clientversion"]);

	}
	this.ShowServerID = _ShowServerID;



	// ##################################################################
	// Sort the alarm table numerically on the address field.
	function _SortAlarmAddr() {
		var tagdata = this.hmidata["alarms"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
			tagarray.push(tag);
		}

		// Sort the array of addresses numerically.
		tagarray.sort(function(a, b) {return a - b;});

		this.SortedAlarms = tagarray;
	}
	this.SortAlarmAddr = _SortAlarmAddr;


	// ##################################################################
	// Sort the event table numerically on the address field.
	function _SortEventAddr() {
		var tagdata = this.hmidata["events"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
			tagarray.push(tag);
		}

		// Sort the array of addresses numerically.
		tagarray.sort(function(a, b) {return a - b;});

		this.SortedEvents = tagarray;
	}
	this.SortEventAddr = _SortEventAddr;


	// ##################################################################
	// Sort the alarms table by a selected alphabetic field.
	function _SortAlarmsAlpha(field) {
		var tagdata = this.hmidata["alarms"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
			tagarray.push([tagdata[tag][field], tag]);
		}
		// Sort the array.
		tagarray.sort();

		// Clear the tag list.
		this.SortedAlarms = [];
		// Create the list of tags.
		for (var tag in tagarray) {
			this.SortedAlarms.push(tagarray[tag][1]);
		}
	}
	this.SortAlarmsAlpha = _SortAlarmsAlpha;


	// ##################################################################
	// Sort the events table by a selected alphabetic field.
	function _SortEventsAlpha(field) {
		var tagdata = this.hmidata["events"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
			tagarray.push([tagdata[tag][field], tag]);
		}
		// Sort the array.
		tagarray.sort();

		// Clear the tag list.
		this.SortedEvents = [];
		// Create the list of tags.
		for (var tag in tagarray) {
			this.SortedEvents.push(tagarray[tag][1]);
		}
	}
	this.SortEventsAlpha = _SortEventsAlpha;

	// ##################################################################
	// Sort the alarm display table according to a specified field
	// and then re-display the sorted table.
	function _SortAlarmTable(field) {
		// Sort the data.
		switch(field) {
		case "addr" : { this.SortAlarmAddr(); break;}
		case "tag" : { this.SortAlarmsAlpha("tag"); break;}
		case "zonelist" : { this.SortAlarmsAlpha("zonelist"); break;}
		}

		// Re-display the data.
		this.UpdateAlarms();

	}
	this.SortAlarmTable = _SortAlarmTable;


	// ##################################################################
	// Fill the alarm table with the alarm info.
	function _UpdateAlarms() {
		var alarmtable = document.getElementById("alarmtable");
		var alarmdata = this.hmidata["alarms"]
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (alarmtable.rows.length > 1) {
			alarmtable.deleteRow(-1);
		}


		// Display the table data.
		for (var alarmindex in this.SortedAlarms) {
			var alarm = this.SortedAlarms[alarmindex];

			var trow = alarmtable.insertRow(-1);
			// This adds an onclick event to allow editing of that record.
			trow.setAttribute("onclick", "AlarmEdit('" + alarm + "')");

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Address.
			this.Utils.InsertTableCell(trow, 0, alarm, tdclass);
			// Tag name.
			this.Utils.InsertTableCell(trow, 1, alarmdata[alarm]["tag"], tdclass);
			// Zone list.
			this.Utils.InsertTableCell(trow, 2, alarmdata[alarm]["zonelist"].join(", "), tdclass);

		}
	}
	this.UpdateAlarms = _UpdateAlarms;

	// ##################################################################
	// Sort the event display table according to a specified field
	// and then re-display the sorted table.
	function _SortEventTable(field) {
		// Sort the data.
		switch(field) {
		case "addr" : { this.SortEventAddr(); break;}
		case "tag" : { this.SortEventsAlpha("tag"); break;}
		case "zonelist" : { this.SortEventsAlpha("zonelist"); break;}
		}

		// Re-display the data.
		this.UpdateEvents();

	}
	this.SortEventTable = _SortEventTable;


	// ##################################################################
	// Fill the event table with the event info.
	function _UpdateEvents() {
		var eventtable = document.getElementById("eventtable");
		var eventdata = this.hmidata["events"]
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (eventtable.rows.length > 1) {
			eventtable.deleteRow(-1);
		}

		// Display the table data.
		for (var eventindex in this.SortedEvents) {
			var event = this.SortedEvents[eventindex];

			var trow = eventtable.insertRow(-1);
			// This adds an onclick event to allow editing of that record.
			trow.setAttribute("onclick", "EventEdit('" + event + "')");

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Address.
			this.Utils.InsertTableCell(trow, 0, event, tdclass);
			// Tag name.
			this.Utils.InsertTableCell(trow, 1, eventdata[event]["tag"], tdclass);
			// Zone list.
			this.Utils.InsertTableCell(trow, 2, eventdata[event]["zonelist"].join(", "), tdclass);

		}
	}
	this.UpdateEvents = _UpdateEvents;


	// ##################################################################
	// Display any errors which may be present.
	function _UpdateErrors() {

		var configerrors = this.hmidata["configerrors"];
		// If there are no errors, hide the error display table and exit.
		if (configerrors.length == 0) {
			this.Utils.HidePageArea("hmierrordisplay");
			return;
		} else {
			this.Utils.ShowPageArea("hmierrordisplay");
		}

		// We display the errors in a table.
		var errortable = document.getElementById("hmierrortable");

		// Delete all the rows in any existing table, but not the header.
		while (errortable.rows.length > 1) {
			errortable.deleteRow(-1);
		}

		// Display the table data.
		for (var errorindex in configerrors) {
			var trow = errortable.insertRow(-1);
			var rowcountref = trow.insertCell(0);
			var errmsgref = trow.insertCell(1);
			// Add the new cell text.
			rowcountref.appendChild(document.createTextNode(errorindex));
			errmsgref.appendChild(document.createTextNode(configerrors[errorindex]));
		}

	}
	this.UpdateErrors = _UpdateErrors;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		this.hmidata = pageresults;
		// Sanitise the tag list.
		this.CleanTagNames();

		// Sort the data by tag name by default.
		this.SortTagNames();

		// Show the server id and client version.
		this.ShowServerID();
		// Fill in the address tag table.
		this.UpdateAddressTags();

		// Fill in the alarm table.
		this.SortAlarmAddr();
		this.UpdateAlarms();
		// Fill in the event table.
		this.SortEventAddr();
		this.UpdateEvents();

		// Show the configuration errors.
		this.UpdateErrors();

	}
	this.UpdatePageResults = _UpdatePageResults;


}

// ##################################################################


