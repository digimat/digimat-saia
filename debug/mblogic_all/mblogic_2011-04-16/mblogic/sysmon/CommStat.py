##############################################################################
# Project: 	MBLogic
# Module: 	CommStat.py
# Purpose: 	Reports and controls status of communications system.
# Language:	Python 2.6
# Date:		25-Apr-2008.
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
"""
This module is used to implement a container object to hold current status 
information. This information is meant to be used for status reporting
and monitoring.

"""
############################################################

import time
import os

from twisted.web import resource

from comsconfig import ComsConfig
import MonUtils
import MBFileServices

############################################################
class CommStat:
	"""Communications status and configuration.
	"""

	########################################################
	def __init__(self):
		# Most recent data about the hmi web pages.
		self._HMIPageData = {}
		# Last time the HMI web page data was updated.
		self._HMIPageUpdateTime = 0.0


	########################################################
	def GetServerID(self):
		"""Return the server ID string from the communications
		configuration.
		"""
		return ComsConfig.ConfigServer.GetServerIDName()


	########################################################
	def GetServerConfigStatParams(self):
		"""Return a dictionary containing the general server
		configuration parameters.
		"""
		return ComsConfig.ConfigServer.GetServerConfigStatParams()
		
	########################################################
	def GetClientConfigStatParams(self):
		"""Return a dictionary containing the general clients
		configuration parameters.
		"""
		return ComsConfig.ConfigClient.GetClientConfigStatParams()


	########################################################
	def GetCurrentServerReportData(self):
		"""Return a dictionary with the current configuration.
		This will be formatted for use in a web report
		"""
		# System (server id).
		serverid = ComsConfig.ConfigServer.GetServerIDName()

		# List of servers.
		serverlist = map(lambda server: server.GetStatusInfo(), 
				ComsConfig.ConfigServer.GetServerList())

		# Expanded data table register map.
		expregs = ComsConfig.ConfigServer.GetExpDTParams()

		return {'system' : {'serverid' : serverid},
			'serverdata' : serverlist, 
			'expregisters' : expregs}



	########################################################
	def SetServerConfig(self, newconfig):
		"""Save the new server configuration and return a list of
		any errors encountered.
		"""
		return ComsConfig.SaveConfigServer(newconfig)



	########################################################
	def GetTCPClientStatusData(self):
		"""Return a list with the current status.
		This will be formatted for use in a web report
		"""
		tcpclientlist = ComsConfig.ConfigClient.GetTCPClientList()
		return map(lambda client: client.GetStatusInfo(), tcpclientlist)




	########################################################
	def GetGenClientStatusData(self):
		"""Return a list with the current status.
		This will be formatted for use in a web report
		"""
		clientlist = ComsConfig.ConfigClient.GetGenClientList()
		return map(lambda client: client.GetStatusInfo(), clientlist)




	########################################################
	def GetCurrentClientConfigData(self):
		"""Return a dictionary with the current configurations for both
		the TCP and generic clients.
		This will be formatted for use in a web report
		"""
		tcpclientlist = ComsConfig.ConfigClient.GetTCPClientList()
		genclientlist = ComsConfig.ConfigClient.GetGenClientList()

		clientconfig = {}
		clientconfig['tcpclientinfo'] = [client.GetConfigInfo() for client in tcpclientlist]
		clientconfig['genclientinfo'] = [client.GetConfigInfo() for client in genclientlist]

		return clientconfig


	########################################################
	def SetClientConfig(self, newconfig):
		"""Save the new client configuration and return a list of
		any errors encountered.
		"""
		return ComsConfig.SaveConfigClient(newconfig)



	########################################################
	def GetExpDTParams(self):
		"""Return a dictionary with the expanded data table
		addressing parameters.
		"""
		return ComsConfig.ConfigServer.GetExpDTParams()


	########################################################
	def GetCurrentCommsMonitor(self):
		"""Return a dictionary with the current status of all the clients
		and servers. This is a brief summary.
		"""
		# Server status.
		serverlist = ComsConfig.ConfigServer.GetServerList()
		tcpserverstat = map(lambda server: server.GetStatusInfo(), serverlist)
		serverstatlist = map(lambda server: {'servername' : server['servername'], 
					'connectioncount': server['connectioncount'], 
					'requestrate' : server['requestrate']}, tcpserverstat)
		# Sort the server list.
		serverstatlist.sort(key=lambda x: x['servername'])


		# TCP client status
		tcpclientlist = ComsConfig.ConfigClient.GetTCPClientList()
		tcpclientstat = map(lambda client: client.GetStatusInfo(), tcpclientlist)
		clientstatlist = map(lambda client: {'connectionname' : client['connectionname'],
							'constatus' : client['constatus'],
							'cmdsummary' : client['cmdsummary']}, tcpclientstat)

		# Sort the tcp client list.
		clientstatlist.sort(key=lambda x: x['connectionname'])

		# Generic client status.
		genclientlist = ComsConfig.ConfigClient.GetGenClientList()
		genclientstat = map(lambda client: client.GetStatusInfo(), genclientlist)
		genclientstatlist = map(lambda client: {'connectionname' : client['connectionname'],
							'constatus' : client['constatus'],
							'cmdsummary' : client['cmdsummary']}, genclientstat)

		# Sort the generic client list.
		genclientstatlist.sort(key=lambda x: x['connectionname'])

		# Add the generic clients in to the TCP clients.
		clientstatlist.extend(genclientstatlist)

		return {'servers' : serverstatlist, 'clients' : clientstatlist}



	########################################################
	def GetCommsErrorLogs(self, connection):
		"""Return a dictionary with the errors logs and status of an 
		individual client.
		"""
		# Search through the list of clients.
		# TCP client status
		tcpclientlist = ComsConfig.ConfigClient.GetTCPClientList()
		clientstat = map(lambda client: client.GetStatusInfo(), tcpclientlist)
		# Generic client status.
		genclientlist = ComsConfig.ConfigClient.GetGenClientList()
		genclientstat = map(lambda client: client.GetStatusInfo(), genclientlist)
		# Combine the lists.
		clientstat.extend(genclientstat)
		# Now, find the requested connection.
		targetclient = filter(lambda client: client['connectionname'] == connection, clientstat)
		# Did we find it?
		if len(targetclient) != 1:
			return {}
		# Return the data for that client.
		return targetclient[0]
		
		

	########################################################
	def GetConfigErrors(self):
		"""Return a list of the configuration error messages.
		"""
		configerrors = []
		configerrors.extend(ComsConfig.ConfigServer.GetConfigErrors())
		configerrors.extend(ComsConfig.ConfigClient.GetConfigErrors())
		return configerrors


	########################################################
	def GetHMIPageList(self):
		"""Scan the HMI directory for web pages and return a list with
		the names of those pages plus their signature. This function 
		should not be called frequently as each call will cause a disk
		access to be performed.
		Returns: (dict) = A dictionary containing the HMI file information.
		"""
		# If the most recent access was less than a specified limit,
		# just return the previous data. This helps protect against
		# excessive requests.
		currenttime = time.time()
		if (currenttime - self._HMIPageUpdateTime) < 30.0:
			return self._HMIPageData

		self._HMIPageUpdateTime = currenttime


		hmipageinfo = []

		# Get the list of web page file names. 
		filenames = MBFileServices.ListHMIFiles('hmipages')
		filenames.sort()

		# Calculate the file signatures.
		for fname in filenames:
			fpath = os.path.join('hmipages', fname)
			filesig = MonUtils.CalcFileSig(fpath)
			hmipageinfo.append({'hmipage' : fname, 'signature' : filesig})

		# Get the HMI server information. We need this to find out
		# what port the HMI server is running on.
		hmiserver = [x for x in ComsConfig.ConfigServer.GetServerList() 
							if x.GetProtocolType() == 'mbhmi']

		# Did we find it?
		if len(hmiserver) == 1:
			port = hmiserver[0].GetHostInfo()
		else:
			port = None

		# We cache this information for future requests.
		self._HMIPageData = {'port' : port, 'hmipageinfo' : hmipageinfo}

		return self._HMIPageData



############################################################

# Communications status and configuration.
CommStatus = CommStat()



############################################################
class SimpleResponse(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.

	########################################################
	def __init__(self, sourcedata):
		"""Initialise with the function to call to fetch the data.
		"""
		self._source = sourcedata

	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Errors will return an HTTP error code.
		try:
			# Get the data and encode it.
			reportdata = MonUtils.JSONEncode(self._source())
		except:
			request.setResponseCode(404)
			reportdata = ''

		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################

# Status data for TCP clients.
CommTCPClientDataResponse = SimpleResponse(CommStatus.GetTCPClientStatusData)
# Status data for generic clients.
CommGenClientDataResponse = SimpleResponse(CommStatus.GetGenClientStatusData)
# Summary of status for all the servers and clients.
CommsMonitorResponse = SimpleResponse(CommStatus.GetCurrentCommsMonitor)
# The configuration data for all servers.
ServerCommsSummaryResponse = SimpleResponse(CommStatus.GetServerConfigStatParams)
# The configuration data for all clients.
ClientCommsSummaryResponse = SimpleResponse(CommStatus.GetClientConfigStatParams)
# The expended register map parameters.
CommsExpDTResponse = SimpleResponse(CommStatus.GetExpDTParams)
# Configuration errors.
CommsConfigErrorResponse = SimpleResponse(CommStatus.GetConfigErrors)
# Information about the HMI files in the HMI web page directory.
HMIFileInfoResponse = SimpleResponse(CommStatus.GetHMIPageList)

# This version reads the query string arguments and uses them when fetching the data.
############################################################
class CommsLogs(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Errors will return an HTTP error code.
		try:
			# Find the connection name.
			connection = request.args.get('connection', [''])[0]

			# Get the data and encode it.
			reportdata = MonUtils.JSONEncode(CommStatus.GetCommsErrorLogs(connection))
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################

# Create a response object.
CommsLogsResponse = CommsLogs()



# Get the communications server data.
############################################################
class CommServerData(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Errors will return an HTTP error code.
		try:
			reportdata = MonUtils.JSONEncode(CommStatus.GetCurrentServerReportData())
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata



	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		requests to write data.
		"""
		try:
			# Get the subroutine data.
			postdata = request.content.read()

			configdata = MonUtils.JSONDecode(postdata)
			rslt = CommStatus.SetServerConfig(configdata)

			reponseaction = 'ok'
		except:
			reponseaction = 'notok'
			rslt = {}


		# This is the response to the request.
		respmsg = MonUtils.JSONEncode({'mblogiccmdack' : reponseaction,
						'errors' : rslt})

		# Return the JSON response.
		return respmsg



############################################################

# Create a response object.
CommServerDataResponse = CommServerData()




# Get the communications client data.
############################################################
class CommClientData(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Errors will return an HTTP error code.
		try:
			reportdata = MonUtils.JSONEncode(CommStatus.GetCurrentClientConfigData())
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata



	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		requests to write data.
		"""
		try:
			# Get the subroutine data.
			postdata = request.content.read()
			configdata = MonUtils.JSONDecode(postdata)

			rslt = CommStatus.SetClientConfig(configdata)

			reponseaction = 'ok'
		except:
			reponseaction = 'notok'
			rslt = {}


		# This is the response to the request.
		respmsg = MonUtils.JSONEncode({'mblogiccmdack' : reponseaction,
						'errors' : rslt})

		# Return the JSON response.
		return respmsg



############################################################

# Create a response object.
CurrentClientConfigResponse = CommClientData()


##############################################################################

