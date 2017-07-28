/** ##########################################################################
# Project: 	MBLogic
# Module: 	ladsubreditlib.js
# Purpose: 	MBLogic ladder editor library.
# Language:	javascript
# Date:		24-Apr-2010.
# Ver:		24-Apr-2010
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

/* Control the editing features for the overall subroutine.
*/

function SubrEditLib(docref, rungdata) {


	// Reference to editable this.docref.
	this.docref = docref;
	// Rung data.
	this.RungData = rungdata;


	// ==================================================================

	// ##################################################################
	/* Enable editing of subroutine comments.
	*/
	function _SubrCommentEdit() {
		// Prime the display with the existing data.

		this.docref.forms.subrcommentedit.subrcommenttext.value = this.RungData["subrcomments"];
		
		// Show the edit field.
		var editshow = this.docref.getElementById("subrcommentedit");
		editshow.setAttribute("class", "rungshow");
	}
	this.SubrCommentEdit = _SubrCommentEdit;


	// ##################################################################
	/* Save the new subroutine comments.
	*/
	function _SubrCommentEnter() {
		// Get and save the new comment data.

		var commenttext = this.docref.forms.subrcommentedit.subrcommenttext.value;

		// Erase any existing comments.
		var commentdisplay = this.docref.getElementById("subrcomments");
		if (commentdisplay.hasChildNodes()) {
			while (commentdisplay.firstChild) {
				commentdisplay.removeChild(commentdisplay.firstChild);
			}
		} 

		// Add the new comments.
		var commentvalue = this.docref.createTextNode(commenttext);
		commentdisplay.appendChild(commentvalue);

		// Hide the edit field.
		var editshow = this.docref.getElementById("subrcommentedit");
		editshow.setAttribute("class", "runghide");

		return commenttext;

	}
	this.SubrCommentEnter = _SubrCommentEnter;


}

