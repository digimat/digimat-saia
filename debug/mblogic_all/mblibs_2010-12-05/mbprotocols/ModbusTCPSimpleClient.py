##############################################################################
# Project: 	ModbusTCPSimpleClient
# Module: 	ModbusTCPSimpleClient.py
# Purpose: 	Simple Modbus TCP client (master).
# Language:	Python 2.5
# Date:		02-Apr-2008.
# Ver:		14-Oct-2008.
# Author:	M. Griffin.
# Copyright:	2008 - Michael Griffin       <m.os.griffin@gmail.com>
#
# ModbusTCPSimpleClient is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ModbusTCPSimpleClient is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ModbusTCPSimpleClient. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import socket
import ModbusTCPMsg

##############################################################################

# Simple Modbus TCP Client.
class ModbusTCPSimpleClient(ModbusTCPMsg.MBTCPClientMessages):

	#############################################################
	# Initialise the Ethernet connnection.
	# Parameters: 
	# host (string) = IP address of server.
	# port (integer) = Port number of server.
	# timeout (float) = Time out in seconds.
	def __init__(self, host, port, timeout):
		# Initialise Modbus messages.
		ModbusTCPMsg.MBTCPClientMessages.__init__(self)

		# Initialise the Ethernet port.
		self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self._socket.settimeout(timeout)
		self._socket.connect((host, port))

	#############################################################
	# Close the Ethernet connection.
	def __del__(self):
		self._socket.close()


	#############################################################
	# Construct and send a Modbus client request to a server.
	# Parameters:
	# TransID (integer 0 - 65535) = Modbus Transacation ID.
	# UnitID (integer 0 - 255) = Modbus Unit ID.
	# Function Code (integer) = Modbus function code.
	# Addr (integer 0 - 65535) = Modbus memory address to read from server.
	# Qty (integer 0 - 65535) = Quantity of items to read from server.
	# MsgData (string) = A packed binary string containing the data to send. This
	#	parameter is optional for functions which do not send data.
	def SendRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		# Construct Modbus/TCP message
		message = self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)
		# Send the message.
		self._socket.send(message)


	#############################################################
	# Receive and decode a Modbus server reply to a client.
	# Returns a tuple containing the following:
	# For successful responses: Transaction ID (integer), Function (integer),
	#	and Message Data (string). Message Data is a packed binary 
	#	string containing the response data.
	# For error responses: Transcation ID (integer), Error Code (integer), 
	#	Exception Code (integer).
	# For undecodable responses: (0, 0, '0'). These are resposnses which
	# do not fit a valid message pattern.
	#
	def ReceiveResponse(self):
		recvmsg = self._socket.recv(1024)
		return self.MBResponse(recvmsg)


	#############################################################
	# Construct a Modbus client request but do not send it.
	# Parameters are the same as for SendRequest. 
	# Returns a string.
	def MakeRawRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		# Construct Modbus/TCP message
		return self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)


	#############################################################
	# Send a previously constructed Modbus request to the server.
	# Parameters: message (string).
	def SendRawRequest(self, Request):
		# Send the message.
		self._socket.send(Request)


	#############################################################
	# Get the raw message response string from the server, but
	# do not decode it into parameters.
	# Returns a string.
	def GetRawResponse(self):
		return self._socket.recv(1024)

##############################################################################

