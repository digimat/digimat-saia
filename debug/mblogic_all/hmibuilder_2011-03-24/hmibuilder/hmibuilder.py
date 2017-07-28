#!/usr/bin/python
##############################################################################
# Project: 	MBLogic
# Module: 	hmibuilder.py
# Purpose: 	Build web based HMI pages.
# Language:	Python 2.5
# Date:		16-Jan-2011.
# Version:	16-Mar-2011.
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


import Tkinter

import sys, subprocess, webbrowser

import SVGEditData, FileOps, SVGParse, UIOps, FileAssembler

############################################################

_SOFTWARENAME = 'HMIBuilder'
_VERSION = '23-Mar-2011'

############################################################



##############################################################################
#Create main window.

MainWin = Tkinter.Tk()
MainWin.title(_SOFTWARENAME + '  ' + _VERSION)
MainWin.configure(bg=UIOps.GUIStyles.BG)

##############################################################################

class HMIBuilder:
	"""This contains the main HMI builder control code.
	"""

	########################################################
	def __init__(self, window):
		"""Parameters: window: (Tkinter window) = The window or frame to draw in.
		"""
		self._MainWin = window

		# SVG file name.
		self._SVGFileName = ''
		# HMI config file name.
		self._ConfigFileName = ''
		# HTML template file name.
		self._TemplateFile = ''
		# Web page output file name.
		self._OutputFile = ''

		# The options lists.
		self._LayersList = []
		self._AlarmZoneList = []
		self._EventZoneList = []

		# The current window we are editing.
		self._CurrentWindow = ''

		# The default file path name.
		self._BasePath = '.'

		# Get the icon files.
		UIOps.GUIStyles.ReadIcons()

		# The help web server has not been started yet.
		self._HelpWebServer = None

		# Create the main app window.
		self._MainApp = UIOps.ButtonContainer(self._MainWin, 
				self._ShutDown, self._GetFiles, self._HelpServer)


		# Pick the files.
		self._FilePick = None
		self._OptionsEdit = None
		self._SVGEditor = None
		self._PageAssembler = None
		self._ErrorMsg = None

		# Get the SVG and HMI config files.
		self._GetFiles()


	########################################################
	def _ShutDown(self):
		"""Exit the program.
		"""
		self._MainWin.destroy()
		self._MainWin.quit()


	########################################################
	def _WindowSwitch(self, current):
		"""Close all windows except the current one. This is used when 
		switching between the available options.
		Parameters: current (string) = A string code indicating what the 
			current window should be. All others will be closed (destroyed)
			if they are open.
		"""
		# Set the current window.
		self._CurrentWindow = current

		# Destroy the file selection window.
		if (current != 'filepick') and (self._FilePick != None):
			self._FilePick.RemoveWindow()

		# Destroy the options edit window.
		if (current != 'optionsedit') and (self._OptionsEdit != None):
			self._OptionsEdit.RemoveWindow()

		# Destroy the SVG edit window.
		if (current != 'editwidgets') and (self._SVGEditor != None):
			self._SVGEditor.RemoveWindow()

		# Destroy the page assembler window.
		if (current != 'assemblepage') and (self._PageAssembler != None):
			self._PageAssembler.RemoveWindow()

		# Destroy the error message window.
		if (current != 'errormsg') and (self._ErrorMsg != None):
			self._ErrorMsg.RemoveWindow()


	########################################################
	def _GetFiles(self):
		"""Select the SVG and HMI config files.
		"""
		# Check if the window is already enabled.
		if self._CurrentWindow == 'filepick':
			return

		# Close any other windows if they are open.
		self._WindowSwitch('filepick')


		# Pick the files.
		self._FilePick = UIOps.FileChooser(self._MainWin, self._BasePath, self._SVGFileName, 
											self._ConfigFileName, self._SelectOptions)


	########################################################
	def _SelectOptions(self):
		"""Select the drawing layers, and the alarm and event zones.
		"""

		# Check if the window is already enabled.
		if self._CurrentWindow == 'optionsedit':
			return

		# Close any other windows if they are open.
		self._WindowSwitch('optionsedit')

		# Get the file names selected.
		self._SVGFileName, self._ConfigFileName, self._BasePath, svgname = self._FilePick.GetFileNames()

		# Set the window title to match the selected SVG file.
		self._MainWin.title(svgname)

		# Read in the files.
		# Read in the HMI tag configuration.
		try:
			self._HMIConfigData = FileOps.HMITags(self._ConfigFileName)
		except FileOps.HMIConfigError as e:
			errmsg = e.errmsg
			self._WindowSwitch('errormsg')
			self._ErrorMsg = UIOps.ShowError(self._MainWin, errmsg)
			return

			
		# Read in the SVG file data.
		try:
			self._SVGData = SVGParse.SVGFileData(self._SVGFileName)

			# Update the layer information.
			self._SVGData.UpdateLayers()

			# Get the current selections from the file. These will exist if they
			# were saved from a previous editing session.
			currentlayers, currentalarmzones, currenteventzones = self._SVGData.GetDrawingParams()

		except SVGParse.SVGParseError as e:
			errmsg = e.errmsg
			self._WindowSwitch('errormsg')
			self._ErrorMsg = UIOps.ShowError(self._MainWin, errmsg)
			return

		# Get the layer ID data.
		layerids = self._SVGData.GetLayerIDs()
		SVGEditData.CodeConstants.LayerList = layerids

		# Get the alarm zone list.
		alarmzones = self._HMIConfigData.GetAlarmZoneList()
		# Get the event zone list.
		eventzones = self._HMIConfigData.GetEventZoneList()

		# Pick the layer IDs, and alarm and event zones.
		self._OptionsEdit = UIOps.OptionChooser(self._MainWin, layerids, currentlayers, 
							alarmzones, currentalarmzones, eventzones, currenteventzones, 
							self._EditWidgets, self._GetFiles, self._SaveSVG)




	########################################################
	def _EditWidgets(self):
		"""Edit the SVG widget tag associations.
		"""
		# Check if this editor already exists.
		if self._CurrentWindow == 'editwidgets':
			return

		# Close any other windows if they are open.
		self._WindowSwitch('editwidgets')

		# Get the list of options.
		self._LayersList = self._OptionsEdit.GetLayersList()
		# Get the alarm zone list.
		self._AlarmZoneList = self._OptionsEdit.GetAlarmZoneList()
		# Get the event zone list.
		self._EventZoneList = self._OptionsEdit.GetEventZoneList()


		# Edit the SVG widgets.
		self._SVGEditor = SVGEditData.SVGEditData(self._MainWin, 
				self._PickTemplate, self._SelectOptions, self._SaveSVG)

		# Set the list of tags which the SVG widgets can select.
		self._SVGEditor.SetHMITagList(self._HMIConfigData.GetTagList())
		# Set the list of SVG data which can be edited.
		self._SVGEditor.SetSVGEditData(self._SVGData.GetSVGFileData())
		# Set the list of layers ("screens") which can be selected.
		SVGEditData.CodeConstants.LayerList = self._LayersList



	########################################################
	def _SaveSVG(self):
		"""Save the SVG file.
		"""
		# Get the list of options.
		self._LayersList = self._OptionsEdit.GetLayersList()
		# Get the alarm zone list.
		self._AlarmZoneList = self._OptionsEdit.GetAlarmZoneList()
		# Get the event zone list.
		self._EventZoneList = self._OptionsEdit.GetEventZoneList()

		# Get the updated data and save it.
		try:
			if self._SVGEditor != None:
				newdata = self._SVGEditor.GetSVGEditData()
				self._SVGData.UpdateWidgetSVG(newdata)
			self._SVGData.UpdateListParams(self._LayersList, self._AlarmZoneList, self._EventZoneList)
			self._SVGData.WriteSVG()
		except SVGParse.SVGParseError as e:
			errmsg = e.errmsg
			self._WindowSwitch('errormsg')
			self._ErrorMsg = UIOps.ShowError(self._MainWin, errmsg)
			return



	########################################################
	def _PickTemplate(self):
		"""Pick the web page template and the final output XHTML web pages.
		"""
		# Check if this already exists.
		if self._CurrentWindow == 'assemblepage':
			return

		# Close any other windows if they are open.
		self._WindowSwitch('assemblepage')
		

		# Pick the files.
		self._PageAssembler = UIOps.HTMLTemplateChooser(self._MainWin, self._BasePath, 
									self._TemplateFile, self._OutputFile, self._AssemblePage)


	########################################################
	def _AssemblePage(self):
		"""Assemble the final web page.
		"""

		# Get the new file names.
		self._TemplateFile, self._OutputFile, self._BasePath = self._PageAssembler.GetFileNames()

		# Assemble the file data.
		try:
			template = FileAssembler.WebPageTemplate(self._TemplateFile, self._OutputFile)
		except SVGParse.SVGParseError as e:
			errmsg = e.errmsg
			self._WindowSwitch('errormsg')
			self._ErrorMsg = UIOps.ShowError(self._MainWin, errmsg)
			return

		# Get the updated widget data.
		widgetdata = self._SVGEditor.GetSVGEditData()

		# Create the input event handlers.
		self._SVGData.GenerateEventHandlers(widgetdata)

		# Insert the SVG.
		template.SetSVG(self._SVGData.GetBareSVGXML())

		# Create the read list.
		try:
			readlist = self._SVGData.GenerateReadList(widgetdata)

			# Insert the control lists.
			template.SetControlLists(readlist, self._AlarmZoneList, self._EventZoneList, self._LayersList)

			# Create the output control scripting.
			outputs = self._SVGData.GenerateOutputs(widgetdata)

			# Insert the control scripts.
			template.SetControlScripts(outputs)

			# Write out the completed file.
			template.WriteWebPage()

		except SVGParse.SVGParseError as e:
			errmsg = e.errmsg
			self._WindowSwitch('errormsg')
			self._ErrorMsg = UIOps.ShowError(self._MainWin, errmsg)
			return


	########################################################
	def _HelpServer(self):
		"""Launch the help web server.
		"""
		# Launch the help web server.
		if not self._HelpWebServer:
			pythonpath = sys.executable
			self._HelpWebServer = subprocess.Popen([pythonpath, 'helpserver.py'])

		# Open the default help page.
		webbrowser.open('http://localhost:8880/index.html', new=2, autoraise=True)


	########################################################
	def TerminateHelpServer(self):
		"""Terminate the help web server if it is running.
		"""
		if self._HelpWebServer:
			self._HelpWebServer.terminate()


##############################################################################

hmibuilder = HMIBuilder(MainWin)


##############################################################################


#######################

# Invoke main event loop.
MainWin.mainloop()

# Stop the help server.
hmibuilder.TerminateHelpServer()

#######################

