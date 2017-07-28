/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatusserver.js
# Purpose: 	MBLogic server communictions config display library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		06-Dec-2010
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
/* This is for the communication configuration display for TCP servers.
	This also handles the expanded data table register map.
	Parameters: utillib (object) = The utility display library.
*/
function ComServerDisplay(utillib, editlib) {


	// Utility library
	this.Utils = utillib;
	// Parameter edit library.
	this.EditLib = editlib;

	// The server data. The keys are the protocol types.
	this.ServerData = {};

	// These IDs are the keys to the web page table. 
	this.ServerIds = {"modbustcp" : ["modbustcp_name", "modbustcp_port", "modbustcp"],
			"mbhmi" : ["hmi_name", "hmi_port", "hmi"],
			"rhmi" : ["rhmi_name", "rhmi_port", "rhmi"],
			"erp" : ["erp_name", "erp_port", "erp"],
			"status" : ["status_name", "status_port", "status"],
			"help" : ["help_name", "help_port", "help"],
			"generic" : ["generic_name", "generic_port", "generic"],
			"mbrest" : ["mbrest_name", "mbrest_port", "mbrest"]
			};

	// Register config data.
	this.RegData = {};

	// Maximum holding register address.
	this.MaxReg = 1048575;

	// Server ID.
	this.ServerID = "";

	// ##################################################################
	// Display the server Id.
	function _UpdateServerId() {
		this.Utils.ShowCell("serverid", this.ServerID);
	}
	this.UpdateServerId = _UpdateServerId;



	// ##################################################################
	// Display the server data in a table.
	function _UpdateServerTable() {

		// Clear out any existing data.
		for (var protocol in this.ServerIds) {
			var serverids = this.ServerIds[protocol];
			// Server name.
			this.Utils.ShowCell(serverids[0], "");
			// Port.
			this.Utils.ShowCell(serverids[1], "");
		}

		// Display the new data.
		for (var protocol in this.ServerData) {

			var datarecord = this.ServerData[protocol];

			var servername = datarecord["servername"];
			var hostinfo = datarecord["port"];

			var serverids = this.ServerIds[protocol];

			// Server name.
			this.Utils.ShowCell(serverids[0], servername);
			// Port.
			this.Utils.ShowCell(serverids[1], hostinfo);
		}

	}
	this.UpdateServerTable = _UpdateServerTable;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		this.ServerID = pageresults['system']['serverid'];

		// Store the server data as an object for easier retrieval.
		this.ServerData = {};
		for (var serverindex in pageresults['serverdata']) {
			var server = pageresults['serverdata'][serverindex];
			this.ServerData[server["protocol"]] = {};
			this.ServerData[server["protocol"]]["servername"] = server["servername"];
			this.ServerData[server["protocol"]]["port"] = server["port"];
		}

		this.RegData = pageresults['expregisters'];

		// Display the data.
		this.UpdateServerId();

		this.UpdateServerTable();

		this.DisplayRegParams();

	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Return the current data in a format suitable for sending to the
	// server for saving the results.
	function _FormatSaveRequest() {
		var datareq = {}

		// Server ID.
		datareq['system'] = {};
		datareq['system']['serverid'] = this.ServerID;

		// Server data.
		serverdata = [];
		for (var server in this.ServerData) {
			record = this.ServerData[server];
			serverdata.push({"servername" : record["servername"],
					"protocol" : server,
					"port" : record["port"]});
		}
		datareq['serverdata'] = serverdata;

		// Expanded registers.
		datareq['expregisters'] = {};
		datareq['expregisters']['mbaddrexp'] = this.RegData['mbaddrexp'];
		datareq['expregisters']['mbaddroffset'] = this.RegData['mbaddroffset'];
		datareq['expregisters']['mbaddrfactor'] = this.RegData['mbaddrfactor'];

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
	// The server ID has changed.
	function _ServerIDChanged() {
		var serverid = document.forms.serveridconfig.serveridname.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.NameStringOK(serverid), "serveridname");
	}
	this.ServerIDChanged = _ServerIDChanged;

	// ##################################################################
	// Initialise the server id edit form with data.
	function _InitEditServerID() {
		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["serveridname"];
		this.EditLib.ResetFieldColours(editfields);

		// The server ID. 
		document.forms.serveridconfig.serveridname.value = this.ServerID;

	}
	this.InitEditServerID = _InitEditServerID;


	// ##################################################################
	// Save the server ID information.
	// Return true if the parameters were saved.
	function _ServerIDEditEnter() {

		// First, check the parameters.
		var serveridname = document.forms.serveridconfig.serveridname.value;

		// Display errors.
		this.ServerIDChanged();

		if (!this.EditLib.NameStringOK(serveridname)) { return false; }

		// Save the data. 
		this.ServerID = serveridname;

		// Display the new server id info.
		this.UpdateServerId();
		return true;
	}
	this.ServerIDEditEnter = _ServerIDEditEnter;




	// ##################################################################
	// The server name has changed.
	function _ServerNameChanged() {
		var servername = document.forms.serverconfig.servername.value;
		this.EditLib.ShowFieldStatusColour(this.EditLib.TagNameOK(servername), "servername");
	}
	this.ServerNameChanged = _ServerNameChanged;




	// ##################################################################
	// The port number has changed.
	function _PortNumberChanged() {
		var port = document.forms.serverconfig.port.value;

		// Was the port a valid number?
		this.EditLib.ShowFieldStatusColour(this.EditLib.PortOk(port), "port");
	}
	this.PortNumberChanged = _PortNumberChanged;

	// ##################################################################
	// Initialise the server editing form with data.
	// Parameters protocol (string) = The server protocol being edited.
	function _InitServerEdit(protocol) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["servername", "port"];
		this.EditLib.ResetFieldColours(editfields);

		// See if there is any existing protocol data. If not,
		// we have to create some defaults.
		if (protocol in this.ServerData) {
			var datarecord = this.ServerData[protocol];
			var hostinfo = datarecord["port"];
			var servername = datarecord["servername"];
		} else {
			var hostinfo = "8000";
			var servername = protocol;
		}


		// Heading for protocol type.
		var heading = this.ServerIds[protocol][2];
		this.Utils.ShowCell("protocolheading", heading);

		// The server name.
		document.forms.serverconfig.servername.value = servername;

		// Set the port number.
		document.forms.serverconfig.port.value = hostinfo;

		// Save the protocol so we can retrieve this later.
		document.forms.serverconfig.protocol.value = protocol;

	}
	this.InitServerEdit = _InitServerEdit;


	// ##################################################################
	// Save the server information.
	// Return true if the parameters were saved.
	function _ServerEditEnter() {

		// First, check the parameters.
		var servername = document.forms.serverconfig.servername.value;
		var port = document.forms.serverconfig.port.value;

		// Display errors.
		this.ServerNameChanged();
		this.PortNumberChanged();

		if (!this.EditLib.TagNameOK(servername)) { return false; }
		if (!this.EditLib.PortOk(port)) { return false; }
	
		// Retrieve the protocol type. This is a hidden field.
		var protocol = document.forms.serverconfig.protocol.value;

		// If the protocol data doesn't exist, create an empty record.
		if (!(protocol in this.ServerData)) {
			this.ServerData[protocol] = {};
			this.ServerData[protocol]["servername"] = "";
			this.ServerData[protocol]["port"] = "";
		}
		var datarecord = this.ServerData[protocol];

		// Save the data. 
		datarecord["servername"] = servername;
		datarecord["port"] = port;

		// Display the new server info.
		this.UpdateServerTable();
		return true;
	}
	this.ServerEditEnter = _ServerEditEnter;


	// ##################################################################
	// Delete a server record.
	function _ServerEditDelete() {

		// Retrieve the protocol type. This is a hidden field.
		var protocol = document.forms.serverconfig.protocol.value;

		// Erase the data.
		delete this.ServerData[protocol];

		// Update the display.
		this.UpdateServerTable();

	}
	this.ServerEditDelete = _ServerEditDelete;



	// ##################################################################
	// Display the parameters.
	function _DisplayRegParams() {

		var enabled = this.RegData["mbaddrexp"];

		// Whether expanded register map is enabled or disabled.
		if (enabled) {
			var mbaddrexp = TextDefsGeneralMsgs["incremental"];
		} else {
			var mbaddrexp = TextDefsGeneralMsgs["disabled"];
		}
		this.Utils.ShowCell("mbaddrexp", mbaddrexp);

		// Expanded register map unit IDs and offsets.
		var expdatatable1 = document.getElementById("mbuidoffset1");
		var expdatatable2 = document.getElementById("mbuidoffset2");
		var lcol = true;


		// Delete all the rows in any existing table, but not the header.
		while (expdatatable1.rows.length > 1) {
			expdatatable1.deleteRow(-1);
		}

		while (expdatatable2.rows.length > 1) {
			expdatatable2.deleteRow(-1);
		}

		if (enabled) {
			this.Utils.TRowStart();
			var mbuidoffset = this.RegData["mbuidoffset"];
			for (var uid in mbuidoffset) {
			
				// Alternate the columns used for display.
				if (lcol) {
					var trow = expdatatable1.insertRow(-1);
					// This is used to provide alternating row colours.
					var tdclass = this.Utils.TRowAlternate();
				} else {
					var trow = expdatatable2.insertRow(-1);
				}
				var lcol = !lcol;

				// First cell is unit id.
				this.Utils.InsertTableCell(trow, 0, uid, tdclass);
				// Second cell is address offset.
				this.Utils.InsertTableCell(trow, 1, mbuidoffset[uid], tdclass);
			}
		}
	}
	this.DisplayRegParams = _DisplayRegParams;


	// ##################################################################
	// Hide the details display.
	function _HideDetails() {
		this.Utils.HidePageArea("expdetails");
	}
	this.HideDetails = _HideDetails;

	// ##################################################################
	// Show the details display.
	function _ShowDetails() {
		this.Utils.ShowPageArea("expdetails");
	}
	this.ShowDetails = _ShowDetails;



	// ##################################################################
	// Register map editing functions.



	// ##################################################################
	// The unit ID offset has changed.
	function _UIDOffsetChanged() {
		var reg = document.forms.expregconfig.uidoffset.value;

		// Was the value a valid number?
		this.EditLib.ShowFieldStatusColour(this.EditLib.IntOk(reg, 0, this.MaxReg), "uidoffset");
	}
	this.UIDOffsetChanged = _UIDOffsetChanged;


	// ##################################################################
	// The register factor has changed.
	function _RegFactorChanged() {
		var reg = document.forms.expregconfig.regfactor.value;

		// Was the value a valid number?
		this.EditLib.ShowFieldStatusColour(this.EditLib.IntOk(reg, 0, this.MaxReg), "regfactor");
	}
	this.RegFactorChanged = _RegFactorChanged;


	// ##################################################################
	// The enable selection has changed.
	function _EnableChanged() {

		// Find out which radio button was checked.
		var radiocheck = this.EnableMode();		
		this.SetParamsToEnableMode(radiocheck);
	}
	this.EnableChanged = _EnableChanged;


	// ##################################################################
	// Determine if the expanded register system is enabled.
	// Returns true if enabled.
	function _EnableMode() {
		return document.forms.expregconfig.expregenable[1].checked;
	}
	this.EnableMode = _EnableMode;


	// ##################################################################
	// Set the remaining parameters according to the enable mode.
	function _SetParamsToEnableMode(mode) {

		if (mode) {
			this.Utils.ShowPageArea("expregparams");
		} else {
			this.Utils.HidePageArea("expregparams");
		}
	}
	this.SetParamsToEnableMode = _SetParamsToEnableMode;


	// ##################################################################
	// Initialise the expanded register map editing form with data.
	function _InitRegsEdit() {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["uidoffset", "regfactor"];
		this.EditLib.ResetFieldColours(editfields);

		// Enabled or disabled.
		if (this.RegData["mbaddrexp"]) {
			document.forms.expregconfig.expregenable[1].checked = true;
		} else {
			document.forms.expregconfig.expregenable[0].checked = true;
		}

		// The unit id offset.
		document.forms.expregconfig.uidoffset.value = this.RegData["mbaddroffset"];

		// The register multiplier factor.
		document.forms.expregconfig.regfactor.value = this.RegData["mbaddrfactor"];


	}
	this.InitRegsEdit = _InitRegsEdit;


	// ##################################################################
	// Save the register map information.
	// Return true if the parameters were saved.
	function _RegsEditEnter() {


		// First, check the parameters.
		var enabled = this.EnableMode();
		var uidoffset = document.forms.expregconfig.uidoffset.value;
		var regfactor = document.forms.expregconfig.regfactor.value;

		// We only care about the other parameters if enabled.
		if (enabled) {
			// Display errors.
			this.UIDOffsetChanged();
			this.RegFactorChanged();
			if ((!this.EditLib.IntOk(uidoffset, 0, this.MaxReg)) || 
				(!this.EditLib.IntOk(regfactor, 1, this.MaxReg))) {
				return false;
			}
		}

		// Save the data. 
		this.RegData["mbaddrexp"] = enabled;
		this.RegData["mbaddroffset"] = uidoffset;
		this.RegData["mbaddrfactor"] = regfactor;


		// Recalculate the register offset tables.

		var regfactorvalue = parseInt(regfactor, 10);
		var uidoffsetvalue = parseInt(uidoffset, 10);

		// Generate the list of offsets.
		var offlist = [];
		var maxreg = this.MaxReg - 65535;
		for (var i=0; i <= maxreg; ) {
			offlist.push("" + i);
			i = i + regfactorvalue;
		}

		// Generate the list of unit IDs.
		var uidlist = [];
		for (var i=uidoffsetvalue; i < 256; i++) {
			uidlist.push("" + i);
		}

		// Delete the old offset table. 
		delete this.RegData["mbuidoffset"];
		this.RegData["mbuidoffset"] = {}

		// The table size is limited to the shortest list.
		if (uidlist.length < offlist.length) {
			var maxtable = uidlist.length;
		} else {
			var maxtable = offlist.length;
		}

		// Create the new offset table.
		for (var i=0; i < maxtable; i++) {
			this.RegData["mbuidoffset"][uidlist[i]] = offlist[i];
		}


		// Display the new info.
		this.DisplayRegParams();
		return true;
	}
	this.RegsEditEnter = _RegsEditEnter;



}

// ##################################################################


