#############################################################################
# Project: 	MBLogic
# Module: 	PLCLadder.py
# Purpose: 	Generic ladder display format for a soft logic system.
# Language:	Python 2.5
# Date:		09-May-2010.
# Ver:		01-Sep-2010.
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

"""Generate ladder data matrices for displaying ladder logic in a web browser.
This creates the JSON data arrays. The web browser is responsible for converting
this into SVG.

This version is based on an earlier one which generated the SVG directly. 
This new version does not concern itself with the actual SVG, just the matrix 
creation.
"""

############################################################

import hashlib

import DLCkDataTable


############################################################
class RungAssembler:
	"""Assemble a single rung.
	"""

	########################################################
	def __init__(self, rungdata):
		"""Params: rungdata = The rung data list.
		"""
		self._RungData = rungdata

		# Collect all the comments together.
		self._Comments = []
		# Keep a copy of everything for the IL list as well.
		self._ILList = []
		# The rung matrix input data.
		self._InputMatrix = []
		# The rung matrix output data.
		self._OutputMatrix = []

		# Collect all the outputs together.
		self._Outputs = []
		# Collect all the inputs together.
		self._Inputs = []



		# 'branchttr' = Top branch extending right.
		# 'branchtr' = Middle branch extending right.
		# 'branchr' = Bottom branch extending right.
		# 'vbarr' = Vertical bar with no branches.
		# The following are for the opposite side. 
		# 'branchttl',  'branchtl', 'branchl', 'vbarl'

		# Valid branch instructions.
		self._Branches = ('branchttr', 'branchtr', 'branchr',  'vbarr',
				'branchttl',  'branchtl', 'branchl', 'vbarl', 
						'hbar')

		# Valid vertical branch instructions. This excludes horizontal
		# symbols.
		self._VertBranches = ('branchttr', 'branchtr', 'branchr',  'vbarr',
				'branchttl',  'branchtl', 'branchl', 'vbarl')


		# Standard Matrix cell elements used for branches.
		self._HBarCell = {'value' : 'hbar', 'addr' : [], 'monitor' : 'none'}
		self._VBarLCell = {'value' : 'vbarl', 'addr' : [], 'monitor' : 'none'}
		self._BranchLCell = {'value' : 'branchl', 'addr' : [], 'monitor' : 'none'}
		self._BranchTRCell = {'value' : 'branchtr', 'addr' : [], 'monitor' : 'none'}
		self._BranchTLCell = {'value' : 'branchtl', 'addr' : [], 'monitor' : 'none'}
		self._BranchTTLCell = {'value' : 'branchttl', 'addr' : [], 'monitor' : 'none'}



		# Classify the instructions.
		self._MatrixType = self._ClassifyRung()
		# Assemble the input matrix.
		if self._MatrixType == 'single':
			self._MatrixAssyOK = self._InputsToMatrixSingle()
			self._OutputsToMatrix()
			# If there was an error assembling the matrix, force it to il,
			# *unless* there are no inputs, in which case we may as well 
			# still display as ladder.
			if (not self._MatrixAssyOK) and (len(self._Inputs) > 0):
				self._MatrixType = 'il'

		elif self._MatrixType in ['double', 'triple']:
			self._MatrixAssyOK = self._InputsToMatrixMulti(self._MatrixType)
			self._OutputsToMatrix()
			# If there was an error assembling the matrix, force it to il.
			if not self._MatrixAssyOK:
				self._MatrixType = 'il'



	########################################################
	def _ClassifyRung(self):
		"""Classify the instructions as to type.
		Return: (string) = The matrix type.
		"""

		# Ladder matrix type. This is dictated by the type of output 
		# together with whether the inputs are compatible with this.
		matrixtype = 'none'


		# Go through each instruction in the rung and categorise them.
		for instr in self._RungData:
			# Keep a copy as IL.
			self._ILList.append(instr['plcsource'])

			# Find out what type of instruction it is.
			instclass = instr['instrdef']['class']

			# This is a comment. We use the original parameter string
			# because we don't want the blanks stripped out. 
			if (instclass == 'comment'):
				self._Comments.append(instr['paramstr'])

			# This output requires no logic input.
			elif (instclass == 'output0'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype in ('none', 'single'):
					matrixtype = 'single'
				else:
					matrixtype = 'il'

			# This output requires one logic input.
			elif (instclass == 'output1'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype in ('none', 'single'):
					matrixtype = 'single'
				else:
					matrixtype = 'il'

			# This output requires two logic inputs.
			elif (instclass == 'output2'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype == 'none':
					matrixtype = 'double'
				else:
					matrixtype = 'il'

			# This output requires three logic inputs.
			elif (instclass == 'output3'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype == 'none':
					matrixtype = 'triple'
				else:
					matrixtype = 'il'

			# FOR instruction.
			elif (instclass == 'for'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype in ('none', 'single'):
					matrixtype = 'single'
				else:
					matrixtype = 'il'

			# Next in FOR.
			elif (instclass == 'next'):
				self._Outputs.append(instr)
				# Determine what sort of matrix type is possible.
				if matrixtype in ('none', 'single'):
					matrixtype = 'single'
				else:
					matrixtype = 'il'

			# Subroutine heading.
			elif (instclass == 'sbr'):
				# Nothing to do other than note the type.
				matrixtype = 'sbr'

			# Rung start.
			elif (instclass == 'rung'):
				# Nothing to do with this.
				pass

			# Whatever is left over is an input.
			else:
				self._Inputs.append(instr)
				# If we encounter an input instruction after
				# processing an output instruction, it is not
				# possible to convert to ladder.
				if matrixtype not in ('none', 'il'):
					matrixtype = 'il'


		# Rung is now classified. Make sure we return a valid type.
		if matrixtype == 'none':
			return 'empty'
		else:
			return matrixtype




	########################################################
	def _OutputsToMatrix(self):
		"""Convert the output list to a 1D matrix.
		"""
		outputs = [{'value' : instr['instrdef']['ladsymb'], 
				'addr' : instr['origparamlist'], 
				'monitor' : instr['instrdef']['monitor']}
					for instr in self._Outputs]
		self._OutputMatrix.extend(outputs)



	########################################################
	def _InputsToMatrixSingle(self):
		"""Convert the input list to a 2D matrix. This handles 
		outputs with single logic inputs only.
		"""

		# The current rung matrix.
		# The matrix is stored as a list of rows. That is:
		# [[row1], [row2], [row3], etc.]
		currentmatrix = [[]]

		# This holds all the matrices.
		# The finished matrix is stored as a list of colums. That is:
		# [[col1], [col2], [col3], etc.]
		matrixstack = []

		# Go through each input instruction.
		for instr in self._Inputs:


			# Find out what type of instruction it is.
			instclass = instr['instrdef']['class']

			# A STORE instruction starts a new block of logic.
			if (instclass == 'store'):
				matrixstack.append(currentmatrix)
				currentmatrix = [[]]
				currentmatrix = self._AppendInputCell(instr, currentmatrix)

			# AND / AND NOT adds a contact to the right of the current position. 
			elif (instclass == 'and'):
				currentmatrix = self._AppendInputCell(instr, currentmatrix)

			# OR / OR NOT adds a contact below the current position.
			elif (instclass == 'or'):
				newmatrix = [[]]
				newmatrix = self._AppendInputCell(instr, newmatrix)
				currentmatrix = self._MergeBelow(currentmatrix, newmatrix)
				currentmatrix = self._CloseBlock(currentmatrix)


			# ORSTORE combines the two previous blocks of logic.
			elif (instclass == 'orstr'):
				oldmatrix = matrixstack.pop()
				currentmatrix = self._MergeBelow(oldmatrix, currentmatrix)
				currentmatrix = self._CloseBlock(currentmatrix)

			# ANDSTORE combines the two previous blocks of logic.
			elif (instclass == 'andstr'):
				oldmatrix = matrixstack.pop()
				currentmatrix = self._MergeRight(oldmatrix, currentmatrix)

			# We ignore the rung (NETWORK) instruction since the program is
			# already broken up into separate rungs for us.
			elif (instclass == 'rung'):
				pass
			else:
				print('Error - Unexpected instruction class:  %s' % instclass)


		# Check to see if the input matrix can be created.
		if (len(matrixstack) == 1):
			# Save the resulting ladder.
			self._InputMatrix.extend(currentmatrix)
			return True
		else:
			return False


	########################################################
	def _InputsToMatrixMulti(self, matrixtype):
		"""Convert the input list to a 2D matrix. This handles 
		outputs with double or triple logic inputs only.
		A double type matrix may only have two (double) or 
		three (triple) input rows.
		Parameters: matrixtype (string) = 'double' for a maximum
			of two rows. 'triple' for a maximum of three rows.
		Returns: (boolean) = True if the matrix was assembled correctly.
		"""

		# The current rung matrix.
		# The matrix is stored as a list of rows. That is:
		# [[row1], [row2], [row3], etc.]
		currentmatrix = [[]]

		# This holds all the matrices.
		# The finished matrix is stored as a list of colums. That is:
		# [[col1], [col2], [col3], etc.]
		matrixstack = []


		# Go through each input instruction.
		for instr in self._Inputs:


			# Find out what type of instruction it is.
			instclass = instr['instrdef']['class']

			# A STORE instruction starts a new block of logic.
			if (instclass == 'store'):
				matrixstack.append(currentmatrix)
				currentmatrix = [[]]
				currentmatrix = self._AppendInputCell(instr, currentmatrix)

			# AND / AND NOT adds a contact to the right of the current position. 
			elif (instclass == 'and'):
				currentmatrix = self._AppendInputCell(instr, currentmatrix)

			# OR / OR NOT adds a contact below the current position.
			elif (instclass == 'or'):
				return False

			# ORSTORE combines the two previous blocks of logic.
			elif (instclass == 'orstr'):
				return False

			# ANDSTORE combines the two previous blocks of logic.
			elif (instclass == 'andstr'):
				return False

			# We ignore the rung (NETWORK) instruction since the program is
			# already broken up into separate rungs for us.
			elif (instclass == 'rung'):
				pass
			else:
				print('Error - Unexpected instruction class:  %s' % instclass)


		# Check to see if the matrix depth matches the expected type.
		if ((matrixtype == 'double') and (len(matrixstack) == 2)):
			matrix = matrixstack[-1]
			matrix.extend(currentmatrix)
			self._InputMatrix.extend(matrix)
			return True
		elif ((matrixtype == 'triple') and (len(matrixstack) == 3)):
			matrix = matrixstack[-2]
			matrix.extend(matrixstack[-1])
			matrix.extend(currentmatrix)
			self._InputMatrix.extend(matrix)
			return True
		else:
			return False





	########################################################
	def _AppendInputCell(self, instr, matrix):
		"""Add an instruction to a matrix. Pad out the other rows as necessary.
		Parameters: 
			instr (dictionary) = The instruction to be added.
			matrix (list) the matrix to add it to.
		Returns: (list) = The modified matrix, where:
			value = The instruction ladder symbol.
			addr = The parameter list addresses.
			monitor = The on line monitor type.
		"""
		matrixval = {'value' : instr['instrdef']['ladsymb'], 
				'addr' : instr['origparamlist'],
				'monitor' : instr['instrdef']['monitor']}
		# Add the instruction.
		matrix[0].append(matrixval)
		# Pad out the other rows.
		for row in matrix[1:]:
			row.append(None)
		return matrix



	########################################################
	def _MergeBelow(self, originalmatrix, newmatrix):
		"""Merge a new matrix below the current matrix.
		Parameters: originalmatrix (list) = The current matrix.
			newmatrix (list) = The new matrix to merge with
				the current one.
		"""

		# Find out which matrix is wider.
		originalwidth = len(originalmatrix[0])
		newwidth = len(newmatrix[0])

		# Pad out the smaller one to keep the result rectangular.
		# Original is wider than new.
		if (originalwidth > newwidth):
			for i in range(len(newmatrix)):
				row = newmatrix[i]
				if i == 0:
					row.extend([dict(self._HBarCell)] * (originalwidth - newwidth))
				elif row[-1] == None:
					row.extend([None] * (originalwidth - newwidth))
				elif row[-1]['value'] in self._VertBranches:
					row.extend([None] * (originalwidth - newwidth))
				else:
					row.extend([dict(self._HBarCell)] * (originalwidth - newwidth))

		# New is wider than old.
		elif (newwidth > originalwidth ):
			for i in range(len(originalmatrix)):
				row = originalmatrix[i]
				if i == 0:
					row.extend([dict(self._HBarCell)] * (newwidth - originalwidth))
				elif row[-1] == None:
					row.extend([None] * (newwidth - originalwidth))
				elif row[-1]['value'] in self._VertBranches:
					row.extend([None] * (newwidth - originalwidth))
				else:
					row.extend([dict(self._HBarCell)] * (newwidth - originalwidth))


		# Merge the new matrix into the old.
		originalmatrix.extend(newmatrix)

		return originalmatrix



	########################################################
	def _MergeRight(self, originalmatrix, newmatrix):
		"""Merge a new matrix to the right of the current matrix.
		Parameters: originalmatrix (list) = The current matrix.
			newmatrix (list) = The new matrix to merge with
				the current one.
		"""

		# Find out which matrix is higher.
		originalheight = len(originalmatrix)
		newheight = len(newmatrix)

		# Add the branches to the left side of the new matrix, but only
		# if the new matrix has multiple rows.
		if (newheight > 1):
			for row in newmatrix:
				row.insert(0, dict(self._BranchTRCell))

			# Fix up the first and last rows.
			newmatrix[0][0]['value'] = 'branchttr'
			newmatrix[-1][0]['value'] = 'branchr'


		# Pad out the smaller one to keep the result rectangular.
		# Original is higher than new.
		if (originalheight > newheight):
			newmatrix.extend([[None] * len(newmatrix[0]) for i in range(originalheight - newheight)])

		# New is higher than original.
		elif (newheight > originalheight):
			originalmatrix.extend([[None] * len(originalmatrix[0]) for i in range(newheight - originalheight)])


		# Now, merge the matrices.
		for original, new in zip(originalmatrix, newmatrix):
			original.extend(new)

		return originalmatrix



	########################################################
	def _CloseBlock(self, matrixblock):
		""" Join up the branches on the right side of a block. This
		version checks to see what the adjacent instruction on 
		the row is to see whether or not to join to it. If branches
		are already present, it leaves them as is.
		Parameters: matrixblock (list) = A matrix of instruction cells
			that needs the branches fixed up.
		Returns: (list) = The original matrix with the branches added.
		"""

		# Scan the rightmost column, looking to see if the widest
		# row is an instruction, and where the last row that is not
		# empty (in that column) is.
		widest = -1
		lastrow = 0
		# True if the widest row holds an instruction.
		wideinstr = False
		for i in range(len(matrixblock)):
			row = matrixblock[i]
			if (len(row) >= widest):
				if (row[-1] != None) and not (row[-1]['value'] in self._Branches):
					wideinstr = True
			# Find the bottom corner.
			if row[-1] != None:
				lastrow = i

		for i in range(len(matrixblock)):

			row = matrixblock[i]
			
			# If we were appending a column and are at the end
			# of adding branches, we need to pad out the row
			# to keep it rectangular.
			if (i > lastrow):
				if wideinstr:
					row.append(None)
			
			# Adjacent cell is empty.
			elif (row[-1] == None):
				if not wideinstr:
					row.pop()
				row.append(dict(self._VBarLCell))

			# Row is a joining horizontal bar and needs a 'T'.
			elif wideinstr and (row[-1]['value'] == 'hbar'):
				row.append(dict(self._BranchTLCell))

			# Row is an instruction and needs a 'T'
			elif wideinstr and (row[-1]['value'] not in self._Branches):
				row.append(dict(self._BranchTLCell))

			# Row is a branch and needs a 'T' appended to it.
			elif (not wideinstr) and (row[-1]['value'] in ['hbar', 'branchl']):
				row.pop()
				row.append(dict(self._BranchTLCell))

			# Row is not none and not a branch, so it must be an instruction.
			elif row[-1]['value'] not in self._Branches:
				if not wideinstr:
					row.pop()
				row.append(dict(self._BranchTLCell))

			# Row has a 'T', which is not appropriate here. If this
			# happens to be the top row, that will get fixed later.
			elif (not wideinstr) and row[-1]['value'] == 'branchttl':
				row.pop()
				row.append(dict(self._BranchTLCell))

			# Already has an appropriate branch not covered by the above.
			elif (not wideinstr) and row[-1]['value'] in self._Branches:
				pass

			# Add a vertical bar.
			else:
				if not wideinstr:
					row.pop()
				row.append(dict(self._VBarLCell))


		# Fix up the top row.
		matrixblock[0].pop()
		matrixblock[0].append(dict(self._BranchTTLCell))


		# Fix up the bottom row.
		matrixblock[lastrow].pop()
		matrixblock[lastrow].append(dict(self._BranchLCell))


		return matrixblock



	########################################################
	def GetLadderData(self):
		"""Return the rung matrix data, formatted for the client.
		This also returns the rung type, IL and rung comments.
		"""
		matrixdata = []

		# Add the inputs.
		for row in range(len(self._InputMatrix)):
			for col in range(len(self._InputMatrix[row])):
				# Ignore empty cells.
				if (self._InputMatrix[row][col]):
					cell = self._InputMatrix[row][col]

					# Construct the on-line monitoring characteristics. 
					# Boolean values.
					if cell['monitor'] in ('bool', 'booln'):
						monitor = (cell['monitor'], cell['addr'][0])
					# Word compares.
					elif cell['monitor'] in ('=', '!=', '>', '<', '>=', '<='):

						addra = cell['addr'][0]
						# Is the first item a valid address?
						if addra in DLCkDataTable.WordDataTable:
							addrc = 0
						# If not, assume it is a constant.
						else:
							addrc = addra
							addra = ''
						
						addrb = cell['addr'][1]
						# Is the second item a valid address?
						if addrb in DLCkDataTable.WordDataTable:
							addrd = 0
						# If not, assume it is a constant.
						else:
							addrd = addrb
							addrb = ''

						monitor = (cell['monitor'], addra, addrb, addrc, addrd)
					# No monitoring.
					else:
						monitor = ('none',)

					matrixdata.append({'type' : 'inp',
							'row' : row, 'col' : col,
							'addr' : cell['addr'],
							'value' : cell['value'],
							'monitor' : monitor
							})

		# Add the outputs.
		for row in range(len(self._OutputMatrix)):
			cell = self._OutputMatrix[row]
			# Construct the on-line monitoring characteristics. 
			# Boolean values.
			if cell['monitor'] in ('bool', 'booln'):
				monitor = (cell['monitor'], cell['addr'][0])
			# No monitoring.
			else:
				monitor = ('none',)

			matrixdata.append({'type' : 'outp',
					'row' : row,  'col' : 0,
					'addr' : cell['addr'],
					'value' : cell['value'],
					'monitor' : monitor
					})

		return {'rungtype' : self._MatrixType, 
				'comment' : ''.join(self._Comments), 
				'ildata' : self._ILList,
				'matrixdata' :matrixdata}



############################################################


############################################################
class LadderFormat:
	"""Format the instructions for ladder display.
	"""

	########################################################
	def __init__(self):
		pass


	############################################################
	def _CalcSig(self, sigdata):
		"""Calculate the signature (hash) of a block of subroutine.
		Parameters: sigdata (dict) = The data on which to calculate
			the hash. This is converted to a string before 
			calculating the hash.
		Returns: (string) = The calculated hash, or None if error.
		"""
		confighash = hashlib.md5()
		confighash.update(str(sigdata))
		return confighash.hexdigest()


	########################################################
	def _AssembleRung(self, rungdata):
		"""Assemble the instructions in a rung.
		Parmeters: rungdata (list) = A list of syntax dictionaries containing
			all the program data and the instruction definitions for each
			instruction. This is the output from the compiler.
		Returns: 
		"""
		# Assemble a single rung.
		RungMatrix = RungAssembler(rungdata)

		return RungMatrix.GetLadderData()


	########################################################
	def AssembleLadder(self, plcsyntax, plcprogname):
		"""Analyse the input parameter, and convert it into blocks of
		matrix data for display and editing.
		Parameters: 
		plcsyntax (dict) = A dictionary containing the 
			analysed PLC program syntax from the compiler.
		plcprogname (string) = Name of plc program for display on the
			header in the main subroutine.
		Returns: (dict) = A dictionary containing the assembled ladder
			matrix data. The keys are the name of the subroutine, 
			and the data is an additional dictionary. That dictionary 
			contains the following items: 

			subrdata - The subroutine matrix data.
			subrcomments - The subroutine comments.
			signature - A hash signature of the subroutine.
			addrlist - An *unvalidated* list of addresses used
				in that subroutine. These must still be filtered 
				for invalid addresses.
		"""
		# Save the plc program name.
		self._MainProgName = plcprogname

		plcprog = {}
		ladderlist = []

		# Go through each main and subroutine.
		for routine, runglist in plcsyntax.items():

			blockname = routine.strip()
			ladderlist = []
			subrcomments = ''
			firstrung = True

			# Go through each rung in a routine.
			for rung in runglist:
				# Assemble a rung of ladder.
				rungladder = self._AssembleRung(rung)

				# It this is a subroutine heading, then collect the comments.
				if firstrung and (rungladder['rungtype'] == 'sbr'):
					subrcomments = rungladder['comment']
				# Otherwise, add the rung to the list.
				else:
					ladderlist.append(rungladder)

				firstrung = False


			# Save the ladder and IL for that subroutine (or main).
			plcprog[blockname] = {}
			plcprog[blockname]['subrdata'] = ladderlist
			plcprog[blockname]['subrcomments'] = subrcomments
			plcprog[blockname]['signature'] = self._CalcSig(ladderlist)


		# return a dictionary containing the completed data.
		return plcprog


##############################################################################


