/** ##########################################################################
# Project: 	MBLogic
# Module: 	libstatusdatatable.js
# Purpose: 	MBLogic program control library.
# Language:	javascript
# Date:		02-Jun-2010
# Ver:		21-Jun-2010
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
/* Monitor data for the soft logic data table.
*/
function SLDataMonitor() {


	// Names of input fields.
	this.InpNames = ["addr00", "addr01", "addr02", "addr03", "addr04", 
			"addr05", "addr06", "addr07", "addr08", "addr09", 
			"addr10", "addr11", "addr12", "addr13", "addr14", 
			"addr15", "addr16", "addr17", "addr18", "addr19"];

	// Names of output fields
	this.DispNames = ["plcdata00", "plcdata01", "plcdata02", "plcdata03", "plcdata04", 
			"plcdata05", "plcdata06", "plcdata07", "plcdata08", "plcdata09", 
			"plcdata10", "plcdata11", "plcdata12", "plcdata13", "plcdata14", 
			"plcdata15", "plcdata16", "plcdata17", "plcdata18", "plcdata19"];


	// ##################################################################
	// Disable the input boxes.
	function _DisableInputs() {
		for (var index in this.InpNames) {

			var inpname = this.InpNames[index];
			var inpbox = document.forms.softlogicdatatable[inpname];
			inpbox.disabled = "disabled";
		}
	}
	this.DisableInputs = _DisableInputs;


	// ##################################################################
	// Enable the input boxes.
	function _EnableInputs() {
		for (var index in this.InpNames) {

			var inpname = this.InpNames[index];
			var inpbox = document.forms.softlogicdatatable[inpname];
			inpbox.disabled = null;
		}
	}
	this.EnableInputs = _EnableInputs;

	// ##################################################################
	// Erase the text at a specified ID.
	function _EraseText(id) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 
	}
	this.EraseText = _EraseText;

	// ##################################################################
	// Replace the text at a given ID with new text.
	function _DisplayText(id, text) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 

		// Add the new cell text.
		cellref.appendChild(document.createTextNode(text));
	}
	this.DisplayText = _DisplayText;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {
		// Make a list of the data keys (addresses).
		addrlist = [];
		for (var addr in pageresults) {
			addrlist.push(addr);
		}
		// Sort the list of addresses.
		addrlist.sort();

		// If the list is too long, discard the excess values.
		if (addrlist.length > this.InpNames.length) {
			addrlist.length = this.InpNames.length;
		}


		// Now display the addresses and data.
		for (var index in addrlist) {
			// Replace the form input contents with the address. 
			var inpname = this.InpNames[index];
			var inpbox = document.forms.softlogicdatatable[inpname];
			inpbox.value = addrlist[index];
			// Show the associated data.
			this.DisplayText(this.DispNames[index], pageresults[addrlist[index]]);
		}

		// Erase any values which we may not be using.
		for (var index = addrlist.length; index < this.InpNames.length; index++) {
			var inpname = this.InpNames[index];
			var inpbox = document.forms.softlogicdatatable[inpname];
			inpbox.value = "";
			this.EraseText(this.DispNames[index]);
		}


	}
	this.UpdatePageResults = _UpdatePageResults;



	// ##################################################################
	// Get all the addresses from the form and return them as a comma
	// separated string.
	function _GetAddresses() {
		// Go through each input box and get the contents.
		addrlist = [];
		for (var index in this.InpNames) {
			// Replace the form input contents with the address. 
			var inpname = this.InpNames[index];
			var inpbox = document.forms.softlogicdatatable[inpname];
			// Don't save empty strings.
			if (inpbox.value.length > 0) {
				addrlist.push(inpbox.value);
			}
		}

		// Turn this into a comma separated string.
		return addrlist.join(",");
	}
	this.GetAddresses = _GetAddresses;


	// ##################################################################
	// Update the screen once.
	function _Update() {
		// Read the addresses from the form.
		this.GetAddresses();
	}
	this.Update = _Update;


// ##################################################################
}



// ##################################################################
/* Monitor data for the system (Modbus) data table.
*/

function SysDataMonitor() {

	// Names of address type selectors.
	this.TypeNames = ["addrtype00", "addrtype01", "addrtype02", "addrtype03", "addrtype04", 
			"addrtype05", "addrtype06", "addrtype07", "addrtype08", "addrtype09", 
			"addrtype10", "addrtype11", "addrtype12", "addrtype13", "addrtype14", 
			"addrtype15", "addrtype16", "addrtype17", "addrtype18", "addrtype19"];

	// Names of input fields.
	this.InpNames = ["addr00", "addr01", "addr02", "addr03", "addr04", 
			"addr05", "addr06", "addr07", "addr08", "addr09", 
			"addr10", "addr11", "addr12", "addr13", "addr14", 
			"addr15", "addr16", "addr17", "addr18", "addr19"];

	// Names of output fields
	this.DispNames = ["plcdata00", "plcdata01", "plcdata02", "plcdata03", "plcdata04", 
			"plcdata05", "plcdata06", "plcdata07", "plcdata08", "plcdata09", 
			"plcdata10", "plcdata11", "plcdata12", "plcdata13", "plcdata14", 
			"plcdata15", "plcdata16", "plcdata17", "plcdata18", "plcdata19"];

	// Convert the form address type labels to the format used by the server.
	this.TypeConvertToServer = {"Coil" : "coil", "Discrete Input" : "inp",
				"Holding Register" : "hreg", "Input Register" : "inpreg" }
	
	// Convert the address type labels from the format used by the server to that used by the web page.
	this.TypeConvertFromServer = {"coil" : "Coil", "inp" : "Discrete Input",
				"hreg" : "Holding Register", "inpreg" : "Input Register" }

	// ##################################################################
	// Disable the input boxes.
	function _DisableInputs() {
		for (var index in this.InpNames) {

			var inpname = this.InpNames[index];
			var inpbox = document.forms.systemdatatable[inpname];
			inpbox.disabled = "disabled";

			var typename = this.TypeNames[index];
			var addrtype = document.forms.systemdatatable[typename];
			addrtype.disabled = "disabled";
		}
	}
	this.DisableInputs = _DisableInputs;


	// ##################################################################
	// Enable the input boxes.
	function _EnableInputs() {
		for (var index in this.InpNames) {

			var inpname = this.InpNames[index];
			var inpbox = document.forms.systemdatatable[inpname];
			inpbox.disabled = null;

			var typename = this.TypeNames[index];
			var addrtype = document.forms.systemdatatable[typename];
			addrtype.disabled = null;
		}
	}
	this.EnableInputs = _EnableInputs;

	// ##################################################################
	// Erase the text at a specified ID.
	function _EraseText(id) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 
	}
	this.EraseText = _EraseText;

	// ##################################################################
	// Replace the text at a given ID with new text.
	function _DisplayText(id, text) {
		var cellref = document.getElementById(id);

		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 

		// Add the new cell text.
		cellref.appendChild(document.createTextNode(text));
	}
	this.DisplayText = _DisplayText;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		addrlist = pageresults

		// If the list is too long, discard the excess values.
		if (addrlist.length > this.InpNames.length) {
			addrlist.length = this.InpNames.length;
		}


		// Now display the addresses and data.
		for (var index in addrlist) {
			// Replace the form input contents with the address. 
			var inpname = this.InpNames[index];
			var inpbox = document.forms.systemdatatable[inpname];
			var typename = this.TypeNames[index];
			var typeselect = document.forms.systemdatatable[typename];

			var addrtypecode = this.TypeConvertFromServer[addrlist[index][0]];

			typename.value = addrtypecode;
			inpbox.value = addrlist[index][1];

			// Show the associated data.
			this.DisplayText(this.DispNames[index], addrlist[index][2]);
		}

		// Erase any values which we may not be using.
		for (var index = addrlist.length; index < this.InpNames.length; index++) {
			var inpname = this.InpNames[index];
			var inpbox = document.forms.systemdatatable[inpname];
			inpbox.value = "";

			var typename = this.TypeNames[index];
			var typeselect = document.forms.systemdatatable[typename];
			typeselect.value = "None";

			this.EraseText(this.DispNames[index]);
		}


	}
	this.UpdatePageResults = _UpdatePageResults;



	// ##################################################################
	// Get all the addresses from the form and return them as a comma
	// separated string.
	function _GetAddresses() {
		// Go through each input box and get the contents.
		addrlist = [];
		for (var index in this.InpNames) {
			// Replace the form input contents with the address. 
			var inpname = this.InpNames[index];
			var inpbox = document.forms.systemdatatable[inpname];
			var typename = this.TypeNames[index];
			var addrtype = document.forms.systemdatatable[typename];
			var addrcode = this.TypeConvertToServer[addrtype.value];

			// Don't save empty strings.
			if ((inpbox.value.length > 0) && (addrcode != null)) {
				addrlist.push(addrcode + ":" + inpbox.value);
			}
		}

		// Turn this into a comma separated string.
		return addrlist.join(",");
	}
	this.GetAddresses = _GetAddresses;


	// ##################################################################
	// Update the screen once.
	function _Update() {
		// Read the addresses from the form.
		this.GetAddresses();
	}
	this.Update = _Update;


// ##################################################################
}



