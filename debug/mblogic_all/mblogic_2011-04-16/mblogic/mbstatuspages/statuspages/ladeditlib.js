/** ##########################################################################
# Project: 	MBLogic
# Module: 	ladeditlib.js
# Purpose: 	MBLogic ladder editor library.
# Language:	javascript
# Date:		1-Feb-2010.
# Ver:		29-Apr-2010
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

/* Ladder Editor for MBLogic. This library acts to edit instructions within
a rung of ladder. It assumes the rung has already been created.

It must be initialised with two parameters. These are:

	docref = A reference to the document.
	rungdata = An object containing the edit matrix data structure the 
		editor operates on.

*/

	// ##################################################################

function LadderEditor(docref, ladsymbols, rungnumber, matrixdata) {

	// Reference to editable document.
	this.docref = docref;

	// Ladder symbols definition.
	this.LadSymbols = ladsymbols.LadSymbols;

	// The current rung number.
	this.RungNumber = rungnumber;

	// Rung type parameters.
	this.RungType = matrixdata["rungtype"];
	// Rung comment.
	this.RungComment = matrixdata["comment"];
	// IL data.
	this.ILData = matrixdata["ildata"];


	// Save an extra copy of the rung comment so we can restore 
	// it if we cancell the edit.
	this.OriginalRungComment = matrixdata["comment"];
	// Save the original matrix data.
	this.OriginalMatrixData = matrixdata["matrixdata"];


	// Rung SVG data.
	this.rungdata = {};

	// Rung editing buttons.
	this.RungInstrButtons = null;
	// Address editing.
	this.RungAddrEditing = null;
	// Rung ladder display.
	this.RungEditMatrix = null;
	// Rung edit and comment edit buttons.
	this.RungEditButtons = null;


	// The container for holding SVG items.
	this.svgcontainer = ladsymbols.svgcontainer;

	// This gives the ladder rung display items an offset.
	this.laddercontainer = ladsymbols.laddercontainer;

	// This is a single "empty" container (group) for holding edit items.
	this.cellcontainer = ladsymbols.cellcontainer;

	// Power rail to join inputs to outputs.
	this.svginprail = ladsymbols.svginprail;
	// Power rail to join inputs to outputs (second optional rail).
	this.svginprail2 = ladsymbols.svginprail2;
	// Power rail to join inputs to outputs (third optional rail).
	this.svginprail3 = ladsymbols.svginprail3;

	// Power rail to join outputs together.
	this.svgoutprail = ladsymbols.svgoutprail;
	// Decoration for output rail.
	this.svgoutpraildec = ladsymbols.svgoutpraildec;

	// Ref for rail to join inputs to outputs.
	this.RailHorz = null;
	// Ref for second (optional) rail to join inputs to outputs.
	this.RailHorz2 = null;
	// Ref for third (optional) rail to join inputs to outputs.
	this.RailHorz3 = null;

	// Ref for rail joining the left side of the outputs.
	this.RailVert = null;



	// Fill colour for cell is selected.
	this.SelectedColour = 'lightgrey';
	// Fill colour for cell is not selected.
	this.DeselectedColour = 'whitesmoke';



	// Parameters for all SVG matrix coordinates. 
	this.AllMatrixParams = ladsymbols.MatrixParams;
	// Parameters for current type of SVG matrix coordinates.
	this.MatrixParams = this.AllMatrixParams["single"];
	// The rung types for valid ladder. 
	this.RungOutputTypes = ladsymbols.RungOutputTypes;
	// Look up the CSS styles for hiding and showing rungs.
	this.RungStylesLadder = ladsymbols.RungStylesLadder;

	// Reference for rung comment editing.
	this.RungCommentDisplayField = null;

	// Instruction edit button "masks".
	this.InstructionMasks = ladsymbols.InstructionMasks;


	// Padding to add to increase the height of the rung.
	this.RungHeightPad = ladsymbols.RungHeightPad;

	// Current cell id string.
	this.CurrentCell = null;

	// Current cell type (input or output).
	this.CurrentCellType = null;


	// Currently selected buttons.
	this.CurrentButtons = "none";


	/* This is the complete list of all the ids for the *groups* of address edit fields. */
	this.addresseditgroups = ladsymbols.addresseditgroups;


	// References to the different edit button types.
	this.ButtonDefs = ladsymbols.buttondefs;
	// References to the background edit tabs for inputs.
	this.ButtonInputTabs = ladsymbols.buttonsinputtabs;
	// References to the background edit tabs for outputs.
	this.ButtonsOutputTabs = ladsymbols.buttonsoutputtabs;
	
	// Get the references to the rung comment edit field. 
	this.RungCommentEdit = null;


	// ==================================================================
	// Generate an editable form of the rung.


	// ##################################################################
	/* Initialise the rung for editing. This *must* be executed immediately
	after the object is created and before any editing operations are 
	attempted.
	This displays whatever initial data is in the matrix object. We 
	initialise whatever we can at this time, but if the rung is empty, we 
	may not be able to complete initialisation until an output type is selected.
	*/
	function _InitEditRung() {


		// Display the rung editor.
		this.RungEditor = this.docref.getElementById("rungeditor");
		this.RungEditor.setAttribute("class", "rungshow");

		// Rung comment area (for editing). Fill the edit field with the current comment.
		this.RungCommentEdit = this.docref.getElementById("rungcommentedit");
		this.RungCommentEdit.value = this.RungComment;

		// Used to display the rung comments.
		this.RungCommentDisplayField = this.docref.getElementById("rungcomment" + this.RungNumber);


		// Set the appropriate matrix coordinate set.
		this.MatrixParams = this.AllMatrixParams[this.RungType];

		// Look up whether to hide or show the ladder or IL areas.
		var ladderstyle = this.RungStylesLadder[this.RungType]["ladder"];
		var ilstyle = this.RungStylesLadder[this.RungType]["il"];
		// Hide all the address edit fields.
		this.HideAddressEditFields();


		// Add the IL editing text area.
		var ILEditBox = this.docref.getElementById("ileditarea");
		ILEditBox.setAttribute("class", ilstyle);
		
		// Make sure there are new line characters at the end of each line.
		var runglist = [];
		for (i in this.ILData) {
			if (this.ILData[i].length > 0) {
				runglist.push(this.ILData[i] + "\n");
			}
		}
		// Fill the IL editor with the IL data.
		this.docref.forms.ileditor.ilcontent.value = runglist.join("");


		// Disable the edit buttons which are not valid for this
		// rung type.
		this.MaskEditButtons(this.RungType);


		// Display the output buttons.
		this.ShowButtons("outputbuttons");
		this.CurrentCellType = "outputs";

		// Initialise the edit matrix provided we know what type
		// of rung to use.
		if (this.RungOutputTypes.indexOf(this.RungType) >= 0) {
			this.InitEditMatrix();
		}
		
	}
	this.InitEditRung = _InitEditRung;


	// ##################################################################
	/* Generate a new rung data object to hold all the current rung data.
	This defines the edit "matrix" for the rung we are currently editing.
		"value" (string) = The ladder symbol code for the current cell.
		"addr" (array) = An array of strings containing the addresses.
		"row" (integer) = The matrix row. Inputs and outputs occupy separate matrices.
		"col" (integer) = The matrix column. Outputs only have one column.
		"type" (string) = inputs or outputs.
		"ladder" (string) = The "id" for the ladder SVG.
		"address" (string) = The "id" for the address SVG.
	*/
	function _GenRungDataObject() {
		this.rungdata= {};
		// Generate the inputs.
		for (var i = 0; i <= this.MatrixParams["maxinputrow"]; i++) {
			for (var j = 0; j <= this.MatrixParams["maxinputcol"]; j++) {
				this.rungdata["inputedit" + i + j] = {"value" : "none", "addr" : [""], 
						"row" : i, "col" : j, 
						"type" : "inputs", 
						"ladder" : "inputladder" + i + j, 
						"address" : "inputtext" + i + j};
			}
		}

		// Generate the outputs.
		for (var i = 0; i <= this.MatrixParams["maxoutputrow"]; i++) {
			this.rungdata["outputedit" + i] = {"value" : "none", "addr" : [""], 
					"row" : i, "col" : 0, 
					"type" : "outputs", 
					"ladder" : "outputladder" + i, 
					"address" : "outputtext" + i};
		}

	}
	this.GenRungDataObject = _GenRungDataObject;


	// ##################################################################
	/* Initialise the edit matrix. At this point we need to know the rung
		type so that we know the rung X and Y parameters. That means
		if we have an empty rung then we have to wait until we add
		an output.
	*/
	function _InitEditMatrix() {
		
		// Re-generate the rung data object.
		this.GenRungDataObject();

		// id for the ladder matrix div.
		var editladder = "laddereditor";

		// Add the rung ladder display to the rung.
		var svgmatrix = this.GenSVGMatrix();
		this.RungEditMatrix = this.docref.getElementById(editladder);
		this.RungEditMatrix.appendChild(svgmatrix);

		// Copy the initialised matrix data to the edit matrix.
		this.SetMatrixData(this.OriginalMatrixData);


		// Display the ladder symbols and their addresses.
		for (var i in this.rungdata) {
			this.DisplayCell(i);
		}

		// Fix up the position of the joining rail.
		this.FixHRail();

		// Fix up the rail which joins the left side of the outputs.
		this.FixVRail();

		// Now we need to set the current cell and update the 
		// address data for editing.
		this.CurrentCell = "outputedit0";
		this.FillEditFields(this.CurrentCell);
		this.SetCellColour(this.CurrentCell, this.SelectedColour);
	}
	this.InitEditMatrix = _InitEditMatrix;


	// ##################################################################
	/* Generate a single input row of SVG.
	Parameters:
		row: (integer) = The current row.
		InputPitch: (integer) = The horizontal pitch between cells.
		InputVert: (integer) = The vertical pitch between cells.
		laddercontainer: (reference) = A row of SVG references to which
			the new SVG is added.
	Return: Nothing (modifies laddercontainer). 
	*/
	function _GenSVGInpRow(row, InputPitch, InputVert, laddercontainer) {
		var y = row * InputVert;

		for (var col = 0; col <= this.MatrixParams["maxinputcol"]; col++) {
			var x = col * InputPitch;
			var cellid =  "inputedit" + row + "" + col;
			var cellcontainer = this.cellcontainer.cloneNode(true);
			cellcontainer.setAttribute("id", cellid);
			cellcontainer.setAttribute("transform", "translate(" + x + "," + y + ")");

			// Add the mouse click handler. 
			cellcontainer.setAttribute("onclick", "LadEditor.ClickInput('"+ cellid + "');");

			// Add the empty edit matrix backgrounds.
			var ladsym = this.LadSymbols["none"]["symbolref"];
			var instrsymb = ladsym.cloneNode(true);
			cellcontainer.appendChild(instrsymb);

			// Add the matrix location to the rung container. 
			laddercontainer.appendChild(cellcontainer);
		}

	}
	this.GenSVGInpRow = _GenSVGInpRow;


	// ##################################################################
	/* Delete the existing SVG edit matrix if it is present.
	*/
	function _DeleteSVGMatrix() {
		var laddercontainer = this.docref.getElementById("laddereditcontainer");

		// Delete the old matrix (if present).
		if (laddercontainer.hasChildNodes()) {
			while (laddercontainer.firstChild) {
				laddercontainer.removeChild(laddercontainer.firstChild);
			}
		} 
	}
	this.DeleteSVGMatrix = _DeleteSVGMatrix;



	// ##################################################################
	/* Generate the SVG edit matrix. This is an empty matrix to which
	instruction elements are added later.
	*/
	function _GenSVGMatrix() {

		// Containers for the entire edit maxtrix.
		var svgcontainer = this.docref.getElementById("laddereditsvgcontainer");
		var laddercontainer = this.docref.getElementById("laddereditcontainer");

		// Delete the old matrix (if present).
		this.DeleteSVGMatrix();

		// Create the input matrix.
		for (var row = 0; row <= this.MatrixParams["maxinputrow"]; row++) {
			this.GenSVGInpRow(row, this.MatrixParams["inputpitch"], 
							this.MatrixParams["inputvert"], laddercontainer);
		}


		// Create the output matrix.
		for (var row = 0; row <= this.MatrixParams["maxoutputrow"]; row++) {
			var cellid = "outputedit" + row;
			var cellcontainer = this.cellcontainer.cloneNode(true);
			cellcontainer.setAttribute("id", cellid);
			var x = this.MatrixParams["outputxpos"];
			var y = row * this.MatrixParams["vertpitch"];
			cellcontainer.setAttribute("transform", "translate(" + x + "," + y + ")");
			// Add the mouse click handler. 
			cellcontainer.setAttribute("onclick", "LadEditor.ClickOutput('" + cellid + "');");

			// Add the empty edit matrix backgrounds.
			var ladsym = this.LadSymbols["none"]["symbolref"];
			var instrsymb = ladsym.cloneNode(true);
			cellcontainer.appendChild(instrsymb);

			laddercontainer.appendChild(cellcontainer);
		}


		// Add in the rung decorations.
		this.RailHorz = this.svginprail.cloneNode(true);
		this.RailHorz2 = this.svginprail2.cloneNode(true);
		this.RailHorz3 = this.svginprail3.cloneNode(true);
		this.RailVert = this.svgoutprail.cloneNode(true);

		this.RailHorz.setAttribute("id", "joinhorz");
		this.RailHorz2.setAttribute("id", "joinhorz2");
		this.RailHorz3.setAttribute("id", "joinhorz3");
		this.RailVert.setAttribute("id", "joinvert");

		laddercontainer.appendChild(this.RailHorz);
		laddercontainer.appendChild(this.RailHorz2);
		laddercontainer.appendChild(this.RailHorz3);
		laddercontainer.appendChild(this.RailVert);

		// Add in the rail join decoration only for "single" rungs.
		if (this.RungType == "single") {
			var decoration = this.svgoutpraildec.cloneNode(true);
			laddercontainer.appendChild(decoration);
		}


		// Set the height for the SVG container.
		var inpheight = (this.MatrixParams["maxinputrow"] + 1) * this.MatrixParams["inputvert"];
		var outpheight = (this.MatrixParams["maxoutputrow"] + 1) * this.MatrixParams["vertpitch"];

		svgcontainer.setAttribute("height", (Math.max(inpheight, outpheight) + this.RungHeightPad) + "px");



		// Return the completed matrix.
		return svgcontainer;
	}
	this.GenSVGMatrix = _GenSVGMatrix;



	// ##################################################################
	/* Copy the initialised matrix data to the edit matrix.
	*/
	function _SetMatrixData(matrixdata) {
		for (var i in matrixdata) {
			this.rungdata[i]["value"] = matrixdata[i]["value"];
			this.rungdata[i]["addr"] = matrixdata[i]["addr"];
		}
	}
	this.SetMatrixData = _SetMatrixData;


	// ##################################################################
	/* Return the current rung matrix data.
	*/
	function _GetMatrixData() {
		var matrixdata = {};
		for (var i in this.rungdata) {
			if (this.rungdata[i]["value"] != "none") {
				matrixdata[i] = {"value" : "none", "addr" : [""]};
				matrixdata[i]["value"] = this.rungdata[i]["value"];
				matrixdata[i]["addr"] = this.rungdata[i]["addr"];
			}
		}

		return matrixdata;
	}
	this.GetMatrixData = _GetMatrixData;


	// ==================================================================


	// ##################################################################
	/* Remove the rung edit buttons.
	*/
	function _RemoveRungEditButtons() {
		var element = this.RungEditButtons;
		if (element) {
			while (element.firstChild) {
			  element.removeChild(element.firstChild);
			}
		}
	}
	this.RemoveRungEditButtons = _RemoveRungEditButtons;

	// ##################################################################
	/* Clean up the existing edit rung prior to exiting. 
	*/
	function _CloseRung() {

		// Hide the rung editor.
		this.RungEditor = this.docref.getElementById("rungeditor");
		this.RungEditor.setAttribute("class", "runghide");

		// Delete the old matrix (if present).
		this.DeleteSVGMatrix();

	}
	this.CloseRung = _CloseRung;



	// ##################################################################
	/* Clear the existing edit matrix, but leave the other editing features
		in place.
	*/
	function _ClearRung() {

		// Delete the SVG edit matrix
		this.DeleteSVGMatrix();
		// Set the rung type to "empty".
		this.RungType = "empty";
		// Hide all the address edit fields.
		this.HideAddressEditFields();

		// Clear the rung data matrix.
		this.OriginalMatrixData = {};
		// Clear the current data.
		this.rungdata = {};

		// Disable the edit buttons which are not valid for this
		// rung type.
		this.MaskEditButtons(this.RungType);

		// Display the output buttons.
		this.ShowButtons("outputbuttons");
		this.CurrentCellType = "outputs";

	}
	this.ClearRung = _ClearRung;

	// ==================================================================


	// ##################################################################
	/* Return the default address for the requested symbol.
	Parameters: ladsymbol (string) = The string code for the ladder symbol.
	Returns: (array) = An array of strings containing the default addresses.
	*/
	function _DefaultAddr(ladsymbol) {
		var defaddr = [];
		for (var i in this.LadSymbols[ladsymbol]["defaultaddr"]) {
			defaddr.push(this.LadSymbols[ladsymbol]["defaultaddr"][i]);
		}
		return defaddr;
	}
	this.DefaultAddr = _DefaultAddr;



	// ##################################################################
	/* Set the cell colour. 
	Parameters:
		cellid (string) = ID for destination.
		newcolour (string) = Desired colour.
	*/
	function _SetCellColour(cellid, newcolour) {
		var cellref = docref.getElementById(cellid);		
		cellref.setAttribute('fill', newcolour);
	}
	this.SetCellColour = _SetCellColour;



	// ##################################################################

	/* Store the values from one individual cell to another. 
	Parameters: srccellid (string) = The id string for the source cell.
		destcellid (string) = The id string for the destination cell.
	*/
	function _CopyCellData(srccellid, destcellid) {

		this.rungdata[destcellid]["value"] = this.rungdata[srccellid]["value"];
		this.rungdata[destcellid]["addr"] = this.rungdata[srccellid]["addr"];
	}
	this.CopyCellData = _CopyCellData;


	// ##################################################################

	/* Delete the values in one individual cell. 
	Parameters: cellid (string) = The id string for the cell to be deleted.
	*/
	function _DeleteCell(cellid) {
		this.rungdata[cellid]["value"] = "none";
		this.rungdata[cellid]["addr"] = [""];
	}
	this.DeleteCell = _DeleteCell;


	// ##################################################################

	/* Returns true if the cell value indicate there is no symbol present.
	Parameters: cellid (string) = The cell id.
	Returns: (boolean) = true if the cell ladder code indicates there is
		no valid symbol present to display.
	*/
	function _CellIsEmpty(cellid) {
		return (this.rungdata[cellid]["value"] == "none");
	}
	this.CellIsEmpty = _CellIsEmpty;



	// ##################################################################
	/* Insert the cell address SVG. 
	Parameters: cellid (string) = The id string for the cell which is to be updated.
	*/
	function _DispCellAddr(cellid) {
		// Look up the matrix data location to see what sort of 
		// instruction it is.
		var cellvalue = this.rungdata[cellid]["value"];
		// Address cell in web page.
		var cellref = this.docref.getElementById(cellid);


		// Display all the addresses (there could be several).
		for (var i=0; i < this.LadSymbols[cellvalue]["addrref"].length; i++) {

			// Cell data to display. 
			var celladdrtext = this.rungdata[cellid]["addr"][i];

			// SVG prototype for displaying addresses.
			var textsrcid = this.LadSymbols[cellvalue]["addrref"][i];
			var textcellsrc = textsrcid.cloneNode(true);


			// Set the text.
			if (textcellsrc != null) {
				textcellsrc.firstChild.data = celladdrtext;
				cellref.appendChild(textcellsrc.cloneNode(true));
			}
			
		}
	
	}
	this.DispCellAddr = _DispCellAddr;



	// ##################################################################
	/* Update the SVG from the matrix data object. 
	This inserts the SVG ladder symbol and then inserts the
	actual text text. It also sets the cell background to the default 
	"deselected" colour.
	Parameters: cellid (string) = The id string for the cell which is to be updated.
	*/
	function _DisplayCell(cellid) {

		// Address cell in web page.
		var cellref = this.docref.getElementById(cellid);


		// If there are any existing elements, remove them first.
		if (cellref.hasChildNodes()) {
			while (cellref.firstChild) {
				cellref.removeChild(cellref.firstChild);
			}
		} 


		// Look up the matrix data location.
		var cellvalue = this.rungdata[cellid]["value"];

		// Ladder cell.
		var ladname = this.LadSymbols[cellvalue]["symbolref"];
		var ladsymb = ladname.cloneNode(true);
		cellref.appendChild(ladsymb);
		
		// Set the text.
		this.DispCellAddr(cellid);

		// Set the background colour to the default.
		cellref.setAttribute('fill', this.DeselectedColour);
	}
	this.DisplayCell = _DisplayCell;


	// ==================================================================


	// ##################################################################
	/* Fix the length of one row of horizontal rails that joins the inputs the outputs.
	Parameters
		row: (integer) = The row that is being fixed.
		rail: (object) = A reference to the rail SVG being fixed up.
	*/
	function _FixOneRail(row, rail) {
		var rowprefix = "inputedit" + row;
		for (var i = (this.MatrixParams["maxinputcol"]); i >= 0; i--) {
			if (!this.CellIsEmpty(rowprefix + i)) {
				rail.setAttribute('x1', this.MatrixParams["inputpitch"] * (i + 1));
				return;
			}
		}
		// Didn't find any instructions.
		rail.setAttribute('x1', this.MatrixParams["inputpitch"] * (this.MatrixParams["maxinputcol"] + 1));
	}
	this.FixOneRail = _FixOneRail;


	// ##################################################################
	/* Fix the length of the horizontal rail that joins the inputs the outputs. 
	   This checks the type of rung and fixes up the appropriate ones. 
	*/
	function _FixHRail() {
		// If this is a single rung.
		if (this.RungType == "single") {
			this.FixOneRail(0, this.RailHorz);
		}
		// If this is a double rung.
		if (this.RungType == "double") {
			this.FixOneRail(0, this.RailHorz);
			this.FixOneRail(1, this.RailHorz2);
		}
		// If this is a double rung.
		if (this.RungType == "triple") {
			this.FixOneRail(0, this.RailHorz);
			this.FixOneRail(1, this.RailHorz2);
			this.FixOneRail(2, this.RailHorz3);
		}
	}
	this.FixHRail = _FixHRail;
	
	

	// ##################################################################
	/* Fix the length of the vertical rail that joins the outputs together. */
	function _FixVRail() {
		for (var i = (this.MatrixParams["maxoutputrow"]); i > 0; i--) {
			if (!this.CellIsEmpty("outputedit" + i)) {
				this.RailVert.setAttribute('y2', this.MatrixParams["vertpitch"] * i);
				return;
			}
		}
		// Didn't find any instructions.
		this.RailVert.setAttribute('y2', 0);
	}
	this.FixVRail = _FixVRail;

	// ==================================================================


	// ################################################
	/* Show one set of instruction edit buttons, while hiding the rest. 
	Parameters: buttonid (string) = ID of button to display.
	*/
	function _ShowButtons(buttonid) {

		// Check to see if there is any change in status.
		if (buttonid == this.CurrentButtons) {
			return;
		}

		// Hide all the buttons.
		for (var i in this.ButtonDefs) {
			this.ButtonDefs[i]["buttonref"].setAttribute("display", "none");
		}
		// Hide the tabs.
		this.ButtonInputTabs.setAttribute("display", "none");
		this.ButtonsOutputTabs.setAttribute("display", "none");

		// Now show the buttons and tabs requested.
		this.ButtonDefs[buttonid]["buttonref"].setAttribute("display", "block");
		this.ButtonDefs[buttonid]["tabref"].setAttribute("display", "block");


		this.CurrentButtons = buttonid;


	}
	this.ShowButtons = _ShowButtons;


	// ################################################
	/* Hide or show the instruction edit button masks according to the current
		rung type. This is used to enable or disable instruction buttons
		which are not supported for the current rung type.
	Parameters: rungtype (string) = The rung type. This should be either
		"single" , "double" , or "triple" and should represent the
		rung type of the current rung. 
	*/
	function _MaskEditButtons(rungtype) {

		var singlemask = "runghide";
		var doublemask = "runghide";
		var triplemask = "runghide";

		// First, figure out what to do with each mask type. We need to 
		// *show* the mask to disable an instruction, and *hide* the
		// mask to disable the instruction.
		switch (rungtype) {
			case "single" : {
				var singlemask = "runghide";
				var doublemask = "rungshow";
				var triplemask = "rungshow";
				break;
			};
			case "double" : {
				var singlemask = "rungshow";
				var doublemask = "runghide";
				var triplemask = "rungshow";
				break;
			};
			case "triple" : {
				var singlemask = "rungshow";
				var doublemask = "rungshow";
				var triplemask = "runghide";
				break;
			};
		};

		// Handle the single instructions.
		for (var i in this.InstructionMasks["single"]) {
			var maskref = this.docref.getElementById(this.InstructionMasks["single"][i]);
			maskref.setAttribute("class", singlemask);
		}
		// Handle the double instructions.
		for (var i in this.InstructionMasks["double"]) {
			var maskref = this.docref.getElementById(this.InstructionMasks["double"][i]);
			maskref.setAttribute("class", doublemask);
		}
		// Handle the triple instructions.
		for (var i in this.InstructionMasks["triple"]) {
			var maskref = this.docref.getElementById(this.InstructionMasks["triple"][i]);
			maskref.setAttribute("class", triplemask);
		}

	}
	this.MaskEditButtons = _MaskEditButtons;


	// ==================================================================

	// ##################################################################
	/* Hide all the address edit fields.
	*/
	function _HideAddressEditFields() {

		// Hide all the address editing fields. We do this by means of classes
		// because setting the display attributes directly does not seem to work.
		for (var i = 0; i < this.addresseditgroups.length; i++) {
			var editref = this.docref.getElementById(this.addresseditgroups[i]);
			editref.setAttribute("class", "editaddrhide");
		}

	}
	this.HideAddressEditFields = _HideAddressEditFields;

	// ==================================================================

	// ##################################################################
	/* The following functions test for common parameter types.
	*/

	/* Returns true if param is a numeric register.
	*/
	function _IsNumericReg(param) {
		return /^D[SDFH][0-9]+$|^[TS]D[0-9]+$|^CTD[0-9]+$|^[XY]S[0-9]+$|^[XY]D[0-9]+$/.test(param);
	}
	this.IsNumericReg = _IsNumericReg;

	/* Returns true if param is a number.
	*/
	function _IsNumber(param) {
		// Integer, floating point, and hexadecimal.
		return /^[-+]?[0-9]+$|^[-+]?[0-9]+[.]?[0-9]+$|^[0-9A-F]+H$/.test(param);
	}
	this.IsNumber = _IsNumber;

	/* Returns true if param is a text register.
	*/
	function _IsTextReg(param) {
		return /^TXT[0-9]+$/.test(param);
	}
	this.IsTextReg = _IsTextReg;

	/* Returns true if param is a text constant (string).
	*/
	function _IsTextConst(param) {
		return /^"[^"]+"$/.test(param);
	}
	this.IsTextConst = _IsTextConst;

	/* Returns true if param is a pointer.
	*/
	function _IsPointer(param) {
		return /^D[SDFH]\[DS[0-9]+\]$/.test(param);
	}
	this.IsPointer = _IsPointer;


	/* Strip blanks and convert to upper case.
	*/
	function _StripAndUpper(param) {
		return param.toUpperCase().replace(/ /g, "");
	}
	this.StripAndUpper = _StripAndUpper;

	/* Change the input box background colour to signal if the parameters were OK.
	Parameters: inpname (string) = The id of the HTML input tag.
	 	paramok (boolean) = True indicates the parameter was OK.
	*/
	function _SignalParamStatus(inpid, paramok) {
		// Signal if the parameters were ok.
		var paraminput = this.docref.getElementById(inpid);
		if (paramok) {
			paraminput.setAttribute("class", "editok");
		} else {
			paraminput.setAttribute("class", "editerror");
		}
	}
	this.SignalParamStatus = _SignalParamStatus;



	// ##################################################################
	/* Fill the edit fields for contacts with one address.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillContactField(rungdata) {
		this.docref.forms.addreditcontact1.contact1a.value = rungdata[0];
		this.SignalParamStatus("editcontact1a", true);
	}
	this.FillContactField = _FillContactField;


	/* Get the data values entered by the user for contacts with one address.
	Returns: (array) = An array of the new data values.
	*/
	function _GetContactValues() {
		var valresult = [];
		var contactaddr = this.docref.forms.addreditcontact1.contact1a.value;

		// Convert to upper case and strip blanks.
		var contactaddr = this.StripAndUpper(contactaddr);
		valresult.push(contactaddr);

		// Check if the address is OK.
		paramok = /^[XYCT][0-9]+$|^CT[0-9]+$|^SC[0-9]+$/.test(contactaddr);
		// Signal the status.
		this.SignalParamStatus("editcontact1a", paramok);
		// Save the result if OK.
		if (paramok) {
			this.rungdata[this.CurrentCell]["addr"] = valresult;
		}

		return paramok;

	}
	this.GetContactValues = _GetContactValues;



	// ##################################################################
	/* Fill the edit fields for compare inputs with two addresses.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCompareField(rungdata) {
		this.docref.forms.addreditcontact2.contact2a.value = rungdata[0];
		this.docref.forms.addreditcontact2.contact2b.value = rungdata[1];
		this.SignalParamStatus("editcontact2a", true);
		this.SignalParamStatus("editcontact2b", true);
	}
	this.FillCompareField = _FillCompareField;


	/* Get the data values entered by the user for compare inputs with two address.
	Returns: (array) = An array of the new data values.
	*/
	function _GetCompareValues() {
		var valresult = [];
		var firstval = this.docref.forms.addreditcontact2.contact2a.value;
		var secondval = this.docref.forms.addreditcontact2.contact2b.value;

		// Convert to upper case and strip blanks but only if they
		// are not string constants.
		if (!this.IsTextConst(firstval)) {
			var firstval = this.StripAndUpper(firstval);
		}
		if (!this.IsTextConst(secondval)) {
			var secondval = this.StripAndUpper(secondval);
		}
		valresult.push(firstval);
		valresult.push(secondval);

		
		// Check if the address is OK.
		var param1ok = (this.IsNumericReg(firstval) || this.IsNumber(firstval) ||
					this.IsTextReg(firstval) || this.IsTextConst(firstval));
		var param2ok = (this.IsNumericReg(secondval) || this.IsNumber(secondval) ||
					this.IsTextReg(secondval) || this.IsTextConst(secondval));

		// Signal if the parameters were ok.
		this.SignalParamStatus("editcontact2a", param1ok);
		this.SignalParamStatus("editcontact2b", param2ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}

	}
	this.GetCompareValues = _GetCompareValues;


	// ##################################################################
	/* Fill the edit fields for coils with one address.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillcoilField(rungdata) {
		this.docref.forms.addreditcoil1.coil1a.value = rungdata[0];
		this.SignalParamStatus("editcoil1a", true);
	}
	this.FillcoilField = _FillcoilField;


	/* Get the data values entered by the user for coils with one address.
	Returns: (array) = An array of the new data values.
	*/
	function _GetcoilValues() {
		var valresult = [];
		var coiladdr = this.docref.forms.addreditcoil1.coil1a.value;

		// Convert to upper case and strip blanks.
		var coiladdr = this.StripAndUpper(coiladdr);
		valresult.push(coiladdr);
		// Update the screen representation.
		this.docref.forms.addreditcoil1.coil1a.value = coiladdr;


		// Check if the address is OK.
		paramok = /^Y[0-9]+$|^C[0-9]+$/.test(coiladdr);
		// Signal the status.
		this.SignalParamStatus("editcoil1a", paramok);
		// Save the result if OK.
		if (paramok) {
			this.rungdata[this.CurrentCell]["addr"] = valresult;
		}

		return paramok;
	}
	this.GetcoilValues = _GetcoilValues;


	// ##################################################################
	/* Fill the edit fields for output coils with two addresses.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCoil2Field(rungdata) {
		this.docref.forms.addreditcoil2.coil2a.value = rungdata[0];
		this.docref.forms.addreditcoil2.coil2b.value = rungdata[1];
		this.SignalParamStatus("editcoil2a", true);
		this.SignalParamStatus("editcoil2b", true);
	}
	this.FillCoil2Field = _FillCoil2Field;


	/* Get the data values entered by the user for output coils with two addresses.
	Returns: (array) = An array of the new data values.
	*/
	function _GetCoil2Values() {
		var valresult = [];
		var coiladdr1 = this.docref.forms.addreditcoil2.coil2a.value;
		var coiladdr2 = this.docref.forms.addreditcoil2.coil2b.value;

		// Convert to upper case and strip blanks.
		var coiladdr1 = this.StripAndUpper(coiladdr1);
		valresult.push(coiladdr1);
		var coiladdr2 = this.StripAndUpper(coiladdr2);
		valresult.push(coiladdr2);

		// Update the screen representation.
		this.docref.forms.addreditcoil2.coil2a.value = coiladdr1;
		this.docref.forms.addreditcoil2.coil2b.value = coiladdr2;

		// Check if the address is OK.
		var param1ok = /^Y[0-9]+$|^C[0-9]+$/.test(coiladdr1);
		var param2ok = /^Y[0-9]+$|^C[0-9]+$/.test(coiladdr2);

		// Signal if the parameters were ok.
		this.SignalParamStatus("editcoil2a", param1ok);
		this.SignalParamStatus("editcoil2b", param2ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}

	}
	this.GetCoil2Values = _GetCoil2Values;


	// ##################################################################
	/* Fill the edit fields for CALL parameters.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCallField(rungdata) {
		this.docref.forms.addreditcall.subrname.value = rungdata[0];
		this.SignalParamStatus("editcall", true);
	}
	this.FillCallField = _FillCallField;


	/* Get the data values entered by the user for CALL parameters.
	Returns: (array) = An array of the new data values.
	*/
	function _GetCallValues() {
		var valresult = [];
		var subname = this.docref.forms.addreditcall.subrname.value;

		// We strip blanks, but we don't convert to upper case.
		var subname = subname.replace(/ /g, "");
		valresult.push(subname);
		// Update the screen representation.
		this.docref.forms.addreditcall.subrname.value = subname;


		// Check if the address is OK.
		paramok = /^[a-zA-Z]+[0-9a-zA-Z]+$/.test(subname);
		// Signal the status.
		this.SignalParamStatus("editcall", paramok);
		// Save the result if OK.
		if (paramok) {
			this.rungdata[this.CurrentCell]["addr"] = valresult;
		}

		return paramok;
	}
	this.GetCallValues = _GetCallValues;


	// ##################################################################
	/* Fill the edit fields for FOR in a For/Next loop.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillForField(rungdata) {
		this.docref.forms.addreditfor.foraddr.value = rungdata[0];
		this.docref.forms.addreditfor.oneshot.checked = (rungdata[1] == true);
		this.SignalParamStatus("editfor", true);
	}
	this.FillForField = _FillForField;


	/* Get the data values entered by the user for FOR in a For/Next loop.
	Returns: (array) = An array of the new data values.
	*/
	function _GetForValues() {
		var valresult = [];
		var forcount = this.docref.forms.addreditfor.foraddr.value;

		// Convert to upper case and strip blanks.
		var forcount = this.StripAndUpper(forcount);
		valresult.push(forcount);
		// Update the screen representation.
		this.docref.forms.addreditfor.foraddr.value = forcount;

		// We can assume the one shot parameter is OK, as it is
		// a check box.
		if (this.docref.forms.addreditfor.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}


		// Check if the address is OK. 
		paramok = (/^DS[0-9]+$/.test(forcount) || /^[0-9]+$/.test(forcount));
		// Signal the status.
		this.SignalParamStatus("editfor", paramok);
		// Save the result if OK.
		if (paramok) {
			this.rungdata[this.CurrentCell]["addr"] = valresult;
		}

		return paramok;
	}
	this.GetForValues = _GetForValues;


	// ##################################################################
	/* Fill the edit fields for counters.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCounterField(rungdata) {
		this.docref.forms.addreditcounter.counteraddr.value = rungdata[0];
		this.docref.forms.addreditcounter.counterpreset.value = rungdata[1];
		this.SignalParamStatus("editcounteraddr", true);
		this.SignalParamStatus("editcounterpreset", true);
	}
	this.FillCounterField = _FillCounterField;


	/* Get the data values entered by the user for counters.
	Returns: (array) = An array of the new data values.
	*/
	function _GetCounterValues() {
		var valresult = [];
		var counteraddr = this.docref.forms.addreditcounter.counteraddr.value;
		var counterpreset = this.docref.forms.addreditcounter.counterpreset.value;

		// Convert to upper case and strip blanks.
		var counteraddr = this.StripAndUpper(counteraddr);
		valresult.push(counteraddr);
		var counterpreset = this.StripAndUpper(counterpreset);
		valresult.push(counterpreset);

		// Update the screen representation.
		this.docref.forms.addreditcounter.counteraddr.value = counteraddr;
		this.docref.forms.addreditcounter.counterpreset.value = counterpreset;

		// Check if the address is OK.
		var param1ok = /^CT[0-9]+$/.test(counteraddr);
		var param2ok = /^[0-9]+$|^DS[0-9]+$|^DD[0-9]+$/.test(counterpreset);

		// Signal if the parameters were ok.
		this.SignalParamStatus("editcounteraddr", param1ok);
		this.SignalParamStatus("editcounterpreset", param2ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetCounterValues = _GetCounterValues;


	// ##################################################################
	/* Fill the edit fields for timers.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillTimerField(rungdata) {
		this.docref.forms.addredittimer.timeraddr.value = rungdata[0];
		this.docref.forms.addredittimer.timerpreset.value = rungdata[1];
		this.SignalParamStatus("edittimeraddr", true);
		this.SignalParamStatus("edittimerpreset", true);

		// Select the correct time base from the available options.
		this.docref.forms.addredittimer.timebase[0].checked = (rungdata[2] == "ms");
		this.docref.forms.addredittimer.timebase[1].checked = (rungdata[2] == "sec");
		this.docref.forms.addredittimer.timebase[2].checked = (rungdata[2] == "min");
		this.docref.forms.addredittimer.timebase[3].checked = (rungdata[2] == "hour");
		this.docref.forms.addredittimer.timebase[4].checked = (rungdata[2] == "day");
	}
	this.FillTimerField = _FillTimerField;


	/* Get the data values entered by the user for timers.
	Returns: (array) = An array of the new data values.
	*/
	function _GetTimerValues() {
		var valresult = [];

		var timeraddr = this.docref.forms.addredittimer.timeraddr.value;
		var timerpreset = this.docref.forms.addredittimer.timerpreset.value;

		// Convert to upper case and strip blanks.
		var timeraddr = this.StripAndUpper(timeraddr);
		valresult.push(timeraddr);
		var timerpreset = this.StripAndUpper(timerpreset);
		valresult.push(timerpreset);

		// Update the screen representation.
		this.docref.forms.addredittimer.timeraddr.value = timeraddr;
		this.docref.forms.addredittimer.timerpreset.value = timerpreset;


		// Get the selected time base from the radio buttons.
		if (this.docref.forms.addredittimer.timebase[0].checked) { 
			valresult.push("ms");
		}
		if (this.docref.forms.addredittimer.timebase[1].checked) { 
			valresult.push("sec");
		}
		if (this.docref.forms.addredittimer.timebase[2].checked) { 
			valresult.push("min");
		}
		if (this.docref.forms.addredittimer.timebase[3].checked) { 
			valresult.push("hour");
		}
		if (this.docref.forms.addredittimer.timebase[4].checked) { 
			valresult.push("day");
		}

		// Check if the parameters are OK.
		var param1ok = /^T[0-9]+$/.test(timeraddr);
		var param2ok = /^[0-9]+$|^DS[0-9]+$/.test(timerpreset);

		// Signal if the parameters were ok.
		this.SignalParamStatus("edittimeraddr", param1ok);
		this.SignalParamStatus("edittimerpreset", param2ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetTimerValues = _GetTimerValues;


	// ##################################################################
	/* Fill the edit fields for COPY.
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCopyField(rungdata) {
		this.docref.forms.addreditcopy.sourceaddr.value = rungdata[0];
		this.docref.forms.addreditcopy.destaddr.value = rungdata[1];
		this.docref.forms.addreditcopy.oneshot.checked = (rungdata[2] == true);

		this.SignalParamStatus("editcopy1a", true);
		this.SignalParamStatus("editcopy1b", true);
	}
	this.FillCopyField = _FillCopyField;


	/* Get the data values entered by the user for COPY.
	Returns: (array) = An array of the new data values.
	*/
	function _GetCopyValues() {
		var valresult = [];
		var copysource = this.docref.forms.addreditcopy.sourceaddr.value;
		var copydest = this.docref.forms.addreditcopy.destaddr.value;

		// Convert to upper case and strip blanks.
		// but only if they are not text constants.
		if (!this.IsTextConst(copysource)) {
			var copysource = this.StripAndUpper(copysource);
		}
		valresult.push(copysource);
		var copydest = this.StripAndUpper(copydest);
		valresult.push(copydest);

		// Update the screen representation.
		this.docref.forms.addreditcopy.sourceaddr.value = copysource;
		this.docref.forms.addreditcopy.destaddr.value = copydest;

		// Get the one shot option.
		if (this.docref.forms.addreditcopy.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (this.IsNumericReg(copysource) || this.IsNumber(copysource) || 
					this.IsTextReg(copysource) || this.IsTextConst(copysource) ||
					this.IsPointer(copysource));
		var param2ok = (/^D[SDFH][0-9]+$|^TD[0-9]+$|^CTD[0-9]+$|^TXT[0-9]+$|^[XY][DS][0-9]+$/.test(copydest) ||
				this.IsPointer(copydest));

		// Signal if the parameters were ok.
		this.SignalParamStatus("editcopy1a", param1ok);
		this.SignalParamStatus("editcopy1b", param2ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetCopyValues = _GetCopyValues;


	// ##################################################################
	/* Fill the edit fields for COPY BLOCK. CPYBLK
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCopyBlockField(rungdata) {
		this.docref.forms.addreditcpyblk.sourcestartaddr.value = rungdata[0];
		this.docref.forms.addreditcpyblk.sourceendaddr.value = rungdata[1];
		this.docref.forms.addreditcpyblk.destaddr.value = rungdata[2];
		this.docref.forms.addreditcpyblk.oneshot.checked = (rungdata[3] == true);

		this.SignalParamStatus("editcpyblk1a", true);
		this.SignalParamStatus("editcpyblk1b", true);
		this.SignalParamStatus("editcpyblk1c", true);
	}
	this.FillCopyBlockField = _FillCopyBlockField;


	/* Get the data values entered by the user for COPY BLOCK. CPYBLK
	Returns: (array) = An array of the new data values.
	*/
	function _GetCopyBlockValues() {
		var valresult = [];
		var sourcestart = this.docref.forms.addreditcpyblk.sourcestartaddr.value;
		var sourceend = this.docref.forms.addreditcpyblk.sourceendaddr.value;
		var dest = this.docref.forms.addreditcpyblk.destaddr.value;

		// Convert to upper case and strip blanks.
		var sourcestart = this.StripAndUpper(sourcestart);
		valresult.push(sourcestart);
		var sourceend = this.StripAndUpper(sourceend);
		valresult.push(sourceend);
		var dest = this.StripAndUpper(dest);
		valresult.push(dest);

		// Update the screen representation.
		this.docref.forms.addreditcpyblk.sourcestartaddr.value = sourcestart;
		this.docref.forms.addreditcpyblk.sourceendaddr.value = sourceend;
		this.docref.forms.addreditcpyblk.destaddr.value = dest;

		// Get the one shot option.
		if (this.docref.forms.addreditcpyblk.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (this.IsNumericReg(sourcestart) || this.IsTextReg(sourcestart));
		var param2ok = (this.IsNumericReg(sourceend) || this.IsTextReg(sourceend));
		var param3ok = (/^D[SDFH][0-9]+$|^TD[0-9]+$|^CTD[0-9]+$|^TXT[0-9]+$/.test(dest));


		// Signal if the parameters were ok.
		this.SignalParamStatus("editcpyblk1a", param1ok);
		this.SignalParamStatus("editcpyblk1b", param2ok);
		this.SignalParamStatus("editcpyblk1c", param3ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetCopyBlockValues = _GetCopyBlockValues;


	// ##################################################################
	/* Fill the edit fields for COPY BLOCK. CPYBLK
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillCopyFillField(rungdata) {
		this.docref.forms.addreditfill.sourceaddr.value = rungdata[0];
		this.docref.forms.addreditfill.deststartaddr.value = rungdata[1];
		this.docref.forms.addreditfill.destendaddr.value = rungdata[2];
		this.docref.forms.addreditfill.oneshot.checked = (rungdata[3] == true);

		this.SignalParamStatus("editfill1a", true);
		this.SignalParamStatus("editfill1b", true);
		this.SignalParamStatus("editfill1c", true);
	}
	this.FillCopyFillField = _FillCopyFillField;


	/* Get the data values entered by the user for COPY BLOCK. CPYBLK
	Returns: (array) = An array of the new data values.
	*/
	function _GetCopyFillValues() {
		var valresult = [];
		var sourceaddr = this.docref.forms.addreditfill.sourceaddr.value;
		var deststart = this.docref.forms.addreditfill.deststartaddr.value;
		var destend = this.docref.forms.addreditfill.destendaddr.value;

		// Convert to upper case and strip blanks.
		// but only if they are not text constants.
		if (!this.IsTextConst(sourceaddr)) {
			var sourceaddr = this.StripAndUpper(sourceaddr);
		}
		valresult.push(sourceaddr);
		var deststart = this.StripAndUpper(deststart);
		valresult.push(deststart);
		var destend = this.StripAndUpper(destend);
		valresult.push(destend);

		// Update the screen representation.
		this.docref.forms.addreditfill.sourceaddr.value = sourceaddr;
		this.docref.forms.addreditfill.deststartaddr.value = deststart;
		this.docref.forms.addreditfill.destendaddr.value = destend;

		// Get the one shot option.
		if (this.docref.forms.addreditfill.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (this.IsNumericReg(sourceaddr) || this.IsTextReg(sourceaddr) ||
				this.IsNumber(sourceaddr) || /^"[^"]"$/.test(sourceaddr));
		var param2ok = (this.IsNumericReg(deststart) || this.IsTextReg(deststart));
		var param3ok = (this.IsNumericReg(destend) || this.IsTextReg(destend));

		// Signal if the parameters were ok.
		this.SignalParamStatus("editfill1a", param1ok);
		this.SignalParamStatus("editfill1b", param2ok);
		this.SignalParamStatus("editfill1c", param3ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetCopyFillValues = _GetCopyFillValues;


	// ##################################################################
	/* Fill the edit fields for Copy PACK. 
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillPackField(rungdata) {
		this.docref.forms.addreditpack.sourcestartaddr.value = rungdata[0];
		this.docref.forms.addreditpack.sourceendaddr.value = rungdata[1];
		this.docref.forms.addreditpack.destaddr.value = rungdata[2];
		this.docref.forms.addreditpack.oneshot.checked = (rungdata[3] == true);

		this.SignalParamStatus("editpack1a", true);
		this.SignalParamStatus("editpack1b", true);
		this.SignalParamStatus("editpack1c", true);
	}
	this.FillPackField = _FillPackField;


	/* Get the data values entered by the user for Copy PACK.
	Returns: (array) = An array of the new data values.
	*/
	function _GetPackValues() {
		var valresult = [];
		var sourcestart = this.docref.forms.addreditpack.sourcestartaddr.value;
		var sourceend = this.docref.forms.addreditpack.sourceendaddr.value;
		var dest = this.docref.forms.addreditpack.destaddr.value;

		// Convert to upper case and strip blanks.
		var sourcestart = this.StripAndUpper(sourcestart);
		valresult.push(sourcestart);
		var sourceend = this.StripAndUpper(sourceend);
		valresult.push(sourceend);
		var dest = this.StripAndUpper(dest);
		valresult.push(dest);

		// Update the screen representation.
		this.docref.forms.addreditpack.sourcestartaddr.value = sourcestart;
		this.docref.forms.addreditpack.sourceendaddr.value = sourceend;
		this.docref.forms.addreditpack.destaddr.value = dest;

		// Get the one shot option.
		if (this.docref.forms.addreditpack.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (/^[XYCT][0-9]+$|^CT[0-9]+$|^SC[0-9]+$/.test(sourcestart));
		var param2ok = (/^[XYCT][0-9]+$|^CT[0-9]+$|^SC[0-9]+$/.test(sourceend));
		var param3ok = (/^DH[0-9]+$|^YD[0-9]+$/.test(dest));


		// Signal if the parameters were ok.
		this.SignalParamStatus("editpack1a", param1ok);
		this.SignalParamStatus("editpack1b", param2ok);
		this.SignalParamStatus("editpack1c", param3ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetPackValues = _GetPackValues;


	// ##################################################################
	/* Fill the edit fields for Copy UNPACK. 
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillUnpackField(rungdata) {
		this.docref.forms.addreditunpack.sourceaddr.value = rungdata[0];
		this.docref.forms.addreditunpack.deststartaddr.value = rungdata[1];
		this.docref.forms.addreditunpack.destendaddr.value = rungdata[2];
		this.docref.forms.addreditunpack.oneshot.checked = (rungdata[3] == true);

		this.SignalParamStatus("editunpack1a", true);
		this.SignalParamStatus("editunpack1b", true);
		this.SignalParamStatus("editunpack1c", true);
	}
	this.FillUnpackField = _FillUnpackField;


	/* Get the data values entered by the user for Copy UNPACK.
	Returns: (array) = An array of the new data values.
	*/
	function _GetUnpackValues() {
		var valresult = [];
		var sourceaddr = this.docref.forms.addreditunpack.sourceaddr.value;
		var deststart = this.docref.forms.addreditunpack.deststartaddr.value;
		var destend = this.docref.forms.addreditunpack.destendaddr.value;

		// Convert to upper case and strip blanks.
		var sourceaddr = this.StripAndUpper(sourceaddr);
		valresult.push(sourceaddr);
		var deststart = this.StripAndUpper(deststart);
		valresult.push(deststart);
		var destend = this.StripAndUpper(destend);
		valresult.push(destend);

		// Update the screen representation.
		this.docref.forms.addreditunpack.sourceaddr.value = sourceaddr;
		this.docref.forms.addreditunpack.deststartaddr.value = deststart;
		this.docref.forms.addreditunpack.destendaddr.value = destend;

		// Get the one shot option.
		if (this.docref.forms.addreditunpack.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (/^DH[0-9]+$/.test(sourceaddr));
		var param2ok = (/^[YC][0-9]+$/.test(deststart));
		var param3ok = (/^[YC][0-9]+$/.test(destend));


		// Signal if the parameters were ok.
		this.SignalParamStatus("editunpack1a", param1ok);
		this.SignalParamStatus("editunpack1b", param2ok);
		this.SignalParamStatus("editunpack1c", param3ok);
		

		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetUnpackValues = _GetUnpackValues;

	// ##################################################################
	/* Fill the edit fields for FIND. 
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillFindField(rungdata) {
		this.docref.forms.addreditfind.searchvalue.value = rungdata[0];
		this.docref.forms.addreditfind.sourcestartaddr.value = rungdata[1];
		this.docref.forms.addreditfind.sourceendaddr.value = rungdata[2];
		this.docref.forms.addreditfind.resultreg.value = rungdata[3];
		this.docref.forms.addreditfind.resultflag.value = rungdata[4];
		this.docref.forms.addreditfind.oneshot.checked = (rungdata[5] == true);

		this.SignalParamStatus("editfind1a", true);
		this.SignalParamStatus("editfind1b", true);
		this.SignalParamStatus("editfind1c", true);
		this.SignalParamStatus("editfind1d", true);
		this.SignalParamStatus("editfind1e", true);
	}
	this.FillFindField = _FillFindField;


	/* Get the data values entered by the user for FIND.
	Returns: (array) = An array of the new data values.
	*/
	function _GetFindValues() {
		var valresult = [];
		var searchvalue = this.docref.forms.addreditfind.searchvalue.value;
		var sourcestartaddr = this.docref.forms.addreditfind.sourcestartaddr.value;
		var sourceendaddr = this.docref.forms.addreditfind.sourceendaddr.value;
		var resultreg = this.docref.forms.addreditfind.resultreg.value;
		var resultflag = this.docref.forms.addreditfind.resultflag.value;


		// Convert to upper case and strip blanks.
		var searchvalue = this.StripAndUpper(searchvalue);
		valresult.push(searchvalue);
		var sourcestartaddr = this.StripAndUpper(sourcestartaddr);
		valresult.push(sourcestartaddr);
		var sourceendaddr = this.StripAndUpper(sourceendaddr);
		valresult.push(sourceendaddr);
		var resultreg = this.StripAndUpper(resultreg);
		valresult.push(resultreg);
		var resultflag = this.StripAndUpper(resultflag);
		valresult.push(resultflag);

		// Update the screen representation.
		this.docref.forms.addreditfind.searchvalue.value = searchvalue;
		this.docref.forms.addreditfind.sourcestartaddr.value = sourcestartaddr;
		this.docref.forms.addreditfind.sourceendaddr.value = sourceendaddr;
		this.docref.forms.addreditfind.resultreg.value = resultreg;
		this.docref.forms.addreditfind.resultflag.value = resultflag;

		// Get the one shot option.
		if (this.docref.forms.addreditfind.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok = (this.IsNumericReg(searchvalue) || this.IsNumber(searchvalue) || 
				this.IsTextReg(searchvalue) || this.IsTextConst(searchvalue));
		var param2ok = (this.IsNumericReg(sourcestartaddr) || this.IsTextReg(sourcestartaddr));
		var param3ok = (this.IsNumericReg(sourceendaddr) || this.IsTextReg(sourceendaddr));
		var param4ok = (/^DS[0-9]+$|^DD[0-9]+$/.test(resultreg));
		var param5ok = (/^C[0-9]+$/.test(resultflag));


		// Signal if the parameters were ok.
		this.SignalParamStatus("editfind1a", param1ok);
		this.SignalParamStatus("editfind1b", param2ok);
		this.SignalParamStatus("editfind1c", param3ok);
		this.SignalParamStatus("editfind1d", param4ok);
		this.SignalParamStatus("editfind1e", param5ok);


		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok && param4ok && param5ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetFindValues = _GetFindValues;

	// ##################################################################
	/* Fill the edit fields for MATHDEC and MATHHEX. 
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillMathField(rungdata) {
		this.docref.forms.addreditmath.destaddr.value = rungdata[0];
		this.docref.forms.addreditmath.oneshot.checked = (rungdata[1] == true);
		this.docref.forms.addreditmath.equation.value = rungdata[2];

		this.SignalParamStatus("editmathdest", true);
		this.SignalParamStatus("editmathequ", true);
	}
	this.FillMathField = _FillMathField;


	/* Get the data values entered by the user for MATHDEC and MATHHEX.
	Returns: (array) = An array of the new data values.
	*/
	function _GetMathValues() {
		var valresult = [];
		var destaddr = this.docref.forms.addreditmath.destaddr.value;
		var equation = this.docref.forms.addreditmath.equation.value;


		// Convert to upper case and strip blanks.
		var destaddr = this.StripAndUpper(destaddr);
		valresult.push(destaddr);

		// Get the one shot option. The one shot parameter comes
		// before the equation with this instruction.
		if (this.docref.forms.addreditmath.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Convert to upper case and strip blanks.
		var equation = equation.toUpperCase();
		valresult.push(equation);

		// Update the screen representation.
		this.docref.forms.addreditmath.destaddr.value = destaddr;
		this.docref.forms.addreditmath.equation.value = equation;


		// Check if the parameters are OK.
		var param1ok = /^D[SDFH][0-9]+$/.test(destaddr);
		// We can't really check equations.
		var param3ok = /^[a-zA-Z0-9 \+\-\*\/\^\(\),]+$/.test(equation);


		// Signal if the parameters were ok.
		this.SignalParamStatus("editmathdest", param1ok);
		this.SignalParamStatus("editmathequ", param3ok);


		// Save the parameters if they were all OK.
		if (param1ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetMathValues = _GetMathValues;



	// ##################################################################
	/* Fill the edit fields for math SUM. 
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillSumField(rungdata) {
		this.docref.forms.addreditsum.destaddr.value = rungdata[0];
		this.docref.forms.addreditsum.sourcestartaddr.value = rungdata[1];
		this.docref.forms.addreditsum.sourceendaddr.value = rungdata[2];
		this.docref.forms.addreditsum.oneshot.checked = (rungdata[3] == true);

		this.SignalParamStatus("editsum1a", true);
		this.SignalParamStatus("editsum1b", true);
		this.SignalParamStatus("editsum1c", true);
	}
	this.FillSumField = _FillSumField;


	/* Get the data values entered by the user for math SUM.
	Returns: (array) = An array of the new data values.
	*/
	function _GetSumValues() {
		var valresult = [];
		var destaddr = this.docref.forms.addreditsum.destaddr.value;
		var sourcestartaddr = this.docref.forms.addreditsum.sourcestartaddr.value;
		var sourceendaddr = this.docref.forms.addreditsum.sourceendaddr.value;


		// Convert to upper case and strip blanks.
		var destaddr = this.StripAndUpper(destaddr);
		valresult.push(destaddr);
		var sourcestartaddr = this.StripAndUpper(sourcestartaddr);
		valresult.push(sourcestartaddr);
		var sourceendaddr = this.StripAndUpper(sourceendaddr);
		valresult.push(sourceendaddr);

		// Update the screen representation.
		this.docref.forms.addreditsum.destaddr.value = destaddr;
		this.docref.forms.addreditsum.sourcestartaddr.value = sourcestartaddr;
		this.docref.forms.addreditsum.sourceendaddr.value = sourceendaddr;

		// Get the one shot option.
		if (this.docref.forms.addreditsum.oneshot.checked) {
			valresult.push(1);
		} else {
			valresult.push(0);
		}

		// Check if the parameters are OK.
		var param1ok =  /^D[SDFH][0-9]+$/.test(destaddr);
		var param2ok =  /^D[SDFH][0-9]+$/.test(sourcestartaddr);
		var param3ok =  /^D[SDFH][0-9]+$/.test(sourceendaddr);


		// Signal if the parameters were ok.
		this.SignalParamStatus("editsum1a", param1ok);
		this.SignalParamStatus("editsum1b", param2ok);
		this.SignalParamStatus("editsum1c", param3ok);


		// Save the parameters if they were all OK.
		if (param1ok && param2ok && param3ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetSumValues = _GetSumValues;


	// ##################################################################
	/* Fill the edit fields for Shift Register. SHFRG
	Parameters: rungdata (array) = An array of the address to use to fill the fields.
	*/
	function _FillShiftRegisterField(rungdata) {
		this.docref.forms.addreditshfrg.sourcestartaddr.value = rungdata[0];
		this.docref.forms.addreditshfrg.sourceendaddr.value = rungdata[1];

		this.SignalParamStatus("editshfrg1a", true);
		this.SignalParamStatus("editshfrg1b", true);
	}
	this.FillShiftRegisterField = _FillShiftRegisterField;


	/* Get the data values entered by the user for Shift Register. SHFRG
	Returns: (array) = An array of the new data values.
	*/
	function _GetShiftRegisterValues() {
		var valresult = [];
		var sourcestartaddr = this.docref.forms.addreditshfrg.sourcestartaddr.value;
		var sourceendaddr = this.docref.forms.addreditshfrg.sourceendaddr.value;


		// Convert to upper case and strip blanks.
		var sourcestartaddr = this.StripAndUpper(sourcestartaddr);
		valresult.push(sourcestartaddr);
		var sourceendaddr = this.StripAndUpper(sourceendaddr);
		valresult.push(sourceendaddr);

		// Update the screen representation.
		this.docref.forms.addreditshfrg.sourcestartaddr.value = sourcestartaddr;
		this.docref.forms.addreditshfrg.sourceendaddr.value = sourceendaddr;


		// Check if the parameters are OK.
		var param1ok =  /^C[0-9]+$/.test(sourcestartaddr);
		var param2ok =  /^C[0-9]+$/.test(sourceendaddr);


		// Signal if the parameters were ok.
		this.SignalParamStatus("editshfrg1a", param1ok);
		this.SignalParamStatus("editshfrg1b", param2ok);


		// Save the parameters if they were all OK.
		if (param1ok && param2ok) {
			// Update the record address.
			this.rungdata[this.CurrentCell]["addr"] = valresult;
			return true;
		} else {
			return false;
		}
	}
	this.GetShiftRegisterValues = _GetShiftRegisterValues;




	// ##################################################################
	/* Fill in the editing fields with the current data. 
	Parameters: id (string) = The id if the input or output matrix location.
	*/
	function _FillEditFields(id) {
		// Find out what type of instruction this is.
		var instype = this.rungdata[id]["value"];
		// Get the rung data.
		var rungdata = this.rungdata[id]["addr"];

		// Select the appropriate address fill function.
		switch (this.LadSymbols[instype]["addredit"]) {
		case "addresseditnone" : { break; }
		case "addreditcontact1" : { this.FillContactField(rungdata); break; }
		case "addreditcontact2" : { this.FillCompareField(rungdata); break; }
		case "addreditcoil1" : { this.FillcoilField(rungdata); break; }
		case "addreditcoil2" : { this.FillCoil2Field(rungdata); break; }
		case "addreditcall" : { this.FillCallField(rungdata); break; }
		case "addreditfor" : { this.FillForField(rungdata); break; }
		case "addreditcounter" : { this.FillCounterField(rungdata); break; }
		case "addredittimer" : { this.FillTimerField(rungdata); break; }
		case "addreditcopy" : { this.FillCopyField(rungdata); break; }
		case "addreditcpyblk" : { this.FillCopyBlockField(rungdata); break; }
		case "addreditfill" : { this.FillCopyFillField(rungdata); break; }
		case "addreditpack" : { this.FillPackField(rungdata); break; }
		case "addreditunpack" : { this.FillUnpackField(rungdata); break; }
		case "addreditfind" : { this.FillFindField(rungdata); break; }
		case "addreditmath" : { this.FillMathField(rungdata); break; }
		case "addreditsum" : { this.FillSumField(rungdata); break; }
		case "addreditshfrg" : { this.FillShiftRegisterField(rungdata); break; }
		default : { break; }

		}


		// Hide all the address edit fields.
		this.HideAddressEditFields();

		// Display the correct editing fields for this instruction type.
		var editfields = this.LadSymbols[instype]["addredit"];
		var editref = this.docref.getElementById(editfields);
		editref.setAttribute("class", "editaddrshow");


	}
	this.FillEditFields = _FillEditFields;
	


	// ##################################################################
	/* The user has entered a new or changed address for the symbol. 
	Parameters: addrtype (string) = The type of address (related to the number
		and type of input fields allowed).
	*/
	function _AddressEnter(addrtype) {

		// Select the appropriate address fill function.
		switch (addrtype) {
		case "addresseditnone" : { return; break; }
		case "addreditcontact1" : { var editresult = this.GetContactValues(); break; }
		case "addreditcontact2" : { var editresult = this.GetCompareValues(); break; }
		case "addreditcoil1" : { var editresult = this.GetcoilValues(); break; }
		case "addreditcoil2" : { var editresult = this.GetCoil2Values(); break; }
		case "addreditcall" : { var editresult = this.GetCallValues(); break; }
		case "addreditfor" : { var editresult = this.GetForValues(); break; }
		case "addreditcounter" : { var editresult = this.GetCounterValues(); break; }
		case "addredittimer" : { var editresult = this.GetTimerValues(); break; }
		case "addreditcopy" : { var editresult = this.GetCopyValues(); break; }
		case "addreditcpyblk" : { var editresult = this.GetCopyBlockValues(); break; }
		case "addreditfill" : { var editresult = this.GetCopyFillValues(); break; }
		case "addreditpack" : { var editresult = this.GetPackValues(); break; }
		case "addreditunpack" : { var editresult = this.GetUnpackValues(); break; }
		case "addreditfind" : { var editresult = this.GetFindValues(); break; }
		case "addreditmath" : { var editresult = this.GetMathValues(); break; }
		case "addreditsum" : { var editresult = this.GetSumValues(); break; }
		case "addreditshfrg" : { var editresult = this.GetShiftRegisterValues(); break; }
		default : { return; break; }

		}

		// Update the ladder matrix if the edit result is ok.
		if (editresult && this.CurrentCell) {

			// Update the display
			this.DisplayCell(this.CurrentCell);
			this.SetCellColour(this.CurrentCell, this.SelectedColour);
		}

	}
	this.AddressEnter = _AddressEnter;


	// ##################################################################
	/* Select an new cell. 
	Parameters: id (string) = The id if the new matrix location.
	*/
	function _SelectCell(id) {
		// Turn the old cell back to unselected.
		if (this.CurrentCell) {
			this.SetCellColour(this.CurrentCell, this.DeselectedColour);
		}
		// Now set the background colour of the new cell.
		this.CurrentCell = id;
		this.SetCellColour(id, this.SelectedColour);

		// Now we need to update the address data for editing.
		this.FillEditFields(id);

	}
	this.SelectCell = _SelectCell;


	// ##################################################################
	/* The user has clicked an input cell. 
	Parameters: id (string) = The id if the input matrix location the user 
		has clicked on.
	*/
	function _ClickInput(id) {
		// Select the input cell.
		this.SelectCell(id);

		// Display the appropriate edit buttons. If the correct type 
		// is already displayed, we leave it as is.
		if (this.CurrentCellType != "inputs") {
			this.ShowButtons("inputbuttons");
			this.CurrentCellType = "inputs";
		}
	}
	this.ClickInput = _ClickInput;



	// ##################################################################
	/* The user has clicked an output cell. 
	Parameters: id (string) = The id if the input matrix location the user 
		has clicked on.
	*/
	function _ClickOutput(id) {
		// Select the output cell.
		this.SelectCell(id);

		// Display the appropriate edit buttons. If the correct type 
		// is already displayed, we leave it as is.
		if (this.CurrentCellType != "outputs") {
			this.ShowButtons("outputbuttons");
			this.CurrentCellType = "outputs";
		}
	}
	this.ClickOutput = _ClickOutput;



	// ##################################################################
	/* The user has clicked a button to add an input. 
	Parameters:
		pos (string) = The instruction insertion direction (right, 
			left, etc.). This tells where the new instruction is
			to be inserted.
		inptype (string) = The code for the new instruction which is
			to be inserted. 
	*/
	function _AddInput(pos, inptype) {
		// If no input is selected, then return. 
		if (!this.CurrentCell) { return; }

		/* Get the current position. If we can't retrieve it, that will
		be because the current cell is not part of the inputs. In this case
		we just abort and ignore the request. */
		try {
			var row = this.rungdata[this.CurrentCell]["row"]; 
			var col = this.rungdata[this.CurrentCell]["col"];
		}
		catch (e) { return; }


		// Increment the cell position according to the command.
		switch (pos) {
		// Insert to the right of the current position.
		case "right" : { 
			// Check if we are at the right hand limit.
			if (col >= this.MatrixParams["maxinputcol"]) {
				return;
			} else {
				col++; 
				break; 
			}
		}
		// Insert to the left of the current position.
		case "left" : { 
			// Check if we are at the left hand limit.
			if (col <= 0) {
				return;
			} else {
				col--;
				break; 
			}
		}
		// Insert below the current position.
		case "below" : { 
			// Check if we are at the bottom.
			if (row >= this.MatrixParams["maxinputrow"]) {
				return;
			} else {
				row++; 
				break; 
			}
		}
		// Replace in the current position.
		case "replace" : break;
		}

		// Find the new cell record. We construct this using strings.
		var newcellid = "inputedit" + row + col;

		// Insert the new cell data.
		this.rungdata[newcellid]["value"] = inptype;
		this.rungdata[newcellid]["addr"] = this.DefaultAddr(inptype);

		// Display the cell.
		this.DisplayCell(newcellid);
		// Advance the current position to the new cell.
		this.SelectCell(newcellid);
		// Fix up the joining rail, if necessary.
		this.FixHRail();

	}
	this.AddInput = _AddInput;


	// ##################################################################

	/* The user has clicked a button to add an output. 
	Parameters:
		pos (string) = The instruction insertion direction (below 
			or replace). This tells where the new instruction is
			to be inserted.
		inptype (string) = The code for the new instruction which is
			to be inserted. 
	*/
	function _AddOutput(pos, outptype) {

		// Check to see if the rung type has been defined yet.
		if (this.RungType == "empty"){
			// Find out the rung type which is compatible with 
			// the selected instructions.
			var matrixtype = this.LadSymbols[outptype]["type"];
			
			// Initialise the SVG matrix (if we know the rung type).
			if (this.RungOutputTypes.indexOf(matrixtype) >= 0) {

				// Save the new rung type.
				this.RungType = matrixtype;

				// Set the appropriate matrix coordinate set.
				this.MatrixParams = this.AllMatrixParams[this.RungType];

				// Disable the edit buttons which are not valid for this
				// new rung type.
				this.MaskEditButtons(this.RungType);

				// Finish initialising the rung.
				this.InitEditMatrix();
			} else {
				return;
			}
		}

		// If no output is selected, then return. 
		if (!this.CurrentCell) { return; }


		/* Get the current position. If we can't retrieve it, that will
		be because the curren cell is not part of the outputs. In this case
		we just abort and ignore the request. */
		try {
			var row = this.rungdata[this.CurrentCell]["row"]; 
		}
		catch (e) { return; }

		// Increment the cell position according to the command.
		switch (pos) {
		// Check to see if the matrix is full.
		case "below" : {
			if (row >= this.MatrixParams["maxoutputrow"]) { 
				return; 
			} else {
				row++; 
				break; 
			}
		}
		case "replace" : break;
		}


		// Find the new cell record. We construct this using strings.
		var cellid = "outputedit" + row;

		// Insert the new cell data.
		this.rungdata[cellid]["value"] = outptype;
		this.rungdata[cellid]["addr"] = this.DefaultAddr(outptype);

		// Display the cell.
		this.DisplayCell(cellid);
		// Advance the current position to the new cell.
		this.SelectCell(cellid);
		// Fix up the joining rail, if necessary.
		this.FixVRail();
	}
	this.AddOutput = _AddOutput;


	// ==================================================================


	// ##################################################################
	/* Returns true if the specified row is full.
	Parameters: row (integer) = The input row number in question.
	Returns: (boolean) = true if the row is full.
	*/
	function _RowIsFull(row) {
		return !this.CellIsEmpty("inputedit" + row + this.MatrixParams["maxinputcol"]);
	}
	this.RowIsFull = _RowIsFull;


	/* Returns true if the specified column is full.
	Parameters: col (integer) = The input column number in question.
	Returns: (boolean) = true if the column is full.
	*/
	function _ColIsFull(col) {
		return !this.CellIsEmpty("inputedit" + this.MatrixParams["maxinputrow"] + col);
	}
	this.ColIsFull = _ColIsFull;


	// ##################################################################
	/* Return true of the specified matrix cell is an input cell.
	Parameters: cellid (string) = The id of the cell to be checked.
	Returns: (boolean) = True if the cell is an input cell.
	*/
	function _IsInputCell(cellid) {
		return this.rungdata[cellid]["type"] == "inputs"	
	}
	this.IsInputCell = _IsInputCell;


	// ##################################################################
	/* Shift the existing inputs right one position in the specified row. 
	Parameters: row, col (integer) = The input matrix row and column numbers 
		which is to be shifted right.
	*/
	function _ShiftInputsRight(row, col) {

		// Now go through the row and move everything right one column.
		for (var i = (this.MatrixParams["maxinputcol"]); i > col; i--) {
			//  Construct the current cell id using a string.
			var currentcellid = "inputedit" + row + i;
			
			//  Construct the id for the cell to the left of it.
			var prevcellid = "inputedit" + row + (i - 1);

			// Copy the individual cell record over.
			this.CopyCellData(prevcellid, currentcellid);

			// Display it.
			this.DisplayCell(currentcellid);
		}
		// Delete the old cell contents to leave an empty cell.
		var currentid = "inputedit" + row + col;
		this.DeleteCell(currentid);
		// Display it.
		this.DisplayCell(currentid);
	}
	this.ShiftInputsRight = _ShiftInputsRight;

	// ##################################################################
	/* Shift the existing inputs left one position in the specified row. 
	Parameters: row, col (integer) = The input matrix row and column numbers 
		which is to be shifted left.
	*/
	function _ShiftInputsLeft(row, col) {

		// Now go through the row and move everything left one column.
		for (var i = col; i < this.MatrixParams["maxinputcol"]; i++) {
			//  Construct the current cell id using a string.
			var currentcellid = "inputedit" + row + i;
			
			//  Construct the id for the cell to the right of it.
			var nextcellid = "inputedit" + row + (i + 1);

			// Copy the individual cell record over.
			this.CopyCellData(nextcellid, currentcellid);

			// Display the new cells.
			this.DisplayCell(currentcellid);
			this.DisplayCell(nextcellid);
		}
		// Delete the rightmost cell contents to leave an empty cell.
		var currentid = "inputedit" + row + this.MatrixParams["maxinputcol"];
		this.DeleteCell(currentid);
		// Display it.
		this.DisplayCell(currentid);
	}
	this.ShiftInputsLeft = _ShiftInputsLeft;



	// ##################################################################
	/* Shift the existing inputs down one position in the specified column. 
	Parameters: row, col (integer) = The input matrix row and column numbers 
		which is to be shifted down.
	*/
	function _ShiftInputsDown(row, col) {

		// Now go through the column and move everything down one.
		for (var i = (this.MatrixParams["maxinputrow"]); i > row; i--) {
			//  Construct the current cell id using a string.
			var currentcellid = "inputedit" + i + col;
			
			//  Construct the id for the cell above it.
			var prevcellid = "inputedit" + (i - 1) + col;

			// Copy the individual cell record over.
			this.CopyCellData(prevcellid, currentcellid);

			// Display it.
			this.DisplayCell(currentcellid);
			this.SetCellColour(currentcellid, this.DeselectedColour);
		}
		// Delete the old cell contents to leave an empty cell.
		var currentid = "inputedit" + row + col;
		this.DeleteCell(currentid);
		// Display it.
		this.DisplayCell(currentid);

	}
	this.ShiftInputsDown = _ShiftInputsDown;


	// ##################################################################
	/* Shift the existing inputs up one position in the specified column. 
	Parameters: row, col (integer) = The input matrix row and column numbers 
		which is to be shifted up.
	*/
	function _ShiftInputsUp(row, col) {

		// Now go through the column and move everything up one.
		for (var i = row; i < this.MatrixParams["maxinputrow"]; i++) {
			//  Construct the current cell id using a string.
			var currentcellid = "inputedit" + i + col;
			
			//  Construct the id for the cell below it.
			var nextcellid = "inputedit" + (i + 1) + col;

			// Copy the individual cell record over.
			this.CopyCellData(nextcellid, currentcellid);

			// Display it.
			this.DisplayCell(currentcellid);
			this.SetCellColour(currentcellid, this.DeselectedColour);
		}
		// Delete the bottom row cell contents to leave an empty cell.
		var currentid = "inputedit" + this.MatrixParams["maxinputrow"] + col;
		this.DeleteCell(currentid);
		// Display it.
		this.DisplayCell(currentid);

	}
	this.ShiftInputsUp = _ShiftInputsUp;


	// ##################################################################
	/* Delete a single input cell (the current cell) without affecting 
	the adjoining cells.
	*/
	function _DeleteInputCell() {
		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Delete the current cell data.
		this.DeleteCell(cellid);
		// Display the new cell contents (empty).
		this.DisplayCell(cellid);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();
	}
	this.DeleteInputCell = _DeleteInputCell;


	// ##################################################################
	/* Insert a new (empty) cell in an existing input row. This shifts all 
		the matrix cells to the left of the current position on the 
		current row one position to the right. 
	*/
	function _InsertInputCell() {
		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Row and column of current cell.
		var row = this.rungdata[cellid]["row"]
		var col = this.rungdata[cellid]["col"]

		// Check to see if the row is already full.
		if (this.RowIsFull(row)) {
			return;
		}

		// Shift the existing cells to the right.
		this.ShiftInputsRight(row, col);

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();

	}
	this.InsertInputCell = _InsertInputCell;
	

	// ##################################################################
	/* Insert the current cell from an existing input row. This shifts all 
		the matrix cells to the right of the current position on the 
		current row one position to the left. 
	*/
	function _RemoveInputCell() {
		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Row and column of current cell.
		var row = this.rungdata[cellid]["row"]
		var col = this.rungdata[cellid]["col"]

		// Shift the existing cells to the left.
		this.ShiftInputsLeft(row, col);

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();

	}
	this.RemoveInputCell = _RemoveInputCell;
	


	// ##################################################################
	/* Insert a new row of cells in the inputs by shifting the existing 
		input rows down one position below the current cell.
	*/
	function _InsertInputRow() {

		// Get the current cell position.
		var cellid = this.CurrentCell;
		// Look up what row the requested cell is on.
		var row = this.rungdata[cellid]["row"];

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Make sure this isn't the last row.
		if ((row >= this.MatrixParams["maxinputrow"])) {
			return;
		}

		// Check to see if the last input row (all columns) is empty.
		for (var i=0; i <= this.MatrixParams["maxinputcol"]; i++) {
			if (this.ColIsFull(i)) {
				return;
			}
		}


		// Go through each column and move everything down one.
		for (var i = 0; i < this.MatrixParams["maxinputcol"]; i++) {
			this.ShiftInputsDown(row, i);
		}

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();
	}
	this.InsertInputRow = _InsertInputRow;


	// ##################################################################
	/* Remove a new row of cells in the inputs by shifting the existing 
		input rows up one position from the current cell.
	*/
	function _RemoveInputRow() {

		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}


		// Look up what row the requested cell is on.
		var row = this.rungdata[cellid]["row"];

		// Go through each column and move everything up one.
		for (var i = 0; i < this.MatrixParams["maxinputcol"]; i++) {
			this.ShiftInputsUp(row, i);
		}

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();
	}
	this.RemoveInputRow = _RemoveInputRow;


	// ##################################################################
	/* Insert a new column of cells in the inputs by shifting the existing 
		input columns right one position from the current cell.
	*/
	function _InsertInputCol() {

		// Get the current cell position.
		var cellid = this.CurrentCell;
		// Look up what column the requested cell is in.
		var col = this.rungdata[cellid]["col"];


		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Make sure this isn't the last column.
		if ((col >= this.MatrixParams["maxinputcol"])) {
			return;
		}

		// Check to see if the last input column (all rows) is empty.
		for (var i=0; i <= this.MatrixParams["maxinputrow"]; i++) {
			if (this.RowIsFull(i)) {
				return;
			}
		}

		// Go through each row and move everything right one.
		for (var i = 0; i <= this.MatrixParams["maxinputrow"]; i++) {
			this.ShiftInputsRight(i, col);
		}

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();
	}
	this.InsertInputCol = _InsertInputCol;



	// ##################################################################
	/* Remove the current column of cells in the inputs by shifting the existing 
		input columns left one position from the current cell.
	*/
	function _RemoveInputCol() {

		// Get the current cell position.
		var cellid = this.CurrentCell;
		// Look up what column the requested cell is in.
		var col = this.rungdata[cellid]["col"];

		// Make sure this is an input cell.
		if (!this.IsInputCell(cellid)) {
			return;
		}

		// Go through each row and move everything left one.
		for (var i = 0; i <= this.MatrixParams["maxinputrow"]; i++) {
			this.ShiftInputsLeft(i, col);
		}

		// Redisplay the background colour for the current cell.
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixHRail();
	}
	this.RemoveInputCol = _RemoveInputCol;

	// ==================================================================

	// ##################################################################
	/* Return true of the specified matrix cell is an output cell.
	Parameters: cellid (string) = The id of the cell to be checked.
	Returns: (boolean) = True if the cell is an output cell.
	*/
	function _IsOutputCell(cellid) {
		return this.rungdata[cellid]["type"] == "outputs"	
	}
	this.IsOutputCell = _IsOutputCell;



	// ##################################################################
	/* Insert a new cell in the outputs by shifting the existing outputs 
		down one position below the current cell. 
	*/
	function _InsertOutputRow() {

		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Look up what row the requested cell is on.
		var row = this.rungdata[cellid]["row"];

		// Make sure it is an output
		if (!this.IsOutputCell(cellid)) {
			return;
		}

		// Make sure this isn't the last row.
		if (row >= this.MatrixParams["maxoutputrow"]) {
			return;
		}

		// Make sure the bottom row isn't already full.
		if (!this.CellIsEmpty("outputedit" + this.MatrixParams["maxoutputrow"])) {
			return;
		}


		// Now go through the column and move everything down one.
		for (var i = this.MatrixParams["maxoutputrow"]; i > row; i--) {
			//  Construct the current cell id using a string.
			var currentcellid = "outputedit" + i;
			
			//  Construct the id for the cell above it.
			var prevcellid = "outputedit" + (i - 1);

			// Copy the individual cell record over.
			this.CopyCellData(prevcellid, currentcellid);

			// Display it.
			this.DisplayCell(currentcellid);
			this.SetCellColour(currentcellid, this.DeselectedColour);
		}

		// Delete the inserted cell data.
		this.DeleteCell(cellid);
		// Display the new cell contents (empty).
		this.DisplayCell(cellid);
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixVRail();
	}
	this.InsertOutputRow = _InsertOutputRow;

	// ##################################################################
	/* Delete the current cell in the outputs and shift the remaining 
		outputs up one position. 
	*/
	function _DeleteOutputRow() {

		// Get the current cell position.
		var cellid = this.CurrentCell;

		// Make sure it is an output
		if (!this.IsOutputCell(cellid)) {
			return;
		}

		// Look up what row the requested cell is on.
		var row = this.rungdata[cellid]["row"];

		//  This is initialised to handle cases where we are deleting 
		// the bottom row.
		var prevcellid = "outputedit" + row;

		// Now go through the column and move everything up one.
		for (var i = row; i < this.MatrixParams["maxoutputrow"]; i++) {

			//  Construct the current cell id using a string.
			var currentcellid = "outputedit" + i;
			
			//  Construct the id for the cell below it.
			var prevcellid = "outputedit" + (i + 1);

			// Copy the individual cell record over.
			this.CopyCellData(prevcellid, currentcellid);

			// Display it.
			this.DisplayCell(currentcellid);
			this.SetCellColour(currentcellid, this.DeselectedColour);
		}

		// Delete the final cell data.
		this.DeleteCell(prevcellid);
		// Display the deleted cell contents (empty).
		this.DisplayCell(prevcellid);
		this.SetCellColour(cellid, this.SelectedColour);
		// Now we need to update the address data for editing.
		this.FillEditFields(cellid);

		// Fix up the joining rail, if necessary.
		this.FixVRail();

	}
	this.DeleteOutputRow = _DeleteOutputRow;

	// ==================================================================

	// Rung comment editing.

	// ##################################################################
	/* Replace any existing comments with a new comment.
	Parameters: commenttext (string) = The comment to display.
	*/
	function _DisplayRungComment(commenttext) {

		// If there are any existing elements, remove them first.
		if (this.RungCommentDisplayField.hasChildNodes()) {
			while (this.RungCommentDisplayField.firstChild) {
				this.RungCommentDisplayField.removeChild(this.RungCommentDisplayField.firstChild);
			}
		} 

		// Add the new comments.
		var commentvalue = this.docref.createTextNode(commenttext);
		this.RungCommentDisplayField.appendChild(commentvalue);
		
	}
	this.DisplayRungComment = _DisplayRungComment;


	
	// ##################################################################
	/* The user has entered a new or changed comment for the rung. 
	*/
	function _RungCommentEnter() {
		// Get the new comment.
		this.RungComment = this.RungCommentEdit.value;

		// Update the display.
		this.DisplayRungComment(this.RungComment);
	}
	this.RungCommentEnter = _RungCommentEnter;


	// ##################################################################
	/* Return the current comment value.
	*/
	function _GetComment() {
		return this.RungComment;
	}
	this.GetComment = _GetComment;


	// ##################################################################
	/* Restore the original rung comment value.
	*/
	function _RestoreComment() {
		// Update the display.
		this.DisplayRungComment(this.OriginalRungComment);
	}
	this.RestoreComment = _RestoreComment;

	// ==================================================================

	// ##################################################################
	/* Return the current rung type.
	*/
	function _GetRungType() {
		return this.RungType;
	}
	this.GetRungType = _GetRungType;


	// ==================================================================

	// IL Editing.

	// ##################################################################
	/* Return the current IL data from the IL editor as a list.
	*/
	function _GetILData() {
			// Fill the IL editor with the IL data.
		var newil = this.docref.forms.ileditor.ilcontent.value;
		return newil.split("\n");
	}
	this.GetILData = _GetILData;


} // end of LadderEditor.


// ##################################################################

