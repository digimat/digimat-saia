/** ##########################################################################
# Project: 	MBLogic
# Module: 	libparamedit.js
# Purpose: 	MBLogic parameter editing library.
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
/* These are functions which are used to edit parameters. These
   are general purpose functions rather than specific to a particular
   page.
*/

// ##################################################################
function LibParamEdit() {



	// ##################################################################
	// This provides a list of offsets used for selection drop-downs on web pages.
	// Address types list must match that used in the web page.
	this.AddressTypes = {"coil" : 0,
				"discrete" : 1,
				"holdingreg" : 2,
				"inputreg" : 3,
				"holdingreg32" : 4,
				"inputreg32" : 5,
				"holdingregfloat" : 6,
				"inputregfloat" : 7,
				"holdingregdouble" : 8,
				"inputregdouble" : 9,
				"holdingregstr8" : 10,
				"inputregstr8" : 11,
				"holdingregstr16" : 12,
				"inputregstr16" : 13
			};

	// Classify addresses by type.
	this.AddressClasses = {"coil" : "boolean",
			"discrete" : "boolean",
			"holdingreg" : "int",
			"inputreg" :  "int",
			"holdingreg32" : "int",
			"inputreg32" :  "int",
			"holdingregfloat" : "float",
			"inputregfloat" : "float",
			"holdingregdouble" : "float",
			"inputregdouble" : "float",
			"holdingregstr8" : "string",
			"inputregstr8" : "string",
			"holdingregstr16" : "string",
			"inputregstr16" : "string"
			};

	// The protocol quantity maximum limits for each Modbus function code.
	this.FuncCodeLimits = {"1" : 2000, "2" : 2000, "3" : 125, "4" : 125, 
				"5" : 1, "6" : 1, "15" : 1968, "16" : 123}


	// ##################################################################
	// Return the drop down list index of an address type.
	function _GetAddrTypeIndex(addrtype) {
		return this.AddressTypes[addrtype];
	}
	this.GetAddrTypeIndex = _GetAddrTypeIndex;


	// ##################################################################
	// Return the data category (boolean, int, float, string) of the address type.
	function _GetAddrCategory(addrtype) {
		return this.AddressClasses[addrtype];
	}
	this.GetAddrCategory = _GetAddrCategory;

	// ##################################################################
	// Return the maximum protocol quantity limit for a specified Modbus 
	// function code.
	function _GetModbusFuncLimit(funccode) {
		return this.FuncCodeLimits[funccode];
	}
	this.GetModbusFuncLimit = _GetModbusFuncLimit;



	// ##################################################################
	// Return true if the address type is for a string.
	function _AddrTypeIsStr(addrtype) {
		return (this.AddressClasses[addrtype] == "string");
	}
	this.AddrTypeIsStr = _AddrTypeIsStr;


	// ##################################################################
	// Reset the field properties. This prevents previous errors
	// from affecting new edits.
	function _ResetFieldColours(editfields) {
		for (var fieldindex in editfields) {
			var field = document.getElementById(editfields[fieldindex]);
			field.setAttribute("class", "editconfigfields");
		}
	}
	this.ResetFieldColours = _ResetFieldColours;


	// ##################################################################
	// Set the colour of the form input field to reflect whether the data is OK.
	function _ShowFieldStatusColour(ok, fieldid) {
		var field = document.getElementById(fieldid);
		if (ok) {
			field.setAttribute("class", "editconfigfields");
		} else {
			field.setAttribute("class", "editconfigerrors");
		}
	}
	this.ShowFieldStatusColour = _ShowFieldStatusColour;


	// ##################################################################
	// Set the colour of the form option field to reflect whether the group of 
	// data is OK. This is used for the "radio button" selectors which are
	// used to select what group of data to edit. This allows setting the text
	// colour to show if any of the fields (which may be hidden) are not Ok.
	function _ShowOptionStatusColour(ok, fieldid) {
		var field = document.getElementById(fieldid);
		if (ok) {
			field.setAttribute("class", "editconfigoptionok");
		} else {
			field.setAttribute("class", "editconfigoptionerrors");
		}
	}
	this.ShowOptionStatusColour = _ShowOptionStatusColour;


	// ##################################################################
	// Return true if the value is a number.
	// Parameters: param (string) = The param value as a string.
	// Returns: true if the value is OK.
	//
	function _CheckNumber(param) {
		// Check if it is all digits. These can be positive, negative,
		// integer, or floating point.
		return /^[-+]?[0-9]+$|^[-+]?[0-9]+[.]?[0-9]+$/.test(param);
	}
	this.CheckNumber = _CheckNumber;


	// ##################################################################
	// Return true if the value is a positive integer.
	// Parameters: param (string) = The param value as a string.
	// Returns: true if the value is OK.
	//
	function _CheckInteger(param) {
		// Check if it is all digits. This must be a positive integer.
		return /^[0-9]+$/.test(param);
	}
	this.CheckInteger = _CheckInteger;



	// ##################################################################
	// Return true if the number is a valid integer within the specified range.
	// Parameters number (string) = The value to verify. 
	//	min, max (integer) = The minimum and maximum values to compare to.
	function _IntOk(number, min, max) {

		if (!/^[0-9]+$/.test(number)) { return false; }
		
		// Convert to base 10 integer.
		var numval = parseInt(number, 10);
		if (isNaN(numval)) { return false; }

		// Check if in valid range.
		if ((numval < min) || (numval > max)) { return false; }

		return true;
	}
	this.IntOk = _IntOk;


	// ##################################################################
	// Return true if the number is a valid float within the specified range.
	// Parameters number (string) = The value to verify. 
	//	min, max (float) = The minimum and maximum values to compare to.
	function _FloatOk(number, min, max) {

		if (!/^[0-9]+\.[0-9]+$/.test(number)) { return false; }
		
		// Convert to float.
		var numval = parseFloat(number);
		if (isNaN(numval)) { return false; }

		// Check if in valid range.
		if ((numval < min) || (numval > max)) { return false; }

		return true;
	}
	this.FloatOk = _FloatOk;



	// ##################################################################
	// Return true if the number is a valid integer *or* float within the 
	// specified range.
	// Parameters number (string) = The value to verify. 
	//	min, max (float) = The minimum and maximum values to compare to.
	function _NumberOk(number, min, max) {

		return (this.IntOk(number, min, max) || this.FloatOk(number, min, max));
	}
	this.NumberOk = _NumberOk;


	// ##################################################################
	// Return true if the number is a valid *negative* integer or float.
	// Parameters number (string) = The value to verify. 
	function _IsNegativeNumber(number) {
		//if (!/^-[0-9]\.*[0-9]*+$/.test(number)) { return false; }
		if (!/^-[0-9]\.*[0-9]*$/.test(number)) { return false; }

		// Convert to float.
		var numval = parseFloat(number);
		if (isNaN(numval)) { return false; }

		return numval < 0.0;

	}
	this.IsNegativeNumber = _IsNegativeNumber;



	// ##################################################################
	// Return true if the port number is OK.
	// Parameters port (string) = The port to verify. 
	function _PortOk(port) {

		if (!/^[0-9]+$/.test(port)) { return false; }
		
		// Convert to base 10 integer.
		var portval = parseInt(port, 10);
		if (isNaN(portval)) { return false; }

		// Check if in valid range.
		if ((portval < 0) || (portval > 65535)) { return false; }

		return true;
	}
	this.PortOk = _PortOk;


	// ##################################################################
	// Return true if the address tag memory address is ok.
	// Parameters: memaddress (string) = The memory address as a string.
	// 	addrtype (string) = The address type. This is required because the
	//	number of valid addresses is not the same for all address types.
	// Returns: true if the address is OK.
	//
	function _CheckMemAddr(memaddress, addrtype) {

		// Check if it is all integer digits.
		if (this.IntOk(memaddress)) {
			// Try to convert the number to an integer.
			var addrval = parseInt(memaddress, 10);

			// Make additional checks.
			if (isNaN(addrval)) {return false;}

			if (addrval < 0) {return false;}

			switch (addrtype) {
			case "holdingreg" : {var maxaddr = 1048575; break; }
			case "holdingreg32" : {var maxaddr = 1048574; break; }
			case "holdingregfloat" : {var maxaddr = 1048574; break; }
			case "holdingregdouble" : {var maxaddr = 1048572; break; }
			case "holdingregstr8" : {var maxaddr = 1048575; break; }
			case "holdingregstr16" : {var maxaddr = 1048575; break; }
			default : {var maxaddr = 65535; break; }
			}

			if (addrval > maxaddr) {return false;}

			// We have passed all the checks.
			return true;

		} else {
			return false;
		}
	}
	this.CheckMemAddr = _CheckMemAddr;


	// ##################################################################
	function _TagNameOK(tagname) {
		return /^[0-9a-zA-Z]+$/.test(tagname);
	}
	this.TagNameOK = _TagNameOK;


	// ##################################################################
	function _NameStringOK(namestring) {
		return /^[0-9a-zA-Z \-\.]+$/.test(namestring);
	}
	this.NameStringOK = _NameStringOK;

}

// ##################################################################


