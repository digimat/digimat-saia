##############################################################################
# Project: 	MBLogic
# Module: 	ConfigCommsServer.py
# Purpose: 	Read configuration data for communications servers.
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	29-Dec-2010.
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


import MBConfigContainers
import ConfigTCPServer, ConfigCommon

from mbprotocols import MBAddrTypes
from sysmon import MonUtils
import MBFileServices

##############################################################################

# This message is for fatal configuration file parsing errors which prevent
# the configuration from being read. If the file cannot be read, the web
# interface cannot be started to display the error.
_ParseErrMsg = """\nThe server communications configuration file %s is corrupt and cannot be
processed. The error was: %s.\n
"""


##############################################################################

class CommsConfig:

	########################################################
	def __init__(self, serverconfigname):
		"""Parameters: serverconfigname (string) - Name of servers configuration file.
		"""

		# Name of configuration file for servers.
		self._ServerConfigFileName = serverconfigname

		# Parser for servers configuration
		self._ServerConfigParser = ConfigParser.ConfigParser()

		# This is necessary to prevent ConfigParser from forcing
		# option names to lower case. 
		self._ServerConfigParser.optionxform = lambda x: x


		# Lists for server and client configurations.
		self._ServerList = []


		# List of recognised protocols for servers.
		self._ServerProtocols = ['modbustcp', 'mbrest', 'status', 'help', 
										'mbhmi', 'rhmi', 'erp', 'generic']

		# Configuration management parameters.
		self._ConfigStatParams = {'serverid' : 'default server id', 
					'starttime' : 0.0, 'serversignature' : 'NA', 
					'serverconfigstat' : None}


		# List of configuration errors.
		# Servers config errors
		self._ServerConfigErrors = []

		# Expanded register map offsets. This is used for protocols that
		# need expanded register map help.
		self._ExpDTParams = {'mbaddrexp' : False, 'mbuidoffset' : {}, 
			'mbaddroffset' : 0, 'mbaddrfactor' : 1}

		# Highest holding register address we can use.
		self._MaxReg = MBAddrTypes.MaxBasicAddrTypes['holdingreg'] - 65535

		# Header to use when writing out modified configurations.
		self._FileHeader = 'TCP Server'


	########################################################
	def ReportErrors(self):
		""" Print the list of errors.
		"""
		for err in self._ServerConfigErrors:
			print(err)


	########################################################
	def _ValidateExpRegParams(self, offset, factor):
		"""Validate the expanded register map parameters.
		Parameters: offset (integer) = The register map offset.
			factor (integer) = The register map multiplication factor.
		Returns (boonea) = True if the parameters are OK.
		"""

		# They must both be positive integers and less than the maximum address.
		return (offset >= 0) and (factor > 0) and (offset <= self._MaxReg) and (factor < self._MaxReg)



	########################################################
	def _CalcExpDTFactors(self, mbuidoffset):
		"""Calculate the data table expanded map offsets.
		Parameters: mbuidoffset (string) = The address offset parameter
			from the configuration file.
		Return (dict) = A dictionary containing the calculated address offsets.
			Returns an empty dict if an error occurred.
		"""
		# Split the offset from the factor.
		offset, factor = mbuidoffset.split(',', 2)
		offset = int(offset)
		factor = int(factor)

		# Validate the offset and factor.
		if not self._ValidateExpRegParams(offset, factor):
			return {}, offset, factor


		# Generate the address offsets.
		offlist = range(0, self._MaxReg + 1, factor)
		# Generate the list of UIDs.
		uidlist = range(offset, 256)

		# Convert it into a dictionary.
		uidoffsets = dict(zip(uidlist, offlist))

		return uidoffsets, offset, factor



	########################################################
	def _GetSysParams(self, parser):
		"""Get the parameters from the &system section. 
		Parameters: parser - config parser object.
		Returns: The server ID name, and dictionary with the parameters 
			for expanded maps.
		"""

		sysparams = {}
		# This is the name of the system section.
		sectionname = '&system'

		# Check to see if there are any unknown parameters (items). At this point we
		# just want a list of the actual parameter names.
		try:
			paramitems = parser.items(sectionname)
			paramlist = [x[0] for x in paramitems]
		except:
			self._ServerConfigErrors.append(ConfigCommon.FormatErr('badsystem', sectionname, '', ''))
			paramlist = []

		# Now see if there are any parameters we don't recognize. This is set
		# arithmetic, not subtraction.
		extra = list(set(paramlist) - set(['serverid', 'mbaddrexp', 'mbuidoffset']))
		
		# Any we don't recognize?
		if len(extra):
			self._ServerConfigErrors.append(ConfigCommon.FormatErr('unknownitem', sectionname, extra, ''))


		# Get the server ID.
		try:
			serverid = parser.get(sectionname, 'serverid')
		except:
			self._ServerConfigErrors.append(ConfigCommon.FormatErr('noserverid', '', '', ''))
			serverid = 'default server id'



		# Expanded register maps for holding registers are optional.
		try:
			sysparams['mbaddrexp'] = (parser.get('&system', 'mbaddrexp') == 'incremental')
		except:
			sysparams['mbaddrexp'] = False

		# This is the address expansion offset values.
		if sysparams['mbaddrexp']:
			try:
				mbuidoffset = parser.get('&system', 'mbuidoffset')
				sysparams['mbuidoffset'], sysparams['mbaddroffset'], sysparams['mbaddrfactor'] = \
										self._CalcExpDTFactors(mbuidoffset)
				if sysparams['mbuidoffset'] == {}:
					self._ServerConfigErrors.append(ConfigCommon.FormatErr('badexpdt', '', '', ''))
					sysparams['mbaddrexp'] = False
			except:
				sysparams['mbuidoffset'] = {}
				sysparams['mbaddroffset'] = 0
				sysparams['mbaddrfactor'] = 1
				self._ServerConfigErrors.append(ConfigCommon.FormatErr('badexpdt', '', '', ''))
				# If we don't have a valid parameter, we have to disable the expanded map.
				sysparams['mbaddrexp'] = False

		else:
			sysparams['mbuidoffset'] = {}


		return serverid, sysparams




	########################################################
	def _CheckConfig(self):
		""" Check a complete configuration and update the configuration results. 
		Returns: Nothing
		"""

		# Get the system parameters, including the server ID.
		serverid, self._ExpDTParams = self._GetSysParams(self._ServerConfigParser)
		self._ConfigStatParams['serverid'] = serverid

		# Read and validate servers configuration

		# Now we have to get the remaining sections. These will be user 
		# defined tag names, so we don't know in advance what these will be.
		# Get a list of sections. Each section represents one address tag.
		sectionlist = self._ServerConfigParser.sections()

		# Filter out the &system section.
		sectionlist = filter(lambda x: x != '&system', sectionlist)

		# Now, classify them according to the known types.
		tcpservers = []
		for item in sectionlist:
			try:
				configtype = self._ServerConfigParser.get(item, 'type').strip()
			except:
				configtype = ''

			# Type is a TCP server.
			if configtype == 'tcpserver':
				tcpservers.append(item)
			# We don't know what this is, or the type is missing.
			# Just add the error report to the list.
			else:
				self._ServerConfigErrors.append(ConfigCommon.FormatErr('badtype', item, configtype, ''))


		ServerList = []
		# Validate the servers
		for section in tcpservers:
			configitems = dict(self._ServerConfigParser.items(section))
			validator = ConfigTCPServer.TCPServerConfig()
			validconfig, errorlist = validator.GetTCPServerItems(section, configitems)
			if len(errorlist) == 0:
				 ServerList.append(validconfig)
			else:
				self._ServerConfigErrors.extend(errorlist)


		# Classify the servers according to whether we know the protocol or not.
		knownservers = filter(lambda x: x['protocol'] in self._ServerProtocols, ServerList)
		# These servers use an unknown protocol.
		unknownservers = filter(lambda x: x['protocol'] not in self._ServerProtocols, ServerList)
		# Create error messages.
		for err in unknownservers:
			self._ServerConfigErrors.append(ConfigCommon.FormatErr('badprotocol', err['server'], err['protocol'], ''))

		# Create the server config containers objects.
		self._ServerList = []
		for server in knownservers:
			# Create a container to hold the parameters.
			serverconfig = MBConfigContainers.TCPServerConnection(server)
			# Add the configuration to the list.
			self._ServerList.append(serverconfig)

		# Set the server configuration status.
		if (len(self._ServerConfigErrors) == 0):
			self._ConfigStatParams['serverconfigstat'] = 'ok'
		else:
			self._ConfigStatParams['serverconfigstat'] = 'error'
						


	########################################################
	def GetServerConfig(self):
		""" Read in the servers configuration file and store the 
		parameters in a set of configuration dictionaries.
		"""

		# List for server configuration.
		self._ServerList = []

		# Servers config errors
		self._ServerConfigErrors = []

		# Calculate the servers file signature.
		try:
			filesig = MonUtils.CalcFileSig(self._ServerConfigFileName)
		except:
			filesig = None

		if filesig != None:
			self._ConfigStatParams['serversignature'] = filesig

		# Read in the servers configuration file for parsing.
		try:
			filename = self._ServerConfigParser.read(self._ServerConfigFileName)

			# The parser should have returned the name of the requested file. 
			if (len(filename) > 0):
				if (filename[0] != self._ServerConfigFileName):
					self._ServerConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ServerConfigFileName, '', ''))
					return
			else:
				self._ServerConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ServerConfigFileName, '', ''))
				return
		except ConfigParser.ParsingError, parserr:
			print (_ParseErrMsg  % (self._ServerConfigFileName, parserr))
			return
		except:
			self._ServerConfigErrors.append(ConfigCommon.FormatErr('badfile', self._ServerConfigFileName, '', ''))
			return

		# Set the read time stamp.
		self._ConfigStatParams['starttime'] = time.time()


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()



	########################################################
	def SetServerConfig(self, newconfig):
		""" Validate a new server configuration dictionary and store 
		it in the configuration file. This assumes that all servers are
		of type 'tcpserver'.
		Parameters: newconfig (dict) = The new configuration dictionary.
		Returns: (list) = A list of errors. If there were no errors an
			empty list is returned.
		"""

		# Get the server ID.
		try:
			section = '&system'
			serverid = newconfig['system']['serverid']
			self._ServerConfigParser.add_section(section)

			# Server ID
			self._ServerConfigParser.set(section, 'serverid', serverid)

			# Expanded register map.
			if newconfig['expregisters']['mbaddrexp']:
				self._ServerConfigParser.set(section, 'mbaddrexp', 'incremental')

			# Register unit id offsets.
			mbuidoffset = newconfig['expregisters']['mbaddroffset']
			mbaddrexp = newconfig['expregisters']['mbaddrfactor']
			self._ServerConfigParser.set(section, 'mbuidoffset', '%s,%s' % (mbuidoffset, mbaddrexp))
		except:
			pass

		# Reformat the server list data from the web format to the disk format.
		# This converts the format from something like this:
		# {"protocol": "modbustcp", "servername": "Main1", 
		#	"connectioncount": 8, "port": 8502, "requestrate": -1}
		# to this:
		# ('Main1', (('type', 'tcpserver'), ('protocol', 'modbustcp'), ('port', '8502')))

		serverdata = newconfig['serverdata']
		serverlist = [(x['servername'], (('type', 'tcpserver'), 
			('protocol', x['protocol']), ('port', x['port']))) for x in serverdata]


		# Add the server data to the parser.
		for (servername, serverparams) in serverlist:
			self._ServerConfigParser.add_section(servername)
			for (item, value) in serverparams:
				self._ServerConfigParser.set(servername, item, str(value))


		# Check the configuration. The results are stored in the class variables.
		self._CheckConfig()


		# Were there any configuration errors?
		if self._ServerConfigErrors:
			return self._ServerConfigErrors

		# If everything was OK, then save the new configuration.
		fileresult = MBFileServices.SaveConfigFile(self._ServerConfigFileName, 
				self._ServerConfigParser, self._FileHeader)

		# Was the file save operation Ok? If not, then convert the 
		# error code into an error message.
		if fileresult != 'ok':
			self._ServerConfigErrors.append(MBFileServices.FormatErr(fileresult, 
							self._ServerConfigFileName))


		# Everything was OK if there were no errors.
		return self._ServerConfigErrors



	########################################################
	def GetConfig(self):
		""" Read in the configuration files and store the parameters in
		a set of configuration dictionaries.
		"""

		# Read servers configuration file
		self.GetServerConfig()



	########################################################
	def GetServerIDName(self):
		"""Return just the server ID name.
		"""
		return self._ConfigStatParams['serverid']


	########################################################
	def GetServerList(self):
		""" Return the list of server configuration container objects.
		"""
		return self._ServerList


	########################################################
	def GetExpDTParams(self):
		"""Return the data table expanded register map offsets (used by
		Modbus) and whether the offsets are enabled.
		Returns (dict) = A dictionay containing the UID offsets, and
		other related parameters (including whether UID offsets are enabled).
		"""
		return self._ExpDTParams



	########################################################
	def GetConfigErrors(self):
		""" Return a list of configuration error strings.
		"""
		return self._ServerConfigErrors


	########################################################
	def GetServerConfigStatParams(self):
		"""Get the configuration status parameters for all servers.
		These contain general information about the configuration 
		used for reporting and monitoring. Returns a dictionary.
		"""
		return {'starttime' : self._ConfigStatParams['starttime'],
			'signature' : self._ConfigStatParams['serversignature'],
			'configstat' : self._ConfigStatParams['serverconfigstat']}



##############################################################################


