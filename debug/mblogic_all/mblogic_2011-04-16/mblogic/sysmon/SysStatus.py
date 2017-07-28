##############################################################################
# Project: 	MBLogic
# Module: 	SysStatus.py
# Purpose: 	Handles reporting of overall system status.
# Language:	Python 2.5
# Date:		07-Jun-2010.
# Version:	14-Dec-2010.
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


############################################################

import time

from twisted.web import resource

from mbplc import PLCIOManage
import PLCRun, HMIData
from comsconfig import ComsConfig
import MonUtils

############################################################
class SysStatusContainer:
	"""Overall system status summary.
	"""

	########################################################
	def __init__(self):

		self._SysStat = {'servername' : 'default server name',
				'softname' : 'default software name',
				'softversion' : 'default version',
				'starttime' : 0.0,
				'uptime' : 0.0
				}

		self.ShutDownReq = None
		self.RestartReq = None


	########################################################
	def SetSoftwareInfo(self, softname, softversion):
		""" Set information to about the software system.
		softname (string) = Name of the application software.
		softversion (string) = Version name (number) for the software.
		"""
		self._SysStat['softname'] = softname
		self._SysStat['softversion'] = softversion

	########################################################
	def SetStartTime(self, starttime):
		"""Set the system start time.
		"""
		self._SysStat['starttime'] = starttime


	########################################################
	def SetShutDownReq(self, shutdownreq):
		"""Set the shutdown request handler.
		"""
		self.ShutDownReq = shutdownreq


	########################################################
	def SetRestartReq(self, restartreq):
		"""Set the restart request handler.
		"""
		self.RestartReq = restartreq


	########################################################
	def GetSysStatus(self):
		"""Return the overall system status data.
		"""
		# Make sure we update the server name.
		self._SysStat['servername'] = ComsConfig.ConfigServer.GetServerIDName()
		# Recalculate the uptime.
		self._SysStat['uptime'] = time.time() - self._SysStat['starttime']
		return self._SysStat


	########################################################
	def GetSysSummary(self):
		"""Get a summary of all the subsystems. This combines
		information from several sources.
		"""
		reportdata = {}

		# Check how many clients and servers are configured.
		servercount = len(ComsConfig.ConfigServer.GetServerList())
		# TCP clients.
		tcpclientlist = ComsConfig.ConfigClient.GetTCPClientList()
		tcpclientcount = len(tcpclientlist)
		# Generic clients
		genclientlist = ComsConfig.ConfigClient.GetGenClientList()
		genclientcount = len(genclientlist)


		# Go through the list of tcp clients and see if we can
		# find any run-time errors.
		tcpclientstatuslist = map(lambda client: client.GetStatusInfo(), tcpclientlist)
		tcpclientrunlist = filter(lambda client: client['constatus'] != 'running', tcpclientstatuslist)
		tcpclientmsglist = filter(lambda client: client['cmdsummary'] != 'ok', tcpclientstatuslist)

		# Do the same for generic clients.
		genclientstatuslist = map(lambda client: client.GetStatusInfo(), genclientlist)
		genclientrunlist = filter(lambda client: client['constatus'] != 'running', genclientstatuslist)
		genclientmsglist = filter(lambda client: client['cmdsummary'] != 'ok', genclientstatuslist)

		# The following attempts to check for errors in the 
		# communications systems. 

		# Check for server configuration errors.
		if len(ComsConfig.ConfigServer.GetConfigErrors()) > 0:
			serverstat = 'error'
		# If no servers are running, this may be an error.
		elif (servercount == 0):
			serverstat = 'alert'
		# No error that we know of.
		else:
			serverstat = 'ok'

		# If there are any client configuration errror, both TCP 
		# and generic clients are suspect. 
		if len(ComsConfig.ConfigClient.GetConfigErrors()) > 0:
			tcpclientstat = 'error'
		# If no clients are running, this may be an error.
		elif (tcpclientcount == 0):
			tcpclientstat = 'alert'
		# There is a run-time client error. 
		elif (len(tcpclientmsglist) != 0):
			tcpclientstat = 'alert'
		# One or more clients are not running.
		elif (len(tcpclientrunlist) != 0):
			tcpclientstat = 'alert'
		# No error that we know of.
		else:
			tcpclientstat = 'ok'


		# If there are any client configuration errror, both TCP 
		# and generic clients are suspect. 
		if len(ComsConfig.ConfigClient.GetConfigErrors()) > 0:
			genclientstat = 'error'
		# If no clients are running, this may be an error.
		elif (genclientcount == 0):
			genclientstat = 'alert'
		# There is a run-time client error. 
		elif (len(genclientmsglist) != 0):
			genclientstat = 'alert'
		# One or more clients are not running.
		elif (len(genclientrunlist) != 0):
			tcpclientstat = 'alert'
		# No error that we know of.
		else:
			genclientstat = 'ok'



		# Set the report status.
		reportdata['tcpservercount'] = servercount
		reportdata['tcpserverstat'] = serverstat
		reportdata['tcpclientcount'] = tcpclientcount
		reportdata['tcpclientstat'] = tcpclientstat
		reportdata['genclientcount'] = genclientcount
		reportdata['genclientstat'] = genclientstat

		configdata = PLCIOManage.PLCIO.GetCurrentIOStatParams()
		reportdata['plciostat'] = configdata['configstat']
		reportdata['plcrunmode'] = PLCRun.PLCSystem.GetPLCRunStatus()['plcrunmode']
		reportdata['hmistat'] = HMIData.Msg.GetCurrentStatParams()['configstat']

		return reportdata

############################################################

SysStatus = SysStatusContainer()



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


# Create a response object.
SysStatusDataResponse = SimpleResponse(SysStatus.GetSysStatus)

# Create a response object.
SysSummaryDataResponse = SimpleResponse(SysStatus.GetSysSummary)



# Accept system control commands.
############################################################
class SysControl(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# There isn't any actual data for this.
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

		# Get the JSON data from the message.
		try:
			reqmsg = request.content.read()
			postdata = MonUtils.JSONDecode(reqmsg)
			syscmd = postdata.get('mblogicsyscmd', '')
			reponseaction = 'ok'
		except:
			reponseaction = 'notok'
			syscmd = ''


		# Was it a shutdown request?
		if syscmd == 'shutdown':
			# Shut down the system.
			SysStatus.ShutDownReq()
		# Was it a restart request?
		elif syscmd == 'restart':
			# Restart the system.
			SysStatus.RestartReq()


		# This is the response to the request.
		respmsg = MonUtils.JSONEncode({'mblogiccmdack' : reponseaction})


		# Return the JSON response.
		return respmsg



############################################################

# Create a response object.
SysControlResponse = SysControl()




############################################################
class SimpleMSIEResponse(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.

	########################################################
	def __init__(self, sourcedata, dataname):
		"""Initialise with the function to call to fetch the data.
		"""
		self._source = sourcedata
		self._DataName = dataname

	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):


		# Errors will return an HTTP error code.
		try:
			# Get the data and encode it.
			reportdata = self._DataName + ' = ' + MonUtils.JSONEncode(self._source())
		except:
			request.setResponseCode(404)
			reportdata = ''

		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################


# These are special versions to use with MSIE.
# Create a response object.
SysStatusDataResponseMSIE = SimpleMSIEResponse(SysStatus.GetSysStatus, 'sysstatus')

# Create a response object.
SysSummaryDataResponseMSIE = SimpleMSIEResponse(SysStatus.GetSysSummary, 'syssummary')


