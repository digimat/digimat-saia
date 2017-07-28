##############################################################################
# Project: 	MBLogic
# Module: 	ConfigTCPServer.py
# Purpose: 	Read configuration data for TCP servers.
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	26-May-2010.
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

"""
This validates the configuration for TCP servers.
"""

import ConfigCommon

########################################################
class TCPServerConfig:

	########################################################
	def __init__(self):
		# List of recognised items for servers.
		self._TCPServerItems = ['type', 'protocol', 'port']


	########################################################
	def ValidateTCPServerParams(self, sectionname, parserdict):
		""" Get the list of config items in a TCP server connection. 
		Parameters: sectionname (string): The name of the section.
			parserdict: A dictionary containing all the configuration items.
		Returns: The server configuration in a dictionary, or None if error.
			{'type' : type, 'protocol' : protocol, 'port' : port}
			Also returns a list of error messages.
		"""


		configdict = {}
		errorlist = []

		# Check that the section name is OK.
		if not ConfigCommon.ValidateSectionName(sectionname):
			errorlist.append(ConfigCommon.FormatErr('badservername', sectionname, '', ''))
			return None, errorlist


		# Check to see if all the correct configuration items are present
		# and there are no extra items.
		parserkeys = parserdict.keys()
		if set(parserkeys) != set(self._TCPServerItems):
			# There is a difference. We need to find out what.
			# Is something missing?
			missing = set(self._TCPServerItems) - set(parserkeys)
			if len(missing) > 0:
				errorlist.append(ConfigCommon.FormatErr('missingitem', sectionname, ', '.join(missing), ''))
			# Is there something extra?
			extra = set(parserkeys) - set(self._TCPServerItems)
			if len(extra) > 0:
				errorlist.append(ConfigCommon.FormatErr('unknownitem', sectionname, ', '.join(extra), ''))

			# Stop here and report errors.
			return None, errorlist
				
		
		# Network port. Must be +ve integer.
		presult, port = ConfigCommon.CheckPort(parserdict['port'])
		if not presult:
			errorlist.append(ConfigCommon.FormatErr('badport', sectionname, '', port))
			return None, errorlist

		
		# Everything was OK, so we can use these parameters.
		configdict = parserdict.copy()
		# The port number was converted to integer.
		configdict['port'] = port

		# This is the validated result.
		return configdict, errorlist


	########################################################
	def GetTCPServerItems(self, sectionname, parserdict):
		""" Like ValidateTCPServerParams, but also adds the name of the 
		server to the configuration dictionary. 
		E.g. {'server' : 'ServerName', 'type' : type, 'protocol' : protocol, 'port' : port}
		"""
		# Validate the server parameters.
		configdict, errorlist = self.ValidateTCPServerParams(sectionname, parserdict)
		if configdict != None:
			# Add in the name of the section.
			configdict['server'] = sectionname
			
		return configdict, errorlist



##############################################################################	

