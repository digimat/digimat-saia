#!/usr/bin/python
##############################################################################
# Project: 	MBLogic
# Module: 	demo.py
# Purpose: 	Demo showing features of MBLogic.
# Language:	Python 2.5
# Date:		26-Jun-2008.
# Ver:		07-Nov-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin   <m.os.griffin@gmail.com>
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
# along with MBServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

from mbsoftlogicck import PLCInterp
from mbsoftlogicck import PLCCompile
from mbsoftlogicck import DLCkInstructions
from mbsoftlogicck import DLCkDataTable
from mbsoftlogicck import DLCkLibs

import time	# This is only required for the demo.

############################################################

"""
This is a simple demo program illustrating some of the functions of MBLogicEngineCk.
MBLogicEngineCk is the soft logic component of MBLogic. When combined with MBServer,
it can provide a stand alone soft logic system. It however can also be used as an
embedded library in another application, such as an auotmated test system. 

MBLogicEngine is designed to be adaptable to allow it to emulate different PLCs.
This instance is modeled on the Koyo "Click" PLC.

"""

print('\n\nMBLogicEngineCk demo program.')

"""
The compiler must be initialised using three parameters. The first is a list
of "instruction definitions". An "instruction definition" is a dictionary which is used
to define a single PLC instruction. An "instruction definition" must exist for
each valid PLC instruction.

The second data structure is an "instruction data table". The "instruction data table"
is a dictionary which is used to hold information which is private to particular 
instructions and which must exist outside of the normal data tables. Some PLC
architectures make use of this feature, while others do not. A typical use is
for boolean differentiation (one shot) instructions where the state is not stored
in the normal data table.

The third parameter is the name of the file containing the soft logic program.
"""

# Compiler for PLC program.
PLCCompiler = PLCCompile.PLCCompiler(DLCkInstructions.InstrDefList, DLCkDataTable.InstrDataTable, 'demoplcprog.txt')

"""
Next we read in the PLC program. The file used is the one specified above.
"""

# Read in the PLC program.
PLCCompiler.ReadInFile()

"""
Next we compile the PLC program. Two sorts of errors can occur here. One is
a PLC program syntax error caused by an incorrect PLC program. This will cause 
the compiler to stop and return a compile error (CompileErrors). At present, 
it simply prints an error message to the terminal.

The other sort of error can be caused by a bug in the soft logic system. The most
common source of bug of this type is an improperly defined instruction. This
will cause an exception which you will need to catch. For software development
purposes though, it is better to leave the exception uncaught, so that it
provides a trace-back error message to pin-point the source of the error.

The compiler returns three things: 
1) A "code object" which is the PLC program ready to execute.
2) A total count of PLC instructions in the PLC program.
3) A boolean flag which is set to "True" if there were any PLC syntax errors.
"""

# Compile the PLC program.
plcprogram, instrcount, CompileErrors = PLCCompiler.CompileProgram()

"""
If there were any compile errors, we can ask for a description. The error
messages are contained in a list.
"""

# Get any compiler error messages.
CompileErrMsgs = PLCCompiler.GetCompileErrors()

for i in CompileErrMsgs:
	print(i)

"""
Next we need to initialise the interpreter. To do this, we need to give it the
following parameters:
1) The compiled PLC program.
2) Boolean, word, and private instruction data tables.
3) A series of objects (8 in total) which provide run-time support functions specific
	to the model of PLC being emulated. Some of these may be just placeholders 
	if they are not needed for this model. 
	In this example, "TableOperations" provides library functions which support 
	copy, search, and other instructions. "Accumulator" is a placeholder. 
	"BinMathLib" provides math functions. "FloatMathLib", "BCDMathLib", 
	and "WordConversions" are placeholders. "CounterTimers" provides counter
	and timer functions. "SystemScan" handles scan overhead functions.

This should get called *once* only, not each PLC program scan.

"""

if (not CompileErrors):
	MainInterp = PLCInterp.PLCInterp(plcprogram,  
		DLCkDataTable.BoolDataTable, DLCkDataTable.WordDataTable, 
		DLCkDataTable.InstrDataTable,
		DLCkLibs.TableOperations, DLCkDataTable.Accumulator,
		DLCkLibs.BinMathLib, DLCkLibs.FloatMathLib, DLCkLibs.BCDMathLib,
		DLCkLibs.WordConversions, DLCkLibs.CounterTimers, DLCkLibs.SystemScan)


	"""
	In this example we are simply executing the program several times. Normally, you
	would provide some other means of calling this after an I/O scan. The MBLogic
	project will integate this into MBServer, which will provide the repeated
	scanning functions. However, if you are embedding these libraries into another
	program you must provide some other means for calling the following functions.
	"""
	for i in range(25):

		"""
		We can enter data into the data tables by calling a function and passing
		it a dictionary. We use SetBoolData to set boolean data, and SetWordData
		to set word data. In this example, we are setting X17 to True, and
		X277 to False. We only need to update data that we are actually using,
		rather than the whole data table.
		"""
		if i == 10:
			MainInterp.SetBoolData({'X17' : True, 'X277' : False})

		"""
		We can place other custom code here if we wish.
		"""

		"""
		We call the main interpreter to execute the PLC program. This 
		should be called once each for program scan. Some errors may cause an 
		exception which terminates the program. The error code, rung, and subroutine
		can be retrieved as the "exit code" (see below). Normal exits are caused by 
		raising an exception. See the documentation for details.
		"""
		MainInterp.MainLoop()

		"""
		We can read the data table by calling GetBoolData or GetWordData and
		passing a list of the addresses we wish to read. The functions will
		return a dictionary containing the keys and data.
		"""
		BData = MainInterp.GetBoolData(['Y1', 'Y367', 'C50', 'CT100'])
		print('%d: Y1 = %s  Y367 = %s  C50 = %s  CT177 = %s' % 
			(i, BData['Y1'], BData['Y367'], BData['C50'], BData['CT100']))

		"""
		For the purposes of the demo we allow the system to 'sleep' after each scan
		to allow other processes to get some work done. Normally the program calling
		'MainInterp' would be doing this as part of its main event loop.
		"""
		# Sleep.
		time.sleep(0.05)

	"""
	We can see the reason why the program exited by getting the exit code. 
	It also gives us the location in the PLC program that it exited from.
	"""
	ExitCode, ExitSubr, ExitRung = MainInterp.GetExitCode()
	print('\nThe PLC program exited in subr %s, rung %s and exit code %s\n' %
		(ExitSubr, ExitRung, ExitCode))

else:
	print('The MBLogicEngine demo program exited due to an error while compiling the PLC program.')

