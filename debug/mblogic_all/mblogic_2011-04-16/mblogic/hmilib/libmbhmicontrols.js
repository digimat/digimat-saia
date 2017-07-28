/** ##########################################################################
# Project: 	libmbhmi
# Module: 	libmbhmicontrols.js
# Purpose: 	HMI library functions for use with Cascadas.
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		05-Dec-2010
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

1) Pilot lights:
2) Selector switches:
3) Text and numeric display:
4) Miscellaneous displays:


Despite such names as "pilot light" and "tank", they are not restricted to 
controlling those shapes only. Since the graphics are completely under user 
control, the actual shape of the graphics can be anything, so that "MB_TankLevel" 
might be used for example to simulate a column gauge.

These code objects are compatible with the Cascadas "display list", as they
export and "UpdateScreen" method which accepts a single parameter.



	#########################################

1) Pilot lights:

MB_PilotLight
	- Manipulates the "fill" property of the SVG graphics to display two colours.

MB_PLMultiColour
	- Manipulates the "fill" property of the SVG graphics to display one of a
	list of colours.

MB_PilotLightStat
	- Like MB_PilotLight, but gets its data from the "stat" field of the
	Cascadas protocol message.

MB_PilotLightFlashTransform
	- Flashes between two colours using animation. 


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

example - 

MB_TextDisplay displays a text message by selecting an element from an array of 
strings according to a numeric array index. For example - 

	var ColourList = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]; 
	var PL4 = new MB_PLMultiColour(document, "PL4", "black", ColourList);


	#########################################

2) Selector switches:

MB_2PosSSDisplay
	- Rotates the operator to display the state of a two position selector 
	switch. This is the *output* action of the selector switch. The *input*
	action is handled using push button-like functions integrated into the
	switch. 

MB_3PosSSDisplay
	- Like MB_2PosSSDisplay, but for three position switches.


	#########################################

3) Text and numeric display:

MB_NumericDisplay
	- Displays numeric values.

MB_NumericFloatDisplay
	- Like MB_NumericDisplay, but includes a decimal point.

MB_StringDisplay
	- Like MB_NumericDisplay, but for strings.

MB_TextDisplay
	- displays a text message by selecting an element from an array of 
	strings according to a numeric array index. For example - 

example - 
	var ColourList = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]; 
	var PL4 = new MB_PLMultiColour(document, "PL4", "black", ColourList);


	#########################################

4) Miscellaneous displays:

MB_DialGauge
	- Manipulates the "rotate" property to allow a dial pointer to be 
	rotated to reflect the current data.

MB_TankLevel
	- Manipulate the "offset" property in linear gradients to give the
	appearance of a vessel filling.

MB_Pipe2
	- Manipulates the fill status like a pilot light.

MB_PumpRotate
	- Rotates an element. Unlike MB_DialGauge, the rotation is incremental, 
	meaning it will rotate each cycle, giving a simple form of animation.

MB_PumpRotateAnimated
	- Provides an animated rotation that does not depend on the scan rate.


MB_TankLevel manipulate the "offset" property in linear gradients, which in 
turn can affect the appearance of other SVG graphics. Since a single gradient 
can be assigned to more than one SVG graphic, this can produce coordinated 
changes in several graphics. With MB_TankLevel, the gradient is set to follow 
the tag is is associated with. 

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


	#########################################

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
		value, the light will turn "off", otherwise, it will turn "on".
		Any value not equal to the comparison value is considered to be
		the result of a condition which must be indicated.
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
	initcolour (string) - Colour to use when undefined.
	offcolour (string) - Colour to use when off.
	oncolour (string) - Colour to use when on.
	okstat (string) - Value to compare to for "ok". This should be a constant.

*/
function MB_PilotLightStat(svgdoc, PLID, initcolour, offcolour, oncolour, okstat) {

	this.PL_offcolour = offcolour;			// Colour to use when off.
	this.PL_oncolour = oncolour;			// Colour to use when on.
	this.PL_initcolour = initcolour;		// Colour to use when undefined.
	this.PL_ref = svgdoc.getElementById(PLID);	// Reference to pilot light.
	this.PL_OKStatus = okstat;			// Comparison value.

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
			if (state == this.PL_OKStatus) {
				this.PL_ref.setAttribute('fill', this.PL_offcolour);
			} else {
				this.PL_ref.setAttribute('fill', this.PL_oncolour);
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdatePilotLight;

}
// End of object definition.



// ##################################################################
/* 	Flashing pilot light control. The flashing does not depend on
	the scan rate. 
	This uses the SVG animateTransform property. 
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
*/
function MB_PilotLightFlashTransform(svgdoc, PLID) {

	// Reference to SVG element.
	this.Element_ref = svgdoc.getElementById(PLID);
	// Reference to animation.
	var animator = this.Element_ref.getElementsByTagName('animateTransform');
	this.animator = animator[0];
	// Turn the animation off.
	try {
		this.animator.endElement();
	// Supress errors for browsers which do not support animation.
	} catch (e) { };

	// Initialise the last state.
	this.LastState = null;


	// Update the current display state. state (integer) - 0 = off. 1 = on.
	function _UpdateAnimation(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			try {
				if (state == 0) {
					this.animator.endElement();
				} else {
					this.animator.beginElement();
				}
			// Supress errors for browsers which do not support animation.
			} catch (e) { };
		}
	}
	// Reference the function to make it public.
	this.UpdateScreen = _UpdateAnimation;

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
/* 	Animated pump rotation control. This provides a smooth continuous
	animation that does not depend on the scan rate. The rotation is
	on or off, and in one direction only. 
	This uses the SVG animateTransform property. 
	Parameters:
	svgdoc - Reference to SVG document.
	PLID (string) - ID of SVG item.
*/
function MB_PumpRotateAnimated(svgdoc, PumpID) {

	// Reference to SVG element.
	this.Element_ref = svgdoc.getElementById(PumpID);
	// Reference to animation.
	var animator = this.Element_ref.getElementsByTagName('animateTransform');
	this.animator = animator[0];
	// Turn the animation off.
	try {
		this.animator.endElement();
	// Supress errors for browsers which do not support animation.
	} catch (e) { };

	// Initialise the last state.
	this.LastState = null;


	// Update the current display state. state (integer) - 0 = off. 1 = on.
	function _UpdateAnimation(state) {
		// Only update if changed since last time.
		if (state != this.LastState) {
			this.LastState = state;
			try {
				if (state == 0) {
					this.animator.endElement();
				} else {
					this.animator.beginElement();
				}
			// Supress errors for browsers which do not support animation.
			} catch (e) { };
		}
	}
	// Reference the function to make it public.
	this.UpdateScreen = _UpdateAnimation;

}
// End of object definition.



// ##################################################################

