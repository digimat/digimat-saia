##############################################################################
# Project: 	HMIServer
# Module: 	ModbusClient.py
# Purpose: 	Pass HMI requests on to a Modbus/TCP server.
# Language:	Python 2.5
# Date:		26-Feb-2009.
# Ver.:		21-Nov-2010.
# Copyright:	2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

"""This module converts HMI read and write requests into Modbus/TCP client 
requests and reads from and writes to a remote Modbus/TCP server accordingly. 
"""

############################################################

import time

from mbprotocols import ModbusTCPSimpleClient2
from mbprotocols import ModbusDataLib

import StatusReporter
import ModbusStatusReportMsg

############################################################

# Error messages.
errmsg = {
'starterr' : 'Error - Could not establish contact with remote host on start up.',
'commerr' : 'Error - Lost contact with remote host.',
'commretry' : 'Trying to re-establish contact with remote host.',
'commok' : 'OK - Re-established contact with remote host',
'retryerr' : 'Error - Could not re-establish contact with remote host after an error.',
'badresp' : 'Error - Bad response from remote host on func: %s  error %s'
}

############################################################

class DataTableAccess:
	"""Create a Modbus/TCP client to communcate with the source of the HMI data.
	"""


	########################################################
	def __init__(self, host, port, timeout, unitid=1):
		"""
		host (string) = IP address of server.
		port (integer) = Port for server.
		timeout (float) = Time out in seconds.
		unitid (integer) = The desired Modbus unit id.
		"""
		self._host = host
		self._port = port
		self._timeout = timeout
		self._uid = unitid
		self._transid = 1

		self._commerror = False
		try:
			self._msg = ModbusTCPSimpleClient2.ModbusTCPSimpleClient(self._host,
				 self._port, self._timeout)
			StatusReporter.Report.SetCommsStatusOK()
		except:
			self._commerror = True
			print(errmsg['starterr'])
			StatusReporter.Report.SetCommsStatusError()


	########################################################
	def _PrintError(self, msg):
		"""Print an error message.
		msg (string) = The error message to print.
		"""
		print('%s: %s' % (time.ctime(), msg))
		


	########################################################
	def _IncTransID(self):
		"""Increment the transaction ID.
		"""
		self._transid +=1
		if self._transid > 32767:
			self._transid = 1

	########################################################
	def _ModbusRequest(self, func, addr, qty, data):
		"""Read data from an address.
		"""

		if self._commerror:
			self._PrintError(errmsg['commretry'])
			try:
				self._msg = ModbusTCPSimpleClient2.ModbusTCPSimpleClient(self._host,
					 self._port, self._timeout)
				self._commerror = False
				self._PrintError(errmsg['commok'])
				StatusReporter.Report.SetCommsStatusOK()
			except:
				self._PrintError(errmsg['retryerr'])
				StatusReporter.Report.SetCommsStatusError()
				return ''

		try:
			
			self._msg.SendRequest(self._transid, self._uid, func, addr, qty, data)
			TransID, rfunct, raddr, rqty, MsgData, exccode = self._msg.ReceiveResponse()
			self._commerror = False
			StatusReporter.Report.SetCommsStatusOK()
		except:
			self._PrintError(errmsg['commerr'])
			self._commerror = True
			StatusReporter.Report.SetCommsStatusError()
			return ''

		if (rfunct != func):
			self._PrintError(errmsg['badresp'] % (rfunct, MsgData))
		

		# Log the messages for reporting purposes.
		StatusReporter.Report.AddFieldRequest(ModbusStatusReportMsg.ModbusClientFieldRequest(self._transid, \
					self._uid, func, addr, qty, data))

		StatusReporter.Report.AddFieldResponse(ModbusStatusReportMsg.ModbusClientFieldResponse(TransID, \
				rfunct, MsgData))


		# Increment the transaction id.
		self._IncTransID()

		return MsgData


	########################################################
	def GetCoilsBool(self, addr):
		"""Read coils from the host (function 1).
		addr (integer) = Modbus coil address.
		"""
		return ModbusDataLib.bin2boollist(self._ModbusRequest(1, addr, 1, None))[0]


	########################################################
	def GetDiscreteInputsBool(self, addr):
		"""Read discrete inputs from the host (function 2).
		addr (integer) = Modbus discrete inputs address.
		"""
		return ModbusDataLib.bin2boollist(self._ModbusRequest(2, addr, 1, None))[0]


	########################################################
	def GetHoldingRegistersInt(self, addr):
		"""Read holding registers from the host (function 3).
		addr (integer) = Modbus discrete inputs address.
		"""
		return ModbusDataLib.signedbin2intlist(self._ModbusRequest(3, addr, 1, None))[0]


	########################################################
	def GetInputRegistersInt(self, addr):
		"""Read input registers from the host (function 4).
		addr (integer) = Modbus discrete inputs address.
		"""
		return ModbusDataLib.signedbin2intlist(self._ModbusRequest(4, addr, 1, None))[0]


	########################################################
	def GetHoldingRegistersIntList(self, addr, qty):
		"""Read holding registers from the host (function 3).
		addr (integer) = Modbus discrete inputs address.
		qty (integer) = Number of registers.
		"""
		return ModbusDataLib.signedbin2intlist(self._ModbusRequest(3, addr, qty, None))


	########################################################
	def GetInputRegistersIntList(self, addr, qty):
		"""Read input registers from the host (function 4).
		addr (integer) = Modbus discrete inputs address.
		qty (integer) = Number of registers.
		"""
		return ModbusDataLib.signedbin2intlist(self._ModbusRequest(4, addr, qty, None))


	########################################################
	def SetCoilsBool(self, addr, data):
		"""Write coils to the host (function 15).
		addr (integer) = Modbus discrete inputs address.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = ModbusDataLib.boollist2bin([data])
		self._ModbusRequest(15, addr, 1, bindata)


	########################################################
	def SetHoldingRegistersInt(self, addr, data):
		"""Write holding registers from the host (function 16).
		addr (integer) = Modbus discrete inputs address.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = ModbusDataLib.signedintlist2bin([data])
		self._ModbusRequest(16, addr, 1, bindata)


	########################################################
	def SetHoldingRegistersIntList(self, addr, qty, data):
		"""Write holding registers from the host (function 16).
		addr (integer) = Modbus discrete inputs address.
		qty (integer) = Number of registers.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = ModbusDataLib.signedintlist2bin(data)
		self._ModbusRequest(16, addr, qty, bindata)


############################################################

