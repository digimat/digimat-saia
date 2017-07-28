/** ##########################################################################
# Project: 	MBLogic
# Module: 	ladsubrdata.js
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


function LadSubrData() {

	// This is the master record for all the subroutine data.
	this.SubrData = {
		"subrname" : "",	// Name of subroutine.
		"subrcomments" : "",	// Subroutine comments.
		"signature" : 0,	// Hash of subroutine to detect changes.
		"subrdata" : []		// The rung data.
	}

	/* This is a master copy of a single rung data record.
	matrixdata = The data matrix. This keys must be "inputedit00" to "inputedit77",
		or "outputedit0" to "outputedit7". Each of these must be a record with
		the value and address. E.g. {"value" : "noc", "addr" : ["X1"]}
	rungtype = The type of rung. Must be "single", "double", "triple", or "empty".
	comment = The rung comment.
	*/
	this.RungDataRecord = {
		"matrixdata" : {},
		"ildata" : [],
		"rungtype" : "empty",
		"comment" : "",
		"reference": -1
	}

	// List of currently valid rung numbers in order.
	this.RungNumberList = [];

	// Reference number for creating unique rung ids.
	// We can't use the rung number for web page ids, because as we add
	// and remove rungs we can't go back and renumber existing ids. This means
	// the id and the rung number will not necessarily be the same if we have
	// deleted any rungs.
	this.RungReference = 0;


	// This indexes rung data by reference number.
	this.RungRefIndex = {};


	// This provides a list of the instructions that are to be monitored.
	this.MonitorList = [];
	// This is a list of the addresses to read from the server.
	this.MonitorAddrList = [];
	// This is the subroutine signature (hash) which is used to detect changes
	// in the subroutine on the server.
	this.Signature = "";

	// ==================================================================
	// ##################################################################
	/* Import the rung matrix data for a single rung matrix. This imports
	the data from the server. 
	Parameters: rungmatrix (list) = This is a list of objects, where each list
		element defines the characteristics of a ladder matrix cell.
		rungref (integer) = The rung reference number. 
	Return: (object) = An object which has been reformatted to include all the
		original data, but with the addition of keys which match the web
		page SVG matrix cell ids.
	*/
	function _ImportRungMatrix(rungmatrix, rungref) {

		var matrixkeys = {"inp" : "inputedit", "outp" : "outputedit"}
		var matrixoutput = {};
		// We keep track of the maximum rows and columns so we can check if
		// the data passed in exceeds the limits of the ladder editor.
		var maxinprow = 0;
		var maxinpcol = 0;
		var maxoutprow = 0;
		var idref = 0;
		for (var i in rungmatrix) {
			var cell = rungmatrix[i];
			// The key tag is the matrix cell id in the web page.
			if (cell["type"] == "inp") {
				var keytag = matrixkeys[cell["type"]] + cell["row"] + "" + cell["col"];
				// Find maximum row and column.
				if (cell["row"] > maxinprow) {
					var maxinprow = cell["row"]
				}
				if (cell["col"] > maxinpcol) {
					var maxinpcol = cell["col"]
				}
			} else {
				var keytag = matrixkeys[cell["type"]] + cell["row"];
				// Find maximum row. We don't have columns for outputs.
				if (cell["row"] > maxoutprow) {
					var maxoutprow = cell["row"]
				}
			}
			
			// Create an "id" tag for monitoring the live data.
			if (cell["monitor"][0] != "none") {
				// Create the id tag name for this instruction.
				var monitortag = "MB_Monitor_" + rungref + "_" + idref;
				idref++;

				// Add the addresses to the list to read from the server.
				this.MonitorAddrList.push(cell["monitor"][1]);
				// Check if there is a second address.
				if (cell["monitor"].length > 2) {
					this.MonitorAddrList.push(cell["monitor"][2]);
				}
				
				// Save the id tag and how it is supposed to be monitored.
				this.MonitorList.push({"id" : monitortag, 
						"monitor" : cell["monitor"]});

			} else {
				// We don't monitor this instruction. 
				var monitortag = "none"
			}

			// Reformat the matrix data.
			matrixoutput[keytag] = {"type" : cell["type"],
					"row" : cell["row"],  
					"col" : cell["col"],
					"addr" : cell["addr"],
					"value" : cell["value"],
					"monitortag" : monitortag};
		}

		return {"matrixdata" : matrixoutput, "maxinprow" : maxinprow, 
			"maxinpcol" : maxinpcol, "maxoutprow" : maxoutprow};

	}
	this.ImportRungMatrix = _ImportRungMatrix;



	// ##################################################################
	/* Remove duplicates from the monitored addresses from the subroutine data. This
	list of addresses is extracted from the ladder matrix. The contents are
	*not* all guaranteed to be valid addresses. 
	*/
	function _ProcessAddrList() {
		// Sort the array.
		this.MonitorAddrList.sort();

		// Remove the duplicates.
		var addlist = [];
		var lastaddr = "";
		for (var i in this.MonitorAddrList) {
			var nextaddr = this.MonitorAddrList[i];
			if (nextaddr != lastaddr) {
				addlist.push(nextaddr);
			}
		}

		// Save the new address list.
		this.MonitorAddrList = addlist;
	}
	this.ProcessAddrList = _ProcessAddrList;



	// ##################################################################
	/* Import initialised data.
	*/
	function _ImportData(subrdata) {

		// Reset the monitoring lists to accept new data.
		this.MonitorAddrList = [];
		this.MonitorList = [];

		this.SubrData["subrname"] = subrdata["subrname"];
		this.SubrData["subrcomments"] = subrdata["subrcomments"];
		this.Signature = subrdata["signature"];
		// This has to be reset in case we reload the data while running.
		this.SubrData["subrdata"] = [];

		var rungs = subrdata["subrdata"];
		for (var i=0; i<rungs.length; i++) {
			// Reformat the matrix data.
			var matrixresult = this.ImportRungMatrix(rungs[i]["matrixdata"], this.RungReference)
			// Check if the number of input columns or rows, or outputs exceeds
			// what the editor can handle.
			if ((rungs[i]["rungtype"] != "il") && 
					((matrixresult["maxinprow"] > 7) || 
					(matrixresult["maxinpcol"] > 7) || 
					(matrixresult["maxoutprow"] > 7))) {
				var rungtype = "il";
				var matrixdata = {};
			} else {
				var rungtype = rungs[i]["rungtype"];
				var matrixdata = matrixresult["matrixdata"];
			}

			this.SubrData["subrdata"].push(
				{"matrixdata" : matrixdata,
				"ildata" : rungs[i]["ildata"],
				"rungtype" : rungtype,
				"comment" : rungs[i]["comment"],
				"reference": this.RungReference
				});
			// Update the reference number index.
			this.RungRefIndex[this.RungReference] = i;
			// Increment the rung reference number.
			this.RungReference++;
		}

		// Process the address list to remove duplicates.
		this.ProcessAddrList();

	}
	this.ImportData = _ImportData;


	// ==================================================================

	// ##################################################################
	/* Export the rung matrix data for a single rung matrix. This exports
	the data to the server. 
	Parameters: rungmatrix (list) = This is a list of objects, where each list
		element defines the characteristics of a ladder matrix cell.
	Return: (object) = An object which has been reformatted to include all the
		original data, but with the addition of keys which match the web
		page SVG matrix cell ids.
	*/
	function ExportRungMatrix(rungmatrix) {
		var matrixkeys = {"inp" : "inputedit", "outp" : "outputedit"}
		var matrixdata = [];

		// Get all the inputs by going through all the possible rows and columns.
		for (var row = 0; row < 8; row++) {
			var rowname = "inputedit" + row;
			for (var col = 0; col < 8; col++) {
				var cellname = rowname + col;
				// Only cells that have data will exist. 
				if (cellname in rungmatrix) {
					var cell = rungmatrix[cellname];
					matrixdata.push({"addr": cell["addr"], "value": cell["value"], 
							"type": "inp", "row": row, "col": col});
				}
			}
		}


		// Get all the outputs by going through all the possible rows.
		for (var row = 0; row < 8; row++) {
			var cellname = "outputedit" + row;
			// Only cells that have data will exist. 
			if (cellname in rungmatrix) {
				var cell = rungmatrix[cellname];
				matrixdata.push({"addr": cell["addr"], "value": cell["value"], 
						"type": "outp", "row": row, "col": 0});
			}
		}

		return matrixdata;
	}


	// ##################################################################
	/* Export data to server.
	*/
	function _ExportData() {
		var exportdata = {};
		exportdata["subrname"] = this.SubrData["subrname"];
		exportdata["subrcomments"] = this.SubrData["subrcomments"];
		exportdata["signature"] = 0;	// We aren't actually using this at this time.
		exportdata["subrdata"] = [];

		var subrdata = [];

		var rungs = this.SubrData["subrdata"];
		for (var i=0; i < rungs.length; i++) {
			// Reformat the matrix data.
			var matrixresult = ExportRungMatrix(rungs[i]["matrixdata"]);
			subrdata.push({"comment" : rungs[i]["comment"], "ildata" : rungs[i]["ildata"], 
				"rungtype" : rungs[i]["rungtype"], "matrixdata": matrixresult});
		}
		exportdata["subrdata"] = subrdata;

		return exportdata;
		
	}
	this.ExportData = _ExportData;



	// ##################################################################
	/* Return the list of monitored addresses from the subroutine data. 
	The contents are *not* all guaranteed to be valid addresses. 
	*/
	function _GetMonitorAddrList() {
		return this.MonitorAddrList;
	}
	this.GetMonitorAddrList = _GetMonitorAddrList;



	// ##################################################################
	/* Return the object reference to the data for the monitored addresses 
	from the subroutine data. 
	*/
	function _GetMonitorDataList() {
		return this.MonitorList;
	}
	this.GetMonitorDataList = _GetMonitorDataList;



	// ##################################################################
	/* Return the original subroutine signature that was sent from the server
	with the original ladder data. 
	*/
	function _GetSignature() {
		return this.Signature;
	}
	this.GetSignature = _GetSignature;


	// ==================================================================





	// ##################################################################
	/* Calculate the maximum rung index. This starts from *zero*, not one.
	*/
	function _CalcMaxRungIndex() {
		return this.MaxRung = this.SubrData["subrdata"].length - 1;
	}
	this.CalcMaxRungIndex = _CalcMaxRungIndex;

	// ##################################################################
	/* Get the rung number, given an id reference number.
	*/
	function _FindRungNumber(rungref) {
		return this.RungRefIndex[rungref];
	}
	this.FindRungNumber = _FindRungNumber;


	// ##################################################################
	/* Append an empty rung to the end of the rung data.
	*/
	function _AppendEmptyRungRecord() {
		// Increment the id reference number.
		this.RungReference++;
		this.SubrData["subrdata"].push({"matrixdata" : {},
						"ildata" : [],
						"rungtype" : "empty",
						"comment" : "",
						"reference": this.RungReference
						});
		
		var newrung = this.CalcMaxRungIndex();
		// Update the rung reference number index.
		this.RungRefIndex[this.RungReference] = newrung;
	}
	this.AppendEmptyRungRecord = _AppendEmptyRungRecord;


	// ##################################################################
	/* Insert an empty rung above the specified rung position.
	Parameters: rungref (integers) = The rung reference number (not the actual
		rung number.
	Returns: (integer) = The new rung reference number.
	*/
	function _InsertEmptyRungRecord(rungref) {

		// Get the rung number so we know the position. 
		var rungnumber = this.RungRefIndex[rungref];

		// Increment the id reference number.
		this.RungReference++;

		// Insert the record.
		this.SubrData["subrdata"].splice(rungnumber, 0, 
						{"matrixdata" : {},
						"ildata" : [],
						"rungtype" : "empty",
						"comment" : "",
						"reference": this.RungReference
						});

		// Rebuild the rung reference number index.
		this.RebuildRefIndex();

		return this.RungReference;
	}
	this.InsertEmptyRungRecord = _InsertEmptyRungRecord;


	// ##################################################################
	/* Rebuild the rung reference number index.
	*/
	function _RebuildRefIndex() {
		this.RungRefIndex = {};
		for (var i=0; i < this.SubrData["subrdata"].length; i++) {
			var refnum = this.SubrData["subrdata"][i]["reference"];
			this.RungRefIndex[refnum] = i;
		}
	}
	this.RebuildRefIndex = _RebuildRefIndex;

	// ##################################################################
	/* Delete a record.
	Parameters: rungref (integers) = The rung reference number (not the actual
		rung number.
	*/
	function _DeleteRungRecord(rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		// Erase the rung record.
		this.SubrData["subrdata"].splice(rungnumber, 1);
		// Rebuild the rung reference number index.
		this.RebuildRefIndex();
	}
	this.DeleteRungRecord = _DeleteRungRecord;



	// ##################################################################
	/* Set the subroutine name.
	Parameters: comments (string) = The subroutine comments.
	*/
	function _SetSubroutineComments(comments) {
		this.SubrData["subrcomments"] = comments;
	}
	this.SetSubroutineComments = _SetSubroutineComments;


	// ==================================================================


	// ##################################################################
	/* Return the complete set of subroutine data.
	*/
	function _GetSubrData() {
		return this.SubrData;
	}
	this.GetSubrData = _GetSubrData;


	// ##################################################################



	// ==================================================================


	// ##################################################################
	/* Convert an actual rung into a rung reference number.
	Parameters: rungnumber (integer) = The rung number (not the reference number.
	Returns: (integer) = The rung reference number.
	*/
	function _GetRungReference(rungnumber) {
		return this.SubrData["subrdata"][rungnumber]["reference"];
	}
	this.GetRungReference = _GetRungReference;

	// ##################################################################
	/* Return an ordered list (array) of rung references, where the index
	of each rung reference corresponds to the rung number (minus one) as 
	viewed on the web page. 
	Returns: (array) = An array of rung reference integers.
	*/
	function _GetRungRefList() {
		var rungreflist = [];
		for (var i=0; i<this.SubrData["subrdata"].length; i++) {
			rungreflist.push(this.SubrData["subrdata"][i]["reference"]);
		}
		return rungreflist;
	}
	this.GetRungRefList = _GetRungRefList;



	// ##################################################################
	/* Return a single rung data record.
	Parameters: rungref (integer) = The rung reference number (not the
		rung number). 
	*/
	function _GetRungData(rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		return this.SubrData["subrdata"][rungnumber];
	}
	this.GetRungData = _GetRungData;


	// ##################################################################
	/* Set the matrix data for a single rung data record.
	Parameters: matrix (object) = The instruction matrix data for a rung.
		rungref (integer) = The rung reference number (not the
				rung number). 
	*/
	function _SetRungMatrix(matrix, rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		this.SubrData["subrdata"][rungnumber]["matrixdata"] = matrix;
	}
	this.SetRungMatrix = _SetRungMatrix;

	// ##################################################################
	/* Set the IL data for a single rung data record.
	Parameters: ildata (list) = The IL list data for a rung.
		rungref (integer) = The rung reference number (not the
				rung number). 
	*/
	function _SetRungIL(ildata, rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		this.SubrData["subrdata"][rungnumber]["ildata"] = ildata;
	}
	this.SetRungIL = _SetRungIL;


	// ##################################################################
	/* Set the IL data for a single rung data record.
	Parameters: rungref (integer) = The rung reference number (not the
				rung number). 
		ildata (list) = The IL list data for a rung.
	*/
	function _GetRungIL(rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		return this.SubrData["subrdata"][rungnumber]["ildata"];
	}
	this.GetRungIL = _GetRungIL;


	// ##################################################################
	/* Set the comments for a single rung data record.
	Parameters: comment (string) = The comment string for a rung.
		rungref (integer) = The rung reference number (not the
				rung number). 
	*/
	function _SetRungComment(comment, rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		return this.SubrData["subrdata"][rungnumber]["comment"] = comment;
	}
	this.SetRungComment = _SetRungComment;

	// ##################################################################
	/* Set the rung type for a single rung data record.
	Parameters: rungtype (string) = The rung type for a rung.
		rungref (integer) = The rung reference number (not the
				rung number). 
	*/
	function _SetRungType(rungtype, rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		this.SubrData["subrdata"][rungnumber]["rungtype"] = rungtype;
	}
	this.SetRungType = _SetRungType;


	// ##################################################################
	/* Get the rung type for a single rung data record.
	Parameters: rungref (integer) = The rung reference number (not the
				rung number). 
	Returns: (string) = The rung type for a rung.
	*/
	function _GetRungType(rungref) {
		var rungnumber = this.RungRefIndex[rungref];
		return this.SubrData["subrdata"][rungnumber]["rungtype"];
	}
	this.GetRungType = _GetRungType;

}



// ##################################################################


