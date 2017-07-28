##############################################################################
# Project: 	MBLogic
# Module: 	HMIMsg.py
# Purpose: 	Provides MB-HMI message functions.
# Language:	Python 2.5
# Date:		10-Sep-2008.
# Ver.:		08-Sep-2009.
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################


_jsonerrmsg = """\nWarning - The optimised standard library was not found. 
A pure Python version is being imported instead.\n
"""

# Check to see if the standard Python JSON library is installed. This is a 
# standard library in Python versions 2.6 and later.
# If it is not present, then import a fall-back pure Python version of the 
# "simplejson" package instead. This allows compatibility with older
# versions of Python.

try:
	import json
except:
	print(_jsonerrmsg)
	import mbprotocols.py_simplejson as json


##############################################################################
"""
This module implements the MB-HMI protocol. It is responsible for converting
message data to and from the JSON based encoding. The same encoding is used
for both straight socket and http transports.

Full Example:
Request:
{
	"id" : "HMI 9876 from Water Pressure INC.",
	"msgid" : 12345,
	"read" : ["PB1", "PB2", "LS1", "SS5", "TankLevel"],
	"write" : {"SOL1" : 0, "SOL2" : 1, "Pump1Speed" : 2250}
}

Response:
{
	"id"    : "Scada 10934 from Water Pressure INC.",
	"msgid"  : 12347,
	"timestamp": 129873294,
	"status" : "ok" ,
	"inputs" : { "PB1" : 1 , "PB2" : 0 , "LS1" : 0 , "SS5" : 1 , "TankLevel" : 50.67 } ,
}

"""

# Error message strings.
_ErrorMsg = {
'serverrequest' : 'Error decoding JSON in HMI client request message at server: ',
'serverresponse' : 'Error encoding JSON in HMI server response message at server: ',
'clientrequest' : 'Error decoding JSON in HMI server response message at client: ',
'clientresponse' : 'Error encoding JSON in HMI client request message at client: '
}

##############################################################################
def ServerErrorMessage():
	"""Returns a message which represents the minimal valid response.
	This may be used when the system is not able to generate any other response.
	It returns a status of "servererror".
	"""
	return '{"id": "", "msgid": 0, "stat" : "servererror"}'

##############################################################################
def ProtocolErrorMessage():
	"""Returns a message which represents the minimal valid response.
	This may be used when the system is not able to generate any other response.
	It returns a status of "protocolerror".
	"""
	return '{"id": "", "msgid": 0, "stat" : "protocolerror"}'

##############################################################################
# Class to assemble or extract data from MB-HMI server messages.
#
class HMIServerMessages:
	"""Assemble or extract data from MB-HMI server messages."""
	########################################################
	def __init__(self, serverid):
		"""Parameters: serverid (string) - The server ID string which 
		is sent with each response.
		"""
		self._ServerID = serverid


	########################################################
	def HMIRequest(self, Message):
		""" Extract the data from an MB-HMI request message.
		 Parameters: Message = This is a string containing the MB-HMI message as received.
		 Return values: 
		 	clientid (string) = Client ID string.
			msgid (integer) = Client message ID.
			readlist (list) = List of tags to be read.
			readnoclist (list) = List of tags to be read with NOC.
			writevalues (dict) = Tags and values to be written.
			readablereq (dict) = Tags to be tested for readability.
			writablereq (dict) = Tags to be tested for writeability.
			eventrequest (dict) = Request for event messages.
			alarmsrequest (list) = Request for alarms.
			alarmackrequest (list) = Alarm acknowledge requests.
			alarmhistoryrequest (dict) = Request for alarm history messages.
		"""

		# Convert the message to a dictionary.
		try:
			msgdict = json.loads(Message)
		except:
			raise ParseError(_ErrorMsg['serverrequest'] + Message)

		# Extract the id string.
		try:
			clientid = msgdict['id']
		except:
			clientid = ''

		# Extract the msgid number.
		try:
			msgid = msgdict['msgid']
		except:
			msgid = 0

		# Extract the read list.
		try:
			readlist = msgdict['read']
		except:
			readlist = []

		# Extract the read NOC list.
		try:
			readnoclist = msgdict['readnoc']
		except:
			readnoclist = []

		# Extract the write dictionary.
		try:
			writevalues = msgdict['write']
		except:
			writevalues = {}

		# Extract the request to check for readable tags.
		try:
			readablereq = msgdict['readable']
		except:
			readablereq = {}

		# Extract the request to check for writable tags.
		try:
			writablereq = msgdict['writable']
		except:
			writablereq = {}

		# Extract the request for event messages.
		try:
			eventrequest = msgdict['events']
		except:
			eventrequest = {}

		# Extract the request for alarm messages.
		try:
			alarmsrequest = msgdict['alarms']
		except:
			alarmsrequest = {}

		# Extract the request for alarm acknowledgements.
		try:
			alarmackrequest = msgdict['alarmack']
		except:
			alarmackrequest = []

		# Extract the request for alarm history messages.
		try:
			alarmhistoryrequest = msgdict['alarmhistory']
		except:
			alarmhistoryrequest = {}


		return (clientid, msgid, readlist, readnoclist, writevalues, readablereq, 
			writablereq, eventrequest, alarmsrequest, alarmackrequest, 
			alarmhistoryrequest)


	########################################################
	def HMIResponse(self, msgid, serverstat, timestamp, readresult, 
		readnocresult, readerrors, writeerrors, readableresp, writableresp, 
		eventbuffer, eventerrors, 
		alarmresp, alarmerrors, 
		alarmhistbuffer, alarmhisterrors):
		"""
		Create an MB-HMI server response message.
		 Parameters: 
		 	serverid (string) = Server ID string.
		 	msgid (integer) = Message ID number.
		 	serverstat (string) = Server status.
		 	timestamp (real) = Time stamp (Unix Epoch format)
		 	readresult (dict) = Dictionary with read values.
		 	readnocresult (dict) = Dictionary with read NOC values.
		 	readerrors (dict) = Dictionary with read errors.
		 	writeerrors (dict) = Dictionary with write errors.
			readableresp (dict) = Dictionary with errors in testing readability.
			writableresp (dict) = Dictionary with errors in testing writeability.
			eventbuffer (list) = List with event records.
			eventerrors (dict) = Dictionary with event errors.
			alarmresp (list) = List with alarms.
			alarmerrors (dict) = Dictionary with alarm errors.
			alarmhistbuffer (list) = List with alarm history records.
			alarmhisterrors (list) = List with alarm history errors.
		 Return values: 
		 Message (string) = Valid JSON string containing a MB-HMI response message.
		"""

		# Construct a message dictionary.
		msgdict = {}
		msgdict['id'] = self._ServerID
		msgdict['msgid'] = msgid
		msgdict['stat'] = serverstat
		msgdict['timestamp'] = timestamp

		# Since the following are optional, we will exclude them if
		# they are empty.
		if (readresult != {}):
			msgdict['read'] = readresult
		if (readnocresult != {}):
			msgdict['readnoc'] = readnocresult
		if (readerrors != {}):
			msgdict['readerr'] = readerrors
		if (writeerrors != {}):
			msgdict['writeerr'] = writeerrors
		if (readableresp != {}):
			msgdict['readable'] = readableresp
		if (writableresp != {}):
			msgdict['writable'] = writableresp
		if (len(eventbuffer) > 0):
			msgdict['events'] = eventbuffer
		if (eventerrors != {}):
			msgdict['eventerr'] = eventerrors
		if (len(alarmresp) > 0):
			msgdict['alarms'] = alarmresp
		if (alarmerrors != {}):
			msgdict['alarmerr'] = alarmerrors
		if (len(alarmhistbuffer) > 0):
			msgdict['alarmhistory'] = alarmhistbuffer
		if (alarmhisterrors != {}):
			msgdict['alarmhisterr'] = alarmhisterrors

		# Convert to JSON and return.
		try:
			return json.dumps(msgdict)
		except:
			raise ParseError(_ErrorMsg['serverresponse'] + str(msgdict))


##############################################################################

##############################################################################
# Class to assemble or extract data from MB-HMI client messages.
#
class HMIClientMessages:
	""" Assemble or extract data from MB-HMI client messages."""
	########################################################
	def __init__(self):
		pass


	########################################################
	def HMIRequest(self, clientid, msgid, readlist, readnoclist, writevalues, 
		readablereq, writablereq, eventrequest, alarmrequest, alarmackrequest):
		"""
		Create an MB-HMI client request message.
		Parameters: 
			clientid (string) = Client ID string.
			msgid (integer) = Message ID number.
			readlist (list) = List with read tags.
			readnoclist (list) = List with read NOC tags.
			writevalues (dict) = Tags and values to be written.
			readablereq (dict) = Tags to be tested for readability.
			writablereq (dict) = Tags to be tested for writeability.
			eventrequest (dict) = Request for event messages.
			alarmrequest (list) = Request for alarm messages.
			alarmackrequest (list) = Acknowledge alarms.
	
		Return values: 
		Message (string) = Valid JSON string containing a MB-HMI response message.
		"""
	

		# Construct a message dictionary.
		msgdict = {}
		msgdict['id'] = clientid
		msgdict['msgid'] = msgid

		# Since the following are optional, we will exclude them if
		# they are empty.
		if (readlist != {}):
			msgdict['read'] = readlist
		if (readnoclist != {}):
			msgdict['readnoc'] = readnoclist
		if (writevalues != {}):
			msgdict['write'] = writevalues
		if (readablereq != {}):
			msgdict['readable'] = readablereq
		if (writablereq != {}):
			msgdict['writable'] = writablereq
		if (eventrequest != {}):
			msgdict['events'] = eventrequest
		if (alarmrequest != []):
			msgdict['alarms'] = alarmrequest
		if (alarmackrequest != []):
			msgdict['alarmack'] = alarmackrequest

		# Convert to JSON and return.
		try:
			return json.dumps(msgdict)
		except:
			raise ParseError(_ErrorMsg['clientrequest'] + str(msgdict))


	########################################################
	def HMIResponse(self, Message):
		"""
		Extract the data from an MB-HMI response message.
		Parameters: Message = This is a string containing the MB-HMI message as received.
		Return values: 
			serverid (string) = Server ID string.
			msgid (integer) = Server message ID.
			serverstat (string) = Server status.
			timestamp (real) = Time stamp (Unix Epoch format)
			readresult (dict) = Dictionary of tags read.
			readnocresult (dict) = Dictionary of tags read using NOC.
			readerrors (dict) = Dictionary with read errors.
		 	writeerrors (dict) = Dictionary with write errors.
			readableresp (dict) = Tags which were tested for readability.
			writableresp (dict) = Tags which were tested for writeability.
			eventbuffer (list) = List with event records.
			eventerrors (dict) = Dictionary with event errors.
			alarmresp (list) = List with alarms.
			alarmerrors (dict) = Dictionary with alarm errors.
			alarmhistbuffer (list) = List with alarm history records.
			alarmhisterrors (list) = List with alarm history errors.
		"""

		# Convert the message to a dictionary.
		try:
			msgdict = json.loads(Message)
		except:
			raise ParseError(_ErrorMsg['clientresponse'] + Message)

		# Extract the id string.
		try:
			serverid = msgdict['id']
		except:
			serverid = ''

		# Extract the msgid number.
		try:
			msgid = msgdict['msgid']
		except:
			msgid = 0

		# Extract the status.
		try:
			serverstat = msgdict['stat']
		except:
			serverstat = 'none'

		# Extract the time stamp.
		try:
			timestamp = msgdict['timestamp']
		except:
			timestamp = 0.0

		# Extract the read dictionary.
		try:
			readresult = msgdict['read']
		except:
			readresult = {}

		# Extract the read NOC dictionary.
		try:
			readnocresult = msgdict['readnoc']
		except:
			readnocresult = {}

		# Extract the read error dictionary.
		try:
			readerrors = msgdict['readerr']
		except:
			readerrors = {}

		# Extract the write error dictionary.
		try:
			writeerrors = msgdict['writeerr']
		except:
			writeerrors = {}

		# Extract the result of the check for readable tags.
		try:
			readableresp = msgdict['readable']
		except:
			readableresp = {}

		# Extract the result of the check for writable tags.
		try:
			writableresp = msgdict['writable']
		except:
			writableresp = {}

		# Extract the events buffer.
		try:
			eventbuffer = msgdict['events']
		except:
			eventbuffer = []

		# Extract the event error dictionary.
		try:
			eventerrors = msgdict['eventerr']
		except:
			eventerrors = {}

		# Extract the alarms.
		try:
			alarmresp = msgdict['alarms']
		except:
			alarmresp = []

		# Extract the alarm error dictionary.
		try:
			alarmerrors = msgdict['alarmerr']
		except:
			alarmerrors = {}

		# Extract the alarm acknowledgements.
		try:
			alarmhistbuffer = msgdict['alarmhistory']
		except:
			alarmhistbuffer = []

		# Extract the alarm history error dictionary.
		try:
			alarmhisterrors = msgdict['alarmhisterr']
		except:
			alarmhisterrors = {}

		return (serverid, msgid, serverstat, timestamp, readresult, 
			readnocresult, readerrors, writeerrors, 
			readableresp, writableresp, 
			eventbuffer, eventerrors, 
			alarmresp, alarmerrors, 
			alarmhistbuffer, alarmhisterrors)


##############################################################################

########################################################
class ParseError(Exception):
	"""This is an exception which is intended to be raised in the event
	of parsing errors.
	"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
########################################################


