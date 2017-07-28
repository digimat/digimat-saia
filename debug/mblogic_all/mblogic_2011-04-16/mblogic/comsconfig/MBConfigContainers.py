##############################################################################
# Project: 	MBLogic
# Module: 	MBConfigContainers.py
# Purpose: 	Validate and store configuration data.
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	18-Oct-2010.
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

import time

############################################################
# Container object for server information for
# Ethernet TCP connections.
class TCPServerConnection:
	"""
	This must be initialised with a dictionary containing the configuration 
	parameters for the connection information. The values are then validated
	and stored.
	This dictionary must have the form: ConfigDict = {'server' : string, 
		'protocol' : string, 'port' : integer}
		The dictionary keys correspond directly to the parameters in
		the configuration file.

	Public Methods:

	1) ConfigOK() - Returns true if the configuration is valid.

	The following methods return the validated configuration information.
	2) GetServerName()
	3) GetProtocolType()
	4) GetHostInfo()

	The following methods increment, decrement, and report on the value of the
	number of current connections from clients. 
	5) IncConnectionCount()
	6) DecConnectionCount()
	7) GetConnectionCount()
	8) SetConnectionCount()
	"""

	########################################################
	def _ReportError(self, errormsg):
		""" Report an error to the user.
		"""
		print(errormsg)

	########################################################
	def __init__(self, serverdata):
		"""serverdata = A dictionary containing the server configuration data.
		Also saves if the configuration was valid. This can be queried later
		by the ConfigOK method.
		"""
		# Number of active connections.
		self._ConnectionCount = 0
		# If configuration is OK.
		self._ConfigValid = True
		# Use to track request rate for those servers which use it.
		self._RequestCounter = []

		self._Server = serverdata.get('server', '')
		if len(self._Server) < 1:
			self._ReportError('Bad server name %s' % self._Server)
			self._ConfigValid = False

		self._Protocol = serverdata.get('protocol', 'None')

		try:
			self._Port = serverdata['port']
			self._Port = int(self._Port)	# Must be +ve integer.
		except:
			self._Port = -1
		if (self._Port < 0):
			self._ReportError('Invalid server port %d' % self._Port)
			self._ConfigValid = False


	########################################################
	def ConfigOK(self):
		""" Return True if the configuration is valid.
		"""
		return self._ConfigValid

	########################################################
	def GetServerName(self):
		""" Return the name of the server. (string)
		"""
		return self._Server

	########################################################
	def GetProtocolType(self):
		""" Return the protocol type. (string)
		"""
		return self._Protocol

	########################################################
	def GetHostInfo(self):
		""" Return the port number.
		"""
		return self._Port

	########################################################
	def IncConnectionCount(self):
		""" Increment the count of active connections.
		"""
		self._ConnectionCount += 1

	########################################################
	def DecConnectionCount(self):
		""" Decrement the count of active connections.
		"""
		self._ConnectionCount -= 1

	########################################################
	def SetConnectionCount(self, count):
		""" Set the count for the number of current active connections.
		"""
		self._ConnectionCount = count

	########################################################
	def GetConnectionCount(self):
		""" Return the current active connections count.
		"""
		return self._ConnectionCount


	########################################################
	def SetRequestCounter(self, reqbuffer):
		""" Set the list of data for calcuating the request rate 
		(requests per minute). This is used for protocols which do not
		maintain a connection (e.g. HTTP).
		Parameters: reqbuffer (list) = A list of time stamps for each
			of the most recent requests.
		"""
		self._RequestCounter = reqbuffer


	########################################################
	def GetStatusInfo(self):
		"""Return a dictionary containing the server status
		information.
		"""
		# If there is anything in the request counter list, this 
		# server does request rate calculations.
		if len(self._RequestCounter) > 0:

			currenttime = time.time()

			# Discard anything older than our time limit (in seconds).
			self._RequestCounter = filter(lambda x: (currenttime - x) < 300.0, self._RequestCounter)

			# Calculate the request rate in requests per minute.
			try:
				reqcount = (len(self._RequestCounter) * 60.0) / (currenttime - self._RequestCounter[0])
				# Set the request rate in the container.
				reqrate = int(reqcount)
			except:
				reqrate = 0

			return {'servername' : self._Server,
			'protocol' : self._Protocol,
			'port' : self._Port,
			'connectioncount' : self._ConnectionCount,
			'requestrate' : reqrate
			}

		# This server doesn't calculate request rate.
		else:
			return {'servername' : self._Server,
			'protocol' : self._Protocol,
			'port' : self._Port,
			'connectioncount' : self._ConnectionCount,
			'requestrate' : -1
			}


############################################################


	


############################################################
# Container object for client information
# for Ethernet TCP connections.


##############################################################################
class ModbusTCPClientConnection:
	"""
	This must be initialised with two parameters. The first is a dictionary 
	containing the validated configuration parameters for the connection 
	information. 
	This dictionary is expected to be in the form:
		ConfigDict = {'type': 'tcpclient', 'client': 'Module001', 
		'protocol': 'modbustcp', 'host': 'localhost', 'port': 8502, 
		'action': 'poll', 'cmdtime': 0.050, 'repeattime': 0.050, 
		'retrytime': 5.0, 'fault_coil': 10001, 'fault_inp': 10001, 
		'fault_holdingreg': 10001, 'fault_inpreg': 10001, 'fault_reset': 65280}

	The dictionary keys correspond directly to the parameters in the configuration file.

	The second parameter is a validated list containing the commands. 
	These are in dictionaries of the following form:
	[{'command': 'writeregs', 'function': 16, 'memaddr': 15016, 'remoteaddr': 5016, 'qty': 1, 'uid' : 1}]

	The dictionary keys correspond directly to the parameters in the configuration file.

	One of the public methods is:

	8) NextCommand() - This method is used to retrieve the next protocol command 
		in the command list. Calling it repeatedly increments the command 
		position. When the end of the command list is reached, it starts again 
		at the beginning. Returns a tuple containing the function code, remote 
		address, quantity, local data table address, (all integers) and a True 
		if the current command is the last command in the list.

	"""


	########################################################
	def __init__(self, connectdata, commandlist):
		""" Parameters: 
		connectdata = A dictionary containing the connection data. 
		commandlist = A list containing the communications commands.
		"""

		self._CurrentCmd = -1		# Index of current client command.



		# List of valid commands.
		self._CommandKeys = ['command', 'function', 'remoteaddr', 'qty', 'memaddr', 'uid']


		# Format the polling list. List of validated client commands.
		self._PollList = map(lambda cmd: (cmd['command'], cmd['function'], 
					cmd['remoteaddr'], cmd['qty'], cmd['memaddr'], cmd['uid']), commandlist)
		# Format the command list for display.
		self._StatusCommands = map(lambda cmd: {'command' : cmd['command'], 
					'function' : cmd['function'], 'remoteaddr' : cmd['remoteaddr'], 
					'qty' : cmd['qty'], 'memaddr' : cmd['memaddr'], 'uid' : cmd['uid']}, commandlist)


		# This is the configuration.
		self._Config = {'host' : connectdata['host'],
				'port' : connectdata['port'],
				'connectionname' : connectdata['client'], 
				'protocol' : connectdata['protocol'], 
				'action' : connectdata['action'], 
				'cmdtime' : connectdata['cmdtime'], 
				'repeattime' : connectdata['repeattime'], 
				'retrytime' : connectdata['retrytime'],
				'fault_inp' : connectdata['fault_inp'],
				'fault_coil' : connectdata['fault_coil'],
				'fault_inpreg' : connectdata['fault_inpreg'],
				'fault_holdingreg' : connectdata['fault_holdingreg'],
				'fault_reset' : connectdata['fault_reset'],
				'cmdlist' : self._StatusCommands
				}

		# Convert times from milli-seconds to seconds.
		self._commandtime = connectdata['cmdtime'] / 1000.0
		self._repeattime = connectdata['repeattime'] / 1000.0
		self._retrytime = connectdata['retrytime'] / 1000.0


		# Previous event.
		self._LastEvent = ''
		# Maximum error messages in buffer.
		self._MaxErrorMsg = 256

		# This is in the format {'command' : (errval, errcode, errstr)}
		# E.g. {'command1' : (5, 'CRCErr', 'CRC Error')}
		commandstatus = dict(map(lambda cmd: (cmd['command'], (0, 'noresult', 'No Result')), commandlist))
		# Previous alarm. We have to initialise it with the same keys as 
		# we use for tracing status.
		self._LastAlarm = dict(map(lambda cmd: (cmd['command'], ''), commandlist))

		# This is the current status.
		# 'connectionname' = Name of connection from configuration.
		# 'constatus' = The condition of the connection.
		# 'cmdstatus' = Result of each individual command.
		# 'cmdsummary' = A summary of all the commands.
		# 'coneventbuff' = constatus event buffer.
		# 'cmdeventbuff' = cmdstatus event buffer.
		# 'clientmsgs' = Client messages.
		# The command summary 'cmdsummary' must be explicitely updated 
		# before using or exporting the data.
		self._Status = {'connectionname' : connectdata['client'],
				'constatus' : 'notstarted',
				'cmdstatus' : commandstatus,
				'cmdsummary' : 'noresult',
				'coneventbuff' : [],
				'cmdeventbuff' : [],
				'clientmsgs' : []
				}



		# Status codes.
		self._StatCodes = {'ok' : (0, 'ok', 'No errors'),
				'badfunc' : (1, 'badfunc', 'Unsupported function'),
				'badaddr' : (2, 'badaddr', 'Invalid address'),
				'badqty' : (3, 'badqty', 'Invalid quantity'),
				'deviceerr' : (4, 'deviceerr', 'Device error'),
				'connection' : (255, 'connection', 'Client connection lost'),
				'timeout' : (254, 'timeout', 'Message time out'),
				'servererr' : (253, 'servererr', 'Undefined server error'),
				'badtid' : (252, 'badtid', 'TID Error'),
				'noresult' : (251, 'noresult', 'No result'),
				}

		# Map ModbusExceptions to fault codes.
		self._ExceptionMap = {1 : 'badfunc',
					2 : 'badaddr',
					3 : 'badqty',
					4 : 'deviceerr'
					}


	########################################################
	def NextCommand(self):
		""" Increment the command index and return the next client command.
		Returns a tuple containing the command name, function code, 
		remote address, quantity, local data table address, (all integers) 
		and a True if the current command is the last command in the list.
		"""
		# Increment the current poll list index.
		self._CurrentCmd += 1
		if (self._CurrentCmd >= len(self._PollList)):
			self._CurrentCmd = 0
			EndofList = True
		else:
			EndofList = False
		try:
			Cmd, FCode, Addr, Qty, MemAddr, UID = self._PollList[self._CurrentCmd]
			return Cmd, FCode, Addr, Qty, MemAddr, UID, EndofList
		except:
			return None, None, None, None, None, None, True


	########################################################
	def FaultCodeToInt(self, faultcode):
		"""Convert a fault code string to an integer suitable for 
		storage in the data table.
		"""
		try:
			return self._StatCodes[faultcode][0]
		except:
			return 255

	########################################################
	def ModbusExceptionToFaultCode(self, mexcept):
		"""Convert a Modbus exception code to a fault code string
		Returns 'servererr' if the number is not in range.
		"""
		return self._ExceptionMap.get(mexcept, 'servererr')


	########################################################
	def GetConnectionName(self):
		""" Return the name of the client. (string)
		"""
		return self._Config['connectionname']

	########################################################
	def GetProtocolType(self):
		""" Return the protocol type. (string)
		"""
		return self._Config['protocol']


	########################################################
	def GetHostInfo(self):
		""" Return a tuple containing the host name (string) and port number (integer).
		"""
		return self._Config['host'], self._Config['port']



	########################################################
	def GetCommandTime(self):
		""" Return the requested time delay (in *seconds*) between
		commands. (float)
		"""
		return self._commandtime

	########################################################
	def GetRepeatTime(self):
		""" Return the requested time delay (in *seconds*) between
		repetition of the complete set of commands. (float)
		"""
		return self._repeattime

	########################################################
	def GetRetryTime(self):
		""" Return the requested time delay (in *seconds*) for
		retrying a command if no reply is received. (float)
		"""
		return self._retrytime


	########################################################
	def GetCommandNames(self):
		""" Returns the ordered list of valid client command names.
		This is intended for status monitoring.
		"""
		return self._CommandKeys

	########################################################
	def GetCommandList(self):
		""" Returns the list of validated client command dictionaries.
		This is intended for status monitoring.
		"""
		return self._StatusCommands



	########################################################
	def GetConStatus(self):
		""" Returns the connection status of the client connection.
		"""
		return self._Status['constatus']


	########################################################
	def _SetConStatus(self, constatus):
		"""Set the status of the client connection.
		Parameters: constatus (string) = The connection status.
		"""
		self._Status['constatus'] = constatus
		if (constatus != self._LastEvent):
			self._Status['coneventbuff'].append((time.time(), constatus))
			self._LastEvent = constatus
			# Check to see if the buffer has reached its maximum length.
			if (len(self._Status['coneventbuff']) > self._MaxErrorMsg):
				self._Status['coneventbuff'].pop(0)



	########################################################
	def SetConStatusStarting(self):
		""" Sets the status of the client connection to 'starting'.
		"""
		self._SetConStatus('starting')


	########################################################
	def SetConStatusRunning(self):
		""" Sets the status of the client connection to 'running'.
		"""
		self._SetConStatus('running')


	########################################################
	def SetConStatusStopped(self):
		""" Sets the status of the client connection to 'stopped'.
		"""
		self._SetConStatus('stopped')


	########################################################
	def SetConStatusFaulted(self):
		""" Sets the status of the client connection to 'faulted'.
		"""
		self._SetConStatus('faulted')


	########################################################
	def _UpdateCmdStatSummary(self):
		"""Update the command status summary. We only update this when
		it will be exported. We do this to avoid doing any unecessary work.
		If commands are not 'ok', we take the first command which has
		an error.
		"""
		cmdsum = filter(lambda cmd: cmd[1] != 'ok', self._Status['cmdstatus'].values())
		if len(cmdsum) > 0:
			self._Status['cmdsummary'] = cmdsum[0][1]
		else:
			self._Status['cmdsummary'] = 'ok'


	########################################################
	def GetCmdStatus(self):
		"""Get the current status of the commands.
		"""
		# First update the command summary. 
		self._UpdateCmdStatSummary()
		return self._Status['cmdstatus']


	########################################################
	def SetCmdStatus(self, cmd, stat):
		""" Set the status of a command.
		Parameters: cmd (string) = The command name.
			stat (string) = The status code string.
		"""
		newstat = self._StatCodes.get(stat, self._StatCodes['servererr'])
		self._Status['cmdstatus'][cmd] = newstat

		if (stat != self._LastAlarm[cmd]):
			self._Status['cmdeventbuff'].append((time.time(), cmd, newstat[0], newstat[1], newstat[2]))
			self._LastAlarm[cmd] = stat
			# Check to see if the buffer has reached its maximum length.
			if (len(self._Status['cmdeventbuff']) > self._MaxErrorMsg):
				self._Status['cmdeventbuff'].pop(0)

	########################################################
	def SetCmdStatusOk(self, cmd):
		"""Set the comand status as indicating no errors.
		Parameters: cmd (string) = The command being monitored.
		"""
		self.SetCmdStatus(cmd, 'ok')


	########################################################
	def GetFaultAddresses(self):
		""" Return the data table addresses used for storing fault
		information. Invalid or unconfigured addresses will be
		returned as -1.
		"""
		return (self._Config['fault_inp'],
			self._Config['fault_coil'],
			self._Config['fault_inpreg'],
			self._Config['fault_holdingreg'],
			self._Config['fault_reset']
			)

	########################################################
	def GetConfigInfo(self):
		"""Return a dictionay containing the configuration data.
		"""
		return self._Config

	########################################################
	def GetStatusInfo(self):
		"""Return a dictionary containing the client status
		information.
		"""
		# First update the command summary. 
		self._UpdateCmdStatSummary()
		return self._Status



############################################################


