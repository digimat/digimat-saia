/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatusclient.js
# Purpose: 	MBLogic client communictions config library.
# Language:	javascript
# Date:		01-Jun-2010
# Ver:		27-Dec-2010
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
/* This is for the communication configuration display for TCP and generic clients.
	Parameters: utillib (object) = The utility display library.
*/
function ComClientDisplay(utillib, editlib) {

	// Utility library
	this.Utils = utillib;
	// Parameter edit library.
	this.EditLib = editlib;

	this.TCPClientInfo = null;

	// This holds TCP client data which has been reformatted to allow
	// the information to be addressed by connection name. 
	this.TCPClientData = {};



	// ##################################################################
	// Reformat TCP client data so it can be addressed by connection name.	
	function _FormatTCPClientData() {
		for (var cname in this.TCPClientInfo) {
			this.TCPClientData[this.TCPClientInfo[cname]["connectionname"]] = this.TCPClientInfo[cname];
		}
	}
	this._FormatTCPClientData = _FormatTCPClientData;




	// ##################################################################
	// This is used to insert new information into a table which 
	// is allowed to grow in length. It also adds an "onclick" event
	// to the individual cell. This version is required because we
	// have one cell in each row which already has its own "onclick",
	// and we don't want to activate both events at once.
	function _InsertTableClickCell(trow, cellcolum, text, tdclass, clickevent) {
			var cell = trow.insertCell(cellcolum);
			var celltext = document.createTextNode(text);
			if (tdclass != "") {
				cell.setAttribute("class", tdclass);
			}
			// Add the onclick event.
			cell.setAttribute("onclick", clickevent);
			cell.appendChild(celltext);
	}
	this.InsertTableClickCell = _InsertTableClickCell;



	// ##################################################################
	// Fill the TCP client table with data.
	function _UpdateTCPClients() {
		var TCPClienttable = document.getElementById("tcpclienttable");

		// Delete all the table rows (if they exist), but not the header.
		while (TCPClienttable.rows.length > 1) {
			TCPClienttable.deleteRow(-1);
		}

		// Create a list so we can sort the clients by name.
		var tcpclientlist = [];
		for (var client in this.TCPClientData) {
			tcpclientlist.push(client);
		}
		tcpclientlist.sort();


		this.Utils.TRowStart();
		for (var i in tcpclientlist) {
			var TCPClient = tcpclientlist[i];

			var record = this.TCPClientData[TCPClient];

			var trow = TCPClienttable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();
			// This creates the "onclick" event.
			var clickevent = "TCPClientEdit('" + record["connectionname"] + "');";

			// Connection name.
			this.InsertTableClickCell(trow, 0, TCPClient, tdclass, clickevent);
			// Protocol.
			this.InsertTableClickCell(trow, 1, record["protocol"], tdclass, clickevent);
			// IP address.
			this.InsertTableClickCell(trow, 2, record["host"], tdclass, clickevent);
			// Port.
			this.InsertTableClickCell(trow, 3, record["port"], tdclass, clickevent);
			// Command action.
			this.InsertTableClickCell(trow, 4, record["action"], tdclass, clickevent);

			// View details button. This is a button which gets automatically added to each row
			var cell = trow.insertCell(5);
			var viewbutton = document.createElement("button");
			viewbutton.setAttribute("onclick", 
				"ShowTCPClient('" + TCPClient + "');");
			var viewbuttonname = document.createTextNode("View");
			viewbutton.appendChild(viewbuttonname);
			
			cell.appendChild(viewbutton);
			cell.setAttribute("class", tdclass);

		}

	}
	this.UpdateTCPClients = _UpdateTCPClients;


	// Used to address the TCP client details fields sequentially.
	this.TCPClientfields = ["cmdtime", "repeattime", "retrytime", "fault_inp", 
			"fault_coil", "fault_inpreg", "fault_holdingreg", "fault_reset"];
	this.tcppagefields = ["tcpcmdtime", "tcprepeattime", "tcpretrytime", "tcpfault_inp", 
			"tcpfault_coil", "tcpfault_inpreg", "tcpfault_holdingreg", "tcpfault_reset"];

	// ##################################################################
	// Create the details for a single TCP client.
	function _PopulateTCPClientDetails(connectionname) {


		// Show the name of the TCPClient.
		this.Utils.ShowCell("tcpclientdetailname", connectionname)
		

		// Fill in the field names for the tables with fixed ids.
		for (var field in this.TCPClientfields) {
			var fieldname = this.TCPClientfields[field];
			var pagefieldname = this.tcppagefields[field];
			this.Utils.ShowCell(pagefieldname, this.TCPClientData[connectionname][fieldname]);
		}


		// Fill in the command list.
		var TCPClientcommandstable = document.getElementById("tcpclientcommandstable");
		var TCPClientcmds = this.TCPClientData[connectionname]["cmdlist"]
		this.Utils.TRowStart();
		for (var cmd in TCPClientcmds) {
			var trow = TCPClientcommandstable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Command name.
			this.Utils.InsertTableCell(trow, 0, TCPClientcmds[cmd]["command"], tdclass);
			// Function code.
			this.Utils.InsertTableCell(trow, 1, TCPClientcmds[cmd]["function"], tdclass);
			// Remote memory address.
			this.Utils.InsertTableCell(trow, 2, TCPClientcmds[cmd]["remoteaddr"], tdclass);
			// Quantity.
			this.Utils.InsertTableCell(trow, 3, TCPClientcmds[cmd]["qty"], tdclass);
			// Local memory address.
			this.Utils.InsertTableCell(trow, 4, TCPClientcmds[cmd]["memaddr"], tdclass);
			// Unit ID.
			this.Utils.InsertTableCell(trow, 5, TCPClientcmds[cmd]["uid"], tdclass);
		}
	}
	this.PopulateTCPClientDetails = _PopulateTCPClientDetails;



	// ##################################################################
	// Delete the command list table to prepare it for new data.
	function _DeleteCmdList() {
		var cmdtable = document.getElementById("tcpclientcommandstable");
		// Delete all the rows, but not the header.
		while (cmdtable.rows.length > 1) {
			cmdtable.deleteRow(-1);
		}
	}
	this.DeleteTCPCmdList = _DeleteCmdList;

	// ##################################################################
	// Hide the TCP client details display.
	function _HideTCPClientDetails() {
		var TCPClientshow = document.getElementById("tcpclientdetails");
		TCPClientshow.setAttribute("class", "datahide");
	}
	this.HideTCPClientDetails = _HideTCPClientDetails;

	// ##################################################################
	// Show the TCP client details display.
	function _ShowTCPClientDetails() {
		var TCPClientshow = document.getElementById("tcpclientdetails");
		TCPClientshow.setAttribute("class", "datashow");
	}
	this.ShowTCPClientDetails = _ShowTCPClientDetails;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		this.TCPClientInfo = pageresults['tcpclientinfo'];
		this.GenClientInfo = pageresults['genclientinfo'];

		// TCP clients.
		// Reformat the TCP client data so we can address it by name.
		this._FormatTCPClientData();
		// Fill the TCPClient table with data.
		this.UpdateTCPClients();

		// Generic clients.
		// Reformat the client data so we can address it by name.
		this._FormatGenClientData();
		// Fill the client table with data.
		this.UpdateGenClients();
	}
	this.UpdatePageResults = _UpdatePageResults;


	// ##################################################################
	// Display the details for a selected TCP client.
	function _ShowTCPClient(connectionname) {
		// Delete the list of commands if any are already present.
		this.DeleteTCPCmdList();

		// Populate the tables with fresh data.
		this.PopulateTCPClientDetails(connectionname);

		// Display the TCP client details if they are still hidden.
		this.ShowTCPClientDetails();
	}
	this.ShowTCPClient = _ShowTCPClient;

	this.GenClientInfo = null;

	// This holds client data which has been reformatted to allow
	// the information to be addressed by connection name. 
	this.GenClientData = {};


	// ##################################################################
	// Reformat client data so it can be addressed by connection name.	
	function _FormatGenClientData() {
		for (var cname in this.GenClientInfo) {
			this.GenClientData[this.GenClientInfo[cname]["connectionname"]] = this.GenClientInfo[cname];
		}
	}
	this._FormatGenClientData = _FormatGenClientData;



	// ##################################################################
	// Fill the client table with data.
	function _UpdateGenClients() {
		var clienttable = document.getElementById("gentable");

		// Delete all the table rows (if they exist), but not the header.
		while (clienttable.rows.length > 1) {
			clienttable.deleteRow(-1);
		}


		// Create a list so we can sort the clients by name.
		var genclientlist = [];
		for (var client in this.GenClientData) {
			genclientlist.push(client);
		}
		genclientlist.sort();


		this.Utils.TRowStart();

		for (var i in genclientlist) {
			var client = genclientlist[i];

			var record = this.GenClientData[client];

			// This is used to provide alternating row colours.
			var trow = clienttable.insertRow(-1);
			var tdclass = this.Utils.TRowAlternate();
			// This creates the "onclick" event.
			var clickevent = "GenClientEdit('" + record["connectionname"] + "');";

			// Connection name.
			this.InsertTableClickCell(trow, 0, client, tdclass, clickevent);
			// Protocol.
			this.InsertTableClickCell(trow, 1, record["protocol"], tdclass, clickevent);
			// Command action.
			this.InsertTableClickCell(trow, 2, record["action"], tdclass, clickevent);

			// View details button. This is a button which gets automatically added to each row
			var cell = trow.insertCell(3);
			var viewbutton = document.createElement("button");
			viewbutton.setAttribute("onclick", "ShowGenClient('" + record["connectionname"] + "');");
			var viewbuttonname = document.createTextNode("View");
			viewbutton.appendChild(viewbuttonname);
			
			cell.appendChild(viewbutton);
			cell.setAttribute("class", tdclass);

		}

	}
	this.UpdateGenClients = _UpdateGenClients;


	// Used to address the client faults fields sequentially.
	this.genfaultnamefields = ["fault_inp", "fault_coil", "fault_inpreg", "fault_holdingreg", "fault_reset"];
	this.genfaultpagefields = ["genfault_inp", "genfault_coil", "genfault_inpreg", "genfault_holdingreg", "genfault_reset"];

	// Used to address the client data table read/write fields.
	this.gendtreadfields = ["inp", "coil", "inpreg", "holdingreg"];
	this.dtreadaddr = ["gendtrd_inp", "gendtrd_coil", "gendtrd_inpreg", "gendtrd_holdingreg"];
	this.gendtreadlength = ["gendtrdlen_inp", "gendtrdlen_coil", "gendtrdlen_inpreg", "gendtrdlen_holdingreg"];

	this.gendtwritefields = ["inp", "coil", "inpreg", "holdingreg"];
	this.gendtwriteaddr = ["gendtwrt_inp", "gendtwrt_coil", "gendtwrt_inpreg", "gendtwrt_holdingreg"];
	this.gendtwritelength = ["gendtwrtlen_inp", "gendtwrtlen_coil", "gendtwrtlen_inpreg", "gendtwrtlen_holdingreg"];

	// General client parameters.
	this.gengeneralparamids = ["genclientfile", "genclientrestart"];
	this.gengeneralparams = ["clientfile", "restartonfail"];


	// ##################################################################
	// Create the details for a single client.
	function _PopulateGenClientDetails(connectionname) {


		// Show the name of the client.
		this.Utils.ShowCell("genclientdetailname", connectionname)

		// Fill in the general parameters.
		for (var field in this.gengeneralparamids) {
			var fieldname = this.gengeneralparams[field];
			var pagefieldname = this.gengeneralparamids[field];
			this.Utils.ShowCell(pagefieldname, this.GenClientData[connectionname][fieldname]);
		}


		// Fill in the fault addresses.
		for (var field in this.genfaultnamefields) {
			var fieldname = this.genfaultnamefields[field];
			var pagefieldname = this.genfaultpagefields[field];
			this.Utils.ShowCell(pagefieldname, this.GenClientData[connectionname][fieldname]);
		}

		// Fill in the client parameters.
		var clientheadings = genericparameters_en[this.GenClientData[connectionname]["protocol"]];
		var clientparamstable = document.getElementById("genclientparamstable");
		var clientparams = this.GenClientData[connectionname]["clientparams"];
		this.Utils.TRowStart();
		for (var param in clientparams) {
			var trow = clientparamstable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();
		
			// Try to look up the parameter name.
			// Is the protocol present in our data file?
			if (clientheadings) {
				// Is the parameter name listed?
				if (param in clientheadings) {
					var paramname = clientheadings[param]; 
				// If not, then just use the parameter name.
				} else {
					var paramname = param; 
				}
			// If not, then just use the parameter name.
			} else {
					var paramname = param; 
			}

			this.Utils.InsertTableCell(trow, 0, paramname, "theadstyle");
			// Parameter value.
			this.Utils.InsertTableCell(trow, 1, clientparams[param], tdclass);
		}


		// Fill in the data table read addresses.
		var dtdata = this.GenClientData[connectionname]["readtable"];
		for (var field in this.gendtreadfields) {
			var fieldname = this.gendtreadfields[field];

			// The parameters are optional, so simply ignore any that are missing.
			try {
				var addrname = dtdata[fieldname][0];
				var addrlen = dtdata[fieldname][1];
			} catch (e) {
				var addrname = "";
				var addrlen = "";
			}

			var addrfieldname = this.dtreadaddr[field];
			var lenfieldname = this.gendtreadlength[field];

			this.Utils.ShowCell(addrfieldname, addrname);
			this.Utils.ShowCell(lenfieldname, addrlen);
		}

		// Fill in the data table write addresses.
		var dtdata = this.GenClientData[connectionname]["writetable"];
		for (var field in this.gendtwritefields) {
			var fieldname = this.gendtwritefields[field];

			// The parameters are optional, so simply ignore any that are missing.
			try {
				var addrname = dtdata[fieldname][0];
				var addrlen = dtdata[fieldname][1];
			} catch (e) {
				var addrname = "";
				var addrlen = "";
			}

			var addrfieldname = this.gendtwriteaddr[field];
			var lenfieldname = this.gendtwritelength[field];

			this.Utils.ShowCell(addrfieldname, addrname);
			this.Utils.ShowCell(lenfieldname, addrlen);
		}


		// Fill in the command list.
		var clientcommandstable = document.getElementById("genclientcommandstable");
		var clientcmds = this.GenClientData[connectionname]["cmdlist"];
		this.Utils.TRowStart();
		for (var cmd in clientcmds) {
			var trow = clientcommandstable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// Command name.
			this.Utils.InsertTableCell(trow, 0, clientcmds[cmd][0], tdclass);
			// Command parameters.
			this.Utils.InsertTableCell(trow, 1, clientcmds[cmd][1], tdclass);
		}
	}
	this.PopulateGenClientDetails = _PopulateGenClientDetails;



	// ##################################################################
	// Delete the command list table to prepare it for new data.
	function _DeleteGenCmdList() {
		var cmdtable = document.getElementById("genclientcommandstable");
		// Delete all the rows, but not the header.
		while (cmdtable.rows.length > 1) {
			cmdtable.deleteRow(-1);
		}
	}
	this.DeleteGenCmdList = _DeleteGenCmdList;

	// ##################################################################
	// Delete the client parameters table to prepare it for new data.
	function _DeleteGenClientParams() {
		var paramtable = document.getElementById("genclientparamstable");
		// Delete all the rows, but not the header.
		while (paramtable.rows.length > 1) {
			paramtable.deleteRow(-1);
		}
	}
	this.DeleteGenClientParams = _DeleteGenClientParams;



	// ##################################################################
	// Hide the client details display.
	function _HideGenClientDetails() {
		var clientshow = document.getElementById("genclientdetails");
		clientshow.setAttribute("class", "datahide");
	}
	this.HideGenClientDetails = _HideGenClientDetails;

	// ##################################################################
	// Show the client details display.
	function _ShowGenClientDetails() {
		var clientshow = document.getElementById("genclientdetails");
		clientshow.setAttribute("class", "datashow");
	}
	this.ShowGenClientDetails = _ShowGenClientDetails;



	// ##################################################################
	// Display the details for a selected client.
	function _ShowGenClient(connectionname) {
		// Delete the list of commands if any are already present.
		this.DeleteGenCmdList();

		// Delete the client parameters if any are already present.
		this.DeleteGenClientParams();

		// Populate the tables with fresh data.
		this.PopulateGenClientDetails(connectionname);

		// Display the client details if they are still hidden.
		this.ShowGenClientDetails();
	}
	this.ShowGenClient = _ShowGenClient;


	// ##################################################################
	// Editing functions.


	// ##################################################################
	// Determine if the page is in view or edit modes.
	// Returns true if in edit mode.
	function _EditMode() {
		return document.forms.editmode.mode[1].checked;
	}
	this.EditMode = _EditMode;


	// ##################################################################
	// Check if the connection name is OK.
	function _TCPConnectionNameOk() {
		var tagname = document.forms.tcpclientparams.tcpconnectionnameedit.value;
		return this.EditLib.TagNameOK(tagname);
	}
	this.TCPConnectionNameOk = _TCPConnectionNameOk;


	// ##################################################################
	// The connection name has changed.
	function _TCPConnectionNameChanged() {
		this.EditLib.ShowFieldStatusColour(this.TCPConnectionNameOk(), "tcpconnectionnameedit");
	}
	this.TCPConnectionNameChanged = _TCPConnectionNameChanged;



	// ##################################################################
	// Check if the IP address is OK. We don't check the format of the string 
	// for any specific pattern, as the user can enter any valid name or 
	// raw address.
	function _TCPIPAddressOk() {
		var ipaddr = document.forms.tcpclientparams.tcpipaddressedit.value;
		return this.EditLib.NameStringOK(ipaddr);
	}
	this.TCPIPAddressOk = _TCPIPAddressOk;

	// ##################################################################
	// The IP address has changed. We don't check the format of the string 
	// for any specific pattern, as the user can enter any valid name or 
	// raw address.
	function _TCPIPAddressChanged() {
		this.EditLib.ShowFieldStatusColour(this.TCPIPAddressOk(), "tcpipaddressedit");
	}
	this.TCPIPAddressChanged = _TCPIPAddressChanged;


	// ##################################################################
	// Check if the IP port is Ok. 
	function _TCPPortOk() {
		var port = document.forms.tcpclientparams.tcpportedit.value;
		return this.EditLib.PortOk(port);
	}
	this.TCPPortOk = _TCPPortOk;


	// ##################################################################
	// The IP port has changed. 
	function _TCPPortChanged() {
		this.EditLib.ShowFieldStatusColour(this.TCPPortOk(), "tcpportedit");
	}
	this.TCPPortChanged = _TCPPortChanged;


	// ##################################################################
	// Check if a fault address is OK. The field id must match the input
	// name as this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	to know what the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _TCPDTAddrOk(fieldid, internalhreg) {

		var memaddress = document.forms.tcpclientparams[fieldid].value;

		// Anything value other than a holding register name will receive
		// the default address range (0 to 65,535).
		if (internalhreg) {
			var addrtype = "holdingreg";
		} else {
			var addrtype = "other";
		}

		// Check if this is a valid data table address.
		return this.EditLib.CheckMemAddr(memaddress, addrtype);
	}
	this.TCPDTAddrOk = _TCPDTAddrOk;

	// ##################################################################
	// The fault address has changed. The field id must match the input
	// name as this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	both to know which input to update, and to know what 
	//		the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _TCPDTAddrChanged(fieldid, internalhreg) {
		this.EditLib.ShowFieldStatusColour(this.TCPDTAddrOk(fieldid, internalhreg), fieldid);
	}
	this.TCPDTAddrChanged = _TCPDTAddrChanged;



	// ##################################################################
	// Check if a polling time is Ok. The time is expected to be an integer 
	// value representing milli-seconds. The field id must match the input
	// name as this is used to look up the form value.
	// Parameters: fieldid (string) = The id of the edit field. This is 
	// used to tell which field has changed.
	function _PollingTimeOk(fieldid) {

		var number = document.forms.tcpclientparams[fieldid].value;

		// Check if this is a valid number.
		return this.EditLib.IntOk(number, 10, 65535);
	}
	this.PollingTimeOk = _PollingTimeOk;


	// ##################################################################
	// A polling time has changed. The time is expected to be an integer 
	// value representing milli-seconds. The field id must match the input
	// name as this is used to look up the form value.
	// Parameters: fieldid (string) = The id of the edit field. This is 
	// used to tell which field has changed.
	function _PollingTimeChanged(fieldid) {
		this.EditLib.ShowFieldStatusColour(this.PollingTimeOk(fieldid), fieldid);
	}
	this.PollingTimeChanged = _PollingTimeChanged;



	// ##################################################################
	// The function code has changed. We need to re-check other fields
	// which may be dependent on it.
	function _TCPEditFunctionChanged() {
		this.TCPLocalAddrChanged();
		this.TCPRemoteAddrOk();
		this.TCPQuantityChanged();
		var cmdname = document.forms.tcpclientparams.tcpcommands.value;
		// We can't save this if there isn't a command selected yet.
		if (cmdname in this.TCPCurrentCommandEdit) {
			this.TCPCurrentCommandEdit[cmdname]["function"] = document.forms.tcpclientparams.tcpfunctioncodeedit.value;
		}
	}
	this.TCPEditFunctionChanged = _TCPEditFunctionChanged;



	// ##################################################################
	// Check if the quantity is Ok. 
	function _TCPQuantityOk() {

		var qty = document.forms.tcpclientparams.tcpquantityedit.value;

		// The maximum address range depends on the function code.
		var functype = document.forms.tcpclientparams.tcpfunctioncodeedit.value;
		var limit = this.EditLib.GetModbusFuncLimit(functype);

		return this.EditLib.IntOk(qty, 1, limit);
	}
	this.TCPQuantityOk = _TCPQuantityOk;

	// ##################################################################
	// The quantity has changed. 
	function _TCPQuantityChanged() {
		var paramok = this.TCPQuantityOk();
		this.EditLib.ShowFieldStatusColour(paramok, "tcpquantityedit");
		if (paramok) {
			var cmdname = document.forms.tcpclientparams.tcpcommands.value;
			// We can't save this if there isn't a command selected yet.
			if (cmdname in this.TCPCurrentCommandEdit) {
				this.TCPCurrentCommandEdit[cmdname]["qty"] = document.forms.tcpclientparams.tcpquantityedit.value;
			}
		}
	}
	this.TCPQuantityChanged = _TCPQuantityChanged;



	// ##################################################################
	// Check if the TCP remote address is Ok.
	function _TCPRemoteAddrOk() {
		var memaddress = document.forms.tcpclientparams.tcpremoteaddredit.value;

		// The maximum address range depends on the function code.
		var functype = document.forms.tcpclientparams.tcpfunctioncodeedit.value;

		if (functype == "3" || functype == "6" || functype == "16") {
			var addrtype = "holdingreg";
		} else {
			var addrtype = "other";
		}

		// Check if this is a valid data table address.
		return this.EditLib.CheckMemAddr(memaddress, addrtype);
	}
	this.TCPRemoteAddrOk = _TCPRemoteAddrOk;

	// ##################################################################
	// The remote address has changed.
	function _TCPRemoteAddrChanged() {
		var paramok = this.TCPRemoteAddrOk();
		this.EditLib.ShowFieldStatusColour(paramok, "tcpremoteaddredit");
		if (paramok) {
			var cmdname = document.forms.tcpclientparams.tcpcommands.value;
			// We can't save this if there isn't a command selected yet.
			if (cmdname in this.TCPCurrentCommandEdit) {
				this.TCPCurrentCommandEdit[cmdname]["remoteaddr"] = document.forms.tcpclientparams.tcpremoteaddredit.value;
			}
		}
	}
	this.TCPRemoteAddrChanged = _TCPRemoteAddrChanged;




	// ##################################################################
	// Check if the TCP local address is Ok.
	function _TCPLocalAddrOk() {

		var memaddress = document.forms.tcpclientparams.tcplocaladdredit.value;

		// The maximum address range depends on the function code.
		var functype = document.forms.tcpclientparams.tcpfunctioncodeedit.value;

		if (functype == "3" || functype == "6" || functype == "16") {
			var addrtype = "holdingreg";
		} else {
			var addrtype = "other";
		}

		// Check if this is a valid data table address.
		return this.EditLib.CheckMemAddr(memaddress, addrtype);
	}
	this.TCPLocalAddrOk = _TCPLocalAddrOk;

	// ##################################################################
	// The tag memory address has changed.
	function _TCPLocalAddrChanged() {
		var paramok = this.TCPLocalAddrOk();
		this.EditLib.ShowFieldStatusColour(paramok, "tcplocaladdredit");
		if (paramok) {
			var cmdname = document.forms.tcpclientparams.tcpcommands.value;
			// We can't save this if there isn't a command selected yet.
			if (cmdname in this.TCPCurrentCommandEdit) {
				this.TCPCurrentCommandEdit[cmdname]["memaddr"] = document.forms.tcpclientparams.tcplocaladdredit.value;
			}
		}
	}
	this.TCPLocalAddrChanged = _TCPLocalAddrChanged;



	// ##################################################################
	// Check if the unit ID is Ok. 
	function _TCPUIDOk() {

		var number = document.forms.tcpclientparams.tcpunitidedit.value;

		// Check if this is a valid number.
		return this.EditLib.IntOk(number, 0, 255);
	}
	this.TCPUIDOk = _TCPUIDOk;

	// ##################################################################
	// The unit ID has changed. 
	function _TCPUIDChanged() {
		var paramok = this.TCPUIDOk();
		this.EditLib.ShowFieldStatusColour(paramok, "tcpunitidedit");
		if (paramok) {
			var cmdname = document.forms.tcpclientparams.tcpcommands.value;
			// We can't save this if there isn't a command selected yet.
			if (cmdname in this.TCPCurrentCommandEdit) {
				this.TCPCurrentCommandEdit[cmdname]["uid"] = document.forms.tcpclientparams.tcpunitidedit.value;
			}
		}
	}
	this.TCPUIDChanged = _TCPUIDChanged;


	// ##################################################################
	// The command has changed. 
	function _TCPCmdChanged() {

		// Get the name of the command.
		var cmd = document.forms.tcpclientparams.tcpcommands.value;

		// Update the form.
		this.InitTCPClientCmdEdit(cmd);
	}
	this.TCPCmdChanged = _TCPCmdChanged;



	// ##################################################################
	// Check if a command name is Ok.
	function _TCPCmdAddedOk() {
		var tagname = document.forms.tcpclientparams.tcpaddcmdedit.value;
		return this.EditLib.TagNameOK(tagname);
	}
	this.TCPCmdAddedOk = _TCPCmdAddedOk;

	// ##################################################################
	// The new command name has changed. This is for adding new command names.
	function _TCPCmdAddedChanged() {
		this.EditLib.ShowFieldStatusColour(this.TCPCmdAddedOk(), "tcpaddcmdedit");
	}
	this.TCPCmdAddedChanged = _TCPCmdAddedChanged;



	// ##################################################################
	// Add a new TCP client command. 
	function _TCPClientCmdAdd() {
		this.Utils.ShowPageArea("tcpeditconnections");
		this.Utils.HidePageArea("tcpeditpolling");
	
		var newcmdname = document.forms.tcpclientparams.tcpaddcmdedit.value;
		this.TCPCmdAddedChanged();
		if (!this.EditLib.TagNameOK(newcmdname)) {
			return;
		}

		// Add the new command to the list.
		this.TCPCurrentCommandEdit[newcmdname] = {"remoteaddr" : 0,
						"memaddr" : 0,
						"qty" : 1,
						"uid" : 1,
						"function" : 1};

		// Populate the command list.
		this.PopulateTCPCmdList();
				
		// Edit the new command.
		this.InitTCPClientCmdEdit(newcmdname)

	}
	this.TCPClientCmdAdd = _TCPClientCmdAdd;


	// ##################################################################
	// Delete the current TCP client command. 
	function _TCPClientCmdDelete() {

		// Get the name of the current command.
		var cmd = document.forms.tcpclientparams.tcpcommands.value;
		// Delete that command.
		delete this.TCPCurrentCommandEdit[cmd];

		// Update the form.
		this.PopulateTCPCmdList();
		var cmd = document.forms.tcpclientparams.tcpcommands.value;
		this.InitTCPClientCmdEdit(cmd);

	}
	this.TCPClientCmdDelete = _TCPClientCmdDelete;



	// ##################################################################
	// This relates the incoming data to the editing fields.
	this.TCPClientEditFields = {"connectionname": "tcpconnectionnameedit", 
		"host": "tcpipaddressedit", 
		"port": "tcpportedit", 

		"fault_coil": "tcpfaultcoil", 
		"fault_holdingreg": "tcpfaulthreg", 
		"fault_reset": "tcpfaultrstcoil", 
		"fault_inpreg": "tcpfaultireg", 
		"fault_inp": "tcpfaultdi", 

		"retrytime": "tcpretrytimeedit",
		"repeattime": "tcprepeattimeedit", 
		"cmdtime": "tcpcmdtimeedit"
		};


	// The commands belonging to the current TCP client.
	this.TCPCurrentCommandEdit = {};


	// ##################################################################
	// Initialise the TCP client editing form with new command data. This
	// can change while running when the user selects a different command 
	// to edit.
	function _InitTCPClientCmdEdit(cmd) {

		// Check to see if any commands are defined. If not, set some
		// default data.
		if (cmd == "") {
			record = {"remoteaddr" : "0", "memaddr" : "0", "qty" : "1", 
							"uid" : "1", "function" : "1"};
		} else {
			var record = this.TCPCurrentCommandEdit[cmd];
		}
		

		document.forms.tcpclientparams.tcpremoteaddredit.value = record["remoteaddr"];
		document.forms.tcpclientparams.tcplocaladdredit.value = record["memaddr"];
		document.forms.tcpclientparams.tcpquantityedit.value = record["qty"];
		document.forms.tcpclientparams.tcpunitidedit.value = record["uid"];


		// Set the function code. This takes a bit of extra work 
		// because we have have to set the correct text and value based
		// on what is stored in the web page.
		// To make the page accept the new option all the time, we need to
		// erase all the selection options and then recreate them. If we don't
		// do that, then the list will not reset correctly if we make a change.
		var funccode = record["function"];
		var funcselect = document.getElementById("tcpfunctioncodeedit");

		// Get a copy of the complete selection options. We also save 
		// an extra copy of the requested option.
		var selects = [];
		var newfunc = "";
		var newtext = "";
		for (var i=0; i<funcselect.length; i++) {
			selects.push([funcselect.options[i].value, funcselect.options[i].text]);
			if (funcselect.options[i].value == funccode) {
				var newfunc = funcselect.options[i].value;
				var newtext = funcselect.options[i].text;
			}
		}
		// Now, delete all the options.
		if (funcselect.hasChildNodes()) {
			while (funcselect.firstChild) {
				funcselect.removeChild(funcselect.firstChild);
			}
		} 
		// Now re-populate the selection with the original data. 
		for (var i=0; i < selects.length; i++) {
			var selectrecord = selects[i];
			var newoption = document.createElement("option");
			newoption.value = selectrecord[0];
			newoption.text = selectrecord[1];
			funcselect.appendChild(newoption);
		}

		// Set the default record to the desired value.
		funcselect.options[0].value = newfunc;
		funcselect.options[0].text = newtext;
		

	}
	this.InitTCPClientCmdEdit = _InitTCPClientCmdEdit;


	// ##################################################################
	// Populate the TCP command list with command names.
	function _PopulateTCPCmdList() {

		// Populate the command list.
		// First remove any existing commands.
		var tcpcommands = document.getElementById("tcpcommands");
		// If there are any existing elements, remove them first.
		if (tcpcommands.hasChildNodes()) {
			while (tcpcommands.firstChild) {
				tcpcommands.removeChild(tcpcommands.firstChild);
			}
		} 

		// Make a list of command names in an array.
		var cmdlist = [];
		for (var i in this.TCPCurrentCommandEdit) {
			cmdlist.push(i);
		}
		// Sort the list of names.
		cmdlist.sort();

		// Now populate the selection with new data. 
		for (var i=0; i < cmdlist.length; i++) {
			var cmdrecord = cmdlist[i];
			var newoption = document.createElement("option");
			newoption.value = cmdrecord;
			newoption.text = cmdrecord;
			tcpcommands.appendChild(newoption);
		}
	
	}
	this.PopulateTCPCmdList = _PopulateTCPCmdList;

	// ##################################################################
	// Initialise the TCP client editing form with data.
	// Parameters connection (string) = The name of the connection being edited.
	function _InitTCPClientEdit(connection) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["tcpconnectionnameedit", "tcpipaddressedit", "tcpportedit",
			"tcpcmdtimeedit", "tcprepeattimeedit", "tcpretrytimeedit", "tcpfaultdi",
			"tcpfaultcoil", "tcpfaultireg", "tcpfaulthreg", "tcpfaultrstcoil", 
			"tcpremoteaddredit", "tcpquantityedit", "tcplocaladdredit", "tcpunitidedit"];

		this.EditLib.ResetFieldColours(editfields);

		// Clear the option radio buttion select titles of any left over warning colours.
		var tcpoptiontitles = ["tcpcommandsoption", "tcpfaultsoption", "tcppollingoption", "tcpconnectionsoption"];
		for (var i in tcpoptiontitles) {
				this.EditLib.ShowOptionStatusColour(true, tcpoptiontitles[i]);
		}
		
		// If the connection name is an empty string, use default data,
		// else retrieve the existing data.
		var editdata = {};
		if (connection.length != 0) {
			var tcpclientdata = this.TCPClientData[connection];
			for (var field in this.TCPClientEditFields) {
				editdata[field] = tcpclientdata[field];
			}
		} else {
			var tcpclientdata = {"cmdlist" : []};
			for (var field in this.TCPClientEditFields) {
				editdata[field] = "";
			}
		}

		// Populate the edit form with data.
		var editform = document.forms.tcpclientparams;
		for (var field in this.TCPClientEditFields) {
			editform[this.TCPClientEditFields[field]].value = editdata[field];
		}


		// Save the current command list in a format we can handle by 
		// command name.
		this.TCPCurrentCommandEdit = {};
		var cmdlist = tcpclientdata["cmdlist"];
		for (var i=0; i < cmdlist.length; i++) {
			var cmdrecord = cmdlist[i];
			var command = cmdrecord["command"];

			this.TCPCurrentCommandEdit[command] = {};
			this.TCPCurrentCommandEdit[command] = {"function" : cmdrecord["function"], 
					"uid": cmdrecord["uid"], 
					"memaddr": cmdrecord["memaddr"], 
					"qty": cmdrecord["qty"], 
					"remoteaddr": cmdrecord["remoteaddr"]};

		}

		// Initialise the command form with the first record. If there
		// are no existing commands, initialise with defaults.
		if (cmdlist.length > 0) {
			var firstrec = cmdlist[0];
			this.InitTCPClientCmdEdit(firstrec["command"]);
		} else {
			this.InitTCPClientCmdEdit("");
		}

		// Populate the command list.
		this.PopulateTCPCmdList();

	}
	this.InitTCPClientEdit = _InitTCPClientEdit;


	// ##################################################################
	// Delete a TCP client record.
	function _TCPClientEditDelete() {
		// The client name.
		var client = document.forms.tcpclientparams.tcpconnectionnameedit.value;

		// If the client exists, delete the record.
		if (client in this.TCPClientData) {
			delete this.TCPClientData[client];
			this.UpdateTCPClients();
		}
	}
	this.TCPClientEditDelete = _TCPClientEditDelete;

	// ##################################################################
	// Validate the TCP client edit data for the connection parameters.
	// Returns true if all OK.
	function _TCPClientConnectionOptionsCheck() {

		// First, check the parameters. This updates the user feedback
		// on the page.
		this.TCPConnectionNameChanged();
		this.TCPIPAddressChanged();
		this.TCPPortChanged();

		// Now check if all the parameters are Ok.
		if (!this.TCPConnectionNameOk() || !this.TCPIPAddressOk() || !this.TCPPortOk()) {
			this.EditLib.ShowOptionStatusColour(false, "tcpconnectionsoption");
			return false;
		}

		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "tcpconnectionsoption");
		return true;
	}
	this.TCPClientConnectionOptionsCheck = _TCPClientConnectionOptionsCheck;


	// ##################################################################
	// Validate the TCP client edit data for the polling parameters.
	// Returns true if all OK.
	function _TCPClientPollingOptionsCheck() {

		// We need the field id to differentiate between timers.
		var pollfields = ["tcpcmdtimeedit", "tcprepeattimeedit", "tcpretrytimeedit"];
		for (var i in pollfields) {
			this.PollingTimeChanged(pollfields[i]);
			if (!this.PollingTimeOk(pollfields[i])) {
				this.EditLib.ShowOptionStatusColour(false, "tcppollingoption");
				return false; 
			}
		}
		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "tcppollingoption");
		return true;
	}
	this.TCPClientPollingOptionsCheck = _TCPClientPollingOptionsCheck;



	// ##################################################################
	// Validate the TCP client edit data for the fault parameters.
	// Returns true if all OK.
	function _TCPClientFaultOptionsCheck() {

		// Faults.
		var dtfields = ["tcpfaultcoil", "tcpfaultdi", "tcpfaultireg", "tcpfaultrstcoil"];
		for (var i in dtfields) {
			this.TCPDTAddrChanged(dtfields[i], false);
			if (!this.TCPDTAddrOk(dtfields[i], false)) {
				this.EditLib.ShowOptionStatusColour(false, "tcpfaultsoption");
				return false; 
			}
		}

		// This one needs a different second parameter.
		this.TCPDTAddrChanged("tcpfaulthreg", true);
		if (!this.TCPDTAddrOk("tcpfaulthreg", true)) {
			this.EditLib.ShowOptionStatusColour(false, "tcpfaultsoption");
			return false; 
		}

		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "tcpfaultsoption");
		return true;
	}
	this.TCPClientFaultOptionsCheck = _TCPClientFaultOptionsCheck;


	// ##################################################################
	// Validate the TCP client edit data for the command parameters.
	// Returns true if all OK.
	function _TCPClientCommandOptionsCheck() {

		// Now check if all the parameters are Ok.
		var paramerr =  (!this.TCPQuantityOk() || !this.TCPRemoteAddrOk() ||
						!this.TCPLocalAddrOk() || !this.TCPUIDOk());

		this.TCPEditFunctionChanged();
		this.TCPQuantityChanged();
		this.TCPLocalAddrChanged();
		this.TCPUIDChanged();
		this.TCPCmdChanged();
		this.TCPCmdAddedChanged();


		if (paramerr) {
			this.EditLib.ShowOptionStatusColour(false, "tcpcommandsoption");
			return false;
		} else {
			// Mark this field as OK.
			this.EditLib.ShowOptionStatusColour(true, "tcpcommandsoption");
			return true;
		}
	}
	this.TCPClientCommandOptionsCheck = _TCPClientCommandOptionsCheck;


	// ##################################################################
	function _TCPClientEditEnter() {
		// First, check the parameters. This updates the user feedback
		// on the page.

		if (!this.TCPClientConnectionOptionsCheck()) { return false; }
		if (!this.TCPClientPollingOptionsCheck()) { return false; }
		if (!this.TCPClientFaultOptionsCheck()) { return false; }
		if (!this.TCPClientCommandOptionsCheck()) { return false; }



		// Save the data (in browser memory).
		// The client name.
		var clientname = document.forms.tcpclientparams.tcpconnectionnameedit.value;
		if (!(clientname in this.TCPClientData)) {
			this.TCPClientData[clientname] = {};
		}
		// Handle the simple cases.
		var client = this.TCPClientData[clientname];
		var paramform = document.forms.tcpclientparams;
		for (var param in this.TCPClientEditFields) {
			client[param] = paramform[this.TCPClientEditFields[param]].value;
		}

		// Handle commands. Extract the commands from the edit dictionary
		// (object) and form them into a list (array). 
		cmdlist = [];
		for (var cmd in this.TCPCurrentCommandEdit) {
			var cmdrecord = this.TCPCurrentCommandEdit[cmd];
			cmdlist.push({"command" : cmd,
					"function" : cmdrecord["function"], 
					"uid": cmdrecord["uid"], 
					"memaddr": cmdrecord["memaddr"], 
					"qty": cmdrecord["qty"], 
					"remoteaddr": cmdrecord["remoteaddr"]});
		}
		// Add it to the parameter set for that connection.
		this.TCPClientData[clientname]["cmdlist"] = cmdlist;

		// These are fixed, as they are not editable at this time.
		this.TCPClientData[clientname]["protocol"] = "modbustcp"
		this.TCPClientData[clientname]["action"] = "poll"


		// Update the display.
		this.UpdateTCPClients();

		// Signal success.
		return true;

	}
	this.TCPClientEditEnter = _TCPClientEditEnter;



	// ##################################################################


	// ##################################################################
	// The connection name is Ok.
	function _GenConnectionNameOk() {
		var tagname = document.forms.genclientparams.genconnectionnameedit.value;
		return this.EditLib.TagNameOK(tagname);
	}
	this.GenConnectionNameOk = _GenConnectionNameOk;


	// ##################################################################
	// The connection name has changed.
	function _GenConnectionNameChanged() {
		this.EditLib.ShowFieldStatusColour(this.GenConnectionNameOk(), "genconnectionnameedit");
	}
	this.GenConnectionNameChanged = _GenConnectionNameChanged;


	// ##################################################################
	// The protocol name is Ok.
	function _GenProtocolOk() {
		var protocol = document.forms.genclientparams.genprotocoledit.value;
		return this.EditLib.TagNameOK(protocol);
	}
	this.GenProtocolOk = _GenProtocolOk;

	// ##################################################################
	// The protocol name has changed.
	function _GenProtocolChanged() {
		this.EditLib.ShowFieldStatusColour(this.GenProtocolOk(), "genprotocoledit");
	}
	this.GenProtocolChanged = _GenProtocolChanged;


	// ##################################################################
	// The program file name is Ok.
	function _GenClientFileOk() {
		var clientfile = document.forms.genclientparams.genclientfileedit.value;
		return this.EditLib.NameStringOK(clientfile);
	}
	this.GenClientFileOk = _GenClientFileOk;

	// ##################################################################
	// The program file name has changed.
	function _GenClientFileChanged() {
		this.EditLib.ShowFieldStatusColour(this.GenClientFileOk(), "genclientfileedit");
	}
	this.GenClientFileChanged = _GenClientFileChanged;





	// ##################################################################
	// A generic client data table address is Ok. The field id must 
	// match the input name as this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	to know what the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _GenDTAddrOk(fieldid, internalhreg) {

		var memaddress = document.forms.genclientparams[fieldid].value;


		// An empty field is OK provided the length parameter is also empty.
		if (memaddress.length == 0) {
			// Get the contents of the length field.
			var memlength = document.forms.genclientparams[this.GenDTFieldSizes[fieldid][0]].value;
			return memlength.length == 0;
		}

		// Anything value other than a holding register name will receive
		// the default address range (0 to 65,535).
		if (internalhreg) {
			var addrtype = "holdingreg";
		} else {
			var addrtype = "other";
		}

		// Check if this is a valid data table address.
		return this.EditLib.CheckMemAddr(memaddress, addrtype);
	}
	this.GenDTAddrOk = _GenDTAddrOk;


	// ##################################################################
	// A generic client data table address has changed. The field id must 
	// match the input name as this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	both to know which input to update, and to know what 
	//		the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _GenDTAddrChanged(fieldid, internalhreg) {
		this.EditLib.ShowFieldStatusColour(this.GenDTAddrOk(fieldid, internalhreg), fieldid);
	}
	this.GenDTAddrChanged = _GenDTAddrChanged;




	// ##################################################################
	// A generic client fault address is Ok. The field id must 
	// match the input name as this is used to look up the form value.
	// This is different from data table addresses, in that fault addresses
	// are mandatory and do not have an associated length.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	to know what the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _GenFaultAddrOk(fieldid, internalhreg) {

		var memaddress = document.forms.genclientparams[fieldid].value;

		// Anything value other than a holding register name will receive
		// the default address range (0 to 65,535).
		if (internalhreg) {
			var addrtype = "holdingreg";
		} else {
			var addrtype = "other";
		}

		// Check if this is a valid data table address.
		return this.EditLib.CheckMemAddr(memaddress, addrtype);
	}
	this.GenFaultAddrOk = _GenFaultAddrOk;


	// ##################################################################
	// A generic client fault address has changed. The field id must 
	// match the input name as this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	both to know which input to update, and to know what 
	//		the correct address range is. 
	//	internalhreg (boolean) = If true, this is an internal holding
	//		register. Otherwise, it is any other address. This is 
	//		used to determine what maximum address range to permit.
	function _GenFaultAddrChanged(fieldid, internalhreg) {
		this.EditLib.ShowFieldStatusColour(this.GenFaultAddrOk(fieldid, internalhreg), fieldid);
	}
	this.GenFaultAddrChanged = _GenFaultAddrChanged;




	// This associates the data table length field ID with the corresponding
	// memory type and also which table address it is associated with.
	this.GenDTFieldSizes = {
		"gendtreadcoillenedit" : ["gendtreadcoiledit", "coil"],
		"gendtreaddilenedit" : ["gendtreaddiedit", "discrete"],
		"gendtreadhreglenedit" : ["gendtreadhregedit", "holdingreg"],
		"gendtreadireglenedit" : ["gendtreadiregedit", "inputreg"],
		"gendtwritecoillenedit" : ["gendtwritecoiledit", "coil"],
		"gendtwritedilenedit" : ["gendtwritediedit", "discrete"],
		"gendtwritehreglenedit" : ["gendtwritehregedit", "holdingreg"],
		"gendtwriteireglenedit" : ["gendtwriteiregedit", "inputreg"],

		"gendtreadcoiledit" : ["gendtreadcoillenedit", "coil"],
		"gendtreaddiedit" : ["gendtreaddilenedit", "discrete"],
		"gendtreadhregedit" : ["gendtreadhreglenedit", "holdingreg"],
		"gendtreadiregedit" : ["gendtreadireglenedit", "inputreg"],
		"gendtwritecoiledit" : ["gendtwritecoillenedit", "coil"],
		"gendtwritediedit" : ["gendtwritedilenedit", "discrete"],
		"gendtwritehregedit" : ["gendtwritehreglenedit", "holdingreg"],
		"gendtwriteiregedit" : ["gendtwriteireglenedit", "inputreg"]
		}
	

	// ##################################################################
	// A generic client data table length is Ok. The length is the
	// number of data table addresses to read or write between the server
	// and the generic client. The field id must  match the input name as 
	// this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	to know what the correct address range is. 
	function _GenDTLenOk(fieldid) {

		// Get the value the user entered.
		var dtlength = document.forms.genclientparams[fieldid].value;
		// Look up the associated length parameters.
		var lenparams = this.GenDTFieldSizes[fieldid];
		// Get the address from the address field. We need this so we know if
		// the address plus length is outside the data table.
		var dtaddr = document.forms.genclientparams[lenparams[0]].value;

		// If both the length and the address fields are empty, this is OK.
		if ((dtlength.length == 0) && (dtaddr.length == 0)) {
			return true;
		}

		// Check the parameters. We have to do a special check here because
		// our library routine doesn't accept a pair of integers.
		// First, do a basic check to makes sure they are integers.
		if (!this.EditLib.CheckInteger(dtlength)) { return false; }
		if (!this.EditLib.CheckInteger(dtaddr)) { return false; }

		// Convert them to integers
		var dtlengthval = parseInt(dtlength, 10);
		if (isNaN(dtlengthval)) { return false; }
		var dtaddrval = parseInt(dtaddr, 10);
		if (isNaN(dtaddrval)) { return false; }

		// Add them together and see if they are in range.
		var dttotal = dtlengthval + dtaddrval
		return this.EditLib.CheckMemAddr(dttotal, lenparams[1]);

	}
	this.GenDTLenOk = _GenDTLenOk;


	// ##################################################################
	// A generic client data table length has changed. The length is the
	// number of data table addresses to read or write between the server
	// and the generic client. The field id must  match the input name as 
	// this is used to look up the form value.
	// Parameters: 
	//	fieldid (string) = The ID of the edit field. This is used
	//	 	both to know which input to update, and to know what 
	//		the correct address range is. 
	function _GenDTLenChanged(fieldid) {
		this.EditLib.ShowFieldStatusColour(this.GenDTLenOk(fieldid), fieldid);
	}
	this.GenDTLenChanged = _GenDTLenChanged;



	// ##################################################################
	// This relates the incoming data to the editing fields.
	this.GenClientEditFields = {"connectionname": "genconnectionnameedit", 
				"clientfile": "genclientfileedit", 
				"protocol": "genprotocoledit", 
				"fault_coil": "genfaultcoil", 
				"fault_inpreg": "genfaultireg", 
				"fault_holdingreg": "genfaulthreg", 
				"fault_inp": "genfaultdi",
				"fault_reset": "genfaultrstcoil"
			};

	this.GenDTReadEditFields = {"coil" : ["gendtreadcoiledit", "gendtreadcoillenedit"],
				"inp" : ["gendtreaddiedit", "gendtreaddilenedit"],
				"holdingreg" : ["gendtreadhregedit", "gendtreadhreglenedit"],
				"inpreg" : ["gendtreadiregedit", "gendtreadireglenedit"]
			};

	this.GenDTWriteEditFields = {"coil" : ["gendtwritecoiledit", "gendtwritecoillenedit"],
				"inp" : ["gendtwritediedit", "gendtwritedilenedit"],
				"holdingreg" : ["gendtwritehregedit", "gendtwritehreglenedit"],
				"inpreg" : ["gendtwriteiregedit", "gendtwriteireglenedit"]
			};


	// ##################################################################
	// Initialise the generic client editing form with data.
	// Parameters connection (string) = The name of the connection being edited.
	function _InitGenClientEdit(connection) {

		// Reset the field properties. This prevents previous errors
		// from affecting new edits.
		var editfields = ["genconnectionnameedit", "genprotocoledit", "genclientfileedit", 
			"genfaultcoil", "genfaultdi", "genfaulthreg", "genfaultireg", "genfaultrstcoil"];

		// We handle these separatel because we also want to clear these fields of data.
		var gendtfields = ["gendtreadcoiledit", "gendtreadcoillenedit", "gendtreaddiedit", 
			"gendtreaddilenedit", "gendtreadhregedit", "gendtreadhreglenedit", 
			"gendtreadiregedit", "gendtreadireglenedit", "gendtwritecoiledit", 
			"gendtwritecoillenedit", "gendtwritediedit", "gendtwritedilenedit", 
			"gendtwritehregedit", "gendtwritehreglenedit", "gendtwriteiregedit", 
			"gendtwriteireglenedit" ];

		this.EditLib.ResetFieldColours(editfields);
		this.EditLib.ResetFieldColours(gendtfields);

		// Clear the data table fields of old data. We need to handle these specially
		// as the field name may not be present in the original data (and so could
		// get skipped during an update.
		for (var i in gendtfields) {
			var field = gendtfields[i];
			document.forms.genclientparams[field].value = "";
		}

		// Clear the option radio buttion select titles of any left over warning colours.
		var genoptiontitles = ["gendtreadoption", "gendtwriteoption", "genclientstartoption", "genfaultsoption"];
		for (var i in genoptiontitles) {
				this.EditLib.ShowOptionStatusColour(true, genoptiontitles[i]);
		}


		// If the connection name is an empty string, use default data,
		// else retrieve the existing data.
		var editdata = {};
		var readtable = {};
		var writetable = {};
		var clientparams = {};
		var cmdlist = [];
		if (connection.length != 0) {
			var genclientdata = this.GenClientData[connection];
			for (var field in this.GenClientEditFields) {
				editdata[field] = genclientdata[field];
			}

			// Restart characteristics.
			editdata["restartonfail"] = genclientdata["restartonfail"];

			// Data table read.
			var rdtable = genclientdata["readtable"];
			for (var field in rdtable) {
				readtable[field] = [rdtable[field][0], rdtable[field][1]];
			}

			// Data table write.
			var wrtable = genclientdata["writetable"];
			for (var field in wrtable) {
				writetable[field] = [wrtable[field][0], wrtable[field][1]];
			}

			// Client params.
			var clientparams = genclientdata["clientparams"];
			// Client commands.
			var cmdlist = genclientdata["cmdlist"];

		} else {
			var genclientdata = {"cmdlist" : [], "clientparams" : {}, 
						"readtable" : {}, "writetable" : {}};
			for (var field in this.GenClientEditFields) {
				editdata[field] = "";
			}
			// Restart characteristics.
			editdata["restartonfail"] = "nostart";
		}

		// Populate the edit form with data.
		var editform = document.forms.genclientparams;

		// Basic parameters.
		for (var field in this.GenClientEditFields) {
			editform[this.GenClientEditFields[field]].value = editdata[field];
		}

		// Restart characteristics.
		switch(editdata["restartonfail"]) {
			case "yes" : {editform.restart[0].checked = true; break; }
			case "no" : {editform.restart[1].checked = true; break; }
			case "nostart" : {editform.restart[2].checked = true; break; }
		}

		// Populate the data table read fields.
		for (var field in genclientdata["readtable"]) {
			editform[this.GenDTReadEditFields[field][0]].value = rdtable[field][0];
			editform[this.GenDTReadEditFields[field][1]].value = rdtable[field][1];
		}

		// Populate the data table write fields.
		for (var field in genclientdata["writetable"]) {
			editform[this.GenDTWriteEditFields[field][0]].value = writetable[field][0];
			editform[this.GenDTWriteEditFields[field][1]].value = writetable[field][1];
		}

		// Populate the client parameters field.
		var cparams = [];
		for (var param in clientparams) {
			cparams.push(param + "=" + clientparams[param]);
		}
		editform.geneditclientparams.value = cparams.join("\n");

		// Populate the command list field.
		var cmdparams = [];
		for (var cmdindex in cmdlist) {
			var cmd = cmdlist[cmdindex];
			cmdparams.push(cmd[0] + "=" + cmd[1]);
		}
		editform.geneditcommandlist.value = cmdparams.join("\n");


	}
	this.InitGenClientEdit = _InitGenClientEdit;


	// ##################################################################
	// Delete a generic client record.
	function _GenClientEditDelete() {
		// The client name.
		var client = document.forms.genclientparams.genconnectionnameedit.value;

		// If the client exists, delete the record.
		if (client in this.GenClientData) {
			delete this.GenClientData[client];
			this.UpdateGenClients();
		}
	}
	this.GenClientEditDelete = _GenClientEditDelete;


	// ##################################################################
	// Validate the generic client edit data for the start parameters.
	// Returns true if all OK.
	function _GenClientStartOptionsCheck() {
		// First, check the parameters.
		this.GenConnectionNameChanged();
		this.GenProtocolChanged();
		this.GenClientFileChanged();

		if (!this.GenConnectionNameOk() || !this.GenProtocolOk() || !this.GenClientFileOk()) {
			this.EditLib.ShowOptionStatusColour(false, "genclientstartoption");
			return false;
		} else {
			// Mark this field as OK.
			this.EditLib.ShowOptionStatusColour(true, "genclientstartoption");
		}

		return true;
	}
	this.GenClientStartOptionsCheck = _GenClientStartOptionsCheck;


	// ##################################################################
	// Validate the generic client edit data for the data table read 
	// parameters. Returns true if all OK.
	function _GenClientDTReadOptionsCheck() {

		// Data table read addresses. This contains the field name,
		// data length field, and if the field is a holding register (which has
		// a larger address range).
		var gendtfields = [
		["gendtreadcoiledit", "gendtreadcoillenedit", false],
		["gendtreaddiedit", "gendtreaddilenedit", false],
		["gendtreadiregedit", "gendtreadireglenedit", false],
		["gendtreadhregedit", "gendtreadhreglenedit", true]
		];

		// Check the fields.
		for (var i in gendtfields) {
			var dtid = gendtfields[i][0];
			var dtlenid = gendtfields[i][1];
			var dtishreg = gendtfields[i][2];

			// Data table addresses.
			this.GenDTAddrChanged(dtid, dtishreg);
			if (!this.GenDTAddrOk(dtid, dtishreg)) {
				this.EditLib.ShowOptionStatusColour(false, "gendtreadoption");
				return false; 
			}

			// Data table lengths.
			this.GenDTLenChanged(dtlenid);
			if (!this.GenDTLenOk(dtlenid)) {
				this.EditLib.ShowOptionStatusColour(false, "gendtreadoption");
				return false; 
			}
		}
		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "gendtreadoption");

		return true;
	}
	this.GenClientDTReadOptionsCheck = _GenClientDTReadOptionsCheck;


	// ##################################################################
	// Validate the generic client edit data for the data table write
	// parameters. Returns true if all OK.
	function _GenClientDTWriteOptionsCheck() {

		// Data table write addresses. This contains the field name,
		// data length field, and if the field is a holding register (which has
		// a larger address range).
		var gendtfields = [
		["gendtwritecoiledit", "gendtwritecoillenedit", false],
		["gendtwritediedit", "gendtwritedilenedit",false],
		["gendtwriteiregedit","gendtwriteireglenedit", false],
		["gendtwritehregedit", "gendtwritehreglenedit", true]
		];

		// Check the fields.
		for (var i in gendtfields) {
			var dtid = gendtfields[i][0];
			var dtlenid = gendtfields[i][1];
			var dtishreg = gendtfields[i][2];

			// Data table addresses.
			this.GenDTAddrChanged(dtid, dtishreg);
			if (!this.GenDTAddrOk(dtid, dtishreg)) {
				this.EditLib.ShowOptionStatusColour(false, "gendtwriteoption");
				return false; 
			}

			// Data table lengths.
			this.GenDTLenChanged(dtlenid);
			if (!this.GenDTLenOk(dtlenid)) {
				this.EditLib.ShowOptionStatusColour(false, "gendtwriteoption");
				return false; 
			}
		}
		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "gendtwriteoption");

		return true;
	}
	this.GenClientDTWriteOptionsCheck = _GenClientDTWriteOptionsCheck;


	// ##################################################################
	// Validate the generic client edit data for the fault address
	// parameters. Returns true if all OK.
	function _GenClientFaultOptionsCheck() {

		// Fault addresses.
		var genfaultfields = ["genfaultcoil", "genfaultdi", "genfaulthreg", "genfaultireg", "genfaultrstcoil"];
		for (var i in genfaultfields) {
			this.GenFaultAddrChanged(genfaultfields[i]);
			if (!this.GenFaultAddrOk(genfaultfields[i])) {
				this.EditLib.ShowOptionStatusColour(false, "genfaultsoption");
				return false; 
			} 
		}
		// Mark this field as OK.
		this.EditLib.ShowOptionStatusColour(true, "genfaultsoption");

		return true;
	}
	this.GenClientFaultOptionsCheck = _GenClientFaultOptionsCheck;



	// ##################################################################
	// Validate the generic client edit data and exit the edit form if OK. 
	function _GenClientEditEnter() {

		// Check the start parameters.
		if (!this.GenClientStartOptionsCheck()) {return false;}

		// Check the data table read parameters.
		if (!this.GenClientDTReadOptionsCheck()) {return false;}

		// Check the data table write parameters.
		if (!this.GenClientDTWriteOptionsCheck()) {return false;}

		// Check the fault address parameters.
		if (!this.GenClientFaultOptionsCheck()) {return false;}


		// Save the data (in browser memory).
		// The client name.
		var clientname = document.forms.genclientparams.genconnectionnameedit.value;
		if (!(clientname in this.GenClientData)) {
			this.GenClientData[clientname] = {};
		}

		// A shortcut to the parameter form.
		var paramform = document.forms.genclientparams;
		var client = this.GenClientData[clientname];

		// Handle the simple cases.
		for (var param in this.GenClientEditFields) {
			client[param] = paramform[this.GenClientEditFields[param]].value;
		}

		// Restart characteristics.
		var restart = "";
		if (paramform.restart[0].checked) {
			var restart = "yes";
		}
		if (paramform.restart[1].checked) {
			var restart = "no";
		}
		if (paramform.restart[2].checked) {
			var restart = "nostart";
		}
		if (restart != "") {
			client["restartonfail"] = restart;
		} else {
			return false;
		}

		// Data table read addresses.
		// First, remove any existing data, and create the key if it doesn't exist.
		client["readtable"] = {};
		var readtable = client["readtable"];
		for (var param in this.GenDTReadEditFields) {
			var paramlist = [];
			var field = this.GenDTReadEditFields[param][0];
			var flength = this.GenDTReadEditFields[param][1];
			var fieldparam = paramform[field].value;
			var lenparam = paramform[flength].value;
			// Don't save empty fields.
			if ((fieldparam.length > 0) && (lenparam.length > 0)) {
				paramlist.push(fieldparam);
				paramlist.push(lenparam);
				readtable[param] = paramlist;
			}
		}


		// Data table write addresses.
		// First, remove any existing data, and create the key if it doesn't exist.
		client["writetable"] = {};
		var writetable = client["writetable"];
		for (var param in this.GenDTWriteEditFields) {
			var paramlist = [];
			var field = this.GenDTWriteEditFields[param][0];
			var flength = this.GenDTWriteEditFields[param][1];
			var fieldparam = paramform[field].value;
			var lenparam = paramform[flength].value;
			// Don't save empty fields.
			if ((fieldparam.length > 0) && (lenparam.length > 0)) {
				paramlist.push(fieldparam);
				paramlist.push(lenparam);
				writetable[param] = paramlist;
			}
		}


		// Client parameters.
		// Split the block of text into lines. 
		var clientparams = paramform.geneditclientparams.value;
		var cparamslist = clientparams.split("\n");
		// Split each line, and add to a dictionary (object).
		var cparms = {};
		for (var i in cparamslist) {
			// Ignore blank lines.
			if (cparamslist[i].trim().length > 0) {
				// Split the line at the '=' sign.
				var parampair = cparamslist[i].split("=");
				// If we don't have exactly two parameters, something is wrong.
				if (parampair.length == 2) {
					cparms[parampair[0]] = parampair[1];
				} else {
					return false;
				}
			}
		}
		// Save the client parameters.
		client["clientparams"] = cparms;


		// Command list.
		// Split the block of text into lines. 
		var commandparams = paramform.geneditcommandlist.value;
		var commandparamslist = commandparams.split("\n");
		// Split each line, and add to a list (array).
		var cmdparms = [];
		for (var i in commandparamslist) {
			// Ignore blank lines.
			if (commandparamslist[i].trim().length > 0) {
				// Find the command delimiter - "="
				var cmdstr = commandparamslist[i];
				var delim = cmdstr.search(/=/);
				// Check if we found the delimiter at all.
				if (delim > 0) {
					// Now, split the string at the delimiter and
					// save the pair in an array.
					cmdparms.push([cmdstr.slice(0, delim), cmdstr.slice(delim + 1)]);
				} else {
					return false;
				}
			}
		}

		// Save the command list.
		client["cmdlist"] = cmdparms;
		

		// This is fixed, as it is not editable at this time.
		client["action"] = "poll"


		// Update the display.
		this.UpdateGenClients();

		// Signal success.
		return true;


	}
	this.GenClientEditEnter = _GenClientEditEnter;



	// ##################################################################
	// Return the current data in a format suitable for sending to the
	// server for saving the results.
	function _FormatSaveRequest() {

		// TCP client data.
		tcpclient = [];
		for (var client in this.TCPClientData) {
			var record = this.TCPClientData[client];
			record["connectionname"] = client;
			tcpclient.push(record);
		}

		// Generic client data.
		genclient = [];
		for (var client in this.GenClientData) {	
			var record = this.GenClientData[client];
			record["connectionname"] = client;
			genclient.push(record);
		}

		// Client configuration data.
		var datareq = {"tcpclientinfo" : tcpclient, "genclientinfo" : genclient};


		return datareq;
	}
	this.FormatSaveRequest = _FormatSaveRequest;



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



}

// ##################################################################


