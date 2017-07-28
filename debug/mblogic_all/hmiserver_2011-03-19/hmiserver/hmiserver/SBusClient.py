##############################################################################
# Project: 	HMIServer
# Module: 	SBusClient.py
# Purpose: 	Pass HMI requests on to an SBus-Ethernet server.
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

"""This module converts HMI read and write requests into SBus Ethernet client 
requests and reads from and writes to a remote SBus-Ethernet server accordingly. 
"""

############################################################

import time

from mbprotocols import SBusSimpleClient
from mbprotocols import SBusMsg
from mbprotocols import ModbusDataLib

import SBusStatusReportMsg
import StatusReporter

############################################################

# Error messages.
errmsg = {
'starterr' : 'Error - Could not establish contact with remote host on start up.',
'commerr' : 'Error - Lost contact with remote host.',
'crcerr' : 'Error - CRC error in response from remote host.',
'msgerr' : 'Error - Bad message format in response from remote host.',
'commretry' : 'Trying to re-establish contact with remote host.',
'commok' : 'OK - Re-established contact with remote host',
'retryerr' : 'Error - Could not re-establish contact with remote host after an error.',
'badresp' : 'Error - Bad response from remote host on func: %s  error %s'
}

############################################################

class DataTableAccess:
	"""Create an SBus Ethernet client to communcate with the source of the HMI data.
	"""


	########################################################
	def __init__(self, host, port, timeout, stnaddr):
		"""
		host (string) = IP address of server.
		port (integer) = Port for server.
		timeout (float) = Time out in seconds.
		stnaddr (string) = SBus station address.
		"""
		self._host = host
		self._port = port
		self._timeout = timeout
		self._stnaddr = stnaddr
		self._msgseq = 1

		self._commerror = False
		try:
			self._msg = SBusSimpleClient.SBusSimpleClient(self._host,
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
	def _Incmsgseq(self):
		"""Increment the transaction ID.
		"""
		self._msgseq +=1
		if self._msgseq > 32767:
			self._msgseq = 1

	########################################################
	def _SBusRequest(self, cmd, addr, qty, data):
		"""Execute an SBus request.
		Parameters:
			cmd (integer) = The SBus command.
			addr (inetger) = The starting address.
			qty (integer) = The number of data elements.
			data (string) = The data to write as a packed binary string.
		Returns:
			A packed binary string containing the requested data. If an error
			occurs, an empty string will be returned.
		"""

		if self._commerror:
			self._PrintError(errmsg['commretry'])
			try:
				self._msg = SBusSimpleClient.SBusSimpleClient(self._host,
								 self._port, self._timeout)
				self._commerror = False
				self._PrintError(errmsg['commok'])
				StatusReporter.Report.SetCommsStatusOK()
			except:
				self._PrintError(errmsg['retryerr'])
				StatusReporter.Report.SetCommsStatusError()
				return ''


		try:
			# Send the request.
			self._msg.SendRequest(self._msgseq, self._stnaddr, cmd, qty, addr, data)
			# Wait for the response.
			telegramattr, msgseq, MsgData = self._msg.ReceiveResponse()
			self._commerror = False
			StatusReporter.Report.SetCommsStatusOK()
		# Message response had a CRC error.
		except SBusMsg.MessageLengthError:
			self._PrintError(errmsg['crcerr'])
			self._commerror = True
			StatusReporter.Report.SetCommsStatusError()
			return ''
		# Message response did not fit any known length.
		except SBusMsg.CRCError:
			self._PrintError(errmsg['msgerr'])
			self._commerror = True
			StatusReporter.Report.SetCommsStatusError()
			return ''
		# Message response had an unspecified error.
		except:
			self._PrintError(errmsg['commerr'])
			self._commerror = True
			StatusReporter.Report.SetCommsStatusError()
			return ''


		# Log the request and response messages for display on the web interface.
		StatusReporter.Report.AddFieldRequest(SBusStatusReportMsg.SBusClientFieldRequest(self._msgseq, \
				self._stnaddr, cmd, addr, qty, data))

		StatusReporter.Report.AddFieldResponse(SBusStatusReportMsg.SBusClientFieldResponse(cmd, \
				telegramattr, msgseq, MsgData))


		# Increment the transaction id.
		self._Incmsgseq()

		return MsgData



	########################################################
	def GetFlagsBool(self, addr):
		"""Read flags from the host (command 2).
		addr (integer) = SBus flags address.
		"""
		return ModbusDataLib.bin2boollist(self._SBusRequest(2, addr, 1, None))[0]


	########################################################
	def GetInputsBool(self, addr):
		"""Read inputs from the host (command 3).
		addr (integer) = SBus inputs address.
		"""
		return ModbusDataLib.bin2boollist(self._SBusRequest(3, addr, 1, None))[0]


	########################################################
	def GetOutputsBool(self, addr):
		"""Read outputs from the host (command 5).
		addr (integer) = SBus outputs address.
		"""
		return ModbusDataLib.bin2boollist(self._SBusRequest(5, addr, 1, None))[0]


	########################################################
	def GetRegistersInt(self, addr):
		"""Read registers from the host (command 6).
		addr (integer) = SBus registers address.
		"""
		return SBusMsg.signedbin2int32list(self._SBusRequest(6, addr, 1, None))[0]


	########################################################
	def GetRegistersIntList(self, addr, qty):
		"""Read registers from the host (command 6).
		addr (integer) = SBus registers address.
		qty (integer) = Number of registers.
		"""
		return SBusMsg.signedbin2int32list(self._SBusRequest(6, addr, qty, None))


	########################################################
	def SetFlagsBool(self, addr, data):
		"""Write flags to the host (command 11).
		addr (integer) = SBus flags address.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = ModbusDataLib.boollist2bin([data])
		self._SBusRequest(11, addr, 1, bindata)


	########################################################
	def SetOutputsBool(self, addr, data):
		"""Write outputs to the host (command 13).
		addr (integer) = SBus outputs address.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = ModbusDataLib.boollist2bin([data])
		self._SBusRequest(13, addr, 1, bindata)


	########################################################
	def SetRegistersInt(self, addr, data):
		"""Write registers to the host (command 14).
		addr (integer) = Modbus discrete inputs address.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = SBusMsg.signedint32list2bin([data])
		self._SBusRequest(14, addr, 1, bindata)


	########################################################
	def SetRegistersIntList(self, addr, qty, data):
		"""Write registers to the host (command 14).
		addr (integer) = Modbus discrete inputs address.
		qty (integer) = Number of registers.
		data (string) = Packed binary string with the data to write.
		"""
		bindata = SBusMsg.signedint32list2bin(data)
		self._SBusRequest(14, addr, qty, bindata)


############################################################

