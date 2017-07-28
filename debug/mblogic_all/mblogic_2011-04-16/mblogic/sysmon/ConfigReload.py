##############################################################################
# Project: 	MBLogic
# Module: 	ConfigReload.py
# Purpose: 	Handles requests to reload configurations.
# Language:	Python 2.5
# Date:		08-Jun-2010.
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
"""
This handles reloading configurations via the web interface.
"""

############################################################

from twisted.web import resource

import StaticWeb

import HMIData

from mbplc import PLCIOManage, PLCComp


############################################################
class StatusControlPage(resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
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

		# Find out what has been submitted.
		try:
			submitbutton = request.args['submit'][0]
		except:
			submitbutton = ''

		# Check if the request is to reload a file.
		if (submitbutton == 'Reload File'):

			# Get the data from the message.
			# HMI.
			try:
				reloadhmiconfig = request.args['reloadhmiconfig'][0]
			except:
				reloadhmiconfig = ''

			# Soft logic IO.
			try:
				reloadplcioconfig = request.args['reloadplcioconfig'][0]
			except:
				reloadplcioconfig = ''

			# Soft logic program.
			try:
				reloadplcprog = request.args['reloadplcprog'][0]
			except:
				reloadplcprog = ''


			# Now, take any actions requested.
			# Reload the HMI configuration.
			if (reloadhmiconfig != ''):
				HMIData.Msg.ReloadHMIConfig()

			# Reload the soft logic IO configuration.
			if (reloadplcioconfig != ''):
				PLCIOManage.PLCIO.LoadIOConfig()

			# Reload the soft logic program.
			if (reloadplcprog != ''):
				PLCComp.PLCLogic.LoadCompileAndRun()


			# Re-display the web page.
			return StaticWeb.SendStaticFile(request)

		else:
			# Nothing was requested.
			return """<HTML>
			<p>No action requested.</p>
			</HTML>"""



############################################################

# Create a response object.
StatusControlPageResponse = StatusControlPage()


