##############################################################################
# Project: 	MBLogic
# Module: 	ErrorMsgs.py
# Purpose: 	Handle error messages.
# Language:	Python 2.6
# Date:		06-Feb-2011.
# Version:	07-Mar-2011.
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


############################################################

class MessageHandler:
	"""This handles message texts.	Messages are centralised here where possible.
	"""



	########################################################
	def GetMessage(self, msgcode, params):
		"""Return a status or error message. 
		Parameters: msgcode (string) = The message code (key).
			params (dict) = Any parameters as a dictionary. The keys will 
				depend on the particular message. 
				Example: {'section' : 'example', 'paramvalue' : 'sample'}
		"""
		# Get the message string.
		try:
			message = self._messages[msgcode]
		except:
			return self._messagefaults['nomessage'] % {'msg' : msgcode}

		# Substitute in the parameters and print the message.
		try:
			return message % params
		except:
			return self._messagefaults['paramerror'] % {'msg' : msgcode, 'paramvalue' : str(params)}


	########################################################
	def __init__(self, messages):
		# The messages. 		
		self._messages = messages


############################################################

Msg = MessageHandler(
	{
	# HMI Config file errors.
	'badhmiconfigread' : 'Error - could not read HMI configuration file %(filename)s.',
	'badhmiconfigparse' : 'Error - could not parse HMI configuration file %(filename)s.',
	'badhmiconfigload' : 'Error - could not load HMI configuration file  %(filename)s.',
	'badhmiconfigevents' : 'Error processing HMI config events.',
	'badhmiconfigalarms' : 'Error processing HMI config alarms.',

	# SVG drawing errors.
	'badsvgfileread' : 'Error - could not read or parse SVG drawing file %(filename)s.',
	'badsvgwidgetid' : 'Error - could not read SVG widget ID.',
	'badsvgbasicdata' : 'Error - bad SVG widget basic data for ID %(id)s.',
	'badsvgmenudata' : 'Error - bad SVG widget menu data for ID %(id)s.',
	'badsvglayerconfig' : 'Error - corrupted or missing SVG layer attribute.',
	'badsvgdrawingparamdata' : 'Error - corrupted or invalid SVG drawing parameter data.',

	# Edit widgets errors.
	'badsvgeditcount' : 'Error - bad SVG widget edit count data for ID %(id)s.',

	# Save SVG.
	'badsavewidgetdata' : 'Error - bad SVG widget data for ID %(id)s.',
	'badsavelayerzone' : 'Error - corrupted or missing SVG layer or zone list data.',
	'badsvgfilesave' : 'Error - could not open SVG drawing file for writing %(filename)s.',
	'badsvgfilewrite' : 'Error - could not write to SVG drawing file %(filename)s.',

	# Assemble output file.
	'badtemplateopen' : 'Error - could not read HTML template file %(filename)s.',
	'badtmplscreentarget' : 'Error - could not find id MBT_SVGScreen in web template file.',
	'badtemplcntrllisttarget' : 'Error - could not find id MBT_ControlLists in web template file.',
	'badtemplcntrlscripttarget' : 'Error - could not find id MBT_ControlScripts in web template file.',

	'badreadlist' : 'Error - could not generate read list.',
	'badinputhandler' : 'Error - could not generate input handlers for ID %(id)s.',
	'badinputhandlerunkn' : 'Error - could not generate input handlers.',
	'badoutputscripts' : 'Error - could not generate output control scripts for ID %(id)s.',
	'badoutputscriptsunk' : 'Error - could not generate output control scripts.',
	'badtemplcntrllistinsert' : 'Error - could not insert control lists into web template file.',
	'badtemplcntrlscriptinsert' : 'Error - could not insert control scripts into web template file.',

	'badoutputfilesave' : 'Error - could not open output web page file for writing %(filename)s.',
	'badoutputfilewrite' : 'Error - could not write to output web page file %(filename)s.',

	# SVG Edit data.
	'badsvgeditsavewidget' : 'Error - Could not save SVG widget edit.',

	# Shared.
	'unknownparamtype' :  'Parameter is a unknown %(paramtype)s',
	'nodrawingparamdata' : 'No drawing parameter data found.'

	})

############################################################

