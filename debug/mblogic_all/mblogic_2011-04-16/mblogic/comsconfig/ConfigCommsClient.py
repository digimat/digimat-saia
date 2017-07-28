##############################################################################
# Project: 	MBLogic
# Module: 	ConfigCommsClient.py
# Purpose: 	Read configuration data for communications clients.
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	27-Dec-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# Modified by: Juan Pomares <pomaresj@gmail.com>
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


import ConfigParser
import time

import MBConfigContainers, GenConfigContainers
import ConfigTCPClient, ConfigGeneric, ConfigCommon

from sysmon import MonUtils
import MBFileServices

##############################################################################

# This message is for fatal configuration file parsing errors which prevent
# the configuration from being read. If the file cannot be read, the web
# interface cannot be started to display the error.
_ParseErrMsg = """\nThe client communications configuration file %s is corrupt and cannot be
processed. The error was: %s.\n
"""


##############################################################################

class CommsConfig:

	########################################################
	def __init__(self, clientconfigname):
		"""Parameters: clientconfigname (string) - Name of clients configuration file.
		"""

		# Name of configuration file for clients.
		self._ClientConfigFileName = clientconfigname

		# Parser for clients configuration
		self._ClientConfigParser = ConfigParser.ConfigParser()

		# This is necessary to prevent ConfigParser from forcing
		# option names to lower case. 
		self._ClientConfigParser.optionxform = lambda x: x

		# Lists for client configurations.
		self._TCPClientList = []
		self._GenClientList = []

		# Dictionary relating reset address to fault storage location.
		self._FaultResetTable = {}

		# List of recognised protocols for TCP clients.
		self._TCPClientProtocols = ['modbustcp']
		# List of recognised protocols for generic clients.
		self._GenClientProtocols = ['generic']

		# Configuration management parameters.
		self._ConfigStatParams = {'starttime' : 0.0,
					'clientsignature' : 'NA', 
					'clientconfigstat' : None}


		# List of configuration errors.
		# Clients config errors
		self._ClientConfigErrors = []

		# Header to use when writing out modified configurations.
		self._FileHeader = 'TCP and Generic Clients'


	########################################################
	def ReportErrors(self):
		""" Print the list of errors.
		"""
		for err in self._ClientConfigErrors:
			print(err)



	########################################################
	def _CheckConfig(self):
		""" Check a complete configuration and update the configuration results. 
		Returns: Nothing
		"""
		# Read and validate clients configuration

		# Now we have to get all the sections. These will be user 
		# defined tag names, so we don't know in advance what these will be.
		# Get a list of sections. Each section represents one address tag.
		sectionlist = self._ClientConfigParser.sections()


		# Now, classify them according to the known types.
		tcpclients = []
		genericlients = []
		for item in sectionlist:
			try:
				configtype = self._ClientConfigParser.get(item, 'type').strip()
			except:
				configtype = ''

			# Type is a TCP client.
			if configtype == 'tcpclient':
				tcpclients.append(item)
			# Type is a generic client.
			elif configtype == 'genericclient':
				genericlients.append(item)
			# We don't know what this is, or the type is missing.
			# Just add the error report to the list.
			else:
				self._ClientConfigErrors.append(ConfigCommon.FormatErr('badtype', item, configtype, ''))

		TCPClientList = []
		# Validate the TCP clients.
		for section in tcpclients:
			configitems = dict(self._ClientConfigParser.items(section))
			validator = ConfigTCPClient.TCPClientConfig()
			validconfig, errorlist = validator.GetTCPClientItems(section, configitems)
			if len(errorlist) == 0:
				 TCPClientList.append(validconfig)
			else:
				# Save the errors.
				self._ClientConfigErrors.extend(errorlist)

		# Classify the TCP clients according to whether we know the protocol.
		knowntcpclient = filter(lambda x: x['protocol'] in self._TCPClientProtocols, TCPClientList)
		# These TCP clients use an unkown protocol.
		unknowntcpclients = filter(lambda x: x['protocol'] not in self._TCPClientProtocols, TCPClientList)
		# Create error messages.
		for err in unknowntcpclients:
			self._ClientConfigErrors.append(ConfigCommon.FormatErr('badprotocol', err['client'], err['protocol'], ''))

		CmdsOK = []
		# Validate the client commands.
		for client in knowntcpclient:
			validator = ConfigTCPClient.ModbusClientConfig()
			# Extract the section name.
			clientname = client['config']['client']
			cmdlist = client['cmdlist']
			cmdresult, errorlist = validator.CheckMBTCPClientCmd(cmdlist, clientname)
			if len(errorlist) == 0:
				# Substitute in the reformatted command list.
				client['cmdlist'] = cmdresult
				CmdsOK.append(client)
			else:
				# Save the errors.
				self._ClientConfigErrors.extend(errorlist)

		# Now, create the client config container list.
		for client in CmdsOK:
			# Create a container to hold the parameters.
			clientconfig = MBConfigContainers.ModbusTCPClientConnection(client['config'], client['cmdlist'])
			# Add the configuration to the list.
			self._TCPClientList.append(clientconfig)

		# Generic clients. We don't check whether we know the protocol, 
		# because checking that is the responsibility of the generic client.
		GenClientList = []
		# Validate the generic clients.
		for section in genericlients:
			configitems = dict(self._ClientConfigParser.items(section))
			validator = ConfigGeneric.GeneriClientConfig()
			validconfig, errorlist = validator.GetGenericClientItems(section, configitems)
			if len(errorlist) == 0:
				 GenClientList.append(validconfig)
			else:
				# Save the errors.
				self._ClientConfigErrors.extend(errorlist)

		# Now, create the generic client config container list.
		self._GenClientList = map(lambda x: GenConfigContainers.GenericClientConnection(x), GenClientList)

		# Finally, create the fault reset address table from the
		# client information.
		for client in self._TCPClientList:
			(InpAddr, CoilAddr, InpRegAddr, HoldingRegAddr, ResetAddr) = \
				client.GetFaultAddresses()
			self._FaultResetTable[ResetAddr] = (InpAddr, CoilAddr, InpRegAddr, HoldingRegAddr)

		# Add generic client info to reset table.
		for client in self._GenClientList:
			(InpAddr, CoilAddr, InpRegAddr, HoldingRegAddr, ResetAddr) = \
				client.GetFaultAddresses()
			self._FaultResetTable[ResetAddr] = (InpAddr, CoilAddr, InpRegAddr, HoldingRegAddr)
						
		# Set the client configuration status.
		if (len(self._ClientConfigErrors) == 0):
			self._ConfigStatParams['clientconfigstat'] = 'ok'
		else:
			self._ConfigStatParams['clientconfigstat'] = 'error'




	########################################################
	def GetClientConfig(self):
		""" Read in the clients configuration file and store the 
		parameters in a set of configuration dictionaries.
		"""

		# Lists for client configurations.
		self._TCPClientList = []
		self._GenClientList = []

		# Clients config errors
		self._ClientConfigErrors = []

		# Calculate the clients file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ClientConfigFileName)
		except:
			filesig = None

		if filesig != None:
			self._ConfigStatParams['clientsignature'] = filesig

		# Read in the clients configuration file for parsing.
		try:
			filename = self._ClientConfigParser.read(self._ClientConfigFileName)

			# The parser should have returned the name of the requested file. 
			if (len(filename) > 0):
				if (filename[0] != self._ClientConfigFileName):
					self._ClientConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ClientConfigFileName, '', ''))
					return
			else:
				self._ClientConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ClientConfigFileName, '', ''))
				return
		except ConfigParser.ParsingError, parserr:
			print (_ParseErrMsg  % (self._ClientConfigFileName, parserr))
			return
		except:
			self._ClientConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ClientConfigFileName, '', ''))
			return

		# Set the read time stamp.
		self._ConfigStatParams['starttime'] = time.time()


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()



	########################################################
	def SetClientConfig(self, newconfig):
		""" Validate a new client configuration dictionary and store 
		it in the configuration file. 
		Parameters: newconfig (dict) = The new configuration dictionary.
		Returns: (list) = A list of errors. If there were no errors an
			empty list is returned.
		"""


		# Start with the TCP client info.
		tcpclientinfo = newconfig['tcpclientinfo']


		# Reformat the command lists to pull the command list into 
		# key/value pairs with the other items.
		for record in  tcpclientinfo:
			# Command list. Reformat this: 
			# {'function': 1, 'uid': 1, 'memaddr': 1010, 'qty': 10, 
			#		'command': 'readcoil', 'remoteaddr': 1}
			# into: 'function=1, uid=1, memaddr=1010, qty=10, remoteaddr=1'
			cmdlist = record['cmdlist']
			for cmd in cmdlist:
				command = '&%s' % cmd['command']
				record[command] = ', '.join(['%s=%s' % (x, y) 
						for x,y in cmd.items() if x!='command'])
			# Remove the command list from the record.
			del(record['cmdlist'])

			# Add in the client type. This is always 'tcpclient' for tcp clients.
			record['type'] = 'tcpclient'


		# Add the client data to the parser.
		for record in tcpclientinfo:
			connectionname = record['connectionname']
			# Remove the connection name.
			del(record['connectionname'])
			# Add the section heading.
			self._ClientConfigParser.add_section(connectionname)
			# Add the options.
			for (item, value) in record.items():
				self._ClientConfigParser.set(connectionname, item, str(value))
			

		# Repeat with the generic client info.
		genclientinfo = newconfig['genclientinfo']


		# Reformat the command lists and client parameters into pull 
		# into key/value pairs with the other items.
		for record in  genclientinfo:
			# Command lists.
			cmdlist = record['cmdlist']
			# Add the command list into the key/value pairs.
			record.update(dict(cmdlist))
			# Remove the command list from the record.
			del(record['cmdlist'])

			# Client parameters.
			clientparams = record['clientparams']
			record.update(dict(clientparams))
			# Remove the client params from the record.
			del(record['clientparams'])

			# Reformat the readtable and writetable parameters.
			# This changes this: 'writetable': {'coil': [11500, 20], 'inp': [11500, 125], 
			#	'inpreg': [11500, 100], 'holdingreg': [11500, 25]} 
			# to this: 'coil=11500:20, holdingreg=11500:25, inp=11500:125, inpreg=11500:100'
			record['readtable'] = ', '.join(['%s=%s:%s' % (x, y[0], y[1]) 
							for x,y in record['readtable'].items()])
			record['writetable'] = ', '.join(['%s=%s:%s' % (x, y[0], y[1]) 
							for x,y in record['writetable'].items()])

			# No data is a special case.
			if record['readtable'] == '':
				record['readtable'] = 'none'
			if record['writetable'] == '':
				record['writetable'] = 'none'

			# Add in the client type. This is always 'genericclient' for generic clients.
			record['type'] = 'genericclient'


		# Add the client data to the parser.
		for record in genclientinfo:
			connectionname = record['connectionname']
			# Remove the connection name.
			del(record['connectionname'])
			# Add the section heading.
			self._ClientConfigParser.add_section(connectionname)
			# Add the options.
			for (item, value) in record.items():
				self._ClientConfigParser.set(connectionname, item, str(value))


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()

		# Were there any configuration errors?
		if self._ClientConfigErrors:
			return self._ClientConfigErrors

		# If everything was OK, then save the new configuration.
		fileresult = MBFileServices.SaveConfigFile(self._ClientConfigFileName, 
				self._ClientConfigParser, self._FileHeader)

		# Was the file save operation Ok? If not, then convert the 
		# error code into an error message.
		if fileresult != 'ok':
			self._ClientConfigErrors.append(MBFileServices.FormatErr(fileresult, 
							self._ClientConfigFileName))


		# Everything was OK if there were no errors.
		return self._ClientConfigErrors


	########################################################
	def GetConfig(self):
		""" Read in the configuration files and store the parameters in
		a set of configuration dictionaries.
		"""

		# Read clients configuration file
		self.GetClientConfig()



	########################################################
	def GetTCPClientList(self):
		""" Return the list of TCP client configuration container objects.
		"""
		return self._TCPClientList

	########################################################
	def GetGenClientList(self):
		""" Return the list of generic client configuration container objects.
		"""
		return self._GenClientList


	########################################################
	def GetFaultResetTable(self):
		""" Return the fault reset table dictionary.
		"""
		return self._FaultResetTable


	########################################################
	def GetConfigErrors(self):
		""" Return a list of configuration error strings.
		"""
		return self._ClientConfigErrors



	########################################################
	def GetClientConfigStatParams(self):
		"""Get the configuration status parameters for all clients.
		These contain general information about the configuration 
		used for reporting and monitoring. Returns a dictionary.
		"""
		return {'starttime' : self._ConfigStatParams['starttime'],
			'signature' : self._ConfigStatParams['clientsignature'],
			'configstat' : self._ConfigStatParams['clientconfigstat']}




##############################################################################


