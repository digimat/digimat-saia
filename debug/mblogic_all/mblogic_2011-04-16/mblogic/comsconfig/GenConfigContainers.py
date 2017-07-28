##############################################################################
# Project: 	MBLogic
# Module: 	GenConfigContainers.py
# Purpose: 	Validate and store configuration data for generic clients.
# Language:	Python 2.5
# Date:		27-May-2010.
# Version:	18-Oct-2010.
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

"""
Container object for client information for generic clients.
"""

import time

##############################################################################
class GenericClientConnection:
	"""Container class for geneeric clients.
	"""



	########################################################
	def __init__(self, connectdata):
		""" Parameters: 
		connectdata = A dictionary containing the connection data. 
		"""

		# Maximum error messages in buffer.
		self._MaxErrorMsg = 50
		# Previous event.
		self._LastEvent = ''


		# Configuration parameters.
		self._Config =  {'connectionname' : connectdata['hostconfig']['client'], 
				'protocol' : connectdata['protocol'],
				'action' : connectdata['hostconfig']['action'], 
				'clientfile' : connectdata['hostconfig']['clientfile'], 
				'restartonfail' : connectdata['hostconfig']['restartonfail'], 
				
				'fault_inp' : connectdata['hostconfig']['fault_inp'],
				'fault_coil' : connectdata['hostconfig']['fault_coil'],
				'fault_inpreg' : connectdata['hostconfig']['fault_inpreg'],
				'fault_holdingreg' : connectdata['hostconfig']['fault_holdingreg'],
				'fault_reset' : connectdata['hostconfig']['fault_reset'],
				'readtable' : connectdata['hostconfig']['readtable'],
				'writetable' : connectdata['hostconfig']['writetable'],

				'cmdlist' : connectdata['cmdlist'],
				'clientparams' : connectdata['clientconfig']
				}


		# This is in the format {'command' : (errval, errcode, errstr)}
		# E.g. {'command1' : (5, 'CRCErr', 'CRC Error')}
		commandstatus = dict(map(lambda cmd: (cmd[0], (0, 'noresult', 'No Result')), connectdata['cmdlist']))
		# Previous alarm. We have to initialise it with the same keys as 
		# we use for tracing status.
		self._LastAlarm = dict(map(lambda cmd: (cmd[0], ''), connectdata['cmdlist']))

		# This is the current status.
		# 'connectionname' = Name of connection from configuration.
		# 'constatus' = The condition of the connection.
		# 'cmdstatus' = Result of each individual command.
		# 'cmdsummary' = A summary of all the commands.
		# 'coneventbuff' = constatus event buffer.
		# 'cmdeventbuff' = cmdstatus event buffer.
		# 'clientmsgs' = Client messages.
		# The command summary 'cmdsummary' must be explicitly updated 
		# before using or exporting the data.
		self._Status = {'connectionname' : connectdata['hostconfig']['client'],
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

		# Connection status codes.
		self._ConnectionCodes = ('starting', 'running', 'stopped', 'faulted')


	########################################################
	def SetConStatus(self, constatus):
		"""Set the status of the client connection.
		Parameters: constatus (string) = The connection status.
		"""
		if constatus in self._ConnectionCodes:
			self._Status['constatus'] = constatus
			if (constatus != self._LastEvent):
				self._Status['coneventbuff'].append((time.time(), constatus))
				self._LastEvent = constatus
				# Check to see if the buffer has reached its maximum length.
				if (len(self._Status['coneventbuff']) > self._MaxErrorMsg):
					self._Status['coneventbuff'].pop(0)


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
	def AddCmdStatus(self, cmdbuff):
		"""Update the command status from a list of command status messages).
		"""
		for cmd in cmdbuff:
			cmdname = cmd[0]
			stat = cmd[2]
			self._Status['cmdstatus'][cmdname] = (cmd[1], cmd[2], cmd[3]) 

			if (stat != self._LastAlarm[cmdname]):
				self._Status['cmdeventbuff'].append((time.time(), cmdname, cmd[1], stat, cmd[3]))
				self._LastAlarm[cmdname] = stat
				# Check to see if the buffer has reached its maximum length.
				if (len(self._Status['cmdeventbuff']) > self._MaxErrorMsg):
					self._Status['cmdeventbuff'].pop(0)



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
	def SetClientMsgs(self, msg):
		"""Set a list of client messages to be displayed in a report.
		"""
		self._Status['clientmsgs'] = msg



	########################################################
	def GetConnectionName(self):
		""" Return the name of the client. (string)
		"""
		return self._Config['connectionname']


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


