##############################################################################
# Project: 	MBLogic
# Module: 	FileAssembler.py
# Purpose: 	Assemble the final web page.
# Language:	Python 2.6
# Date:		28-Jan-2011.
# Version:	28-Jan-2011.
# Author:	M. Griffin.
# Copyright:	2011 - Michael Griffin       <m.os.griffin@gmail.com>
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


import xml.dom.minidom
import json

import ErrorMsgs

##############################################################################
# Error handling exception classes.
class FileAssembleError(Exception):
	"""Error assembling output file.
	"""
	def __init__(self, errmsg):
		self.errmsg = errmsg


##############################################################################
class WebPageTemplate:
	"""Read in the web page template file data and assemble the finished web page.
	"""

	########################################################
	def __init__(self, templatefilename, outputfilename):
		"""Parameters: templatefilename (string) = The name of the template file.
			outputfilename (string) = The name of the output file.
		"""
		# The file name.
		self._WebTemplateFileName = templatefilename
		# The output file name.
		self._OutputFileName = outputfilename

		# Open the file.
		try:
			self._Template = xml.dom.minidom.parse(self._WebTemplateFileName)
		except:
			errfile = {'filename' : self._WebTemplateFileName}
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtemplateopen', errfile))


		# Get all the divs.
		self._DivList = self._Template.getElementsByTagName('div')

		# Find the one with the ID we are looking for.
		try:
			self._SVGTarget = [x for x in self._DivList if x.getAttribute('id') == 'MBT_SVGScreen']
			self._SVGTarget = self._SVGTarget[0]
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtmplscreentarget', {}))


		# Find the script sections.
		self._ScriptList = self._Template.getElementsByTagName('script')

		# Find the one for the control lists.
		try:
			self._ControlListTarget = [x for x in self._ScriptList if x.getAttribute('id') == 'MBT_ControlLists']
			self._ControlListTarget = self._ControlListTarget[0]
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtemplcntrllisttarget', {}))

		# Find the one for the control scripts.
		try:
			self._ControlScriptsTarget = [x for x in self._ScriptList if x.getAttribute('id') == 'MBT_ControlScripts']
			self._ControlScriptsTarget = self._ControlScriptsTarget[0]
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtemplcntrlscripttarget', {}))



	########################################################
	def SetSVG(self, svgdata):
		"""Insert the SVG data.
		"""
		self._SVGTarget.appendChild(svgdata)


	########################################################
	def SetControlLists(self, readlist, alarmzonelist, eventzonelist, svgscreentable):
		"""Insert the control list data.
		"""
		# The data must be converted to JSON to make sure it is compatible.
		try:
			listdata = {'readlist' : json.dumps(readlist),
						'alarmzonelist' : json.dumps(alarmzonelist),
						'eventzonelist' : json.dumps(eventzonelist),
						'svgscreentable' : json.dumps(svgscreentable)}

			# Substitute in the new data.
			for x in self._ControlListTarget.childNodes:
				x.data = x.data % listdata
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtemplcntrllistinsert', {}))



	########################################################
	def SetControlScripts(self, scriptdata):
		"""Insert the control script data.
		"""
		# The data must be converted to JSON to make sure it is compatible.
		try:
			listdata = {'controlscripts' : scriptdata}

			# Substitute in the new data.
			for x in self._ControlScriptsTarget.childNodes:
				x.data = x.data % listdata
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badtemplcntrlscriptinsert', {}))



	########################################################
	def WriteWebPage(self):
		"""Combine the web page template with the current SVG data and write
		out the finished web page.
		"""
		errfile = {'filename' : self._OutputFileName}

		# Open the web page output file.
		try:
			fwebpage = open(self._OutputFileName, 'w')
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badoutputfilesave', errfile))


		# Write out the finished web page.
		try:
			fwebpage.write(self._Template.toxml())
		except:
			raise FileAssembleError(ErrorMsgs.Msg.GetMessage('badoutputfilewrite', errfile))
		finally:
			fwebpage.close()



##############################################################################


