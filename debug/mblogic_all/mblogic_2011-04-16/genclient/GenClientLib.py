#!/usr/bin/env python
##############################################################################
# Project: 	MBLogic
# Module: 	GenClientLib.py
# Purpose: 	Demonstration Generic Client Interface (client).
# Language:	Python 2.6
# Date:		23-May-2010.
# Version:	26-Jan-2011.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

"""This module demonstrates the client part of a "Generic Client" interface.
"""

############################################################

import time
import struct
import binascii

import getopt, sys

from twisted.spread import pb
from twisted.internet import reactor


############################################################
class GenClient:
	"""Implements a generic client for MBLogic.
	"""


	########################################################
	def __init__(self, userprotocol, clientname):
		"""Params: userprotocol = The user protocol object.
			clientname (string) = The client name used to contact the server.
		"""
		self.UserProtocol = userprotocol()
		self._ClientName = clientname

		# Message texts.
		self._MsgTexts = {
			'errorconfig' : 'Error - Could not retrieve the configuration from the server %s.',
			'errorreq' : 'Error - Invalid request for server command %s.',
			'errorbroker' : 'Fatal error - Stale broker for client %s at %s',
			'errorcmd' : 'Error - Invalid server command %s',

			'gotparams' : 'Got parameters from server for client %s',
			'stopreq' : 'Server requested stop for generic client %s at %s.',
		}


	########################################################
	def check_ConfigErrors(self, failure):
		"""An error occured while trying to retrieve the configuration parameters.
		"""
		print(self._MsgTexts['errorconfig'] % time.ctime())


	########################################################
	def check_CmdError(self, failure):
		"""An error occured on the server while trying to request a
		command from the server.
		"""
		print(self._MsgTexts['errorreq'] % time.ctime())


	########################################################
	def _DeadReferenceHandler(self):
		"""An error occured on the server while trying to request a
		command from the server.
		"""
		print(self._MsgTexts['errorbroker'] % (self._ClientName, time.ctime()))
		reactor.stop()


	########################################################
	def StartUp(self, genserver):
		"""Perform any one-time start up operations and initialises parameters.
		Parameters: genserver (obj) = A reference to the 
			remote server.
		"""
		self.GenServer = genserver
		# Configuration parameters from the server.
		# Host configuration. 
		self._HostConfig = {}
		# Client configuration.
		self._ClientConfig = {}
		# Command list.
		self._CmdList = {}
		self._ConnectStatus = 'notstarted'
		self._CmdStatus = []

		# List of client specified messages.
		self._ClientMsgs = []

		# Used to track and control configuration requests from the server.
		self._ConfigStatus = 'request'

		# Mirror of server data table.
		self._IOReadDataTable = {'coil' : [], 'inp' : [], 'inpreg' : [], 'holdingreg' : []}
		self._IOWriteDataTable = {'coil' : [], 'holdingreg' : [], 'inpreg' : [], 'holdingreg' : []}


		# Delay between getting a server response and returning to RunClient.
		self._IODelay = 0.100
		# Delay between cycles.
		self._RunDelay = 1.0

		

		# Tracks the state of the client.
		self._RunState = 'getparams'
		# Synchronise the server command.
		self._ServerCmd = 'restart'
		# Last server command executed.
		self._LastCmd = None
		# Fault code to be reported to system monitor.
		self._FaultCode = 0

		# This is the client status that is reported to the server.
		self._RunStatus = 'starting'

		# Call the main state machine.
		reactor.callLater(2.0, self.RunClient)

		# Schedule the next I/O update.
		reactor.callLater(self._IODelay, self.ScanServer)



	########################################################
	def RunClient(self):
		"""This acts as a state machine to control the current state
		and sequence of the client.
		"""

		# See if a new configuration has been requested.
		if self._ConfigStatus == 'request':
			self.GetConfig()
			self._ConfigStatus = 'waiting'


		# There is a new configuration that needs to be passed to the client.
		if self._ConfigStatus == 'received':
			self.UserProtocol.SetParams(self._HostConfig, self._ClientConfig, self._CmdList)
			self._ConfigStatus = 'validated'


		# Delay until next cycle.
		rundelay = 0

		# Run 
		if self._ServerCmd in ('run', 'pause', 'restart'):
			self._RunStatus = 'running'

			# Call the user code for the generic client. 
			(self._IOWriteDataTable, rundelay) = self.UserProtocol.NextCommand(self._IOReadDataTable, self._ServerCmd)

		# Halt the generic client.
		elif self._ServerCmd == 'stop':
			self._RunStatus = 'stopping'
			print(self._MsgTexts['stopreq'] % (self._ClientName, time.ctime()))
			self._ConnectStatus = 'stopped'
			reactor.callLater(rundelay, self.ShutDown)
			# We don't want to do anything other that shut down.
			return


		# We shouldn't ever see this.
		else:
			print(self._MsgTexts['errorcmd'] % self._ServerCmd)

		# Fetch the current client status.
		self._ConnectStatus, self._CmdStatus = self.UserProtocol.GetStatus()
		# Fetch the current client messages.
		self._ClientMsgs = self.UserProtocol.GetClientMsgs()


		# Check whether to use the user specified poll repeat time, or the default.
		if (rundelay <= 0):
			rundelay = self._RunDelay
		# Call the main state machine again.
		reactor.callLater(rundelay, self.RunClient)




	########################################################
	def GetConfig(self):
		"""Read the configuration parameters from the server. The
		configuration parameters determine the behaviour of the client.
		"""
		try:
			self.ParamsCallback = self.GenServer.callRemote('GetParams', self._ClientName)
			self.ParamsCallback.addCallback(self.ConfigResult)
			self.ParamsCallback.addErrback(self.check_ConfigErrors)
		except pb.DeadReferenceError:
			self._DeadReferenceHandler()

		# We have requested the new configuration.
		self._ConfigRequested = True


	########################################################
	def ConfigResult(self, params):
		"""Callback from the server for the configuration parameters.
		Parameters: params (tuple) = A tuple containing the folllowing items:
		HostConfig (dict) = The "standard" parameters.
		ClientConfig (dict) = The parameters which are special to the generic client.
		CmdList (list) = A list of client commands.
		The latter two sets of parameters have NOT been checked by the server.
		"""
		self._ClientConfig = params['clientparams']
		self._CmdList = params['cmdlist']
		self._HostConfig = params


		# We have new configuration parameters.
		self._ConfigStatus = 'received'

		print(self._MsgTexts['gotparams'] % self._ClientName)


	########################################################
	def _EncodeDataTable(self, dtable):
		"""Encode the data table lists to hex strings. This is used to improve
		performance when transfering the data via Perspective Broker.
		Parameters: dtable (dict) = A dictionary containing the data table.
		Returns (dict) = A dictionary containing the resulting encoded data. 
		"""
		encodedtable = {}
		# Coils.
		try:
			encodedtable['coil'] = binascii.hexlify(struct.pack('>%db' % len(dtable['coil']), *dtable['coil']))
		except:
			pass

		# Discrete inputs.
		try:
			encodedtable['inp'] = binascii.hexlify(struct.pack('>%db' % len(dtable['inp']), *dtable['inp']))
		except:
			pass

		# Holding registers.
		try:
			encodedtable['holdingreg'] = binascii.hexlify(struct.pack('>%dh' % len(dtable['holdingreg']), *dtable['holdingreg']))
		except:
			pass

		# Input registers.
		try:
			encodedtable['inpreg'] = binascii.hexlify(struct.pack('>%dh' % len(dtable['inpreg']), *dtable['inpreg']))
		except:
			pass

		return encodedtable


	########################################################
	def _DecodeDataTable(self, dtable):
		"""Decode hex strings into data table lists. This is used to improve
		performance when transfering the data via Perspective Broker.
		Parameters: dtable (dict) = A dictionary containing the encoded data.
		Returns (dict) = A dictionary containing the resulting decoded data. 
		"""
		decodedtable = {}
		# Coils.
		try:
			msgdata = binascii.unhexlify(dtable['coil'])
			decodedtable['coil'] = map(bool, struct.unpack('>%db' % len(msgdata), msgdata))
		except:
			pass

		# Discrete inputs.
		try:
			msgdata = binascii.unhexlify(dtable['inp'])
			decodedtable['inp'] = map(bool, struct.unpack('>%db' % len(msgdata), msgdata))
		except:
			pass

		# Holding registers.
		try:
			msgdata = binascii.unhexlify(dtable['holdingreg'])
			decodedtable['holdingreg'] = list(struct.unpack('>%dh' % (len(msgdata) / 2), msgdata))
		except:
			pass

		# Input registers.
		try:
			msgdata = binascii.unhexlify(dtable['inpreg'])
			decodedtable['inpreg'] = list(struct.unpack('>%dh' % (len(msgdata) / 2), msgdata))
		except:
			pass

		return decodedtable



	########################################################
	def ServerCmdResult(self, result):
		"""Callback from the server for server commands.
		Parameters: result (string, dict) = Response from server.
		The first item is the command. This instructs the client to 
			perform an action such as stop, halt, run, etc.
		The second item is a dictionary containing the requested
			read copy of the data table.
		"""
		# The results must be packed in a tuple because Twisted PB wants them that way.
		self._ServerCmd = result[0]
		self._IOReadDataTable = self._DecodeDataTable(result[1])


	########################################################
	def ScanServer(self):
		"""Go through the input and output buffers and schedule the read 
		and write operations. This sends the following information:
		* client name - This identifies the client to the server.
		* runs status - The current running status of the client.
		* connection status - The status of the connection.
		* command status - The status of each command.
		* client messages - The current messages from the client. 
		* data table write - The values to write to the server data table.
		"""
		try:
			cmdstat = self._CmdStatus
			self._CmdStatus = []

			wrtable = self._EncodeDataTable(self._IOWriteDataTable)

			self.CmdCallback = self.GenServer.callRemote('GetServerCmd', 
							self._ClientName, self._RunStatus, 
								self._ConnectStatus, cmdstat,
								self._ClientMsgs,
								wrtable)
			self.CmdCallback.addCallback(self.ServerCmdResult)
			self.CmdCallback.addErrback(self.check_CmdError)
		except pb.DeadReferenceError:
			self._DeadReferenceHandler()



		# Schedule the next I/O update.
		CallID = reactor.callLater(self._IODelay, self.ScanServer)



	########################################################
	def ShutDown(self):
		"""Handle a shutdown request.
		"""
		reactor.stop()



############################################################

class StatCodes:
	"""Format the command status codes.
	"""

	########################################################
	def __init__(self):
		self._StatCodes = {'ok' : (0, 'ok', 'No errors'),
				'badfunc' : (1, 'badfunc', 'Unsupported function'),
				'badaddr' : (2, 'badaddr', 'Invalid address'),
				'badqty' : (3, 'badqty', 'Invalid quantity'),
				'deviceerr' : (4, 'deviceerr', 'Device error'),
				'frameerr' : (5, 'frameerr', 'Frame error'),				
				'connection' : (255, 'connection', 'Client connection lost'),
				'timeout' : (254, 'timeout', 'Message time out'),
				'servererr' : (253, 'servererr', 'Undefined server error'),
				'badtid' : (252, 'badtid', 'TID Error'),
				'noresult' : (251, 'noresult', 'No result'),
				}


	########################################################
	def FormatStatusCode(self, cmd, statcode):
		"""Format a command status code.
		Parameters: cmd (string) - A command name.
			statcode (string) - A command status code.
		Returns: ('cmd', 'statvalue', 'statcode', 'message')
		"""
		return (cmd, self._StatCodes[statcode][0],
				self._StatCodes[statcode][1],  
				self._StatCodes[statcode][2])




############################################################
class GenClientController:
	"""This controls the start up of the generic client.
	"""

	########################################################
	def __init__(self, port, clientname, clientprotocol):
		"""Parameters: port (integer) = The port number of the generic server.
			clientname (string) = The name used to identify the client to
				the generic server.
			clientprotocol (class) = The client protocol handler.
		"""
		self._Port = port
		self._ClientProtocol = clientprotocol
		self._ClientName = clientname


	########################################################
	def StartClient(self):
		"""Start the client.
		"""
		self._factory = pb.PBClientFactory()
		reactor.connectTCP("localhost", self._Port, self._factory)
		self._GenServer = self._factory.getRootObject()
		self._GenServer.addCallbacks(GenClient(self._ClientProtocol, self._ClientName).StartUp)
		reactor.run()


	########################################################
	def StopClient(self):
		"""Stop the generic client running.
		"""
		reactor.stop()



############################################################
class GetOptions:
	"""Get the command line options. These are required to allow the client
	to contact the server. This does not include the IP address. 
	"""

	########################################################
	def __init__(self):
		self._clientname = None
		self._port = None
		self._startdelay = 5.0

		# Message texts.
		self._MsgTexts = {
			'badoptunknown' : 'Unknown options.',
			'badoptport' : 'Invalid port number.',
			'badoptname' : 'Invalid client name.',
			'badoptstartdelay' : 'Invalid start delay.',
			'badoptrecognised' : 'Unrecognised option %s %s',
			'clientmissing' : 'Client name parameter is missing.',
			'portmissing' : 'Port parameter is missing'
		}


		# Read the command line options.
		try:
			opts, args = getopt.getopt(sys.argv[1:], 'p: c: d:', 
				['port', 'clientname', 'startdelay'])
		except:
			print(self._MsgTexts['badoptunknown'])
			sys.exit()


		# Parse out the options.
		for o, a in opts:

			# Port for server.
			if o == '-p':
				try:
					self._port = int(a)
				except:
					print(self._MsgTexts['badoptport'])
					sys.exit()

			# Client name.
			elif o == '-c':
				if (len(a) > 0):
					self._clientname = a
				else:
					print(self._MsgTexts['badoptname'])
					sys.exit()

			# Start delay.
			elif o == '-d':
				try:
					self._startdelay = int(a)
				except:
					print(self._MsgTexts['badoptstartdelay'])
					sys.exit()

			else:
				print(self._MsgTexts['badoptrecognised'] % (o, a))
				sys.exit()


		# Check to see that the clientname and port are present.
		if (self._clientname == None):
			print(self._MsgTexts['clientmissing'])
			sys.exit()

		if (self._port == None):
			print(self._MsgTexts['portmissing'])
			sys.exit()


	########################################################
	def GetStartParams(self):
		"""Return the start parameters.
		Return: port, client name, start delay.
		"""
		return self._port, self._clientname, self._startdelay



############################################################


############################################################
class ClientParamValidator:
	"""Standard client parameter validator. This parses, reformats, and does
	some basic checking of client parameters including client configuration
	and client commands. For commands, clients are expected to use a common 
	format. This also contains some common validator functions. Use of this is 
	optional for clients. 
	"""


	########################################################
	def __init__(self, clientname):
		# The client name.
		self._ClientName = clientname

		# Message texts.
		self._MsgTexts = {
			'badcmdformat' : '%(genclient)s - Bad client command format in %(cmdname)s.',
			'badparamname' : '%(genclient)s - Bad or missing client command parameter name in %(cmdname)s.',
			'invalidparam' : '%(genclient)s - Invalid client command parameter value in %(cmdname)s.',

			'badconfigparamvalue' : '%(genclient)s - Invalid client config parameter value in %(params)s.',
			'missingconfigparam' : '%(genclient)s - Missing client config parameter %(params)s.',
			'unkownconfigparam' : '%(genclient)s - Unknown client config parameter %(params)s.'
			}


	########################################################
	def _CheckCmd(self, cmd, cmdvalidator):
		"""This checks one command for ValidateCmdList.
		Parmeters: cmd (list) = One command.
			cmdvalidator (dict) = The validator dictionary from ValidateCmdList.
		Returns: (list) = The validated and reformatted command list, or None if
				there was an error.
			(string) = A descriptive error string, or empty string if there there
				were no errors.
		"""

		# The command name.
		cmdname = cmd[0]
		# Split the parameters between '=' signs.
		paramsplit = map(lambda x: x.split('='), cmd[1])

		# Check to see if all are formatted correctly.
		paramlen = filter(lambda x: len(x) != 2, paramsplit)
		# There should not be any which were not a pair. If there was,
		# stop here as something is seriously wrong.
		if len(paramlen) != 0:
			return None, self._MsgTexts['badcmdformat'] % {'cmdname' : cmdname, 
															'genclient' : self._ClientName}



		# Get the keys.
		paramkeys = map(lambda x: x[0], paramsplit)
		# And the values.
		paramvalues = map(lambda x: x[1], paramsplit)

		# Check if all the command parameters are present.
		if set(paramkeys) != set(cmdvalidator.keys()):
			return None, self._MsgTexts['badparamname'] % {'cmdname' : cmdname, 
															'genclient' : self._ClientName}


		# Call the validator for each item.
		checkedparams = map(lambda x,y: (x, cmdvalidator[x](y)), paramkeys, paramvalues)
		# Check to see if any failed validation.
		badparams = filter(lambda x: x[1] == None, checkedparams)
		if len(badparams) != 0:
			return None, self._MsgTexts['invalidparam'] % {'cmdname' : cmdname, 
															'genclient' : self._ClientName}


		# At this point everything should be OK.
		return (cmdname, checkedparams), ''



	########################################################
	def ValidateCmdList(self, cmdlist, cmdvalidator):
		"""Validate the command list.
		Parameters: cmdlist (list) = The command list in the format
				[('&cmdname', 'key1=value1, key2=value2, ...etc.'), ... etc. ]
			cmdvalidator (dict) = A dictionary containing the command parameters 
				together with validator functions. 	{'key1' : valditor1, 'key2' : validator2, etc.}
				Each validator function must accept one parameter (the value to 
				be validated), and return the reformatted parameter (e.g. 
				converted, scaled, etc.) if OK, or None if an error occurred.
		Return (list) = The command list in the original format, but validated and 
				with the individual parameters transformed as necessary.
			(list) = A list of any errors encountered. If there were no errors,
				the list will be empty.
		"""

		# Break up the command list into components.
		# Strip out all blanks.
		cmdstrip = map(lambda x : (x[0].replace(' ', ''), x[1].replace(' ', '')), cmdlist)
		# Split the parameters between commas.
		paramsplit = map(lambda x : (x[0], x[1].split(',')), cmdstrip)


		# Validate the commands one at a time.
		commands = []
		cmderrs = []
		for cmd in paramsplit:

			validated, errstr = self._CheckCmd(cmd, cmdvalidator)

			# Was OK?
			if validated != None:
				commands.append(validated)
			else:
				cmderrs.append(errstr)

		return commands, cmderrs


	########################################################
	def ValidateConfig(self, clientconfig, clvalidator):
		"""Validate the client configuration.
		Parameters: clientconfig (dict) = The client configuration in the format
			clvalidator (dict) = A dictionary containing the config parameters 
				together with validator functions. 	{'key1' : valditor1, 'key2' : validator2, etc.}
				Each validator function must accept one parameter (the value to 
				be validated), and return the reformatted parameter (e.g. 
				converted, scaled, etc.) if OK, or None if an error occurred.
		Return (dict) = The client configuration in the original format, but 
					validated and with the individual parameters transformed 
					as necessary.
			(list) = A list of any errors encountered. If there were no errors,
				the list will be empty.
		"""

		# Check to see if all the expected parameters are present.
		clientkeys = clientconfig.keys()
		validkeys = clvalidator.keys()

		# These ones are missing.
		missing = set(validkeys) - set(clientkeys)
		# These are unrecognized.
		unrecognised = set(clientkeys) - set(validkeys)

		# These are missiong.
		if len(missing):
			return None, [self._MsgTexts['missingconfigparam' % {'params' : missing, 
															'genclient' : self._ClientName}]]

		# These are unrecognised.
		if len(unrecognised):
			return None, [self._MsgTexts['unkownconfigparam'] % {'params' : unrecognised, 
															'genclient' : self._ClientName}]


		# Call the validator for each item.
		checkedparams = map(lambda (x,y): (x, clvalidator[x](y)), clientconfig.items())
		# Check to see if any failed validation.
		badparams = filter(lambda x: x[1] == None, checkedparams)
		if len(badparams) != 0:
			return None, [self._MsgTexts['badconfigparamvalue'] % {'params' : 
						', '.join(map(lambda x: x[0], badparams)), 'genclient' : self._ClientName}]


		# At this point everything should be OK.
		return dict(checkedparams), ['']



	########################################################
	# The following are commonly used validator functions. Custom validator 
	# functions can be created if the ones here are not suitable. 



	########################################################
	def PollAction(self, action):
		"""Validator for poll action. This just checks to see the the parameter
		is 'poll'.
		Parameters: action (string) = The command action (must be 'poll').
		Returns: (string) = The original parameter if ok, else None.
		"""
		if action == 'poll':
			return action
		else:
			None


	########################################################
	def IntCheck(self, checkval):
		"""Validator for positive integer value (>= 0).
		Parameters: checkval (string) = The string digits 0 - 9.
		Return: (int) = The original value as an integer, or None if error.
		"""
		try:
			c = int(checkval)
		except:
			return None

		if c >= 0:
			return c
		else:
			return None


	########################################################
	def DataTableTypeCheck(self, memtype):
		"""Validator for system data table memory types.
		Parameters: memtype (string) = A valid modbus memory type.
		Returns: (string) = The original parameter if ok, else None.
		"""
		if memtype in ('coil', 'inp', 'holdingreg', 'inpreg'):
			return memtype
		else:
			return None


	########################################################
	def PollTime(self, ptime):
		"""Validator for a polling time. 
		Parameters: ptime (string) = The polling time in milli-seconds.
		Returns: (float) = The validated time in seconds, or None if error.
		"""
		try:
			p = int(ptime)
		except:
			return None

		return p  / 1000.0


	########################################################
	def HostName(self, host):
		"""Validator for host name. Since host names and addresses can come 
		in many forms, this just checks to see that the parameter is not blank.
		Parameters: host (string) = The host name.
		Returns: (string) = The orginal host name, or None if error.
		"""
		if len(host) == 0:
			return None
		else:
			return host


	########################################################
	def Port(self, port):
		"""Validator for IP port (0 to 65,535). 
		Parameters: port (string) = The port number.
		Returns: (int) = The port number, or None if error.
		"""
		try:
			p = int(port)
		except:
			return None

		if (p < 0) or (p > 65535):
			return None

		return p



############################################################


