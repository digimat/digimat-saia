/** ##########################################################################
# Project: 	libmbhmi
# Module: 	libmbhmi.js
# Purpose: 	HMI library functions for use with Cascadas.
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		03-Feb-2009
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
This library is intended to provide useful functions for a web based HMI, as
well as acting as an example for how to write additional functions should
they be required. It is assumed that you know how to create a web page,
and know something about Javascript, CSS, and SVG. If you are using SVG
graphics, you must create the page as an xhtml page rather than an ordinary
html page as html (at least html 4) does not support in-line SVG.


The functions here fall into the following categories - 

1) Objects to control various types of SVG graphics. These include:
MB_PilotLight, MB_PLMultiColour, MB_PilotLightStat,
MB_2PosSSDisplay, MB_3PosSSDisplay, MB_SlideDisplay, 
MB_SVGPushButton, MB_NumericDisplay, MB_NumericFloatDisplay,
MB_StringDisplay, MB_TextDisplay, MB_NumericPad, 
MB_DialGauge, MB_TankLevel, MB_Pipe, MB_Pipe2, MB_PipeFlow, MB_PipeFlow2, 
MB_PumpRotate, MB_StripChart, MB_GraphicSelect, MB_LEDDigit,
MB_GraphicShowHide


Despite such names as "pilot light" and "tank", they are not restricted to 
controlling those shapes only. Since the graphics are completely under user 
control, the actual shape of the graphics can be anything, so that "MB_TankLevel" 
might be used for example to simulate a column gauge.

These code objects are compatible with the Cascadas "display list", as they
export and "UpdateScreen" method which accepts a single parameter.

example - 

The user must create an SVG graphic and place it on the screen. This creates a 
circle which we can use as a pilot light. Note the id="PL1".

<svg:circle id="PL1" cx="50px" cy="50px" r="25px" fill="black" stroke="black" stroke-width="5px"/>

The user must then create a code object to control the SVG graphic. Note that 
one of the parameters here is "PL1". This establishes the reference between
the screen graphic and the code object. 

	var PL1 = new MB_PilotLight(document, "PL1", "black", "green", "red");

The code object will (in the case of this function) simply manipulates the 
"fill" property, setting it to green or red (or black until initialised). 
The fill property of any shape can be manipulated this way, which means we
are not limited to circular objects or to pilot lights.

We next use the Cascadas library AddToDisplayList to control it. The Cascadas 
is not strictly necessary, as We could simply call it directly.

	CASCADAS.AddToDisplayList(PL1, "PL1", "read");


MB_PilotLight and MB_PLMultiColour manipulate the "fill" property of the SVG graphics.
MB_NumericDisplay and MB_NumericFloatDisplay display numeric values. 
MB_StringDisplay displays string data.
MB_Pipe manipulates the "stroke" property. 
MB_Pipe2 manipulates the "fill" property. This differs from MB_PilotLight in 
	that 0 is off, and non-zero is on, whereas MB_PilotLight only accepts
	0 and 1 as valid values.
MB_DialGauge manipulates the "rotate" property. 
MB_StripChart changes the "points" propery in a polyline.

MB_TextDisplay displays a text message by selecting an element from an array of 
strings according to a numeric array index. For example - 

	var ColourList = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]; 
	var PL4 = new MB_PLMultiColour(document, "PL4", "black", ColourList);

MB_TankLevel, MB_PipeFlow, and MB_PipeFlow2 manipulate the "offset" property 
in linear gradients, which in turn can affect the appearance of other SVG 
graphics. Since a single gradient can be assigned to more than one SVG 
graphic, this can produce coordinated changes in several graphics. 
With MB_TankLevel, the gradient is set to follow the tag is is associated with. 
With MB_PipeFlow and MB_PipeFlow2, the gradient changes by one increment
each time the function is called, with the direction being set according to the
sign (+ve, 0, or -ve) of the tag it is associated with. This can be used as a simple 
form of animation.

Example - 
	<!-- This displays the fill level for tank 1. The x and y values control 
		the direction of the gradient. The middle two gradient offsets are set
		wide apart so there is no sharp devault tank level shown. -->
	<defs>
		<linearGradient id="TankFill1" x1="0" y1="1" x2="0" y2="0">
			<stop offset="0%" stop-color="blue" />
			<stop id="TFill1A" offset="10%" stop-color="blue" />
			<stop id="TFill1B" offset="90%" stop-color="white" />
			<stop offset="100%" stop-color="white" />
		</linearGradient>
	</defs>


	<!-- Display tank 1. -->
	<g transform="translate(50,25)">
		<rect x="0" y="0" width="125" height="300" rx="62" fill="url(#TankFill1)" 
			stroke="purple" stroke-width="20"/>
	</g>

	// Tank 1 fill level graphic display.
	var Tank1 = new MB_TankLevel(document, "TFill1A", "TFill1B");


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



MB_PumpRotate manipulates the rotation property of an SVG object on an incremental 
basis. Each time the function is called, the component is rotated by an increment
specified in the parameters. This can be used as a simple form of animation.

	<circle cx="0" cy="0" r="25" fill="none" stroke-width="10" stroke="purple"  />
	<g  id="Pump1" transform="rotate(0)">
		<polyline fill="none" stroke="red" stroke-width="10"
		points="-20,0 20,0 0,0 0,-20 0,20" />
	</g>

	// Pump rotation.
	var PumpRotation = new MB_PumpRotate(document, "Pump1", 19);


MB_GraphicShowHide is used to display or hide an SVG graphic. This can be used
to enable or disable an input button by putting another "mask" graphic
over top of the button and then showing or hiding the mask.


2) An object for entering numeric data (MB_NumericPad). This provides
a function which allows digits 0 to 9, '-', and '.' to be entered. It also 
provides functions to clear the current value, and to retrieve the current
value as an integer or as a float. It also automatically updates an SVG
text display to show the current value.

This object does *not* use the display list. The user must call each 
function as appropriate.

Example:

The numeric pad object must be created on start up.

	// Numeric display. This does not get added to the display list.
	var NumberPad = new MB_NumericPad(document, "numberpaddisplay", 12);


The numeric pad requires an text area to write the intermediate value into
for display purposes. This does not send the value to the server.

	<!-- Numeric display -->			
	<rect x="20" y="20" width="150" height="50" rx="15" fill="white"/>
	<text id="numberpaddisplay" x="22" y="50" font-size="20" 
			stroke-width="2px">????????????</text> 


Each numeric button must be provided individually. This shows how to do
one button (for the number 7). The "onclick" function causes the digit
to be appended when the user clicks the SVG rectangle button.

	<g  transform="translate(0, 0)" id="svgbuttondef"
			onclick="NumberPad.AppendDigit(7);">
		<rect x="0" y="0" width="35" height="35" rx="5"
				fill="url(#NumericEntryButtonGradient)"/>
		<text x="8" y="25" font-size="24" stroke-width="2px">7</text> 
	</g>


The current value can be clears by calling the "ClearDisplay" method. This only
clears the intermediate display value and does not affect any value which may 
have been stored in the data table.

	<g  transform="translate(70, 180)" id="svgbuttondef"
			onclick="NumberPad.ClearDisplay();">
		<rect x="0" y="0" width="55" height="35" rx="5"
				fill="url(#NumericEntryButtonGradient)"/>
		<text x="8" y="25" font-size="20" stroke-width="2px">CLR</text> 
	</g>


The numeric pad object does not itself write directly to the data table. The 
current value must be retrieved by calling GetValueInt (retrieve the value as
an integer) or GetValueFloat (retrieve the value as a floating point number).
Another library function (e.g. MBHMIProtocol.WriteImmediate) can then write 
this value to the data table. Alternatively, a custom written function can
retrieve the value and perform some other operations on it.

	<g  transform="translate(0, 180)" id="svgbuttondef"
			onclick="MBHMIProtocol.WriteImmediate('Testholdingreg32', 
				NumberPad.GetValueInt()); ">
		<rect x="0" y="0" width="60" height="35" rx="5"
				fill="url(#NumericEntryButtonGradient)"/>
		<text x="8" y="25" font-size="20" stroke-width="2px">STR</text> 
	</g>


3) An object to handle the display of screens. An "AJAX" type web application 
is usually all in one page because (for security reasons) there is no easy way for 
applications in different web pages to communicate with each other. However, a
web application can give the appearance of having different pages (referred to 
as HMI "screens" here) by hiding and revealing different parts of a single 
page. MB_ScreenSelect can be used to easily control this process. 

First some "div" blocks must be set up in the web page, one for each HMI "screen".
Examples -

	<div id="mainscreen">
	<p><h2>CaScadaS Demo Main Screen:</h2></p> 
	
		<!-- The main web page goes here. -->

	</div>

	<div id="eventscreen">
		<p><h2>Events:</h2> </p>

		<!-- The events web page goes here. -->

	</div>


	<div id="alarmscreen">
		<p><h2>Active Alarms:</h2> 

		<!-- The alarms web page goes here. -->

	</div>


Next, MB_ScreenSelect is created in the Javascript section and passed an array
of the ids for each screen.

	var ScreenTable = ["mainscreen", "eventscreen", "alarmscreen"];
	// This creates an object that controls display of the screens.
	var ScreenSelect = new MB_ScreenSelect(document, ScreenTable);

Next, a menu is created and placed somewhere on the screen which calls ScreenSelect
with the desired screen id as a parameter.

	<div id="nav">
		<ul>
			<li><a onclick = "ScreenSelect.SelectScreen('mainscreen')">Main</a></li>
			<li><a onclick = "ScreenSelect.SelectScreen('eventscreen')">Events</a></li>
			<li><a onclick = "ScreenSelect.SelectScreen('alarmscreen')">Alarms</a></li>
		</ul>
	</div>

Finally a few lines are added to the CSS for the page. 

	#mainscreen {
		display: block;
		}

	#eventscreen {
		display: none;
		}

	#alarmscreen {
		display: none;
		}

Other style properties such as colour, width, font, etc. can of course also
be set in these same CSS sections, but are not shown here. MB_ScreenSelect 
operates by manipulating the "display" property. If "display" is set to "block", 
the "screen" is visible. If it is set to "none", it is hidden. Set the default
screen (the one which is visible on start up) to "block" in the CSS.


*/



// ##################################################################

/* 	Pilot light control.
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	offcolour (string) - Colour to use when off.
	oncolour (string) - Colour to use when on.

*/
function MB_PilotLight(svgdoc, PLID, initcolour, offcolour, oncolour) {

	this.PL_offcolour = offcolour;			// Colour to use when off.
	this.PL_oncolour = oncolour;			// Colour to use when on.
	this.PL_initcolour = initcolour;		// Colour to use when undefined.
	this.PL_ref = svgdoc.getElementById(PLID);	// Reference to pilot light.

	// Set the initial colour.
	this.PL_ref.setAttribute('fill', this.PL_initcolour);

	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. 
	state (integer) - 0 = off. 1 = on. -1 = display init colour.
	*/
	function _UpdatePilotLight(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			switch(state) {
			case 0 : this.PL_ref.setAttribute('fill', this.PL_offcolour); break;
			case 1 : this.PL_ref.setAttribute('fill', this.PL_oncolour); break;
			default : this.PL_ref.setAttribute('fill', this.PL_initcolour); break;
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePilotLight;

}
// End of object definition.

// ##################################################################

/* 	Pilot light control with multiple colours.
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	colourlist (array) - Array of strings containing colours.
*/
function MB_PLMultiColour(svgdoc, PLID, initcolour, colourlist) {

	this.PL_colourlist = colourlist;		// Array of strings containing colours.
	this.PL_initcolour = initcolour;		// Colour to use when undefined.
	this.PL_ref = svgdoc.getElementById(PLID);	// Reference to pilot light.

	// Set the initial colour.
	this.PL_ref.setAttribute('fill', this.PL_initcolour);

	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. 
	colourindex (integer) - Index into colourlist indicating the selected colour.
	*/
	function _UpdatePilotLight(colourindex) {
		// Only update if changed since last time.
		if (colourindex != this.LastState) {
			this.LastState = colourindex;
			newcolour = this.PL_colourlist[colourindex];
			this.PL_ref.setAttribute('fill', newcolour);
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePilotLight;

}
// End of object definition.

// ##################################################################

/* 	Pilot light control. If the present value is equal to the comparison 
		value, the light will turn "on", otherwise, it will turn "off".
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	offcolour (string) - Colour to use when off.
	oncolour (string) - Colour to use when on.
	onstat (string) - Value to compare to for "on". This should be a constant.

*/
function MB_PilotLightStat(svgdoc, PLID, initcolour, offcolour, oncolour, onstat) {

	this.PL_offcolour = offcolour;			// Colour to use when off.
	this.PL_oncolour = oncolour;			// Colour to use when on.
	this.PL_initcolour = initcolour;		// Colour to use when undefined.
	this.PL_ref = svgdoc.getElementById(PLID);	// Reference to pilot light.
	this.PL_OnStatus = onstat;			// Comparison value.

	// Set the initial colour.
	this.PL_ref.setAttribute('fill', this.PL_initcolour);

	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. 
	*/
	function _UpdatePilotLight(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			switch(state) {
			case "" : this.PL_ref.setAttribute('fill', this.PL_initcolour); break;
			case "ok" : this.PL_ref.setAttribute('fill', this.PL_offcolour); break;
			default : this.PL_ref.setAttribute('fill', this.PL_oncolour); break;
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePilotLight;

}
// End of object definition.


// ##################################################################

/* 	Two Position Selector Switch Control. This rotates an element to one
	of two angles, depending on whether the monitored value is off ("0")
	or on (non-zero).
	Parameters:
	svgdoc - Reference to SVG document.
	SSID (string) - ID of SVG item.
	offangle (integer) - Angle in degrees when value is off (0).
	onangle (integer) - Angle in degrees when value is on (non-zero).

*/
function MB_2PosSSDisplay(svgdoc, SSID, offangle, onangle) {

	this.SS_ref = svgdoc.getElementById(SSID);	// Reference to selector switch.
	this.offangle = offangle; 			// Angle when off.
	this.onangle = onangle;				// Angle when on.


	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. */
	function _UpdateSS(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			// Angle for off.
			if (state == 0) {
				this.SS_ref.setAttribute("transform", "rotate(" + this.offangle +")");
			}
			// Angle for on.
			else {
				this.SS_ref.setAttribute("transform", "rotate(" + this.onangle +")");
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateSS;

}
// End of object definition.



// ##################################################################

/* 	Three Position Selector Switch Display.  This rotates an element to one
	of three angles, depending on the sign (-ve, +ve, or 0) of the 
	monitored value.
	Parameters:
	svgdoc - Reference to SVG document.
	SSID (string) - ID of SVG item.
	negativeangle (integer) - Angle in degrees when value is negative.
	zeroangle (integer) - Angle in degrees when value is zero.
	positiveangle (integer) - Angle in degrees when value is positive.

*/
function MB_3PosSSDisplay(svgdoc, SSID, negativeangle, zeroangle, positiveangle) {

	this.SS_ref = svgdoc.getElementById(SSID);	// Reference to selector switch.
	this.negativeangle = negativeangle;		// Angle when negative.
	this.zeroangle = zeroangle; 			// Angle when zero.
	this.positiveangle = positiveangle;		// Angle when positive.


	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. */
	function _UpdateSS(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			// Angle for negative.
			if (state < 0) {
				this.SS_ref.setAttribute("transform", "rotate(" + this.negativeangle +")");
			}
			// Angle for positive.
			else if (state > 0) {
				this.SS_ref.setAttribute("transform", "rotate(" + this.positiveangle +")");
			}
			// Angle for zero.
			else {
				this.SS_ref.setAttribute("transform", "rotate(" + this.zeroangle +")");
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateSS;

}
// End of object definition.



// ##################################################################

/* 	Two Position Slide Control. This translates (slides) an element to one
	of two positions, depending on whether the monitored value is off ("0")
	or on (non-zero).
	Parameters:
	svgdoc - Reference to SVG document.
	SSID (string) - ID of SVG item.
	offposx, offposy (integer) - X & Y positions in pixels when value is off (0).
	onposx, onposy (integer) - X & Y position in pixels when value is on (non-zero).

*/
function MB_SlideDisplay(svgdoc, SlideID, offposx, offposy, onposx, onposy) {

	this.Slide_ref = svgdoc.getElementById(SlideID);	// Reference to moving element.
	this.offposx = offposx;				// X position when off.
	this.offposy = offposy;				// Y position when off.
	this.onposx = onposx;				// X position when on.
	this.onposy = onposy;				// Y position when on.


	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. */
	function _UpdateSlide(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			// Position for off.
			if (state == 0) {
				this.Slide_ref.setAttribute("transform", "translate(" + this.offposx + "," + this.offposy +")");
			}
			// Position for on.
			else {
				this.Slide_ref.setAttribute("transform", "translate(" + this.onposx + "," + this.onposy +")");
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateSlide;

}
// End of object definition.


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

/*	Update a display of a number. This operates by changing the
	text property of an SVG string.
	Parameters:
	svgdoc - Reference to SVG document.
	NumberID (string) - ID of SVG text item.
*/
function MB_NumericDisplay(svgdoc, NumberID){

	this.Numeric_ref = svgdoc.getElementById(NumberID);	// Reference to numeric display.

	// Initialise the last value.
	this.LastValue = null;

	function _UpdateText(newvalue) {
		// Only update if changed since last time.
		if (newvalue != this.LastValue) {
			this.LastValue = newvalue;
			this.Numeric_ref.firstChild.data = newvalue;
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateText;

}
// End of object definition.

// ##################################################################

/*	Update a display of a floating point number with control of the number 
	of decimals displayed. This operates by changing the text property of 
	an SVG string.
	Parameters:
	svgdoc - Reference to SVG document.
	NumberID (string) - ID of SVG text item.
	Decimals (integer) - Number of decimal places.
*/
function MB_NumericFloatDisplay(svgdoc, NumberID, Decimals){

	this.Numeric_ref = svgdoc.getElementById(NumberID);	// Reference to numeric display.
	this.decimals = Decimals;

	// Initialise the last value.
	this.LastValue = null;

	function _UpdateText(newvalue) {
		// Only update if changed since last time.
		if (newvalue != this.LastValue) {
			this.LastValue = newvalue;
			this.Numeric_ref.firstChild.data = newvalue.toFixed(this.decimals);
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateText;

}
// End of object definition.


// ##################################################################

/*	Update a display of a string. This operates by changing the
	text property of an SVG string.
	Parameters:
	svgdoc - Reference to SVG document.
	NumberID (string) - ID of SVG text item.
*/
function MB_StringDisplay(svgdoc, NumberID){

	this.String_ref = svgdoc.getElementById(NumberID);	// Reference to string display.

	// Initialise the last value.
	this.LastValue = null;

	function _UpdateText(newvalue) {
		// Only update if changed since last time.
		if (newvalue != this.LastValue) {
			this.LastValue = newvalue;
			this.String_ref.firstChild.data = newvalue;
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateText;

}
// End of object definition.



// ##################################################################

/*	Update a display of a text message. This operates by changing the
	text property of an SVG string.
	Parameters:
	svgdoc - Reference to SVG document.
	TextMsgID (string) - ID of SVG text item.
	MsgList (array) - Array of strings containing messages.
*/
function MB_TextDisplay(svgdoc, TextMsgID, MsgList){

	this.Text_ref = svgdoc.getElementById(TextMsgID);	// Reference to numeric display.
	this.TextMsgList = MsgList;				// List of text messages.

	// Initialise the last value.
	this.LastValue = null;

	function _UpdateText(newvalue) {
		// Only update if changed since last time.
		if (newvalue != this.LastValue) {
			this.LastValue = newvalue;
			this.Text_ref.firstChild.data = this.TextMsgList[newvalue];
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateText;

}
// End of object definition.

// ##################################################################

/*	Implement a numer entry pad.
	This does not use the display list.
	Parameters:
	svgdoc - Reference to SVG document.
	NumberID (string) - ID of SVG text item.
	MaxDigits (integer) - Maximum number of digits permitted.
*/
function MB_NumericPad(svgdoc, NumberID, MaxDigits){

	this.Numeric_ref = svgdoc.getElementById(NumberID);	// Reference to numeric display.
	this.MaxDigits = MaxDigits;	// Maximum number of digits permitted.

	// Current entry value.
	this.Currentvalue = "";
	this.DecimalSet = false;
	this.Sign = '+';

	// Append the newest value.
	function _AppendDigit(newdigit) {
		if ((newdigit in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) &&
			(this.Currentvalue.length < this.MaxDigits)) {
			this.Currentvalue = this.Currentvalue + newdigit;
		}
		else if ((newdigit == '.') && (!this.DecimalSet)) {
			this.Currentvalue = this.Currentvalue + newdigit;
			this.DecimalSet = true;
		}
		else if ((newdigit == '-') && (this.Sign == '+')) {
			this.Sign = '-';
		}
		else if ((newdigit == '-') && (this.Sign == '-')) {
			this.Sign = '+';
		}

		this.Numeric_ref.firstChild.data = this.Sign + this.Currentvalue;
	}

	// Clear the current value.
	function _ClearDisplay() {
		this.Currentvalue = "";
		this.DecimalSet = false;
		this.Sign = '+';
		this.Numeric_ref.firstChild.data = this.Sign + this.Currentvalue;
	}

	// Return the current value as an integer.
	function _GetValueInt() {
		return parseInt(this.Sign + this.Currentvalue, 10);
	}

	// Return the current value as a floating point value.
	function _GetValueFloat() {
		return parseFloat(this.Sign + this.Currentvalue);
	}

	// Reference the functions to make them public.
	this.AppendDigit = _AppendDigit;
	this.ClearDisplay = _ClearDisplay;
	this.GetValueInt = _GetValueInt;
	this.GetValueFloat = _GetValueFloat;

}
// End of object definition.


// ##################################################################

/* 	Dial Gauge Indicator Control.
	Parameters:
	svgdoc - Reference to SVG document.
	DialID (string) - ID of SVG item.
	dialoffset (integer) - Minimum angle for dial.
	offset (float) - Offset to apply to reading.
	gain (float) - Gain factor to apply to reading.

*/
function MB_DialGauge(svgdoc, DialID, dialoffset, offset, gain) {

	this.Dial_ref = svgdoc.getElementById(DialID);	// Reference to dial pointer.
	this.dialoffset = dialoffset;	// Minimum angle for dial.
	this.offset = offset; 		// Offset to add to reading.
	this.gain = gain;		// Gain factor to multiply reading by.


	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. */
	function _UpdateDial(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			// Rotate the pointer.
			newangle = (state + this.offset) * this.gain + this.dialoffset;
			this.Dial_ref.setAttribute("transform", "rotate(" + newangle +")");
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateDial;

}
// End of object definition.


// ##################################################################

/* 	Tank level control. This operates by adjusting the linear gradient
	that is used to fill a "tank" (any closed SVG object).
	Parameters:
	svgdoc - Reference to SVG document.
	TankID1 (string) - ID of first gradient stop in SVG item.
	TankID2 (string) - ID of second gradient stop in SVG item.
*/
function MB_TankLevel(svgdoc, TankID1, TankID2) {

	this.Tank_ref1 = svgdoc.getElementById(TankID1);	// Reference to first gradient stop.
	this.Tank_ref2 = svgdoc.getElementById(TankID2);	// Reference to second gradient stop.

	// Initialise the last state.
	this.LastFillLevel = null;

	// When first initialised, the gradients are shown with the maximum
	// degree of shading.
	this.Tank_ref1.setAttribute("offset", "0" + "%");
	this.Tank_ref2.setAttribute("offset", "100" + "%");

	/* Update the current display state. 
	filllevel = tank fill level in % (0 to 100).
	*/
	function _UpdateTankLevel(filllevel) {
		// Only update if changed since last time.
		if (filllevel != this.LastFillLevel) {
			this.LastFillLevel = filllevel;
		
			this.Tank_ref1.setAttribute("offset", filllevel + "%");
			this.Tank_ref2.setAttribute("offset", filllevel + "%");
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateTankLevel;

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

/* 	Indicate conditions in pipes or ducts. This operates by adjusting the 
	fill colour according to whether the value being monitored is zero or not.
	Parameters:
	svgdoc - Reference to SVG document.
	PipeID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	offcolour (string) - Colour to use when zero.
	oncolour (string) - Colour to use when not zero.
*/
function MB_Pipe2(svgdoc, PipeID, initcolour, offcolour, oncolour) {

	this.Pipe_ref = svgdoc.getElementById(PipeID);	// Reference to pipe.
	this.Pipe_offcolour = offcolour;		// Colour to use when off.
	this.Pipe_oncolour = oncolour;			// Colour to use when on.
	this.Pipe_initcolour = initcolour;		// Colour to use when undefined.

	// Initialise the last state.
	this.LastState = null;

	/* Update the current display state. 
	Parameters: flowing (integer) - 0 = stopped. non-zero = flowing.
	*/
	function _UpdatePipe2(flowing) {
		// Only update if changed since last time.
		if (flowing != this.LastState) {
			this.LastState = flowing;
			if (flowing == 0) { 
				this.Pipe_ref.setAttribute('fill', this.Pipe_offcolour);
			}
			else {
				this.Pipe_ref.setAttribute('fill', this.Pipe_oncolour);
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePipe2;

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

/* 	Pump or fan control. This operates by rotating the "pump" (any SVG object).
	Parameters:
	svgdoc - Reference to SVG document.
	PumpID (string) - ID of pump SVG item.
	rotation (integer) - Number of degrees to rotate each time. 
		From -360 to 360. +ve = cw. -ve = ccw.
*/
function MB_PumpRotate(svgdoc, PumpID, rotation) {

	this.Pump = svgdoc.getElementById(PumpID);	// Reference to pump.
	this.Rotation = rotation;			// Amount and direction to rotate
	this.PumpAngle = 0;				// Last pump rotation angle.


	/* Update the current display state. 
	Parameters: direction (integer) - 0 = stopped. +ve = cw. -ve = ccw.
	*/
	function _UpdatePumpRotate(direction) {
		// Pump is stopped.
		if (direction == 0) {
			return;
		}

		// Pump is going cw.
		if (direction > 0) {
			this.PumpAngle = this.PumpAngle + this.Rotation;
		}
		// Pump is going ccw.
		else if (direction < 0) {
			this.PumpAngle = this.PumpAngle - this.Rotation;
		}

		// We limit the rotation angle to keep it from winding up.
		if ((this.PumpAngle > 360) || (this.PumpAngle < -360)){
			this.PumpAngle = 0
		}

		// Rotate the pump.
		this.Pump.setAttribute("transform", "rotate(" + this.PumpAngle +")");
	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePumpRotate;

}
// End of object definition.

// ##################################################################

/*	Update a strip chart. This operates by changing the points property of 
	an SVG polyline.
	Parameters:
	svgdoc - Reference to SVG document.
	ChartID (string) - ID of SVG polyline.
	MaxPoints (integer) - Maximum number of chart points.
	XInc (integer) - Increment for each X position.
	YScale (integer) - Scale factor to apply to readings.
	TimeInc (float) - Minimum time increment in seconds.
*/
function MB_StripChart(svgdoc, ChartID, MaxPoints, XInc, YScale, TimeInterval){

	this.Chart_ref = svgdoc.getElementById(ChartID);	// Reference to chart.
	this.MaxPoints = MaxPoints;
	this.ChartData = [];
	this.XInc = XInc;
	this.YScale = YScale;
	this.TimeInterval = TimeInterval * 1000.0;	// Convert to milliseconds.

	this.ChartStr = "";	// String used to update the chart points.
	this.LastTime = 0.0;

	function _UpdateChart(newvalue) {
		// Check to see if the minimum timer interval has passed.
		var IntervalTimer = new Date();
		if ((IntervalTimer.getTime() - this.LastTime) < this.TimeInterval) {
			return;
		}
		this.LastTime = IntervalTimer.getTime();

		// Add the new value to the end of the array.
		this.ChartData.push((newvalue * -1) * this.YScale);
		// Check if the array has reached the maximum length.
		if (this.ChartData.length > this.MaxPoints) {
			this.ChartData.shift();
		}

		this.ChartStr = "";
		// Update the chart.
		for (var i = 0; i < this.ChartData.length; i++) {
			this.ChartStr = this.ChartStr + " " + (this.XInc * i) + "," + this.ChartData[i];
		}

		// Update the web page.
		this.Chart_ref.setAttribute('points', this.ChartStr);

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateChart;

}
// End of object definition.


// ##################################################################

/*	Select an SVG image from a list (array) of images. Each image
	must have a unique "id" string. This function hides or displays
	different parts to display only one at a time.
	This is compatible with the display list.
	Parameters: 
	pagedoc - A reference to the HTML document.
	graphictable (array) - An array of strings containing the ids of
		the SVG graphic images.
	tableoffset (integer) - This value is added to the monitored value in
		determining the index for the "graphictable". This allows
		data ranges which do not start at zero to be used directly
		as image selectors (e.g. such as 3 position selector switches).
*/

function MB_GraphicSelect(pagedoc, graphictable, tableoffset) {

	this.PageDoc = pagedoc;
	this.GraphicTable = graphictable;
	this.NumbImages = this.GraphicTable.length;
	this.TableOffset = tableoffset;
	this.ImageRef = [];

	// Make a table of references to each image, and turn 
	// the display mode off for each.
	for (i = 0; i < this.NumbImages; i++) {
		var imagestr = this.GraphicTable[i];
		this.ImageRef.push(this.PageDoc.getElementById(imagestr))
		this.ImageRef[i].style.display = "none";
	}

	// Initialise the last state.
	this.LastState = null;

	// Select a new image.
	//	Parameters: imageindex (integer) - The index of the new image in 
	//		the graphictable array.	

	function _SelectImage(imageindex) {
		// Only update if changed since last time.
		if (imageindex != this.LastState) {
			// First, turn off the old image.
			if (this.LastState == null) {
				this.LastState = 0;
			}
			this.ImageRef[this.LastState + this.TableOffset].style.display = "none";

			// Check if the image is within range.
			var offsetindex = imageindex + this.TableOffset;
			if ((offsetindex >= 0) && (offsetindex < this.NumbImages)) {
				// Show the new image.
				this.ImageRef[offsetindex].style.display = "block";
				// Save the new index.
				this.LastState = imageindex;
			}
		}
	}

	// Reference the function to make it public.
	this.UpdateScreen = _SelectImage;

}
// End of object definition.


// ##################################################################

/*	Display or hide an SVG image. 0 = hide the image. 1 = Show the image.
	This is compatible with the display list.
	Parameters: 
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
*/

function MB_GraphicShowHide(svgdoc, GraphicId) {

	this.graphicid = svgdoc.getElementById(GraphicId);	// Reference to graphic.
	this.graphicid.style.display = "none";

	// Initialise the last state.
	this.LastState = null;

	// Enables or disabled showing the item.
	function _UpdateGraphic(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			if (state == 0) {
				this.graphicid.style.display = "none";
			} else {
				this.graphicid.style.display = "block";
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateGraphic;

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

/*	Select which HMI "screens" are visible. The "screens" are all parts of 
	the same xhtml document. This function hides or displays different
	parts to give the illusion of different screens being selected.
	Parameters: 
	pagedoc - A reference to the HTML document.
	screentable (array) - An array of strings containing the ids of
		the screen divs.
*/

function MB_ScreenSelect(pagedoc, screentable) {

	this.PageDoc = pagedoc;
	this.ScreenTable = screentable;


	/* Select a new screen.
		Parameters: screenname (string) - The id of the new screen.
	*/
	function _SelectScreen(screenname) {
		// First, turn off all the screens.
		var numbscreens = this.ScreenTable.length;
		for (i = 0; i < numbscreens; i++) {
			var screenstr = this.ScreenTable[i];
			var screenref = this.PageDoc.getElementById(screenstr);
			screenref.style.display = "none";
		}
		// Now, turn on the selected screen.
		var screenref = this.PageDoc.getElementById(screenname);
		screenref.style.display = "block";
	}

	// Reference the function to make it public.
	this.SelectScreen = _SelectScreen;


}
// End of object definition.

// ##################################################################

