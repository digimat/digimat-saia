##############################################################################
# Project: 	MBLogic
# Module: 	SVGEditData.py
# Purpose: 	Get the SVG file data.
# Language:	Python 2.5
# Date:		16-Jan-2011.
# Version:	23-Mar-2011.
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

import UIOps
import ErrorMsgs

##############################################################################

# Colour to indicate an entry is OK.
_OKCOLOUR = 'white'
# Colour to indicate an error.
_ERRORCOLOUR = 'red'
# Colour to indicate an item has been edited.
_EDITEDCOLOUR = 'green'


##############################################################################

class CodeConstantsContainer:
	"""This stores data temporarily until it can be inserted into the SVG file.
	"""

	########################################################
	def __init__(self):
		# List of layers which are controlled by the screen selections.
		self.LayerList = []

CodeConstants = CodeConstantsContainer()


##############################################################################

class SVGEditData:
	"""Read in and parse SVG file data.
	"""
	########################################################
	def __init__(self, container, nextenable, prevenable, savesvg):
		"""Parameters: container (object) = The Tkinter window or frame
			container to draw the user interface in.
			nextenable: (function) = Call to go to the next step. 
			prevenable: (function) = Call to go to the previous step. 
			savesvg: (function) = Call to save the SVG data file.
		"""

		# The window or frame container to put the widgets in.
		self._Container = Tkinter.Frame(container, borderwidth=2, bg=UIOps.GUIStyles.BG)


		# SVG file data.
		self._SVGFileData = []
		# SVG file data keyed by ID.
		self._WidgetData = {}


		# List of address tags.
		self._AddrTagList = []


		# Combined list of IDs.
		self._IDList = []

		# The list box used to select SVG widget ids for editing.
		self._WidgetIDSelect = None
		# The current selection index.
		self._CurrentIDIndex = None

		# Contains the entire widget editing area.
		self._EditFrame = None
		# Frame for editing a single widget.
		self._WidgetEditFrame = None
		# References to the current parameters we are editing. We store these 
		# in a list so we can relate the parameter number to the edit control.
		self._CurrentMenuParams = []
		# The currently selected id.
		self._CurrentID = ''

		# Used to display error messages. A value of None means the error
		# message is not currently displayed. We have to avoid duplicating
		# this multiple times.
		self._ErrorContainer = None


		# Construct the user interface.

		######

		# Create a frame to hold the list of widget ids.
		taglistframe = Tkinter.Frame(self._Container, borderwidth=2, bg=UIOps.GUIStyles.BG)
		# Label the box.
		Tkinter.Label(taglistframe, text = 'SVG Drawing IDs', font=18, 
			bg=UIOps.GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)
		# Create a list box.
		self._WidgetIDSelect = Tkinter.Listbox(taglistframe, height=40, width=15)
		self._WidgetIDSelect.bind('<ButtonRelease-1>', self._PickID)
		self._WidgetIDSelect.bind('<Return>', self._PickID)
		# Add a scroll bar.
		scroll = Tkinter.Scrollbar(taglistframe, bg=UIOps.GUIStyles.BG, command=self._WidgetIDSelect.yview)
		self._WidgetIDSelect.configure(yscrollcommand=scroll.set)
		self._WidgetIDSelect.pack(side=Tkinter.LEFT)
		scroll.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

		# Make it visible.
		taglistframe.pack(side=Tkinter.LEFT)

		######

		# Create a frame to hold the address tags.
		self._AddrContainer = Tkinter.Frame(self._Container, bg=UIOps.GUIStyles.BG)

		# Label the list box.
		Tkinter.Label(self._AddrContainer, text = 'Address Tags', 
								bg=UIOps.GUIStyles.BG, font=18).pack(side=Tkinter.TOP, pady = 10)

		# Create a list box.
		self._AddrTagSelect = Tkinter.Listbox(self._AddrContainer, height=30, width=15)
		# Add a scroll bar.
		scroll = Tkinter.Scrollbar(self._AddrContainer, bg=UIOps.GUIStyles.BG, command=self._AddrTagSelect.yview)
		self._AddrTagSelect.configure(yscrollcommand=scroll.set)
		self._AddrTagSelect.pack(side=Tkinter.LEFT)
		scroll.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

		self._AddrContainer.pack(side=Tkinter.LEFT)

		######

		# Create a frame to hold the editing widgets.
		editcontainer = Tkinter.Frame(self._Container, bg=UIOps.GUIStyles.BG)

		# Create a frame to hold the editing widgets which change with each item.
		self._EditFrame = Tkinter.Frame(editcontainer, bg=UIOps.GUIStyles.BG)

		# Label the edit area.
		Tkinter.Label(self._EditFrame, text = 'Edit SVG Widget Parameters', 
								bg=UIOps.GUIStyles.BG, font=18).pack(side=Tkinter.TOP, pady = 10)


		# make the edit frame visible.
		self._EditFrame.pack(side=Tkinter.TOP)


		# Add buttons to save or cancel.
		ButtonFrame = Tkinter.Frame(editcontainer, bg=UIOps.GUIStyles.BG)

		self._EditCancelButton = Tkinter.Button(ButtonFrame, compound=Tkinter.LEFT, text='Cancel', 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			image=UIOps.GUIStyles.Cancel, command = self._CancelButton)
		self._EditCancelButton.pack(side=Tkinter.LEFT, padx=20, pady=20)

		self._EditOKButton = Tkinter.Button(ButtonFrame, compound=Tkinter.LEFT, text='Ok', 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			image=UIOps.GUIStyles.Ok, command = self._OkButton)
		self._EditOKButton.pack(side=Tkinter.RIGHT, padx=20, pady=20)

		ButtonFrame.pack(side=Tkinter.TOP)


		# Disable the buttons.
		self._EditOKButton.configure(state=Tkinter.DISABLED)
		self._EditCancelButton.configure(state=Tkinter.DISABLED)


		# Create a frame to hold the next, save, previous buttons.
		buttoncontainer = Tkinter.Frame(editcontainer, bg=UIOps.GUIStyles.BG)

		# Add a button to go back to the previous screen.
		Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Prev', 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			image=UIOps.GUIStyles.Prev, command=prevenable).pack(side=Tkinter.LEFT, padx=10, pady=20)

		# Add a button to save the SVG file.
		Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Save', 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			image=UIOps.GUIStyles.FileSave, command=savesvg).pack(side=Tkinter.LEFT, padx=10, pady=20)

		# Add a button to indicate when we are done. This button is initially disabled.
		self._NextButton = Tkinter.Button(buttoncontainer, compound=Tkinter.LEFT, text='Next', 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			image=UIOps.GUIStyles.Next, state=Tkinter.DISABLED, command=nextenable)
		self._NextButton.pack(side=Tkinter.RIGHT, padx=10, pady=20)

		# Make it visible.
		buttoncontainer.pack(side=Tkinter.TOP)

		editcontainer.pack(side=Tkinter.TOP)

		######

		# Make it visible.
		self._Container.pack(side=Tkinter.LEFT)


	########################################################
	def RemoveWindow(self):
		"""Destroy the window.
		"""
		self._Container.destroy()


	########################################################
	def SetHMITagList(self, taglist):
		"""Set the HMI tag list.
		Parameters: taglist (list) = The list of HMI address tags.
		"""
		self._AddrTagList = taglist

		# Add the address tag list to the list box.
		for tag in self._AddrTagList:
			self._AddrTagSelect.insert(Tkinter.END, tag)

		# Disable the list box.
		self._AddrTagSelect.configure(state=Tkinter.DISABLED)


	########################################################
	def SetSVGEditData(self, svgfiledata):
		"""Set the SVG file data list.
		Parameters: svgfiledata (list) = The list of SVG file data read from disk.
		"""
		self._SVGFileData = svgfiledata

		# Convert the data to a dictionary keyed on id.
		self._WidgetData = dict([(x['widgetid'], x) for x in self._SVGFileData])

		# Get a list of widgets which have already been edited.
		edited = [x for x,y in self._WidgetData.items() if str(y['editcount']) != '0']

		# Get a simple list of IDs.
		self._IDList = self._WidgetData.keys()
		# Sort.
		self._IDList.sort()

		# Add the widget list to the list box.
		for index, id in enumerate(self._IDList):
			self._WidgetIDSelect.insert(Tkinter.END, id)
			# Was the current selection previously edited?
			if id in edited:
				self._WidgetIDSelect.itemconfig(index, background=_EDITEDCOLOUR)


		# Check if all the widgets have been edited yet.
		self._CheckEditStatus()



	########################################################
	def GetSVGEditData(self):
		"""Return the edited SVG widget data.
		"""
		return self._WidgetData



	########################################################
	def _OkButton(self):
		"""The user clicked on the OK button. Update the parameter data with 
		the current edits.
		"""

		if self._SaveChanges():
			# Enable the list box.
			self._WidgetIDSelect.configure(state=Tkinter.NORMAL)

			# Mark the curren selection as edited.
			self._WidgetIDSelect.itemconfig(self._CurrentIDIndex, background=_EDITEDCOLOUR)

			# Disable the buttons.
			self._EditOKButton.configure(state=Tkinter.DISABLED)
			self._EditCancelButton.configure(state=Tkinter.DISABLED)

			# Remove the edit frame.
			self._RemoveEditFrame()

			# Re-initialise the list of active parameter edit widgets.		
			self._CurrentMenuParams = []

		# We have an error, but only display the message if it isn't already displayed.
		elif self._ErrorContainer == None:
			self._ErrorContainer = Tkinter.Frame(self._Container, borderwidth=2, bg=UIOps.GUIStyles.BG)

			errmsg = ErrorMsgs.Msg.GetMessage('badsvgeditsavewidget', {})
			self._SaveErrorMsg = UIOps.ShowError(self._ErrorContainer, errmsg)

			self._SaveErrorAck = Tkinter.Button(self._ErrorContainer, text='Ok', 
				bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
				command = self._SaveErrorAckButton)
			self._SaveErrorAck.pack(side=Tkinter.TOP)
			self._ErrorContainer.pack(side=Tkinter.TOP)



	########################################################
	def _SaveErrorAckButton(self):
		"""Acknowledge a widget save error, and remove the error message.
		"""
		# Remove the error message.
		self._ErrorContainer.destroy()
		self._ErrorContainer = None



	########################################################
	def _CancelButton(self):

		# If the frame already exits, destroy it.
		self._RemoveEditFrame()
		# Re-initialise the list of active parameter edit widgets.		
		self._CurrentMenuParams = []

		# If an error message is displayed, cancel it.
		if self._ErrorContainer != None:
			self._SaveErrorAckButton()

		# Enable the list box.
		self._WidgetIDSelect.configure(state=Tkinter.NORMAL)

		# Disable the buttons.
		self._EditOKButton.configure(state=Tkinter.DISABLED)
		self._EditCancelButton.configure(state=Tkinter.DISABLED)


	########################################################
	def _PickID(self, event):
		"""The user has selected an id from the list box.
		"""
		selection = self._WidgetIDSelect.curselection()
		# Check if we have a valid selection.
		if (len(selection) != 1):
			return

		# Is it already currently selected?
		if selection == self._CurrentIDIndex:
			return
		else:
			self._CurrentIDIndex = selection

		# Disable the list box.
		self._WidgetIDSelect.configure(state=Tkinter.DISABLED)

		# Relate this to the actual ID.
		index = int(selection[0])
		id = self._IDList[index]
		

		# Build the input form.
		self._BuildEditForm(id, self._EditFrame)

		# Enable the buttons.
		self._EditOKButton.configure(state=Tkinter.NORMAL)
		self._EditCancelButton.configure(state=Tkinter.NORMAL)


	########################################################
	def _RemoveEditFrame(self):
		"""Remove the current edit frame if it exists.
		"""
		if self._WidgetEditFrame:
			self._WidgetEditFrame.destroy()



	########################################################
	def _BuildEditForm(self, id, window):
		"""Create a form for editing SVG widgets.
		"""

		# Re-initialise the list of active parameter edit widgets.		
		self._CurrentMenuParams = []
		# Set the current ID.
		self._CurrentID = id

		# If the frame already exits, destroy it.
		self._RemoveEditFrame()


		# Create a frame to hold the editing widgets.
		self._WidgetEditFrame = Tkinter.Frame(window, borderwidth=2, bg=UIOps.GUIStyles.BG)

		# This is the parameter set the user selected.
		currentparams = self._WidgetData[id]

		# The id of the widget.
		Tkinter.Label(self._WidgetEditFrame, text = id, font=18, 
			bg=UIOps.GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)

		# The name of the widget.
		Tkinter.Label(self._WidgetEditFrame, text = currentparams['widgetname'], font=18, 
			bg=UIOps.GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.TOP, pady = 10)


		# Build the form itself.
		self._BuildForm(self._WidgetEditFrame, currentparams['menu'])


		# make the edit frame visible.
		self._WidgetEditFrame.pack(side=Tkinter.TOP)



	########################################################
	def _BuildForm(self, window, paramlist):
		"""Create a form for editing inputs or outputs.
		Parameters: window: (Tkinter window) = The Tkinter window or frame to draw in.
			paramlist: (list) = The list of parameters to edit.
		"""
		# Create a frame to hold the editing widgets.
		editframe = Tkinter.Frame(window, borderwidth=2, bg=UIOps.GUIStyles.BG)


		for index, x in enumerate(paramlist):
			paramtype = x['type']
			paramvalue = x['value']

			# Check if it is a visible editing control. We don't edit 
			# constants, so we don't want to create labels for them.
			if paramtype in ['tag', 'int', 'float', 'str', 'textlist', 'colour', 'layer', 'none']:
				# Create a frame to hold the editing widgets.
				itemframe = Tkinter.Frame(editframe, borderwidth=2, bg=UIOps.GUIStyles.BG)
				# Add a label.
				Tkinter.Label(itemframe, text = x['name'], font=12, 
					bg=UIOps.GUIStyles.BG, relief=Tkinter.RIDGE, borderwidth=3).pack(side=Tkinter.LEFT, pady = 2)


				# This parameter wants an address tag.
				if paramtype == 'tag':
					self._CurrentMenuParams.append(EditAddrTags(itemframe, index, paramvalue, 
								self._AddrTagList, self._AddrTagSelect, self._DefaultCallBack))
				# Integer.
				elif paramtype == 'int':
					self._CurrentMenuParams.append(EditInt(itemframe, index, paramvalue))
				# Floating point number.
				elif paramtype == 'float':
					self._CurrentMenuParams.append(EditFloat(itemframe, index, paramvalue))
				# String.
				elif paramtype == 'str':
					self._CurrentMenuParams.append(EditStr(itemframe, index, paramvalue))
				# Text list (list of strings).
				elif paramtype == 'textlist':
					self._CurrentMenuParams.append(EditTextList(itemframe, index, paramvalue))
				# Colour
				elif paramtype == 'colour':
					self._CurrentMenuParams.append(EditColour(itemframe, index, paramvalue))
				# Layer, which provides "screens".
				elif paramtype == 'layer':
					self._CurrentMenuParams.append(EditScreenSelects(itemframe, index, paramvalue))
				# No parameters to edit.
				elif paramtype == 'none':
					self._CurrentMenuParams.append(EditNone(index))

				# Make the frame visible.
				itemframe.pack(side=Tkinter.TOP, pady = 2)

		# Make the edit frame visible.
		editframe.pack(side=Tkinter.TOP, pady = 10)


	########################################################
	def _DefaultCallBack(self, event):
		"""This is used as a default callback handler to prevent errors from
		callbacks that no longer exist when edit objects are destroyed.
		"""
		pass



	########################################################
	def _SaveChanges(self):
		"""Save the editing changes. Returns True if the save operation
		was completed successfully. 
		"""
		if len(self._CurrentMenuParams) == 0:
			return False

		# Check all the parameters.
		menupresult = [x.Validate() for x in self._CurrentMenuParams]

		# Check if there were errors. 
		if not all(menupresult):
			return False


		# Get the current widget.
		widget = self._WidgetData[self._CurrentID]

		# Add the edited input parameters to the widget data.
		for i in self._CurrentMenuParams:
			pvalue, pindex = i.GetValue()
			widget['menu'][pindex]['value'] = pvalue


		# Increment the edit counter.
		widget['editcount'] = int(widget['editcount']) + 1

		# Check if all the widgets have been edited yet.
		self._CheckEditStatus()

		return True


	########################################################
	def _CheckEditStatus(self):
		"""Check the status of all the widgets to see if they have been
		edited yet. If all widgets have been edited, enable the "next" button.
		"""

		# Get a list of widgets which have NOT already been edited.
		notedited = [x for x,y in self._WidgetData.items() if str(y['editcount']) == '0']

		# If there are no unedited widgets, enable the "next" button.
		if len(notedited) == 0:
			self._NextButton.configure(state=Tkinter.NORMAL)


##############################################################################


##############################################################################
class EditInt:
	"""Edit an integer parameter.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Parameters: window: (Tkinter window) = The window or frame 
		to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter, 1 is the second, etc.).
			paramvalue: (string) = The current integer value as a string.
		"""
		self._Index = index
		self._ControlVar = Tkinter.StringVar()
		self._ControlVar.set(paramvalue)
		self._Entry = Tkinter.Entry(window, textvariable=self._ControlVar, 
					width=10, justify=Tkinter.RIGHT, bg=UIOps.GUIStyles.Entry)
		self._Entry.pack(side=Tkinter.LEFT)

		# Add a handler so we can validate the input.
		self._Entry.bind('<KeyRelease>', self._VHandler)
		

	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._ControlVar.get(), self._Index)

	########################################################
	def Validate(self):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid integer.
		"""
		# Get the contents.
		value = self._ControlVar.get()

		# Can we convert to integer?
		try:
			x = int(value)
			self._Entry.configure(bg=_OKCOLOUR)
			return True
		except:
			self._Entry.configure(bg=_ERRORCOLOUR)
			return False


	########################################################
	def _VHandler(self, event):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid integer.
		Parameters: event (Tkinter event) = The Tkinter event.
		"""
		self.Validate()



##############################################################################
class EditFloat:
	"""Edit a float parameter.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Parameters: window: (Tkinter window) = The window or frame 
		to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter, 1 is the second, etc.).
			paramvalue: (string) = The current float value as a string.
		"""
		self._Index = index
		self._ControlVar = Tkinter.StringVar()
		self._ControlVar.set(paramvalue)
		self._Entry = Tkinter.Entry(window, textvariable=self._ControlVar, 
					width=10, justify=Tkinter.RIGHT, bg=UIOps.GUIStyles.Entry)
		self._Entry.pack(side=Tkinter.LEFT)

		# Add a handler so we can validate the input.
		self._Entry.bind('<KeyRelease>', self._VHandler)
		

	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._ControlVar.get(), self._Index)

	########################################################
	def Validate(self):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid float.
		"""
		# Get the contents.
		value = self._ControlVar.get()

		# Can we convert to float?
		try:
			x = float(value)
			self._Entry.configure(bg=_OKCOLOUR)
			return True
		except:
			self._Entry.configure(bg=_ERRORCOLOUR)
			return False


	########################################################
	def _VHandler(self, event):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid integer.
		Parameters: event (Tkinter event) = The Tkinter event.
		"""
		self.Validate()



##############################################################################

class EditStr:
	"""Edit a string parameter.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Add a string edit box.
		Parameters: window: (Tkinter window) = The window or frame to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter, 1 is the second, etc.).
			paramvalue: (string) = The current string value.
		"""
		self._Index = index
		self._ControlVar = Tkinter.StringVar()
		self._ControlVar.set(paramvalue)
		self._Entry = Tkinter.Entry(window, textvariable=self._ControlVar, 
					width=10, justify=Tkinter.RIGHT, bg=UIOps.GUIStyles.Entry)
		self._Entry.pack(side=Tkinter.LEFT)

		# Add a handler so we can validate the input.
		self._Entry.bind('<KeyRelease>', self._VHandler)
		

	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._ControlVar.get(), self._Index)

	
	########################################################
	def Validate(self):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid string.
		"""
		# We actually allow anything, including empty strings.
		self._Entry.configure(bg=_OKCOLOUR)
		return True
		
	########################################################
	def _VHandler(self, event):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid string.
		Parameters: event (Tkinter event) = The Tkinter event.
		"""
		self.Validate()


##############################################################################

class EditTextList:
	"""Edit a text list parameter.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Add a text list edit box.
		Parameters: window: (Tkinter window) = The window or frame to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter, 1 is the second, etc.).
			paramvalue: (list) = The current value as a list of strings.
		"""
		self._Index = index
		self._ControlVar = Tkinter.StringVar()

		# Convert the parameter value into a string before assigning it.
		try:
			paramstr = ', '.join(paramvalue)
		except:
			# We may not have valid data. 
			paramstr = ''

		self._ControlVar.set(paramstr)
		self._Entry = Tkinter.Entry(window, textvariable=self._ControlVar, 
					width=24, justify=Tkinter.RIGHT, bg=UIOps.GUIStyles.Entry)
		self._Entry.pack(side=Tkinter.LEFT)

		# Add a handler so we can validate the input.
		self._Entry.bind('<KeyRelease>', self._VHandler)
		

	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		# Get the current value. We also convert to string to prevent
		# unicode symbols from ending up in the finished string.
		tstr = str(self._ControlVar.get())
		# Strip out any embedded double quotes.
		tstr = tstr.replace('"', '')
		# And single quotes.
		tstr = tstr.replace("'", '')
		# Split the string into a list of strings and strip the white space.
		tlist = [x.strip() for x in tstr.split(',')]
		# Return the list of strings, and the index.
		return (tlist, self._Index)

	
	########################################################
	def Validate(self):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid string.
		"""
		# Get the contents.
		value = self._ControlVar.get()

		# Are there any characters?
		if len(value) > 0:
			self._Entry.configure(bg=_OKCOLOUR)
			return True
		else:
			self._Entry.configure(bg=_ERRORCOLOUR)
			return False


	########################################################
	def _VHandler(self, event):
		"""Validate a Tkinter Entry box to check if the contents are a
		valid string.
		Parameters: event (Tkinter event) = The Tkinter event.
		"""
		self.Validate()



##############################################################################


class EditAddrTags:
	"""Edit an address tag.
	"""
	########################################################
	def __init__(self, window, index, paramvalue, addrtags, listbox, defcallback):
		"""Add an address tag edit widget.
		Parameters: window: (Tkinter window) = The window or frame to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter, 1 is the second, etc.).
			paramvalue: (string) = The current address tag value.
			addrtags: (list) = List of valid address tags.
			listbox: (object) = The address tag selection list box.
			defcallback: (function) = The function to use as a default 
				callback when this object is no longer active. 
		"""
		self._Index = index
		self._ListBox = listbox
		self._AddrTag = paramvalue
		self._AddrTagList = addrtags
		self._DefCallBack = defcallback
		
		self._EditAddrButton = Tkinter.Button(window, compound=Tkinter.LEFT, text=paramvalue, 
			bg=UIOps.GUIStyles.BG, activebackground=UIOps.GUIStyles.Hover, 
			command = self._SetCallBack)
		self._EditAddrButton.pack(side=Tkinter.RIGHT)



	########################################################
	def _SetCallBack(self):
		"""Set the current object as the callback for selecting an item
		from the address list box "click".
		"""
		self._ListBox.bind('<ButtonRelease-1>', self._PickAddrTag)
		self._ListBox.bind('<Return>', self._PickAddrTag)
		# Enable the list box.
		self._ListBox.configure(state=Tkinter.NORMAL)
		

	########################################################
	def _PickAddrTag(self, event):
		"""The user has selected an address tag from the list box.
		"""
		selection = self._ListBox.curselection()
		# Check if we have a valid selection.
		if (len(selection) != 1):
			return

		# Disable the list box.
		self._ListBox.configure(state=Tkinter.DISABLED)
		# Set the callbacks to a default. This effectively removes the callback
		# from the listbox to avoid errors after this edit object is destroyed.
		self._ListBox.bind('<ButtonRelease-1>', self._DefCallBack)
		self._ListBox.bind('<Return>', self._DefCallBack)

		# Relate this to the actual address tag.
		index = int(selection[0])
		self._AddrTag = self._AddrTagList[index]
		self._EditAddrButton.configure(text=self._AddrTag)


	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._AddrTag, self._Index)


	########################################################
	def Validate(self):
		"""Validate a Tkinter option menu to check if anything has been selected.
		"""
		# Get the contents.
		# Check if a value is present.
		if len(self._AddrTag) > 0:
			self._EditAddrButton.configure(bg=_OKCOLOUR)
			return True
		else:
			self._EditAddrButton.configure(bg=_ERRORCOLOUR)
			return False


##############################################################################

class EditColour:
	"""Edit colour entry.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Add colour selection edit widget.
		Parameters: window: (Tkinter window) = The window or frame to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter:, 1 is the second, etc.).
			paramvalue: (string) = The current colour.
		"""
		self._Index = index
		# List of colours.
		self._ColourList = ['black', 'aqua', 'blue', 'cyan', 'grey', 'green', 
			'indigo', 'khaki', 'lime', 'maroon', 'navy', 'olive', 'orange', 
			'purple', 'red', 'silver', 'tan', 'teal', 'violet', 'white', 
			'yellow']

		# Create an option menu to select address tags for parameters.
		self._ControlVar = Tkinter.StringVar()
		# Set the current parameter value, if there is one.
		if paramvalue in self._ColourList:
			self._ControlVar.set(paramvalue)

		self._Entry = Tkinter.OptionMenu(window, self._ControlVar, *self._ColourList)
		self._Entry.configure(bg=UIOps.GUIStyles.BG)
		self._Entry.pack(side=Tkinter.LEFT)


	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._ControlVar.get(), self._Index)


	########################################################
	def Validate(self):
		"""Validate a Tkinter option menu to check if anything has been selected.
		"""
		# Get the contents.
		value = self._ControlVar.get()
		# Check if a value is present.
		if len(value) > 0:
			self._Entry.configure(bg=_OKCOLOUR)
			return True
		else:
			self._Entry.configure(bg=_ERRORCOLOUR)
			return False



##############################################################################

class EditScreenSelects:
	"""Edit screen select entry.
	"""

	########################################################
	def __init__(self, window, index, paramvalue):
		"""Add layer selection edit widget.
		Parameters: window: (Tkinter window) = The window or frame to draw the UI in.
			index: (integer) = The parameter index (e.g. 0 is the first 
				parameter:, 1 is the second, etc.).
			paramvalue: (string) = The current layer.
		"""
		self._Index = index

		# Create an option menu to select address tags for parameters.
		self._ControlVar = Tkinter.StringVar()
		# Set the current parameter value, if there is one.
		if paramvalue in CodeConstants.LayerList:
			self._ControlVar.set(paramvalue)

		self._Entry = Tkinter.OptionMenu(window, self._ControlVar, *CodeConstants.LayerList)
		self._Entry.configure(bg=UIOps.GUIStyles.BG)
		self._Entry.pack(side=Tkinter.LEFT)


	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return (self._ControlVar.get(), self._Index)


	########################################################
	def Validate(self):
		"""Validate a Tkinter option menu to check if anything has been selected.
		"""
		# Get the contents.
		value = self._ControlVar.get()
		# Check if a value is present.
		if len(value) > 0:
			self._Entry.configure(bg=_OKCOLOUR)
			return True
		else:
			self._Entry.configure(bg=_ERRORCOLOUR)
			return False
	
		


##############################################################################
class EditNone:
	"""Dummmy edit routine for widgets which take no parameters.
	"""

	########################################################
	def __init__(self, index):
		"""
		Parameters: index: (integer) = The parameter index (e.g. 0 is the first 
				parameter:, 1 is the second, etc.).
		"""
		self._Index = index
		pass
		

	########################################################
	def GetValue(self):
		"""Return the widget value and the index.
		"""
		return ('', self._Index)

	########################################################
	def Validate(self):
		"""Always returns True.
		"""
		return True


	########################################################
	def _VHandler(self, event):
		"""Always returns True.
		Parameters: event (Tkinter event) = The Tkinter event.
		"""
		self.Validate()



##############################################################################

