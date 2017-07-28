/** ##########################################################################
# Project: 	MBLogic
# Module: 	libhistory.js
# Purpose: 	MBLogic alarm and event history view library.
# Language:	javascript
# Date:		30-Dec-2010
# Ver:		16-Mar-2011
# Author:	M. Griffin.
# Copyright:	2010 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
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


// ##################################################################
/* This contains common code for events and alarms.
*/
function HistoryUtils() {
	// ##################################################################
	// This is used to insert new information into a table which 
	// is allowed to grow in length.
	function _InsertTableCell(trow, cellcolum, text, tdclass) {
			var cell = trow.insertCell(cellcolum);
			var celltext = document.createTextNode(text);
			if (tdclass != "") {
				cell.setAttribute("class", tdclass);
			}
			cell.appendChild(celltext);
	}
	this.InsertTableCell = _InsertTableCell;


	// ##################################################################
	// Set the display attribute of a section of a web page to display
	// a hidden area of the page. This relies on the CSS class for "datashow".
	function _ShowPageArea(id) {
		document.getElementById(id).setAttribute("class", "datashow");
	}
	this.ShowPageArea = _ShowPageArea;

	// ##################################################################
	// Set the display attribute of a section of a web page to hide
	// a hidden area of the page.This relies on the CSS class for "datahide".
	function _HidePageArea(id) {
		document.getElementById(id).setAttribute("class", "datahide");
	}
	this.HidePageArea = _HidePageArea;


	// ##################################################################
	// Return true if the number is a valid integer within the specified range.
	// Parameters number (string) = The value to verify. 
	//	min, max (integer) = The minimum and maximum values to compare to.
	function _IntOk(number, min, max) {

		if (!/^[0-9]+$/.test(number)) { return false; }
		
		// Convert to base 10 integer.
		var numval = parseInt(number, 10);
		if (isNaN(numval)) { return false; }

		// Check if in valid range.
		if ((numval < min) || (numval > max)) { return false; }

		return true;
	}
	this.IntOk = _IntOk;

	// ##################################################################
	// Return true if the number is a valid integer greater than or equal to 
	// the specified minimum.
	// Parameters number (string) = The value to verify. 
	//	min  (integer) = The minimum value to compare to.
	function _IntOkMin(number, min) {

		if (!/^[0-9]+$/.test(number)) { return false; }
		
		// Convert to base 10 integer.
		var numval = parseInt(number, 10);
		if (isNaN(numval)) { return false; }

		// Check if in valid range.
		if (numval < min) { return false; }

		return true;
	}
	this.IntOkMin = _IntOkMin;



	// ##################################################################
	// Set the colour of the form input field to reflect whether the data is OK.
	function _ShowFieldStatusColour(ok, fieldid) {
		var field = document.getElementById(fieldid);
		if (ok) {
			field.setAttribute("class", "editfields");
		} else {
			field.setAttribute("class", "editerrors");
		}
	}
	this.ShowFieldStatusColour = _ShowFieldStatusColour;


	// ##################################################################
	// Return a string containing a properly formatted date string for
	// a query. E.g. "YYYYMMDDHHMMSS"
	function _FormatQueryDate(year, month, day, hour, minute, second) {
		var yearstr = year.toString();
		var monthstr = month.toString();
		var daystr = day.toString();
		var hourstr = hour.toString();
		var minutestr = minute.toString();
		var secondstr = second.toString();

		if (monthstr.length < 2) { var monthstr = "0" + monthstr; }
		if (daystr.length < 2) { var daystr = "0" + daystr; }
		if (hourstr.length < 2) { var hourstr = "0" + hourstr; }
		if (minutestr.length < 2) { var minutestr = "0" + minutestr; }
		if (secondstr.length < 2) { var secondstr = "0" + secondstr; }

		return yearstr.concat(monthstr, daystr, hourstr, minutestr, secondstr);
	}
	this.FormatQueryDate = _FormatQueryDate;

}


// ##################################################################
/* This handles event history querying.
Parameters: utils = The library used for common functions.
	msgs (object) = The event messages as {"key1" : "message 1", "key2" : "message 2", etc.}.
	orstr (string) = The word to use to indicate an "OR" condition when 
		combining event conditions. This is not hard coded in this library so
		that we can change it for different language web page versions. 
*/

function Events(utils, msgs, orstr) {

	this.Utils = utils;
	this.MsgsTxts = msgs;
	this.ORStr = orstr;


	// ##################################################################
	// Initialise the page display defaults.
	function _InitPage() {
		this.PopulateMessages();
		this.InitDateFields();

		document.forms.eventeditmode.mode[0].checked = true;
		document.forms.eventeditmode.mode[1].checked = false;
		this.ShowQueryMode();
	}
	this.InitPage = _InitPage;



	// ##################################################################
	/* This populates the HTML message selectors.
	*/
	function _PopulateMessages() {

		// Populate the events.
		var msgchoice = document.getElementById("eventchoice");

		// Create an decorated array.
		var msgarray = [];
		for (var i in this.MsgsTxts) {
			msgarray.push([this.MsgsTxts[i], i]);
		}
		// Sort by message text.
		msgarray.sort();


		// Populate the event messages.
		for (var i in msgarray) {
			var msgtag = msgarray[i][1];
			var msgtxt = this.MsgsTxts[msgtag];
			var newoption = document.createElement("option");
			newoption.value = msgtag;
			newoption.text = msgtxt;
			msgchoice.appendChild(newoption);
		}

	}
	this.PopulateMessages = _PopulateMessages;



	// ##################################################################
	// Set the dates to the default values.
	function _InitDateFields() {
		// Current date and time.
		var datenow = new Date();
		document.forms.eventdatequery.eventyearto.value = datenow.getFullYear();
		document.forms.eventdatequery.eventmonthto.value = datenow.getMonth() + 1;
		document.forms.eventdatequery.eventdayto.value = datenow.getDate();
		document.forms.eventdatequery.eventhourto.value = datenow.getHours();
		document.forms.eventdatequery.eventminuteto.value = datenow.getMinutes();
		document.forms.eventdatequery.eventsecto.value = datenow.getSeconds();

		// The time 24 hours ago.
		var dateyesterday = new Date(datenow.getTime() - (24 * 60 * 60 * 1000));
		document.forms.eventdatequery.eventyearfrom.value = dateyesterday.getFullYear();
		document.forms.eventdatequery.eventmonthfrom.value = dateyesterday.getMonth() + 1;
		document.forms.eventdatequery.eventdayfrom.value = dateyesterday.getDate();
		document.forms.eventdatequery.eventhourfrom.value = dateyesterday.getHours();
		document.forms.eventdatequery.eventminutefrom.value = dateyesterday.getMinutes();
		document.forms.eventdatequery.eventsecfrom.value = dateyesterday.getSeconds();

	}
	this.InitDateFields = _InitDateFields;



	// ##################################################################
	// Get what the current selection is for the type of query (e.g. by date or event).
	// Returns: (integer) = A number representing the selected mode. 
	function _GetMode() {
		var mode = 0;
		if (document.forms.eventeditmode.mode[0].checked) { var mode = mode | 1; }
		if (document.forms.eventeditmode.mode[1].checked) { var mode = mode | 2; }

		return mode;
	}
	this.GetMode = _GetMode;


	// ##################################################################
	// Display the correct query selections according to the current 
	// mode (by date by event, etc.).
	function _ShowQueryMode() {
		var mode = this.GetMode();

		// By date.
		if (mode & 1) { 
			this.Utils.ShowPageArea("showeventsbydate");
		} else {
			this.Utils.HidePageArea("showeventsbydate");
		}

		// By event.
		if (mode & 2) { 
			this.Utils.ShowPageArea("showeventsbyevent");
		} else {
			this.Utils.HidePageArea("showeventsbyevent");
		}
	}
	this.ShowQueryMode = _ShowQueryMode;



	// ##################################################################
	// Reset the date query fields back to their defaults.
	function _ResetDateQuery() {
		this.InitDateFields();
	}
	this.ResetDateQuery = _ResetDateQuery;


	// ##################################################################
	// Reset the event query selections back to their defaults.
	function _ResetEventQuery() {
		this.EventQueryList = [];

		// Delete any event selection which is listed on the page. 
		var querylist = document.getElementById("eventquerylist");
		if (querylist.hasChildNodes()) {
			while (querylist.firstChild) {
				querylist.removeChild(querylist.firstChild);
			}
		} 
	}
	this.ResetEventQuery = _ResetEventQuery;



	// ##################################################################
	// Do a basic range check, set the appropriate colour, and return the result.
	function _CheckDateField(id, value, dmin, dmax) {
		var dateok = this.Utils.IntOk(value, dmin, dmax);
		this.Utils.ShowFieldStatusColour(dateok, id);
		return dateok;
	}
	this.CheckDateField = _CheckDateField;


	// ##################################################################
	// Validate date. Returns true if the date was OK.
	function _CheckFromDate() {

		// First, do a basic check.
		var year = document.forms.eventdatequery.eventyearfrom.value;
		var yearok = this.CheckDateField("eventyearfrom", year, 0, 3000);

		var month = document.forms.eventdatequery.eventmonthfrom.value;
		var monthok = this.CheckDateField("eventmonthfrom", month, 1, 12);

		var day = document.forms.eventdatequery.eventdayfrom.value;
		var dayok = this.CheckDateField("eventdayfrom", day, 1, 31);

		// If there are any errors, we can't continue with the next check.
		if (!yearok || !monthok || !dayok) { return false; }

		// Convert the year, month, and day fields into a single date.
		var newdate = new Date(year, month - 1, day);
		// If the new day does not match the original, then the day is invalid.
		if (newdate.getDate() != day) {
			this.Utils.ShowFieldStatusColour(false, "eventdayfrom");
			return false;
		}

		// The date is OK.
		return true;

	}
	this.CheckFromDate = _CheckFromDate;


	// ##################################################################
	// Validate the "to" date. Returns true if the date was OK.
	function _CheckToDate() {

		// First, do a basic check.
		var year = document.forms.eventdatequery.eventyearto.value;
		var yearok = this.CheckDateField("eventyearto", year, 0, 3000);

		var month = document.forms.eventdatequery.eventmonthto.value;
		var monthok = this.CheckDateField("eventmonthto", month, 1, 12);

		var day = document.forms.eventdatequery.eventdayto.value;
		var dayok = this.CheckDateField("eventdayto", day, 1, 31);

		// If there are any errors, we can't continue with the next check.
		if (!yearok || !monthok || !dayok) { return false; }

		// Convert the year, month, and day fields into a single date.
		var newdate = new Date(year, month - 1, day);
		// If the new day does not match the original, then the day is invalid.
		if (newdate.getDate() != day) {
			this.Utils.ShowFieldStatusColour(false, "eventdayto");
			return false;
		}

		// The date is OK.
		return true;

	}
	this.CheckToDate = _CheckToDate;


	// ##################################################################
	// This contains the time parameters. These include the id or form field name
	// (these must be identical), and the minimum and maximum permitted values.
	this._TimeParams = {
		"eventhourfrom" : [0, 23],
		"eventminutefrom" : [0, 59],
		"eventsecfrom" : [0, 59],
		"eventhourto" : [0, 23],
		"eventminuteto" : [0, 59],
		"eventsecto" : [0, 59]
		}


	// ##################################################################
	// Validate the time form entry. Returns true if the time was OK.
	function _CheckTime(id) {
		// Check an individual field.
		if (id != "") {
			var tmin = this._TimeParams[id][0];
			var tmax = this._TimeParams[id][1];
			var formbase = document.forms.eventdatequery[id];
			var fvalue = formbase.value;

			var dresult = this.CheckDateField(id, fvalue, tmin, tmax);
			return dresult;
		} else {
		// check everything.
			var allok = true;
			for (var nextid in this._DateParams) {
				var tmin = this._TimeParams[id][0];
				var tmax = this._TimeParams[id][1];
				var formbase = document.forms.eventdatequery[nextid];
				var fvalue = formbase.value;

				var dresult = this.CheckDateField(id, fvalue, tmin, tmax);
				if (!dresult) { var allok = false; }
			}

			return allok;
		}
	}
	this.CheckTime = _CheckTime;


	// ##################################################################
	// Format the date portion of the query string. 
	function _FormatDate() {
		var fromdate = this.Utils.FormatQueryDate(
						document.forms.eventdatequery.eventyearfrom.value,
						document.forms.eventdatequery.eventmonthfrom.value,
						document.forms.eventdatequery.eventdayfrom.value,
						document.forms.eventdatequery.eventhourfrom.value,
						document.forms.eventdatequery.eventminutefrom.value,
						document.forms.eventdatequery.eventsecfrom.value);

		var todate = this.Utils.FormatQueryDate(
						document.forms.eventdatequery.eventyearto.value,
						document.forms.eventdatequery.eventmonthto.value,
						document.forms.eventdatequery.eventdayto.value,
						document.forms.eventdatequery.eventhourto.value,
						document.forms.eventdatequery.eventminuteto.value,
						document.forms.eventdatequery.eventsecto.value);
		return "timestamp=".concat(fromdate, ",", todate);

	}
	this.FormatDate = _FormatDate;



	// ##################################################################
	// This is the current list of events to be queried.
	this.EventQueryList = [];


	// ##################################################################
	// Add a new event to the list of events to be part of the query.
	function _AddEvent() {
		var newevent = document.forms.eventeventquery.eventchoice.value;

		// Ignore the default placeholder.
		if (newevent == "none") { return; }

		// Check for duplicates.
		if (this.EventQueryList.indexOf(newevent) >= 0) { return; }


		// Add it to the list.
		this.EventQueryList.push(newevent);


		var querylist = document.getElementById("eventquerylist");

		// Show the OR condition if there that one selected.
		if (this.EventQueryList.length > 1) {
			var padstr = this.ORStr;
		} else {
			var padstr = "";
		}

		var newmsg = document.createTextNode(padstr + "[" + this.MsgsTxts[newevent] + "]");
		querylist.appendChild(newmsg);

	}
	this.AddEvent = _AddEvent;

	// ##################################################################
	// Format the event portion of the query string. 
	function _FormatEvents() {
		return "events=".concat(this.EventQueryList);
	}
	this.FormatEvents = _FormatEvents;


	// ##################################################################
	// Format a query string based on the selected parameters. Returns the 
	// complete query string including the URL, but not the host or port.
	//	http://localhost:8082/aequery/events?timestamp=20101217080000,20101218120059;events=PumpStopped,Tank1Full
	function _FormatQuery() {

		var mode = this.GetMode();

		// Nothing is selected.
		if (mode == 0) { return ""; }

		var querylist = [];

		// By date.
		if (mode & 1) { 
			// Only proceed if the dates are valid. 
			if (this.CheckFromDate() && this.CheckToDate() && this.CheckTime("")) {
				querylist.push(this.FormatDate());
			} else {
				return "";
			}
		} 

		// By event.
		if (mode & 2) { 
			querylist.push(this.FormatEvents());
		} 

		return "/aequery/events?" + querylist.join(";");
	}
	this.FormatQuery = _FormatQuery;


	// ##################################################################
	// Update the page display with the new data.
	function _UpdatePageResults(pageresults) {

		// Now, update the server table data.
		var eventtable = document.getElementById("eventtable");

		// First, delete the table if it already exists (but not the header).
		while (eventtable.rows.length > 1) {
			eventtable.deleteRow(-1);
		}

		// This is used to give table rows alternating colours.
		var trowcounter = false;
		var trowcolours = ["t1", "t2"];


		// This counts the maximum number of rows to display.
		var limitcounter = 0;

		// Go through all the records.
		for (var i in pageresults) {

			var trow = eventtable.insertRow(-1);

			// This is used to provide alternating row colours.
			if (trowcounter) {
				var tdclass = trowcolours[0];
			} else {
				var tdclass = trowcolours[1];
			}
			var trowcounter = !trowcounter;


			// Extract the original date and event tag number.
			var recdate = pageresults[i][1];
			var rectag = pageresults[i][2];

			// We need to format the date.
			var datelocal = new Date(recdate * 1000.0);

			// First cell is date.
			this.Utils.InsertTableCell(trow, 0, datelocal.toLocaleString(), tdclass);
			// Second cell is event.
			this.Utils.InsertTableCell(trow, 1, this.MsgsTxts[rectag], tdclass);

			// Limit the number of rows displayed.
			var limitcounter = limitcounter + 1;
			if (limitcounter > 100) { return; }
			

		}

	}
	this.UpdatePageResults = _UpdatePageResults;


}

// ##################################################################



// ##################################################################
/* This handles alarm history querying.
Parameters: utils = The library used for common functions.
	msgs (object) = The alarm messages as {"key1" : "message 1", "key2" : "message 2", etc.}.
	orstr (string) = The word to use to indicate an "OR" condition when 
		combining alarm conditions. This is not hard coded in this library so
		that we can change it for different language web page versions. 
	maxcount (integer) = The default value for the "to" field in a count search.
*/

function Alarms(utils, msgs, orstr, maxcount) {

	this.Utils = utils;
	this.MsgsTxts = msgs;
	this.ORStr = orstr;

	this.MaxCount = maxcount;


	// ##################################################################
	// Initialise the page display defaults.
	function _InitPage() {
		this.PopulateMessages();
		this.InitDateFields();

		document.forms.alarmeditmode.mode[0].checked = true;
		document.forms.alarmeditmode.mode[1].checked = false;
		document.forms.alarmeditmode.mode[2].checked = false;

		document.forms.alarmcountquery.alarmqueryfrom.value = 1;
		document.forms.alarmcountquery.alarmqueryto.value = this.MaxCount;

		this.ShowQueryMode();
	}
	this.InitPage = _InitPage;


	// ##################################################################
	/* This populates the HTML event selectors.
	*/
	function _PopulateMessages() {

		// Populate the events.
		var msgchoice = document.getElementById("alarmchoice");

		// Create an decorated array.
		var msgarray = [];
		for (var i in this.MsgsTxts) {
			msgarray.push([this.MsgsTxts[i], i]);
		}
		// Sort by message text.
		msgarray.sort();


		// Populate the event messages.
		for (var i in msgarray) {
			var msgtag = msgarray[i][1];
			var msgtxt = this.MsgsTxts[msgtag];
			var newoption = document.createElement("option");
			newoption.value = msgtag;
			newoption.text = msgtxt;
			msgchoice.appendChild(newoption);
		}

	}
	this.PopulateMessages = _PopulateMessages;



	// ##################################################################
	// Set the dates to the default values.
	function _InitDateFields() {
		// Current date and time.
		var datenow = new Date();
		document.forms.alarmdatequery.alarmyearto.value = datenow.getFullYear();
		document.forms.alarmdatequery.alarmmonthto.value = datenow.getMonth() + 1;
		document.forms.alarmdatequery.alarmdayto.value = datenow.getDate();
		document.forms.alarmdatequery.alarmhourto.value = datenow.getHours();
		document.forms.alarmdatequery.alarmminuteto.value = datenow.getMinutes();
		document.forms.alarmdatequery.alarmsecto.value = datenow.getSeconds();

		// The time 24 hours ago.
		var dateyesterday = new Date(datenow.getTime() - (24 * 60 * 60 * 1000));
		document.forms.alarmdatequery.alarmyearfrom.value = dateyesterday.getFullYear();
		document.forms.alarmdatequery.alarmmonthfrom.value = dateyesterday.getMonth() + 1;
		document.forms.alarmdatequery.alarmdayfrom.value = dateyesterday.getDate();
		document.forms.alarmdatequery.alarmhourfrom.value = dateyesterday.getHours();
		document.forms.alarmdatequery.alarmminutefrom.value = dateyesterday.getMinutes();
		document.forms.alarmdatequery.alarmsecfrom.value = dateyesterday.getSeconds();

	}
	this.InitDateFields = _InitDateFields;


	// ##################################################################
	// Get what the current selection is for the type of query (e.g. by date or alarm).
	// Returns: (integer) = A number representing the selected mode. 
	function _GetMode() {
		var mode = 0;
		if (document.forms.alarmeditmode.mode[0].checked) { var mode = mode | 1; }
		if (document.forms.alarmeditmode.mode[1].checked) { var mode = mode | 2; }
		if (document.forms.alarmeditmode.mode[2].checked) { var mode = mode | 4; }

		return mode;
	}
	this.GetMode = _GetMode;


	// ##################################################################
	// Display the correct query selections according to the current 
	// mode (by date by alarm, etc.).
	function _ShowQueryMode() {

		var mode = this.GetMode();

		// By date.
		if (mode & 1) { 
			this.Utils.ShowPageArea("showalarmsbydate");
		} else {
			this.Utils.HidePageArea("showalarmsbydate");
		}

		// By alarm.
		if (mode & 2) { 
			this.Utils.ShowPageArea("showalarmsbyalarm");
		} else {
			this.Utils.HidePageArea("showalarmsbyalarm");
		}

		// By count.
		if (mode & 4) { 
			this.Utils.ShowPageArea("showalarmsbycount");
		} else {
			this.Utils.HidePageArea("showalarmsbycount");
		}

		return;

	}
	this.ShowQueryMode = _ShowQueryMode;



	// ##################################################################
	// Reset the date query fields back to their defaults.
	function _ResetDateQuery() {
		this.InitDateFields();
	}
	this.ResetDateQuery = _ResetDateQuery;


	// ##################################################################
	// Reset the alarm query selections back to their defaults.
	function _ResetAlarmQuery() {
		this.AlarmQueryList = [];

		// Delete any alarm selection which is listed on the page. 
		var querylist = document.getElementById("alarmquerylist");
		if (querylist.hasChildNodes()) {
			while (querylist.firstChild) {
				querylist.removeChild(querylist.firstChild);
			}
		} 
	}
	this.ResetAlarmQuery = _ResetAlarmQuery;



	// ##################################################################
	// Do a basic range check, set the appropriate colour, and return the result.
	function _CheckDateField(id, value, dmin, dmax) {
		var dateok = this.Utils.IntOk(value, dmin, dmax);
		this.Utils.ShowFieldStatusColour(dateok, id);
		return dateok;
	}
	this.CheckDateField = _CheckDateField;


	// ##################################################################
	// Validate date. Returns true if the date was OK.
	function _CheckFromDate() {

		// First, do a basic check.
		var year = document.forms.alarmdatequery.alarmyearfrom.value;
		var yearok = this.CheckDateField("alarmyearfrom", year, 0, 3000);

		var month = document.forms.alarmdatequery.alarmmonthfrom.value;
		var monthok = this.CheckDateField("alarmmonthfrom", month, 1, 12);

		var day = document.forms.alarmdatequery.alarmdayfrom.value;
		var dayok = this.CheckDateField("alarmdayfrom", day, 1, 31);

		// If there are any errors, we can't continue with the next check.
		if (!yearok || !monthok || !dayok) { return false; }

		// Convert the year, month, and day fields into a single date.
		var newdate = new Date(year, month - 1, day);
		// If the new day does not match the original, then the day is invalid.
		if (newdate.getDate() != day) {
			this.Utils.ShowFieldStatusColour(false, "alarmdayfrom");
			return false;
		}

		// The date is OK.
		return true;

	}
	this.CheckFromDate = _CheckFromDate;


	// ##################################################################
	// Validate the "to" date. Returns true if the date was OK.
	function _CheckToDate() {

		// First, do a basic check.
		var year = document.forms.alarmdatequery.alarmyearto.value;
		var yearok = this.CheckDateField("alarmyearto", year, 0, 3000);

		var month = document.forms.alarmdatequery.alarmmonthto.value;
		var monthok = this.CheckDateField("alarmmonthto", month, 1, 12);

		var day = document.forms.alarmdatequery.alarmdayto.value;
		var dayok = this.CheckDateField("alarmdayto", day, 1, 31);

		// If there are any errors, we can't continue with the next check.
		if (!yearok || !monthok || !dayok) { return false; }

		// Convert the year, month, and day fields into a single date.
		var newdate = new Date(year, month - 1, day);
		// If the new day does not match the original, then the day is invalid.
		if (newdate.getDate() != day) {
			this.Utils.ShowFieldStatusColour(false, "alarmdayto");
			return false;
		}

		// The date is OK.
		return true;

	}
	this.CheckToDate = _CheckToDate;


	// ##################################################################
	// This contains the time parameters. These include the id or form field name
	// (these must be identical), and the minimum and maximum permitted values.
	this._TimeParams = {
		"alarmhourfrom" : [0, 23],
		"alarmminutefrom" : [0, 59],
		"alarmsecfrom" : [0, 59],
		"alarmhourto" : [0, 23],
		"alarmminuteto" : [0, 59],
		"alarmsecto" : [0, 59]
		}


	// ##################################################################
	// Validate the time form entry. Returns true if the time was OK.
	function _CheckTime(id) {
		// Check an individual field.
		if (id != "") {
			var tmin = this._TimeParams[id][0];
			var tmax = this._TimeParams[id][1];
			var formbase = document.forms.alarmdatequery[id];
			var fvalue = formbase.value;

			var dresult = this.CheckDateField(id, fvalue, tmin, tmax);
			return dresult;
		} else {
		// check everything.
			var allok = true;
			for (var nextid in this._DateParams) {
				var tmin = this._TimeParams[id][0];
				var tmax = this._TimeParams[id][1];
				var formbase = document.forms.alarmdatequery[nextid];
				var fvalue = formbase.value;

				var dresult = this.CheckDateField(id, fvalue, tmin, tmax);
				if (!dresult) { var allok = false; }
			}

			return allok;
		}
	}
	this.CheckTime = _CheckTime;



	// ##################################################################
	// Validate the count input.
	function _CheckCount(id) {
		switch (id) {
			case "alarmqueryfrom" : {
				var fromval = document.forms.alarmcountquery.alarmqueryfrom.value;
				var fromok = this.Utils.IntOkMin(fromval, 1);
				this.Utils.ShowFieldStatusColour(fromok, id);
				return fromok;
			}
			case "alarmqueryto" : {
				var toval = document.forms.alarmcountquery.alarmqueryto.value;
				var took = this.Utils.IntOkMin(toval, 1);
				this.Utils.ShowFieldStatusColour(took, id);
				return took;
			}
			case "" : {
				var fromval = document.forms.alarmcountquery.alarmqueryfrom.value;
				var fromok = this.Utils.IntOkMin(fromval, 1);
				this.Utils.ShowFieldStatusColour(fromok, "alarmqueryfrom");
				var toval = document.forms.alarmcountquery.alarmqueryto.value;
				var took = this.Utils.IntOkMin(toval, 1);
				this.Utils.ShowFieldStatusColour(took, "alarmqueryto");
				return fromok && took;
			}
		}
	}
	this.CheckCount = _CheckCount;
	


	// ##################################################################
	// Format the date portion of the query string. 
	function _FormatDate() {
		var fromdate = this.Utils.FormatQueryDate(
						document.forms.alarmdatequery.alarmyearfrom.value,
						document.forms.alarmdatequery.alarmmonthfrom.value,
						document.forms.alarmdatequery.alarmdayfrom.value,
						document.forms.alarmdatequery.alarmhourfrom.value,
						document.forms.alarmdatequery.alarmminutefrom.value,
						document.forms.alarmdatequery.alarmsecfrom.value);

		var todate = this.Utils.FormatQueryDate(
						document.forms.alarmdatequery.alarmyearto.value,
						document.forms.alarmdatequery.alarmmonthto.value,
						document.forms.alarmdatequery.alarmdayto.value,
						document.forms.alarmdatequery.alarmhourto.value,
						document.forms.alarmdatequery.alarmminuteto.value,
						document.forms.alarmdatequery.alarmsecto.value);
		return "time=".concat(fromdate, ",", todate);

	}
	this.FormatDate = _FormatDate;



	// ##################################################################
	// This is the current list of alarms to be queried.
	this.AlarmQueryList = [];


	// ##################################################################
	// Add a new alarm to the list of alarms to be part of the query.
	function _AddAlarm() {
		var newalarm = document.forms.alarmalarmquery.alarmchoice.value;

		// Ignore the default placeholder.
		if (newalarm == "none") { return; }

		// Check for duplicates.
		if (this.AlarmQueryList.indexOf(newalarm) >= 0) { return; }


		// Add it to the list.
		this.AlarmQueryList.push(newalarm);


		var querylist = document.getElementById("alarmquerylist");

		// Show the OR condition if there that one selected.
		if (this.AlarmQueryList.length > 1) {
			var padstr = this.ORStr;
		} else {
			var padstr = "";
		}

		var newmsg = document.createTextNode(padstr + "[" + this.MsgsTxts[newalarm] + "]");
		querylist.appendChild(newmsg);

	}
	this.AddAlarm = _AddAlarm;


	// ##################################################################
	// Format the alarm portion of the query string. 
	function _FormatAlarms() {
		return "alarms=".concat(this.AlarmQueryList);
	}
	this.FormatAlarms = _FormatAlarms;



	// ##################################################################
	// Format the count portion of the query string.
	function _FormatCount() {
		var fromval = document.forms.alarmcountquery.alarmqueryfrom.value;
		var toval = document.forms.alarmcountquery.alarmqueryto.value;

		return "count=".concat(fromval, ",", toval);
	}
	this.FormatCount = _FormatCount;



	// ##################################################################
	// Format a query string based on the selected parameters. Returns the 
	// complete query string including the URL, but not the host or port.
	// http://localhost:8082/aequery/alarmhist?time=20101217080000,20101220120059;alarms=PB1Alarm,PB2Alarm;count=2,4
	function _FormatQuery() {

		var mode = this.GetMode();

		// Nothing is selected.
		if (mode == 0) { return ""; }

		var querylist = [];

		// By date.
		if (mode & 1) {
			// Only proceed if the dates are valid. 
			if (this.CheckFromDate() && this.CheckToDate() && this.CheckTime("")) {
				querylist.push(this.FormatDate());
			} else {
				return "";
			}
		} 

		// By alarm.
		if (mode & 2) { 
			querylist.push(this.FormatAlarms());
		} 

		// By count.
		if (mode & 4) { 
			// Only proceed if the counts are valid. 
			if (this.CheckCount("")) {
				querylist.push(this.FormatCount());
			} else {
				return "";
			}
		} 


		return "/aequery/alarmhist?" + querylist.join(";");

	}
	this.FormatQuery = _FormatQuery;


	// ##################################################################
	// Update the page display with the new data. The data format is:
	// [1, 1292821240.519172, 1292821243.5283351, "PB2Alarm", 1, "HMI Demo", "inactive"]
	function _UpdatePageResults(pageresults) {

		// Now, update the server table data.
		var alarmtable = document.getElementById("alarmtable");

		// First, delete the table if it already exists (but not the header).
		while (alarmtable.rows.length > 1) {
			alarmtable.deleteRow(-1);
		}

		// This is used to give table rows alternating colours.
		var trowcounter = false;
		var trowcolours = ["t1", "t2"];

		// This counts the maximum number of rows to display.
		var limitcounter = 0;

		// Go through all the records.
		for (var i in pageresults) {

			var trow = alarmtable.insertRow(-1);

			// This is used to provide alternating row colours.
			if (trowcounter) {
				var tdclass = trowcolours[0];
			} else {
				var tdclass = trowcolours[1];
			}
			var trowcounter = !trowcounter;


			// Extract the original date and alarm tag number.
			var recdate = pageresults[i][1];
			var okdate = pageresults[i][2];
			var rectag = pageresults[i][3];

			// We need to format the date.
			var datelocal = new Date(recdate * 1000.0);
			var dateoklocal = new Date(okdate * 1000.0);

			// First cell is date.
			this.Utils.InsertTableCell(trow, 0, datelocal.toLocaleString(), tdclass);
			// Second cell is time OK.
			this.Utils.InsertTableCell(trow, 1, dateoklocal.toLocaleString(), tdclass);
			// Third cell is alarm.
			this.Utils.InsertTableCell(trow, 2, this.MsgsTxts[rectag], tdclass);
			// Client which acknowledged the alarm.
			this.Utils.InsertTableCell(trow, 3, pageresults[i][5], tdclass);
			// Number of times the alarm was active.
			this.Utils.InsertTableCell(trow, 4, pageresults[i][4], tdclass);


			// Limit the number of rows displayed.
			var limitcounter = limitcounter + 1;
			if (limitcounter > 100) { return; }
			
		}

	}
	this.UpdatePageResults = _UpdatePageResults;


}

// ##################################################################



