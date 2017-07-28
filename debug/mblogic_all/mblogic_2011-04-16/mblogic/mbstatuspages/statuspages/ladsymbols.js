/** ##########################################################################
# Project: 	MBLogic
# Module: 	ladsymbols.js
# Purpose: 	MBLogic ladder editor library.
# Language:	javascript
# Date:		17-Mar-2010.
# Ver:		14-May-2010
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

/*
*/
function LadSymDefs(docref) {


	this.docref = docref;

	// These are used for displaying address in SVG.
	this.inptext1 = [this.docref.getElementById("inptext1")];
	this.inptext2 = [this.docref.getElementById("inptext2a"), this.docref.getElementById("inptext2b")];
	this.coiltext2 = [this.docref.getElementById("coiltext2a"), this.docref.getElementById("coiltext2b")];
	this.timertext1 = [this.docref.getElementById("timertext1a"), 
				this.docref.getElementById("timertext1b"),
				this.docref.getElementById("timertext1c")];
	this.findtext = [this.docref.getElementById("findtext1a"), this.docref.getElementById("findtext1b"),
			this.docref.getElementById("findtext1c"), this.docref.getElementById("findtext1d"),
			this.docref.getElementById("findtext1e"), this.docref.getElementById("findtext1f")];
	this.mathtext = [this.docref.getElementById("mathtext1a"), 
				this.docref.getElementById("mathtext1b"), 
				this.docref.getElementById("mathtext1c")];
	this.sumtext = [this.docref.getElementById("sumtext1a"), 
				this.docref.getElementById("sumtext1b"), 
				this.docref.getElementById("sumtext1c"),
				this.docref.getElementById("sumtext1d")];

	
	// This is the complete list of all the ids for the address edit forms. 
	this.addresseditgroups = ["addresseditnone", "addreditcontact1", "addreditcontact2", 
				"addreditcoil1", "addreditcoil2", "addreditcall", 
				"addreditfor", "addreditcounter", "addredittimer",    
				"addreditcopy", "addreditcpyblk", "addreditfill", 
				"addreditpack", "addreditunpack", "addreditfind", 
				"addreditmath", "addreditsum", "addreditshfrg"];


	// Default addresses for FIND instructions.
	this.FindDefaults = ["1", "DS9998", "DS9999", "DS10000", "C2000", "0"];



	// ==================================================================

	/* This converts the ladder symbol names used in the data matrix
		to the names used in the page SVG. 
	symbolref: (ref) = reference to SVG ladder symbol. 
	addredit: (string) =  Type of address edting to use. This is used in a switch
		statement in labeditlib.js to select the correct code, and it is also
		the id of the div in the web page for hide/show.
	addrref: (ref) = List of references to address display fields.
	defaultaddr: (list of strings) = List of default address when adding instructions.
	type: (string) = Instruction type.
	*/
	this.LadSymbols = {
		// Empty cell.
		"none" : {"symbolref" : this.docref.getElementById("none"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "none"},

		// Input contacts.
		"noc" : {"symbolref" : this.docref.getElementById("inputno"),
				"addredit" : "addreditcontact1", 
				"addrref" : this.inptext1,
				"defaultaddr" : ["C2000"],
				"type" : "input"},
		"ncc" : {"symbolref" : this.docref.getElementById("inputnc"),
				"addredit" : "addreditcontact1", 
				"addrref" : this.inptext1,
				"defaultaddr" : ["C2000"],
				"type" : "input"},
		"nocpd" : {"symbolref" : this.docref.getElementById("inputnopd"),
				"addredit" : "addreditcontact1", 
				"addrref" : this.inptext1,
				"defaultaddr" : ["C2000"],
				"type" : "input"},
		"nocnd" : {"symbolref" : this.docref.getElementById("inputnond"),
				"addredit" : "addreditcontact1", 
				"addrref" : this.inptext1,
				"defaultaddr" : ["C2000"],
				"type" : "input"},

		// Compare contacts.
		"compeq" : {"symbolref" : this.docref.getElementById("inputcompeq"),
				"addredit" : "addreditcontact2", 
				"defaultaddr" : ["DS10000", "DS10000"],
				"addrref" : this.inptext2,
				"type" : "input"},
		"compneq" : {"symbolref" : this.docref.getElementById("inputcompneq"),
				"addredit" : "addreditcontact2",  
				"defaultaddr" : ["DS10000", "DS10000"],
				 "addrref" : this.inptext2,
				"type" : "input"},
		"compgt" : {"symbolref" : this.docref.getElementById("inputcompgt"),
				"addredit" : "addreditcontact2",  
				"defaultaddr" : ["DS10000", "DS10000"],
				"addrref" : this.inptext2,
				"type" : "input"},
		"complt" : {"symbolref" : this.docref.getElementById("inputcomplt"),
				"addredit" : "addreditcontact2",  
				"defaultaddr" : ["DS10000", "DS10000"],
				"addrref" : this.inptext2,
				"type" : "input"},
		"compge" : {"symbolref" : this.docref.getElementById("inputcompge"),
				"addredit" : "addreditcontact2",  
				"defaultaddr" : ["DS10000", "DS10000"],
				"addrref" : this.inptext2,
				"type" : "input"},
		"comple" : {"symbolref" : this.docref.getElementById("inputcomple"),
				"addredit" : "addreditcontact2",  
				"defaultaddr" : ["DS10000", "DS10000"],
				"addrref" : this.inptext2,
				"type" : "input"},


		// Input branches.
		"branchttl" : {"symbolref" : this.docref.getElementById("branchttl"),
				"addredit" : "addresseditnone",  
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"branchttr" : {"symbolref" : this.docref.getElementById("branchttr"),
				"addredit" : "addresseditnone",  
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"branchl" : {"symbolref" : this.docref.getElementById("branchl"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"branchr" : {"symbolref" : this.docref.getElementById("branchr"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"branchtl" : {"symbolref" : this.docref.getElementById("branchtl"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"branchtr" : {"symbolref" : this.docref.getElementById("branchtr"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"vbarr" : {"symbolref" : this.docref.getElementById("vbarr"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"vbarl" : {"symbolref" : this.docref.getElementById("vbarl"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},
		"hbar" : {"symbolref" : this.docref.getElementById("hbar"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "input"},

		// Coil outputs with single addresses.
		"out" : {"symbolref" : this.docref.getElementById("outputout"),
				"addredit" : "addreditcoil1",
				"defaultaddr" : ["C2000"],
				"addrref" : this.inptext1,
				"type" : "single"},
		"set" : {"symbolref" : this.docref.getElementById("outputset"),
				"addredit" : "addreditcoil1",
				"defaultaddr" : ["C2000"],
				"addrref" : this.inptext1,
				"type" : "single"},
		"rst" : {"symbolref" : this.docref.getElementById("outputreset"),
				"addredit" : "addreditcoil1",
				"defaultaddr" : ["C2000"],
				"addrref" : this.inptext1,
				"type" : "single"},
		"pd" : {"symbolref" : this.docref.getElementById("outputpd"),
				"addredit" : "addreditcoil1",
				"defaultaddr" : ["C2000"],
				"addrref" : this.inptext1,
				"type" : "single"},

		// Coil outputs with a range of addresses.
		"out2" : {"symbolref" : this.docref.getElementById("outputout2"),
				"addredit" : "addreditcoil2",
				"defaultaddr" : ["C1999", "C2000"],
				"addrref" : this.coiltext2,
				"type" : "single"},
		"set2" : {"symbolref" : this.docref.getElementById("outputset2"),
				"addredit" : "addreditcoil2",
				"defaultaddr" : ["C1999", "C2000"],
				"addrref" : this.coiltext2,
				"type" : "single"},
		"rst2" : {"symbolref" : this.docref.getElementById("outputreset2"),
				"addredit" : "addreditcoil2",
				"defaultaddr" : ["C1999", "C2000"],
				"addrref" : this.coiltext2,
				"type" : "single"},
		"pd2" : {"symbolref" : this.docref.getElementById("outputpd2"),
				"addredit" : "addreditcoil2",
				"defaultaddr" : ["C1999", "C2000"],
				"addrref" : this.coiltext2,
				"type" : "single"},

		// Program control instructions. 
		"end" : {"symbolref" : this.docref.getElementById("progcontrolend"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "single"},
		"endc" : {"symbolref" : this.docref.getElementById("progcontrolendc"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "single"},
		"rt" : {"symbolref" : this.docref.getElementById("progcontrolrt"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "single"},
		"rtc" : {"symbolref" : this.docref.getElementById("progcontrolrtc"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "single"},
		"call" : {"symbolref" : this.docref.getElementById("progcontrolcall"),
				"addredit" : "addreditcall", 
				"defaultaddr" : ["none"], 
				"addrref" : [this.docref.getElementById("calltext")],
				"type" : "single"},
		"for" : {"symbolref" : this.docref.getElementById("progcontrolfor"),
				"addredit" : "addreditfor", 
				"defaultaddr" : ["0", "0"], 
				"addrref" : [this.docref.getElementById("fortext1a"), 
						this.docref.getElementById("fortext1b")],
				"type" : "single"},
		"next" : {"symbolref" : this.docref.getElementById("progcontrolnext"),
				"addredit" : "addresseditnone", 
				"defaultaddr" : [], "addrref" : [], "type" : "single"},



		// Counters. 
		"cntu" : {"symbolref" : this.docref.getElementById("timercntu"),
				"addredit" : "addreditcounter", 
				"defaultaddr" : ["CT250", "1"], 
				"addrref" : [this.docref.getElementById("countertext1a"),
						this.docref.getElementById("countertext1b")],
				"type" : "double"},
		"cntd" : {"symbolref" : this.docref.getElementById("timercntd"),
				"addredit" : "addreditcounter", 
				"defaultaddr" : ["CT250", "1"], 
				"addrref" : [this.docref.getElementById("countertext1a"),
						this.docref.getElementById("countertext1b")],
				"type" : "double"},
		"udc" : {"symbolref" : this.docref.getElementById("timerudc"),
				"addredit" : "addreditcounter", 
				"defaultaddr" : ["CT250", "1"], 
				"addrref" : [this.docref.getElementById("countertext1a"),
						this.docref.getElementById("countertext1b")],
				"type" : "triple"},

		// Timers.
		"tmra" : {"symbolref" : this.docref.getElementById("timertmra"),
				"addredit" : "addredittimer", 
				"defaultaddr" : ["T500", "1000", "ms"], 
				"addrref" : [this.docref.getElementById("tmratext1a"),
						this.docref.getElementById("tmratext1b"),
						this.docref.getElementById("tmratext1c")],
				"type" : "double"},

		"tmr" : {"symbolref" : this.docref.getElementById("timertmr"),
				"addredit" : "addredittimer", 
				"defaultaddr" : ["T500", "1000", "ms"], 
				"addrref" : this.timertext1,
				"type" : "single"},
		"tmroff" : {"symbolref" : this.docref.getElementById("timertmroff"),
				"addredit" : "addredittimer", 
				"defaultaddr" : ["T500", "1000", "ms"], 
				"addrref" : this.timertext1,
				"type" : "single"},


		// Copy instructions. 
		"copy" : {"symbolref" : this.docref.getElementById("copy"),
				"addredit" : "addreditcopy", 
				"defaultaddr" : ["0", "DS10000", "0"], 
				"addrref" : [this.docref.getElementById("copytext1a"),
						this.docref.getElementById("copytext1b"),
						this.docref.getElementById("copytext1c")],
				"type" : "single"},
		"cpyblk" : {"symbolref" : this.docref.getElementById("cpyblk"),
				"addredit" : "addreditcpyblk", 
				"defaultaddr" : ["DS9997", "DS9998", "DS9999", "0"], 
				"addrref" : [this.docref.getElementById("cpyblktext1a"),
						this.docref.getElementById("cpyblktext1b"),
						this.docref.getElementById("cpyblktext1c"),
						this.docref.getElementById("cpyblktext1d")],
				"type" : "single"},
		"fill" : {"symbolref" : this.docref.getElementById("fill"),
				"addredit" : "addreditfill", 
				"defaultaddr" : ["DS9997", "DS9998", "DS9999", "0"], 
				"addrref" : [this.docref.getElementById("filltext1a"),
						this.docref.getElementById("filltext1b"),
						this.docref.getElementById("filltext1c"),
						this.docref.getElementById("filltext1d")],
				"type" : "single"},
		"pack" : {"symbolref" : this.docref.getElementById("pack"),
				"addredit" : "addreditpack", 
				"defaultaddr" : ["C1999", "C2000", "DS10000", "0"], 
				"addrref" : [this.docref.getElementById("packtext1a"),
						this.docref.getElementById("packtext1b"),
						this.docref.getElementById("packtext1c"),
						this.docref.getElementById("packtext1d")],
				"type" : "single"},
		"unpack" : {"symbolref" : this.docref.getElementById("unpack"),
				"addredit" : "addreditunpack", 
				"defaultaddr" : ["DS10000", "C1999", "C2000", "0"], 
				"addrref" : [this.docref.getElementById("unpacktext1a"),
						this.docref.getElementById("unpacktext1b"),
						this.docref.getElementById("unpacktext1c"),
						this.docref.getElementById("unpacktext1d")],
				"type" : "single"},

		// Find or search instructions. 
		"findeq" : {"symbolref" : this.docref.getElementById("findeq"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findne" : {"symbolref" : this.docref.getElementById("findne"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findgt" : {"symbolref" : this.docref.getElementById("findgt"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findge" : {"symbolref" : this.docref.getElementById("findge"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findlt" : {"symbolref" : this.docref.getElementById("findlt"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findle" : {"symbolref" : this.docref.getElementById("findle"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findieq" : {"symbolref" : this.docref.getElementById("findieq"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findine" : {"symbolref" : this.docref.getElementById("findine"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findigt" : {"symbolref" : this.docref.getElementById("findigt"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findige" : {"symbolref" : this.docref.getElementById("findige"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findilt" : {"symbolref" : this.docref.getElementById("findilt"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},
		"findile" : {"symbolref" : this.docref.getElementById("findile"),
				"addredit" : "addreditfind",
				"defaultaddr" : this.FindDefaults, 
				"addrref" : this.findtext,
				"type" : "single"},


		// Math instructions. 
		"mathdec" : {"symbolref" : this.docref.getElementById("mathdec"),
				"addredit" : "addreditmath", 
				"defaultaddr" : ["DS10000", "1 + 1", "0"], 
				"addrref" : this.mathtext,
				"type" : "single"},
		"mathhex" : {"symbolref" : this.docref.getElementById("mathhex"),
				"addredit" : "addreditmath", 
				"defaultaddr" : ["DH2000", "1h + 1h", "0"],
				 "addrref" : this.mathtext,
				"type" : "single"},
		"sum" : {"symbolref" : this.docref.getElementById("sum"),
				"addredit" : "addreditsum", 
				"defaultaddr" : ["DS10000", "DS9998", "DS9999", "0"], 
				"addrref" : this.sumtext,
				"type" : "single"},

		// Shift register.
		"shfrg" : {"symbolref" : this.docref.getElementById("shfrg"),
				"addredit" : "addreditshfrg", 
				"defaultaddr" : ["C1999", "C2000"], 
				"addrref" : [this.docref.getElementById("shfrgtext1a"),
						this.docref.getElementById("shfrgtext1b")],
				"type" : "triple"}
		};



	// ==================================================================


	// ##################################################################

	// Get the references to the background edit tabs.
	this.buttonsinputtabs = this.docref.getElementById("inputtabs");
	this.buttonsoutputtabs = this.docref.getElementById("outputtabs");
	

	// Get the correct references to the different edit button types.
	this.buttonsinputs = this.docref.getElementById("inputbuttons");
	this.buttonscompare = this.docref.getElementById("comparebuttons");
	this.buttonsbranches = this.docref.getElementById("branchbuttons");
	this.buttonsinputedit = this.docref.getElementById("inputmatrixeditbuttons");

	this.buttonsoutputs = this.docref.getElementById("outputbuttons");
	this.buttonsprogcontrol = this.docref.getElementById("progcontrolbuttons");
	this.buttonstimercounter = this.docref.getElementById("timercounterbuttons");
	this.buttonscopydata = this.docref.getElementById("copydatabuttons");
	this.buttonsfind = this.docref.getElementById("findbuttons");
	this.buttonsmisc = this.docref.getElementById("miscbuttons");
	this.buttonsoutputedit = this.docref.getElementById("outputmatrixeditbuttons");

	/* These are the groups of buttons which are used when editing a rung.
	this is normally used to control when each of these groups is displayed.
	"buttonref" = The individual groups of buttons, plus the highlighted tab.
	"tabref" = The tabs used to select the groups of buttons.
	*/
	this.buttondefs = {
		"inputbuttons" : {"buttonref" : this.buttonsinputs, "tabref" : this.buttonsinputtabs},
		"comparebuttons" : {"buttonref" : this.buttonscompare, "tabref" : this.buttonsinputtabs},
		"branchbuttons" : {"buttonref" : this.buttonsbranches, "tabref" : this.buttonsinputtabs},
		"inputmatrixeditbuttons" : {"buttonref" : this.buttonsinputedit, "tabref" : this.buttonsinputtabs},
		"outputbuttons" : {"buttonref" : this.buttonsoutputs, "tabref" : this.buttonsoutputtabs},
		"progcontrolbuttons" : {"buttonref" : this.buttonsprogcontrol, "tabref" : this.buttonsoutputtabs},
		"timercounterbuttons" : {"buttonref" : this.buttonstimercounter, "tabref" : this.buttonsoutputtabs},
		"copydatabuttons" : {"buttonref" : this.buttonscopydata, "tabref" : this.buttonsoutputtabs},
		"findbuttons" : {"buttonref" : this.buttonsfind, "tabref" : this.buttonsoutputtabs},
		"miscbuttons" : {"buttonref" : this.buttonsmisc, "tabref" : this.buttonsoutputtabs},
		"outputmatrixeditbuttons" : {"buttonref" : this.buttonsoutputedit, "tabref" : this.buttonsoutputtabs},
	}


	// ##################################################################
	/* These provide lists of ids for "instruction masks". The instruction
		masks are used to disable instructions which are not valid for the
		type of rung currently being displayed. These are used by
		changing the class of the mask between classes which use
		the display property to hide or show the mask. 
	*/
	this.InstructionMasks = {"single" : ["masktimersingle", "maskcoilssingle", 
						"maskbranch", "maskprogsingle", 
						"maskcopysingle", "maskfindsingle", 
						"maskmiscsingle"],
				"double" : ["masktimerdouble"],
				"triple" : ["masktimertriple", "maskmisctriple"]
				}
	// ==================================================================


	// ##################################################################

	// The subroutine name go in this.
	this.subroutinename = this.docref.getElementById("subroutinename");
	// The subroutine comments go in this.
	this.subrcomments = this.docref.getElementById("subrcomments");

	// The container for holding SVG items.
	this.svgcontainer = this.docref.getElementById("ladderdispprototype");

	// This gives the ladder rung display items an offset.
	this.laddercontainer = this.docref.getElementById("laddercontainer");

	// This is a single "empty" container (group) for holding edit items.
	this.cellcontainer = this.docref.getElementById("cellcontainer");


	// The list of static (non-editing) rungs go in here.
	this.staticladderlist = this.docref.getElementById("staticrunglist");

	// Power rail to join inputs to outputs.
	this.svginprail = this.docref.getElementById("svginprail1");
	// Power rail to join inputs to outputs (second optional rail).
	this.svginprail2 = this.docref.getElementById("svginprail2");
	// Power rail to join inputs to outputs (third optional rail).
	this.svginprail3 = this.docref.getElementById("svginprail3");

	// Power rail to join outputs together.
	this.svgoutprail = this.docref.getElementById("svgoutprail");
	
	// Decoration for output rail.
	this.svgoutpraildec = this.docref.getElementById("svgoutraildecoration");

	// ##################################################################

	// The definition for the edit matrix. 
	this.MatrixDef = {};

	// Generate the inputs.
	for (var i = 0; i <= this.MaxInputRow; i++) {
		for (var j = 0; j <= this.MaxInputCol; j++) {
			this.MatrixDef["inputedit" + i + j] = {"row" : i, "col" : j, 
							"type" : "inputs", 
							"ladder" : "inputladder" + i + j, 
							"address" : "inputtext" + i + j};
		}
	}

	// Generate the outputs.
	for (var i = 0; i <= this.MaxOutputRow; i++) {
		this.MatrixDef["outputedit" + i] = {"row" : i, "col" : 0, 
						"type" : "outputs", 
						"ladder" : "outputladder" + i, 
						"address" : "outputtext" + i};
	}


	// ==================================================================

	// Padding to add to increase the height of the rung.
	this.RungHeightPad = 15;


	// Parameters for SVG matrix coordinates. 
	this.MatrixParams = {
		// One logic stack input per rung. Most outputs use this.
		"single" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 7, 	// Maximum input row.
				"maxoutputrow" : 7,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 75,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},

		// Two logic stack inputs per rung. 
		"double" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 1, 	// Maximum input row.
				"maxoutputrow" : 0,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 150,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},

		// Three logic stack inputs per rung. 
		"triple" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 2, 	// Maximum input row.
				"maxoutputrow" : 0,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 225,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},

		// No instructions present in this rung yet. 
		"empty" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 0, 	// Maximum input row.
				"maxoutputrow" : 0,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 75,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},

		// This is for IL. The numbers here are meaningless, as they are not used.
		// The presense of this option however keeps other logic happy.
		"il" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 0, 	// Maximum input row.
				"maxoutputrow" : 0,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 75,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},

		// This is for the subroutine heading. The numbers here are meaningless, 
		// as they are not used. The presense of this option however keeps other logic happy.
		"sbr" : {	"maxinputcol" : 7, 	// Maximum input column.
				"maxinputrow" : 0, 	// Maximum input row.
				"maxoutputrow" : 0,	// Maximum output row.
				"inputpitch" : 75,	// Horizontal pitch for input positions.
				"inputvert" : 75,	// Vertical pitch for inputs.
				"vertpitch" : 75,	// Vertical pitch for output positions.
				"outputxpos" : 610	// X coordinate of the output column.
			},
	}

	// The rung types for valid ladder. 
	this.RungOutputTypes = ["single", "double", "triple"];

	// ==================================================================

	// Look up the CSS styles for hiding and showing rungs.
	this.RungStylesLadder = {
		"single" : {"ladder" : "ladderdisplayshow", "il" : "ildisplayhide"},
		"double" : {"ladder" : "ladderdisplayshow", "il" : "ildisplayhide"},
		"triple" : {"ladder" : "ladderdisplayshow", "il" : "ildisplayhide"},
		"il" : {"ladder" : "ladderdisplayhide", "il" : "ildisplayshow"},
		"empty" : {"ladder" : "ladderdisplayhide", "il" : "ildisplayhide"},
		"sbr" : {"ladder" : "ladderdisplayhide", "il" : "ildisplayhide"}
	}


// ==================================================================


}


