##############################################################################
# Project: 	mbserver
# Module: 	ModbusRestMsg.py
# Purpose: 	Provides MB-REST base functions.
# Language:	Python 2.5
# Date:		06-Apr-2008.
# Ver.:		08-May-2008.
# Copyright:	2008 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

import xml.parsers.expat

import ModbusDataStrLib

##############################################################################
"""
This module is used for assembling and dissassembling MB-REST messages.
Each method either accepts a set of parameters and constructs a valid
MB-REST message ready for transmission, or it takes a MB-REST
message which has bee received and dissassembles it into its components
so that the contents may be read. 

There are two classes. One class (MBRestServerMessages) is used with servers (slaves),
while the other (MBRestClientMessages) is used with clients (masters). Neither class
implements that actual transmission or receipt of messages, nor do they implement
a Modbus memory structure for storing data.

Public Classes
A) MBRestServerMessages - This must be initialised with 4 integers indicating the 
	maximum number of coils, discrete inputs, holding registers, and input 
	registers. These are used to determine if the address in a client request 
	is out of range.

Public Methods:
For the following: 
TransID = transaction ID (integer), 
TID = transaction ID (string), 
UnitID = unit ID (integer), 
UID = unit ID (string), 
FunctionCode = Modbus function code (integer), 
Func = Modbus function code (string), 
ErrorCode = Modbus error code (integer), 
ExceptionCode = Modbus exception code (integer),
Addr = data table address (integer), 
Qty = Number of consecutive addresses (integer), 
MsgData = data (ASCII string),

A1) MBResponse(TransID, UnitID, FunctionCode, MsgData) - Construct an MB-REST 
	response message. Returns a string containing the XML message.
A2) MBErrorResponse(TransID, UnitID, ErrorCode, ExceptionCode) - Construct a 
	MB-REST error response message. Returns a string containing the XML message.
A3) MBGetRequest(Func, Addr, Qty, TID, UID) - Extract the data from a MB-REST 
	GET request message. This handles reads. Returns a tuple containing 
	TransID, UnitID, FunctionCode, Address, Quantity, exceptioncode.
A4) MBPostRequest(Func, Addr, Qty, TID, UID, Message) 
	- Extract the data from a MB-REST POST request message. This handles writes.
	Returns a tuple containing TransID, UnitID, FunctionCode, Address, 
	MsgData, exceptioncode. For functions 15 and 16, MsgData is actually a tuple
	containing (Quantity, MsgData).


Public Classes:
B) MBRestClientMessages

Public Methods:
For the following:
TransID = Transaction ID (integer)
UnitID = Unit ID (integer)
FunctionCode - Modbus function (integer)
Addr - Data table address (integer)
Qty - Number of consecutive addresses (integer)
MsgData = 'none' - Message data (default of 'none') (ASCII string)
Message - Message data (string)
B1) MBRequest(TransID, UnitID, FunctionCode, Addr, Qty, MsgData = 'none')
	- Make a modbus client request message. Returns a tuple containing the
	URL and an XML document (both strings).
B2) MBResponse(Message) - Extract the data from a server response message.
	Returns a tuple containing the transaction ID (integer), function (integer),
	and data (ASCII string).

======================================================================================
An MB-Rest message consists of two parts, 

URL:

XML:

This library supports the following functions:
1	= Read Coils
2	= Read Discrete Inputs
3	= Read Holding Registers
4	= Read Input Registers
5	= Write Single Coil
6	= Write Single Register
15	= Write Multiple Coils
16	= Write Multiple registers


Modbus Exceptions:
If there is an error in the message, a Modbus exception code is generated.
Modbus exception codes are generated in the following order: 1, 3, 2, 4. When
an exception is found, processing stops there and the code is returned.

Exceptions are defined as followed:
Exception Code 1 (All functions): Function code is not supported.
Exception Code 2 (functions 1, 2, 3, 4): Start address not OK or Start address + qty outputs not OK.
Exception Code 2 (functions 5, 6): Output address not OK.
Exception Code 2 (functions 15, 16): Start address not OK or start address + qty outputs or registers not OK.
Exception Code 3 (functions 1, 2): Qty of inputs, or outputs is not between 1 and 0x07D0.
Exception Code 3 (functions 3, 4): Qty of registers is not between 1 and 0x07D.
Exception Code 3 (function 5): Output value is not 0x0000 or 0xFF00.
Exception Code 3 (function 6): Register value is not between 0x0000 and 0xFFFF.
Exception Code 3 (functions 15, 16): Qty of outputs or registers is not between 1 and 0x07B0.
Exception Code 4 (All functions):An error has occurred during reading or writing an input, output, 
or register. This exception cannot be detected at this point, and so will not be returned.
"""



##############################################################################
# Parse an XML Modbus message.
# Attributes:
# ParseRequest(message) - Takes a string of XML client request message and parses it to extract
# the data. Returns "True" if the last tag in the message was "request" (indicating the end
# of the message was found).
#
# ParseResponse(message) - Takes a string of XML server response message and parses it to extract
# the data. Returns "True" if the last tag in the message was "reponse" (indicating the end
# of the message was found).
#
# GetMsgData() - Returns the message data (string). If none was found, it returns an empty string.
# GetMsgFunction() - Returns the transaction ID and function code (both strings). Returns empty
# strings if either is not found.
# 
class RestXMLParser:


	########################################################
	# Called when an element's start tag is encountered.
	def _StartElement(self, name, attrs):
		self._CurrentElement = name
		if (name == self._OuterTag):
			self._FoundData = True

	########################################################
	# Called when an element's end tag is encountered.
	def _EndElement(self, name):
		self._CurrentElement = None
		if (name == self._OuterTag):
			self._FoundData = False
			self._LastEndTag = name

	########################################################
	# Called when element data is encountered.
	def _ElementData(self, data):
		# Ignore data that is not within the defined tags.
		if self._FoundData:
			# Ignore text that is not between tags.
			if self._CurrentElement:
				self._DataDict[self._CurrentElement] = data


	########################################################
	# This must be re-initialised for each XML message or
	# else xpat will choke on the *second* message.
	def __init__(self):
		self._DataDict = {}
		self._CurrentElement = None
		self._LastEndTag = None
		self._OuterTag = ''
		self._FoundData = False

		self._Parser = xml.parsers.expat.ParserCreate()
		self._Parser.StartElementHandler = self._StartElement
		self._Parser.EndElementHandler = self._EndElement
		self._Parser.CharacterDataHandler = self._ElementData


	########################################################
	# Call this to parse the XML Request data. 
	# This is for REQUEST messages (received by server).
	# Parameters: 'message' is expected to be a string containing XML. 
	# Returns True if no parsing errors were found.
	# This does not check the data for errors.
	def ParseRequest(self, message):
		self._DataDict = {}
		self._LastEndTag = None
		self._CurrentElement = None
		self._OuterTag = 'request'
		try:
			self._Parser.Parse(message.strip(), 1)
		except:
			pass
		return self._LastEndTag == 'request'


	########################################################
	# Call this to parse the XML Response data. 
	# This is for RESPONSE messages (received by client).
	# Parameters: 'message' is expected to be a string containing XML. 
	# Returns True if no parsing errors were found.
	# This does not check the data for errors.
	def ParseResponse(self, message):
		self._DataDict = {}
		self._LastEndTag = None
		self._CurrentElement = None
		self._OuterTag = 'response'
		try:
			self._Parser.Parse(message.strip(), 1)
		except:
			pass
		return self._LastEndTag == 'response'


	########################################################
	# Return a string containing the message data. Returns an
	# empty string if no data was present.
	def GetMsgData(self):
		try:
			data = self._DataDict['msgdata']
		except:
			data = ''
		return data

	########################################################
	# Return a tuple containing the transaction ID, and the function.
	# These are contained in strings.
	# Returns an pair of empty strings if no data was present.
	def GetMsgFunction(self):
		try:
			return self._DataDict['transactionid'], self._DataDict['functioncode']
		except:
			return '', ''


##############################################################################


##############################################################################
# Class to assemble or extract data from Modbus Rest server messages.
# This class must be initialised with the maximum permitted addresses for
# coils, discrete inputs, holding registers, and input registers. 
# This is necessary so requests for attempts to access addresses which are
# out of range can be detected and an exception generated.
#
class MBRestServerMessages:
	########################################################
	# Initialise the limits to the data tables.
	def __init__(self, maxcoils, maxdiscretes, maxholdingreg, maxinputreg):
		# A dictionary is used to hold the address limits. The dictionary key
		# is the Modbus function code, and the data is the address limit.
		self._addrlimits = {1 : maxcoils, 2 : maxdiscretes, 3 : maxholdingreg,
		4 : maxinputreg, 5 : maxcoils, 6 : maxholdingreg, 15 : maxcoils, 16 : maxholdingreg }

		# A dictionary is used to hold the constants for the protocol addressing range.
		# These are the  maximum number of elements that can be read or written to at one
		# time without exceeding the protocol limit. Exceeding these limits results in 
		# a Modbus exception 3.
		self._protocollimits = {1 : 0x07D0, 2 : 0x07D0, # Max coils that can be read at once.
					3 : 0x07D, 4 : 0x07D,	# Max registers that can be read at once.
					5 : 0x0, 6 : 0x0,	# N/A for 5 or 6.
					15 : 0x07B0, 		# Max coils that can be written at once.
					16 : 0x07B}		# Max registers that can be written at once.

		self._ServerResponse = """
			<?xml version="1.0" encoding="utf-8" ?>
			<response status="%s">
				<transactionid>%d</transactionid>
				<protocol>modbusrest_v1.0</protocol>
				<unitid>%d</unitid>
				<functioncode>%d</functioncode>
				<msgdata>%s</msgdata>
			</response>""" 

	########################################################
	# Construct a MB-REST response message.
	# TransID (integer) = Transaction ID. This must match the value used by the client.
	# UnitID (integer) = Unit ID.
	# FunctionCode (integer) = Modbus/TCP function code.
	# MsgData (ASCII string) = The data to be returned.
	# Returns a string containing the XML response. 
	def MBResponse(self, TransID, UnitID, FunctionCode, MsgData):

		return self._ServerResponse % ('ok', TransID, UnitID, FunctionCode, MsgData)

	########################################################
	# Construct a MB-REST error response message.
	# TransID (integer) = Transaction ID. This must match the value used by the client.
	# UnitID (integer) = Unit ID.
	# ErrorCode (integer) = Modbus/TCP error code.
	# ExceptionCode (integer) = Modbus/TCP exception code.
	# Returns a string containing the XML response. 
	def MBErrorResponse(self, TransID, UnitID, ErrorCode, ExceptionCode):

		return self._ServerResponse % ('fail', TransID, UnitID, ErrorCode, ExceptionCode)


	########################################################
	# Check for address limits.
	# Returns True if address + quantity is within the max limit.
	def _AddrLimitsOK(self, Addr, Qty, Func):
		return ((Addr + Qty - 1) <= self._addrlimits[Func])

	
	########################################################
	# Try to validate the message parameters contained in the URL.
	# Parameters: 
	# Func (string) = The Modbus function code. 
	# Addr (string) = The Modbus memory address.
	# Qty (string) = The quantity of addresses. If blank a default of 1 is assumed.
	# TID (string) = Transaction ID. If blank a default of -1 is assumed.
	# UID (string) = UnitID. If blank a default of -1 is assumed.
	# Return values: 
	# TransID (integer) = Transaction ID.
	# UnitID (integer) = Unit ID.
	# Function (integer) = Function or error code.
	# Start (integer) = First address in request.
	# 
	def _ValidateURLParams(self, Func, Addr, Qty, TID, UID):
		# Convert the function code and address to integer.
		# Valid values for these paraemters are mandatory.
		try:
			FunctionCode = int(Func)
			Address = int(Addr)
		except:	# Message cannot be decoded properly.
			FunctionCode = None
			Address = None


		# Check for optional parameters which may be blank.
		# If no quantity is specified, the default is 1.
		if (Qty == ''):
			Quantity = 1
		else:	# Try to convert to integer.
			try:
				Quantity = int(Qty)
			except:
				Quantity = None

		# Using a transaction ID is optional. If none is specified, then
		# return a default of -1
		if (TID == ''):
			TransID = -1
		else:	# Try to convert to integer.
			try:
				TransID =  int(TID)
			except:
				TransID = None

		# Using a unit ID is optional. If none is specified, then
		# return a default of -1
		if (UID == ''):
			UnitID = -1
		else:	# Try to convert to integer.
			try:
				UnitID = int(UID)
			except:
				UnitID = None

		return FunctionCode, Address, Quantity, TransID, UnitID


	########################################################
	# Extract the data from a MB-REST GET request message.
	# Parameters: 
	# Func (string) = The Modbus function code. 
	# Addr (string) = The Modbus memory address.
	# Qty (string) = The quantity of addresses. If blank a default of 1 is assumed.
	# TID (string) = Transaction ID. If blank a default of -1 is assumed.
	# UID (string) = UnitID. If blank a default of -1 is assumed.
	# Return values: 
	# TransID (integer) = Transaction ID.
	# UnitID (integer) = Unit ID.
	# Function (integer) = Function or error code.
	# Start (integer) = First address in request.
	# data = Message data. For functions 1, 2, 3, 4 this is an integer representing the quantity
	#	of requested inputs, coils or registers. In the case of exception 1 (unsupported 
	#	function), this will be an ASCII string containing zeros.
	# exceptioncode (integer) = Modbus exception code. This is 0 if there is no error.
	# If a message cannot be decoded, zeros will be returned for all fields.
	#
	def MBGetRequest(self, Func, Addr, Qty, TID, UID):

		# Check the parameters which represent the URL string.
		FunctionCode, Address, Quantity, TransID, UnitID = self._ValidateURLParams(Func, Addr, Qty, TID, UID)

		# Check if the values could be read without error.
		if ((FunctionCode == None) or (Address == None) or (Quantity == None) or (TransID == None) or (UnitID == None)):
			# Set some initial default values for these.
			TransID = -1
			UnitID = -1
			FunctionCode = 0
			Address = 0
			data = '0000'
			exceptioncode = 0
			return TransID, UnitID, FunctionCode, Address, data, exceptioncode


		# At this point, the parameters have all be checked to see if they can be used.
		# Now validate the data according to the requirements of each function.
		if FunctionCode in (1, 2, 3, 4):
			exceptioncode = 0	# Default exception code.
			MsgData = ''		# No XML data expected.

			# Check for address limits.
			if not self._AddrLimitsOK(Address, Quantity, FunctionCode):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 2			# Exception code.
			# Check for quantity limits.
			elif (Quantity < 1) or (Quantity > self._protocollimits[FunctionCode]):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3			# Exception code.

			return TransID, UnitID, FunctionCode, Address, Quantity, exceptioncode


		# Function code is not supported.
		else:
			# This error code needs special treatment in case of bad function
			# codes that are very large.
			FunctionCode = (FunctionCode & 0xff) | 0x80	# Create error code.
			exceptioncode = 1		# Exception code.
			return TransID, UnitID, FunctionCode, 0, '0000', exceptioncode


	########################################################
	# Extract the data from a MB-REST POST request message.
	# This handles POST requests only, and so is only valid
	# for requests which write data. Requests to read data
	# (e.g. 1, 2, 3, 4) will be considered an exception.
	# Parameters: 
	# Func (string) = The Modbus function code. 
	# Addr (string) = The Modbus memory address.
	# Qty (string) = The quantity of addresses. If blank a default of 1 is assumed.
	# TID (string) = Transaction ID. If blank a default of -1 is assumed.
	# UID (string) = UnitID. If blank a default of -1 is assumed.
	# Message = This is a string containing the HTTP header string as received. 
	# Return values: 
	# TransID (integer) = Transaction ID.
	# UnitID (integer) = Unit ID.
	# Function (integer) = Function or error code.
	# Start (integer) = First address in request.
	# data = Message data. For functions 5 or 6, this is an ASCII string containing
	#	the coil or register data. For 15 or 16 this is a tuple containing an integer with the 
	#	number of coils or registers, and an ASCII string containing the data. In the case of
	#	exception 1 (unsupported function), this will be an ASCII string containing zeros.
	# exceptioncode (integer) = Modbus exception code. This is 0 if there is no error.
	# If a message cannot be decoded, zeros will be returned for all fields.
	#
	def MBPostRequest(self, Func, Addr, Qty, TID, UID, Message):

		# Check the parameters which represent the URL string.
		FunctionCode, Address, Quantity, TransID, UnitID = self._ValidateURLParams(Func, Addr, Qty, TID, UID)


		# Check if the values could be read without error.
		if ((FunctionCode == None) or (Address == None) or (Quantity == None) or (TransID == None) or (UnitID == None)):
			# Set some initial default values for these.
			TransID = -1
			UnitID = -1
			FunctionCode = 0
			Address = 0
			data = '0000'
			exceptioncode = 0
			return TransID, UnitID, FunctionCode, Address, data, exceptioncode

		# Try to parse the XML message to get just the data portion of the message.
		XMLParser = RestXMLParser()
		if XMLParser.ParseRequest(Message):
			MsgData =  XMLParser.GetMsgData()
		else:
			MsgData =  ''


		# At this point, the parameters have all be checked to see if they can be used.
		# Now validate the data according to the requirements of each function.
		if (FunctionCode == 5):

			exceptioncode = 0	# Default exception code.

			# Check for address limits.
			if not self._AddrLimitsOK(Address, Quantity, FunctionCode):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 2			# Exception code.

			# Check if request data is valid.
			if MsgData not in ('0000', 'ff00', 'fF00', 'Ff00', 'FF00'):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.

			return TransID, UnitID, FunctionCode, Address, MsgData, exceptioncode

		elif (FunctionCode == 6):

			exceptioncode = 0	# Default exception code.

			# Check for address limits.
			if not self._AddrLimitsOK(Address, Quantity, FunctionCode):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 2			# Exception code.

			# Check if message length is OK.
			if (len(MsgData) != 4):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			else:

				# Try to convert to binary string. If no good, then
				# the string is not valid hexadecimal data.
				try:
					temp = ModbusDataStrLib.hex2bin(MsgData)
				except:
					FunctionCode = FunctionCode + 128	# Create error code.
					exceptioncode = 3		# Exception code.
			
			return TransID, UnitID, FunctionCode, Address, MsgData, exceptioncode
		
		elif (FunctionCode == 15):

			exceptioncode = 0	# Default exception code.

			# Check for address limits.
			if not self._AddrLimitsOK(Address, Quantity, FunctionCode):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 2			# Exception code.
			# Qty of outputs is out of range.
			elif ((Quantity < 1) or (Quantity > self._protocollimits[FunctionCode])):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty for coils exceeds the amount of data sent.
			elif (Quantity > len(MsgData)):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3			# Exception code.
			# Qty for coils is less than the amount of data sent.
			elif (Quantity < (len(MsgData) - 8)):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty for coils exceeds amount of data sent.
			# Try to convert to binary string. If no good, then
			# the string is not valid hexadecimal data.
			# Length must also be a multiple of 8.
			else:
				try:
					temp = ModbusDataStrLib.bininversor(MsgData)
				except:
					FunctionCode = FunctionCode + 128	# Create error code.
					exceptioncode = 3		# Exception code.


			return TransID, UnitID, FunctionCode, Address, (Quantity, MsgData), exceptioncode

		elif (FunctionCode == 16):

			exceptioncode = 0	# Default exception code.

			# Check for address limits.
			if not self._AddrLimitsOK(Address, Quantity, FunctionCode):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 2			# Exception code.
			# Qty of registers is out of range.
			elif ((Quantity < 1) or (Quantity > self._protocollimits[FunctionCode])):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Qty does not match the amount of data sent.
			elif ((Quantity * 4) != len(MsgData)):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			# Check if message length is OK. Length must be a multiple of 4.
			elif ((len(MsgData) % 4) != 0):
				FunctionCode = FunctionCode + 128	# Create error code.
				exceptioncode = 3		# Exception code.
			else:
				# Try to convert to binary string. If no good, then
				# the string is not valid hexadecimal data.
				try:
					temp = ModbusDataStrLib.hex2bin(MsgData)
				except:
					FunctionCode = FunctionCode + 128	# Create error code.
					exceptioncode = 3		# Exception code.

			return TransID, UnitID, FunctionCode, Address, (Quantity, MsgData), exceptioncode

		# Function code is not supported.
		else:
			# This error code needs special treatment in case of bad function
			# codes that are very large.
			FunctionCode = (FunctionCode & 0xff) | 0x80	# Create error code.
			exceptioncode = 1		# Exception code.
			return TransID, UnitID, FunctionCode, 0, '0000', exceptioncode



##############################################################################
# Class to assemble or extract data from MB-REST client messages.
#
class MBRestClientMessages:

	def __init__(self):
		pass

	########################################################
	# Make a modbus client request message.
	# Parameters:
	# TransID (integer) = Transaction ID.
	# UnitID (integer) = Unit ID.
	# FunctionCode (integer) = Function code.
	# Addr (integer) = Data address.
	# Qty (integer) = Number of addresses to read or write.
	# MsgData (ASCII string) = Data in MB-REST ASCII string format. Valid data is required 
	#	for functions 5, 6, 15, and 16. For 1, 2, 3, and 4, this parameter is optional.
	# Returns a tuple containing two strings. The first is the URL, and second is the XML 
	# request (when applicable). 
	def MBRequest(self, TransID, UnitID, FunctionCode, Addr, Qty, MsgData = 'none'):

		if FunctionCode in (1, 2, 3, 4):
			return '%d/%d?qty=%d&tid=%d&uid=%d' % (FunctionCode, Addr, Qty, TransID, UnitID), ''
		elif FunctionCode in (5, 6, 15, 16):
			return '%d/%d?qty=%d&tid=%d&uid=%d' % (FunctionCode, Addr, Qty, TransID, UnitID), \
			"""
			<?xml version="1.0" encoding="utf-8" ?>
			<request>
				<protocol>modbusrest_v1.0</protocol>
				<msgdata>%s</msgdata>
			</request>""" % (MsgData)
		else:
			return '', ''

	########################################################
	# Extract the data from a server response message.
	# Parameters: Message = This is a string containing the raw binary message as received.
	# Return values: 
	# TransID (integer) = Transaction ID.
	# Function (integer) = Function or error code.
	# Data or Exception Code = Message data. For a successful request, 
	#	this is an ASCII string containing the coil or register data. 
	#	For errors, this is an integer indicating the Modbus exception code.
	# If a message cannot be decoded, zeros will be returned for all fields.
	#
	def MBResponse(self, Message):

		# Set some initial default values for these.
		TransID = 0
		Function = 0
		MsgData = '0000'
		exceptioncode = 0

		XMLParser = RestXMLParser()

		# Try to parse the XML message.
		try:
			Finished = XMLParser.ParseResponse(Message)

			# Parser did not find the closing tag for the response.
			if (not Finished):
				return (TransID, Function, MsgData)

			TransID, Function = XMLParser.GetMsgFunction()
			MsgData = XMLParser.GetMsgData()

		except:	# The message cannot be parsed properly.
			return (TransID, Function, MsgData)

		# Try to convert TransID, Function to integer.
		try:
			TID = int(TransID)
			Func = int(Function)
		except:
			return (TransID, Function, MsgData)


		# Everything looks like it is OK.
		# MsgData is simply returned as is.
		return (TID, Func, MsgData)


##############################################################################

