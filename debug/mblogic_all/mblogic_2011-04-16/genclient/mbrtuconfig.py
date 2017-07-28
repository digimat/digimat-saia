#!/usr/bin/python

##############################################################################
# Project: 	MBLogic
# Module: 	mbrtuconfig.py
# Purpose: 	Configuration functions for ModbusRTU Generic Client.
# Language:	Python 2.6
# Date:		04-Aug-2010.
# Version:	26-Jan-2011.
# Author:	J. Pomares.
# Copyright:	2010 - 2011 - Juan Pomares       	<pomaresj@gmail.com>
# Based on code of Michael Griffin <m.os.griffin@gmail.com>
#
# This file is proposed to be optional part of MBLogic.
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
Used to read and validate commands for Modbus/RTU (serial protocol) generic client. 
This only handles the commands, and does not deal with the other connection parameters.

Functions:
	FormatError = Format and return an error message. 

Classes:
	MBRTUCommandConfig - Used to validate Modbus/RTU generic client command configurations.
	This only handles the commands, and does not deal with the other connection parameters.
		Functions:
			CheckMBRTUClientCmd = Validate the list of commands for a Modbus/RTU generic client.
			_CheckModbusRTUClientCommand = Validate a single Modbus RTU generic client command. 
"""


# Error message convertion dictionary.
ErrMsg = {
	# Generic error messages.
	'badcmdname' : 'Invalid command name (&x): %(command)s',
	'missingcmdparam' : 'Missing parameter: %(paramvalue)s, in command %(command)s.',
	'unknowncmdparam' : 'Unknown parameter: %(paramvalue)s, in command %(command)s.',
	'badaction' : 'Invalid action (poll,oneshot,disabled): %(paramvalue)s, in command %(command)s.',
	'disabled' : 'Command %(command)s inactive because parameter action: %(paramvalue)s.',
	# Modbus specific error messages.
	'baduid' : 'Missing or invalid modbus unit id (0,...,247), in command %(command)s.',
	'rangeuid' : 'Out of range modbus unit id (0,...,247): %(paramvalue)s, in command %(command)s.',
	'badfunccode' : 'Missing or not supported modbus function code (1,2,3,4,5,6,15,16), in command %(command)s.',
	'rangefunccode' : 'Not supported modbus function code (1,2,3,4,5,6,15,16): %(paramvalue)s, in command %(command)s.',
	'badremoteaddr' : 'Missing or invalid modbus remote address (0,...,65535), in command %(command)s.',
	'rangeremoteaddr' : 'Out of range modbus remote address (0,...,65535): %(paramvalue)s, in command %(command)s.',
	'badqty' : 'Missing or invalid modbus data quantity (1,...,n), in command %(command)s.',
	'rangeqty' : 'Out of range data quantity (according function code): %(paramvalue)s, in command %(command)s.',
	'tableqty' : 'Data quantity exceed readtable/writetable limits: %(paramvalue)s, in command %(command)s.',
	'missingdatatype' : 'Missing data type (coil,inp,holdingreg,inpreg), in command %(command)s.',
	'baddatatype' : 'Not supported data type (coil,inp,holdingreg,inpreg): %(paramvalue)s, in command %(command)s.',
	'mismatchwdtype' : 'Data type not present in writetable: %(paramvalue)s, in command %(command)s.',
	'mismatchrdtype' : 'Data type not present in readtable: %(paramvalue)s, in command %(command)s.',
	'baddataoffset' : 'Missing or invalid data offset (0,...,n), in command %(command)s.',
	'rangedataoffset' : 'Out of range data offset: %(paramvalue)s, in command %(command)s.'
	}


##############################################################################
def FormatError(errkey, command, paramvalue):
	"""
		Format and return an error message. 
		Parameters:
			errkey (string) = A key to the error message dictionary.
			command (string) = The command the error occurred in.
			paramvalue (string) = The parameter value which is in error.
		Returns:
			result (string) = The formatted error message.
	"""
	
	return (ErrMsg[errkey] % {'command' : command, 'paramvalue' : paramvalue})


##############################################################################
class MBRTUCommandConfig:
	"""
		Used to validate Modbus/RTU generic client command configurations.
		This only handles the commands, and does not deal with the other
		connection parameters.
	"""

	########################################################
	def __init__(self):

		# Maximum *theoretical* table address. This is not necessarily
		# the same as the local data table limits.
		self._MaxTableAddr = 65535
		# This gives the limits for checking Modbus functions. The keys are
		# the function codes, and the values are the maximum quantity
		# (for read or write, as applicable to the function).
		self._MBQtyLimits = {'0' : self._MaxTableAddr, '1' : 2000, '2' : 2000, \
			'3' : 125, '4' : 125, '5' : 1, '6' : 1, '15' : 1968, '16' : 123}
		# Make a list of function codes.
		self._MBFuncCodes = self._MBQtyLimits.keys()
		# List of valid poll actions.
		self._ValidActions = ['poll', 'oneshot', 'disabled']
		# List of valid data types.
		self._DataTypes = ['coil', 'inp', 'holdingreg', 'inpreg']
		# List of errors
		self._ErrorList = []


	########################################################
	def _CheckModbusRTUClientCommand(self, command, hostconfig):
		"""
			Validate a single Modbus RTU generic client command. 
			Params: 
				command (tuple) _ A single Modbus command. The expected format is:
				('&writecoils', 'action=poll, uid=1, function=15, remoteaddr=15, qty=10,
				datatype=coil, dataoffset=0')
				clientname (string) = The client name. This is used for error reporting.
				hostconfig (dictionary) = Global configuration parameters received from server.
			Return:
				cmddict (dictionary) - A dictionary containing the validated Modbus command.
				None if error. The dictionary is in the format:
				{'command' : cmdname, 'action' : cmdaction, 'uid' : cmduid, 
				'function' : cmdfunction, 'remoteaddr' : cmdremoteaddr, 'qty' : cmdqty,
				'datatype' : cmddatatype, 'dataoffset' : cmddataoffset,
				'faults' : cmdfaults, 'sent' : cmdsent, 'msgcache' : cmdmsgcache}
		"""

		# Temporary error list for this command
		errorlist = []

		# Copy the command name
		cmdname = command[0]
		# Split the command string into separate command groups.
		commandlist = command[1].split(',')
		# Split each of these groups into key/value pairs.
		commandlist = map(lambda x: x.split('='), commandlist)
		# Now check to see that each of these has exactly two parts.
		badcmds = filter(lambda x: len(x) != 2, commandlist)
		if len(badcmds) > 0:
			errorlist.append(FormatError('badcmdname', cmdname, ', '.join(badcmds)))
			return None
		# Trim the leading and trailing spaces off the parameter names.
		commandlist = map(lambda x: (x[0].strip(), x[1]), commandlist)
		# Convert this into a dictionary.
		cmddict = dict(commandlist)

		# Action (action) is optional. Is it present? If not, then
		# add it in with a default value = 'poll'.
		try:
			cmdaction = cmddict['action']
		except:
			cmddict['action'] = 'poll'

		# Check each parameter to make sure it is valid.
		# Is the action parameter valid?
		if (cmddict['action'] in self._ValidActions):
			cmdaction = cmddict['action']
		else:
			# Disable execution of this command.
			errorlist.append(FormatError('badaction', cmdname, cmddict['action']))
			cmdaction = 'disabled'

		# Is the Unit ID valid?
		try:
			cmduid = int(cmddict['uid'])
		except:
			cmduid = 0
			errorlist.append(FormatError('baduid', cmdname, ''))
		if (not((cmduid >= 0) and (cmduid <=247))):
			errorlist.append(FormatError('rangeuid', cmdname, str(cmduid)))
		# Is the function code valid?
		functiondefined = True
		try:
			cmdfunction = int(cmddict['function'])
		except:
			functiondefined = False
			cmdfunction = 0
			errorlist.append(FormatError('badfunccode', cmdname, ''))
		if (functiondefined and not(str(cmdfunction) in self._MBFuncCodes)):
			errorlist.append(FormatError('rangefunccode', cmdname, str(cmdfunction)))
		# Is the remote address valid?
		try:
			cmdremoteaddr = int(cmddict['remoteaddr'])
		except:
			cmdremoteaddr = 0
			errorlist.append(FormatError('badremoteaddr', cmdname, ''))
		if (cmdremoteaddr > self._MaxTableAddr) or (cmdremoteaddr < 0):
			errorlist.append(FormatError('rangeremoteaddr', cmdname, str(cmdremoteaddr)))
		# Is the data type valid?
		datatypedefined = True		
		try:
			cmddatatype = cmddict['datatype']
		except:
			datatypedefined = False
			maxaddress = self._MaxTableAddr
			errorlist.append(FormatError('missingdatatype', cmdname, ''))
		if datatypedefined:
			if (cmddict['datatype'] not in self._DataTypes):
				maxaddress = self._MaxTableAddr
				errorlist.append(FormatError('baddatatype', cmdname, cmddict['datatype']))
			else:
				cmddatatype = cmddict['datatype']
				# Validate if selected datatype is defined in writetable/readtable 
				if (cmdfunction in [1,2,3,4]):
					try:
						maxaddress = int(hostconfig['writetable'][cmddict['datatype']][1])
					except:
						errorlist.append(FormatError('mismatchwdtype', cmdname, cmddict['datatype']))
						maxaddress = self._MaxTableAddr
				elif (cmdfunction in [5,6,15,16]):
					try:
						maxaddress = int(hostconfig['readtable'][cmddict['datatype']][1])
					except:
						errorlist.append(FormatError('mismatchrdtype', cmdname, cmddict['datatype']))
						maxaddress = self._MaxTableAddr
				else:
					maxaddress = self._MaxTableAddr
		# Is the data index valid?
		try:
			cmddataoffset = int(cmddict['dataoffset'])
		except:
			cmddataoffset = 0
			errorlist.append(FormatError('baddataoffset', cmdname, ''))
		if (cmddataoffset >= self._MaxTableAddr) or (cmddataoffset >= maxaddress) \
			or (cmddataoffset < 0):
			errorlist.append(FormatError('rangedataoffset', cmdname, str(cmddataoffset)))
		# Is the quantity valid?
		qtydefined = True
		try:
			cmdqty = int(cmddict['qty'])
		except:
			qtydefined = False
			cmdqty = 1
			errorlist.append(FormatError('badqty', cmdname, ''))
		if (qtydefined and (str(cmdfunction) in self._MBFuncCodes)):
			if ((cmdqty > self._MBQtyLimits[str(cmdfunction)]) or (cmdqty < 1)):
				errorlist.append(FormatError('rangeqty', cmdname, str(cmdqty)))
			elif ((((cmdqty + cmddataoffset) > self._MaxTableAddr) or ((cmdqty + cmddataoffset) > maxaddress)) \
				and not((cmddataoffset >= self._MaxTableAddr) or (cmddataoffset >= maxaddress))):
				errorlist.append(FormatError('tableqty', cmdname, str(cmdqty)))

		# If errors were found, stop here and report errors.
		if len(errorlist) > 0:
			self._ErrorList.extend(errorlist)
			return None
		
		# Initialize remaining command parameters
		# Qty of consecutive faults.
		cmdfaults = 0
		# Indicate if this command was successfully sent at least once.
		cmdsent = False
		# Last valid and successfully message sent.
		cmdmsgcache = []

		# If command has no errors and action parameter is disabled, send a message,
		# but consider this an inactive, but valid command.
		if (cmdaction == 'disabled'):
			self._ErrorList.append(FormatError('disabled', cmdname, cmddict['action']))

		# All tests passed, so return the validated result and the error message list.
		return {'command' : cmdname, 'action' : cmdaction, 'uid' : cmduid, 'function' : cmdfunction, 
			'remoteaddr' : cmdremoteaddr, 'qty' : cmdqty, 'datatype' : cmddatatype, 'dataoffset' : cmddataoffset,
			'faults' : cmdfaults, 'sent' : cmdsent, 'msgcache' : cmdmsgcache}


	########################################################
	def CheckMBRTUClientCmd(self, cmdlist, hostconfig):
		"""
			Validate the list of commands for a Modbus/RTU generic client.
			Parameters:
				cmdlist (dictionary) = Commands configuration parameters received from server.
				hostconfig (dictionary) = Global configuration parameters received from server.
			Returns:
				validatedlist (dictionary) = Dictionary with validated commands configuration parameters
				self._ErrorList (list) =  An list containing error message strings. Empty list if no error.
		"""

		# Sort alphabetically cmdlist, based on command name, to match status web pages
		cmdlist.sort()
		# Validate the command list.
		results = map(lambda x: self._CheckModbusRTUClientCommand(x, hostconfig), cmdlist)
		# Filter out commands that has configuration errors.
		validatedlist = [x for x in results if x != None]
		return validatedlist, self._ErrorList
