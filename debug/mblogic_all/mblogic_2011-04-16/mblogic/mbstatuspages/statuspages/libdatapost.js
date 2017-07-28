/** ##########################################################################
# Project: 	MBLogic
# Module: 	libdatapost.js
# Purpose: 	POST data to server to send control messages.
# Language:	javascript
# Date:		20-Sep-2008.
# Ver:		26-Jun-2010
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


/**

**/

// ##################################################################
/* Communicate with the MBLogic status interface.
Parameters: 
	hostname: (string) = Hostname (e.g. "localhost").
	port: (string) = Port number (e.g. "8080").
	usercallback (function) = A reference to a callback function which 
		will accept the received data. This must accept one parameter 
		containing the data.
	E.g. StatusDataSend(host, port, ProgSource);

*/
function StatusDataSend(hostname, port, usercallback) {
	// Port and host name info.
	this.hostname = hostname;
	this.Port = port;
	this.host = "http://" + hostname + ":" + port;
	this.UserCallBack = usercallback;

	// If True, we want an asynchronous request. 
	this.AysyncOption = true;


	// The request object we use to communicate with the server. Initialising 
	// it indirectly seems to be necessary to keep WebKit happy.
	var reqobj = new XMLHttpRequest();
	this.ServerReq = reqobj;



	// ##################################################################
	/* Send a request to the server. Call this regularly to poll the server.
	This will fetch data associated with an optional query string.
	Parameters:
		url: (string) = URL including query string and parameters.
		E.g. "/statdata/plccurrentil.js?subrname=Alarms"
	*/
	function _SendPostRequest(url, data) {

		// Create the JSON string for the message.
		var reqdata = JSON.stringify(data);

		// Set the ansynchronous request to "true".
		this.ServerReq.open("POST", this.host + url, this.AysyncOption); 

		// Set the content type.
		this.ServerReq.setRequestHeader('Content-Type', 'application/json; charset=x-user-defined');

		// This overrides the MimeType to make sure the browser does 
		// not attempt to parse it.
		this.ServerReq.overrideMimeType('application/json; charset=x-user-defined'); 

		// The following two lines are not obvious, but they set up a 
		// callback function to receive the asynchronous response. It 
		// has to be done in this round about fashion because the 
		// "ServerReq" would not otherwise be visible to "ReceiveResponse"
		// when it gets called by XMLHttpRequest.
		if (this.AysyncOption){
			var respobj = this;
			this.ServerReq.onreadystatechange = function(ServerReq) {respobj.ReceiveResponse(ServerReq);}
		}


		// Send the request with the data.
		this.ServerReq.send(reqdata);


	}
	this.SendPostRequest = _SendPostRequest;



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


		// Convert the JSON string into an object.
		var responseobj = JSON.parse(this.ServerReq.responseText);

		// Update the page with the new results.
		//this.UserCallBack.UpdatePageResults(responseobj);
		this.UserCallBack(responseobj);

	}
	this.ReceiveResponse = _ReceiveResponse;



// ##################################################################
}

