##############################################################################
# Project: 	MBLogic
# Module: 	SVGParse.py
# Purpose: 	SVG parsing and analysis.
# Language:	Python 2.6
# Date:		19-Jan-2011.
# Version:	12-Mar-2011.
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

import itertools
import xml.dom.minidom
import json

import ErrorMsgs

##############################################################################
# Error handling exception classes.

class SVGParseError(Exception):
	"""Error reading or decoding SVG file.
	"""
	def __init__(self, errmsg):
		self.errmsg = errmsg

##############################################################################
class SVGFileData:
	"""Read in the SVG file data and parse out the MBLogic widgets.
	"""

	########################################################
	def __init__(self, svgfilename):
		"""Parameters: svgfilename (string) = The name of the svg file.
		"""
		# The file name.
		self._SVGFileName = svgfilename
		# The resulting SVG widget data.
		self._SVGWidgetInfo = []
		# The SVG object.
		self._SVG = None
		# The parsed SVG.
		self._SVGXML = None

		# The list of layer IDs.
		self._LayerIDs = []

		# Read in the file and parse the data.
		self.ReadSVGFile()


	########################################################
	def ReadSVGFile(self):
		"""Read in the SVG file and parse out the HMI SVG widgets.
		Results are stored in a class variable. 
		"""
		errfile = {'filename' : self._SVGFileName}

		# Open the file.
		try:
			self._SVG = xml.dom.minidom.parse(self._SVGFileName)
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvgfileread', errfile))

		# Get all the groups.
		glist = self._SVG.getElementsByTagName('g')
		# Now, filter them to select just the ones that represent widgets.
		self._SVGXML = [x for x in glist if x.hasAttribute('mblogic:widgettype')]


		# Get the information about the widgets.
		self._SVGWidgetInfo = map(self._GetWidgetData, self._SVGXML)


	########################################################
	def WriteSVG(self):
		"""Write the current SVG data to disk to the current file.
		"""
		errfile = {'filename' : self._SVGFileName}

		# Open the file for writing.
		try:
			f = open(self._SVGFileName, 'w')
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvgfilesave', errfile))

		# Write out the data.
		try:
			f.write(self._SVG.toxml())
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvgfilewrite', errfile))
		finally:
			f.close()


	########################################################
	def GetSVGFileData(self):
		"""Return the list of SVG widget data.
		Returns: (list) = List of SVG widget data.
		"""
		return self._SVGWidgetInfo


	########################################################
	def UpdateLayers(self):
		"""Find all the layers, and update the layer id information with
		the appropriate Inkscape attribute data.
		"""
		try:
			# Layers use groups. Find all the group tags.
			groups = self._SVG.getElementsByTagName('g')

			# Filter those groups which are layers, and also get the Inkscape layer labels. 
			layers = [(x, x.getAttribute('inkscape:label')) for x in groups if x.getAttribute('inkscape:groupmode') == 'layer']

			# Update the group IDs to assign the same ID as was used for the group name.
			for group, label in layers:
				group.setAttribute('id', label)

			# Save the list of IDs.
			self._LayerIDs = [x[1] for x in layers]

		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvglayerconfig', {}))


	########################################################
	def GetLayerIDs(self):
		"""Return the list of layer IDs.
		Returns: (list) = List of strings containing the layer IDs.
		"""
		return self._LayerIDs



	########################################################
	def _GetWidgetData(self, node):
		"""Get all the data and attributes for a single HMI SVG widget.
		Parameters: node (xml node) = An xml node for an HMI SVG widget.
		Returns: (dict) = A dictionary with the results.
		"""
		widgetdata = {}

		# Get the id.
		widgetdata['widgetid'] = node.getAttribute('id')

		# Get the basic widget definition data.
		widgetdata['widgettype'] = node.getAttribute('mblogic:widgettype')
		widgetdata['widgetname'] = node.getAttribute('mblogic:widgetname')
		widgetdata['editcount'] = node.getAttribute('mblogic:editcount')

		# These items are stored as JSON data embedded in the attribute string.
		widgetdata['menu'] = json.loads(node.getAttribute('mblogic:menu'))
		widgetdata['inputfunc'] = json.loads(node.getAttribute('mblogic:inputfunc'))
		widgetdata['outputfunc'] = node.getAttribute('mblogic:outputfunc')


		# Return this as a dictionary.
		return widgetdata


	########################################################
	def _UpdateWidgetData(self, node, widgetdata):
		"""Update the edited data and attributes for a single HMI SVG widget.
		Parameters: node (xml node) = An xml node for an HMI SVG widget.
				widgetdata: (dict) = A dictionary with the new widget data.
		"""

		# Update the edit count. The edit count is how we keep track of
		# whether this widget has been edited.
		node.setAttribute('mblogic:editcount', str(widgetdata['editcount']))

		# We update the menu data because this is where we store the 
		# parameters which the user set.
		node.setAttribute('mblogic:menu', json.dumps(widgetdata['menu']))




	########################################################
	def _SaveDrawingParamSet(self, container, groupname, paramlist):
		"""Save a set of drawing parameters. This is for a single set of 
		parameters within the overall parameter container.
		Parameters: container: (XML node) = An XML node to which the new
				data is to be attached.
			groupname: (string) = The name of the parameter set. This will
				be used as the new tag name.
			paramlist: (list) = The list of parameter data.
		"""
		# Get the list of parameter elements.
		grouplist = container.getElementsByTagName(groupname)

		# Check if it exists.
		if len(grouplist) == 0:
			# Create it.
			groupcontainer = self._SVG.createElement(groupname)
			# Add it to the data container.
			container.appendChild(groupcontainer)
		else:
			groupcontainer = grouplist[0]


		# Check if any existing parameters (list elements) exist. 
		for x in groupcontainer.getElementsByTagName('param'):
			groupcontainer.removeChild(x)

		# Add the new list of layers to the parameter container.
		for x in paramlist:
			# Create the XML tag.
			param = self._SVG.createElement('param')
			# Create the data for the tag.
			paramdata = self._SVG.createTextNode(x)
			# Add the data to the XML tag.
			param.appendChild(paramdata)
			# Add the XML tag to the container.
			groupcontainer.appendChild(param)

		


	########################################################
	def _SaveDrawingParams(self, layerslist, alarmzonelist, eventzonelist):
		"""Update the XML with the drawing parameters.
		Parameters: layerslist: (list) = The list of layers which are 
				controlled by the screen control functions.
			alarmzonelist: (list) = The list of alarm zones to monitor.
			eventzonelist: (list) = The list of event zones to monitor.
		"""

		# Find the root SVG tag.
		svgtaglist = self._SVG.getElementsByTagName('svg')
		svgtag = svgtaglist[0]

		# Get the container for overall data. 
		containerlist = svgtag.getElementsByTagName('mblogicdata')

		# Check if the container exists.
		if len(containerlist) == 0:
			# Create it.
			container = self._SVG.createElement('mblogicdata')
			# Add it to the root.
			svgtag.appendChild(container)
		else:
			container = containerlist[0]

		# Add in the layers list data.
		self._SaveDrawingParamSet(container, 'layerlist', layerslist)

		# Add in the alarm zone list data.
		self._SaveDrawingParamSet(container, 'alarmzonelist', alarmzonelist)

		# Add in the event zone list data.
		self._SaveDrawingParamSet(container, 'eventzonelist', eventzonelist)



	########################################################
	def _GetNodeData(self, node):
		"""Get the node data. 
		Parameters: node: (xml node) = An XML node.
		Returns: (string) = The node data.
		"""
		tnodes = node.childNodes
		return tnodes[0].data


	########################################################
	def _GetDrawingParamData(self, container, groupname):
		"""Return the drawing parameters for a single
		type of data.
		Parameters: container: (XML node) = An XML node to which the data is attached.
			groupname: (string) = The name of the parameter set (tag name).
		Returns: (list) = A list of string data with the parameters.
		"""
		# Get the data.
		datalist = []
		groupcon = container.getElementsByTagName(groupname)
		if len(groupcon) > 0:
			params = groupcon[0].getElementsByTagName('param')
			# Get all the parameters.
			datalist = [self._GetNodeData(x) for x in params]

		return datalist


	########################################################
	def GetDrawingParams(self):
		"""Return the drawing parameters saved in the SVG file.
		Returns: (list), (list), (list) = Layer list, alarm zone list, and
			event zone list. These are lists of strings containing the IDs or
			zone tag names respectively.
		"""
		
		# Get the main parameter container.
		containerlist = self._SVG.getElementsByTagName('mblogicdata')

		# Does any data exist yet? This is *not* an error.
		if len(containerlist) == 0:
			return [], [], []

		container = containerlist[0]

		try:
			# Layers.
			layerlist = self._GetDrawingParamData(container, 'layerlist')

			# Alarm zones.
			alarmzonelist = self._GetDrawingParamData(container, 'alarmzonelist')

			# Event zones.
			eventzonelist = self._GetDrawingParamData(container, 'eventzonelist')
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvgdrawingparamdata', {}))

		return layerlist, alarmzonelist, eventzonelist



	########################################################
	def UpdateWidgetSVG(self, newwidgetdata):
		"""Update the XML with the edited widget parameters.
		Parameters: newwidgetdata: (dict) = The updated edit data. 
		"""

		# Go through the list of widget data.
		for node in self._SVGXML:
			# Get the id.
			try:
				widgetid = node.getAttribute('id')
			except:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsvgwidgetid', {}))
			

			try:
				# Save the parameters.
				self._UpdateWidgetData(node, newwidgetdata[widgetid])

			except:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsavewidgetdata', {'id' : widgetid}))



	########################################################
	def UpdateListParams(self, layerslist, alarmzonelist, eventzonelist):
		"""Update the XML with the edited parameters.
		Parameters: layerslist: (list) = The list of layers which are 
				controlled by the screen control functions.
			alarmzonelist: (list) = The list of alarm zones to monitor.
			eventzonelist: (list) = The list of event zones to monitor.
		"""
		# Add the layers and alarm and event zone lists to the drawing.
		try:
			self._SaveDrawingParams(layerslist, alarmzonelist, eventzonelist)
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badsavewidgetdata', {}))




	########################################################
	def GetBareSVGXML(self):
		"""Return the SVG XML as a string. This *excludes* the XML document 
		declaration at the begining of the file, so it should not be used for
		saving just the SVG to disk. 
		"""
		return self._SVG.documentElement


	########################################################
	def GenerateEventHandlers(self, newwidgetdata):
		"""Generate the event handlers for the input widgets. This inserts the
		event handler code directly in the widget.
		Parameters: newwidgetdata: (dict) = The updated edit data. 
		"""
		widgetid = ''
		try:
			for node in self._SVGXML:
				widgetid = ''
				# Get the id.
				widgetid = node.getAttribute('id')
				# Get the widget data.
				widgetdata = newwidgetdata[widgetid]

				# Get the input function definition. This will be a list of
				# strings defining the input event handlers.
				inputfunc = widgetdata['inputfunc']
				# Get the menu data.
				menudata = widgetdata['menu']

				# Are there any for this widget?
				if len(inputfunc) > 0:
					# Add the input hanlders.
					self._AddHandlers(node, inputfunc, menudata)
		except:
			if len(widgetid) > 0:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badinputhandler', {'id' : widgetid}))
			else:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badinputhandlerunkn', {}))



	########################################################
	def _AddHandlers(self, node, inputfunc, menudata):
		"""Add a set of input event handlers to a widget.
		Parameters: node (xml node) = The document node representing the widget.
			inputfunc (list) = A list of dictionaries defining the input event
				handler Javascript functions.
			menudata (list) = A list of dictionaries containing the menu 
				parameter data.
		"""
		# Construct a dictionary from the menu data. This will be used to
		# hold the menu parameters in a form which is easier to substitute 
		# into the event handlers.
		menuparams = dict([(x['param'],x['value']) for x in menudata])

		# Now substitute the data into each event handler, and add it to 
		# the node attribute.
		for handler in inputfunc:
			evhandler = handler['func'] % menuparams
			node.setAttribute(handler['event'], evhandler)




	########################################################
	def GenerateOutputs(self, newwidgetdata):
		"""Generate the output scripting based on the entered parameters.
		Parameters: newwidgetdata: (dict) = The updated edit data. 
		Returns: (string) = A string containing the block of assembled Javascript.
		"""
		outputlist = []
		widgetid = ''

		try:
			for node in self._SVGXML:
				widgetid = ''
				# Get the id.
				widgetid = node.getAttribute('id')

				# Get the widget data.
				widgetdata = newwidgetdata[widgetid]

				# Get the output function definition. This will be a 
				# strings defining the output Javascript code.
				outputfunc = widgetdata['outputfunc']

				# Are there any for this widget?
				if len(outputfunc) > 0:
					# Get the menu data.
					menudata = widgetdata['menu']

					# Construct a dictionary from the menu data. This will be used to
					# hold the menu parameters in a form which is easier to substitute 
					# into the function code.
					# If any of the parameters are arrays (text lists), we need to 
					# encode the data as proper JSON strings so we don't end 
					# up with u'' codes (Python 2.x unicode) in the output.
					menuparams = {}
					for x in menudata:
						mkey = x['param']
						if x['type'] == 'textlist':
							menuparams[mkey] = json.dumps(x['value'])
						else:
							menuparams[mkey] = x['value']

					# Add in the widget ID.
					menuparams['widgetid'] = widgetid
					# Substitute in the data.
					funcout = outputfunc % menuparams
					outputlist.append(funcout)

		except:
			if len(widgetid) > 0:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badoutputscripts', {'id' : widgetid}))
			else:
				raise SVGParseError(ErrorMsgs.Msg.GetMessage('badoutputscriptsunk', {}))

		return '\n\t'.join(outputlist)



	########################################################
	def GenerateReadList(self, newwidgetdata):
		"""Generate the read list from the SVG data, and return it as a list.
		Parameters: newwidgetdata: (dict) = The updated edit data. 
		Returns: (list) = A list of address tags strings.
		"""
		try:
			# Get all the menu data.
			menudata = [x['menu'] for x in newwidgetdata.values()]
			# Flatten the list.
			menu = itertools.chain(*menudata)
			# Get all the tag related values.
			readlist = [x['value'] for x in menu if x['type'] == 'tag']
		except:
			raise SVGParseError(ErrorMsgs.Msg.GetMessage('badreadlist', {}))


		# Remove the duplicates and return the results.
		return list(set(readlist))


##############################################################################


