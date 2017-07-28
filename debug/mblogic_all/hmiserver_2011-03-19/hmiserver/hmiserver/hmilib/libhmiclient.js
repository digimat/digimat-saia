/** ##########################################################################
# Project: 	MB-HMI
# Module: 	libhmiclient.js
# Purpose: 	MB-HMI demo client (master).
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		21-May-2009
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
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


/**

This module is used to demonstrate the MB-HMI web based industrial HMI protocol.

This version supports asynchronous communcations and "new style" alarms.


Public Methods
==============

1) Initialise the hmi object with the appropriate parameters, including the 
host URL and port, client ID, the "read list", and an option to select synchronous
or asynchronous polling.

2) Use "AddToDisplayList" to add screen items (code objects controlling graphics, 
text, tables, etc.) to the "display list". These will be called on a regular
basis and asked to update themselves.

3) Call "SendRequest" on a regular basis (e.g. once per second). "SendRequest" 
will communicate with the server and then will update the display list with 
any new data when a reply is received.

4) Use "AddWrite", "WriteImmediate", "WriteToggleImmediate" and "WriteIncImmediate"
to write data to the server. These would normally be attached to a control
such as a push button. The "immediate" instructions trigger a new polling and
update cycle immediately, instead of waiting for the next regular polling cycle
to send data.

5) "GetRead" can be used to read the current value associated with a tag on 
the read list. This is read from the input buffer and is whatever the value
was at the time of the latest poll.

6) "GetTimeStamp" returns the server time stamp from the latest poll. 


Read List and IO Polling
========================

The "read list" is an array of tag names that are to be polled (read) on a 
regular basis. 
Example - 

	var ReadList = ["PL1", "PL2", "PL3", "PL4", "PL5", "PL6", "PL7", "PL8",
		"Tank1Level", "Tank2Level", "PumpSpeedCmd", "PumpSpeedActual"];

	var MBHMIProtocol = new HMIClient("localhost", 8503, "sample client", ReadList, 
				AlarmZones, EventZones, true);

This creates a new object called MBHMIProtocol, which polls "localhost" at port 8503
to read the tags in ReadList. It also enabled asynchronous communications.

There should only be *one* MB-HMI object in an application that takes care of
*all* polling. 

The "same origin" security policy in most web browsers requires that a web client
application can only communicate with the same host that the web page was loaded
from. This means that a single server must be used as the source of the web page
and as the source (and destination) of all data. 



The Display List
================

The display list is an array of code objects which control graphics, text, tables,
etc. "UpdateDisplay" calls each item in turn, passes it the latest data, and asks
it to update itself. Each screen item must be a code object which exports a method
called "UpdateScreen", and which accepts one parameter.
e.g. "objref.UpdateScreen(presentstate);"

To add an item to the display list, create the object and pass it to "AddToDisplayList".
For example - 

	// This defines a pilot light control.
	var PL1 = new MB_PilotLight("green", "red", "black", "PL1", document);
	MBHMIProtocol.AddToDisplayList(PL1, "PL1", "read");


This creates a pilot light using "MB_PilotLight" (part of another library), assigns
it to a reference called PL1, and passes it to "AddToDisplayList" along with two
other parameters. 

The second parameter is the "address label". This is used by instructions which need 
to read the input values. This should be a valid tag from the read list whenever 
the address label is "read". Its value is not significant for other address labels.

The third parameter is the "tag type". This is a description of the type of 
address used in the second parameter. This determines the source of the data 
which is passed to the dislay item. Valid value are: "read" (input data from 
the read list), "timestamp" (the server time stamp from the last message), "stat"
(the server stat value from the last message), "msgid" (the message id returned
by the server), "events" (an array of the latest event messages), and "alarms"
(an object containing alarms and alarm acknowledgements). 


=====================================================================

Initialisation
==============

The class must be initalised before it can be used.

Parameters:
 	url (string) - URL to host.
	port (integer) - port for host.
	cid (string) - Client ID string.
	readlist (array) - List of tags to poll.
	alarmzonelist (array) - List of alarm zone filters.
	eventzonelist (array) - List of event zone filters.
	ansyncoption (boolean) - If true, communcations are asynchronous.
		This can cause compatibility problems with some browsers.


function HMIClient(url, port, cid, readlist, alarmzonelist, eventzonelist, ansyncoption)

e.g. 
	var MBHMIProtocol = new HMIClient(HMIDemoConfig["host"], HMIDemoConfig["port"], 
			HMIDemoConfig["cid"], ReadList, AlarmZones, EventZones, true);


Public Methods
==============

Add a tag to the list of values to write. 
Parmeters: 
	writetag (string) - A valid writable tag.
	writeval (any type) - A legal value for that tag.

function AddWrite(writetag, writeval)

==========
Add a tag to the list of values to write. Unlike a regular write, 
this triggers an immediate update of everything.
Parmeters: 
	writetag (string) - A valid writable tag.
	writeval (any type) - A legal value for that tag.

function WriteImmediate(writetag, writeval) 

==========
Add a tag to the list of values to write. This function will write
the opposite of whatever the value at reftag (0 or 1) is to writetag.
Unlike a regular write, this triggers an immediate update of everything.
Parameters:
	writetag (string) - Tag address to write to.
	reftag (string) - Reference tag address. 

function WriteToggleImmediate(writetag, reftag)

==========
Add a tag to the list of values to write. This function will read
the value at reftag, increment it by the value in incval, and
write the result to writetag. If the result exceeds inclimit,
the result will be reset to zero. A negative increment is
also valid. Unlike a regular write, this triggers an immediate 
update of everything.
Parameters:
	writetag (string) - Tag address to write to.
	reftag (string) - Reference tag address. 
	incval (integer) - Amount to increment by.
	inclimit (integer) - The maximum increment limit.

function WriteIncImmediate(writetag, reftag, incval, inclimit)

==========
Read the value of the id string. 
function GetServerID() 

==========
Read the value of the current message status. 
function GetMsgStat()

==========
Read the value of the time stamp. This returns the server time stamp. 
function GetTimeStamp()

==========
Read the value of an input. "readlabel" should be a valid tag name.
This returns the value associated with that tag.
Parameters: readlabel (string) - A valid readable tag.

function GetRead(readlabel)


Add an alarm acknowledge message to the list of alarm acknowledge 
responses to write. 

function AddAlarmAck()

==========
Add an item to the display list. Any item on the screen which 
must be updated regularly needs to be added to the "display list" in 
order to be automatically updated. This should be called for each screen
item as part of the program initialisation. Once an item has been added
to the display list, there should be no need to call this function again.
Parameters:
	objref (object) - A reference to the svg object.
	addrlabel (string) - The name of the data table address tag.
	tagtype (string) - The type of tag (internal, read, timestamp, stat, msgid).

function AddToDisplayList(objref, addrlabel, tagtype)

==========
Send a request to the server. Call this regularly to poll the server.
Each time this is called, any pending writes are sent to the server, together
with the read list, alarm acknowledgements, etc. This should be called on 
a regular cycle (e.g. once per second). This is also called on demand by 
some functions in order to force an immediate I/O update in order to make 
the system more responsive to user input.

function SendRequest()

==========
Check if responses are being received from the server. This is 
done by checking to see if a communications counter is 
incrementing. 
Parameters: limit (integer) - The amount of difference permitted
	between the number of messages sent and received before an 
	error is reported. This allows for minor "glitches" without 
	an error being reported. 
Returns true if the count of messages sent is greater than the 
	limit parameter. The send counter is reset every
	time a message is received.

function CommsWatchDogTimeOut(limit)




**/


// ##################################################################

/* Parameters: 	url (string) - URL to host.
		port (integer) - port for host.
		cid (string) - Client ID string.
		readlist (array) - List of tags to poll.
		alarmzonelist (array) - List of alarm zone filters.
		eventzonelist (array) - List of event zone filters.
		ansyncoption (boolean) - If true, communcations are asynchronous.
			This can cause compatibility problems with some browsers.
 */

function HMIClient(url, port, cid, readlist, alarmzonelist, eventzonelist, ansyncoption) {

	// Port and host name info.
	this.URL = url;
	this.Port = port;
	this.host = "http://" + url + ":" + port + "/mbhmi";


	// Set this to true to do asynchronous communications.
	this.AysyncOption = ansyncoption;

	// The request object we use to communicate with the server. Initialising 
	// it indirectly seems to be necessary to keep WebKit happy.
	var reqobj = new XMLHttpRequest();
	this.ServerReq = reqobj;


	// This is used to track whether messages which are being sent.
	// are also being received.
	this.CommsSendCounter = 0;


	// This is the base object used to define messages.
	this.HMIJSONObject = {
			"id" : "None",
			"msgid" : 0,
			"read" : [null],
			"write" : {},
			"events" : {"serial" : 0, "max" : 50, "zones" : "zone1"},
			"alarms" : [],
			"alarmhistory" : {"serial" : 0, "max" : 50, "zones" : "zone1"},
			"alarmack" : []
			};

	// Set the client ID.
	this.ClientID = cid;
	this.HMIJSONObject["id"] = this.ClientID;
	// Set the read list.
	this.ReadList = readlist;
	this.HMIJSONObject["read"] = readlist;

	// Alarm and event zones.
	this.AlarmZoneList = alarmzonelist;
	this.EventZoneList = eventzonelist;
	this.HMIJSONObject["alarms"] = this.AlarmZoneList;
	this.HMIJSONObject.events["zones"] = this.EventZoneList;
	this.HMIJSONObject.alarmhistory["zones"] = this.AlarmZoneList;


	this.MsgID = 0;
	this.Stat = "";
	this.WriteList = "";


	/* This is the central data table for holding variable data
	which was read from the server. */
	this.ReadDataTable = {};
	/* This is a private table used to hold the list of screen items 
		which must be updated. */
	this._DisplayList = [];

	// Maximum length for error buffer.
	this._MaxErrorBuffer = 50;

	// This holds error information returned from the server.
	this._ErrorBuffer = [];


	// Maximum length for status log buffer. 
	this._MaxStatusBuffer = 50;

	// This holds status codes returns from the server.	
	this._StatusBuffer = [];

	// This is the latest server ID. 
	this.ServerID = "";

	// This is the latest timestamp. 
	this.TimeStamp = 0.0;

	// FIFO buffer to hold event history. 
	this._EventBuffer = [];
	// Maximum length for event buffer. 
	this._MaxEventBuffer = 50;
	// Set the maximum number of event messages to request.
	this.HMIJSONObject.events["max"] = this._MaxEventBuffer;
	// The event with the highest serial number.
	this._LatestEvent = 0;


	// Alarms.
	this.Alarms = [];

	// FIFO buffer to hold alarm history. 
	this._AlarmHistoryBuffer = [];
	// Maximum length for alarm history buffer. 
	this._MaxAlarmHistoryBuffer = 50;
	// Set the maximum number of alarms history messages to request.
	this.HMIJSONObject.alarmhistory["max"] = this._MaxAlarmHistoryBuffer;
	// The alarm history with the highest serial number.
	this._LatestAlarmHistory = 0;
	// The alarm history buffer has been updated. 
	this._AlarmHistoryUpdated = 0;


	// FIFO buffer to hold alarm acknowledge history. 
	this._AlarmAckBuffer = [];
	// Maximum length for alarm acknowledge buffer. 
	this._MaxAlarmAckBuffer = 50;
	// The alarm acknowledge with the highest serial number.
	this._LatestAlarmAck = 0;
	// The alarm buffer has been updated. 
	this._AlarmAckUpdated = 0;



	// ##################################################################

	/*	Add a tag to the list of values to write. 
		Parmeters: writetag (string) - A valid writable tag.
		writeval (any type) - A legal value for that tag.
	*/
	function _AddWrite(writetag, writeval) {
		this.HMIJSONObject.write[writetag] = writeval;
	}


	// ##################################################################

	/*	Add a tag to the list of values to write. Unlike a regular write, 
		this triggers an immediate update of everything.
		Parmeters: writetag (string) - A valid writable tag.
		writeval (any type) - A legal value for that tag.
	*/
	function _WriteImmediate(writetag, writeval) {

 		this.HMIJSONObject.write[writetag] = writeval;

		// Now, do an update right away.
		// Query the server for updates.
		this.SendRequest();
		// Update the display.
		this.UpdateDisplay();
	}


	// ##################################################################

	/*	Add a tag to the list of values to write. This function will write
		the opposite of whatever the value at reftag (0 or 1) is to writetag.
		Unlike a regular write, this triggers an immediate update of everything.
		Parameters:
		writetag (string) - Tag address to write to.
		reftag (string) - Reference tag address. 
	*/
	function _WriteToggleImmediate(writetag, reftag) {
		if (this.GetRead(reftag) == 0) {
			this.WriteImmediate(writetag, 1);
		}
		else {
			this.WriteImmediate(writetag, 0);
		}

	}


	// ##################################################################

	/*	Add a tag to the list of values to write. This function will read
		the value at reftag, increment it by the value in incval, and
		write the result to writetag. If the result exceeds inclimit,
		the result will be reset to zero. A negative increment is
		also valid. Unlike a regular write, this triggers an immediate 
		update of everything.
		Parameters:
		writetag (string) - Tag address to write to.
		reftag (string) - Reference tag address. 
		incval (integer) - Amount to increment by.
		inclimit (integer) - The maximum increment limit.
	*/
	function _WriteIncImmediate(writetag, reftag, incval, inclimit) {
		presentvalue = this.GetRead(reftag);
		// If we have a math error, we just skip the increment.
		try {
			presentvalue += incval;
			if (Math.abs(presentvalue) > Math.abs(inclimit)) {
				presentvalue = 0;
			}
		}
		// If error, read the tag again.
		catch (e) { presentvalue = this.GetRead(reftag); }

		this.WriteImmediate(writetag, presentvalue);
	}

	// ##################################################################

	// Read the value of the id string. 
	function _GetServerID() {
		return this.ServerID;
	}


	// ##################################################################

	// Read the value of the current message status. 
	function _GetMsgStat() {
		return this.Stat;
	}


	// ##################################################################

	// Read the value of the time stamp. This returns the server time stamp. 
	function _GetTimeStamp() {
		return this.TimeStamp;
	}

	// ##################################################################

	/* Read the value of an input. "readlabel" should be a valid tag name.
	This returns the value associated with that tag.
	Parameters: readlabel (string) - A valid readable tag.
	*/
	function _GetRead(readlabel) {
		return this.ReadDataTable[readlabel];
	}


	// ##################################################################

	/*	Add a new message to the appropriate message buffer. This is 
		intended to be a private method. This handles events, alarm history, etc.
		Parameters: 
		newmessages (array) - A message buffer with new messages.
		latestmessage (integer) - The serial number of the last message.
		messagebuffer (array) - The message buffer with existing messages.
		maxbuffersize (integer) - The limit on the message buffer size.
			If the buffer exceeds this, old messages are pruned.
		Returns: (integer) - The serial number of the last message.
	*/
	function _SaveMessage(newmessages, latestmessage, messagebuffer, maxbuffersize) {
		// Add these messages to the existing buffer
		var largest = 0;
		for (i in newmessages) {
			// Extract the serial number from the current record.
			var serialnum = newmessages[i]["serial"];

			/* Make sure we didn't get sent a record
			 that we already have.*/
			if (serialnum > latestmessage) {
				messagebuffer.push(newmessages[i]);

				// Remember the largest serial number found.
				if (serialnum > largest) {
					largest = serialnum;
				}
			}
		}

		// Now, check if the buffer has grown too long and needs pruning.
		var buffover = messagebuffer.length - maxbuffersize;
		j = messagebuffer.splice(0, buffover);

		// Return the latest serial number.
		if (largest > latestmessage) {
			return largest;
		}
		else {
			return latestmessage;
		}
	}


	// ##################################################################

	/* Save any new events to the event buffer. 
		This is intended to be a private method. 
	Parameters: events (array) - Array of event records.
	Returns: nothing. Modifies the event buffer.
	*/
	function _SaveEvents(events) {
		// If there are no events, we can quit right here.
		try {if (events.length == 0) {return;}
		}
		catch (e) {
			// Update the events request.
			this.HMIJSONObject.events["serial"] = this._LatestEvent;
			return;
		}

		this._LatestEvent = _SaveMessage(events, this._LatestEvent, this._EventBuffer, this._MaxEventBuffer);

		// Update the events request.
		this.HMIJSONObject.events["serial"] = this._LatestEvent;
	}



	// ##################################################################

	/* Save any new alarm history to the alarm history buffer. 
		This is intended to be a private method. 
	Parameters: alarms (array) - Array of alarm history records.
	Returns: nothing. Modifies the alarm history buffer.
	*/
	function _SaveAlarmHistory(alarmhistory) {
		// If there are no alarm history records, we can quit right here.
		try {if (alarmhistory.length == 0) {return;}
		}
		catch (e) {
			// Update the alarm history request.
			this.HMIJSONObject.alarmhistory["serial"] = this._LatestAlarmHistory;
			return;
		}

		this._LatestAlarmHistory = _SaveMessage(alarmhistory, this._LatestAlarmHistory, 
				this._AlarmHistoryBuffer, this._MaxAlarmHistoryBuffer);

		// Update the alarm history request.
		this.HMIJSONObject.alarmhistory["serial"] = this._LatestAlarmHistory;
	}



	// ##################################################################

	/*	Add an alarm acknowledge message to the list of alarm acknowledge 
		responses to write. 
	*/
	function _AddAlarmAck() {
		for (i in this._Alarms) {
			// If the alarm is active, but not acknowledged add 
			// it to the acknowledge request.
			try { 
				if ((this._Alarms[i]["state"] == "alarm") ||
					(this._Alarms[i]["state"] == "ok")) {
					this.HMIJSONObject.alarmack.push(i);
				}
			}
			catch (e) {
				// Ignore the error here.
			}
		}
	}

	// ##################################################################

	/*	Add a new error to the error buffer. This is 
		intended to be a private method. This handles read errors, 
		write errors, etc. A time stamp is added to each error message 
		and both are saved together as an object.
		Parameters: 
		newerrors (array) - An array with new errors.
	*/
	function _SaveError(newerrors) {

		// If there are no errors, we can quit right here.
		try {if (newerrors.length == 0) {return;} 
		}
		catch (e) {return;}

		// Get the current server time stamp.
		var timestamp = this.TimeStamp ;

		// Add these errors to the existing buffer. We set the "displayed"
		// flag to false until it has been displayed on the screen.
		for (i in newerrors) {
			this._ErrorBuffer.push({"timestamp" : timestamp, "tag" : i, 
				"errors" : newerrors[i], "displayed" : false});
		}

		// Now, check if the buffer has grown too long and needs pruning.
		var buffover = this._ErrorBuffer.length - this._MaxErrorBuffer;
		j = this._ErrorBuffer.splice(0, buffover);

	}


	// ##################################################################

	/*	Add a new status code to the status buffer. This is 
		intended to be a private method. Any message status other than
		"ok" is saved to this buffer together with a time stamp.
		Parameters: 
		newstatus (string) - The current status code.
	*/
	function _SaveStatus(newstatus) {

		// If status is "ok", we can quit right here.
		try {if (newstatus == "ok") {return;} 
		}
		catch (e) {return;}

		// Get the current server time stamp.
		var timestamp = this.TimeStamp ;

		// Add the current status to the existing buffer. We set the "displayed"
		// flag to false until it has been displayed on the screen.
		this._StatusBuffer.push({"timestamp" : timestamp, "code" : newstatus, 
				"displayed" : false});


		// Now, check if the buffer has grown too long and needs pruning.
		var buffover = this._StatusBuffer.length - this._MaxStatusBuffer;
		j = this._StatusBuffer.splice(0, buffover);

	}


	// ##################################################################

	/* 	Add an item to the display list. Any item on the screen which 
	must be updated regularly needs to be added to the "display list" in 
	order to be automatically updated. This should be called for each screen
	item as part of the program initialisation. Once an item has been added
	to the display list, there should be no need to call this function again.
		Parameters:
		objref (object) - A reference to the svg object.
		addrlabel (string) - The name of the data table address tag.
		tagtype (string) - The type of tag (internal, read, timestamp, stat, msgid).
	*/
	function _AddToDisplayList(objref, addrlabel, tagtype) {
		this._DisplayList.push({"addrlabel" : addrlabel, "objref" : objref, "tagtype" : tagtype});
	}


	// ##################################################################

	/* Update the screen display with any changed data. 
		This is intended to be a private method. 
	This is called (by "ReceiveResponse") on a regular cycle (e.g. once per 
	second) when a response is received to update the display of items 
	in the "display list". This is also called on demand by some functions in order
	to force a screen update in order to make the system more responsive to user input.
	*/
	function _UpdateDisplay() {

		// Go through the list of addresses in the display list.
		for (i in this._DisplayList) {
			// Get the object.
			var displayobject = this._DisplayList[i];
			// Get the address label.
			var addrlabel = displayobject["addrlabel"];
			// Get the present state, access to which depends on the type.
			var tagtype = displayobject["tagtype"];
			var presentstate = "";
			switch (tagtype) {
			case "read" : presentstate = this.ReadDataTable[addrlabel]; break;
			case "timestamp" : presentstate = this.TimeStamp; break;
			case "serverid" : presentstate = this.ServerID; break;
			case "stat" : presentstate = this.Stat; break;
			case "msgid" : presentstate = this.MsgID; break;
			case "alarms" : presentstate = this._Alarms; break; 
			case "alarmhistory" : presentstate = this._AlarmHistoryBuffer; break; 
			case "events" : presentstate = this._EventBuffer; break;
			case "errors" : presentstate = this._ErrorBuffer; break;
			case "status" : presentstate = this._StatusBuffer; break;
			}

			var objref = displayobject["objref"];
			objref.UpdateScreen(presentstate);

		}

	}

	// ##################################################################

	/* 	Read the data from the server response object. The results
		are saved in the appropriate global variables.
		This is intended to be a private method.
	*/

	function _ReadResponseData() {

		var responseobj = {};

		// Convert the JSON string into an object.
		responseobj = JSON.parse(this.ServerReq.responseText);

		// Save the read results.
		readresult = responseobj["read"];
		var readlable;
		var readindex;
		for (readindex in this.ReadList) {
			readlable = this.ReadList[readindex];
			try {
				this.ReadDataTable[readlable] = readresult[readlable];
			}
			catch (e) {
				this.ReadDataTable[readlable] = null;
			}
		}

		// Save the server ID.
		try {
			this.ServerID = responseobj["id"];
		}
		catch (e) {
			this.ServerID = null;
		}


		// Save the time stamp.
		try {
			this.TimeStamp = responseobj["timestamp"];
		}
		catch (e) {
			this.TimeStamp = null;
		}

		// Save the errors.
		// Read errors.
		this._SaveError(responseobj["readerr"]);
		
		// Write errors.
		this._SaveError(responseobj["writeerr"]);

		// Errors when checking if type of tag is readable.
		this._SaveError(responseobj["readable"]);

		// Errors when checking if type of tag is writable.
		this._SaveError(responseobj["writable"]);

		// Event errors.
		this._SaveError(responseobj["eventerr"]);

		// Alarm errors.
		this._SaveError(responseobj["alarmerr"]);

		// Alarm history errors.
		this._SaveError(responseobj["alarmhisterr"]);


		// Save the communications status in a buffer.
		this._SaveStatus(responseobj["stat"]);

		// Save the current communications status.
		try {
			this.Stat = responseobj["stat"];
		}
		catch (e) {
			this.Stat = null;
		}

		// Save the alarm messages.
		try {
			this._Alarms = responseobj["alarms"];
		}
		catch (e) {
			this._Alarms = null;
		}

		// Save the events.
		this._SaveEvents(responseobj["events"]);

		// Save the alarm history.
		this._SaveAlarmHistory(responseobj["alarmhistory"]);

		// Empty the previous write queue. 
		this.HMIJSONObject.write = {};
		// Empty the previous acknowledge request.
		this.HMIJSONObject.alarmack = [];

	}

	// ##################################################################


	/* Send a request to the server. Call this regularly to poll the server.
	Each time this is called, any pending writes are sent to the server, together
	with the read list, alarm acknowledgements, etc. This should be called on 
	a regular cycle (e.g. once per second). This is also called on demand by 
	some functions in order to force an immediate I/O update in order to make 
	the system more responsive to user input.
	*/
	function _SendRequest() {

		// Create the JSON string for the message.
		var reqdata = JSON.stringify(this.HMIJSONObject);

		// Increment the message sent counter.
		this.CommsSendCounter++;

		// Set the ansynchronous request to "true".
		this.ServerReq.open("POST", this.host, this.AysyncOption); 

		// Set the content type.
		this.ServerReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

		// Put the data in the header.
		this.ServerReq.setRequestHeader("Cascadas", reqdata);

		// This overrides the MimeType to make sure the browser does 
		// not attempt to parse it.
		this.ServerReq.overrideMimeType('text/plain; charset=x-user-defined'); 

		// The following two lines are not obvious, but they set up a 
		// callback function to receive the asynchronous response. It 
		// has to be done in this round about fashion because the 
		// "ServerReq" would not otherwise be visible to "ReceiveResponse"
		// when it gets called by XMLHttpRequest.
		if (this.AysyncOption){
			var respobj = this;
			this.ServerReq.onreadystatechange = function(ServerReq) {respobj.ReceiveResponse(ServerReq);}
		}

		// Send the request.
		this.ServerReq.send(reqdata);

		if (!this.AysyncOption){
			this.ReceiveResponse();
		}

	}


	// ##################################################################

	/* Receive the server response a request to the server. This is called 
	automatically as a "callback". The request is set up by SendRequest.
	This is intended to be a private method.
	*/
	function _ReceiveResponse() {
		
		// Check to see if the response is final yet. 
		if (this.ServerReq.readyState != 4) {
			return;
		}

		// Check if the http response was OK.
		if(this.ServerReq.status != 200) {
			return;
		}

		// Reset the message counter.
		this.CommsSendCounter = 0;

		// If we passed the above tests, we assume the server
		// responded with a valid message.

		// Get the response data.
		this.ReadResponseData();

		// Update the dislay with the new data.
		this.UpdateDisplay();

		// Increment the message id.
		this.MsgID = this.MsgID + 1;
		if (this.MsgID > 65535) {
			this.MsgID = 1;
		}
		this.HMIJSONObject["msgid"] = this.MsgID;
	}


	// ##################################################################

	/* 	Check if responses are being received from the server. This is 
		done by checking to see if a communications counter is 
		incrementing. 
		Parameters: limit (integer) - The amount of difference permitted
			between the number of messages sent and received before an 
			error is reported. This allows for minor "glitches" without 
			an error being reported. 
		Returns true if the count of messages sent is greater than the 
			limit parameter. The send counter is reset every
			time a message is received.
	*/
	function _CommsWatchDogTimeOut(limit) {
		return (this.CommsSendCounter > limit);
	}


	// ##################################################################

	// Reference these functions to make them public.

	this.AddWrite = _AddWrite;
	this.WriteImmediate = _WriteImmediate;
	this.WriteToggleImmediate = _WriteToggleImmediate;
	this.WriteIncImmediate = _WriteIncImmediate

	this.GetServerID = _GetServerID;
	this.GetMsgStat = _GetMsgStat;
	this.GetTimeStamp = _GetTimeStamp;
	this.GetRead = _GetRead;

	this._SaveEvents = _SaveEvents;
	this._SaveAlarmHistory = _SaveAlarmHistory;
	this.AddAlarmAck = _AddAlarmAck;

	this._SaveError = _SaveError
	this._SaveStatus = _SaveStatus

	this.AddToDisplayList = _AddToDisplayList;
	this.UpdateDisplay = _UpdateDisplay;
	this.SendRequest = _SendRequest;
	this.ReceiveResponse = _ReceiveResponse;
	this.CommsWatchDogTimeOut = _CommsWatchDogTimeOut;
	this.ReadResponseData = _ReadResponseData;


// ##################################################################

}


