##############################################################################
# Project: 	MBLogic
# Module: 	PLCProgram.py
# Purpose: 	Stores and reports on the status of the soft logic system.
# Language:	Python 2.5
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

import StaticWeb
from mbplc import PLCComp
import MonUtils


############################################################

# Error messages
_ErrMsgss = {'noreq' : '<HTML><p>No action requested.</p></HTML>',
		'httperr' : '<HTML><p>HTTP Error.</p></HTML>'
}

############################################################
class PLCProgram:
	"""Soft logic control and programming.
	"""

	########################################################
	def __init__(self):
		pass


	########################################################
	def GetCurrentSource(self, subname):
		"""Return the original IL and ladder source for the requested 
		subroutine.
		Parameters: subname (string) = Name of the subroutine.
		Return: (object) = Object (dictionary) with subroutine source.
		"""
		currentprog = PLCComp.PLCLogic.ReportCurrentPLCProgram()

		subrsource = {}
		subrsource['subrname'] = subname

		# Get the source data.
		ladder = currentprog['ladder']
		# Get the subroutine data.
		try:
			subroutine = ladder[subname]
			subrsource['subrdata'] = subroutine['subrdata']
			subrsource['subrcomments'] = subroutine['subrcomments']
			subrsource['signature'] = subroutine['signature']
		except:
			subrsource['subrdata'] = []
			subrsource['subrcomments'] = ''
			subrsource['signature'] = ''

		subrsource['plccompileerr'] = currentprog['plccompileerr']
		subrsource['plccompilemsg'] = currentprog['plccompilemsg']
		return subrsource


	########################################################
	def GetNewSource(self, subname):
		"""Return the "new" IL and ladder source for the requested subroutine.
		This may contain errors due to editing errors.
		Parameters: subname (string) = Name of the subroutine.
		Return: (object) = Object (dictionary) with subroutine source.
		"""
		newprog = PLCComp.PLCLogic.ReportNewPLCProgram()
		compileresults = newprog.GetCompileResults()

		# Get the ladder source.
		ladder = newprog.GetLadder()

		subrsource = {}
		subrsource['subrname'] = subname

		# Get the subroutine data.
		try:
			subroutine = ladder[subname]
			subrsource['subrdata'] = subroutine['subrdata']
			subrsource['subrcomments'] = subroutine['subrcomments']
			subrsource['signature'] = subroutine['signature']
		except:
			subrsource['subrdata'] = []
			subrsource['subrcomments'] = ''
			subrsource['signature'] = ''

		subrsource['plccompileerr'] = compileresults['plccompileerr']
		subrsource['plccompilemsg'] = compileresults['plccompilemsg']
		return subrsource


	########################################################
	def GetCurrentSignature(self, subname):
		"""Return the "signature" (hash) for the requested subroutine.
		This allows checking if a subroutine in the current running 
		program has changed. 
		Parameters: subname (string) = Name of the subroutine.
		Return: (string) = Hash of the subroutine data, or an empty
			string if the subroutine was not found.
		"""
		currentprog = PLCComp.PLCLogic.ReportCurrentPLCProgram()

		ladder = currentprog['ladder']

		# Get the subroutine data.
		subroutine = ladder.get(subname, {})

		# Return the signature data.
		return {'signature' : subroutine.get('signature', '')}




	########################################################
	def GetSubrListReportData(self):
		"""Return a list of subroutine names.
		"""
		subdata = PLCComp.PLCLogic.ReportCurrentPLCProgram()['subroutines']
		subdata.sort()
		return subdata


############################################################

PLCProgStat = PLCProgram()



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
SubrListResponse = SimpleResponse(PLCProgStat.GetSubrListReportData)



# Get the current soft logic program source.
############################################################
class ProgCurrentSource(resource.Resource):
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
			# Find the subroutine name.
			args = request.args
			subrname = args.get('subrname', ('', ''))[0]

			reportdata = MonUtils.JSONEncode(PLCProgStat.GetCurrentSource(subrname))
		except:
			request.setResponseCode(404)
			reportdata = ''


		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################

# Create a response object.
ProgCurrentSourceResponse = ProgCurrentSource()



# Get the current soft logic program source signature (hash) for a subroutine.
############################################################
class ProgCurrentSig(resource.Resource):
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
			# Find the subroutine name.
			args = request.args
			subrname = args.get('subrname', ('', ''))[0]

			reportdata = MonUtils.JSONEncode(PLCProgStat.GetCurrentSignature(subrname))
		except:
			request.setResponseCode(404)
			reportdata = ''

		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################

# Create a response object.
ProgCurrentSigResponse = ProgCurrentSig()




# Get the new soft logic program source.
############################################################
class ProgNewSource(resource.Resource):
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
			# Find the subroutine name.
			args = request.args
			subrname = args.get('subrname', ('', ''))[0]

			reportdata = MonUtils.JSONEncode(PLCProgStat.GetNewSource(subrname))
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

			editdata = MonUtils.JSONDecode(postdata)
			rslt = PLCComp.PLCLogic.MergeSourceBlock(editdata)

			reponseaction = 'ok'
		except:
			reponseaction = 'notok'


		# This is the response to the request.
		respmsg = MonUtils.JSONEncode({'mblogiccmdack' : reponseaction})

		# Return the JSON response.
		return respmsg



############################################################

# Create a response object.
ProgNewSourceResponse = ProgNewSource()



# Add or delete subroutines.
############################################################
class ProgSubr(resource.Resource):
	"""Add or delete subroutines. 
	"""

	isLeaf = True	# This is a resource end point.


	########################################################
	def render_GET(self, request):
		"""Return the page for a GET. This will handle requests
		to read data.
		"""
		# Just send the file.
		return StaticWeb.SendStaticFile(request)



	########################################################
	def render_POST(self, request):
		""" Process a POST and return a response. This will handle
		requests to write data.
		"""

		# Errors will return an HTTP error code.
		try:
			# See what the request was.
			AddSubrButton = request.args.get('addsubr', None)
			DeleteSubrButton = request.args.get('deletesubr', None)
		except:
			request.setResponseCode(404)
			return _ErrMsgss['httperr']


		# If it was a request to add, then get the subroutine name.
		if AddSubrButton != None:
			# Read the name of the subroutine button.
			try:
				SubrName = request.args.get('subrname', [''])[0]
			except:
				SubrName = ''
			# If we have a name, add a subroutine.
			if SubrName != '':
				rslt = PLCComp.PLCLogic.AddNewSubr(SubrName)

			# Re-display the web page.
			return StaticWeb.SendStaticFile(request)

		# Was it a request to delete a subroutine?
		elif DeleteSubrButton != None:
			SubrNames = request.args.get('deletesub', [])
			# If we have a name, delete a subroutine. This may
			# be a list of several names.
			if SubrNames != []:
				rslt = PLCComp.PLCLogic.DeleteSubr(SubrNames)

			# Re-display the web page.
			return StaticWeb.SendStaticFile(request)

		else:
			# Nothing was requested.
			return _ErrMsgss['noreq']



############################################################

# Create a response object.
ProgSubrResponse = ProgSubr()



