/** ##########################################################################
# Project: 	libmbhmi
# Module: 	libmbhmiold.js
# Purpose: 	HMI library functions for use with Cascadas.
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		08-Aug-2010
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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
The functions in this library are provided for compatibility with existing 
HMI applications, and are not recommended for new HMI applications.

The functions included here are:

MB_SVGPushButton
	- Reverses the linear gradient of a push button.

MB_Pipe
	- Indicate conditions in pipes or ducts by using stroke colour. 

MB_PipeFlow
	- Flow of liquids or gases in pipes or ducts by adjusting the linear gradient.
	
MB_PipeFlow2
	- Flow of liquids or gases in pipes or ducts by adjusting the linear gradient.

MB_LEDDigit
	- Display digits using 7-segment graphics.


MB_Pipe manipulates the "stroke" property. 
MB_Pipe2 manipulates the "fill" property. This differs from MB_PilotLight in 
	that 0 is off, and non-zero is on, whereas MB_PilotLight only accepts
	0 and 1 as valid values.


MB_PipeFlow, and MB_PipeFlow2 manipulate the "offset" property 
in linear gradients, which in turn can affect the appearance of other SVG 
graphics. Since a single gradient can be assigned to more than one SVG 
graphic, this can produce coordinated changes in several graphics. 
With MB_PipeFlow and MB_PipeFlow2, the gradient changes by one increment
each time the function is called, with the direction being set according to the
sign (+ve, 0, or -ve) of the tag it is associated with. This can be used as a simple 
form of animation.

Example - 

	<!-- This displays the flow in the piping. 
		This version illustrates MB_PipeFlow. -->
	<defs>
	<linearGradient id="PipeFlow">
	<stop offset="0%" stop-color="blue" />
	<stop id="PipeFlowA" offset="10%" stop-color="blue"/>
	<stop id="PipeFlowB" offset="15%" stop-color="white"/>
	<stop id="PipeFlowC" offset="20%" stop-color="blue"/>
	<stop offset="100%" stop-color="blue" />
	</linearGradient>
	</defs>

	<polyline fill="none" stroke="url(#PipeFlow)" stroke-width="10"
				points="0,0 0,50 140,50" />

	// Pipe flow.
	var PipeFlow = new MB_PipeFlow(document, "PipeFlowA", "PipeFlowB", "PipeFlowC", 10);


	<!-- This version illustrates MB_PipeFlow. -->
	<!-- This displays the flow in the piping. The X and
			Y parameters control the direction the gradient moves in.-->
	<linearGradient id="PipeFlowV" spreadMethod="repeat" 
			x1="0%" x2="0%" y1="0%" y2="50%">
		<stop id="PipeFlowVA" offset="10%" stop-color="white" />
		<stop id="PipeFlowVB" offset="20%" stop-color="blue" />
	</linearGradient>

	<!-- Vertical pipe from tank 1 to first bend. 
		This shows how to use a rectangle rather than a polyline. -->
	<rect x="0" y="0" width="10" height="50" fill="url(#PipeFlowV)" />


	// Pipe flow for vertical pipes.
	var PipeFlowV = new MB_PipeFlow2(document, "PipeFlowVA", "PipeFlowVB", 20);
	MBHMIProtocol.AddToDisplayList(PipeFlowV, "PumpSpeedActual", "read");

*/



// ##################################################################

/* 	SVG Push Button. This operates by adjusting the linear gradient. The 
		function reverses the gradient colours to reverse
		the gradient colour pattern.
	Parameters:
	svgdoc - Reference to SVG document.
	GradStop1 (string) - ID of first linear gradient stop.
	GradStop2 (string) - ID of last linear gradient stop.

*/
function MB_SVGPushButton(svgdoc, GradStop1, GradStop2) {

	this.Stop1 = svgdoc.getElementById(GradStop1);	// Reference to linear gradient.
	this.Stop2 = svgdoc.getElementById(GradStop2);	// Reference to linear gradient.
	// Get the current gradient stop colours.
	this.Colour1 = this.Stop1.getAttribute("stop-color");
	this.Colour2 = this.Stop2.getAttribute("stop-color");

	// Change the button to the "pressed" colours. 
	function _ButtonPressed() {
		this.Stop1.setAttribute("stop-color", this.Colour2);
		this.Stop2.setAttribute("stop-color", this.Colour1);
	}

	// Change the button to the "released" colours. 
	function _ButtonReleased() {
		this.Stop1.setAttribute("stop-color", this.Colour1);
		this.Stop2.setAttribute("stop-color", this.Colour2);
	}

	// Reference the functions to make them public.
	this.ButtonPressed = _ButtonPressed;
	this.ButtonReleased = _ButtonReleased;

}
// End of object definition.



// ##################################################################

/* 	Indicate conditions in pipes or ducts. This operates by adjusting the 
	stroke colour according to whether the value being monitored is zero or not.
	Parameters:
	svgdoc - Reference to SVG document.
	PipeID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	offcolour (string) - Colour to use when zero.
	oncolour (string) - Colour to use when not zero.
*/
function MB_Pipe(svgdoc, PipeID, initcolour, offcolour, oncolour) {

	this.Pipe_ref = svgdoc.getElementById(PipeID);	// Reference to pipe.
	this.Pipe_offcolour = offcolour;		// Colour to use when off.
	this.Pipe_oncolour = oncolour;			// Colour to use when on.
	this.Pipe_initcolour = initcolour;		// Colour to use when undefined.

	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. 
	Parameters: flowing (integer) - 0 = stopped. non-zero =  flowing.
	*/
	function _UpdatePipe(flowing) {
		// Only update if changed since last time.
		if (flowing != this.LastState) {
			this.LastState = flowing;
			if (flowing == 0) { 
				this.Pipe_ref.setAttribute('stroke', this.Pipe_offcolour);
			}
			else {
				this.Pipe_ref.setAttribute('stroke', this.Pipe_oncolour);
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePipe;

}
// End of object definition.



// ##################################################################


/* 	Flow of liquids or gases in pipes or ducts. This operates by adjusting the 
	linear gradient along a line (SVG object). See also MB_PipeFlow2 which 
	allows simpler gradient definitions.
	Parameters:
	svgdoc - Reference to SVG document.
	PipeID1 (string) - ID of first linear gradient for pipe SVG item.
	PipeID2 (string) - ID of second linear gradient for pipe SVG item.
	PipeID3 (string) - ID of third linear gradient for pipe SVG item.
	flowinc (integer) - Amount and direction to flow. 
		From -100 to 100. +ve = to right. -ve =  to left.
*/
function MB_PipeFlow(svgdoc, PipeID1, PipeID2, PipeID3, flowinc) {

	this.Pipe1 = svgdoc.getElementById(PipeID1);	// Reference to pipe gradient.
	this.Pipe2 = svgdoc.getElementById(PipeID2);	// Reference to pipe gradient.
	this.Pipe3 = svgdoc.getElementById(PipeID3);	// Reference to pipe gradient.
	this.FlowInc = flowinc;				// Amount and direction to flow.
	this.FlowVal = 0;				// Amount of flow.

	/* Update the current display state. 
	Parameters: direction (integer) - 0 = stopped. +ve = flow is to the right.
		-ve = flow is to the left.
	*/
	function _UpdatePipeFlow(direction) {
		// Flow is stopped.
		if (direction == 0) {
			return;
		}

		// Flow is to right.
		if (direction > 0) {
			this.FlowVal = this.FlowVal + this.FlowInc;
		}
		// Flow is to left.
		else if (direction < 0) {
			this.FlowVal = this.FlowVal - this.FlowInc;
		}

		// The flow value must be limited to between 0% and 100%.
		if (this.FlowVal > 90) {
			this.FlowVal = 5;
		}
		if (this.FlowVal < 5) {
			this.FlowVal = 90;
		}

		// Make the liquid flow.
		this.Pipe1.setAttribute("offset", this.FlowVal + "%");
		this.Pipe2.setAttribute("offset", 10 + this.FlowVal + "%");
		this.Pipe3.setAttribute("offset", 50 + this.FlowVal + "%");

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePipeFlow;

}
// End of object definition.



// ##################################################################


/* 	Flow of liquids or gases in pipes or ducts. This operates by adjusting the 
	linear gradient along a line (SVG object). This version requires only 2
	gradients to be defined, but uses the SVG "spreadMethod". This allows
	for simpler definitions. 
	Parameters:
	svgdoc - Reference to SVG document.
	PipeID1 (string) - ID of first linear gradient for pipe SVG item.
	PipeID2 (string) - ID of second linear gradient for pipe SVG item.
	flowinc (integer) - Amount and direction to flow. 
		From -100 to 100. +ve = to right. -ve =  to left.
*/
function MB_PipeFlow2(svgdoc, PipeID1, PipeID2, flowinc) {

	this.Pipe1 = svgdoc.getElementById(PipeID1);	// Reference to pipe gradient.
	this.Pipe2 = svgdoc.getElementById(PipeID2);	// Reference to pipe gradient.
	this.FlowInc = flowinc;				// Amount and direction to flow.
	this.FlowVal = 0;				// Amount of flow.

	/* Update the current display state. 
	Parameters: direction (integer) - 0 = stopped. +ve = flow is to the right.
		-ve = flow is to the left.
	*/
	function _UpdatePipeFlow2(direction) {
		// Flow is stopped.
		if (direction == 0) {
			return;
		}

		// Flow is to right.
		if (direction > 0) {
			this.FlowVal = this.FlowVal + this.FlowInc;
		}
		// Flow is to left.
		else if (direction < 0) {
			this.FlowVal = this.FlowVal - this.FlowInc;
		}

		// The flow value must be limited to between 0% and 100%.
		// We use 90% as the test limit, as we add 10% to this later.
		if (this.FlowVal > 90) {
			this.FlowVal = 0;
		}
		else if (this.FlowVal < 0) {
			this.FlowVal = 90;
		}

		// Make the liquid flow.
		this.Pipe1.setAttribute("offset", this.FlowVal + "%");
		this.Pipe2.setAttribute("offset", 10 + this.FlowVal + "%");

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePipeFlow2;

}
// End of object definition.



// ##################################################################

/*	Display a single digit of an integer as an LED 7 segment
	style graphic. This selects an SVG image from among the
	10 possible images to display according to the value
	of an integer. Each image must have a unique "id" string. 
	This function hides or displays different parts to display 
	only one at a time.
	This is compatible with the display list.
	Parameters: 
	pagedoc - A reference to the HTML document.
	LEDTable (array) - An array of strings containing the ids of
		the SVG graphic LED images.
	leddigit (integer) - The digit to display. Where 1 is the ones digit,
		2 is the tens digit,  3 is the hundreds digit, etc.
*/

function MB_LEDDigit(pagedoc, ledtable, leddigit) {

	this.PageDoc = pagedoc;
	this.LEDTable = ledtable;
	this.LEDDigit = Math.pow(10, (leddigit - 1));

	this.NumbImages = this.LEDTable.length;
	this.ImageRef = [];

	// Make a table of references to each image, and turn 
	// the display mode off for each.
	for (i = 0; i < this.NumbImages; i++) {
		var imagestr = this.LEDTable[i];
		this.ImageRef.push(this.PageDoc.getElementById(imagestr))
		this.ImageRef[i].style.display = "none";
	}

	// Initialise the last state.
	this.LastState = null;

	// Select a new image.
	//	Parameters: imageindex (integer) - The index of the new image in 
	//		the LEDTable array.	

	function _SelectLEDImage(imageindex) {
		// Select the digit that we want.
		var indexvalue = Math.floor(imageindex / this.LEDDigit);
		var indexstr = indexvalue.toString();
		var indexdigit = indexstr[indexstr.length - 1];

		
		// Only update if changed since last time.
		if (indexdigit != this.LastState) {
			// First, turn off the old image.
			if (this.LastState == null) {
				this.LastState = 0;
			}
			this.ImageRef[this.LastState].style.display = "none";

			// Check if the image is within range.
			if ((indexdigit >= 0) && (indexdigit < this.NumbImages)) {
				// Show the new image.
				this.ImageRef[indexdigit].style.display = "block";
				// Save the new index.
				this.LastState = indexdigit;
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _SelectLEDImage;

}
// End of object definition.


// ##################################################################

