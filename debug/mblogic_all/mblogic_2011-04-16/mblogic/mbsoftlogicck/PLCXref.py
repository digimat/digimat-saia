#############################################################################
# Project: 	MBLogic
# Module: 	PLCXref.py
# Purpose: 	Cross reference generator for a soft logic system.
# Language:	Python 2.5
# Date:		26-Apr-2009.
# Ver:		28-Jul-2010.
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

"""Generate soft logic program cross references for instructions and
for addresses.
"""


############################################################
class XrefGen:
	"""Generatea a cross reference.
	"""

	########################################################
	def _AddInstruction(self, instrclass, routine, rung, opcode, params):
		"""
		"""
		# If this is a comment, ignore it.
		if (instrclass in ['comment', 'rung', 'sbr']):
			return

		# Check if the subroutine name has already been found.
		if (opcode not in self._InstrXref):
			self._InstrXref[opcode] = {routine : [rung]}
		elif (routine not in self._InstrXref[opcode]):
			self._InstrXref[opcode][routine] = [rung]
		else:
			self._InstrXref[opcode][routine].append(rung)


		# Extract the parameters.

		# If this is a math equation, the parameters are stored in a special list.
		if ('addrlist' in params):
			addrlist = params['addrlist']
			for paramvalue in addrlist:
				if (paramvalue not in self._AddrXref):
					self._AddrXref[paramvalue] = {routine : [rung]}
				elif (routine not in self._AddrXref[paramvalue]):
					self._AddrXref[paramvalue][routine] = [rung]
				else:
					self._AddrXref[paramvalue][routine].append(rung)

		# For regular instructions, we have to extract the addresses from the 
		# original parameter set.
		else:
			for paramname, paramvalue in params.items():
				if (paramname not in ['instrindex', 'errors', 'equationparams']):
					if (paramvalue not in self._AddrXref):
						self._AddrXref[paramvalue] = {routine : [rung]}
					elif (routine not in self._AddrXref[paramvalue]):
						self._AddrXref[paramvalue][routine] = [rung]
					else:
						self._AddrXref[paramvalue][routine].append(rung)



	########################################################
	def __init__(self, plcsyntax):
		"""Generate a cross reference.
		"""
		self._PLCSyntax = plcsyntax

		self._InstrXref = {}
		self._AddrXref = {}

		# Iterate through each main and subroutine.
		for subblock, runglist in self._PLCSyntax.items():

			# Iterate through each rung.
			for rung in runglist:
				for i in rung:
					self._AddInstruction(i['instrdef']['class'], subblock, i['rung'], 
							i['instrdef']['opcode'], i['originalparams'])


	########################################################
	def GetInstrXref(self):
		"""Generate and return an instruction cross reference.
		"""
		return self._InstrXref


	########################################################
	def GetAddrXref(self):
		"""Generate and return an address cross reference.
		"""
		return self._AddrXref


##############################################################################


