/** ##########################################################################
# Project: 	libmbhmi
# Module: 	libmbhmimisc.js
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
This library is intended to provide useful functions for a web based HMI, as
well as acting as an example for how to write additional functions should
they be required. It is assumed that you know how to create a web page,
and know something about Javascript, CSS, and SVG. If you are using SVG
graphics, you must create the page as an xhtml page rather than an ordinary
html page as html (at least html 4) does not support in-line SVG.

MB_ScreenSelect

MB_NumericPad

MB_SlideDisplay
MB_StripChart
MB_GraphicSelect
MB_GraphicShowHide


These objects fall into the following categories:

##########################################################################

Control of the screen display:

An "AJAX" type web application is usually all in one page because (for security 
reasons) there is no easy way for applications in different web pages to 
communicate with each other. However, a web application can give the appearance 
of having different pages (referred to as HMI "screens" here) by hiding and 
revealing different parts of a single page. MB_ScreenSelect can be used to 
easily control this process. 

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


##########################################################################


MB_NumericPad provides a function which allows digits 0 to 9, '-', and '.' 
to be entered. It also  provides functions to clear the current value, and 
to retrieve the current value as an integer or as a float. It also automatically 
updates an SVG text display to show the current value.

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



##########################################################################

MB_StripChart
MB_GraphicSelect
MB_GraphicShowHide
MB_SlideDisplay

These code objects are compatible with the Cascadas "display list", as they
export and "UpdateScreen" method which accepts a single parameter.

example - 

MB_StripChart changes the "points" propery in a polyline.

MB_GraphicShowHide is used to display or hide an SVG graphic. This can be used
to enable or disable an input button by putting another "mask" graphic
over top of the button and then showing or hiding the mask.

MB_GraphicSelect is similar to MB_GraphicShowHide, but selects one graphic at
a time out of a list of several.

MB_SlideDisplay will translate (slide or move) an element to one of two
positions, depending the whether the monitored value is on or off. This
is primarily useful with custom graphics.

##########################################################################

*/



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

	// Reference to stripchart display.
	containerref = svgdoc.getElementById(ChartID);
	// We need to look for the polyline elements.
	polylineref = containerref.getElementsByTagName('polyline');
	this.Chart_ref = polylineref[0];


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

