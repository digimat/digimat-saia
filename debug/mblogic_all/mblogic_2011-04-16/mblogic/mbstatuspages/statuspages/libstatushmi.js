/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatushmi.js
# Purpose: 	MBLogic status display library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		07-Dec-2010
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
function HMIStatus(utillib, editlib) {

	// Utility library
	this.Utils = utillib;
	// Parameter edit library.
	this.EditLib = editlib;

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
	// Sanitise the list of tag names.
	// serverid and client version do not belong in this list.
	function _CleanTagNames() {
		var tagdata = this.hmidata["hmitagdata"]
		this.TagNames = [];
		for (var tag in tagdata) {
			if ((tag != "serverid") && (tag != "clientversion")) {
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
		var tagdata = this.hmidata["hmitagdata"]

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
		var tagdata = this.hmidata["hmitagdata"]

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
		var tagdata = this.hmidata["hmitagdata"]

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
		var tagdata = this.hmidata["hmitagdata"]
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
		this.Utils.ShowCell("serverid", this.hmidata["hmitagdata"]["serverid"]["serverid"]);
		this.Utils.ShowCell("clientversion", this.hmidata["hmitagdata"]["clientversion"]["clientversion"]);

	}
	this.ShowServerID = _ShowServerID;



	// ##################################################################
	// Sort the alarm table numerically on the address field.
	function _SortAlarmAddr() {
		var tagdata = this.hmidata["alarmconfig"]

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
		var tagdata = this.hmidata["eventconfig"]

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
		var tagdata = this.hmidata["alarmconfig"]

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
		var tagdata = this.hmidata["eventconfig"]

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
		var alarmdata = this.hmidata["alarmconfig"]
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
		var eventdata = this.hmidata["eventconfig"]
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
	// Fill the ERP list table with data.
	function _UpdateERPList() {

		var erprddata = this.hmidata["erplist"]["read"];
		var erpwrdata = this.hmidata["erplist"]["write"];

		erprddata.sort()
		erpwrdata.sort()

		this.Utils.ShowCell("erpread", erprddata.join(", "));
		this.Utils.ShowCell("erpwrite", erpwrdata.join(", "));

	}
	this.UpdateERPList = _UpdateERPList;



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

		// Fill in the ERP list table.
		this.UpdateERPList();

	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Return the current data in a format suitable for sending to the
	// server for saving the results.
	function _FormatSaveRequest() {
		var datareq = {}

		// HMI configuration data.
		datareq["hmitagdata"] = this.hmidata["hmitagdata"];
		datareq["alarmconfig"] = this.hmidata["alarmconfig"];
		datareq["eventconfig"] = this.hmidata["eventconfig"];
		datareq["erplist"] = this.hmidata["erplist"];

		return datareq;
	}
	this.FormatSaveRequest = _FormatSaveRequest;

	// ##################################################################
	// Editing functions.

	// ##################################################################
	// Show the results of the save operation.
	function _EditSaveResult(saveresult) {

		var ack = saveresult["mblogiccmdack"];
		var errorlist = saveresult["errors"];

		var haserrors = (errorlist.length > 0) || (ack != "ok");

		// First, delete the error table if it already exists.
		var errtable = document.getElementById("saveerrortable");
		while (errtable.rows.length > 0) {
			errtable.deleteRow(-1);
		}

		// Now, add the new error table data.
		// We limit the display to no more than 100 errors. 
		for (var err=0; (err < errorlist.length) && (err < 100); err++) {
			var trow = errtable.insertRow(-1);

			// Number the row.
			var cell = trow.insertCell(0);
			var celltext = document.createTextNode(parseInt(err) + 1);
			cell.appendChild(celltext);

			// Error message.
			var cell = trow.insertCell(1);
			var celltext = document.createTextNode(errorlist[err]);
			cell.appendChild(celltext);
		}

		// If there are any errors, display the error messages.
		if (haserrors) {
			this.Utils.ShowPageArea("saveerrors");
		} else {
			this.Utils.HidePageArea("saveerrors");
		}

		// If the server reported a system error (the acknowledge), then
		// display the error message embedded in the page.
		if (ack != "ok") {
			this.Utils.ShowPageArea("serversaveerror");
		}
	}
	this.EditSaveResult = _EditSaveResult;



	// ##################################################################
	// Determine if the page is in view or edit modes.
	// Returns true if in edit mode.
	function _EditMode() {
		return document.forms.editmode.mode[1].checked;
	}
	this.EditMode = _EditMode;



	// ##################################################################
	// Set the remaining parameters to be compatible with the address type.
	// Parameters: addrtype (string) = The address type.
	function _SetParamsToAddrType(addrtype) {

		// Find the correct category.
		var addrcategory = this.EditLib.GetAddrCategory(addrtype);


		// We don't need the data type or scale factors if we know
		// the address type is boolean.
		if (addrcategory == "boolean") {
			this.Utils.HidePageArea("tageditdatatype");
			this.Utils.HidePageArea("tageditnumericproperties");
			this.Utils.HidePageArea("tageditstringproperties");
		}

		// If the address type is numeric, we need additional parameters.
		if (addrcategory == "int" || addrcategory == "float") {
			this.Utils.ShowPageArea("tageditdatatype");
			this.Utils.ShowPageArea("tageditnumericproperties");
			this.Utils.HidePageArea("tageditstringproperties");
		}

		// Set the data type to a suitable default.
		if (addrcategory == "int") {
			document.forms.taginfo.datatype[1].checked = true;
		}
		if (addrcategory == "float") {
			document.forms.taginfo.datatype[2].checked = true;
		}

		// If the address type is string.
		if (addrcategory == "string") {
			this.Utils.HidePageArea("tageditdatatype");
			this.Utils.HidePageArea("tageditnumericproperties");
			this.Utils.ShowPageArea("tageditstringproperties");
		}
	}
	this.SetParamsToAddrType = _SetParamsToAddrType;




	// ##################################################################
	// The current tag address type has changed.
	function _AddrTypeChanged() {
		var addrtype = document.forms.taginfo.addresstype.value;
		this.SetParamsToAddrType(addrtype);
		return;
	}
	this.AddrTypeChanged = _AddrTypeChanged;



	// ##################################################################
	// Get the data type from the edit form.
	// Return (string) = The currently selected data type.
	function _GetDataType() {
		// Find out which radio button was checked.		
		var radiocheck = -1;
		for (var i=0; i < document.forms.taginfo.datatype.length; i++) {
			if (document.forms.taginfo.datatype[i].checked) {
				var radiocheck = i;
			}
		}

		switch (radiocheck) {
		case 0 : return "boolean";
		case 1 : return "integer";
		case 2 : return "float";
		default : return "error";
		}
		
	}
	this.GetDataType = _GetDataType;


	// ##################################################################
	// Set the remaining parameters according to the data type.
	function _SetParamsToDataType(datatype) {

		switch (datatype) {
			// Boolean.
			case "boolean" : {this.Utils.HidePageArea("tageditnumericproperties"); break;}
			// Integer.
			case "integer" : {this.Utils.ShowPageArea("tageditnumericproperties"); break;}
			// Float.
			case "float" : {this.Utils.ShowPageArea("tageditnumericproperties"); break;}
			// Something went wrong, so we'll just ignore this.
			default : return;
		}
	}
	this.SetParamsToDataType = _SetParamsToDataType;


	// ##################################################################
	// The tag data type has changed.
	function _DataTypeChanged() {

		// Find out which radio button was checked.
		var radiocheck = this.GetDataType();		
		this.SetParamsToDataType(radiocheck);
	}
	this.DataTypeChanged = _DataTypeChanged;


	// ##################################################################
	// The tag name has changed.
	function _TagNameChanged() {
		var tagname = document.forms.taginfo.tagname.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.TagNameOK(tagname), "tagname")
	}
	this.TagNameChanged = _TagNameChanged;

	// ##################################################################
	// The tag memory address has changed.
	function _TagMemAddrChanged() {
		var memaddress = document.forms.taginfo.memaddress.value;
		// The maximum address range depends on the address type.
		var addrtype = document.forms.taginfo.addresstype.value;

		// Check if this is a valid data table address.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckMemAddr(memaddress, addrtype), "memaddress")
	}
	this.TagMemAddrChanged = _TagMemAddrChanged;


	// ##################################################################
	// The minimum range has changed.
	function _MinRangeChanged() {
		var minrange = document.forms.taginfo.minrange.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckNumber(minrange), "minrange")
	}
	this.MinRangeChanged = _MinRangeChanged;

	// ##################################################################
	// The maximum range has changed.
	function _MaxRangeChanged() {
		var maxrange = document.forms.taginfo.maxrange.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckNumber(maxrange), "maxrange")
	}
	this.MaxRangeChanged = _MaxRangeChanged;


	// ##################################################################
	// The scale offset has changed.
	function _ScaleOffsetChanged() {
		var scaleoffset = document.forms.taginfo.scaleoffset.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckNumber(scaleoffset), "scaleoffset")
	}
	this.ScaleOffsetChanged = _ScaleOffsetChanged;



	// ##################################################################
	// The scale span has changed.
	function _ScaleSpanChanged() {
		var scalespan = document.forms.taginfo.scalespan.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckNumber(scalespan), "scalespan")
	}
	this.ScaleSpanChanged = _ScaleSpanChanged;


	// ##################################################################
	// The string length has changed.
	function _StringLengthChanged() {
		var stringlen = document.forms.taginfo.stringlen.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckInteger(stringlen), "stringlen")
	}
	this.StringLengthChanged = _StringLengthChanged;



	// ##################################################################
	// Initialise the address tag editing form with data.
	// Parameters tagname (string) = The name of the tag being edited.
	function _InitAddTagEdit(tagname) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["tagname", "memaddress", "minrange", "maxrange", 
			"scaleoffset", "scalespan", "stringlen"];
		this.EditLib.ResetFieldColours(editfields);

		// If the tag name is an empty string, provide a default edit record.
		if (tagname.length != 0) {
			var tagdata = this.hmidata["hmitagdata"];
			var datarecord = tagdata[tagname];

			var addrtype = datarecord["addrtype"];
			var datatype = datarecord["datatype"];
			var minrange = datarecord["minrange"];
			var maxrange = datarecord["maxrange"];
			var scaleoffset = datarecord["scaleoffset"];
			var scalespan = datarecord["scalespan"];

			// The address format depends on whether the address type is a string.
			// Strings addresses are arrays with address and length.
			if (typeof(datarecord["memaddr"]) == "object") {
				var memaddr = datarecord["memaddr"][0];
				var strlength = datarecord["memaddr"][1];
			} else {
				var memaddr = datarecord["memaddr"];
				var strlength = 0;
			}

		} else {
			var memaddr = "";
			var strlength = 0;
			var addrtype = "coil";
			var datatype = "boolean";
			var minrange = "";
			var maxrange = "";
			var scaleoffset = "";
			var scalespan = "";

		}


		// The address tag name.
		document.forms.taginfo.tagname.value = tagname;

		// Set the address type.
		var addrindex = this.EditLib.GetAddrTypeIndex(addrtype);
		document.forms.taginfo.addresstype[addrindex].selected = "1";
		this.SetParamsToAddrType(addrtype);

		// Set the data type radio buttons.
		switch (datatype) {
		case "boolean" : {document.forms.taginfo.datatype[0].checked = true; break;}
		case "integer" : {document.forms.taginfo.datatype[1].checked = true; break;}
		case "float" : {document.forms.taginfo.datatype[2].checked = true; break;}
		}
		this.SetParamsToDataType(datatype);

		document.forms.taginfo.memaddress.value = memaddr;
		document.forms.taginfo.stringlen.value = strlength;

		document.forms.taginfo.minrange.value = minrange;
		document.forms.taginfo.maxrange.value = maxrange;
		document.forms.taginfo.scaleoffset.value = scaleoffset;
		document.forms.taginfo.scalespan.value = scalespan;

	}
	this.InitAddTagEdit = _InitAddTagEdit;


	// ##################################################################
	// Save the address tag information.
	// Return true if the parameters were saved.
	function _TagEditEnter() {

		// Check the parameters.

		// The address tag name.
		var tagname = document.forms.taginfo.tagname.value;
		if (!this.EditLib.TagNameOK(tagname)) { 
			this.TagNameChanged();
			this.TagMemAddrChanged();
			return false; 
		}

		// The memory address.
		var memaddrval = document.forms.taginfo.memaddress.value;
		if(!this.EditLib.CheckMemAddr(memaddrval)) { 
			this.TagMemAddrChanged();
			return false; 
		}

		// The address type.
		var addresstype = document.forms.taginfo.addresstype.value;

		// Assume the address type is numeric.
		var addrclass = "numeric"

		// Boolean addresses only need the tag name, address type, and address.
		if (addresstype == "coil" || addresstype == "discrete") {
			var addrclass = "bit"
		}

		var strlength = document.forms.taginfo.stringlen.value;
		// The address format depends on the address type.
		if (this.EditLib.AddrTypeIsStr(addresstype)) {
			if (!this.EditLib.CheckInteger(strlength)) {
				this.StringLengthChanged();
				return false;
			}
			var addrclass = "string"
		}

		// These are used for numeric addresses only.
		var minrange = document.forms.taginfo.minrange.value;
		var maxrange = document.forms.taginfo.maxrange.value;
		var scaleoffset = document.forms.taginfo.scaleoffset.value;
		var scalespan = document.forms.taginfo.scalespan.value;

		if (addrclass == "numeric") {
			if (!this.EditLib.CheckNumber(minrange) || !this.EditLib.CheckNumber(maxrange) ||
			!this.EditLib.CheckNumber(scaleoffset) || !this.EditLib.CheckNumber(scalespan)) {
				this.MinRangeChanged();
				this.MaxRangeChanged();
				this.ScaleOffsetChanged();
				this.ScaleSpanChanged();
				return false;
			}
		}

		var tagdata = this.hmidata["hmitagdata"];
		// If the tag doesn't exist, create an empty record.
		if (!(tagname in tagdata)) {
			tagdata[tagname] = {};
		}
		var datarecord = tagdata[tagname];


		// Now, save the data and update the display.
		switch (addrclass) {
		case "bit" : {
			datarecord["memaddr"] = memaddrval;
			datarecord["addrtype"] = addresstype;
			datarecord["datatype"] = "boolean";
			datarecord["minrange"] = null;
			datarecord["maxrange"]  = null;
			datarecord["scaleoffset"] = null;
			datarecord["scalespan"] = null;
			break;
			}

		case "string" : {
			datarecord["addrtype"] = addresstype;
			datarecord["memaddr"] = [memaddrval, strlength];
			// We have to force this to string, as the regular logic
			// doesn't handle this elsewhere.
			datarecord["datatype"] = "string";
			datarecord["minrange"] = null;
			datarecord["maxrange"]  = null;
			datarecord["scaleoffset"] = null;
			datarecord["scalespan"] = null;
			break;
			}

		default : {
			datarecord["memaddr"] = memaddrval;
			// The data type radio buttons.
			var datatype = this.GetDataType();
			datarecord["datatype"] = datatype;
			// The remaining address types are integer or floating point.
			datarecord["addrtype"] = addresstype;
			var minrange = document.forms.taginfo.minrange.value;
			datarecord["minrange"] = minrange;
			var maxrange = document.forms.taginfo.maxrange.value;
			datarecord["maxrange"] = maxrange;
			var scaleoffset = document.forms.taginfo.scaleoffset.value;
			datarecord["scaleoffset"] = scaleoffset;
			var scalespan = document.forms.taginfo.scalespan.value;
			datarecord["scalespan"] = scalespan;
			break;
			}
		}
		// Fill the address tag table with the tag info.
		this.CleanTagNames();
		this.SortTagNames();
		this.UpdateAddressTags();

		return true;
	}
	this.TagEditEnter = _TagEditEnter;



	// ##################################################################
	// Delete an address tag record.
	function _TagEditDelete() {
		// The address tag name.
		var tagname = document.forms.taginfo.tagname.value;

		var tagdata = this.hmidata["hmitagdata"];
		// If the tag exists, delete the record.
		if (tagname in tagdata) {
			delete tagdata[tagname];
			this.CleanTagNames();
			this.SortTagNames();
			this.UpdateAddressTags();
		}
	}
	this.TagEditDelete = _TagEditDelete;




	// ##################################################################
	// Alarm and event editing functions.


	// ##################################################################
	// The alarm memory address has changed.
	function _AlarmAddrChanged() {
		var memaddress = document.forms.alarminfo.memaddress.value;

		// Check if this is a valid data table address.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckMemAddr(memaddress, "coil"), "alarmaddress")
	}
	this.AlarmAddrChanged = _AlarmAddrChanged;


	// ##################################################################
	// The event memory address has changed.
	function _EventAddrChanged() {
		var memaddress = document.forms.eventinfo.memaddress.value;

		// Check if this is a valid data table address.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckMemAddr(memaddress, "coil"), "eventaddress")
	}
	this.EventAddrChanged = _EventAddrChanged;

	// ##################################################################
	// The alarm tag name has changed.
	function _AlarmTagChanged() {
		var tagname = document.forms.alarminfo.tagname.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.TagNameOK(tagname), "alarmname")
	}
	this.AlarmTagChanged = _AlarmTagChanged;

	// ##################################################################
	// The event tag name has changed.
	function _EventTagChanged() {
		var tagname = document.forms.eventinfo.tagname.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.TagNameOK(tagname), "eventname")
	}
	this.EventTagChanged = _EventTagChanged;


	// ##################################################################
	// This attempts to reformat alarm and event zone lists, and then 
	// checks to see if the zone tag names meet the tag name rules. 
	// Parameters: zonestring (string) = The string containing the zone information.
	//	Returns: (array) = If OK, the reformatted zone list. If not OK, an
	//		empty array.
	function _ZoneFormat(zonestring) {
		// Strip all blanks and split into an array.
		var zonearray = zonestring.replace(/ /g, "").split(",");
		var zones = [];
		for (var zoneindex in zonearray) {
			var testzone = zonearray[zoneindex];
			if (this.EditLib.TagNameOK(testzone)) {
				zones.push(testzone);
			} else {
				return [];
			}
		}
		return zones;
	}
	this.ZoneFormat = _ZoneFormat;


	// ##################################################################
	// The alarm zone list has changed.
	function _AlarmZonesChanged() {
		var zones = document.forms.alarminfo.zones.value;
		var zonelist = this.ZoneFormat(zones);
		this.EditLib.ShowFieldStatusColour(zonelist.length > 0, "alarmzones")
		if (zonelist.length > 0) {
			document.forms.alarminfo.zones.value = zonelist.join(" ,");
		}
	}
	this.AlarmZonesChanged = _AlarmZonesChanged;

	// ##################################################################
	// The event zone list has changed.
	function _EventZonesChanged() {
		var zones = document.forms.eventinfo.zones.value;
		var zonelist = this.ZoneFormat(zones);
		this.EditLib.ShowFieldStatusColour(zonelist.length > 0, "eventzones")
		if (zonelist.length > 0) {
			document.forms.alarminfo.zones.value = zonelist.join(" ,");
		}
	}
	this.EventZonesChanged = _EventZonesChanged;


	// ##################################################################
	// Initialise the alarm editing form with data.
	// Parameters alarmaddr (string) = The address of the alarm being edited.
	function _InitAlarmEdit(alarmaddr) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["alarmaddress","alarmname", "alarmzones"];
		this.EditLib.ResetFieldColours(editfields);


		// If the address is an empty string, use default data,
		// else retrieve the existing data.
		if (alarmaddr.length != 0) {
			var alarmdata = this.hmidata["alarmconfig"];
			var datarecord = alarmdata[alarmaddr];
			var tag = datarecord["tag"];
			var zonelist = datarecord["zonelist"];
		} else {
			var tag = "";
			var zonelist = [];
		}

		document.forms.alarminfo.memaddress.value = alarmaddr;
		document.forms.alarminfo.tagname.value = tag;
		document.forms.alarminfo.zones.value = zonelist.join(", ");
	}
	this.InitAlarmEdit = _InitAlarmEdit;


	// ##################################################################
	// Initialise the event editing form with data.
	// Parameters eventaddr (string) = The address of the event being edited.
	function _InitEventEdit(eventaddr) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["eventaddress","eventname", "eventzones"];
		this.EditLib.ResetFieldColours(editfields);

		// If the address is an empty string, use default data,
		// else retrieve the existing data.
		if (eventaddr.length != 0) {
			var eventdata = this.hmidata["eventconfig"]
			var datarecord = eventdata[eventaddr];
			var tag = datarecord["tag"];
			var zonelist = datarecord["zonelist"];
		} else {
			var tag = "";
			var zonelist = [];
		}

		document.forms.eventinfo.memaddress.value = eventaddr;
		document.forms.eventinfo.tagname.value = tag;
		document.forms.eventinfo.zones.value = zonelist.join(", ");
	}
	this.InitEventEdit = _InitEventEdit;


	// ##################################################################
	// Save the alarm information.
	// Return true if the parameters were saved.
	function _AlarmEditEnter() {

		// First, check the parameters.
		var memaddress = document.forms.alarminfo.memaddress.value;
		var tagname = document.forms.alarminfo.tagname.value;
		var zones = document.forms.alarminfo.zones.value;

		// Display errors.
		this.AlarmAddrChanged();
		this.AlarmTagChanged();
		this.AlarmZonesChanged();

		if(!this.EditLib.CheckMemAddr(memaddress)) { return false; }
		if (!this.EditLib.TagNameOK(tagname)) { return false; }
		// Check the detailed formatting to make sure it is OK.
		var zonelist = this.ZoneFormat(zones);
		if (zonelist.length < 1) { return false; }

		var alarmdata = this.hmidata["alarmconfig"]
		var datarecord = alarmdata[memaddress];
		// If the address doesn't exist, create an empty record.
		if (!(memaddress in alarmdata)) {
			alarmdata[memaddress] = {};
		}
		var datarecord = alarmdata[memaddress];

		// Save the data. We also reformat the zone list to strip 
		// blanks and convert to a list.
		datarecord["tag"] = tagname;
		datarecord["zonelist"] = zones.replace(/ /g, "").split(",");

		// Display the new alarm info.
		this.SortAlarmAddr();
		this.UpdateAlarms();
		return true;
	}
	this.AlarmEditEnter = _AlarmEditEnter;


	// ##################################################################
	// Save the event information.
	// Return true if the parameters were saved.
	function _EventEditEnter() {

		// First, check the parameters.
		var memaddress = document.forms.eventinfo.memaddress.value;
		var tagname = document.forms.eventinfo.tagname.value;
		var zones = document.forms.eventinfo.zones.value;

		// Display errors.
		this.EventAddrChanged();
		this.EventTagChanged();
		this.EventZonesChanged();


		if(!this.EditLib.CheckMemAddr(memaddress)) { return false; }
		if (!this.EditLib.TagNameOK(tagname)) { return false; }
		// Check the detailed formatting to make sure it is OK.
		var zonelist = this.ZoneFormat(zones);
		if (zonelist.length < 1) { return false; }
	
		var eventdata = this.hmidata["eventconfig"]
		var datarecord = eventdata[memaddress];
		// If the address doesn't exist, create an empty record.
		if (!(memaddress in eventdata)) {
			eventdata[memaddress] = {};
		}
		var datarecord = eventdata[memaddress];

		// Save the data. We also reformat the zone list to strip 
		// blanks and convert to a list.
		datarecord["tag"] = tagname;
		datarecord["zonelist"] = zones.replace(/ /g, "").split(",");

		// Display the new alarm info.
		this.SortEventAddr();
		this.UpdateEvents();
		return true;
	}
	this.EventEditEnter = _EventEditEnter;


	// ##################################################################
	// Delete an alarm record.
	function _AlarmEditDelete() {

		var memaddress = document.forms.alarminfo.memaddress.value;
		var alarmdata = this.hmidata["alarmconfig"]

		// If it exists, delete the record.
		if (memaddress in alarmdata) {
			delete alarmdata[memaddress];
			this.SortAlarmAddr();
			this.UpdateAlarms();
		}
	}
	this.AlarmEditDelete = _AlarmEditDelete;


	// ##################################################################
	// Delete an event record.
	function _EventEditDelete() {

		var memaddress = document.forms.eventinfo.memaddress.value;
		var eventdata = this.hmidata["eventconfig"]

		// If it exists, delete the record.
		if (memaddress in eventdata) {
			delete eventdata[memaddress];
			this.SortEventAddr();
			this.UpdateEvents();
		}
	}
	this.EventEditDelete = _EventEditDelete;


	// ##################################################################
	// Edit server data.

	// ##################################################################
	// The server ID has changed.
	function _ServerIDChanged() {
		var serverid = document.forms.serverinfo.serverid.value;

		this.EditLib.ShowFieldStatusColour(serverid.length > 0, "serveridedit")
	}
	this.ServerIDChanged = _ServerIDChanged;


	// ##################################################################
	// The clientversion has changed.
	function _ClientVersionChanged() {
		var clientversion = document.forms.serverinfo.clientversion.value;

		this.EditLib.ShowFieldStatusColour(clientversion.length > 0, "clientversionedit")
	}
	this.ClientVersionChanged = _ClientVersionChanged;


	// ##################################################################
	// Initialise the server data editing form with data.
	function _InitServerEdit() {
		var datarecord = this.hmidata["hmitagdata"]

		document.forms.serverinfo.serverid.value = datarecord["serverid"]["serverid"];
		document.forms.serverinfo.clientversion.value = datarecord["clientversion"]["clientversion"];
	}
	this.InitServerEdit = _InitServerEdit;

	// ##################################################################
	// Save the server information.
	// Return true if the server information was saved.
	function _ServerInfoEnter() {
		var serverid = document.forms.serverinfo.serverid.value;
		var clientversion = document.forms.serverinfo.clientversion.value;

		// Check the data for validity.
		if (serverid.length < 1 || clientversion.length < 1) {
			return false;
		}

		// Update the data record.
		var datarecord = this.hmidata["hmitagdata"];
		datarecord["serverid"]["serverid"] = serverid;
		datarecord["clientversion"]["clientversion"] = clientversion;

		// Update the web page.
		this.ShowServerID();

		// Signal the update was ok.
		return true;

	}
	this.ServerInfoEnter = _ServerInfoEnter;


	// ##################################################################
	// Edit ERP list data.

	// These are the current state of the ERP tags in the editor.
	this.ERPReadEditData = [];
	this.ERPWriteEditData = [];
	// This is a placeholder that we use to indicate an empty selection.
	this.ERPEmptySelection = " ----- ";

	// ##################################################################
	// Populate a current ERP tag edit list. This shows in the editor the 
	// tags that are currently selected for use.
	// Parameters: displayid (string) = The ID for the area to display in.
	//		tagdata (array) = The data to display.
	function _PopulateERPTagEditList(displayid, tagdata) {
		var tags = document.getElementById(displayid);

		// If there are any existing elements, remove them first.
		if (tags.hasChildNodes()) {
			while (tags.firstChild) {
				tags.removeChild(tags.firstChild);
			}
		} 

		// Display the new data.
		tagdata.sort();
		tags.appendChild(document.createTextNode(tagdata.join(", ")));

	}
	this.PopulateERPTagEditList = _PopulateERPTagEditList;


	// ##################################################################
	// Populate a ERP tag list selection widget with HMI tags.
	// Parameters: displayid (string) = The selection list.
	//		tagdata (array) = The data to display.
	function _PopulateERPTagList(displayid, tagdata) {

		// Populate the tag list.
		// First remove any existing tags.
		var tags = document.getElementById(displayid);
		// If there are any existing elements, remove them first.
		if (tags.hasChildNodes()) {
			while (tags.firstChild) {
				tags.removeChild(tags.firstChild);
			}
		} 

		// Make a list of tag names in an array.
		var taglist = [];

		for (var i in tagdata) {
			taglist.push(tagdata[i]);
		}
		// Sort the list of names.
		taglist.sort();
		// The default selection has to be empty so we can detect a change.
		var tagarray = [this.ERPEmptySelection].concat(taglist);

		// Now populate the selection with new data. 
		for (var i=0; i < tagarray.length; i++) {
			var tagrecord = tagarray[i];
			var newoption = document.createElement("option");
			newoption.value = tagrecord;
			newoption.text = tagrecord;
			tags.appendChild(newoption);
		}
	
	}
	this.PopulateERPTagList = _PopulateERPTagList;


	// ##################################################################
	// Initialise the ERP list editing form with data.
	function _InitERPListEdit() {
		var datarecord = this.hmidata["erplist"];

		// Set the selection radio buttons to the default.
		

		// Initialise the editor data.
		var erpreaddata = this.hmidata["erplist"]["read"];
		this.ERPReadEditData = [];
		for (var i=0; i < erpreaddata.length; i++) {
			this.ERPReadEditData.push(erpreaddata[i]);
		}
		var erpwritedata = this.hmidata["erplist"]["write"];
		this.ERPWriteEditData = [];
		for (var i=0; i < erpwritedata.length; i++) {
			this.ERPWriteEditData.push(erpwritedata[i]);
		}

		// Display the current tag data in the edit area.
		this.PopulateERPTagEditList("erplistreadeditcurrent", this.ERPReadEditData);
		this.PopulateERPTagEditList("erplistwriteeditcurrent", this.ERPWriteEditData);


		// Populate the drop-down lists used to select tags.
		this.PopulateERPTagList("erpreadadd", this.SortedTags);
		this.PopulateERPTagList("erpreadremove", this.ERPReadEditData);

		this.PopulateERPTagList("erpwriteadd", this.SortedTags);
		this.PopulateERPTagList("erpwriteremove", this.ERPWriteEditData);

	}
	this.InitERPListEdit = _InitERPListEdit;

	// ##################################################################
	// Save the ERP list information.
	// Return true if the ERP list information was saved.
	function _ERPListEditEnter() {

		// Save the editor data by copying it.

		// Erase the current data.
		this.hmidata["erplist"]["read"] = [];
		// Replace it with the new data.
		for (var i=0; i < this.ERPReadEditData.length; i++) {
			this.hmidata["erplist"]["read"].push(this.ERPReadEditData[i]);
		}

		// Erase the current data.
		this.hmidata["erplist"]["write"] = [];
		// Replace it with the new data.
		for (var i=0; i < this.ERPWriteEditData.length; i++) {
			this.hmidata["erplist"]["write"].push(this.ERPWriteEditData[i]);
		}

		// Update the page display.
		this.UpdateERPList();

		return true;

	}
	this.ERPListEditEnter = _ERPListEditEnter;


	// ##################################################################
	// Add a tag to the ERP RW display.
	function _ERPReadAddChanged() {

		// Get the user selection.
		var tagname = document.forms.erplistinfo.erpreadadd.value;

		// This is the empty selection, so ignore it.
		if (tagname == this.ERPEmptySelection) {
			return;
		}

		// Check if the tag has already been added.
		if (this.ERPReadEditData.indexOf(tagname) >= 0) {
			return;
		}

		// Add the tag to the current data.
		this.ERPReadEditData.push(tagname);
		this.ERPReadEditData.sort();

		// Display it.
		this.PopulateERPTagEditList("erplistreadeditcurrent", this.ERPReadEditData);

		// Update the removal list.
		this.PopulateERPTagList("erpreadremove", this.ERPReadEditData);

	}
	this.ERPReadAddChanged = _ERPReadAddChanged;

	// ##################################################################
	// Remove a tag from the ERP RW display.
	function _ERPReadRemoveChanged() {

		// Get the user selection.
		var tagname = document.forms.erplistinfo.erpreadremove.value;

		// Remove the tag from the current data.
		tagindex = this.ERPReadEditData.indexOf(tagname);
		if (tagindex < 0) {
			return;
		}
		this.ERPReadEditData.splice(tagindex, 1);
		this.ERPReadEditData.sort();

		// Display it.
		this.PopulateERPTagEditList("erplistreadeditcurrent", this.ERPReadEditData);

		// Update the removal list.
		this.PopulateERPTagList("erpreadremove", this.ERPReadEditData);

	}
	this.ERPReadRemoveChanged = _ERPReadRemoveChanged;

	// ##################################################################
	// Add a tag to the ERP RO display.
	function _ERPWriteAddChanged() {

		// Get the user selection.
		var tagname = document.forms.erplistinfo.erpwriteadd.value;

		// This is the empty selection, so ignore it.
		if (tagname == this.ERPEmptySelection) {
			return;
		}

		// Check if the tag has already been added.
		if (this.ERPWriteEditData.indexOf(tagname) >= 0) {
			return;
		}

		// Add the tag to the current data.
		this.ERPWriteEditData.push(tagname);
		this.ERPWriteEditData.sort();

		// Display it.
		this.PopulateERPTagEditList("erplistwriteeditcurrent", this.ERPWriteEditData);

		// Update the removal list.
		this.PopulateERPTagList("erpwriteremove", this.ERPWriteEditData);

	}
	this.ERPWriteAddChanged = _ERPWriteAddChanged;

	// ##################################################################
	// Remove a tag from the ERP RO display.
	function _ERPWriteRemoveChanged() {

		// Get the user selection.
		var tagname = document.forms.erplistinfo.erpwriteremove.value;

		// Remove the tag from the current data.
		tagindex = this.ERPWriteEditData.indexOf(tagname);
		if (tagindex < 0) {
			return;
		}
		this.ERPWriteEditData.splice(tagindex, 1);
		this.ERPWriteEditData.sort();

		// Display it.
		this.PopulateERPTagEditList("erplistwriteeditcurrent", this.ERPWriteEditData);

		// Update the removal list.
		this.PopulateERPTagList("erpwriteremove", this.ERPWriteEditData);

	}
	this.ERPWriteRemoveChanged = _ERPWriteRemoveChanged;



}

// ##################################################################


