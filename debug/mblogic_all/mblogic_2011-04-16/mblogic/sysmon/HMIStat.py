##############################################################################
# Project: 	MBLogic
# Module: 	HMIStat.py
# Purpose: 	Reports and controls status of HMI system.
# Language:	Python 2.6
# Date:		25-Apr-2008.
# Version:	29-Dec-2010.
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
This module is used to implement a container object to hold current status 
information. This information is meant to be used for status reporting
and monitoring.

"""
############################################################

from twisted.web import resource

import HMIData
import MonUtils


############################################################
class HMIStat:
	"""HMI configuration status.
	"""

	########################################################
	def __init__(self):
		pass



	########################################################
	def GetCurrentHMIReportData(self):
		"""Return a dictionary with the current configuration.
		This will be formatted for use in a web report
		"""
		hmiinfo = HMIData.Msg.GetCurrentHMIInfo()
		reportdata = {}
		reportdata['hmitagdata'] = hmiinfo.GetConfigDict()
		reportdata['alarmconfig'] = hmiinfo.GetAlarmConfig()
		reportdata['eventconfig'] = hmiinfo.GetEventConfig()
		reportdata['configerrors'] = hmiinfo.GetConfigErrors()
		reportdata['erplist'] = hmiinfo.GetERPConfig()
		reportdata['timestamp'] = hmiinfo.GetTimeStamp()
		return reportdata

	########################################################
	def GetNewHMIReportData(self):
		"""Return a dictionary with the new configuration.
		This will be formatted for use in a web report
		"""
		hmiinfo = HMIData.Msg.GetNewHMIInfo()
		reportdata = {}
		reportdata['hmitagdata'] = hmiinfo.GetConfigDict()
		reportdata['alarmconfig'] = hmiinfo.GetAlarmConfig()
		reportdata['eventconfig'] = hmiinfo.GetEventConfig()
		reportdata['configerrors'] = hmiinfo.GetConfigErrors()
		reportdata['erplist'] = hmiinfo.GetERPConfig()
		reportdata['timestamp'] = hmiinfo.GetTimeStamp()
		return reportdata


	########################################################
	def GetHMINewConfigErrors(self):
		"""Return the HMI new configuration errors list.
		"""
		return HMIData.Msg.GetNewHMIInfo().GetConfigErrors()


	########################################################
	def GetHMICurrentConfigErrors(self):
		"""Return the HMI current configuration errors list.
		"""
		return HMIData.Msg.GetCurrentHMIInfo().GetConfigErrors()


	########################################################
	def HMIConfigReload(self, configreload):
		"""Trigger an HMI configuration reload.
		"""
		HMIData.Msg.ReloadHMIConfig()


	########################################################
	def GetHMICurrentStatParams(self):
		"""Return the HMI configuration status parameters.
		Returns a dict.
		"""
		return HMIData.Msg.GetCurrentStatParams()


	########################################################
	def SetHMIConfig(self, newconfig):
		"""Set the new HMI configuration. If the configuration is OK,
		it is saved to a file and becomes the current HMI configuration.
		If it is not OK, a list of errors is returned.
		Parameters: newconfig (dict) = The new configuration to check.
		Returns: (list) = The list of error messages.
		"""
		return HMIData.Msg.ConfigEdit(newconfig)



############################################################

# HMI configuration and status.
HMIStatus = HMIStat()




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
HMISummaryResponse = SimpleResponse(HMIStatus.GetHMICurrentStatParams)

# The HMI configuration summary
HMINewDataResponse = SimpleResponse(HMIStatus.GetNewHMIReportData)


# The current HMI configuration parameters.
############################################################
class HMICurrentData(resource.Resource):
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
			reportdata = MonUtils.JSONEncode(HMIStatus.GetCurrentHMIReportData())
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
			rslt = HMIStatus.SetHMIConfig(configdata)

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
HMICurrentDataResponse = HMICurrentData()

##############################################################################

