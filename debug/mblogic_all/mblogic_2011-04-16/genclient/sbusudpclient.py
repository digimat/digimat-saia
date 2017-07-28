#!/usr/bin/python
##############################################################################
# Project: 	MBLogic
# Module: 	sbusudpclient.py
# Purpose: 	MBLogic generic client for SAIA Ether-SBus client.
# Language:	Python 2.6
# Date:		02-Jan-2011.
# Version:	05-Jan-2011.
# Author:	M. Griffin.
# Copyright:	2011 - Michael Griffin       <m.os.griffin@gmail.com>
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
This implements an MBLogic generic client for SAIA Ether-SBus.
"""

import time
import signal

import GenClientLib

from mbprotocols import SBusSimpleClient, ModbusDataLib


############################################################

_SOFTWARENAME = 'SBClient'
_VERSION = '05-Jan-2011'

############################################################
class UserClient:
	"""
	"""

	########################################################
	def __init__(self):
		"""
		"""
		# TODO: This needs to be set automatically, but may require changes
		# to other generic clients.
		self._ClientName = 'SBus Client'

		# Configuration is OK.
		self._ConfigOK = False
		# Connection status.
		self._ConnectStatus = 'starting'
		# Command status.
		self._CmdStatusBuff = []

		# List of strings containing error messages.
		self._ErrorMsgs = []

		# Host configuration. 
		self._HostConfig = {}
		# Client configuration.
		self._ClientConfig = {}
		# Command list.
		self._CommandList = []
		self._CurrentCmd = 0
		# Client messages.
		self._ClientMsgs = []

		# Client status.
		self._ClientStatus = 'init'

		self._MsgID = 0

		# Default register data.
		self._RegData = [0,0]


		# This formats the command status messages
		self._StatusMsgs = GenClientLib.StatCodes()

		# The write data table.
		self._WriteTable = {}

		# This is the SBus client connection.
		self._SBusClient = None
		# This is the SBus message sequence number.
		self._MsgSeq = 0


	########################################################
	def _AddCmdStatus(self, cmd, statcode):
		"""Add the status for a command.
		"""
		self._CmdStatusBuff.append(self._StatusMsgs.FormatStatusCode(cmd, statcode))
		
		

	########################################################
	def GetClientMsgs(self):
		"""Return the list of client messages.
		"""
		return self._ClientMsgs


	########################################################
	def GetStatus(self):
		"""Return the current status. This must include the following:
		Connection Status (string) = A code that represents the status of
			the generic client, including the connection to any field
			devices.
		Command Status (dict) = A dictionary containing the latest
			status of any commands. This must be in the format:
			{'cmdname1' : (0, 'noresult', 'No Result'), 
			'cmdname2' : (0, 'ok', 'Ok'), etc. }
			The tuple values have the following meanings:
			1st (integer) - The status code to be written to the data table.
			2nd (string) - A key representing the status description.
			3rd (string) - An optional string representing the status description.
		"""
		cmdstat = self._CmdStatusBuff
		self._CmdStatusBuff = []
		return self._ConnectStatus, cmdstat




	########################################################
	def SbusStn(self, stn):
		"""Validator for SBus station.
		"""
		try:
			s = int(stn)
		except:
			return None

		if (s >= 0) and (s <= 255):
			return s
		else:
			return None

	########################################################
	def SBusCmd(self, cmd):
		"""Validator for SBus cmd.
		"""
		try:
			s = int(cmd)
		except:
			return None

		if s in (2, 3, 5, 6, 11, 13, 14):
			return s
		else:
			return None

	########################################################
	def SBusRmtAddr(self, raddr):
		"""Validator for remote SBus address. 
		"""
		try:
			r = int(raddr)
		except:
			return None

		if (r >= 0) and (r <= 65535):
			return r
		else:
			return None


	########################################################
	def SetParams(self, hostconfig, clientconfig, cmdlist):
		"""This must accept the configuration parameters
		dictionary and validate the parameters in it. 
		Parameters: 
			hostconfig (dict) = The standard configuration parameters 
				used by the server. The generic client does not 
				typically need to use this information.
			clientconfig (dict) = These are the parameters intended 
				for the generic client and must be validated by 
				the client.
			cmdlist (dict) = A list of commands for the client. These 
				must be validated by the client (if there are any).
		"""

		# This will validate the client parameters.
		paramvalidator = GenClientLib.ClientParamValidator(self._ClientName)


		# These are the client config validator functions.
		sbuscfg = {
			'repeattime' : paramvalidator.PollTime,
			'retrytime' : paramvalidator.PollTime,
			'cmdtime' : paramvalidator.PollTime,
			'timeout' : paramvalidator.PollTime,
			'host' : paramvalidator.HostName,
			'port' : paramvalidator.Port
		}

		# Validate the client configuration.
		validclconfig, clerrors = paramvalidator.ValidateConfig(clientconfig, sbuscfg)


		# These are the command validators.
		sbuscmds = {
			'action' : paramvalidator.PollAction, 
			'stn' : self.SbusStn, 
			'cmd' : self.SBusCmd, 
			'remoteaddr' : self.SBusRmtAddr, 
			'qty' : paramvalidator.IntCheck, 
			'datatype' : paramvalidator.DataTableTypeCheck, 
			'dataoffset' : paramvalidator.IntCheck
			}

		# Validate the client commands.
		commands, cmderrs = paramvalidator.ValidateCmdList(cmdlist, sbuscmds)

		# In addition to simple validation, we need to check the commands for 
		# consistency between associated parameters.
		for cmd in commands:
			# Turn the command parameters into a dictionary so we can 
			# access specific parameters more easily.
			rec = dict(cmd[1])

			# This is boolean command.
			if rec['cmd'] in (2, 3, 5, 11, 13):
				limit = 128
				cmdtype = 'bool'
			# else, we assume this is register command. 
			else:
				limit = 32
				cmdtype = 'reg'

			# Check to see if the quantity is within the limits of the protocol.
			if (rec['qty'] > limit) or (rec['qty'] < 1):
					cmderrs.append('Bad quantity in %s' % cmd[0])


			# Check to see if the SBus memory type is compatible with the 
			# main server data table memory type that we are going to try
			# to read or write.
			if (((cmdtype == 'bool') and (rec['datatype'] in ('holdingreg', 'inpreg'))) or
							((cmdtype == 'reg') and (rec['datatype'] in ('coil', 'inp')))):
				cmderrs.append('Incompatible memory types in %s' % cmd[0])

			# TODO: Check if the data will fit in the data table.

		faulterrs = clerrors
		faulterrs.extend(cmderrs)

		# Strip out any empty strings.
		faulterrs = filter(len, faulterrs)

		# Get the size of the write data table. We need to make this a class
		# variable, because there are several commands which over-write 
		# different parts of it. 
		# TODO: These sizes should be passed in as parameters rather than pulled out of the config.
		self._WriteTable = {}
		for dttype, dtsize in hostconfig['writetable'].items():
			if dttype in ('coil', 'inp'):
				self._WriteTable[dttype] = [False] * dtsize[1]
			else:
				self._WriteTable[dttype] = [0] * dtsize[1]


		if len(faulterrs) == 0:
			self._CommandList = commands
			self._RepeatTime = validclconfig['repeattime']
			self._RetryTime = validclconfig['retrytime']
			self._CommandTime = validclconfig['cmdtime']
			self._TimeOut = validclconfig['timeout']
			self._Port = validclconfig['port']
			self._Host = validclconfig['host']

			self._CommandIter = iter(self._CommandList)
			self._CmdStatus = dict(map(lambda cmd: (cmd[0], (0, 'noresult', 'No Result')), self._CommandList))
			self._ConfigOK = True
			self._ClientMsgs.append('The parameters were ok.')
		else:
			# Save the errors.
			self._ClientMsgs.extend(faulterrs)



	########################################################
	def NextCommand(self, readtable, servercmd):
		"""This should execute the next command, whatever it is. This
		is called regularly by GenClient.
		Parameters: readtable (dict) = A dictionary containing a mirror of the
			requested portion of the server data table. E.g.
			{'coil' : [True, False, True, True], 'inp' : [True, False, True, True],
			'inpreg' : [], 'holdingreg' : [1234, 5678]}

			servercmd (string) = A command from the server. This will 
				consist of one of the following:
				'run' = Run normally.
				'pause' = Pause operation.
				'restart' = A restart is requested. The restart 
					request will remain in effect until new
					parameters are loaded.

		Returns: dict, float = 
			- A dictionary in the same format as the "readtable" input parameter. This 
				will contain the data to be written to the server.
			- The time in seconds to wait before running this function again.

			Data table items in excess of those configured for transfer will be ignored.
		"""
		# First check if we've got a good parameter set.
		if not self._ConfigOK:
			# Set the connection status.
			self._ConnectStatus = 'stopped'
			nextpoll = 1.0

			return self._WriteTable, nextpoll


		# Get the next command.
		try:
			cmdname, cmdvalue = self._CommandIter.next()
			nextpoll = self._CommandTime
		except StopIteration:
			self._CommandIter = iter(self._CommandList)
			cmdname, cmdvalue = self._CommandIter.next()
			nextpoll = self._RepeatTime


		# See what the command says we should do. A typical command looks like this:
		# [('action', 'poll'), ('stn', 1), ('cmd', 3), ('remoteaddr', 0), 
		# 		('qty', 10), ('datatype', 'coil'), ('dataoffset', 0)]		
		cmdexp = dict(cmdvalue)
		cmd = cmdexp['cmd']
		datatype = cmdexp['datatype']
		dataoffset = cmdexp['dataoffset']
		qty = cmdexp['qty']

		# This is a write command, so we need data.
		# Write flags or outputs.
		if cmd in (11, 13):
			msgdata = ModbusDataLib.boollist2bin(readtable[datatype][dataoffset:dataoffset + qty])
		# Write registers. SBus registers are 32 bit, so we need 2 Modbus 
		# registers for each SBus register.
		elif cmd == 14:
			msgdata = ModbusDataLib.signedintlist2bin(readtable[datatype][dataoffset:dataoffset + (qty * 2)])
		else:
			msgdata = ''

		# #####################################
		# If we have an error, then bail out, close the socket and set an error
		# code. Set the client to None so we will re-initialise on the next round. 

		# Create the client if necessary.
		if self._SBusClient == None:
			self._SBusClient = SBusSimpleClient.SBusSimpleClient(self._Host, self._Port, self._TimeOut)

		self._MsgSeq += 1

		try:
			# Send the request.
			self._SBusClient.SendRequest(self._MsgSeq, cmdexp['stn'], cmd, qty, cmdexp['remoteaddr'], msgdata)
			# Get the response.
			telegramattr, recvmsgseq, recvdata = self._SBusClient.ReceiveResponse()
		# If we have an error, bail out here.
		except:
			self._SBusClient = None
			self._ConnectStatus = 'faulted'
			self._AddCmdStatus(cmdname, 'connection')
			# Exit here if error.
			return {}, 0.5

		# #####################################


		# This is a read command, so we need to save the data.
		# Read flags, inputs, or outputs.
		if (cmd in (2, 3, 5)) and (telegramattr == 1):
			booldata = ModbusDataLib.bin2boollist(recvdata)
			self._WriteTable[datatype][dataoffset:dataoffset + qty] = booldata[:qty]
			# Set the connection status.
			self._ConnectStatus = 'running'
			self._AddCmdStatus(cmdname, 'ok')
		# Read registers.
		elif (cmd == 6) and (telegramattr == 1):
			regdata = ModbusDataLib.signedbin2intlist(recvdata)
			# SBus registers are twice the size of Modbus registers.
			self._WriteTable[datatype][dataoffset:dataoffset + (qty * 2)] = regdata[:qty * 2]
			# Set the connection status.
			self._ConnectStatus = 'running'
			self._AddCmdStatus(cmdname, 'ok')
		# This was a write and the response was an ack or nak.
		elif (cmd in (11, 13, 14)) and (telegramattr == 2):
			# Decode the ack/nak
			acknak = ModbusDataLib.BinStr2SignedInt(recvdata)
			# The Ack was OK. 
			if acknak != 0:
				self._ConnectStatus = 'faulted'
				self._AddCmdStatus(cmdname, 'deviceerr')
			else:
				# Set the connection status.
				self._ConnectStatus = 'running'
				self._AddCmdStatus(cmdname, 'ok')
		else:
			self._ConnectStatus = 'faulted'
			self._AddCmdStatus(cmdname, 'deviceerr')


		return self._WriteTable, nextpoll


############################################################



############################################################
# Signal handler.
def SigHandler(signum, frame):
	print('\nOperator terminated generic client %s at %s' % (clientname, time.ctime()))
	gencontrol.StopClient()

def SigTermHandler(signum, frame):
	print('\Received terminate signal for generic client %s at %s' % (clientname, time.ctime()))
	gencontrol.StopClient()



# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)
signal.signal(signal.SIGTERM, SigTermHandler)


############################################################

# Get the command line parameter options.
CmdOpts = GenClientLib.GetOptions()
port, clientname, startdelay = CmdOpts.GetStartParams()


# Initialise the generic client handler.
gencontrol = GenClientLib.GenClientController(port, clientname, UserClient)


print('\n\nStarting generic client %s version %s at %s' % (clientname, _VERSION, time.ctime()))

# Delay the specified number of seconds. This will allow the main
# program to start up before trying to contact it.
time.sleep(startdelay)


# Start the generic client.
gencontrol.StartClient()

print('\n\nGeneric client %s halted at %s' % (clientname, time.ctime()))


