##############################################################################
# Project: 	MBLogic
# Module: 	PLCRunStat.py
# Purpose: 	Reports and controls status of soft logic system.
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

import MonUtils
from mbplc import PLCComp, PLCIOManage
import PLCRun


############################################################
class PLCRunStat:
	"""Soft logic status and configuration.
	"""

	########################################################
	def __init__(self):
		self._SysCntrldata = None
		self._RunStateData = None
		self._CurrentPLCProgInfo = None



	########################################################
	def SetPLCSysCntrlData(self, syscntrldata):
		"""Set the reference to the soft logic system control
		data.
		"""
		self._SysCntrldata = syscntrldata

	########################################################
	def SetPLCRunState(self, runstate):
		"""Set the reference to the runstate function. This
		is executed to return the current state.
		"""
		self._RunStateData = runstate

	########################################################
	def SetCurrentPLCProgInfo(self, proginfo):
		"""Set the reference to the soft logic system program
		information for the currently running program.
		"""
		self._CurrentPLCProgInfo = proginfo


	########################################################
	def SetDataTableValueRead(self, datatableread):
		"""Set a reference to a function which can be used to read
		data table values.
		"""
		self._ReadDataTableValues = datatableread



	########################################################
	def GetSysControlReportData(self):
		"""Return a dictionary with the current soft logic system state.
		This will be formatted for use in a web report.
		"""
		# A function is executed to get the latest data.
		return self._SysCntrldata()


	########################################################
	def GetCurrentPLCIOInfo(self):
		"""Return a dictionary with the current soft logic program 
		information. This will be formatted for use in a web report.
		"""
		configdata = PLCIOManage.PLCIO.GetCurrentIOStatParams()
		reportdata = {}

		reportdata['starttime'] = configdata['starttime']
		reportdata['signature'] = configdata['signature']
		reportdata['configstat'] = configdata['configstat']

		return reportdata

	########################################################
	def GetNewPLCIOInfo(self):
		"""Return a dictionary with the new soft logic program 
		information. This will be formatted for use in a web report.
		"""
		configdata = PLCIOManage.PLCIO.GetNewIOStatParams()
		reportdata = {}

		reportdata['starttime'] = configdata['starttime']
		reportdata['signature'] = configdata['signature']
		reportdata['configstat'] = configdata['configstat']

		return reportdata

	########################################################
	def SetPLCIOConfig(self, newconfig):
		"""Set the new soft logic IO configuration. If the 
		configuration is OK, it is saved to a file and becomes the 
		current configuration.	If it is not OK, a list of errors is 
		returned.
		Parameters: newconfig (dict) = The new configuration to check.
		Returns: (list) = A list containing error messages.
		"""
		return PLCIOManage.PLCIO.ConfigEdit(newconfig)


	########################################################
	def GetCurrentPLCIOConfigData(self):
		"""Return a dictionary with the current parameters for the 
		running soft logic IO configuration.
		"""
		configdata = PLCIOManage.PLCIO.GetCurrentIOConfigReport()
		reportdata = {}

		reportdata['logicioconfig'] = configdata.GetConfigDict()
		reportdata['sysparams'] = configdata.GetSysParams()
		reportdata['memsaveparams'] = configdata.GetMemSaveParams()
		# Flatten the error lists.
		reportdata['configerrors'] =  configdata.GetConfigErrorsList()

		return reportdata


	########################################################
	def GetNewPLCIOConfigData(self):
		"""Return a dictionary with the current parameters for the 
		running soft logic IO configuration.
		"""
		configdata = PLCIOManage.PLCIO.GetNewIOConfigReport()
		reportdata = {}

		reportdata['logicioconfig'] = configdata.GetConfigDict()
		reportdata['sysparams'] = configdata.GetSysParams()
		reportdata['memsaveparams'] = configdata.GetMemSaveParams()
		# Flatten the error lists.
		reportdata['configerrors'] =  configdata.GetConfigErrorsList()

		return reportdata


	########################################################
	def GetCurrentPLCProgInfo(self):
		"""Return a dictionary with the current soft logic program 
		information. This will be formatted for use in a web report.
		"""
		configdata = PLCComp.PLCLogic.GetCurrentPLCStatParams()
		reportdata = {}

		reportdata['starttime'] = configdata['starttime']
		reportdata['signature'] = configdata['signature']
		reportdata['configstat'] = configdata['configstat']

		return reportdata


	########################################################
	def GetNewPLCProgInfo(self):
		"""Return a dictionary with the new soft logic program 
		information. This will be formatted for use in a web report.
		"""
		configdata = PLCComp.PLCLogic.GetNewPLCStatParams()
		reportdata = {}

		reportdata['starttime'] = configdata['starttime']
		reportdata['signature'] = configdata['signature']
		reportdata['configstat'] = configdata['configstat']

		return reportdata


	########################################################
	def GetCurrentPLCProgConfigData(self):
		"""Return a dictionary with the compiler errors for the 
		running soft logic program.
		"""
		configdata = PLCComp.PLCLogic.ReportCurrentPLCProgram()
		
		reportdata = {}

		reportdata['plccompileerr'] = configdata['plccompileerr']
		reportdata['plccompilemsg'] = configdata['plccompilemsg']

		return reportdata



	########################################################
	def GetNewPLCProgConfigData(self):
		"""Return a dictionary with the compiler errors for the 
		new soft logic program.
		"""
		configdata = PLCComp.PLCLogic.ReportNewPLCProgram()
		
		plcdata = configdata.GetCompileResults()
		reportdata = {}

		reportdata['plccompileerr'] = plcdata['plccompileerr']
		reportdata['plccompilemsg'] = plcdata['plccompilemsg']

		return reportdata



	########################################################
	def GetPLCRunData(self):
		"""Return a dictionary with the current status of the running
		soft logic system. This includes run mode, scan times, etc.
		"""
		reportdata = {}

		# This is the current run mode.
		reportdata['runmode'] = PLCRun.PLCSystem.GetPLCRunStatus()['plcrunmode']

		# Get the number of instructions.
		proginfo = PLCComp.PLCLogic.ReportCurrentPLCProgram()
		reportdata['plcinstrcount'] = proginfo['plcinstrcount']

		configdata = PLCRun.PLCSystem.GetSystemControlData()

		# These are the run-time scan counters, timers, etc.
		reportdata['scancount'] = configdata['scancount']
		reportdata['scantime'] = configdata['scantime']
		reportdata['minscan'] = configdata['minscan']
		reportdata['maxscan'] = configdata['maxscan']
		reportdata['plcexitcode'] = configdata['plcexitcode']
		reportdata['plcexitsubr'] = configdata['plcexitsubr']
		reportdata['plcexitrung'] = configdata['plcexitrung']


		return reportdata


	########################################################
	def GetInstrXrefReportData(self):
		"""Return a dictionary with the current instruction xref.
		This will be formatted for use in a web report.
		"""
		xrefdata = PLCComp.PLCLogic.ReportCurrentPLCProgram()

		return xrefdata['instrxref']

	########################################################
	def GetAddrXrefReportData(self):
		"""Return a dictionary with the current address xref.
		This will be formatted for use in a web report.
		"""
		xrefdata = PLCComp.PLCLogic.ReportCurrentPLCProgram()

		return xrefdata['addrxref']



############################################################

# Soft logic status and configuration.
PLCRunStatus = PLCRunStat()



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

		# Get the data and encode it.
		reportdata = MonUtils.JSONEncode(self._source())

		ctype = 'application/json'

		# Send the headers.
		request.setHeader('content-type', ctype)
		# Send the page.
		return reportdata



############################################################



# Current soft logic IO configuration summary.
IOSummaryResponse = SimpleResponse(PLCRunStatus.GetCurrentPLCIOInfo)

# New soft logic IO configuration parameters.
IONewDataResponse = SimpleResponse(PLCRunStatus.GetNewPLCIOConfigData)

# Current soft logic program summary.
PLCSummaryResponse = SimpleResponse(PLCRunStatus.GetCurrentPLCProgInfo)

# Current soft logic program error messages.
PLCCurrentDataResponse = SimpleResponse(PLCRunStatus.GetCurrentPLCProgConfigData)

# New soft logic program error messages.
PLCNewDataResponse = SimpleResponse(PLCRunStatus.GetNewPLCProgConfigData)

# Soft logic run-time counters and values.
PLCRunResponse = SimpleResponse(PLCRunStatus.GetPLCRunData)

# Soft logic instruction cross reference.
InstrXRefDataResponse = SimpleResponse(PLCRunStatus.GetInstrXrefReportData)

# Soft logic address cross reference.
AddrXRefDataResponse = SimpleResponse(PLCRunStatus.GetAddrXrefReportData)


# The current IO configuration parameters.
############################################################
class IOCurrentData(resource.Resource):
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
			reportdata = MonUtils.JSONEncode(PLCRunStatus.GetCurrentPLCIOConfigData())
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
			rslt = PLCRunStatus.SetPLCIOConfig(configdata)

			reponseaction = 'ok'
		except:
			reponseaction = 'notok'
			rslt = []


		# This is the response to the request.
		respmsg = MonUtils.JSONEncode({'mblogiccmdack' : reponseaction,
						'errors' : rslt})

		# Return the JSON response.
		return respmsg



############################################################

# Create a response object.
IOCurrentDataResponse = IOCurrentData()

##############################################################################

