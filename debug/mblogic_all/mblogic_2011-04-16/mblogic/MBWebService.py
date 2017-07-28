##############################################################################
# Project: 	MBLogic
# Module: 	MBWebService.py
# Purpose: 	Modbus Web Service Server.
# Language:	Python 2.5
# Date:		27-Mar-2008.
# Version:	23-Jul-2010.
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
"""
This module implements a web service which is closely patterned after Modbus.

The MBWebRestService class implements the web service functions. It is to be started
up using Twisted reactor.listenTCP. 
E.g.
RestRoot = MBWebService.MBWebRestService()
RestSite = server.Site(RestRoot)
reactor.listenTCP(ServerInstance.GetHostInfo(), RestSite)

"""
############################################################

import time

from twisted.web import resource

from mbprotocols import ModbusRestLib
from mbprotocols import ModbusRestMsg
import MBDataTable

############################################################

#  Create a server instance of the Modbus REST messages and
# initialise it with the maximum Modbus *protocol* address ranges.
# This is *not* necessarily the same as the data table address limits.
ModbusMsg = ModbusRestMsg.MBRestServerMessages(65535, 65535, 65535, 65535)

# Message to use for 404 errors which are caused due to incorrect URL parameters.
_ErrorHtml = """<html><head><title>404 - No Such Resource</title></head>
	<body><h1>No Such Resource</h1>
	<p>%s<br>
	Function: %s  Address: %s  Quantity: %s  TID: %s  UID: %s</p></body></html>
	""" 


############################################################
# Display an error message when attempting to access a
# resource which does not exist.
class ServiceError(resource.Resource):

	isLeaf = True


	########################################################
	# Set the Modbus error parameters to be used when
	# displaying an error condition.
	#
	def SetRESTError(self, MessageText):
		# HTML portion of error message.
		self._ErrorStr = """
		<html><head><title>404 - No Such Resource</title></head>
			<body><h1>No Such Resource</h1>
			<p>%s</p></body></html>
		""" % MessageText

	########################################################
	# This is called by Twisted to handle GET calls.
	#
	def render(self, request):
		request.setResponseCode(404)
		return self._ErrorStr

############################################################

_ServiceError = ServiceError()


############################################################
# Respond with the appropriate Modbus response.
class ShowModbusResponse(resource.Resource):

	isLeaf = True


	########################################################
	# Extract the Modbus parameters from the URL and arguements.
	# Returns: strings containing function code, address,
	# quantity of addresses, transaction ID, and userID.
	def _GetURLParams(self, request):
		# Get the URL path.
		path = request.postpath
		args = request.args

		# Extract the function code and address from the URL.
		func = path[0]
		addr = path[1]

		# Extract the quantity, transaction ID, and unit ID from the
		# query string. If not present, then default to an empty string.
		qty = args.get('qty', ('', ''))[0]
		tid = args.get('tid', ('', ''))[0]
		uid = args.get('uid', ('', ''))[0]

		return func, addr, qty, tid, uid



	########################################################
	# Construct the reply message data for an HTTP GET.
	#
	def HandleGETRequest(self, Func, Addr, Qty, TID, UID):
		# Decode message. 'RequestData' means either number of coils or registers, depending
		# upon the function code being received. 
		TransID, UnitID, FunctionCode, Address, RequestData, \
			ExceptionCode = ModbusMsg.MBGetRequest(Func, Addr, Qty, TID, UID)

		if FunctionCode == 1:		# Read coils.
			bindata = MBDataTable.MemMap.GetCoils(Address, RequestData)	# RequestData = quantity.
			RequestData = ModbusRestLib.inversorbin(bindata)
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode == 2:		# Read discrete inputs.
			bindata = MBDataTable.MemMap.GetDiscreteInputs(Address, RequestData)	# RequestData = quantity.
			RequestData = ModbusRestLib.inversorbin(bindata)
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode == 3:		# Read holding registers.
			bindata = MBDataTable.MemMap.GetHoldingRegisters(Address, RequestData)	# RequestData = quantity.
			RequestData = ModbusRestLib.bin2hex(bindata)
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode == 4:		# Read input registers.
			bindata = MBDataTable.MemMap.GetInputRegisters(Address, RequestData)	# RequestData = quantity.
			RequestData = ModbusRestLib.bin2hex(bindata)
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode > 127:	# Modbus exception.
			if (ExceptionCode == 1):
				ReplyData = _ErrorHtml % ('The Modbus function requested is not supported using HTTP Get', \
					Func, Addr, Qty, TID, UID)
				return ReplyData, False
			elif (ExceptionCode == 2):
				ReplyData = _ErrorHtml % ('The address or address plus quantity is out of range.', \
					Func, Addr, Qty, TID, UID)
				return ReplyData, False
			else:
				ReplyData = ModbusMsg.MBErrorResponse(TransID, UnitID, FunctionCode, ExceptionCode)
				return ReplyData, True

		else:
			# We shouldn't get here unless we can't understand the request at all.
			ReplyData = _ErrorHtml % ("""The Modbus function is not supported using HTTP GET or else one 
			or more URL parameters could not be understood.""", Func, Addr, Qty, TID, UID)
			return ReplyData, False


	########################################################
	# Construct the reply message data for an HTTP POST.
	#
	def HandlePOSTRequest(self, Func, Addr, Qty, TID, UID, XMLData):
		# Decode message. 'RequestData' means either number of coils or registers, depending
		# upon the function code being received. 
		TransID, UnitID, FunctionCode, Address, RequestData, \
			ExceptionCode = ModbusMsg.MBPostRequest(Func, Addr, Qty, TID, UID, XMLData)


		if FunctionCode == 5:		# Write single coil.
			if (RequestData == '0000'):
				bindata = '\x00\x00'
			else:
				bindata = '\xFF\x00'
			MBDataTable.MemMap.SetCoils(Address, 1, bindata)	# RequestData contains data.
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode == 6:		# Write single holding register.
			bindata = ModbusRestLib.hex2bin(RequestData)
			MBDataTable.MemMap.SetHoldingRegisters(Address, 1, bindata)	# RequestData contains data.
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData)
			return ReplyData, True

		elif FunctionCode == 15:	# Write multiple coils.
			bindata = ModbusRestLib.bininversor(RequestData[1])
			MBDataTable.MemMap.SetCoils(Address, RequestData[0], bindata)	# RequestData is a tuple.
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData[0])
			return ReplyData, True

		elif FunctionCode == 16:	# Write multiple holding registers.
			bindata = ModbusRestLib.hex2bin(RequestData[1])
			MBDataTable.MemMap.SetHoldingRegisters(Address, RequestData[0], bindata)	# RequestData is a tuple.
			ReplyData = ModbusMsg.MBResponse(TransID, UnitID, FunctionCode, RequestData[0])
			return ReplyData, True

		elif FunctionCode > 127:	# Modbus exception.
			if (ExceptionCode == 1):
				ReplyData = _ErrorHtml % ('The Modbus function requested is not supported using HTTP POST', \
					Func, Addr, Qty, TID, UID)
				return ReplyData, False
			elif (ExceptionCode == 2):
				ReplyData = _ErrorHtml % ('The address or address plus quantity is out of range.', \
					Func, Addr, Qty, TID, UID)
				return ReplyData, False
			else:
				ReplyData = ModbusMsg.MBErrorResponse(TransID, UnitID, FunctionCode, ExceptionCode)
				return ReplyData, True

		else:
			# We shouldn't get here unless we can't understand the request at all.
			ReplyData = _ErrorHtml % ("""The Modbus function is not supported using HTTP POST or else one 
			or more URL parameters could not be understood.""", Func, Addr, Qty, TID, UID)
			return ReplyData, False


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Extract the URL parameters.
		func, addr, qty, tid, uid = self._GetURLParams(request)

		# Handle the Modbus request.
		MsgData, OK = self.HandleGETRequest(func, addr, qty, tid, uid)

		# Check if request completed OK. This is an HTTP error, 
		# NOT a Modbus exception.
		if not OK:
			request.setResponseCode(404)

		# Return the results.
		return MsgData


	########################################################
	# Process a POST and return a response. This will handle
	# requests to write data.
	def render_POST(self, request):

		# Extract the URL parameters.
		func, addr, qty, tid, uid = self._GetURLParams(request)

		# Get the XML data from the message.
		ModbusXML = request.received_headers['modbusrest']

		# Handle the Modbus request.
		MsgData, OK = self.HandlePOSTRequest(func, addr, qty, tid, uid, ModbusXML)

		# Check if request completed OK. This is an HTTP error, 
		# NOT a Modbus exception.
		if not OK:
			request.setResponseCode(404)

		# Return the results.
		# For some reason Twisted complains this isn't a string unless
		# we do some extra type coercion on it with "str()".
		return str(MsgData)


############################################################

_ModbusResponse = ShowModbusResponse()


############################################################
# Implement a REST type web service for Modbus servers.
class MBWebRestService(resource.Resource):

	

	########################################################
	# This is called by Twisted to handle the URL decoding
	# and route the request to the appropriate destination.
	#
	def getChild(self, name, request):

		# Get the URL path.
		self._prepath = request.prepath
		self._postpath = request.postpath
		self._path = request.prepath[:]
		self._path.extend(request.postpath[:])


		# Check if the last element is empty (because it
		# was a '/'). If so, then delete it.
		if (self._path[-1] == ''):
			self._path.pop()

		# Get the query arguements.
		self._args = request.args

		# Increment the request counter for reporting.
		ReportTracker.IncRequestCounter()

		# If only 'modbus' in path, then show error page.
		if ((len(self._path) == 1) and (self._path[0].lower() == 'modbus')):
			return _ServiceError

		# Check if no path in URL.
		if (len(self._path) == 0):
			_ServiceError.SetRESTError('No service requested.')
			return _ServiceError

		# Check if modbus service is not being requested.
		if ((len(self._path) > 0) and (self._path[0] != 'modbus')):
			_ServiceError.SetRESTError('Unknown service requested.')
			return _ServiceError

		# Check if the path is too long or too short.
		if (len(self._path) != 3):
			_ServiceError.SetRESTError('Invalid number of arguments in URL.')
			return _ServiceError

		# Check if too many arguements in the query string.
		if (len(self._args) > 3):
			_ServiceError.SetRESTError('Invalid number of arguments in query string.')
			return _ServiceError


		# Point to the class which displays the web service results.
		return _ModbusResponse



##############################################################################



############################################################
class RepCounter:
	""" This handles calculating the server statistics for reporting purposes.
	"""

	########################################################
	def __init__(self):
		# For server connection stats calculations.
		self._RequestCounter = []

		# For updating the status information.
		self._StatusInfo = None


	########################################################
	def SetStatusInfo(self, statusinfo):
		""" Must call this to add a reference to the configuration 
		information. This allows status information to be
		tracked and reported.
		"""
		self._StatusInfo = statusinfo
	


	########################################################
	def IncRequestCounter(self):
		"""Increment the request counter. This keeps track when each
		request was made in order to calculate a request rate in terms of
		requests per unit of time.
		"""
		# Note: This list could be replaced by a deque if we don't need
		# to support anything older than Python 2.6. This would allow us
		# to use the maxlen parameter to automatically manage the deque length.

		# Add a time stamp to the end of the buffer.
		self._RequestCounter.append(time.time())
		# We limit the size of the buffer so it doesn't grow excessively.
		if len(self._RequestCounter) > 25:
			self._RequestCounter.pop(0)

		# Set the request rate in the container.
		self._StatusInfo.SetRequestCounter(self._RequestCounter)

ReportTracker = RepCounter()

##############################################################################



