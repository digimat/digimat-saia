/** ##########################################################################
# Project: 	MBLogic
# Module: 	libdatamonitor.js
# Purpose: 	MBLogic data monitoring library.
# Language:	javascript
# Date:		25-Aug-2010
# Ver:		25-Aug-2010
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


// ############################################################################
/* This controls the program monitoring page.
	Parameters: utillib (object) = The utility display library.
*/
function SubrListDisplay(utillib) {

	// Utility library
	this.Utils = utillib;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		var subrtable = document.getElementById("subrtable");
		// First, delete the table (but not the header) if it already exists.
		while (subrtable.rows.length > 1) {
			subrtable.deleteRow(-1);
		}

		this.Utils.TRowStart();
		for (subr in pageresults) {
			var trow = subrtable.insertRow(-1);
			var subrname = pageresults[subr]

			// This is used to provide alternating row colours.
			var tdclass = this.Utils.TRowAlternate();

			// First cell is the subroutine name.
			this.Utils.InsertTableText(trow, 0, subrname, tdclass);

			// Second cell is a link to viewing the subroutine in ladder.
			this.Utils.InsertTableLink(trow, 1, "laddermonitor.xhtml?subrname=" + subrname, "Monitor Ladder", tdclass);

			// Third cell is a link to viewing the subroutine in IL.
			this.Utils.InsertTableLink(trow, 2, "ildisplay.html?subrname=" + subrname, "View IL", tdclass);
		}
	}
	this.UpdatePageResults = _UpdatePageResults;

}
// ############################################################################


