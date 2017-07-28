/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatusplcio.js
# Purpose: 	MBLogic status display library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		24-Sep-2010
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
/* This is for the soft logic IO status.
*/
function PLCIOStatus(utillib, editlib) {

	// Utility library
	this.Utils = utillib;
	// Parameter edit library.
	this.EditLib = editlib;

	this.logiciodata = null;
	// Sorted list of tags.
	this.SortedTags = [];


	// ##################################################################
	// Sort the table by tag name.
	function _SortTagNames() {
		var tagdata = this.logiciodata["logicioconfig"];

		// Clear the tag list.
		this.SortedTags = [];

		for (var tag in tagdata) {
			this.SortedTags.push(tag);
		}
		// Sort the array of tags.
		this.SortedTags.sort();
	}
	this.SortTagNames = _SortTagNames;


	// ##################################################################
	// Sort the table by a selected alphabetic field.
	function _SortAlpha(field) {
		var tagdata = this.logiciodata["logicioconfig"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
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
	// Sort the table numerically on a selected field.
	function _SortNumeric(field) {
		var tagdata = this.logiciodata["logicioconfig"]

		// Create a temporary array.
		var tagarray = [];
		// Create a decorated array.
		for (var tag in tagdata) {
			
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
		case "base" : { this.SortNumeric("base"); break;}
		case "action" : { this.SortAlpha("action"); break;}
		case "logictable" : { this.SortAlpha("logictable"); break;}
		}

		// Re-display the data.
		this.UpdateIOConfig();

	}
	this.SortTagTable = _SortTagTable;


	// ##################################################################
	// Fill the IO configuration table with data.
	function _UpdateIOConfig() {
		var iotable = document.getElementById("ioconfig");
		var iodata = this.logiciodata["logicioconfig"];
		this.Utils.TRowStart();

		// Delete all the rows in any existing table, but not the header.
		while (iotable.rows.length > 1) {
			iotable.deleteRow(-1);
		}

		// Display the table data.
		for (var tagindex in this.SortedTags) {
			var io = this.SortedTags[tagindex];

			var trow = iotable.insertRow(-1);
			// This adds an onclick event to allow editing of that record.
			trow.setAttribute("onclick", "SLIOTagEdit('" + io + "')");

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// IO Section.
			this.Utils.InsertTableCell(trow, 0, io, tdclass);
			// Address Type.
			this.Utils.InsertTableCell(trow, 1, iodata[io]["addrtype"], tdclass);

			// String types have a string length parameter.
			if (iodata[io]["strlen"] > 0) {
				baselen = "  length(" + iodata[io]["strlen"] + ")";
			} else {
				baselen = "";
			}
			// Server Base Address.
			this.Utils.InsertTableCell(trow, 2, iodata[io]["base"] + baselen, tdclass);

			// IO Action.
			this.Utils.InsertTableCell(trow, 3, iodata[io]["action"], tdclass);
			// Soft Logic Addresses.
			this.Utils.InsertTableCell(trow, 4, iodata[io]["logictable"].join(", "), tdclass);
		}
	}
	this.UpdateIOConfig = _UpdateIOConfig;


	// ##################################################################
	// Fill the soft logic system parameters table.
	function _UpdateSystemParams() {
		this.Utils.ShowCell("type", this.logiciodata["sysparams"]["type"]);
		this.Utils.ShowCell("plcprog", this.logiciodata["sysparams"]["plcprog"]);
		this.Utils.ShowCell("scan", this.logiciodata["sysparams"]["scan"]);
	}
	this.UpdateSystemParams = _UpdateSystemParams;


	// ##################################################################
	// Fill the soft logic system parameters table.
	function _UpdateMemSaveParams() {
		this.Utils.ShowCell("updateinterval", this.logiciodata["memsaveparams"]["updateinterval"]);
		this.Utils.ShowCell("wordaddr", this.logiciodata["memsaveparams"]["wordaddr"].join(", "));

		// If the memory save parameters are disabled, hide the parameter 
		// values and just show a default view. A negative update interval will
		// disable memory save.
		if (this.logiciodata["memsaveparams"]["updateinterval"] > 0) {
			this.MemSaveParamsShowEnable(true);
		} else {
			this.MemSaveParamsShowEnable(false);
		}

	}
	this.UpdateMemSaveParams = _UpdateMemSaveParams;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		this.logiciodata = pageresults;
		// Fill in the system parameters.
		this.UpdateSystemParams();
		this.UpdateMemSaveParams();
		// Fill the IO configuration table with data.
		// We sort by tag name by default.
		this.SortTagNames();
		this.UpdateIOConfig();

	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Return the current data in a format suitable for sending to the
	// server for saving the results.
	function _FormatSaveRequest() {
		var datareq = {}

		// Configuration data.
		datareq["memsaveparams"] = this.logiciodata["memsaveparams"]
		datareq["sysparams"] = this.logiciodata["sysparams"]
		datareq["logicioconfig"] = this.logiciodata["logicioconfig"]

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
	// Determine if the memory save is enabled.
	// Returns true if enabled.
	function _EnableMode() {
		return document.forms.memsaveparams.memsaveenable[1].checked;
	}
	this.EnableMode = _EnableMode;


	// ##################################################################
	// Set the remaining memory save parameters according to the enable mode.
	function _SetParamsToEnableMode(mode) {

		if (mode) {
			this.Utils.ShowPageArea("memparams");
		} else {
			this.Utils.HidePageArea("memparams");
		}
	}
	this.SetParamsToEnableMode = _SetParamsToEnableMode;


	// ##################################################################
	// Determine if the page is in view or edit modes.
	// Returns true if in edit mode.
	function _EditMode() {
		return document.forms.editmode.mode[1].checked;
	}
	this.EditMode = _EditMode;

	// ##################################################################
	function _FileNameOK(programfile) {
		return /^[0-9a-zA-Z][0-9a-zA-Z\.]+$/.test(programfile);
	}
	this.FileNameOK = _FileNameOK;


	// ##################################################################
	function _ProgramFileChanged() {
		var programfile = document.forms.sysparams.programfile.value;
		this.EditLib.ShowFieldStatusColour(this.FileNameOK(programfile), "programfile")
	}
	this.ProgramFileChanged = _ProgramFileChanged;


	// ##################################################################
	function _ScanRateChanged() {
		var scanrate = document.forms.sysparams.scanrate.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.IntOk(scanrate, 10, 65535), "scanrate")
	}
	this.ScanRateChanged = _ScanRateChanged;


	// ##################################################################
	function _EnableChanged() {
		var radiocheck = this.EnableMode();	

		// If the memory save was disabled (and therefore negative), set the
		// enabled value to some reasonable positive number. 
		if (radiocheck) {
			var scanrate = document.forms.memsaveparams.updateinterval.value;
			if (scanrate < 0) {
				document.forms.memsaveparams.updateinterval.value = 10.0;
			}
		}
		this.SetParamsToEnableMode(radiocheck);
	}
	this.EnableChanged = _EnableChanged;


	// ##################################################################
	function _UpdateIntervalChanged() {
		var scanrate = document.forms.memsaveparams.updateinterval.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.NumberOk(scanrate, 1.0, 65535.0), "updateintervaledit");
	}
	this.UpdateIntervalChanged = _UpdateIntervalChanged;


	// ##################################################################
	function _MemSaveAddressesChanged() {
		var memsaveaddresses = document.forms.memsaveparams.memsaveaddresses.value;
		this.EditLib.ShowFieldStatusColour(memsaveaddresses.length > 0, "memsaveaddresses")
	}
	this.MemSaveAddressesChanged = _MemSaveAddressesChanged;


	// ##################################################################
	// Show either the memory save parameters, or show a disabled view
	// in the main table display.
	function _MemSaveParamsShowEnable(mode) {
		if (mode) {
			this.Utils.ShowPageArea("slmemsaveenabled");
			this.Utils.HidePageArea("slmemsavedisabled");
		} else {
			this.Utils.HidePageArea("slmemsaveenabled");
			this.Utils.ShowPageArea("slmemsavedisabled");
		}
	}
	this.MemSaveParamsShowEnable = _MemSaveParamsShowEnable;


	// ##################################################################
	// Initialise the soft logic system parameters editing form with data.
	function _SysParamsEditInit() {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["programfile", "scanrate"];
		this.EditLib.ResetFieldColours(editfields);

		var plcprog = this.logiciodata["sysparams"]["plcprog"];
		var scan = this.logiciodata["sysparams"]["scan"];
		var scanratenumber = parseInt(scan, 10);

		// The soft logic program file name.
		document.forms.sysparams.programfile.value = plcprog;

		// The target scan rate (scan delay).
		document.forms.sysparams.scanrate.value = scanratenumber;

	}
	this.SysParamsEditInit = _SysParamsEditInit;


	// ##################################################################
	// Initialise the memory save parameters editing form with data.
	function _InitMemParamsEdit() {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["updateintervaledit", "memsaveaddresses"];
		this.EditLib.ResetFieldColours(editfields);

		var updateinterval = this.logiciodata["memsaveparams"]["updateinterval"];
		var updateinternumber = parseFloat(updateinterval);
		var wordaddr = this.logiciodata["memsaveparams"]["wordaddr"];


		// Enabled or disabled. Disabled if update interval is negative.
		if (updateinternumber < 0) {
			document.forms.memsaveparams.memsaveenable[0].checked = true;
			this.SetParamsToEnableMode(false);
		} else {
			document.forms.memsaveparams.memsaveenable[1].checked = true;
			this.SetParamsToEnableMode(true);
		}

		// The update interval.
		document.forms.memsaveparams.updateinterval.value = updateinterval;

		// The list of addresses to save.
		document.forms.memsaveparams.memsaveaddresses.value = wordaddr.join(", ");


	}
	this.InitMemParamsEdit = _InitMemParamsEdit;


	// ##################################################################
	// Save the system parameter information.
	// Return true if the parameters were saved.
	function _SysParamsEditEnter() {


		// First, check the parameters.
		var programfile = document.forms.sysparams.programfile.value;
		var scanrate = document.forms.sysparams.scanrate.value;

		// Display errors.
		this.ProgramFileChanged();
		this.ScanRateChanged();
		if ((!this.EditLib.IntOk(scanrate, 10, 65535)) || 
			!this.FileNameOK(programfile)) {
			return false;
		}

		// Save the data. 
		this.logiciodata["sysparams"]["plcprog"] = programfile;
		this.logiciodata["sysparams"]["scan"] = scanrate;


		// Display the new info.
		this.UpdateSystemParams();
		return true;
	}
	this.SysParamsEditEnter = _SysParamsEditEnter;


	// ##################################################################
	// Save the memory save parameter information.
	// Return true if the parameters were saved.
	function _MemSaveParamsEditEnter() {


		// First, check the parameters.
		var memsaveaddresses = document.forms.memsaveparams.memsaveaddresses.value;
		var updateinterval = document.forms.memsaveparams.updateinterval.value;

		// Strip all the blanks from the memory save addresses.
		var memsaveaddresses = memsaveaddresses.replace(/ /g, "");

		// Display errors.
		this.UpdateIntervalChanged();
		this.MemSaveAddressesChanged();

		// Set update interval to negative if disabled.
		if (document.forms.memsaveparams.memsaveenable[0].checked) {
			var updateinterval = -1.0;
		}

		// If negative, this disables the update.
		if (this.EditLib.IsNegativeNumber(updateinterval)) {
			var updateinterval = -1.0;
		} else {
			if ((!this.EditLib.NumberOk(updateinterval, 1, 65535)) || 
				(memsaveaddresses.length < 1)) {
				return false;
			}
		}

		// Save the data. 
		this.logiciodata["memsaveparams"]["updateinterval"] = updateinterval;

		// Split the string into an array.
		// If there are no addresses, we need to handle this specially as 
		// otherwise Javascript may leave one empty string in the array.
		if (memsaveaddresses.length > 0) {
			var memsavelist = memsaveaddresses.split(",");
		} else {
			var memsavelist = [];
		}
		this.logiciodata["memsaveparams"]["wordaddr"] = memsavelist;


		// Display the new info.
		this.UpdateMemSaveParams();
		return true;
	}
	this.MemSaveParamsEditEnter = _MemSaveParamsEditEnter;


	// ##################################################################
	// IO section tag name changed.
	function _SLIOTagChanged() {
		var sliotag = document.forms.sliotagparams.sliotag.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.TagNameOK(sliotag), "sliotag")
	}
	this.SLIOTagChanged = _SLIOTagChanged;

	// ##################################################################
	// Address type changed.
	function _AddrTypeChanged() {
		var addrtype = document.forms.sliotagparams.addresstype.value;
		// Find the correct category.
		var addrcategory = this.EditLib.GetAddrCategory(addrtype);

		// If the address type is string.
		if (addrcategory == "string") {
			this.Utils.ShowPageArea("tageditstringproperties");
		} else {
			this.Utils.HidePageArea("tageditstringproperties");
		}
	}
	this.AddrTypeChanged = _AddrTypeChanged;


	// ##################################################################
	// The base memory address has changed.
	function _BaseAddrChanged() {
		var baseaddr = document.forms.sliotagparams.baseaddr.value;
		// The maximum address range depends on the address type.
		var addrtype = document.forms.sliotagparams.addresstype.value;

		// Check if this is a valid data table address.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckMemAddr(baseaddr, addrtype), "baseaddr")
	}
	this.BaseAddrChanged = _BaseAddrChanged;


	// ##################################################################
	// The string length has changed.
	function _StringLengthChanged() {
		var stringlen = document.forms.sliotagparams.stringlength.value;

		// Check if this is a valid number.
		this.EditLib.ShowFieldStatusColour(this.EditLib.CheckInteger(stringlen), "stringlength")
	}
	this.StringLengthChanged = _StringLengthChanged;


	// ##################################################################
	// The soft logic IO address list changed.
	function _SLIOAddressesChanged() {
		var slioaddresses = document.forms.sliotagparams.slioaddresses.value;
		var slioaddrstr = slioaddresses.replace(/ /g, "");
		this.EditLib.ShowFieldStatusColour(slioaddrstr.length > 0, "slioaddresses")
	}
	this.SLIOAddressesChanged = _SLIOAddressesChanged;



	// ##################################################################
	// Initialise the soft logic IO parameters editing form with data.
	// Parameters: sliotag (string) = The IO section name.
	function _InitSLIOTagEdit(sliotag) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["sliotag", "baseaddr", "stringlength", "slioaddresses"];
		this.EditLib.ResetFieldColours(editfields);


		// If no tag name is provided, use default parameters in a new record.
		if (sliotag.length > 0) {
			var tagdata = this.logiciodata["logicioconfig"][sliotag];
			var addrtype = tagdata["addrtype"];
			var baseaddress = tagdata["base"];
			var stringlength = tagdata["strlen"];
			var action = tagdata["action"];
			var sladdresses = tagdata["logictable"].join(", ");
		} else {
			var addrtype = "coil";
			var baseaddress = 0;
			var stringlength = 0;
			var action = "read";
			var sladdresses = " ";
		}


		// IO section name.
		document.forms.sliotagparams.sliotag.value = sliotag;
		// Address type.
		var addrindex = this.EditLib.GetAddrTypeIndex(addrtype);
		document.forms.sliotagparams.addresstype[addrindex].selected = "1";
		// Server base address.
		document.forms.sliotagparams.baseaddr.value = baseaddress;
		// String length.
		document.forms.sliotagparams.stringlength.value = stringlength;
		// IO Action.

		if (action == "read") {
			document.forms.sliotagparams.slioaction[0].checked = true;
		} else {
			document.forms.sliotagparams.slioaction[1].checked = true;
		}

		// Soft logic addresses.
		document.forms.sliotagparams.slioaddresses.value = sladdresses;

		// Show the appropriate fields according to the address type.
		this.AddrTypeChanged();
		
	}
	this.InitSLIOTagEdit = _InitSLIOTagEdit;



	// ##################################################################
	// Save the soft logic IO parameter information.
	// Return true if the parameters were saved.
	function _SLIOEditEnter() {

		// Get the parameters.
		var sliotag = document.forms.sliotagparams.sliotag.value;
		var baseaddr = document.forms.sliotagparams.baseaddr.value;
		// The address type.
		var addresstype = document.forms.sliotagparams.addresstype.value;
		var strlength = document.forms.sliotagparams.stringlength.value;
		// Soft logic addresses.
		var slioaddresses = document.forms.sliotagparams.slioaddresses.value;


		// Check the parameters.

		// The address tag name.
		if (!this.EditLib.TagNameOK(sliotag)) { 
			this.SLIOTagChanged();
			return false; 
		}

		// The memory base address.
		if(!this.EditLib.CheckMemAddr(baseaddr, addresstype)) { 
			this.BaseAddrChanged();
			return false; 
		}


		// Find the address category.
		var addresscategory = this.EditLib.GetAddrCategory(addresstype);

		// The address format depends on the address type.
		if (addresscategory == "string") {
			if (!this.EditLib.CheckInteger(strlength)) {
				this.StringLengthChanged();
				return false;
			}
		}


		var slioaddrstr = slioaddresses.replace(/ /g, "").toUpperCase();
		var slioaddrlist = slioaddrstr.split(",");
		// The soft logic addresses.
		if (slioaddrstr.length < 1) { 
			this.SLIOAddressesChanged();
			return false; 
		}


		var tagdata = this.logiciodata["logicioconfig"];

		// If the tag doesn't exist, create an empty record.
		if (!(sliotag in tagdata)) {
			tagdata[sliotag] = {};
		}
		var datarecord = tagdata[sliotag];


		// Now, save the data and update the display.
		datarecord["base"] = baseaddr;
		datarecord["addrtype"] = addresstype;
		datarecord["strlen"] = strlength;
		datarecord["logictable"] = slioaddrlist;
		if (document.forms.sliotagparams.slioaction[0].checked) {
			datarecord["action"] = "read";
		} else {
			datarecord["action"] = "write";
		}

		// Fill the address tag table with the tag info.
		this.SortTagNames();
		this.UpdateIOConfig();

		return true;
	}
	this.SLIOEditEnter = _SLIOEditEnter;


	// ##################################################################
	// Delete a record.
	function _SLIOEditDelete() {
		// The address tag name.
		var tagname = document.forms.sliotagparams.sliotag.value;

		var tagdata = this.logiciodata["logicioconfig"];
		// If the tag exists, delete the record.
		if (tagname in tagdata) {
			delete tagdata[tagname];
			this.SortTagNames();
			this.UpdateIOConfig();
		}
	}
	this.SLIOEditDelete = _SLIOEditDelete;




}

// ##################################################################


