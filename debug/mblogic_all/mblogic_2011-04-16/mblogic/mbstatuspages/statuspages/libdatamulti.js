/** ##########################################################################
# Project: 	MBLogic
# Module: 	libdatamulti.js
# Purpose: 	MBLogic status data library.
# Language:	javascript
# Date:		10-Jun-2010
# Ver:		10-Jun-2010
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
This is used to query the MBLogic server for soft logic data table values.
This differs from libdata in that it allows for a list of URLs and callbacks
which are automatically called in sequence. This allows for scanning of 
multiple data sources for a single page.
*/


// ##################################################################
/* Communicate with the MBLogic status interface.
Parameters: 
	hostname: (string) = Hostname (e.g. "localhost").
	port: (string) = Port number (e.g. "8080").
	ULRlist (array) = An array of URL strings which specify the data sources.
	callbacklist (array) = An array of references to callback functions which 
			will accept the received data. This must accept one parameter 
			containing the data.
	ULRlist and callbacklist must be of equal length.
*/
function StatusDataIFMulti(hostname, port, ULRlist, callbacklist) {
	// Port and host name info.
	this.hostname = hostname;
	this.Port = port;
	this.host = "http://" + hostname + ":" + port;

	this.ULRList = ULRlist;
	this.CallBackList = callbacklist;

	// Keeps track of where we are in the call list.
	this.ListIndex = 0;

	// If True, we want an asynchronous request. 
	this.AysyncOption = true;

	// The request object we use to communicate with the server. Initialising 
	// it indirectly seems to be necessary to keep WebKit happy.
	var reqobj = new XMLHttpRequest();
	this.ServerReq = reqobj;

	// Server communications watchdog counter.
	this.Watchdog = 0;
	// This limit gets changed when the callback function is set.
	this.WatchdogLimit = 1000000;
	this.WatchdogCallback = null;
	this.WatchdogTripped = false;



	// ##################################################################
	// Set a display callback to use if the watchdog times out.
	// Paramters: callback = The function to call if the watchdog times out.
	//	wlimit (integer) = If the client has polled the server for 
	//	"wlimit" iterations without a reply, "callback" will be called.
	//	with a parameter of true. When the next reply is received, "callback"
	//	will be called again with a parameter of false.
	function _SetWatchdogCallback(callback, wlimit) {
		this.WatchdogCallback = callback;
		this.WatchdogLimit = wlimit;
	}
	this.SetWatchdogCallback = _SetWatchdogCallback;


	// ##################################################################
	/* Send a request to the server. Call this regularly to poll the server.
	This will initiate a complete cycle of fetching data associated with the 
	initialisation parameters.
	*/
	function _SendGetRequest() {


		// Construct the GET query string.
		var ulrstr = this.ULRList[this.ListIndex];

		// Set the ansynchronous request to "true".
		this.ServerReq.open("GET", this.host + ulrstr, this.AysyncOption); 

		// Set the content type.
		this.ServerReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');


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

		// Watchdog to detect server communications problems.
		this.Watchdog++;
		if (this.Watchdog > this.WatchdogLimit) {
			// Check to see if it was set.
			if (this.WatchdogCallback != null) {
				this.WatchdogTripped = true;
				this.WatchdogCallback(true);
			}
		}

		// Send the request.
		this.ServerReq.send(null);


	}
	this.SendGetRequest = _SendGetRequest;



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

		// If we passed the above tests, we assume the server
		// responded with a valid message.

		// Check the watchdog.
		if (this.WatchdogTripped) {
			// Check to see if it was set.
			if (this.WatchdogCallback != null) {
				this.WatchdogCallback(false);
				this.WatchdogTripped = false;
			}
		}
		// Reset the watchdog counter.
		this.Watchdog = 0;


		// Convert the JSON string into an object.
		var responseobj = JSON.parse(this.ServerReq.responseText);


		// Update the page with the new results.
		callback = this.CallBackList[this.ListIndex];
		callback.UpdatePageResults(responseobj);

		// Update the list index.
		this.ListIndex++;

		// Check to see if we are through the complete list.
		if (this.ListIndex >= this.ULRList.length) {
			this.ListIndex = 0;
			return;
		} else {
		// Schedule the next target.
			this.SendGetRequest();
		}

	}
	this.ReceiveResponse = _ReceiveResponse;



// ##################################################################
}

