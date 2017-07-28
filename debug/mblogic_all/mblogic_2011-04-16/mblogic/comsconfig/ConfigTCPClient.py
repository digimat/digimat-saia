##############################################################################
# Project: 	MBLogic
# Module: 	ConfigTCPClient.py
# Purpose: 	Read configuration data for TCP clients.
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	16-Mar-2011.
# Author:	M. Griffin.
# Copyright:	2008 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
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
This validates the configuration for TCP clients. This handled internal 
clients only. Generic clients are handled separately.
"""
########################################################

import ConfigCommon
import itertools

from mbprotocols import MBAddrTypes

########################################################




########################################################
class TCPClientConfig:
	"""Parse and check the configuration for TCP clients. This does not check
	commands, as those are protocol specific.
	"""

	########################################################
	def __init__(self):
		
		# List of recognised items for TCP clients.
		self._TCPClientItems = ['type', 'protocol', 'host', 'port', 
			'action', 'cmdtime', 'repeattime', 'retrytime', 
			'fault_inp', 'fault_coil', 'fault_inpreg', 'fault_holdingreg', 
			'fault_reset']

		# We use these to tell us how to validate the parameters. 
		self._TCPClientValidator = {
				'type' : ConfigCommon.CheckAny, 
				'protocol' : ConfigCommon.CheckAny, 
				'host' : ConfigCommon.CheckHost,
				'port' : ConfigCommon.CheckPort,
				'action' : ConfigCommon.CheckAny,
				'cmdtime' : ConfigCommon.CheckTime,
				'repeattime' : ConfigCommon.CheckTime,
				'retrytime' : ConfigCommon.CheckTime,
				'fault_inp' : ConfigCommon.CheckDTDisInpAddr,
				'fault_coil' : ConfigCommon.CheckDTCoilAddr,
				'fault_inpreg' : ConfigCommon.CheckDTInpRegAddr,
				'fault_holdingreg' : ConfigCommon.CheckDTHRegAddr,
				'fault_reset' : ConfigCommon.CheckDTCoilAddr
				}


	########################################################
	def GetTCPClientItems(self, sectionname, parserdict):
		""" Get the list of config items in a TCP client connection. 
		Parameters: sectionname (string): The name of the section.
			parserdict: A dictionary containing all the configuration items.
		Returns: The client configuration in a dictionary.
			{'client' : sectionname, 'config' : clientconfig, 'protocol' : protocol, 
					'cmdlist' : commandlist}
			Also returns a list of error messages.
		"""

		errorlist = []

		# Check that the section name is OK.
		if not ConfigCommon.ValidateSectionName(sectionname):
			errorlist.append(ConfigCommon.FormatErr('badclientname', sectionname, '', ''))
			return None, errorlist

		# Get the items which are Not commands. These do Not start with an '&'.
		stdparams = dict(filter(lambda x:x[0][0] != '&', parserdict.items()))

		# Check to see if all the correct configuration items are present
		# and there are no extra items.
		stdkeys = stdparams.keys()
		if set(stdkeys) != set(self._TCPClientItems):
			# There is a difference. We need to find out what.
			# Is something missing?
			missing = set(self._TCPClientItems) - set(stdkeys) 
			if len(missing) > 0:
				errorlist.append(ConfigCommon.FormatErr('missingitem', 
							sectionname, ', '.join(missing), ''))
			# Is there something extra?
			extra = set(stdkeys) - set(self._TCPClientItems)
			if len(extra) > 0:
				errorlist.append(ConfigCommon.FormatErr('unknownitem', 
							sectionname, ', '.join(extra), ''))

			# Stop here and report errors.
			return None, errorlist


		# We put the results in here as we check each one.
		checkedparams = {}
		# At this point we know that all the item names are valid.
		# Validate the parameters for each one.
		for paramname, params in stdparams.items():
			rsltOK, rvalue = self._TCPClientValidator[paramname](params)
			if not rsltOK:
				errorlist.append(ConfigCommon.FormatErr('badvalue', 
								sectionname, paramname, params))
			else:
				checkedparams[paramname] = rvalue

		# If we have any errors, stop here.
		if len(errorlist) > 0:
			return None, errorlist


		# Now, get the commands and check the command 'names' (item keys).
		# Commands are any item that starts with an '&'.
		cmdlist = filter(lambda x:x[0][0] == '&', parserdict.items())
		# Sort by command name.
		cmdlist.sort(key=lambda x:x[0])

		# We just check to see that the names have at least one character
		# besides the '&'. We don't validate the actual commands themselves,
		# as those are protocol dependent.
		badcmds = filter(lambda x: len(x[0]) < 2, cmdlist)

		# Report if there were any bad command names.
		if len(badcmds) > 0:
			errorlist.append(ConfigCommon.FormatErr('badcmdname', 
						sectionname, ', '.join(badcmds), ''))
			return None, errorlist

		configdict = {}
		configdict.update(checkedparams)
		# Add the client name directly into the config
		configdict['client'] = sectionname


		# Return the client configuration and command list. The 
		# commmand list is not validated yet as this depends on the
		# actual protocol used. 
		# Protocol is returned separately for convenience. The section name
		# is also returned so we can keep track of it.
		return {'protocol' : configdict['protocol'], 
				'config' : configdict, 'cmdlist' : cmdlist}, errorlist

		
##############################################################################	





########################################################
class ModbusClientConfig:
	"""Used to validate Modbus/TCP client command configurations.
	This only handles the commands, and does not deal with the other
	connection parameters.
	"""


	########################################################
	def __init__(self):
	
		# This gives the limits for checking Modbus functions. The keys are
		# the function codes, and the values are the maximum quantity
		# (for read or write, as applicable to the function).
		self._MBQtyLimits = {1 : 2000,
					2 : 2000,
					3 : 125,
					4 : 125,
					5 : 1,
					6 : 1,
					15 : 1968,
					16 : 123
					}

		# Make a list of function codes. 
		self._MBFuncCodes = self._MBQtyLimits.keys()

		# Maximum *theoretical Modbus* address. This is not necessarily
		# the same as the local data table limits.
		self._MaxModbusAddr = 65535

		# Relate Modbus function codes to local *data table* limits. These are
		# not necessarily the same as the theoretical Modbus limits.
		self._MaxLocalFuncLimit = {1 : MBAddrTypes.MaxBasicAddrTypes['coil'],
					2 : MBAddrTypes.MaxBasicAddrTypes['discrete'],
					3 : MBAddrTypes.MaxBasicAddrTypes['holdingreg'],
					4 : MBAddrTypes.MaxBasicAddrTypes['inputreg'],
					5 : MBAddrTypes.MaxBasicAddrTypes['coil'],
					6 : MBAddrTypes.MaxBasicAddrTypes['holdingreg'],
					15 : MBAddrTypes.MaxBasicAddrTypes['coil'],
					16 : MBAddrTypes.MaxBasicAddrTypes['holdingreg']
					}


	########################################################
	def CheckMBTCPClientCmd(self, cmdlist, sectionname):
		""" Validate the list of commands for a Modbus/TCP client.
		"""

		# Validate the command list.
		results = map(lambda x: self._CheckModbusClientCommand(x, sectionname), cmdlist)

		# Filter out the good commands.
		validatedlist = [x[0] for x in results if x[0] != None]

		# Filter out the errors.
		errorlist = [x[1] for x in results if len(x[1]) > 0]
		# Flatten the error list.
		errorlist = list(itertools.chain(*errorlist))

		return validatedlist, errorlist




	########################################################
	def _CheckModbusClientCommand(self, command, sectionname):
		""" Validate a single modbus client command. 
		Params: command (tuple) - A single Modbus command. The expected format is:
			('&writecoils', 'function=15, remoteaddr=15, qty=1, memaddr=1015')
			funclist (list) - A list of recognised Modbus function codes as strings.
		
			sectionname (string) = The section name. This is used for error reporting.
		Return: (cmddict, error)
			cmddict (dict) - A dictionary containging the validated Modbus 
			command. None if error. The dictionary is in the format:
				{'command' : commandname, 'function' : cmdfunction, 
				'remoteaddr' : cmdremote, 'qty' : cmdqty, 'memaddr' : cmdmemaddr}
			error (list) -  An list contaiing error message strings. Empty list if no error.
		"""


		# We use this to accumulate formatted error messages.
		errorlist = []

		# Copy the command name without the '&'
		commandname = command[0][1:]

		# Strip new line characters from the command. This can get embedded in 
		# the command string if line continuations are used in the configuration.
		cmdstring = command[1].replace('\n', '')

		# Split the command string into separate command groups.
		commandlist = cmdstring.split(',')

		# Split each of these groups into key/value pairs.
		commandlist = map(lambda x: x.split('='), commandlist)

		# Now check to see that each of these has exactly two parts.
		badcmds = filter(lambda x: len(x) != 2, commandlist)
		if len(badcmds) > 0:
			errorlist.append(ConfigCommon.FormatErr('badcmdname', 
					sectionname, commandname, ', '.join(badcmds)))
			return None, errorlist

		# Trim the leading and trailing spaces off the parameter names.
		commandlist = map(lambda x: (x[0].strip(), x[1]), commandlist)

		# Convert this into a dictionary.
		cmddict = dict(commandlist)

		# Unit id (UID) is optional. Is it present? If not, then
		# add it in with a default UID.
		if cmddict.get('uid', None) == None:
			cmddict['uid'] = 1

		# Check to see that all the command parameters are present, and that 
		# nothing is present which doesn't belong there.
		cmdkeys = set(cmddict.keys())

		# This are the commands. 
		cmdset = set(['function', 'remoteaddr', 'qty', 'memaddr', 'uid'])

		# These comparisons are set operations, not arithmetic compares. 
		if len(cmdset - cmdkeys) > 0:
			# There is a difference. We need to find out what.
			# Is something missing?
			missing = (cmdset >= cmdkeys)
			if len(missing) > 0:
				errorlist.append(ConfigCommon.FormatErr('missingcmdparam', 
						sectionname, commandname, ', '.join(missing)))
			# Is there something extra?
			extra = (cmdset <= cmdkeys)
			if len(extra) > 0:
				errorlist.append(ConfigCommon.FormatErr('uknowncmdparam', 
						sectionname, commandname, ', '.join(extra)))

			# Stop here and report errors.
			return None, errorlist

		# Now, try converting each command parameter into an integer. 
		# We'll do this in a conventional loop so we can report which
		# one had a problem.
		intdict = {}
		for cmd, value in cmddict.items():
			try:
				intdict[cmd] = int(value)
			except:
				errorlist.append(ConfigCommon.FormatErr('badcmdparamval', 
						sectionname, commandname, '%s = %s' % (cmd, value)))

		# Stop here and report errors.
		if len(errorlist) > 0:
			return None, errorlist

		cmddict = intdict

		# Check each parameter to make sure it is valid.

		# Is the function code valid?
		if (cmddict['function'] not in self._MBFuncCodes):
			errorlist.append(ConfigCommon.FormatErr('badfunccode', 
					sectionname, commandname, cmddict['function']))
			# Stop here and report errors. We can't complete the next
			# tests without a valid function code.
			return None, errorlist

		# Is the quantity valid? The function code must be valid to check this.
		if (cmddict['qty'] > self._MBQtyLimits[cmddict['function']]) or (cmddict['qty'] < 1):
			errorlist.append(ConfigCommon.FormatErr('badqty', 
					sectionname, commandname, cmddict['qty']))

		# Is the local data table address valid?
		if ((cmddict['qty'] + cmddict['memaddr']) > self._MaxLocalFuncLimit[cmddict['function']]) or (cmddict['memaddr'] < 0):
			errorlist.append(ConfigCommon.FormatErr('badmemaddr', 
					sectionname, commandname, cmddict['memaddr']))

		# Is the remote address valid?
		if ((cmddict['qty'] + cmddict['remoteaddr']) > self._MaxModbusAddr) or (cmddict['remoteaddr'] < 0):
			errorlist.append(ConfigCommon.FormatErr('badremoteaddr', 
					sectionname, commandname, cmddict['remoteaddr']))

		# Is the UID valid?
		if (cmddict['uid'] > 255) or (cmddict['uid'] < 0):
			errorlist.append(ConfigCommon.FormatErr('baduid', 
					sectionname, commandname, cmddict['uid']))

		# Stop here and report errors.
		if len(errorlist) > 0:
			return None, errorlist


		# All tests passed, so return the validated result and the error message list.
		return {'command' : commandname, 'function' : cmddict['function'], 
			'remoteaddr' : cmddict['remoteaddr'], 'qty' : cmddict['qty'], 
			'memaddr' : cmddict['memaddr'], 'uid' : cmddict['uid']}, errorlist


##############################################################################

