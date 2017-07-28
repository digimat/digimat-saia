##############################################################################
# Project: 	MBLogic
# Module: 	DataMonitor.py
# Purpose: 	Handles requests to read the soft logic data table.
# Language:	Python 2.5
# Date:		08-Jun-2010.
# Version:	10-Aug-2010.
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
"""
This handles reading the soft logic data table using AJAX requests.

"""
############################################################


from twisted.web import resource

import PLCRun
import MBDataTable
from mbprotocols import MBAddrTypes
import MonUtils

############################################################


############################################################
class DataTableHander:
	"""Handle fetching the data from the data table.
	"""

	########################################################
	def __init__(self):
	
		# Get the data table memory limits. These are *not* limited by
		# the Modbus spec.
		self._MaxDisInp = MBAddrTypes.MaxBasicAddrTypes['discrete']
		self._MaxCoils = MBAddrTypes.MaxBasicAddrTypes['coil']
		self._MaxInpReg = MBAddrTypes.MaxBasicAddrTypes['inputreg']
		self._MaxHReg = MBAddrTypes.MaxBasicAddrTypes['holdingreg']

	########################################################
	def ReadSLData(self, params):
		"""Read data table values from the soft logic data table.
		Parameters: params (string) = A comma separated string
			containing the list of addresses to be read.
		Returns (dict) = A dictionary containing the data
			values read.
		"""
		# Strip out white space and tabs.
		addrstr = params.replace(' ', '')
		addrstr = addrstr.replace('\t', '')
		# Convert to upper case.
		addrstr = addrstr.upper()
		# Split it into a list.
		addrlist = addrstr.split(',')
		# Get the data from the soft logic data table. 
		return PLCRun.PLCSystem.GetDataTableValues(addrlist)
		


	########################################################
	def ReadSysData(self, params):
		"""Read data table values from the system data table.
		Parameters: params (string) = A comma separated string
			containing the list of addresses to be read.
		Returns (dict) = A dictionary containing the data
			values read.
		"""
		# Strip out white space and tabs.
		addrstr = params.replace(' ', '')
		addrstr = addrstr.replace('\t', '')
		# Convert to lower case.
		addrstr = addrstr.lower()
		# Split it into a list.
		addrlist = addrstr.split(',')
		# Split the list elements into address tuples.
		addrlist = map(lambda x: x.split(':', 1), addrlist)


		result = []
		# Read each address.
		for addr in addrlist:
			try:
				addrval = int(addr[1])


				# Ignore addresses that are out of range.
				if addrval >= 0:

					if addr[0] == 'coil' and addrval <= self._MaxCoils:
						val = MBDataTable.MemMap.GetCoilsBool(addrval)
					elif addr[0] == 'inp' and addrval <= self._MaxDisInp:
						val = MBDataTable.MemMap.GetDiscreteInputsBool(addrval)
					elif addr[0] == 'hreg' and addrval <= self._MaxHReg:
						val = MBDataTable.MemMap.GetHoldingRegistersInt(addrval)
					elif addr[0] == 'inpreg' and addrval <= self._MaxInpReg:
						val = MBDataTable.MemMap.GetInputRegistersInt(addrval)
					# We don't recognise the type, so ignore it.
					else:
						continue

					# Pack it in a tuple as type, address, value
					result.append((addr[0], addrval, val))

			# Ignore any requests that are invalid
			except:
				pass


		# Return the result. 
		return result



############################################################

MonDataTable = DataTableHander()


############################################################
class SoftLogicData(resource.Resource):
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
			# Get the request arguments. Extract it from
			# the list. If there is no valid data, an empty
			# string will be used.
			addrlist = request.args.get('addr', [''])[0]

			# Get the data and encode it.
			reportdata = MonUtils.JSONEncode(MonDataTable.ReadSLData(addrlist))
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata



############################################################

# Create a response object.
SoftLogicDataResponse = SoftLogicData()


############################################################
class SysDataTable(resource.Resource):
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
			# Get the request arguments. Extract it from
			# the list. If there is no valid data, an empty
			# string will be used.
			addrlist = request.args.get('addr', [''])[0]

			# Get the data and encode it.
			reportdata = MonUtils.JSONEncode(MonDataTable.ReadSysData(addrlist))
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata



############################################################

# Create a response object.
SysDataTableResponse = SysDataTable()


