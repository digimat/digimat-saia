/** ##########################################################################
# Project: 	libmbevents
# Module: 	libmbevents.js
# Purpose: 	HMI library functions for use with Cascadas.
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		05-Feb-2011.
# Author:	M. Griffin.
# Copyright:	2008 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
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

This version implements the new style alarms.

The functions here fall into the following categories - 

#####################################################################

A) Objects to handle events and alarms. These require that certain HTML tables 
already exist for them to be associated with. They then add and remove rows of 
data to or from these tables to display events, alarms, and alarm history.

Events and alarms messages are generated at the server and transported
over the HMI protocol. The Javascript library is used to display these
messages in the web browser.

=====================================================================

1) Display HMI "events" on an HTML screen. "Events" is the standard
term for occurances which an operator must be notified of, but
which does not require acknowledgement. 
Parameters: 
	eventdoc - A reference to the HTML document.
	eventtableID (string) - The id of the html table used to display events.
	maxlength (integer) - The maximum number of rows to display.
	eventtexts (array) - An array of strings with the event messages.

function MB_EventDisplay(eventdoc, eventtableID, maxlength, eventtexts)


MB_EventDisplay requires one table with four columns. For example - 

<table id="EventDisplay" border="5" cellpadding="5">
<tr>
<td><b>Event #:</b></td> 
<td><b>Date:</b></td> 
<td><b>Event:</b></td> 
<td><b>State:</b></td>
</tr>
</table>

The first column will be the Event number. The second column is the date, the
third column is the event name, and the fourth column is the event state.
These column assignments are fixed, and cannot be changed without editing 
the code.

The Javascript code to display events is shown below.

// This is to display the events.
var EventDisplay = new MB_EventDisplay(document, "EventDisplay", 50, event_text);
// Add this to the display list.
MBHMIProtocol.AddToDisplayList(EventDisplay, "events", "events");


The texts displayed on the screen are not carried in the actual messages, but must 
be provided by the client. The messages are expected to be in object literals with 
the message tags acting as keys to the actual messages. An easy way of implementing 
this is to put the messages into external Javascript files containing just the data 
definitions. For example:

event_text = {
"PumpRunning" : "Tank pump is running.",
"PumpStopped" : "Tank pump is stopped.",
"Tank1Empty" : "Tank 1 is empty.",
"Tank1Full" : "Tank 1 is full.",
"Tank2Empty" : "Tank 2 is empty.",
"Tank2Full" : "Tank 2 is full."
}

=====================================================================

2) Display HMI "alarms" on an HTML screen. "Alarms" is the standard
term for occurances which an operator must be notified of, and which
*must* be acknowledged. 
Parameters: 
	alarmdoc - A reference to the HTML document.
	alarmtableID (string) - The id of the html table used to display alarms.
	alarmtexts (object) - An object of strings with the alarm messages.
	alarmstatetexts (object) - An object of strings with the alarm states.
	alarmcolour (string) - The HML colour to indicate alarm conditions.
	ackcolour (string) - The HML colour to indicate acknowledged conditions.
	okcolour (string) - The HML colour to indicate OK conditions.

function MB_AlarmDisplay(alarmdoc, alarmtableID, alarmtexts, alarmstatetexts,
	alarmcolour, ackcolour, okcolour)


MB_AlarmDisplay requires one table with five columns. For example - 

<table id="AlarmDisplay" border="5" cellpadding="5">
<tr> 
<td><b>Alarm:</b></td>
<td><b>Alarm State:</b></td>
<td><b>Time:</b></td> 
<td><b>Time OK:</b></td> 
<td><b>Count:</b></td>
</tr>
</table>

The first column will display the name of the alarm. The second column
will display the alarm state. The third column will display the time at
which the fault was detected. The fourth column will display the time
at which the fault became OK. The fifth column will display the number of
times the fault occured while the alarm was displayed.

The Javascript code to display alarms is shown below.

// This is to display the alarms.
var AlarmDisplay = new MB_AlarmDisplay(document, "AlarmDisplay", 
	alarm_text, alarmstates_text, "red", "orange", "green");
// Add this to the display list.
MBHMIProtocol.AddToDisplayList(AlarmDisplay, "alarms", "alarms");


The texts displayed on the screen are not carried in the actual messages, but must 
be provided by the client. The messages are expected to be in object literals with 
the message tags acting as keys to the actual messages. An easy way of implementing 
this is to put the messages into external Javascript files containing just the data 
definitions. For example:

alarm_text = {
"PB1Alarm" : "PB1 was pressed.",
"PB2Alarm" : "PB2 was pressed.",
"PB3Alarm" : "PB3 was pressed.",
"PB4Alarm" : "PB4 was pressed."
}

The texts used to describe the alarm states are not carried in the actual messages, 
but must be provided by the client. The messages are expected to be in object 
literals with the message tags acting as keys to the actual messages. An easy way of 
implementing this is to put the messages into external Javascript files containing 
just the data definitions. For example:

alarmstates_text = {
"alarm" : "Fault is active",
"ackalarm" : "Alarm acknowledged",
"ok" : "Fault cleared",
"ackok" : "Fault cleared and acknowledged",
"inactive" : "Alarm inactive"
}


MB_AlarmDisplay does not provide a function to input the alarm acknowledge action. 
However an appropriate function is provided in the libhmiclient library which can be
attached to a button on the screen.


<!-- Push button to acknowledge alarms. -->
<g transform="translate(50, 10)" onclick="MBHMIProtocol.AddAlarmAck();">

	<!-- Put some SVG or other suitable mark up in here to display a button -->

</g>

=====================================================================

2) Display HMI "alarm history" on an HTML screen. "Alarms" is the standard
term for occurances which an operator must be notified of and
acknowledge. Alarm history is a record of past alarms.
Parameters: 
	alarmhistorydoc - A reference to the HTML document.
	alarmhistorytableID (string) - The id of the html table used to 
		display alarm history.
	maxlength (integer) - The maximum number of rows to display.
	alarmtexts (array) - An array of strings with the alarm messages.


function MB_AlarmHistoryDisplay(alarmhistorydoc, alarmhistorytableID, maxlength, alarmtexts)


MB_AlarmHistoryDisplay requires one table with four columns. For example - 

<table id="AlarmHistoryDisplay" border="5" cellpadding="5">
<tr>
<td><b>Alarm:</b></td>
<td><b>Alarm Time:</b></td> 
<td><b>Time OK:</b></td> 
<td><b>Ack By:</b></td> 
</tr>
</table>


The first column is the alarm name. The second column will display the time at
which the fault was detected. The third column will display the time
at which the fault became OK. The fourth column will display who (which client ID) 
acknowledged the alarm.

The Javascript code to display alarm history is shown below.

// This is to display the alarm history.
var AlarmHistoryDisplay = new MB_AlarmHistoryDisplay(document, 
	"AlarmHistoryDisplay", 50, alarm_text);
// Add this to the display list.
MBHMIProtocol.AddToDisplayList(AlarmHistoryDisplay, "alarmhistory", "alarmhistory");

The texts displayed on the screen are not carried in the actual messages, but must 
be provided by the client. The messages are expected to be in object literals with 
the message tags acting as keys to the actual messages. An easy way of implementing 
this is to put the messages into external Javascript files containing just the data 
definitions. For example:

alarm_text = {
"PB1Alarm" : "PB1 was pressed.",
"PB2Alarm" : "PB2 was pressed.",
"PB3Alarm" : "PB3 was pressed.",
"PB4Alarm" : "PB4 was pressed."
}


=====================================================================

#####################################################################

B) Objects to display protocol errors and communications status in HTML tables. 
These include MB_TagErrorDisplay and MB_StatusLogDisplay. These require that 
certain HTML tables already exist for them to be associated with. They then add 
and remove rows of data to or from these tables to display logs of communications 
errors.

Errors and communication status are generated at the server and transported
over the HMI protocol. The Javascript library is used to display these
messages in the web browser.


Errors and communications status are not buffered in the server. Reloading
the browser will cause the existing record to be erased.

=====================================================================

1) Display protocol errors on an HTML screen. 
Parameters: 
	errordoc - A reference to the HTML document.
	errortableID (string) - The id of the html table used to display errors.
	maxlength (integer) - The maximum number of rows to display.
	errortexts (array) - An object with the error messages.

function MB_TagErrorDisplay(errordoc, errortableID, maxlength, errortexts)


MB_TagErrorDisplay requires one table with three columns. For example - 

<p><h2>Communications Errors:</h2>
<table id="ErrorDisplay" border="5" cellpadding="5">
<tr>
<td><b>Date:</b></td> 
<td><b>Tag:</b></td> 
<td><b>Error:</b></td>
</tr>
</table>
</p>

The first column will be the current date and time. The second column is the name
of the tag which encountered an error, and the third column is the text description
of the error. These column assignments are fixed, and cannot be changed without editing 
the source code.

The Javascript to display communications errors is shown below.

// This is to display the communications errors.
var ErrorDisplay = new MB_TagErrorDisplay(document, "ErrorDisplay", 50, error_text);
// Add this to the display list.
MBHMIProtocol.AddToDisplayList(ErrorDisplay, "errors", "errors");


The text for the descriptions are not carried in the actual messages, but must 
be provided by the client. The text of the descriptions are expected to be in 
object literals with the message tags acting as keys to the actual messages. 
An easy way of implementing this is to put the messages into external Javascript 
files containing just the data definitions. For example

error_text = {"tagnotfound" : "The address tag is not recognised by the server.",
"badtype" : "The data value is of an incompatible type.",
"outofrange" : "The data value is out of range.",
"writeprotected" : "An attempt was made to write to an address which is write 
	protected or otherwise not writable.",
"addresserror" : "An error occurred in attempting to map the tag to the 
	internal server address representation.",
"servererror" : "An unspecified error has occurred in the server which prevents 
	the request from being completed.",
"accessdenied" : "The client does not have authorisation to access this tag. "
}

=====================================================================

2) Display protocol status conditions on an HTML screen. 
Parameters: 
	statusdoc - A reference to the HTML document.
	statustableID (string) - The id of the html table used to display status.
	maxlength (integer) - The maximum number of rows to display.
	statustexts (array) - An object with the status messages.

function MB_StatusLogDisplay(statusdoc, statustableID, maxlength, statustexts)


MB_StatusLogDisplay requires one table with three columns. For example - 

<p><h2>Communications Status:</h2>
<table id="StatusDisplay" border="5" cellpadding="5">
<tr>
<td><b>Date:</b></td> 
<td><b>Status Code:</b></td> 
<td><b>Status:</b></td>
</tr>
</table>
</p>


The first column will be the current date and time. The second column is the name
of the status code, and the third column is the text description of the status code. 
These column assignments are fixed, and cannot be changed without editing 
the source code.

The Javascript to display the communications status log is shown below.

// This is to display the communications status log.
var StatusLogDisplay = new MB_StatusLogDisplay(document, "StatusDisplay", 50, status_text);
// Add this to the display list.
MBHMIProtocol.AddToDisplayList(StatusLogDisplay, "status", "status");


The text for the descriptions are not carried in the actual messages, but must 
be provided by the client. The text of the descriptions are expected to be in 
object literals with the message tags acting as keys to the actual messages. 
An easy way of implementing this is to put the messages into external Javascript 
files containing just the data definitions. For example

status_text = {
"ok" : "No errors.",
"protocolerror" : "An error was encountered in the protocol and the entire message 
	was discarded by the server.",
"commanderror" : "A request command field provided incorrect or invalid data.",
"servererror" : "An unspecified error has occurred in the server which prevents 
	the request from being completed.",
"unauthorised" : "The client is not authorised to communicate with this server.",
"noclistempty" : "The client attempted to read using NOC without an NOC list being 
	present in the server."
}

=====================================================================

*/


// ##################################################################

/*	Display HMI "events" on an HTML screen. "Events" is the standard
	term for occurances which an operator must be notified of, but
	which does not require acknowledgement. 
	Parameters: eventdoc - A reference to the HTML document.
	eventtableID (string) - The id of the html table used to display events.
	maxlength (integer) - The maximum number of rows to display.
	eventtexts (array) - An array of strings with the event messages.
*/

function MB_EventDisplay(eventdoc, eventtableID, maxlength, eventtexts) {

	// Reference to table for event display.
	this.EventTable = eventdoc.getElementById(eventtableID);
	// Serial number of last event displayed.
	this.LastEvent = 0;
	// Maximum length (in rows) allowed for the event table display.
	this.MaxLength = maxlength;
	// Current actual length of the table.
	this.ActualLength = 0;

	// The actual event text messages.
	this.EventTexts = eventtexts;

	// Format a date for display.
	// Cascadas operates in UTC time.
	function _FormatDate(msgdate) {
		var serverdate = new Date();
		// Convert seconds to milliseconds, and to local time.
		serverdate.setTime(msgdate * 1000.0);
		return serverdate;
	}

	/* Update the current display state. 
	Parameters: eventbuff (array) - An array with the new events.
	*/
	function _UpdateHMIEvents(eventbuff) {

		// If there are no events, we can quit right here.
		try { 
			if (eventbuff.length == 0) {
				return;
			}
		}
		catch (e) {return;}


		/* Extract the serial number from the last (newest) record so 
		we can check if the newest event has already been displayed. */
		try {
			var serialnum = eventbuff[eventbuff.length - 1]["serial"];
			if (this.LastEvent >= serialnum) {return;}
		}
		catch (e) {return;}


		/* Now loop through the buffer, and fill in the records in
		the display table. */
		for (i in eventbuff) {
			var serialnum = eventbuff[i]["serial"];
			/* check if this message has already been displayed.
			We do this by comparing the serial number to see if it 
			is larger than the last displayed one.
			*/
			if (serialnum > this.LastEvent) {
				var eventtag = eventbuff[i]["event"];
				var timestamp = eventbuff[i]["timestamp"];
				var statevalue = eventbuff[i]["value"];
				
				// Format the date for display.
				var datedisplay = _FormatDate(timestamp);

				// Get the actual event texts.
				var eventmsg = this.EventTexts[eventtag];
				

				// Add a new row to the top row of the document. 
				var newrow = this.EventTable.insertRow(1);
				// Add the cells.
				var newserial = newrow.insertCell(0);
				var newdate = newrow.insertCell(1);
				var newmessage = newrow.insertCell(2);
				var newstate = newrow.insertCell(3);


				// Now add the new text to each cell in the top row.
				newserial.innerHTML = serialnum;
				newdate.innerHTML = datedisplay;
				newmessage.innerHTML = eventmsg;
				newstate.innerHTML = statevalue;

				// If the table has exceeded its maximum length,
				// delete the bottom row.
				if (this.ActualLength > this.MaxLength) {
					this.EventTable.deleteRow(-1);
				}
				else {
					this.ActualLength++;
				}

				// Now, save this new serial number as the highest.
				this.LastEvent = serialnum;
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateHMIEvents;


}
// End of object definition.


// ##################################################################

/*	Display HMI "alarm history" on an HTML screen. "Alarms" is the standard
	term for occurances which an operator must be notified of and
	acknowledge. Alarm history is a record of past alarms.
	Parameters: alarmhistorydoc - A reference to the HTML document.
	alarmhistorytableID (string) - The id of the html table used to 
		display alarm history.
	maxlength (integer) - The maximum number of rows to display.
	alarmtexts (array) - An array of strings with the alarm messages.
*/

function MB_AlarmHistoryDisplay(alarmhistorydoc, alarmhistorytableID, maxlength, alarmtexts) {

	// Reference to table for alarm history display.
	this.AlarmHistoryTable = alarmhistorydoc.getElementById(alarmhistorytableID);
	// Serial number of last alarm history message displayed.
	this.LastAlarmHistory = 0;
	// Maximum length (in rows) allowed for the alarm history table display.
	this.MaxLength = maxlength;
	// Current actual length of the table.
	this.ActualLength = 0;

	// The actual alarm text messages.
	this.AlarmTexts = alarmtexts;

	// Format a date for display.
	// Cascadas operates in UTC time.
	function _FormatDate(msgdate) {
		var serverdate = new Date();
		// Convert seconds to milliseconds, and to local time.
		serverdate.setTime(msgdate * 1000.0);
		return serverdate;
	}

	/* Update the current display state. 
	Parameters: alarmhistorybuff (array) - An array with the new alarm history.
	*/
	function _UpdateHMIAlarmHistory(alarmhistorybuff) {

		// If there are no alarm history messages, we can quit right here.
		try { 
			if (alarmhistorybuff.length == 0) {
				return;
			}
		}
		catch (e) {return;}


		/* Extract the serial number from the last (newest) record so 
		we can check if the newest alarm history has already been displayed. */
		try {
			var serialnum = alarmhistorybuff[alarmhistorybuff.length - 1]["serial"];
			if (this.LastAlarmHistory >= serialnum) {return;}
		}
		catch (e) {return;}


		/* Now loop through the buffer, and fill in the records in
		the display table. */
		for (i in alarmhistorybuff) {
			var serialnum = alarmhistorybuff[i]["serial"];
			/* check if this message has already been displayed.
			We do this by comparing the serial number to see if it 
			is larger than the last displayed one.
			*/
			if (serialnum > this.LastAlarmHistory) {
				// Get the actual alarm texts.
				alarmtag = alarmhistorybuff[i]["alarm"];
				var alarmmsg = this.AlarmTexts[alarmtag];

				// Get the other variables, and format any dates for display.
				var timestamp = _FormatDate(alarmhistorybuff[i]["time"]);
				var timeok = _FormatDate(alarmhistorybuff[i]["timeok"]);
				var ackby = alarmhistorybuff[i]["ackclient"];


				// Add a new row to the top row of the document. 
				newrow = this.AlarmHistoryTable.insertRow(1);
				// Add the cells.
				newalarmtag = newrow.insertCell(0);
				newtimestamp = newrow.insertCell(1);
				newtimeok = newrow.insertCell(2);
				newackby = newrow.insertCell(3);


				// Now add the new text to each cell in the top row.
				newalarmtag.innerHTML = alarmmsg;
				newtimestamp.innerHTML = timestamp;
				newtimeok.innerHTML = timeok;
				newackby.innerHTML = ackby;

				// If the table has exceeded its maximum length,
				// delete the bottom row.
				if (this.ActualLength > this.MaxLength) {
					this.AlarmHistoryTable.deleteRow(-1);
				}
				else {
					this.ActualLength++;
				}

				// Now, save this new serial number as the highest.
				this.LastAlarmHistory = serialnum;
			}
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateHMIAlarmHistory;


}
// End of object definition.



// ##################################################################

/*	Display HMI "alarms" on an HTML screen. "Alarms" is the standard
	term for occurances which an operator must be notified of, and which
	*must* be acknowledged. 
	Parameters: 
	alarmdoc - A reference to the HTML document.
	alarmtableID (string) - The id of the html table used to display alarms.
	alarmtexts (object) - An object of strings with the alarm messages.
	alarmstatetexts (object) - An object of strings with the alarm states.
	alarmcolour (string) - The HML colour to indicate alarm conditions.
	ackcolour (string) - The HML colour to indicate acknowledged conditions.
	okcolour (string) - The HML colour to indicate OK conditions.
*/
function MB_AlarmDisplay(alarmdoc, alarmtableID, alarmtexts, alarmstatetexts,
	alarmcolour, ackcolour, okcolour) {

	// Reference to table for alarm display.
	this.AlarmTable = alarmdoc.getElementById(alarmtableID);

	// The actual alarm text messages.
	this.AlarmTexts = alarmtexts;

	// The texts used to describe the alarm states.
	this.AlarmStateTexts = alarmstatetexts;

	// The colours to use for alarm display table backgrounds.
	this.AlarmColour = alarmcolour;
	this.AckColour = ackcolour;
	this.OkColour = okcolour;

	// Last screen update.
	this.LastAlarmDisplay = {};

	// Format a date for display.
	// Cascadas operates in UTC time.
	function _FormatDate(msgdate) {
		var serverdate = new Date();
		// Convert seconds to milliseconds, and to local time.
		serverdate.setTime(msgdate * 1000.0);
		return serverdate;
	}


	/* Display the alarms.
	Parameters: alarmbuff (array) - Array of new alarm messages.
	*/
	function _DisplayAlarms(alarmbuff) {

		
		// Check if there has been any new alarms or changes in the alarms.
		updated = false;
		for (i in alarmbuff) {
			// If this is a completely new alarm, there will be an exception
			// when we try to access it.
			try { 
				// Now compare each of the elements that we are monitoring.
				if (alarmbuff[i]["state"] != this.LastAlarmDisplay[i]["state"]) {
					updated = true; break;}
				if (alarmbuff[i]["time"] != this.LastAlarmDisplay[i]["time"]) {
					updated = true; break;}
				if (alarmbuff[i]["timeok"] != this.LastAlarmDisplay[i]["timeok"]) {
					updated = true; break;}
				if (alarmbuff[i]["count"] != this.LastAlarmDisplay[i]["count"]) {
					updated = true; break;}
			}
			catch (e) {
				updated = true;
				break;
			}
		}

		// Check to see if any of the alarms has disappeared. An exception
		// will be raised if the previous record has an alarm which isn't
		// present in the new one.
		for (i in this.LastAlarmDisplay) {
			try {
				dummy = alarmbuff[i]["state"];
			}
			catch (e) {
				updated = true;
				break;
			}
		}

		// If nothing has changed, then stop and return.
		if (!updated) {
			return;
		}
		

		// Save the new record for comparison.
		this.LastAlarmDisplay = alarmbuff;
		

		// First delete the existing table.
		while (true) {
			try {this.AlarmTable.deleteRow(1);}
			catch (e) {break;}
		}

		/* Now loop through the buffer, and fill in the records in
		the display table. */
		for (i in alarmbuff) {

			// Look up the alarm texts.
			var alarmmsg = this.AlarmTexts[i];

			// Look up the correct texts for the alarm state.
			var alarmstate = this.AlarmStateTexts[alarmbuff[i]["state"]]

			var alarmtime = _FormatDate(alarmbuff[i]["time"]);
			// There might be no OK time yet.
			if (alarmbuff[i]["timeok"] > 0.0) {
				var alarmtimeok = _FormatDate(alarmbuff[i]["timeok"]);
			}
			else {
				var alarmtimeok = "Not OK";
			}
			var alarmcount = alarmbuff[i]["count"];


			// Add a new row to the top row of the document. 
			newrow = this.AlarmTable.insertRow(1);

			// Set the background colour according to the state.
			switch(alarmbuff[i]["state"]) {
			case "alarm":
				newrow.style.backgroundColor = this.AlarmColour;
				break;
			case "ok":
				newrow.style.backgroundColor = this.OkColour;
				break;
			case "ackalarm":
				newrow.style.backgroundColor = this.AckColour;
				break;
			}


			// Add the cells.
			newalarmmsg = newrow.insertCell(0);
			newalarmstate = newrow.insertCell(1);
			newalarmtime = newrow.insertCell(2);
			newalarmtimeok = newrow.insertCell(3);
			newalarmcount = newrow.insertCell(4);


			// Now add the new text to each cell in the top row.
			newalarmmsg.innerHTML = alarmmsg;
			newalarmstate.innerHTML = alarmstate;
			newalarmtime.innerHTML = alarmtime;
			newalarmtimeok.innerHTML = alarmtimeok;
			newalarmcount.innerHTML = alarmcount;

			
		}

	}	// end of  _DisplayAlarms


	// Reference the function to make it public.
	this.UpdateScreen = _DisplayAlarms;


}
// End of object definition.


// ##################################################################

/*	Display protocol errors on an HTML screen. 
	Parameters: errordoc - A reference to the HTML document.
	errortableID (string) - The id of the html table used to display errors.
	maxlength (integer) - The maximum number of rows to display.
	errortexts (array) - An object with the error messages.
*/

function MB_TagErrorDisplay(errordoc, errortableID, maxlength, errortexts) {

	// Reference to table for error display.
	this.ErrorTable = errordoc.getElementById(errortableID);
	// Maximum length (in rows) allowed for the error table display.
	this.MaxLength = maxlength;
	// Current actual length of the table.
	this.ActualLength = 0;

	// The actual error text messages.
	this.ErrorTexts = errortexts;

	// Format a date for display.
	// Cascadas operates in UTC time.
	function _FormatDate(msgdate) {
		var serverdate = new Date();
		// Convert seconds to milliseconds, and to local time.
		serverdate.setTime(msgdate * 1000.0);
		return serverdate;
	}

	/* Update the current display state. 
	Parameters: errorbuff (array) - An array with the new errors.
	*/
	function _UpdateHMIErrors(errorbuff) {

		// If there are no errors, we can quit right here.
		try { 
			if (errorbuff.length == 0) {
				return;
			}
		}
		catch (e) {return;}


		// Check to see if the last (newest) record has already been displayed. 
		// If so, we can exit now. 
		try {
			if (errorbuff[errorbuff.length - 1]["displayed"]) {return;}
		}
		catch (e) {return;}


		/* Now loop through the buffer, and fill in the records in
		the display table. */
		for (i in errorbuff) {
			// Check if this error has already been displayed.
			if (! errorbuff[i]["displayed"]) {
				var timestamp = errorbuff[i]["timestamp"];
				var errortag = errorbuff[i]["tag"];
				var errorcode = errorbuff[i]["errors"];

				// Get the actual error texts.
				errormsg = this.ErrorTexts[errorcode];
				

				// Format the date for display.
				datedisplay = _FormatDate(timestamp);

				// Add a new row to the top row of the document. 
				newrow = this.ErrorTable.insertRow(1);
				// Add the cells.
				newdate = newrow.insertCell(0);
				newtag = newrow.insertCell(1);
				newerrormsg = newrow.insertCell(2);


				// Now add the new text to each cell in the top row.
				newdate.innerHTML = datedisplay;
				newtag.innerHTML = errortag;
				newerrormsg.innerHTML = errormsg;

				// Mark this record as having been displayed.
				errorbuff[i]["displayed"] = true;

				// If the table has exceeded its maximum length,
				// delete the bottom row.
				if (this.ActualLength > this.MaxLength) {
					this.ErrorTable.deleteRow(-1);
				}
				else {
					this.ActualLength++;
				}

			}
			
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateHMIErrors;


}
// End of object definition.

// ##################################################################

/*	Display protocol status conditions on an HTML screen. 
	Parameters: statusdoc - A reference to the HTML document.
	statustableID (string) - The id of the html table used to display status.
	maxlength (integer) - The maximum number of rows to display.
	statustexts (array) - An object with the status messages.
*/

function MB_StatusLogDisplay(statusdoc, statustableID, maxlength, statustexts) {

	// Reference to table for error display.
	this.StatusTable = statusdoc.getElementById(statustableID);
	// Maximum length (in rows) allowed for the status table display.
	this.MaxLength = maxlength;
	// Current actual length of the table.
	this.ActualLength = 0;

	// The actual status text messages.
	this.StatusTexts = statustexts;

	// Format a date for display.
	// Cascadas operates in UTC time.
	function _FormatDate(msgdate) {
		var serverdate = new Date();
		// Convert seconds to milliseconds, and to local time.
		serverdate.setTime(msgdate * 1000.0);
		return serverdate;
	}

	/* Update the current display state. 
	Parameters: statusbuff (array) - An array with the current condition log.
	*/
	function _UpdateHMIStatus(statusbuff) {

		// If there are no status problems, we can quit right here.
		try { 
			if (statusbuff.length == 0) {
				return;
			}
		}
		catch (e) {return;}


		// Check to see if the last (newest) record has already been displayed. 
		// If so, we can exit now. 
		try {
			if (statusbuff[statusbuff.length - 1]["displayed"]) {return;}
		}
		catch (e) {return;}


		/* Now loop through the buffer, and fill in the records in
		the display table. */
		for (i in statusbuff) {
			// Check if this error has already been displayed.
			if (! statusbuff[i]["displayed"]) {
				var timestamp = statusbuff[i]["timestamp"];
				var statuscode = statusbuff[i]["code"];

				// Get the actual error texts.
				statusmsg = this.StatusTexts[statuscode];
				

				// Format the date for display.
				datedisplay = _FormatDate(timestamp);

				// Add a new row to the top row of the document. 
				newrow = this.StatusTable.insertRow(1);
				// Add the cells.
				newdate = newrow.insertCell(0);
				newcode = newrow.insertCell(1);
				newstatusmsg = newrow.insertCell(2);


				// Now add the new text to each cell in the top row.
				newdate.innerHTML = datedisplay;
				newcode.innerHTML = statuscode;
				newstatusmsg.innerHTML = statusmsg;

				// Mark this record as having been displayed.
				statusbuff[i]["displayed"] = true;

				// If the table has exceeded its maximum length,
				// delete the bottom row.
				if (this.ActualLength > this.MaxLength) {
					this.StatusTable.deleteRow(-1);
				}
				else {
					this.ActualLength++;
				}

			}
			
		}

	}

	// Reference the function to make it public.
	this.UpdateScreen = _UpdateHMIStatus;


}
// End of object definition.

// ##################################################################

