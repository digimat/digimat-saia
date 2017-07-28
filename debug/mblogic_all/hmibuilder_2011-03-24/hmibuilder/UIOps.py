##############################################################################
# Project: 	MBLogic
# Module: 	UIOps.py
# Purpose: 	User interface handling.
# Language:	Python 2.5
# Date:		23-Jan-2011.
# Version:	21-Mar-2011.
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

import Tkinter, tkFileDialog
import os


##############################################################################
class GUIStyleContainer:
	"""This holds GUI styling information, including icons. 
	Icons are read at start up, and stored in member variables.
	"""

	########################################################
	def __init__(self):
		self.BG = '#FAF0E6'
		self.Hover = '#D3D3D3'
		self.Entry = '#fff'
		self.Error = '#f97'

	########################################################
	def ReadIcons(self):
		"""Read in the icons. We can't create these during the module import, 
		because Tkinter will complain.		
		"""
		icondir = 'icons'
		self.Cancel = Tkinter.PhotoImage(file=os.path.join(icondir, 'cancelicon.gif'))
		self.FileOpen = Tkinter.PhotoImage(file=os.path.join(icondir, 'fileopenicon.gif'))
		self.Next = Tkinter.PhotoImage(file=os.path.join(icondir, 'nexticon.gif'))
		self.Prev = Tkinter.PhotoImage(file=os.path.join(icondir, 'previcon.gif'))
		self.Ok = Tkinter.PhotoImage(file=os.path.join(icondir, 'okicon.gif'))
		self.FileNew = Tkinter.PhotoImage(file=os.path.join(icondir, 'filenewicon.gif'))
		self.FileSave = Tkinter.PhotoImage(file=os.path.join(icondir, 'saveicon.gif'))
		self.Quit = Tkinter.PhotoImage(file=os.path.join(icondir, 'quiticon.gif'))
		self.Help = Tkinter.PhotoImage(file=os.path.join(icondir, 'helpicon.gif'))

GUIStyles = GUIStyleContainer()



##############################################################################
class ButtonContainer:
	"""This contains the main UI menu buttons.
	"""

	########################################################
	def __init__(self, window, shutdown, getfiles, help):
		"""Parameters: 
		window (Tkinter window) = The Tkinter window to contain the buttons.
		shutdown (function) = The function to call to exit the program.
		getfiles (function) = The function to call to get the input files.
		help (function) = The function to call to start the help server. 
		"""

		# This contains the buttons.
		self._ButtonFrame = Tkinter.Frame(window, bg=GUIStyles.BG)

		Tkinter.Button(self._ButtonFrame, compound=Tkinter.LEFT, image=GUIStyles.FileOpen, text='Select Files', 
						bg=GUIStyles.BG, activebackground=GUIStyles.Hover, command = getfiles).pack(side=Tkinter.LEFT)

		Tkinter.Button(self._ButtonFrame, compound=Tkinter.LEFT, image=GUIStyles.Quit, text='Quit', 
						bg=GUIStyles.BG, activebackground=GUIStyles.Hover, command = shutdown).pack(side=Tkinter.LEFT, padx=40)

		Tkinter.Button(self._ButtonFrame, compound=Tkinter.LEFT, image=GUIStyles.Help, text='Help', 
						bg=GUIStyles.BG, activebackground=GUIStyles.Hover, command = help).pack(side=Tkinter.LEFT)

		self._ButtonFrame.pack(side=Tkinter.TOP)


##############################################################################



##############################################################################
class FileChooser:
	"""Create a window which allows the user to select the files to work on.
	"""

	########################################################
	def __init__(self, window, basepath, svgfile, configfile, nextenable):
		"""Parameters: window: = (Tkinter window or frame).
			basepath: (string) = The default base path for locating files.
			svgfile: (string) = The currently selected SVG file name (if any).
			configfile: (string) = The currently selected HMI config file name (if any).
			nextenable: (Tkinter button) = The next screen to enable. 
		"""

		# SVG file name.
		self._SVGFileName = svgfile
		# HMI config file name.
		self._ConfigFileName = configfile

		# Base file path.
		self._BasePath = basepath
		# The SVG file name without the path.
		self._SVGName = os.path.split(svgfile)[1]

		# Create a frame to hold everything.
		self._FilesFrame = Tkinter.Frame(window, borderwidth=2, bg=GUIStyles.BG)

		# Label the box.
		Tkinter.Label(self._FilesFrame, text = 'Select Files', font=18, 
			bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# Make it visible.
		self._FilesFrame.pack(side=Tkinter.TOP)

		# Select the SVG file.
		SVGFrame = Tkinter.Frame(self._FilesFrame, bg=GUIStyles.BG)
		Tkinter.Button(SVGFrame, compound=Tkinter.LEFT, text='Select SVG File', 
			image=GUIStyles.FileOpen, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
			command = self._PickSVGFile).pack(side=Tkinter.LEFT)
		self._SVGLabel = Tkinter.Label(SVGFrame, text = '', font=12, bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3)
		self._SVGLabel.pack(side=Tkinter.LEFT, pady = 10)
		self._SVGLabel.configure(text=self._SVGFileName)
		SVGFrame.pack(side=Tkinter.TOP)

		# Select the config file.
		ConfigFrame = Tkinter.Frame(self._FilesFrame, bg=GUIStyles.BG)
		Tkinter.Button(ConfigFrame, compound=Tkinter.LEFT, text='Select HMI Config File', 
			image=GUIStyles.FileOpen, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
			command = self._PickConfigFile).pack(side=Tkinter.LEFT)
		self._ConfigLable = Tkinter.Label(ConfigFrame, text = '', font=12, bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3)
		self._ConfigLable.pack(side=Tkinter.LEFT, pady = 10)
		self._ConfigLable.configure(text=self._ConfigFileName)
		ConfigFrame.pack(side=Tkinter.TOP)

		# Next button.
		self._SelectOptsButton = Tkinter.Button(self._FilesFrame, compound=Tkinter.LEFT, text='Next', 
							bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
							image=GUIStyles.Next, state=Tkinter.DISABLED, command = nextenable)
		self._SelectOptsButton.pack(side=Tkinter.TOP)

		# Enable the "next" button if both files have already been chosen.
		if (len(self._SVGFileName) > 0) and (len(self._ConfigFileName) > 0):
			self._SelectOptsButton.configure(state=Tkinter.NORMAL)



	########################################################
	def RemoveWindow(self):
		"""Destroy the window.
		"""
		self._FilesFrame.destroy()


	########################################################
	def _PickSVGFile(self):
		"""Pick the SVG File.
		"""

		# define options for opening or saving a file
		fileoptions = {
			'defaultextension' : '',
			'filetypes' : [('svg files', '.svg'), ('all files', '.*')],
			'initialdir' : self._BasePath,
			'initialfile' : 'hmi.svg',
			'parent' : self._FilesFrame,
			'title' : 'Select SVG File'
			}

		# get filename
		self._SVGFileName = tkFileDialog.askopenfilename(**fileoptions)
		self._SVGLabel.configure(text=self._SVGFileName)

		# Get the new base file path.
		self._BasePath, self._SVGName = os.path.split(self._SVGFileName)

		# Enable the "next" button if both files have been chosen.
		if (len(self._SVGFileName) > 0) and (len(self._ConfigFileName) > 0):
			self._SelectOptsButton.configure(state=Tkinter.NORMAL)


	########################################################
	def _PickConfigFile(self):
		"""Pick the SVG File.
		"""

		# define options for opening or saving a file
		fileoptions = {
			'defaultextension' : '',
			'filetypes' : [('config files', '.config'), ('all files', '.*')],
			'initialdir' : self._BasePath,
			'initialfile' : 'mbhmi.config',
			'parent' : self._FilesFrame,
			'title' : 'Select HMI Config File'
			}

		# get filename
		self._ConfigFileName = tkFileDialog.askopenfilename(**fileoptions)
		self._ConfigLable.configure(text=self._ConfigFileName)

		# Get the new base file path.
		self._BasePath = os.path.split(self._ConfigFileName)[0]

		# Enable the "next" button if both files have been chosen.
		if (len(self._SVGFileName) > 0) and (len(self._ConfigFileName) > 0):
			self._SelectOptsButton.configure(state=Tkinter.NORMAL)


	########################################################
	def GetFileNames(self):
		"""Return the file names selected.
		Returns: svgfile (string), configfile (string), basepath (string),
			svgname (string) = The file names of the selected files plus the 
			base of the file path used to access them and the SVG file name
			without the directory path.
		"""
		return self._SVGFileName, self._ConfigFileName, self._BasePath, self._SVGName


##############################################################################



##############################################################################
class OptionChooser:
	"""Create a window which allows the user to select which layers to control
	using the screen menu system, plus also the alarm and event zones to monitor.
	"""

	########################################################
	def __init__(self, window, layerlist, currentlayers, alarmzonelist, currentalarms, 
							eventzonelist, currentevents, nextenable, prevenable, savesvg):
		"""Parameters: window: = (Tkinter window or frame).
			layerlist: (list) = The list of drawing layers to choose.
			currentlayers: (list) = List of layers that were previously selected. 
			alarmzonelist: (list) = The list of alarm zones to choose.
			currentalarms: (list) = List of alarm zones that were previously selected. 
			eventzonelist: (list) = The list of event zones to choose.
			currentevents: (list) = List of event zones that were previously selected. 
			nextenable: (function) = Call to go to the next step. 
			prevenable: (function) = Call to go to the previous step. 
			savesvg: (function) = Call to save the SVG data file.
		"""
		self._EnableNext = nextenable

		# SVG file name.
		self._SVGFileName = ''
		# HMI config file name.
		self._ConfigFileName = ''


		# Create a frame to hold everything.
		self._ContainerFrame = Tkinter.Frame(window, borderwidth=2, bg=GUIStyles.BG)


		# Make it visible.
		self._ContainerFrame.pack(side=Tkinter.TOP)


		# Create a frame to hold the various options.
		optioncontainer = Tkinter.Frame(self._ContainerFrame, borderwidth=2, bg=GUIStyles.BG)


		# Create a frame to hold the layer selection.
		layercontainer = Tkinter.Frame(optioncontainer, borderwidth=2, bg=GUIStyles.BG, relief=Tkinter.RAISED)

		# Label the box.
		Tkinter.Label(layercontainer, text = 'Select Layers', font=18, 
			bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# This list relates the IDs to the check boxes.
		self._LayerCheckBoxes = []

		# Select the layers.
		for id in layerlist:
			controlvar = Tkinter.IntVar()
			button = Tkinter.Checkbutton(layercontainer, text=id, variable=controlvar, bg=GUIStyles.BG)
			# Check if previously enabled.
			if id in currentlayers:
				button.select()
			button.pack(side=Tkinter.TOP, anchor=Tkinter.W, pady = 2)
			self._LayerCheckBoxes.append((controlvar, id))

		layercontainer.pack(side=Tkinter.LEFT)



		# Create a frame to hold the alarm zone selection.
		alarmcontainer = Tkinter.Frame(optioncontainer, borderwidth=2, bg=GUIStyles.BG, relief=Tkinter.RAISED)

		# Label the box.
		Tkinter.Label(alarmcontainer, text = 'Select Alarm Zones', font=18, 
			bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# This list relates the IDs to the check boxes.
		self._AlarmCheckBoxes = []

		# Select the alarms.
		for tag in alarmzonelist:
			controlvar = Tkinter.IntVar()
			button = Tkinter.Checkbutton(alarmcontainer, text=tag, variable=controlvar, bg=GUIStyles.BG)
			if tag in currentalarms:
				button.select()
			button.pack(side=Tkinter.TOP, anchor=Tkinter.W, pady = 2)
			self._AlarmCheckBoxes.append((controlvar, tag))

		alarmcontainer.pack(side=Tkinter.LEFT)


		# Create a frame to hold the event zone selection.
		eventcontainer = Tkinter.Frame(optioncontainer, borderwidth=2, bg=GUIStyles.BG, relief=Tkinter.RAISED)

		# Label the box.
		Tkinter.Label(eventcontainer, text = 'Select EventZones', font=18, 
			bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# This list relates the IDs to the check boxes.
		self._EventCheckBoxes = []

		# Select the events.
		for tag in eventzonelist:
			controlvar = Tkinter.IntVar()
			button = Tkinter.Checkbutton(eventcontainer, text=tag, variable=controlvar, bg=GUIStyles.BG)
			if tag in currentevents:
				button.select()
			button.pack(side=Tkinter.TOP, anchor=Tkinter.W, pady = 2)
			self._EventCheckBoxes.append((controlvar, tag))

		eventcontainer.pack(side=Tkinter.LEFT)

		# Make it visible.
		optioncontainer.pack(side=Tkinter.TOP)


		# Create a frame to hold the buttons.
		buttoncontainer = Tkinter.Frame(self._ContainerFrame, bg=GUIStyles.BG)

		# Add a button to go back to the previous screen.
		Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Prev', 
			image=GUIStyles.Prev, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
			command=prevenable).pack(side=Tkinter.LEFT, padx=10)

		# Add a button to save the SVG file.
		Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Save', 
			image=GUIStyles.FileSave, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
			command=savesvg).pack(side=Tkinter.LEFT, padx=10)

		# Add a button to indicate when we are done.
		Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Next', 
			image=GUIStyles.Next, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
			command=nextenable).pack(side=Tkinter.RIGHT, padx=10)

		# Make it visible.
		buttoncontainer.pack(side=Tkinter.TOP)



	########################################################
	def RemoveWindow(self):
		"""Destroy the window.
		"""
		self._ContainerFrame.destroy()


	########################################################
	def GetLayersList(self):
		"""Return the list of which layers were selected.
		Returns: (list) = List of ID strings which were selected.
		"""
		return [x[1] for x in self._LayerCheckBoxes if x[0].get() == 1]
		

	########################################################
	def GetAlarmZoneList(self):
		"""Return the list of which alarm zones were selected.
		Returns: (list) = List of alarm zones which were selected.
		"""
		return [x[1] for x in self._AlarmCheckBoxes if x[0].get() == 1]


	########################################################
	def GetEventZoneList(self):
		"""Return the list of which event zones were selected.
		Returns: (list) = List of event zones which were selected.
		"""
		return [x[1] for x in self._EventCheckBoxes if x[0].get() == 1]


##############################################################################



##############################################################################
class HTMLTemplateChooser:
	"""Create a window which allows the user to select the HTML template file
	and the output file name.
	"""

	########################################################
	def __init__(self, window, basepath, templatefile, outputfile, nextenable):
		"""Parameters: window: = (Tkinter window or frame).
			basepath: (string) = The default base path for locating files.
			templatefile: (string) = The currently selected HTML template 
				file name (if any).
			outputfile: (string) = The currently selected output file name (if any).
			nextenable: (function) = The step to perform. 
		"""

		# HTML template file name.
		self._TemplateFile = templatefile
		# Output file name.
		self._OutputFile = outputfile

		self._NextButton = nextenable

		# Base file path.
		self._BasePath = basepath


		# Create a frame to hold everything.
		self._FilesFrame = Tkinter.Frame(window, borderwidth=2, bg=GUIStyles.BG)

		# Label the box.
		Tkinter.Label(self._FilesFrame, text = 'Select Template and Output Files', font=18, 
			bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# Make it visible.
		self._FilesFrame.pack(side=Tkinter.TOP)

		# Select the HTML template file.
		TemplateFrame = Tkinter.Frame(self._FilesFrame, bg=GUIStyles.BG)
		Tkinter.Button(TemplateFrame, compound=Tkinter.LEFT, text='Select Template File', 
				image=GUIStyles.FileOpen, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
				command = self._PickTemplateFile).pack(side=Tkinter.LEFT)
		self._TemplateLabel = Tkinter.Label(TemplateFrame, text = '', 
				font=12, bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3)
		self._TemplateLabel.pack(side=Tkinter.LEFT, pady = 10)
		self._TemplateLabel.configure(text=self._TemplateFile)
		TemplateFrame.pack(side=Tkinter.TOP)


		# Select the HTML output file.
		OutputFrame = Tkinter.Frame(self._FilesFrame, bg=GUIStyles.BG)
		Tkinter.Button(OutputFrame, compound=Tkinter.LEFT, text='Select Output File Name', 
				image=GUIStyles.FileNew, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
				command = self._PickOutputFile).pack(side=Tkinter.LEFT)
		self._OutputLabel = Tkinter.Label(OutputFrame, text = '', 
				font=12, bg=GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3)
		self._OutputLabel.pack(side=Tkinter.LEFT, pady = 10)
		self._OutputLabel.configure(text=self._OutputFile)
		OutputFrame.pack(side=Tkinter.TOP)



		# Add button to assemble file.
		AssembleFrame = Tkinter.Frame(self._FilesFrame, borderwidth=2, bg=GUIStyles.BG)
		self._AssembleButton = Tkinter.Button(AssembleFrame, compound=Tkinter.LEFT, text='Assemble Page', 
					image=GUIStyles.FileSave, bg=GUIStyles.BG, activebackground=GUIStyles.Hover, 
					command = self._NextButton, state=Tkinter.DISABLED, padx=25, pady=25)
		self._AssembleButton.pack(side=Tkinter.LEFT)
		AssembleFrame.pack(side=Tkinter.TOP)
		

	########################################################
	def RemoveWindow(self):
		"""Destroy the window.
		"""
		self._FilesFrame.destroy()


	########################################################
	def _PickTemplateFile(self):
		"""Pick the template File.
		"""

		# define options for opening or saving a file
		fileoptions = {
			'defaultextension' : '',
			'filetypes' : [('xhtml files', '.xhtml'), ('html files', '.html'), ('all files', '.*')],
			'initialdir' : self._BasePath,
			'initialfile' : 'hmi.xhtml',
			'parent' : self._FilesFrame,
			'title' : 'Select XHTML Template File'
			}

		# get filename
		self._TemplateFile = tkFileDialog.askopenfilename(**fileoptions)
		self._TemplateLabel.configure(text=self._TemplateFile)

		# Get the new base file path.
		self._BasePath = os.path.split(self._TemplateFile)[0]

		# Enable the "next" button if both files have been chosen.
		if (len(self._TemplateFile) > 0) and (len(self._OutputFile) > 0):
			self._AssembleButton.configure(state=Tkinter.NORMAL)


	########################################################
	def _PickOutputFile(self):
		"""Pick the output File.
		"""

		# define options for opening or saving a file
		fileoptions = {
			'defaultextension' : '',
			'filetypes' : [('xhtml files', '.xhtml'), ('html files', '.html'), ('all files', '.*')],
			'initialdir' : self._BasePath,
			'initialfile' : 'hmi.xhtml',
			'parent' : self._FilesFrame,
			'title' : 'Select XHTML Output File'
			}

		# get filename
		self._OutputFile = tkFileDialog.asksaveasfilename(**fileoptions)
		self._OutputLabel.configure(text=self._OutputFile)

		# Get the new base file path.
		self._BasePath = os.path.split(self._OutputFile)[0]

		# Enable the "next" button if both files have been chosen.
		if (len(self._TemplateFile) > 0) and (len(self._OutputFile) > 0):
			self._AssembleButton.configure(state=Tkinter.NORMAL)


	########################################################
	def GetFileNames(self):
		"""Return the file names selected.
		Returns: template (string), output (string), basepath (string) = The 
			file names of the selected files plus the base of the file path
			used to access them.
		"""
		return self._TemplateFile, self._OutputFile, self._BasePath


##############################################################################



##############################################################################
class ShowError:
	"""This is used to display errors. It just shows an error message, but
	does not allow any other interaction.
	"""

	########################################################
	def __init__(self, window, msg):
		"""Parameters: window: = (Tkinter window or frame).
			msg: (string) = The error message to display.
		"""

		# Create a frame to hold everything.
		self._MsgFrame = Tkinter.Frame(window, bg=GUIStyles.Error)

		# Show the error message.
		Tkinter.Message(self._MsgFrame, text = msg, font=12, aspect=500, bg=GUIStyles.Error,
			relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# Make it visible.
		self._MsgFrame.pack(side=Tkinter.TOP)


	########################################################
	def RemoveWindow(self):
		"""Destroy the window.
		"""
		self._MsgFrame.destroy()


##############################################################################


