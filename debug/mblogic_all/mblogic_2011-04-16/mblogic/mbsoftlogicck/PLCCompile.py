##############################################################################
# Project: 	MBLogic
# Module: 	PLCCompile.py
# Purpose: 	Generic compiler for a soft logic system.
# Language:	Python 2.5
# Date:		16-Dec-2007.
# Ver:		23-Aug-2010
# Author:	M. Griffin.
# Copyright:	2007-2010 - Michael Griffin   <m.os.griffin@gmail.com>
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
	Read in the PLC program and compile it to an executable code object.
"""

# Error during instruction parsing.
CompileErrMsg = 'Error in %s network %s - %s for %s'
# Compiler error messages.
ErrMsgs = {'notfound' : 'unknown instruction',
	'badparam' : 'missing or incorrect parameters',
	'nosubr' : 'referenced subroutine does not exist'
}



############################################################

class PLCCompiler:
	"""Compile IL code into executable Python code. 
	"""

	########################################################
	def __init__(self, instlist, instdatatable, filename):
		"""Expects a list of instruction definition dictionaries defining 
		the valid PLC instructions. 
		instlist (list) = A list of instruction definitions.
		instdatatable (dict) = An empty dictionary. This is used by some 
			instructions to store instruction data.
		filename (string) = The name of the file containing 
			the soft logic program IL.
		"""

		# The program file name.
		self._FileName = filename
		self._InstrDataTable = instdatatable

		# Used to parse out the IL syntax.
		self._SourceAnalyser = SourceAnalyse(instlist)

		self._CodeCompiler = None

		# If True, dump the Python source.
		self._DumpSource = False


	########################################################
	def ReadInFile(self):
		"""Read in the PLC source file. The file name used is the one
		set during initialisation.
		"""
		progsource = SourceContainer(self._FileName)
		progsource.ReadInFile()
		# Set the source file data.
		self._SourceAnalyser.SetSourceList(progsource.GetProgramCopy())


	########################################################
	def WriteOutFile(self):
		"""Write out the PLC source file. The file name used is the same as
		was set when the file was read.
		"""
		sourcelist = self._SourceAnalyser.GetSourceList()
		progsource = SourceContainer(self._FileName)
		progsource.SetProgramCopy(sourcelist)
		progsource.WriteOutFile()


	########################################################
	def SetProgramCopy(self, iltext):
		"""Accept a list of text containing the IL program. This allows the
		program souce to be set without reading it from a file.
		Parameters: iltext (list) = A list of strings containing the
			soft logic program IL. There should be one line of text
			per list element.
		"""
		self._SourceAnalyser.SetSourceList(iltext)


	########################################################
	def GetProgramCopy(self):
		"""Return a copy (in text) of the soft logic program. This returns
		a list with one line of source per list element.
		"""
		return self._SourceAnalyser.GetSourceList()


	########################################################
	def MergeSourceBlock(self, subname, ilsource):
		"""This merges in a subroutine of IL source. If the subroutine 
		does not already exist, it is added. If it does exist, it replaces
		the original.
		Parameters: subname (string) = Name of subroutine.
		ilsource (list) = A list of strings containing the subroutine 
			source code, with one line per subroutine.
		"""
		self._SourceAnalyser.MergeSourceBlock(subname, ilsource)


	########################################################
	def AddSourceBlock(self, ilsource):
		"""This adds a subroutine of IL source. This does not check
		to see if the subroutine already exists.
		Parameters: ilsource (list) = A list of strings containing the 
			subroutine source code, with one line per subroutine.
		"""
		self._SourceAnalyser.AddSourceBlock(ilsource)


	########################################################
	def DeleteSourceBlock(self, delsubname):
		"""This deletes a subroutine of IL source. If the subroutine 
		does not exist, the result is ignored.
		Parameters: delsubname (string) = Name of subroutine.
		"""
		self._SourceAnalyser.DeleteSourceBlock(delsubname)


	########################################################
	def GetProgramBlocks(self):
		"""Return a copy (in text) of the soft logic program broken down 
		into subroutines. The subroutine names are used as keys, and lists
		of the IL source are used as values. There is one line of source 
		per list element.
		"""
		return self._SourceAnalyser.GetProgramBlocks()



	########################################################
	def GetCompileErrors(self):
		"""Returns a list of compile error messages.
		"""
		return self._SourceAnalyser.GetCompileErrors()


	########################################################
	def GetProgramSyntaxResults(self):
		"""Returns a dictionary of references to the instruction definition 
		list. This is in the order that was compiled. This may
		be further processed by other modules for such things as ladder
		display.
		"""
		return self._SourceAnalyser.GetProgramSyntaxResults()


	########################################################
	def SetDumpSourceOn(self):
		"""Enables dumping of Python source code of PLC program to be 
		dumped to a text file. This is sometimes useful for debugging.
		"""
		self._DumpSource = True
		print('\n*** Source dump mode is on ***\n')

	########################################################
	def SetErrorPrintOn(self):
		"""Enable the direct printing of compile errors to the console.
		"""
		self._SourceAnalyser.SetErrorPrintOn()



	########################################################
	# Compile the PLC program.
	def CompileProgram(self):
		"""Compile the current program.
		"""

		# Convert the raw source into a parsed syntax list.
		self._SourceAnalyser.AnalyseProgram()
		# Check for errors which are apparent only when reviewing the
		# entire programming.
		self._SourceAnalyser.CheckCalls()
		# Get any error messages.
		self._PLCSyntax = self._SourceAnalyser.GetProgramSyntaxResults()


		# Compile the program syntax into an executable code block.
		self._CodeCompiler = CompileCode(self._PLCSyntax, self._InstrDataTable)
		codeobj = self._CodeCompiler.CompileSource()


		if (self._DumpSource):
			progsource = SourceContainer(self._FileName)
			progsource.SetProgramCopy(self._SourceAnalyser.GetSourceList())
			progsource.WriteDumpFile(self._CodeCompiler.GetSource())


		return (codeobj, self._SourceAnalyser.GetInstrCount(), 
				self._SourceAnalyser.HasErrors())


############################################################


############################################################
class SourceContainer:
	"""Container object for unparsed source. This should only be created as 
	needed to read and write files.
	"""

	########################################################
	def __init__(self, filename):
		"""
		Parameters: filename (string) = The name of the file containing 
			the soft logic program IL.
		"""
		self._PLCSourceList = []
		self._FileName = filename


	########################################################
	def ReadInFile(self):
		"""Read in the PLC source file. 
		Stores the resulting data in a list.
		"""
		PLCSourceFile = open(self._FileName, 'r', -1)
		self._PLCSourceList = PLCSourceFile.readlines(-1)
		PLCSourceFile.close()


	########################################################
	def WriteOutFile(self):
		"""Write out the PLC source to a file. Expects a file name.
		Writes the the current source list to the file, and then
		closes the file.
		"""
		PLCSourceFile = open(self._FileName, 'w', -1)
		PLCSourceFile.writelines(self._PLCSourceList)
		PLCSourceFile.flush()
		PLCSourceFile.close()


	########################################################
	def GetProgramCopy(self):
		"""Return a copy (in text) of the soft logic program. This returns
		a list with one line of source per list element.
		"""
		return self._PLCSourceList


	########################################################
	def SetProgramCopy(self, sourcelist):
		"""Set a copy (in text) of the soft logic program. This expects
		a list with one line of source per list element
		"""
		self._PLCSourceList = sourcelist


	########################################################
	def WriteDumpFile(self, sourcedata):
		"""Write out a file containing the Python source for the PLC 
		program. The data to be written is expected to be string.
		"""
		PLCSourceFile = open(self._FileName + '.dump', 'w', -1)
		PLCSourceFile.write(sourcedata)
		PLCSourceFile.close()


############################################################



############################################################
class SourceAnalyse:
	"""This reads in the source for the soft logic program and breaks it 
	down into basic blocks.
	"""

	########################################################
	def __init__(self, instlist):
		"""
		instlist (list) = A list of instruction definitions.
		"""
		# Source code list.
		self._PLCSourceList = []

		# Definitions of instructions. 
		self._PLCInst = self._AssembleInstrDict(instlist)


		# Program syntax description. As compiler checks each instruction,
		# it adds it to a formatted list which can be processed later for
		# such purposes as creating ladder displays.
		self._PLCSyntax = {}

		# This is used to save the original text divided up into 
		# subroutines. This allows us to merge changed subroutines
		# back into the source file. 
		self._SourceBlocks = {}

		self._CompileErrors = 0		# Number of compile errors.
		self._CompileMsgs = []	# Error message log.
		self._ErrorPrintEnabled = False		# Enable printing errors.

		self._InstrCount = 0	# Number of instructions compiled.

		# This an ordered list of the parameter keys. These keys
		# are used to hold the parameters in the correct order
		# when they are passed to other routines.
		# This allows the compiler to handle a number of parameters up
		# to the value in self._MaxParamCount. This value has to take into 
		# account the number of symbols in a MATH instruction. 
		self._MaxParamCount = 50
		self._InstrParamList = ['inparam%s' % pcounter for pcounter in range(1,self._MaxParamCount + 1)]


	########################################################
	def ReportError(self, errcode, block, rung, instrstr):
		""" Report an error to the user, and store the message in
		a buffer for later status reporting.
		Parameters: errcode (string) = The error code.
			block (string) = The code block (subroutine) where the
				error was found.
			rung (string) = The rung (network) where the error was found.
			instrstr (string) = The instruction with the error.
		"""
		errormsg = CompileErrMsg % (block.strip(), rung, ErrMsgs[errcode], instrstr)
		self._CompileMsgs.append(errormsg)
		if (self._ErrorPrintEnabled):
			print(errormsg)


	########################################################
	def SetErrorPrintOn(self):
		"""Enable the direct printing of compile errors to the console.
		"""
		self._ErrorPrintEnabled = True


	########################################################
	def GetProgramSyntaxResults(self):
		"""Returns a dictionary of references to the instruction definition 
		list. This is in the order that was compiled. This may
		be further processed by other modules for such things as ladder
		display.
		"""
		return self._PLCSyntax

	########################################################
	def GetCompileErrors(self):
		"""Returns a list of compile error messages.
		"""
		return self._CompileMsgs

	########################################################
	def HasErrors(self):
		"""Returns (boolean) = True if any compile errors were
			encountered.
		"""
		return (len(self._CompileMsgs) > 0)


	########################################################
	def GetInstrCount(self):
		"""Returns (int) = The number of IL instructions compiled.
		"""
		return self._InstrCount

	############################################################
	def _AssembleInstrDict(self, InstrList):
		"""Assemble an instruction dictionary from a list of instruction
		definition dictionaries passed as a parameter.
		Return this instruction dictionary to be used in compiling PLC 
		programs. Instructions are stored in a dictionary where the 
		instruction code (e.g. 'AND') is the key, and the instruction 
		definition is the data. Instruction definitions are stored in a list 
		associated with each instruction code. The list allows the storage
		of duplicate codes which are distinguished only by their parameter types. 
		"""
		InstrDict = {}
		for Instruction in InstrList:
			PLCInstrCode = Instruction['opcode']
			# Check to see if an instruction of the same name already exists.
			if (InstrDict.get(PLCInstrCode) == None):	# No?
				# Create a new dictionary entry for it.
				InstrDict[PLCInstrCode] = [Instruction,]
			else:	# Already an instruction by that name.
				# Append the new copy to the end of the list for that code.
				InstrDict[PLCInstrCode].append(Instruction)
		return InstrDict


	########################################################
	def SetSourceList(self, sourcelist):
		"""Set the source code for the current IL program.
		Parameters: sourcelist (list) = The program with one line of
			IL source per list element.
		"""
		self._PLCSourceList = sourcelist


	########################################################
	def GetSourceList(self):
		"""Get the source code for the current IL program. This returns
		a list of IL text.
		"""
		return self._PLCSourceList


	########################################################
	def SetProgramBlocks(self, sourceblocks):
		"""Import a dictionary containing an IL program broken up
		into subroutines (blocks). This allows a program to be
		copied without having to read it from disk and parse
		out each line. 
		Parameters: sourceblocks (dict) = Subroutine names are keys,
		and lists of IL source are values. There is one line of source 
		per list element.
		"""
		self._SourceBlocks = sourceblocks


	########################################################
	def GetProgramBlocks(self):
		"""Return a copy (in text) of the soft logic program broken down 
		into subroutines. The subroutine names are used as keys, and lists
		of the IL source are used as values. There is one line of source 
		per list element.
		"""
		return self._SourceBlocks


	########################################################
	def MergeSourceBlock(self, newsubname, ilsource):
		"""This merges in a subroutine of IL source. If the subroutine 
		does not already exist, it is added. If it does exist, it replaces
		the original.
		Parameters: newsubname (string) = Name of subroutine.
		ilsource (list) = A list of strings containing the subroutine 
			source code, with one line per subroutine.
		"""

		sourcelist = []

		# Merge in the edited block, replacing the existing one.
		self._SourceBlocks[newsubname] = ilsource

		# Get the main program first.
		sourcelist.extend(self._SourceBlocks['main'])

		# Repeat this for the rest of the subroutines.
		for subname, sublist in self._SourceBlocks.items():
			if (subname != 'main'):
				sourcelist.extend(sublist)

		# This now becomes the new list of IL source.
		self._PLCSourceList = sourcelist


	########################################################
	def AddSourceBlock(self, ilsource):
		"""This adds a subroutine of IL source. This does not check
		to see if the subroutine already exists.
		Parameters: ilsource (list) = A list of strings containing the 
			subroutine source code, with one line per subroutine.
		"""

		sourcelist = []

		# Get the main program first.
		sourcelist.extend(self._SourceBlocks['main'])

		# Repeat this for the rest of the subroutines.
		for subname, sublist in self._SourceBlocks.items():
			if (subname != 'main'):
				sourcelist.extend(sublist)

		# Add in the new subroutine.
		sourcelist.extend(ilsource)

		# This now becomes the new list of IL source.
		self._PLCSourceList = sourcelist


	########################################################
	def DeleteSourceBlock(self, delsubnames):
		"""This deletes subroutines of IL source. It will accept multiple
		subroutines in a list. If any of the subroutines do not exist, 
		they are ignored.
		Parameters: delsubnames (list) = List of names of subroutines.
		"""

		sourcelist = []

		# If we are deleting the main routine, then we need to substitute
		# in a blank line.
		if ('main' in delsubnames):
			self._SourceBlocks['main'] = ['']

		# Get the main program first.
		else:
			sourcelist.extend(self._SourceBlocks['main'])

		# Add in the rest of the subroutines.
		for subname, sublist in self._SourceBlocks.items():
			if (subname != 'main') and (subname not in delsubnames):
				sourcelist.extend(sublist)

		# This now becomes the new list of IL source.
		self._PLCSourceList = sourcelist


	########################################################
	def _ExtractParams(self, inst):
		"""Extract the parameters from the instruction string.
		Parameters: inst (string) = A line of IL source code from the program.
		Returns: instruction (string) = The IL instruction op code.
			paramdict (dict) = The parameters as a dictionary where 
				the keys are numbered as 'inparam1', 'inparam2', etc.
			paramstr (string) = The IL instruction parameters as a string,
				which has been reformatted to remove excess leading
				or trailing spaces.
		"""
		# extract the instruction code and parameters.
		codeline = inst.split(None)
		instruction = codeline[0]
		

		# Separate out the parameters and trim off leading and trailing blanks.
		params = [x.strip() for x in codeline[1:]]
		# Create a new reformatted string with the parameters for display purposes.
		paramstr = ' '.join(params)
		# Put the parameters into a dictionary for validation. 
		paramdict = dict([('inparam%s' % y, x) for x,y in zip(params, range(1, len(params) + 1))])


		return instruction, paramdict, paramstr



	########################################################
	def _FindInstruction(self, instruction, paramdict):
		"""Find the correct version of the instruction from several
		similar alternatives.
		Parameters: instruction (string) = The instruction op code.
			paramdict (dict) = The parameters as a dictionary where 
				the keys are numbered as 'inparam1', 'inparam2', etc.
		Returns: InstrDef (dict) = A dictionary containing a complex set of 
				data which defines the instruction found. (Or None
				if the instruction was not found).
			validparams (dict) = The validated parameters returned from
				the instruction validator. (Or None
				if the instruction was not found).
			originalparams (dict) = The "original" parameters returned
				from the instruction validator. This may be
				modified as compared to the actual original parameters.
				(Or None if the instruction was not found).
			paramlist (list) = The parameters returned as a list of strings.
				This includes adding in implied optional parameters, and
				assembling math equations into a single string.
			errorcode (string) = An error code if the instruction op code 
				was not found or if the parameters did not match. 
		"""

		# Look up the instruction and get the information about that instruction.
		# This will be a list of instructions with the appropriate op-code. This
		# permits having multiple instructions with the same name that are 
		# differentiated by different parameter types.
		try:
			InstrList = self._PLCInst[instruction]
		except:
			# Instruction was not found in the dictionary.
			return None, None, None, None, 'notfound'

		# Get the number of parameters. paramdict may be modified
		# while searching for the correct version of the instruction.
		paramcount = len(paramdict)

		# There may be more than one instruction with the same mnemonic code.
		# The correct one must be inferred from the parameters which it accepts.
		# Search through the list of objects to find one where the parameters
		# expected matches the ones present in this instance.
		validparams = {}
		for InstrDef in InstrList:
			# First, check if the parameter count is correct.
			if (paramcount <= InstrDef['params']) or (InstrDef['params'] < 0):
				# Next, check the parameters.
				validator = InstrDef['validator']
				result, validparams, originalparams, paramlist = validator(paramdict)

				if result:
					return InstrDef, validparams, originalparams, paramlist, ''

		# None of the parameters matched.
		return None, None, None, None, 'badparam'


	########################################################
	def _AddInstr(self, plcsource, paramstr, originalparams, origparamlist, 
				validparams, instrdef, sbr, rung):
		"""Add one instruction to the syntax list.
		Parameters:
			plcsource (string) = Original IL source string.
			paramstr (string) = Original parameters for display.
			originalparams (dict) = Original unvalidated parameters.
			origparamlist (list) = originalparams as a list (in order).
			validparams (dict) = Validated parameters.
			instrdef (dict) = Dictionary with instruction definition data.
			sbr (string) = Subroutine name (for error reporting).
			rung (string) = Rung number (for error reporting).
		"""
		return {'paramstr' : paramstr,
			'plcsource' : plcsource,
			'pycode' : '',
			'validparams' : validparams,
			'originalparams' : originalparams,
			'origparamlist' : origparamlist,
			'instrdef' : instrdef,
			'sbr' : sbr,
			'rung' : rung
			}


	########################################################
	def AnalyseProgram(self):
		"""Break the program down into subroutines.
		"""
		currentblock = 'main'	# The main program is the default.
		currentrung = 0		# Counter for rungs.
		rungref = '0'		# What the user called the rung.
		self._InstrCount = 0	# Number of instructions compiled.
		sourcecount = 0		# Lines of source processed.
		self._CompileErrors = 0	# Reset compile errors counter.

		# The default starting block is main.
		self._PLCSyntax = {}
		self._PLCSyntax[currentblock] = []
		self._PLCSyntax[currentblock].append([])
		# Initialise the starting block of IL source.
		self._SourceBlocks = {}
		self._SourceBlocks[currentblock] = []

		for inst in self._PLCSourceList:

			# Current IL source line.
			sourcecount +=1

			# Check for a blank line. For blank lines, save the source, 
			# but do not add it to the syntax list.
			if inst.strip() == '':
				self._SourceBlocks[currentblock].append(inst)
			else:

				self._InstrCount += 1

				# Extract the instruction and its parameters from the string.
				instruction, paramdict, paramstr = self._ExtractParams(inst)

				# Now find the correct instruction.
				instrdef, validparams, originalparams, origparamlist, errcode = \
						self._FindInstruction(instruction, paramdict)

				
				# Test if the instruction is invalid.
				if not instrdef:
					self._CompileErrors += 1
					self.ReportError(errcode, currentblock, rungref, inst)
					# We still add the source to the block 
					# list so we can display and edit the error.
					self._SourceBlocks[currentblock].append(inst)

				# New rung.
				elif (instrdef['class'] == 'rung'):
					currentrung += 1
					rungref = paramstr
					self._PLCSyntax[currentblock].append([self._AddInstr(inst, paramstr, 
						originalparams, origparamlist, validparams, instrdef,
							 currentblock, rungref)])
					self._SourceBlocks[currentblock].append(inst)

				# Subroutine.
				elif (instrdef['class'] == 'sbr'):
					currentrung = 0
					rungref = '0'
					currentblock = paramstr.strip()
					self._PLCSyntax[currentblock] = []
					self._PLCSyntax[currentblock].append([self._AddInstr(inst, paramstr, 
						originalparams, origparamlist, validparams, instrdef, 
							currentblock, rungref)])
					self._SourceBlocks[currentblock] = []
					self._SourceBlocks[currentblock].append(inst)


				# Ordinary instruction.
				else:
					self._PLCSyntax[currentblock][currentrung].extend([self._AddInstr(inst, paramstr, 
						originalparams, origparamlist, validparams, instrdef, 
							currentblock, rungref)])
					self._SourceBlocks[currentblock].append(inst)



	########################################################
	def _CheckSubCall(self, instr):
		"""Check a subroutine call to seee if the subroutine exits.
		Parameters: instr (dict) = The instruction to be checked.
		"""
		if (instr['validparams']['inparam1'] not in self._PLCSyntax):
			self._CompileErrors += 1
			self.ReportError('nosubr', instr['sbr'], instr['rung'], instr['plcsource'])


	########################################################
	def CheckCalls(self):
		"""Check that all calls to subroutines have valid targets.
		"""

		# Iterate through each main and subroutine.
		for subblock, runglist in self._PLCSyntax.items():

			# Iterate through each rung.
			for rung in runglist:

				# Iterate through each instruction in each rung.
				for instr in rung:

					# If this is a subroutine call, check if the subroutine exists.
					if (instr['instrdef']['type'] == 'call'):
						self._CheckSubCall(instr)



############################################################


############################################################
class CompileCode:
	"""Compile the analysed IL to executable code.
	"""

	########################################################
	def __init__(self, plcsyntax, instdatatable):
		"""
		plcsyntax (dict) = A data structure for holding the parsed program
			syntax.
		instdatatable (dict) = An empty dictionary. This is used by some 
			instructions to store instruction data.
		"""
		self._PLCSyntax = plcsyntax
		self._IndentLevel = 0	# Level for indenting subr code.
		self._InstrIndex = 0	# Counter for unique instructions.

		# This is used by some instructions to store instruction data.
		self._InstDataTable = instdatatable

		# Python source text.
		self._PythonSource = ''


	########################################################
	def _FormatInstr(self, InstrCode, InstrType, InstrStrList, Params):
		"""Format the instruction.
		Parmeters: 
		InstrCode (string) - The name of the instruction.
		InstrType (string) - The type of instruction.
		InstrStrList (list) - List of strings containing the instruction 
			Python source code.
		Params (string) - The parameters as a string. This is used
			only for display in a comment.
		Returns: (string) - A single string containing the formatted 
			instruction ready for the parameters to be inserted.
		"""

		# Determine the number of required indents. Indenting is used 
		# to handle correct formatting for subroutines, loops, etc.
		Indents = '\t' * self._IndentLevel

		# If this is the start of a new subroutine, reset the indent 
		# level to 1. However, we use no indents for the start of the 
		# subroutine itself.
		if (InstrType == 'sbr'):
			self._IndentLevel = 1
			Indents = ''

		# For loops require 2 additional indents, because they are conditional.
		elif (InstrType == 'for'):
			self._IndentLevel += 2

		# The NEXT instruction reverses the indenting used by the FOR.
		elif (InstrType == 'next'):
			self._IndentLevel -= 2
			if (self._IndentLevel < 0):
				self._IndentLevel = 0


		# Insert the comment into the beginning. Indent as required.
		InstStr = '%s# %s %s\n' % (Indents, InstrCode, Params)

		# Merge the list into a single string. Add newline characters
		# to the end of each line. Indent according to the specified
		# indent level.
		for i in InstrStrList:
			InstStr = '%s%s%s\n' % (InstStr, Indents, i)

		# Add a comment block on the end as a marker.
		InstStr = '%s%s%s\n' % (InstStr, Indents, '#####')

		return InstStr


				
	########################################################
	def _CompileIL(self):
		"""Compile each IL instruction to Python source code.
		"""

		# Iterate through each main and subroutine.
		for subblock, runglist in self._PLCSyntax.items():

			# If this is the main program, reset the indent level.
			if (subblock == 'main'):
				self._IndentLevel = 0

			# Iterate through each rung.
			for rung in runglist:

				# Iterate through each instruction in each rung.
				for instr in rung:

					# Get the definition for this instruction.
					instrdef = instr['instrdef']
					# Get the original parameters (for display).
					paramstr = instr['paramstr']

					# Format the instruction into a single string.
					instrstr = self._FormatInstr(instrdef['opcode'], instrdef['type'], 
						instrdef['instruction'], paramstr)

					# Check if it uses the instruction data table to store
					# information outside of the normal data table. This is
					# typically used for differentiating instructions.
					instrdefault = instrdef['instrdefault']
					if (instrdefault != None):
						self._InstrIndex += 1
						self._InstDataTable[str(self._InstrIndex)] = instrdefault

					# Save the parameters.
					validparams = instr['validparams']
					validparams['instrindex'] = self._InstrIndex

					# Insert the parameters.
					instrstr = instrstr % validparams

					# Save the result.
					instr['pycode'] = instrstr

	
	########################################################
	def _AssembleILCodeBlocks(self):
		"""Assemble the Python source code into a single block
		for compiling to Python byte code. This returns a single
		block of text ready to compile.
		"""

		pythonsourcelist = []
		mainsourcelist = []

		# First, get the source from the main program.
		mainsource = self._PLCSyntax['main']

		# Go through each rung.
		for rung in mainsource:
			# And through each instruction in each rung.
			for pysource in rung:
				mainsourcelist.extend(pysource['pycode'])

		# Now, get the remaining subroutines.
		for subsource, runglist in self._PLCSyntax.items():
			# We've already done the main program.
			if (subsource != 'main'):
				 # Go through each rung.
				for rung in runglist:
					# And each instruction in each rung.
					for pysource in rung:
						pythonsourcelist.extend(pysource['pycode'])

		# Add the main program to the end. The main program has to go at
		# the end so that it can see the subroutines before compiling them.
		pythonsourcelist.extend(mainsourcelist)

		# Convert the list to a single string, and return it.
		return ''.join(pythonsourcelist)


	########################################################
	def CompileSource(self):
		"""Compile the analysed syntax into a code object.
		Returns (codeobject) = A code object with executable Python 
			byte code.
		"""
		# Go through and compile each instruction to Python source code.
		self._CompileIL()

		# Turn the list of instruction strings into a single
		# block of text. The 'main' routine must go first.
		self._PythonSource = self._AssembleILCodeBlocks()

		# Compile the source code into Python p-code.
		# This should be enclosed in an exception handler by the caller
		# to deal with syntax errors in a more intelligent way.
		codeobj = compile(self._PythonSource, '<plc code>', 'exec')

		return codeobj


	########################################################
	def GetSource(self):
		"""Return a block of text with the Python source code.
		Returns (string) = The complete Python source code of the
			soft logic program.
		"""
		return self._PythonSource


############################################################


