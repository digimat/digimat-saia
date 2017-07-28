##############################################################################
# Project: 	MBLogic
# Module: 	ConfigGeneric.py
# Purpose: 	Read configuration data for generic clients.
# Language:	Python 2.5
# Date:		24-May-2010.
# Version:	16-Mar-2011.
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
This validates the configuration for generic clients. 
"""

########################################################

import ConfigCommon

########################################################



########################################################
class GeneriClientConfig:

	########################################################
	def __init__(self):
	
		# Standard generic client items. Additional items are permitted 
		# but must be validated by the client itself. 
		self._GenericClientItems = ['type', 'protocol', 'action', 'clientfile', 'restartonfail',
			'fault_inp', 'fault_coil', 'fault_inpreg', 'fault_holdingreg', 'fault_reset',
			'readtable', 'writetable']


		# We use these to tell us how to validate the known parameters. 
		self._GenericClientValidator = {
				'type' : ConfigCommon.CheckAny, 
				'protocol' : ConfigCommon.CheckAny, 
				'action' : ConfigCommon.CheckAny,
				'clientfile' : ConfigCommon.CheckAny,
				'restartonfail' : ConfigCommon.CheckGenRestart,
				'fault_inp' : ConfigCommon.CheckDTDisInpAddr,
				'fault_coil' : ConfigCommon.CheckDTCoilAddr,
				'fault_inpreg' : ConfigCommon.CheckDTInpRegAddr,
				'fault_holdingreg' : ConfigCommon.CheckDTHRegAddr,
				'fault_reset' : ConfigCommon.CheckDTCoilAddr,
				'readtable' : ConfigCommon.CheckGenDTAddr,
				'writetable' : ConfigCommon.CheckGenDTAddr
				}



	########################################################
	def GetGenericClientItems(self, sectionname, parserdict):
		""" Get the list of config items for a generic client. 
		Parameters: sectionname (string): The name of the section.
			parserdict: A dictionary containing all the configuration items.
		Returns: The client configuration in a dictionary.
			{'config' : clientconfig, 'protocol' : protocol, 'cmdlist' : commandlist}
			Also returns a list of error messages.
		"""

		errorlist = []

		# Check that the section name is OK.
		if not ConfigCommon.ValidateSectionName(sectionname):
			errorlist.append(ConfigCommon.FormatErr('badclientname', sectionname, '', ''))
			return None, errorlist

		# Get the items which are Not commands. These do Not start with an '&'.
		paramitems = filter(lambda x:x[0][0] != '&', parserdict.items())
		# Get the parameters that we expect.
		stdgenitems = filter(lambda x: x[0] in self._GenericClientItems, paramitems)
		# Get the ones we don't know. We assume these will belong to the generic client.
		clientitems = filter(lambda x: x[0] not in self._GenericClientItems, paramitems)

		# Check to see if any of the mandatory configuration items are missing.
		# The generic client is responsible for dealing with any extra items.
		# This is the significant difference from a standard client. 
		stdkeys = map(lambda x : x[0], stdgenitems)
		missing = set(self._GenericClientItems) - set(stdkeys)
		if len(missing) > 0:
			errorlist.append(ConfigCommon.FormatErr('missingitem', sectionname, ', '.join(missing), ''))
			# Stop here and report errors.
			return None, errorlist

		# Extra items are not an error. We assume they belong to the generic 
		# client and it will deal with them.
		stdparams = dict(stdgenitems)

		# These we don't know about, so we'll give them to the client and let
		# it deal with them.
		clientparams = dict(clientitems)


		# We put the results in here as we check each one.
		checkedparams = {}
		# At this point we know that all the item names are valid.
		# Validate the known parameters for each one.
		for paramname, params in stdparams.items():
			rsltOK, rvalue = self._GenericClientValidator[paramname](params)
			if not rsltOK:
				errorlist.append(ConfigCommon.FormatErr('badvalue', sectionname, paramname, params))
			else:
				checkedparams[paramname] = rvalue

		# If we have any errors, stop here.
		if len(errorlist) > 0:
			return None, errorlist


		# Now, get the commands and check the command 'names' (item keys).
		# Commands are any item that starts with an '&'.
		# Also, strip new line characters from the command. This can get embedded in 
		# the command string if line continuations are used in the configuration.
		cmdlist = [(x.replace('\n', ''), y.replace('\n', '')) for x,y in parserdict.items() if x[0][0] == '&']

		# We just check to see that the names have at least one character
		# besides the '&'. We don't validate the actual commands themselves,
		# as those are protocol dependent.
		badcmds = filter(lambda x: len(x[0]) < 2, cmdlist)

		# Report if there were any bad command names.
		if len(badcmds) > 0:
			errorlist.append(ConfigCommon.FormatErr('badcmdname', sectionname, ', '.join(badcmds), ''))
			return None, errorlist

		# Add the generic items back into the checked parameters. 
		configdict = {}
		configdict.update(checkedparams)


		# Add the client name directly into the config
		configdict['client'] = sectionname


		# Return the client configuration and command list. The 
		# commmand list is not validated yet as this depends on the
		# actual protocol used. 
		# Protocol is returned separately for convenience.
		return {'protocol' : configdict['protocol'], 
			'hostconfig' : configdict, 
			'clientconfig' : clientparams,
			'cmdlist' : cmdlist}, errorlist

##############################################################################	

