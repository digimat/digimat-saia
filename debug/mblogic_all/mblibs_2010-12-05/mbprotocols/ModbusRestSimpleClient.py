#!/usr/bin/python
##############################################################################
# Project: 	ModbusRestSimpleClient
# Module: 	ModbusRestSimpleClient.py
# Purpose: 	Simple Modbus Rest client (master).
# Language:	Python 2.5
# Date:		09-Apr-2008.
# Ver:		03-May-2008.
# Author:	M. Griffin.
# Copyright:	2008 - Michael Griffin       <m.os.griffin@gmail.com>
#
# ModbusRestSimpleClient is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ModbusRestSimpleClient is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ModbusRestSimpleClient. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import httplib

import ModbusRestMsg

##############################################################################

# Simple Modbus Rest Client.
class ModbusRestSimpleClient(ModbusRestMsg.MBRestClientMessages):

	#############################################################
	# Initialise the http connnection parameters. This stores
	# the host and port, but does not initiate the actual connection.
	# Parameters: 
	# host (string) = IP or domain name of host plus the URL up to
	#	just before the function code. 
	# port (integer) = Port number of server.
	def __init__(self, host, port):
		self._port = port

		# Split the host name from any other additional path.
		urllist = host.split('/',1)
		self._urlhost = '%s' % urllist[0]
		if (len(urllist) > 1):
			self._urlprefix = urllist[1]
		else:
			self._urlprefix = ''

		# Initialise Modbus messages.
		ModbusRestMsg.MBRestClientMessages.__init__(self)


	#############################################################
	# Does nothing, but provided for compatibility with ModbusTCPSimpleClient.
	def __del__(self):
		pass


	#############################################################
	# Construct and send a Modbus MB-REST client request to a server.
	# Parameters:
	# TransID (integer 0 - 65535) = Modbus Transacation ID.
	# UnitID (integer 0 - 255) = Modbus Unit ID.
	# Function Code (integer) = Modbus function code.
	# Addr (integer 0 - 65535) = Modbus memory address to read from server.
	# Qty (integer 0 - 65535) = Quantity of items to read from server.
	# MsgData (string) = An ASCII string containing the data to send. This
	#	parameter is optional for functions which do not send data.
	# Returns:
	# Returns a tuple containing the following: 1) Transaction ID, 
	#	2) Function or Error Code, 3) Message Data or Exception Code,
	#	4) Http Status, 5) Http Reason.
	# For successful responses: Transaction ID (integer), Function (integer),
	#	and Message Data (string). Message Data is an ASCII string 
	#	containing the response data.
	# For error responses: Transcation ID (integer), Error Code (integer), 
	#	Exception Code (integer).
	# For undecodable responses: (0, 0, '0'). These are resposnses which
	# do not fit a valid message pattern.
	# Http Status (integer) and Http Reason (string) are standard Http codes.
	# 
	def SendRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):

		# Construct message
		RequestURL, RequestMsg =  self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)

		# Send the message.
		conn = httplib.HTTPConnection(self._urlhost, self._port)
		if FunctionCode in (1, 2, 3, 4):
			conn.request('GET', '/%s/%s' % (self._urlprefix, RequestURL))
		elif FunctionCode in (5, 6, 15, 16):
			Postheaders = {'modbusrest': RequestMsg}
			conn.request('POST', '/%s/%s' % (self._urlprefix, RequestURL), '', Postheaders)
		else:
			print 'Unsupported function code.'

		# Get the response from the server.
		response = conn.getresponse()
		httpstatus, httpreason, recvmsg = response.status, response.reason, response.read()
		conn.close()

		# Decode the returned message.
		Recv_TransID, Recv_Function, Recv_Msg = self.MBResponse(recvmsg)

		# Return the reply.
		return Recv_TransID, Recv_Function, Recv_Msg, httpstatus, httpreason


	#############################################################
	# Construct a Modbus MB-REST client request but do not send it.
	# Parameters are the same as for SendRequest. 
	# Returns a tuple with two strings. RequestURL, RequestMsg.
	def MakeRawRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		# Construct message
		return self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)


	#############################################################
	# Send a previously constructed Modbus MB-REST request to the server.
	# Parameters: RequestURL (string) = URL to used.
	# RequestMsg (string) = XML message (can be left blank for GET).
	# RequestGET (boolena) = True if GET is requested. Else, uses POST.
	def SendRawRequest(self, RequestURL, RequestMsg, RequestGET):

		# Send the message.
		conn = httplib.HTTPConnection(self._urlhost, self._port)
		if RequestGET:
			conn.request('GET', '/%s/%s' % (self._urlprefix, RequestURL))
		else:
			Postheaders = {'modbusrest': RequestMsg}
			conn.request('POST', '/%s/%s' % (self._urlprefix, RequestURL), '', Postheaders)

		# Get the response from the server.
		response = conn.getresponse()
		httpstatus, httpreason, recvmsg = response.status, response.reason, response.read()
		conn.close()

		# Decode the returned message.
		Recv_TransID, Recv_Function, Recv_Msg = self.MBResponse(recvmsg)

		# Return the reply.
		return Recv_TransID, Recv_Function, Recv_Msg, httpstatus, httpreason


##############################################################################

