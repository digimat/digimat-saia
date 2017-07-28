##############################################################################
# Project: 	MBLogic
# Module: 	PLCComp.py
# Purpose: 	Analyse the soft logic configuration.
# Language:	Python 2.5
# Date:		30-Jan-2009.
# Ver:		10-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2009 - 2010 - Michael Griffin   <m.os.griffin@gmail.com>
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


import time
import copy

from mbsoftlogicck import DLCkDataTable, DLCkInstructions, PLCCompile, PLCLadder, PLCXref, DLCkTemplates, PLClad2il

import PLCRun
import PLCIOManage
from sysmon import MonUtils


############################################################
class ProgCompiler(PLCCompile.PLCCompiler):
	"""Compile the soft logic program, and hold the results. This inherits
	from the compiler class in the soft logic library. 
	"""

	############################################################
	def __init__(self, plcprogfilename, timestamp):
		"""Parameters: 
		plcprogfilename (string) - Name of soft logic program.
		timestamp (float) - Time stamp for when we started.
		"""

		# Initialise the inherented class.
		PLCCompile.PLCCompiler.__init__(self, DLCkInstructions.InstrDefList, 
							DLCkDataTable.InstrDataTable,
							plcprogfilename)

		# Create a ladder assembler.
		self._LadderAssy = PLCLadder.LadderFormat()

		# Time program compiled.
		self._StartTime = timestamp
		# Soft logic program file name.
		self._PLCProgFileName = plcprogfilename

		# True if program is OK to run.
		self._ProgOK = False


		# Compiled program.
		self._PLCProgram = None
		# Number of instructions compiled.
		self._InstrCount = 0
		# True of any compiler errors.
		self._CompileErrors = True
		# Copy of compiler error messages.
		self._CompileErrMsgs = []


		# Ladder representation.
		self._LadderData = None
		# Cross references.
		self._InstrXref = None
		self._AddrXref = None



	############################################################
	def CompileAll(self):
		"""Compile the program.
		"""
		# Compile the PLC program.
		self._PLCProgram, self._InstrCount, self._CompileErrors = self.CompileProgram()

		# Get any compiler error messages.
		self._CompileErrMsgs = self.GetCompileErrors()

		# Signal the program is OK.
		self._ProgOK = not self._CompileErrors


		# Assemble the ladder representation.
		self._RawSyntax = self.GetProgramSyntaxResults()
		self._LadderData = self._LadderAssy.AssembleLadder(self._RawSyntax, self._PLCProgFileName)

		# Generate a cross reference.
		xref = PLCXref.XrefGen(self._RawSyntax)
		self._InstrXref = xref.GetInstrXref()
		self._AddrXref = xref.GetAddrXref()



	############################################################
	def ProgramOK(self):
		"""Return True if the program is OK to run.
		"""
		return self._ProgOK


	############################################################
	def IsCompileError(self):
		"""Returns True if there were any compile errors.
		"""
		return self._CompileErrors

	############################################################
	def GetPLCProg(self):
		"""Return the compiled soft logic program executable.
		"""
		return self._PLCProgram

	############################################################
	def GetCompileResults(self):
		"""Return a dictionary containing the results of the
		compile effort.
		"""
		if self._CompileErrors:
			compmode = 'Errors'
			compcolour = 'statusfault'
		else:
			compmode = 'Ok'
			compcolour = 'statusok'

		return {'plcprogsource' : self.GetProgramCopy(),	# Copy of source code.
			'plcinstrcount' : self._InstrCount,		# Number of instructions.
			'plccompileerr' : self._CompileErrors,		# True if errors.
			'plccompilemsg' : self._CompileErrMsgs,		# Compile error messages.
			'plccompilemode' : compmode,			# Message for compile state.
			'plccompilecolour' : compcolour,		# CSS colours for compile state.
			'plcstarttime' : self._StartTime,		# Time compiled at.
			}

	############################################################
	def GetLadder(self):
		"""Return the ladder presentation.
		"""
		return self._LadderData

	############################################################
	def GetXref(self):
		"""Return the instruction and address cross references.
		"""
		return self._InstrXref, self._AddrXref


########################################################################


########################################################################
class PLCSyntaxChecker(PLCCompile.SourceAnalyse):
	"""Conduct a test compile of a soft logic program or part of one. This
	can be used to test fragments of a program before committing to a change. 
	This does not check subroutine calls to see if a subroutine exists.
	This inherits from the compiler class in the soft logic library. 
	"""

	############################################################
	def __init__(self):
		"""
		"""

		# Initialise the inherented class.
		PLCCompile.SourceAnalyse.__init__(self, DLCkInstructions.InstrDefList)


########################################################################



########################################################################
class PComp:
	""".
	"""

	############################################################
	def __init__(self):
		"""Initialise the instruction set.
		"""

		# Time stamp for report data.
		timestamp = time.time()

		# Current running configuration. This dictionary will hold the 
		# results from the compiler, and will breake the link to the
		# compiler object so it won't be affected when we try to do
		# on-line editing of the program.
		self._SoftLogicCurrentParams = {
			# True, if initialised at least once.
			'initdone' : False,
			# The runnable compiled program.
			'runnableprogram' : None,
			# A list of the IL source code.
			'plcprogsource' : [],
			# True if errors.
			'plccompileerr' : [],
			# Compile error messages.
			'plccompilemsg' : [],
			# Number of instructions.
			'plcinstrcount' : 0,
			# The IL as blocks in a dictionary.
			'ilblocks' : {},
			# The ladder source as a matrix.
			'ladder' : {},
			# A list of subroutines.
			'subroutines' : [],
			# The address cross reference.
			'addrxref' : {},
			# The instruction cross reference.
			'instrxref' : {},
			}


		# The compiled PLC program.
		self._PLCProgram = None

		# New compiled soft logic program information.
		self._PLCNewProg = None

		# Create an initial default soft logic program. We give it an 
		# empty file name, because we don't want to load the program just yet.
		# We need an object  so the reports don't have to deal with 
		# uninitialised objects.
		self._DefaultReportProg = ProgCompiler('', timestamp)


		# General configuration status parameters for program.
		self._NewPLCConfigStatParams = {'starttime' : 0.0, 'signature' : 'NA', 'configstat' : 'error'}
		self._CurrentPLCConfigStatParams = {'starttime' : 0.0, 'signature' : 'NA', 'configstat' : 'error'}


	########################################################
	def GetSubrTemplate(self):
		"""Return the template used for creating new subroutines in IL.
		"""
		return DLCkTemplates.PLCSubrTemplate


	########################################################
	def _SetConfigStatus(self, timestamp, filesig, configok):
		"""Set the configuration status codes.
		timestamp = Time stamp (as unix time).
		filesig = File hash signature.
		configok = If True, the configuration was OK.
		"""
		if configok:
			configstat = 'ok'
		else:
			configstat = 'error'
		return {'starttime' : timestamp, 'signature' : filesig, 'configstat' : configstat}


	############################################################
	def ReportCurrentPLCProgram(self):
		"""Return a dictionary containing the current soft logic 
		program information.
		"""
		return self._SoftLogicCurrentParams

	############################################################
	def ReportNewPLCProgram(self):
		"""Return an object containing the new soft logic 
		program information.
		"""
		if self._PLCNewProg:
			return self._PLCNewProg
		else:
			return self._DefaultReportProg


	########################################################
	def GetNewPLCStatParams(self):
		"""Return the soft logic IO status parameters for the new
		soft logic program.
		"""
		return self._NewPLCConfigStatParams

	########################################################
	def GetCurrentPLCStatParams(self):
		"""Return the soft logic IO status parameters for the current
		soft logic program.
		"""
		return self._CurrentPLCConfigStatParams


	############################################################
	def _UpdateCompileInfo(self):
		"""Update the program status information after compiling.
		"""

		# If we don't have anything for the current program yet, then use
		# the one we just read, whether it is any good or not.
		# Otherwise, if the new PLC program is OK use the information for
		# it in place of the old one.
		if (not self._SoftLogicCurrentParams['initdone']) or (not self._PLCNewProg.IsCompileError()):
			currentprogram = {}
			# True, if initialised at least once.
			currentprogram['initdone'] = True
			# The runnable compiled program.
			currentprogram['runnableprogram'] = self._PLCNewProg.GetPLCProg()
			# A list of the IL source code.
			currentprogram['plcprogsource'] = self._PLCNewProg.GetProgramCopy()
			# True if errors.
			currentprogram['plccompileerr'] = self._PLCNewProg.GetCompileResults()['plccompileerr']
			# Compile error messages.
			currentprogram['plccompilemsg'] = self._PLCNewProg.GetCompileResults()['plccompilemsg']
			# Number of instructions.
			currentprogram['plcinstrcount'] = self._PLCNewProg.GetCompileResults()['plcinstrcount']
			# Ladder source.
			currentprogram['ladder'] = self._PLCNewProg.GetLadder()
			# The IL as blocks in a dictionary.
			currentprogram['ilblocks'] = self._PLCNewProg.GetProgramBlocks()
			# A list of subroutines.
			currentprogram['subroutines'] = currentprogram['ilblocks'].keys()

			InstrXref, AddrXref = self._PLCNewProg.GetXref()
			# The address cross reference.
			currentprogram['addrxref'] = AddrXref
			# The instruction cross reference.
			currentprogram['instrxref'] = InstrXref


			# Do a deep copy to completely break any connections to the compiler.
			# This will allow us to do on-line edits without affecting the
			# running program.
			self._SoftLogicCurrentParams = copy.deepcopy(currentprogram)

			# Update the status parameters.
			self._CurrentPLCConfigStatParams = self._NewPLCConfigStatParams


	############################################################
	def _PreparePLCProgForRun(self, timestamp):
		"""This prepares a compiled program for running. This process
		is common to compiling new programs from disk, or recompiling
		programs already in memory.
		"""
		# Compile the program.
		self._PLCNewProg.CompileAll()

		# Get a copy of the program.
		sourcelist = self._PLCNewProg.GetProgramCopy()

		# Calculate the source listing signature.
		filesig = MonUtils.CalcSig(''.join(sourcelist))
		
		# Check if errors are present in the new configuration.
		ConfigOK = not self._PLCNewProg.IsCompileError()

		# Calculate the new status parameters.  
		self._NewPLCConfigStatParams = self._SetConfigStatus(timestamp, filesig, ConfigOK)

		# Indicate if the *new version* of the program is OK to run.
		return ConfigOK



	############################################################
	def _CompileNewPLCProg(self):
		"""Read in the PLC program from disk and compile it. 
		"""
		# Get the time stamp for when we started.
		timestamp = time.time()

		# Initialise a new compiler object.
		self._PLCNewProg = ProgCompiler(PLCIOManage.PLCIO.GetCurrentPLCProgName(), timestamp)

		# Read in the file. If we can't read this, then we just 
		# continue on and let the rest of the system handle the error.
		try:
			self._PLCNewProg.ReadInFile()
		except:
			pass

		# Complete the recompile process. 
		return self._PreparePLCProgForRun(timestamp)


	############################################################
	def _RecompileEditedPLCProg(self):
		"""Recompile the existing PLC program after changing
		it on line. 
		"""
		# Get the time stamp for when we started.
		timestamp = time.time()


		# Get a copy of the existing PLC program source (as an IL list).
		sourcelist = self._PLCNewProg.GetProgramCopy()

		# Initialise a new compiler object with the new source code. 
		# This creates a compiler object that is independent of the 
		# currently running soft logic program.
		self._PLCNewProg = ProgCompiler(PLCIOManage.PLCIO.GetCurrentPLCProgName(), timestamp)

		# Use the copy of the program source that we saved. 
		self._PLCNewProg.SetProgramCopy(sourcelist)

		# Complete the recompile process. 
		return self._PreparePLCProgForRun(timestamp)


	############################################################
	def CheckPLCProgSyntax(self, plcproglist):
		"""Compile a temporary copy of a program or subroutine
			to test if it is OK. 
		Parameters: plcproglist (list) = A list of IL source with one
			instruction per list element. This will be compiled to 
			test if it is OK.
		Returns: (boolean, list) True if OK, and a list of
			any compile errors.
		"""

		# Initialise a new compiler object with the new source code. 
		# This creates a compiler object that is independent of the 
		# currently running soft logic program.
		testcompiler = PLCSyntaxChecker()
		# Use the copy of the program source that we saved. 
		testcompiler.SetSourceList(plcproglist)

		# Compile the program.
		testcompiler.AnalyseProgram()

		return 	testcompiler.HasErrors(), testcompiler.GetCompileErrors()



	############################################################
	def _RunCompiledPLCProg(self):
		"""Set the current PLC program to the compiled version, and set the
		soft logic system to the run state.
		"""
		# Set the program to run.
		PLCRun.PLCSystem.SetPLCProgram(self._SoftLogicCurrentParams['runnableprogram'])

		# Enable or disable the scan as required.
		if self._SoftLogicCurrentParams['plccompileerr']:
			PLCRun.PLCSystem.DisableRunScan()
		else:
			PLCRun.PLCSystem.EnableRunScan()

		# Update the scan rate.
		PLCRun.PLCSystem.SetScanRate()



	############################################################
	def RecompileAndRun(self):
		"""Recompile and run the existing plc program.
		If there was a compile error, the new program is not started
		and any existing running program will not be affected.
		Returns true if the compile was OK.
		"""
		# Compile.
		cresult = self._RecompileEditedPLCProg()
		if cresult:
			# Update the reporting system with the compile results.
			self._UpdateCompileInfo()
			# Run.
			self._RunCompiledPLCProg()
			# Reset the scan records.
			PLCRun.PLCSystem.ResetScanValues()
		return cresult


	############################################################
	def LoadCompileAndRun(self):
		"""Load from disk, compile and run the plc program.
		If there was a compile error, the new program is not started
		and any existing running program will not be affected.
		Returns true if the compile was OK.
		"""
		# Compile.
		cresult = self._CompileNewPLCProg()
		if cresult:
			# Update the reporting system with the compile results.
			self._UpdateCompileInfo()
			# Run.
			self._RunCompiledPLCProg()
			# Reset the scan records.
			PLCRun.PLCSystem.ResetScanValues()
		return cresult


	############################################################
	def AddNewSubr(self, subname):
		"""This adds a new subroutine, based on a predefined template.
		This does not check to see if the subroutine already exists.
		Parameters: subname (string) = Name of subroutine.
		"""
		# Substitute the subroutine name into the template.
		newsubr = self.GetSubrTemplate() % subname

		# Split the block of text into lines. This also strips out any line endings.
		# Then we add the line endings back in. We do it this way to control
		# platform dependent line ending differences.
		formattedtext = map(lambda textline : '%s\n' % textline, newsubr.splitlines())

		# Check if the subroutine is OK. This will confirm that the 
		# subroutine name is syntactically correct.
		haserrors, self._SubrErrors = self.CheckPLCProgSyntax(formattedtext)

		# If the new subroutine name is OK, then save it. Otherwise, we just
		# throw it away.
		if not haserrors:

			# Add in the new block.
			self._PLCNewProg.AddSourceBlock(formattedtext)

			# Save to disk. If saved successfully, recompile and run.
			try:
				self._PLCNewProg.WriteOutFile()
				self.RecompileAndRun()
				saveok = True
			except:
				saveok = False

		else:
			saveok = False

		return saveok


	########################################################
	def DeleteSubr(self, delsubnames):
		"""This deletes subroutines of IL source. It will accept multiple
		subroutines in a list. If any of the subroutines do not exist, 
		they are ignored.
		Parameters: delsubnames (list) = List of names of subroutines.
		Returns: (boolean) = True if the delete and save was OK.
		"""
		self._PLCNewProg.DeleteSourceBlock(delsubnames)

		# Save to disk. If saved successfully, recompile and run.
		try:
			self._PLCNewProg.WriteOutFile()
			self.RecompileAndRun()
			saveok = True
		except:
			saveok = False


		return saveok




	########################################################
	def MergeSourceBlock(self, subrdata):
		"""This merges in a subroutine of soft logic source. If the subroutine 
		does not already exist, it is added. If it does exist, it replaces
		the original.
		Parameters: subrdata (dict) = A dictionary containing the complete 
			subroutine data from the editor.
		Returns: (boolean) = True if the merge and save was OK.
		"""

		# Convert the editor data to IL source for a complete subroutine.
		analyser = PLClad2il.SubrAnalyser(DLCkInstructions.InstrDefList)
		subrname, subrcomments, decodedilsource = analyser.DecodeSubroutine(subrdata)

		# Assemble the subroutine code.
		subril = PLClad2il.AssembleSubr(subrname, subrcomments, decodedilsource)

		# Strips out any line endings then add the line endings back in. 
		# We do it this way to control platform dependent line ending differences.
		formattedtext = ['%s\n' % textline for textline in subril]


		# Merge in the results. We merge the edits without checking them first, because
		# we need to keep them so we can correct any errors, instead of just 
		# throwing all the new edits away.
		self._PLCNewProg.MergeSourceBlock(subrname, formattedtext)


		# Recompile and try to run the edited program.
		compileOK = self.RecompileAndRun()

		# If the edits were OK, then save them.
		if compileOK:

			# Save to disk. If saved successfully, recompile and run.
			try:
				self._PLCNewProg.WriteOutFile()
				saveok = True
			except:
				saveok = False
		else:
			saveok = False

		return saveok



########################################################################


# Create the soft logic program compile and control object. This manages loading,
# recompiling, and editing soft logic programs.
PLCLogic = PComp()

########################################################################

