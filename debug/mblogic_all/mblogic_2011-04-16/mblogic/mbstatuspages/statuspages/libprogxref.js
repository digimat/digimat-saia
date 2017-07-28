/** ##########################################################################
# Project: 	MBLogic
# Module: 	libprogxref.js
# Purpose: 	MBLogic program control library.
# Language:	javascript
# Date:		02-Jun-2010
# Ver:		04-Sep-2010
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
/* This displays the address cross reference.
	Parameters:
		utillib (object) = The utility display library.
*/
function AddrXref(utillib) {

	// Utility library
	this.Utils = utillib;

	this._PLCAddrXref = {};
	this._AddrSummary = [];
	// The current address xref filter character.
	this.AddrFilter = "";
	// The address xref formed into a table (2D array).
	this.AddrMatrix = [];

	// This is used to test for numeric characters.
	this.Numbers = {"0" : 0, "1" : 1, "2" : 2, "3" : 3, "4" : 4, 
			"5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9};



	// ##################################################################
	// Split an address string into text and numeric halves.
	// Return the halves in an array.
	function _AddrDecorator(addr) {
		// Check to see if it is a mixed string in the format like "DS100".
		var re = /^\D+\d+$/;
		if (re.test(addr)) {
			var prefix = [];
			for (var i in addr) {
				var testchar = addr[i];
				if (testchar in this.Numbers) {
					return [prefix.join(""), addr.slice(i)];
				} else {
					prefix.push(testchar);
				}
			}
			return [prefix.join(""), addr.slice(i)];
		}
		// Check to see if it is entirely a number.
		var re = /^\d+$/;
		if (re.test(addr)) {
			return ["", addr];
		}
		// Assume it is a string of some undefined format.
		return [addr, 0];
	}
	this.AddrDecorator = _AddrDecorator;



	// ##################################################################
	// Convert the address xref data into a 2D array so we can manipulate it 
	// more easily. This also creates a pair of split address fields so we
	// can sort addresse in the format "DS1234" more nicely.
	function _MakeAddrMatrix() {
		this.AddrMatrix = [];


		// Now, go through the sorted list of addresses and add them to the table.
		for (var addr in this._PLCAddrXref) {
			// Split the address into halves.
			var deco = this.AddrDecorator(addr);
			// Get all the subroutines for that address.
			for (var subr in this._PLCAddrXref[addr]) {
				this.AddrMatrix.push([addr, subr, this._PLCAddrXref[addr][subr], deco[0], deco[1]]);
			}
		}
	}
	this.MakeAddrMatrix = _MakeAddrMatrix;



	// ##################################################################
	// Sort the address xref details by address. 
	function _SortAddr() {
		this.AddrMatrix.sort(function(a, b) {
				if (a[3] < b[3]) { return -1; }
				if (a[3] > b[3]) { return 1; }
				if ((a[4] == "") || (b[4] == "")) { return 0; }
				return a[4] - b[4];
			});
	}
	this.SortAddr = _SortAddr;


	// ##################################################################
	// Sort the address xref details by subroutine name. Return a sorted list
	// of addresses to display.
	function _SortSubr() {
		this.AddrMatrix.sort(function(a, b) {
				if (a[1] < b[1]) { return -1; }
				if (a[1] > b[1]) { return 1; }
				return 0;
			});
	}
	this.SortSubr = _SortSubr;

	// ##################################################################
	// Sort the address xref details by a selected field. 
	function _SortAddrTable(field) {
		if (field == "subr") {
			this.SortSubr();
		} else {
			this.SortAddr();
		}
		this.DeleteAddrXRefTable();
		this.PopulateAddrXRefTable();
	}
	this.SortAddrTable = _SortAddrTable;


	// ##################################################################
	// Populate the address xref details table based on a list of addresses.
	function _PopulateAddrXRefTable() {
		// Get the address xref table in the web page.
		var xreftable = document.getElementById("addrxreftable");

		// Now, go through the sorted list of addresses and add them to the table.
		this.Utils.TRowStart();

		for (var index in this.AddrMatrix) {
			var record = this.AddrMatrix[index];
			if (record[0][0] == this.AddrFilter[0]) {
				var trow = xreftable.insertRow(-1);
				// This is used to provide alternating row colours.
				var tdclass = this.Utils.TRowAlternate();

				// First cell is the address name.
				this.Utils.InsertTableText(trow, 0, record[0], tdclass);
				// Second cell is the subroutine name.
				this.Utils.InsertTableText(trow, 1, record[1], tdclass);
				// Third cell is the list of rungs.
				this.Utils.InsertTableText(trow, 2, record[2], tdclass);	
			}
		}
	}
	this.PopulateAddrXRefTable = _PopulateAddrXRefTable;


	// ##################################################################
	// Delete the address cross reference table to prepare it for new data.
	function _DeleteAddrXRefTable() {
		var xreftable = document.getElementById("addrxreftable");
		// Delete all the rows, but not the header.
		while (xreftable.rows.length > 1) {
			xreftable.deleteRow(-1);
		}
	}
	this.DeleteAddrXRefTable = _DeleteAddrXRefTable;




	// ##################################################################
	// Summarise the address xref data into a list categorised by first character.
	function _MakeAddrXRefSummary() {

		// Create a sorted list of addresses.
		summary = [];
		for (var addr in this._PLCAddrXref) {
			summary.push(addr);
		}
		summary.sort();

		// Get the first character of each element.
		var lastchar = "";
		this._AddrSummary = [];
		for (var fcharindex in summary) {
			if (summary[fcharindex][0] != lastchar) {
				this._AddrSummary.push(summary[fcharindex][0]);
				var lastchar = summary[fcharindex][0];
			}
		}
	}
	this.MakeAddrXRefSummary = _MakeAddrXRefSummary;



	// ##################################################################
	// Populate the list with the summary of address xref names.
	function _PopulateAddrXrefList() {
		// Now, display them on the page.
		var addrxreflist = document.getElementById("addrxref");
		for (var addr in this._AddrSummary) {

			var addrtext = this._AddrSummary[addr];
			var addrlink = document.createElement("li");
			var viewbutton = document.createElement("button");
			viewbutton.setAttribute("width", "20");
			viewbutton.setAttribute("onclick", "AXRef.ShowAddrXref('" + addrtext + "');");
			var viewbuttonname = document.createTextNode(addrtext);
			viewbutton.appendChild(viewbuttonname);
			addrlink.appendChild(viewbutton);
			addrxreflist.appendChild(addrlink);
		}
	}
	this.PopulateAddrXrefList = _PopulateAddrXrefList;


	// ##################################################################
	// Show the selected address cross reference.
	function _ShowAddrXref(addrname) {
		this.DeleteAddrXRefTable();

		// Save the filter character.
		this.AddrFilter = addrname;
		this.SortAddr();
		this.PopulateAddrXRefTable();

		var xrefdetails = document.getElementById("addrxrefdetails");
		xrefdetails.setAttribute("class", "datashow");	
	}
	this.ShowAddrXref = _ShowAddrXref;

	// ##################################################################
	// Hide the address xref details.
	function _HideAddrDetails() {
		var xrefdetails = document.getElementById("addrxrefdetails");
		xrefdetails.setAttribute("class", "datahide");
	}
	this.HideAddrDetails = _HideAddrDetails;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {
		this._PLCAddrXref = pageresults;
		this.MakeAddrMatrix();
		this.MakeAddrXRefSummary();
		this.PopulateAddrXrefList();
	}
	this.UpdatePageResults = _UpdatePageResults;

}

// ############################################################################

// ##################################################################
/* This displays the instruction cross reference.
	Parameters:
		utillib (object) = The utility display library.
*/
function InstrXref(utillib) {

	// Utility library
	this.Utils = utillib;

	this._PLCInstrXref = {};

	// ##################################################################
	// Populate the instruction xref details table.
	function _PopulateInstrXRefTable(instrname) {
		var xreftable = document.getElementById("instrxreftable");

		// Sort the list of subroutine names.
		var subrnames = [];
		for (var subr in this._PLCInstrXref[instrname]) {
			subrnames.push(subr);
		}
		subrnames.sort();

		this.Utils.TRowStart();
		//for (var subr in this._PLCInstrXref[instrname]) {
		for (var subrindex in subrnames) {
			var subr = subrnames[subrindex];
			var trow = xreftable.insertRow(-1);

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// First cell is the subroutine name.
			this.Utils.InsertTableText(trow, 0, subr, tdclass);
			// Second cell is the list of rungs.
			this.Utils.InsertTableText(trow, 1, this._PLCInstrXref[instrname][subr], tdclass);

		}
	}
	this.PopulateInstrXRefTable = _PopulateInstrXRefTable;

	// ##################################################################
	// Delete the instruction cross reference table to prepare it for new data.
	function _DeleteInstrXRefTable() {
		var xreftable = document.getElementById("instrxreftable");
		// Delete all the rows, but not the header.
		while (xreftable.rows.length > 1) {
			xreftable.deleteRow(-1);
		}
	}
	this.DeleteInstrXRefTable = _DeleteInstrXRefTable;


	// ##################################################################
	// Show the selected instruction cross reference.
	function _ShowInstrXref(instrname) {
		this.DeleteInstrXRefTable();
		this.PopulateInstrXRefTable(instrname);
		var xrefdetails = document.getElementById("instrxrefdetails");
		xrefdetails.setAttribute("class", "datashow");

		// Delete the old heading.
		var ixrefheading = document.getElementById("ixrefheading");

		// If there are any existing elements, remove them first.
		if (ixrefheading.hasChildNodes()) {
			while (ixrefheading.firstChild) {
				ixrefheading.removeChild(ixrefheading.firstChild);
			}
		} 
		// Add the new heading text.
		ixrefheading.appendChild(document.createTextNode(instrname));

	}
	this.ShowInstrXref = _ShowInstrXref;

	// ##################################################################
	// Hide the instruction xref details.
	function _HideInstrDetails() {
		var xrefdetails = document.getElementById("instrxrefdetails");
		xrefdetails.setAttribute("class", "datahide");
	}
	this.HideInstrDetails = _HideInstrDetails;



	// ##################################################################
	// Populate the list with the summary of instruction xref names.
	function _PopulateInstrXrefList() {
		var xrefnames = [];
		// Get all the instruction xref names so we can sort them.
		for (var addr in this._PLCInstrXref) {
			xrefnames.push(addr);
		}
		// Sort the list of names.
		xrefnames.sort();

		// Now, display them on the page.
		var instrxreflist = document.getElementById("instrxref");
		for (var instr in xrefnames) {

			var instrtext = xrefnames[instr];
			var instrlink = document.createElement("li");
			var viewbutton = document.createElement("button");
			viewbutton.setAttribute("width", "20");
			viewbutton.setAttribute("onclick", "IXRef.ShowInstrXref('" + instrtext + "');");
			var viewbuttonname = document.createTextNode(instrtext);
			viewbutton.appendChild(viewbuttonname);
			instrlink.appendChild(viewbutton);
			instrxreflist.appendChild(instrlink);

		}
	}
	this.PopulateInstrXrefList = _PopulateInstrXrefList;



	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {
		this._PLCInstrXref = pageresults;
		this.PopulateInstrXrefList();
	}
	this.UpdatePageResults = _UpdatePageResults;

}

// ############################################################################

