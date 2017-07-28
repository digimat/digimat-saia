##############################################################################
# Project: 	hmiserver
# Module: 	HMIServerCommon.py
# Purpose: 	Common code library.
# Language:	Python 2.5
# Date:		08-Mar-2008.
# Ver:		03-Dec-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of HMIServer.
# HMIServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# HMIServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with HMIServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import asyncore
import asynchat
import socket
import getopt
import sys
import os
import time
import shutil
import BaseHTTPServer
import threading

from mbhmi import HMIAddr
from mbhmi import HMIConfig
from mbprotocols import HMIMsg

import MBWebPage
import StatusReporter
import MonUtils

############################################################

# Version of the protocol implemented.
_ProtocolVersion = 'Prototype 0.9rc'


# Name of the directory where the web pages are stored.
PageDir = 'hmipages'

# Name of the directory where the standard HMI library files are stored.
HMILibDir = os.path.join('hmiserver', 'hmilib')

# Name of the directory where the reports and help pages are stored.
AppPageDir = os.path.join('hmiserver', 'reportpages')

# Names of the reports.
HMIMsgPage = 'hmimsgs.html'
FieldDataMsgPage = 'fielddatamsgs.html'
SysStatusPage = 'hmiserverstatus-en.html'

ReportPages = [HMIMsgPage, FieldDataMsgPage, SysStatusPage]


# AJAX interface data path names.
StatusDataPath = 'statdata'
# Overall status summary.
StatusSummaryRpt = 'hmistatus.js'
# HMI configuration.
HMIConfigRpt = "hmicurrentconfig.js"
# Target for server control commands. 
SysControl = 'syscontrol.js'
# Target for HMI protocol message monitoring.
MsgHMIMonitorRpt = 'hmimsgmonitor.js'
# Target for field device message monitoring.
MsgFieldMonitorRpt = 'fieldmsgmonitor.js'



############################################################
#
class GetOptionsServer:
	"""Get the command line options for server versions.
	"""

	########################################################
	def __init__(self, defaultport, helpstr):
		"""Parameters: defaultport (int) = Default field device port.
			helpstr: (string) = The help message to print on error.
		"""
		self._fieldport = defaultport
		self._hmiport = 8082


		# Read the command line options.
		try:
			opts, args = getopt.getopt(sys.argv[1:], 'p: r:', 
				['mbport', 'webport'])
		except:
			print(helpstr)
			sys.exit()

		# Parse out the options.
		for o, a in opts:
			# Field protocol port number.
			if o == '-r':
				try:
					self._fieldport = int(a)
				except:
					print('Invalid field protocol port number.')
					sys.exit()

			elif o == '-p':
				try:
					self._hmiport = int(a)
				except:
					print('Invalid HMI port number.')
					sys.exit()


			# Print help.
			elif o == '-e':
				print(helpstr)
				sys.exit()

			else:
				print('Unrecognised option %s %s' % (o, a))
				sys.exit()

		# Check that the two ports are different.
		if (self._fieldport == self._hmiport):
			print('The field %d and HMI %d ports may not be the same.' % (self._fieldport, self._hmiport))
			sys.exit()


	########################################################
	def GetFieldPort(self):
		"""Return the port setting for the fieldbus protocol.
		"""
		return self._fieldport

	########################################################
	def GetHMIPort(self):
		"""Return the port setting for the HMI protocol.
		"""
		return self._hmiport


############################################################


############################################################
class GetOptionsClient:
	""" Get the command line options for client versions.
	"""

	########################################################
	def __init__(self, defaultport, helpstr):
		"""Parameters: defaultport (int) = Default field device port.
			helpstr: (string) = The help message to print on error.
		"""
		self._port = 8082
		self._rhost = 'localhost'
		self._rport = defaultport
		self._runitid = 1
		self._timeout = 5.0

		# Read the command line options.
		try:
			opts, args = getopt.getopt(sys.argv[1:], 'p: h: r: u: t: e:', 
				['port', 'remotehost', 'remoteport', 'unitid', 'timeout', 'help'])
		except:
			print('Unrecognised options.')
			sys.exit()

		# Parse out the options.
		for o, a in opts:

			# Port for web server.
			if o == '-p':
				try:
					self._port = int(a)
				except:
					print('Invalid local port number.')
					sys.exit()

			# Remote host name or IP address.
			elif o == '-h':
				if (len(a) > 0):
					self._rhost = a
				else:
					print('Invalid remote host name.')
					sys.exit()

			# Remote port number.
			elif o == '-r':
				try:
					self._rport = int(a)
				except:
					print('Invalid remote port number.')
					sys.exit()


			# Remote unit id.
			elif o == '-u':
				try:
					self._runitid = int(a)
				except:
					print('Invalid remote unit ID number.')
					sys.exit()
				if ((self._runitid > 255) or (self._runitid < 0)):
					print('Invalid remote unit ID number.')
					sys.exit()

			# Time out for field device communications.
			elif o == '-t':
				try:
					self._timeout = float(a)
				except:
					print('Invalid time out.')
					sys.exit()
				if (self._timeout < 0.0):
					print('Invalid Invalid time out.')
					sys.exit()

			# Help.
			elif o == '-e':
				print(helpstr)
				sys.exit()

			else:
				print('Unrecognised option %s %s' % (o, a))
				sys.exit()

	########################################################
	def GetPort(self):
		"""Return the port setting.
		"""
		return self._port

	########################################################
	def GetRemoteParams(self):
		"""Return the remote server parameters.
		Return: hostname, portnumber, timeout, unitid
		"""
		return self._rhost, self._rport, self._timeout, self._runitid


############################################################


########################################################
def HandleHMIMessage(recvjson):
	"""Handle an HMI protocol message.
	Parameters: recvjson (string) = The received JSON message.
	Returns: (string) = The response JSON string.
	"""

	# Add the recieved message to the message buffer.
	StatusReporter.Report.AddHMIRequest(recvjson)

	# Decode the message.
	try:
		(clientid, msgid, readlist, readnoclist, writevalues, 
		readablereq, writablereq, eventrequest, alarmrequest, 
		alarmackrequest, 
		alarmhistoryrequest) = HMIConf.HMIServerMsg.HMIRequest(recvjson)
	except:
		# Add the error response message to the message buffer.
		StatusReporter.Report.AddHMIResponse(HMIMsg.ProtocolErrorMessage())

		# Couldn't decode the JSON string.
		return HMIMsg.ProtocolErrorMessage()


	# Analyse the request and construct a response.
	try:
		# Write the data table.
		if (len(writevalues) > 0):
			writeerrors = HMIConf.HMIData.WriteDataTable(writevalues)
		else:
			writeerrors = {}

		# Read the data table.
		if (len(readlist) > 0):
			readresult, readerrors = HMIConf.HMIData.ReadDataTable(readlist)
		else:
			readresult = {}
			readerrors = {}

		# We don't support read with NOC.
		readnocresult = {}

		# Test the tags to see if they are readable.
		if (readablereq != {}):
			readableresp = HMIConf.HMIData.TestTags(readablereq, False)
		else:
			readableresp = {}

		# Test the tags to see if they are writable.
		if (writablereq != {}):
			writableresp = HMIConf.HMIData.TestTags(writablereq, True)
		else:
			writableresp = {}


		# Update the events from the data table. Our event scan rate
		# here is only as fast as the client asks for them.
		HMIConf.HMIData.UpdateEvents()
		# Construct a response.
		eventbuffer, eventerrors = HMIConf.HMIData.GetEvents(eventrequest)

		# Update the alarms from the data table. Our alarm scan rate
		# here is only as fast as the client asks for them.
		HMIConf.HMIData.UpdateAlarms()
		# Construct a response.
		alarmresp, alarmerrors = HMIConf.HMIData.GetAlarms(alarmrequest)

		# Update the alarm acknowledge requests from the client. These
		# only need to be processed as they arrive.
		HMIConf.HMIData.AckAlarms(alarmackrequest, clientid)

		# Update the alarm history from the records.
		# Construct a response.
		alarmhistorybuffer, alarmhisterrors = HMIConf.HMIData.GetAlarmHistory(alarmhistoryrequest)

		# Determine if there were any command errors. Since we don't
		# support read with NOC, any attempt at that is a command error.
		if ((writeerrors != {}) or (readerrors != {}) or 
			(len(readnoclist) != 0) or 
			(readableresp != {}) or	(writableresp != {}) or 
			(eventerrors != {}) or 
			(alarmerrors != {}) or 	(alarmhisterrors != {})):
			serverstat = 'commanderror'
		else:
			# If not, then the server status is ok.
			serverstat = 'ok'

	except:
		# Add the error response message to the message buffer.
		StatusReporter.Report.AddHMIResponse(HMIMsg.ServerErrorMessage())

		# We couldn't use the request message, so we need to return a server error.
		return HMIMsg.ServerErrorMessage()


	# The time stampe is UTC (GMT).
	timestamp = time.time()


	# Construct the response.
	try:
		sentjson =  HMIConf.HMIServerMsg.HMIResponse(msgid, serverstat, 
				timestamp, readresult, readnocresult, 
				readerrors, writeerrors, 
				readableresp, writableresp,
				eventbuffer, eventerrors, 
				alarmresp, alarmerrors, 
				alarmhistorybuffer, alarmhisterrors)

		# Add the response message to the message buffer.
		StatusReporter.Report.AddHMIResponse(sentjson)

		return sentjson

	except:
		# We couldn't encode a proper response for some reason.
		print('Error encoding MB-HMI response: %s' % time.ctime())
		
		# Add the error response message to the message buffer.
		StatusReporter.Report.AddHMIResponse(HMIMsg.ServerErrorMessage())

		return HMIMsg.ServerErrorMessage()

############################################################


############################################################

class HMIAsyncServer(asyncore.dispatcher):
	"""This listens for new HMI HTTP connection requests, and when
	a new connection is made it starts up a handler for it
	to run asynchronously.
	"""

	########################################################
	def __init__(self, port):
		try:
			asyncore.dispatcher.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.set_reuse_addr()
		except:
			print('Failed to create socket for port: %d. Exiting...' % port)
			sys.exit()

		# If we exit and then try to restart the server again immediately,
		# sometimes we cannot bind to the port until a short period of time
		# has passed. In this case, we will sleep, and try again later. If
		# we still don't succeed after several attempts, we will give up.
		bindcount = 10
		while True:
			try:
				self.bind(('', port))
				break	# Succeeded, so we can exit this loop.
			except:
				if (bindcount > 0):
					print('Failed to bind to socket for port: %d. Will retry in 30 seconds...' % port)
					bindcount -= 1
					time.sleep(30)
				else:
					print('Failed to bind to socket for port: %d. Exiting...' % port)
					sys.exit()

			
		# Try listening to port.
		try:
			self.listen(5)
		except:
			print('Failed listening to port: %d. Exiting...' % port)
			sys.exit()

		print('HMI server running on port %d...' % port)

	########################################################
	def __del__(self):
		self.close()

	########################################################
	def handle_accept(self):
		"""This handles the connection. We don't announce each 
		connection and disconnection because with HTTP this is routine.
		"""
		NewSocket, Address = self.accept()
		HMIWebRequestHandlerServers(NewSocket)

	########################################################
	def handle_close(self):
		pass


############################################################

# These are constants used by the HTTP server.

# Names of the days of the week.
_WEEKDAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
# Names fo the months of the year.
_MONTHNAMES = (None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

_ERRORMSG = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
	"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head><title>Error</title></head>
<body>
<h1>Error</h1>
<p><b>Error Code:</b> %(ecode)s</p>
<p><b>Message:</b> %(errmsg)s</p>
</body>
</html>
"""


############################################################
class HeaderStr:
	"""This is a container for the HTTP header string. This must
	be configured with the correct software name and version before
	we can use it.
	"""

	########################################################
	def __init__(self):
		self._HeaderStr = ''

	########################################################
	def ConfigHeader(self, softname, version):
		"""Configure the HTTP header string with the software name and version.
		Parameters: softname: (string) = The name of the program.
			version: (string) = The version number of the program.
		"""
		self._HeaderStr = ''.join(['HTTP/1.0 %(code)s %(message)s\r\n',
		'Server %s ver. %s\r\n' % (softname, version),
		'Date %(date)s\r\n',
		'Content-type %(ctype)s\r\n',
		'Content-Length %(flength)s\r\n',
		'Last-Modified %(lastmod)s\r\n',
		'\r\n'])

	########################################################
	def GetHeaderStr(self):
		"""Return the configured HTTP header string
		"""
		return self._HeaderStr


HeaderStrContainer = HeaderStr()


############################################################
class HMIWebRequestHandlerServers(asynchat.async_chat):
	"""This handles HMI http requests for servers.
	"""

	########################################################
	def __init__(self, newsocket):
		asynchat.async_chat.__init__(self, newsocket)
		# This buffers the incoming data.
		self.Inpbuffer = []
		# This provides an output buffer we can handle in chunks.
		self.OutBuffer = ''
		# The terminator is used to find the end of the headers.
		self.set_terminator('\r\n\r\n')
		self.reading_headers = True
		self.handling = False

		# The data of interest in a request.
		self.Content = ''
		self._Command = ''
		self._RecvPath = ''
		self._CasData = ''


	########################################################
	def collect_incoming_data(self, data):
		"""Buffer the incoming data.
		"""
		self.Inpbuffer.append(data)


	########################################################
	def found_terminator(self):
		"""A terminator condition was found.
		"""
		# Are we reading the headers?
		if self.reading_headers:
			self.reading_headers = False
			# All we want from the headers is the command, the path, and the
			# content length (if present).
			self._Command, self._RecvPath, clen, self._CasData = self._ParseHeaders(''.join(self.Inpbuffer))
			self.Inpbuffer = []

			# If this was a post, we also have to collect any content which may be present.
			if self._Command == "POST":
				self.set_terminator(clen)
			else:
				self.handling = True
				# Stop collecting data even if the browser sends more.
				self.set_terminator(None)
				# Handle the request.
				self.handle_request()

		# Read the contents, if any.
		elif not self.handling:
			# Stop collecting data even if the browser sends more.
			self.set_terminator(None)
			# Save the content as a single string.
			self.Content = ''.join(self.Inpbuffer)
			self.Inpbuffer = []
			self.handling = True
			# Handle the request.
			self.handle_request()



	########################################################
	def writable(self):
		"""Return true if there is output data to write.
		This method is called directly by asyncore.dispatcher to see
		if there is any data available to write.
		"""
		return len(self.OutBuffer) > 0


	########################################################
	def handle_write(self):
		"""Write out as much of the available output data as we can.
		This method is called directly by asyncore.dispatcher to get
		whatever data is available to write. asyncore.dispatcher will
		only take whatever data it can write immediately, so it may take
		several cycles to send all the available data.
		"""
		sent = self.send(self.OutBuffer)
		self.OutBuffer = self.OutBuffer[sent:]
		# Check if we are done writing all the available data.
		if not self.writable():
			self.handle_close()


	########################################################
	def handle_request(self):
		"""Read the incoming data and handle the request.
		This method is called directly by asyncore.dispatcher to handle
		reading data.
		"""

		# A POST request will be an AJAX protocol request. The data is 
		# contained in class level variables. 
		if self._Command == 'POST':
				self._Handle_POST()

		# A GET request will be for a file, or for AJAX monitoring data.
		elif self._Command == 'GET':
			self._Handle_GET(self._RecvPath)



	########################################################
	def handle_close(self):
		self.close()


	########################################################
	def _Handle_GET(self, recvpath):
		"""Serve a GET request. GET requests should all be requests for
			a file. These may be static files or reports which require
			data substitution.
		Parameters: recvpath (string) = The path to the requested file.
		"""
		# Check if the request is the right length. The first element
		# should be a blank ''.
		fpath = recvpath.split('/')
		if (len(fpath) == 2):
			filepath = fpath[1]
		elif (len(fpath) == 3):
			filepath = os.path.join(fpath[1], fpath[2])
		elif (len(fpath) == 4):
			filepath = os.path.join(fpath[1], fpath[2], fpath[3])
		else:
			# If it wasn't found, return an error
			self._SendError(404, 'File not found: %s - bad path length.' % recvpath)
			return

		# Is this an AJAX data request?
		if (len(fpath) == 3) and (fpath[1] == StatusDataPath):
			if self._AJAXResponse(fpath[2], recvpath):
				return


		# Look for the requested file in the HMI directory.
		if self._StaticFileResponse(PageDir, filepath):
			return

		# Look for the requested file in the HMI library directory.
		if self._StaticFileResponse(HMILibDir, filepath):
			return

		# Is is a recognised static data report? (Non-AJAX report).
		if (len(fpath) > 1) and (fpath[1] in ReportPages):
			if self._StaticReportResponse(AppPageDir, filepath, fpath[1]):
				return

		# Didn't find it? Check again in the application report directory.
		if self._StaticFileResponse(AppPageDir, filepath):
			return

		# Still didn't find it? Return an error.
		self._SendError(404, 'File not found.')


	########################################################
	def _Handle_POST(self):
		"""Serve a POST request. 
		"""

		# Check if the request is the right length. The first element
		# should be a blank ''.
		fpath = self._RecvPath.split('/')
		# Check to see if this is a status system command.
		if ((len(fpath) == 3) and (fpath[1] == StatusDataPath) and 
							(fpath[2] == SysControl)):
			self._HandleCommand(self.Content)

		# Assume this is probably a Cascadas message.
		else:
			# Analyse the request and construct a response.
			respjson = HandleHMIMessage(self._CasData)

			# Send the headers and content.
			self._SendOKResponse('application/json', len(respjson), time.mktime(time.gmtime()), respjson)



	########################################################
	def _ParseHeaders(self, recvdata):
		"""Parse the HTTP headers to get the command.
		Parameters: recvdata (string) = The received data.
		Returns: (string) = The HTTP request command
				(string) = The path to the requested file.
				(int) = The content length, or None if not present.
				(string) = The Cascadas data (or empty string if not present).
		"""
		command = ''
		filepath = ''
		clen = None
		cascadas = ''

		headerlines = recvdata.splitlines()

		# Find the command and file path.
		if len(headerlines) > 0:
			cmd = headerlines[0].split()
			if len(cmd) > 1:
				command = cmd[0]
				filepath = cmd[1]

		# Analyse the headers.
		headerdata = headerlines[1:]
		if len(headerlines) > 1:
			# Find the content length (if present). 
			clenline = filter(lambda x: x.startswith('Content-Length:'), headerdata)
			if len(clenline) > 0:
				clenhead, clenstr = clenline[0].split('Content-Length:')
				clen = int(clenstr)

			# Find the Cascadas protocol data (if present).
			casline = filter(lambda x: x.startswith('Cascadas:'), headerdata)
			if len(casline) > 0:
				cashead, cascadas = casline[0].split('Cascadas:')

		return command, filepath, clen, cascadas



	########################################################
	def _WriteResponse(self, outdata):
		"""Add the data to the response output buffer.
		Parameters: outdata (string) = Data to add to output buffer.
		"""
		self.OutBuffer = self.OutBuffer + outdata

		
	########################################################
	def _SendHeaders(self, rcode, ctype, flength, datestamp):
		"""Send the HTTP response headers.
		Parameters: rcode (integer) = The HTTP response code.
			ctype (string) = The content type.
			flength (integer) = content length.
			datestamp (float) = the time stamp.
		"""
		# Determine the response message from the code.
		if (rcode == 200):
			message = 'OK'
		elif (rcode == 404):
			message = 'Not Found'
		elif (rcode == 405):
			message = 'Method Not Allowed'
		else:	# Force this to 405
			rcode == 405
			message = 'Method Not Allowed'

		# Construct the date string.
		tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(datestamp)
		datestr = '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (_WEEKDAYS[tm_wday], tm_mday, 
							_MONTHNAMES[tm_mon], tm_year, tm_hour, tm_min, tm_sec)

		# This is the data which gets substituted into the header.
		headerdata = {'code' : rcode, 'message' : message, 'date' : datestr, 
			'ctype' : ctype, 'flength' : flength, 'lastmod' : datestr}
		headers = HeaderStrContainer.GetHeaderStr() % headerdata

		# Write the headers.
		self._WriteResponse(headers)



	########################################################
	def _SendOKResponse(self, ctype, flength, datestamp, cdata):
		"""Send a successful HTTP response including the content data.
		Parameters: ctype (string) = The content type.
			flength (integer) = content length.
			datestamp (float) = the time stamp.
			cdata (string) = The actual content data to write.
		"""
		self._SendHeaders(200, ctype, flength, datestamp)
		self._WriteResponse(cdata)


	########################################################
	def _SendError(self, ecode, errmsg):
		"""Send an error response.
		Parameters: ecode (integer) = The appropriate HTTP error code. 
			 errmsg (string) = The error message to appear in the content.
		"""
		errmsg = _ERRORMSG % {'ecode' : ecode, 'errmsg' : errmsg}
		flength = len(errmsg)
		self._SendHeaders(ecode, 'text/html', flength, time.time())
		self._WriteResponse(errmsg)


	########################################################
	def _AJAXResponse(self, reportname, recvpath):
		"""Prepare and send the response for the AJAX interface.
		Parameters: reportname (string) = The JSON data "file" name.
			recvpath (string) = The complete received path. 
		Returns: (boolean) = True if the requested path was found, false
			if the requested path was *not* found. 
		"""

		try:
			# Is this a request for the status summary?
			if reportname == StatusSummaryRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetStatParams())
			# Is this a request for the configuration data?
			elif reportname == HMIConfigRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetHMIConfigParams())
			# Is this a request for the HMI monitoring data?
			elif reportname == MsgHMIMonitorRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetHMIMsgsList())
			# Is this a request for the field device monitoring data?
			elif reportname == MsgFieldMonitorRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetFieldDeviceMsgsList())
			# Don't know this request.
			else:
				return False
		except:
			reportdata = None

		# Did we found a valid report?
		if reportdata != None:
			# Construct the response time stamp.
			resptimestamp = time.mktime(time.gmtime())

			# Send the headers and data.
			self._SendOKResponse('application/json', len(reportdata), resptimestamp, reportdata)

		else:
			# If it wasn't found, return an error
			self._SendError(404, 'File not found: %s.' % recvpath)

		return True



	########################################################
	def _StaticReportResponse(self, searchdir, filepath, reportname):
		"""Search for a static report file, insert the data, and send it if 
		found. The file *should* be present, as it's a known report file.
		Parameters: searchdir (string) = The directory to search in.
			filepath (string) = The name (path) of the report file to search for.
			reportname (string) = The name of the report file (not the full path).
		Return (boolean) = Return true if the file was found.
		"""
		# Look for the requested file in the specified directory.
		f, ctype, flength, ftime, ErrorStr = MBWebPage.GetWebPage(searchdir, filepath)
		# Send the reply.
		if f:
			reportfile = f.read(-1)
			f.close()

			# Substitute in the data.
			if (reportname == HMIMsgPage):
				reportdata = reportfile % StatusReporter.Report.GetHMIMsgs()
			elif (reportname == FieldDataMsgPage):
				reportdata = reportfile % StatusReporter.Report.GetFieldDeviceMsgs()
			elif (reportname == SysStatusPage):
				reportdata = reportfile % StatusReporter.Report.GetStaticParams()
			else:
				reportdata = ''

			# Send the headers and data.
			self._SendOKResponse(ctype, len(reportdata), ftime, reportdata)

			return True

		else:
			return False


	########################################################
	def _StaticFileResponse(self, searchdir, filepath):
		"""Search for a static file, and send it if found.
		Parameters: searchdir (string) = The directory to search in.
			filepath (string) = The name of the file to search for.
		Return: (boolean) = True if the file was found, false if it was not found.
		"""
		# Look for the requested file in the specified directory.
		f, ctype, flength, ftime, ErrorStr = MBWebPage.GetWebPage(searchdir, filepath)
		# Send the reply.
		if f:
			# Read in the page. We copy this in one large chunk.
			outdata = f.read(-1)
			f.close()
			# Send the headers and data.
			self._SendOKResponse(ctype, flength, ftime, outdata)
			return True

		else:
			return False


	########################################################
	def _HandleCommand(self, cmdtext):
		"""Handle system control commands which arrive via the web 
		interface.
		Parameters: cmdtext (string) = The command JSON string.
		"""
		# Decode the JSON.
		try:
			cmd = MonUtils.JSONDecode(cmdtext)
			cmdcode = cmd['mblogicsyscmd']
		except:
			self._SendError(404, MonUtils.JSONEncode({'mblogicsyscmd' : 'error'}))
			return

		timestamp = time.mktime(time.gmtime())
		respjson = MonUtils.JSONEncode({'mblogicsyscmd' : 'ok'})

		# Now, see what the command was.
		if cmdcode == 'reloadhmiconfig':
			print('\nRemote config reload command at %s\n' % time.ctime())
			# Send the headers and content.
			self._SendOKResponse('application/json', len(respjson), timestamp, respjson)

			HMIConf.LoadHMIConfig()

		elif cmdcode == 'shutdown':
			print('\nRemote shutdown command at %s\n' % time.ctime())
			# Send the headers and content.
			self._SendOKResponse('application/json', len(respjson), timestamp, respjson)

			asyncore.close_all()

		# We don't recognise the command.
		else:
			self._SendError(404, MonUtils.JSONEncode({'mblogicsyscmd' : 'error'}))
			

#############################################################################

class HMIConfigStart:
	"""HMI configuration loading and validation.
	Call LoadHMIConfig whenever the HMI configuration file parameter 
		is to be reloaded.
	This includes references to the following functions:
	HMIServerMsg
	HMIData
	"""

	########################################################
	def __init__(self):

		# These are function references which will be replaced by the correct
		# refernces when LoadHMIConfig is called.
		self.HMIServerMsg = None
		self.HMIData = None
		self._configvalidator = None
		self._datatable = None


	########################################################
	def SetConfigParams(self, configvalidator, datatable):
		"""Set the parameters which determine the configuration reload behaviour.
		Parameters: configvalidator: (object) = The configuration validator 
						for this protocol.
			datatable: (object) = The data table object.
		"""
		self._configvalidator = configvalidator
		self._datatable = datatable


	########################################################
	def LoadHMIConfig(self):
		"""Load and validate the HMI configuration.
		"""

		# This object validates the protocol specific parameters.
		self._HMITagValidator = self._configvalidator.HMIConfigValidator()


		starttimestamp = '%s' % time.ctime()

		# Load and validate the parameter file.
		hmitagconfig = HMIConfig.HMIConfig('mbhmi.config', starttimestamp, self._HMITagValidator)
		hmitagconfig.ReadConfigFile()

		# Print any errors which were found.
		for errmsg in hmitagconfig.GetConfigErrors():
			print(errmsg)


		# This handles encoding and decoding messages.
		self.HMIServerMsg = HMIMsg.HMIServerMessages(hmitagconfig.GetServerID())

		# Initialise the reserved tags handling.
		hmireservedtags = HMIAddr.HMIReservedTags(hmitagconfig.GetClientVersion(), _ProtocolVersion)

		# This handles converting MB-HMI tags to data table addresses.
		self.HMIData = HMIAddr.HMIData(self._datatable, hmitagconfig.GetConfigDict(), 
			hmireservedtags, hmitagconfig.GetEventConfig(), 
			hmitagconfig.GetAlarmConfig())

		# This initialises the last (previous) state dictionaries of the 
		# event and alarm handlers. This is required so they don't issue
		# spurious events and alarms on start up.
		self.HMIData.InitMessages()

		# Store the HMI configuration.
		StatusReporter.Report.SetHMIConfig(hmitagconfig.GetServerID(), hmitagconfig.GetClientVersion(),
			hmitagconfig.GetConfigDict(), hmitagconfig.GetEventConfig(), 
			hmitagconfig.GetAlarmConfig(), hmitagconfig.GetConfigErrors())


#############################################################################

# Stores the HMI configuration.
HMIConf = HMIConfigStart()


#############################################################################


############################################################
def ReadHMIFiles():
	"""Update the list of available HMI files.
	"""
	StatusReporter.Report.ListHMIFiles(PageDir)


#############################################################################



############################################################
class ClientControlContainer:
	"""This is a container for the client version information. This must
	be configured with the correct version before we can use it.
	"""

	########################################################
	def __init__(self):
		self._version = 'default version'

	########################################################
	def ConfigVersion(self, version):
		"""Configure the software version.
		Parameters: version: (string) = The version number of the program.
		"""
		self._version = version

	########################################################
	def GetVersion(self):
		"""Return the configured version string.
		"""
		return self._version

	########################################################
	def SetShutDown(self, server):
		"""Save a reference to the server so we can shut it down later.
		"""
		self._server = server
		# We must issue the shutdown request via another thread by using a 
		# threading timer. We must do it this way to avoid a deadlock in 
		# SocketServer.
		self._serverdelay = threading.Timer(0.5, self._shutdown)

	########################################################
	def ShutDown(self):
		"""Request a delayed server shutdown.
		"""
		self._serverdelay.start()


	########################################################
	def _shutdown(self):
		"""Call the server shutdown. Do not call this directly.
		"""
		# SocketServer shutdown is a new feature in Python 2.6. This will
		# not work with Python 2.5.
		try:
			self._server.shutdown()
		except:
			print('Remote shutdown failed - this feature may not be available.')


ClientControl = ClientControlContainer()



############################################################

class HMIWebRequestHandlerClients(BaseHTTPServer.BaseHTTPRequestHandler):
	"""Web request handler for clients.
	"""


	########################################################
	# Set server version number.
	server_version = ClientControl.GetVersion()
	# Set HTTP version.
	protocol_version = 'HTTP/1.0'


	########################################################
	def _request_report(self, result):
		"""This is just used to enable silencing the routine 
		connection logging.
		"""
		pass


	# Turn off routine display of connections.
	log_request = _request_report



	########################################################
	def _SendOKResponse(self, ctype, flength, datestamp, cdata):
		"""Send a successful HTTP response including the content data.
		Parameters: ctype (string) = The content type.
			flength (integer) = content length.
			datestamp (float) = the time stamp.
			cdata (string) = The actual content data to write.
		"""
		# Send the headers.
		self.send_head(ctype, flength, datestamp)
		# Send the page.
		self.wfile.write(cdata)


	########################################################
	def _AJAXResponse(self, reportname, recvpath):
		"""Prepare and send the response for the AJAX interface.
		Parameters: reportname (string) = The JSON data "file" name.
			recvpath (string) = The complete received path. 
		Returns: (boolean) = True if the requested path was found, false
			if the requested path was *not* found. 
		"""

		try:
			# Is this a request for the status summary?
			if reportname == StatusSummaryRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetStatParams())
			# Is this a request for the configuration data?
			elif reportname == HMIConfigRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetHMIConfigParams())
			# Is this a request for the HMI monitoring data?
			elif reportname == MsgHMIMonitorRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetHMIMsgsList())
			# Is this a request for the field device monitoring data?
			elif reportname == MsgFieldMonitorRpt:
				# Get the data and encode it.
				reportdata = MonUtils.JSONEncode(StatusReporter.Report.GetFieldDeviceMsgsList())
			# Don't know this request.
			else:
				return False
		except:
			reportdata = None


		# Did we found a valid report?
		if reportdata != None:
			# Construct the response time stamp.
			resptimestamp = time.mktime(time.gmtime())
			self._SendOKResponse('application/json', len(reportdata), resptimestamp, reportdata)
		else:
			# Still didn't find it? Return an error.
			self.send_error(404, 'File not found: %s.' % recvpath)

		return True


	########################################################
	def _StaticReportResponse(self, searchdir, filepath, reportname):
		"""Search for a static report file, insert the data, and send it if 
		found. The file *should* be present, as it's a known report file.
		Parameters: searchdir (string) = The directory to search in.
			filepath (string) = The name (path) of the report file to search for.
			reportname (string) = The name of the report file (not the full path).
		Return (boolean) = Return true if the file was found.
		"""
		# Look for the requested file in the specified directory.
		f, ctype, flength, ftime, ErrorStr = MBWebPage.GetWebPage(searchdir, filepath)
		# Send the reply.
		if f:
			reportfile = f.read(-1)
			f.close()

			# Substitute in the data.
			if (reportname == HMIMsgPage):
				reportdata = reportfile % StatusReporter.Report.GetHMIMsgs()
			elif (reportname == FieldDataMsgPage):
				reportdata = reportfile % StatusReporter.Report.GetFieldDeviceMsgs()
			elif (reportname == SysStatusPage):
				reportdata = reportfile % StatusReporter.Report.GetStaticParams()
			else:
				reportdata = ''

			self._SendOKResponse(ctype, len(reportdata), ftime, reportdata)

			return True

		else:
			return False




	########################################################
	def _StaticFileResponse(self, searchdir, filepath):
		"""Search for a static file, and send it if found.
		Parameters: searchdir (string) = The directory to search in.
			filepath (string) = The name of the file to search for.
		Return: (boolean) = True if the file was found, false if it was not found.
		"""
		# Look for the requested file in the specified directory.
		f, ctype, flength, ftime, ErrorStr = MBWebPage.GetWebPage(searchdir, filepath)
		# Send the reply.
		if f:
			# Send the headers.
			self.send_head(ctype, flength, ftime)
			# Send the page.
			shutil.copyfileobj(f, self.wfile)
			f.close()

			return True

		else:
			return False


	########################################################
	def do_GET(self):
		"""Serve a GET request."""

		# Check if the request is the right length. The first element
		# should be a blank ''.
		fpath = self.path.split('/')
		if (len(fpath) == 2):
			filepath = fpath[1]
		elif (len(fpath) == 3):
			filepath = os.path.join(fpath[1], fpath[2])
		elif (len(fpath) == 4):
			filepath = os.path.join(fpath[1], fpath[2], fpath[3])
		else:
			# If it wasn't found, return an error
			self.send_error(404, 'File not found: %s - bad path length.' % self.path)
			return

		# Is this an AJAX data request?
		if (len(fpath) == 3) and (fpath[1] == StatusDataPath):
			if self._AJAXResponse(fpath[2], self.path):
				return


		# Look for the requested file in the HMI directory.
		if self._StaticFileResponse(PageDir, filepath):
			return

		# Look for the requested file in the HMI library directory.
		if self._StaticFileResponse(HMILibDir, filepath):
			return

		# Is is a recognised static data report? (Non-AJAX report).
		if (len(fpath) > 1) and (fpath[1] in ReportPages):
			if self._StaticReportResponse(AppPageDir, filepath, fpath[1]):
				return

		# Didn't find it? Check again in the application report directory.
		if self._StaticFileResponse(AppPageDir, filepath):
			return


		# Still didn't find it? Return an error.
		self.send_error(404, 'File not found.')



	########################################################
	def do_POST(self):
		"""Serve a POST request."""

		# Split the headers into separate lines.
		recvheaders = str(self.headers).splitlines()

		# Check if the request is the right length. 
		fpath = self.path.split('/')

		# Check to see if this is a status system command.
		if ((len(fpath) == 3) and (fpath[1] == StatusDataPath) and 
							(fpath[2] == SysControl)):

			# Find the content length.
			clenline = filter(lambda x: x.startswith('Content-Length:'), recvheaders)
			if len(clenline) > 0:
				clenhead, clenstr = clenline[0].split('Content-Length:')
				clen = int(clenstr)
				# Read the data.
				content = self.rfile.read(clen)
				# Handle the command.
				self._HandleCommand(content)

		# Assume this is probably a Cascadas message.
		else:

			# Look for the POST data for the protocol.
			recvjson = ''
			casline = filter(lambda x: x.startswith('Cascadas:'), recvheaders)
			if len(casline) > 0:
				cashead, recvjson = casline[0].split('Cascadas:')


			# Analyse the request and construct a response.
			respjson = HandleHMIMessage(recvjson)


			# Send the data. If there is an error here, there's not 
			# much we can do about it so we ignore it.
			try:
				self._SendOKResponse('application/json', len(respjson), time.mktime(time.gmtime()), respjson)
			except:
				pass


	########################################################
	def _HandleCommand(self, cmdtext):
		"""Handle system control commands which arrive via the web 
		interface.
		Parameters: cmdtext (string) = The messge content (does not include headers).
		"""
		# Decode the JSON.
		try:
			cmd = MonUtils.JSONDecode(cmdtext)
			cmdcode = cmd['mblogicsyscmd']
		except:
			self.send_error(404, MonUtils.JSONEncode({'mblogicsyscmd' : 'error'}))
			return

		timestamp = time.mktime(time.gmtime())
		respjson = MonUtils.JSONEncode({'mblogicsyscmd' : 'ok'})

		# Now, see what the command was.
		if cmdcode == 'reloadhmiconfig':
			print('\nRemote config reload command at %s\n' % time.ctime())
			self._SendOKResponse('application/json', len(respjson), timestamp, respjson)

			HMIConf.LoadHMIConfig()

		elif cmdcode == 'shutdown':
			print('\nRemote shutdown command at %s\n' % time.ctime())
			self._SendOKResponse('application/json', len(respjson), timestamp, respjson)

			ClientControl.ShutDown()

		# We don't recognise the command.
		else:
			self.send_error(404, MonUtils.JSONEncode({'mblogicsyscmd' : 'error'}))
			

	########################################################
	def MBdate_time_string(self, timestamp=None):
		"""Return the current date and time formatted for a message header. 
		(2.4 compatability)
		Contributed by Chris Kearns.
		"""
		if timestamp is None:
			timestamp = time.time()
		year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
		s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
			self.weekdayname[wd],
			day, self.monthname[month], year,
			hh, mm, ss)
		return s


	########################################################
	def send_head(self, ctype, flength, lastmod):
		""" Send the headers."""

		# The file was found and opened, now send the response.
		self.send_response(200)
		self.send_header('Content-type', ctype)  
		self.send_header('Content-Length', flength)
		self.send_header('Last-Modified', self.MBdate_time_string(lastmod))
		self.end_headers()



#############################################################################

