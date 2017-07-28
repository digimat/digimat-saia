##############################################################################
# Project: 	ModbusTCPSimpleClient2
# Module: 	ModbusTCPSimpleClient2.py
#		Based on the earlier ModbusTCPSimpleClient.py
# Purpose: 	Simple Modbus TCP client (master).
# Language:	Python 2.5
# Date:		02-Apr-2008.
# Ver:		06-Jul-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
#
# ModbusTCPSimpleClient2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ModbusTCPSimpleClient2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ModbusTCPSimpleClient2. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import socket
import ModbusTCPLib

##############################################################################

# Simple Modbus TCP Client.
class ModbusTCPSimpleClient(ModbusTCPLib.MBTCPClientMessages):
	"""This provides a simple socket interface for Modbus/TCP clients. 
	This replaces the earlier ModbusTCPSimpleClient and uses the newer
	ModbusTCPLib. The return values for ReceiveResponse differ slightly 
	from those in the older library as a result.
	"""

	#############################################################
	def __init__(self, host, port, timeout):
		"""Initialise the Ethernet connnection.
		Parameters: 
			host (string) = IP address of server.
			port (integer) = Port number of server.
			timeout (float) = Time out in seconds.
		"""
		# Initialise Modbus messages.
		ModbusTCPLib.MBTCPClientMessages.__init__(self)

		# Initialise the Ethernet port.
		self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self._socket.settimeout(timeout)
		self._socket.connect((host, port))

	#############################################################
	def __del__(self):
		""" Close the Ethernet connection.
		"""
		self._socket.close()


	#############################################################
	def SendRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		"""Construct and send a Modbus client request to a server.
		Parameters:
			TransID (integer 0 - 65535) = Modbus Transacation ID.
			UnitID (integer 0 - 255) = Modbus Unit ID.
			Function Code (integer) = Modbus function code.
			Addr (integer 0 - 65535) = Modbus memory address to read from server.
			Qty (integer 0 - 65535) = Quantity of items to read from server.
			MsgData (string) = A packed binary string containing the data to send. This
				parameter is optional for functions which do not send data.
		"""
		# Construct Modbus/TCP message
		message = self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)
		# Send the message.
		self._socket.send(message)


	#############################################################
	def ReceiveResponse(self):
		"""Receive and decode a Modbus server reply to a client.
		The parameters and Python exceptions are the same as those 
		defined in MBResponse in ModbusDataLib. 
		"""
		recvmsg = self._socket.recv(1024)
		return self.MBResponse(recvmsg)


	#############################################################
	def MakeRawRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = None):
		"""Construct a Modbus client request but do not send it.
		Parameters are the same as for SendRequest. Returns a raw binary string.
		"""
		# Construct Modbus/TCP message
		return self.MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData)


	#############################################################
	def SendRawRequest(self, Request):
		"""Send a previously constructed Modbus request to the server.
		Parameters: message (string).
		"""
		# Send the message.
		self._socket.send(Request)


	#############################################################
	def GetRawResponse(self):
		"""Get the raw message response string from the server, but
		do not decode it into parameters. 
		Returns a raw binary string.
		"""
		return self._socket.recv(1024)

##############################################################################

