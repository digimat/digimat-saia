#############################################################################
# Project: 	MBLogic
# Module: 	PLCLad2ilr.py
# Purpose: 	Convert ladder to instruction list.
# Language:	Python 2.5
# Date:		15-May-2010.
# Ver:		14-Sep-2010.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin   <m.os.griffin@gmail.com>
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

"""This is used to convert a ladder matrix back into IL.
"""

from mbsoftlogicck import DLCkInstructions, DLCkTemplates


############################################################
class RungDisassembler:
	"""Convert a rung matrix to IL.
	"""

	########################################################
	def __init__(self, instrdeflist, rungmatrix):
		"""Params: instrdeflist: (list) = The instruction definition list
				which defines the complete instruction set.
			rungdata: (list) = The rung matrix.
		"""
		self._RungMatrix = rungmatrix
		# The instruction set look-up table.
		self._InstrDefs = instrdeflist

		# Collect all the inputs together.
		self._Inputs = []
		# Collect all the outputs together.
		self._Outputs = []
		# We convert the input list into a 2D matrix.
		self._InpMatrix = []


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
		self._VBranches = ('branchttr', 'branchtr', 'branchr',  'vbarr',
				'branchttl',  'branchtl', 'branchl', 'vbarl')

		# Branches which do *not* have a vertical component.
		self._HBranches = ('hbar')

		# Cells for horizontal rungs that are not themselves instructions.
		self._HStructureCells = ('hbar', None, 'none')


		# Cells that provide structure, but are not themselves instructions.
		self._StructureCells = ('branchttr', 'branchtr', 'branchr',  'vbarr',
				'branchttl',  'branchtl', 'branchl', 'vbarl', 
				'hbar', None, 'none')


	########################################################
	def _ClassifyMatrix(self):
		"""Categorise the matrix into input and output lists.
		"""
		# Filter the rung matrix for inputs and outputs and put them in their own lists.
		self._Inputs = [cell for cell in self._RungMatrix if cell['type'] == 'inp']
		self._Outputs = [cell for cell in self._RungMatrix if cell['type'] == 'outp']

		# Sort the output matrix.
		self._Outputs.sort(key=(lambda x: x['row']))

		# Check if the number of cells exceeds the permitted matrix dimensions.
		# The way we sort inputs limits the size of the matrix. This is not
		# related to any other size limitations elsewhere.
		# TODO: This needs more detailed handling.
		cols = [cell for cell in self._Inputs if cell['col'] > 99]
		if (len(cols) > 0):
			print('Input matrix sort overflow error.')
		
		# Sort the inputs. We sort by row and then col by multiplying
		# row by a factor and then adding it to column. This however inherently
		# limits the size of the matrix.
		self._Inputs.sort(key=(lambda x: (x['row'] * 100) + x['col']))


	########################################################
	def _GiveInpList(self, iplist):
		"""This is a generator function which is used to meter out
		input cells one at a time as we need them.
		Parameters: iplist (list) = The list of inputs.
		"""
		for i in iplist:
			yield i


	########################################################
	def _Make2DInputMatrix(self):
		"""Convert the input list into a 2D matrix. The list is
		assumed to be already sorted by row and column.
		"""

		# Check if there are any inputs to process.
		if len(self._Inputs) == 0:
			return

		maxrow = 0
		maxcol = 0
		# Find the maximum row and column.
		for record in self._Inputs:
			if record['row'] > maxrow:
				maxrow = record['row']
			if record['col'] > maxcol:
				maxcol = record['col']


		# Create the generator to give us input cell data one at a 
		# time on demand.
		inplist = self._GiveInpList(self._Inputs)

		# Get the first cell.
		cell = inplist.next()

		# Create the 2D matrix, including padding empty cells. 
		for row in range(maxrow + 1):
			matrixrow = []
			for col in range(maxcol + 1):

				# If we are at the same column, save the cell in
				# the matrix and get the next cell.
				if (cell != None) and (col == cell['col']) and (row == cell['row']):
					matrixrow.append([{'value': cell['value'], 'addr': cell['addr'], 'type': 'inp'}])
					try:
						cell = inplist.next()
					except:
						# We are out of cells.
						cell = None

				# Cells are missing, so we need to pad the row.
				else:
					matrixrow.append([{'value': 'none', 'addr': [], 'type': 'inp'}])

			# Add the latest row to the matrix.
			self._InpMatrix.append(matrixrow)




	########################################################
	def _MergeANDMatrixCell(self, sourcecell, mergecell):
		"""Reformat an instruction cell for its new location.
		Parameters: sourcecell (list) = The source cell.
			mergecell (list) = The cell which sourcecell is to be merged into.
		"""
		
		# If a new instruction type has been assigned, keep it,
		# otherwise, it must be an 'and'.
		mergesource = [{'type': 'and', 'addr': x['addr'], 'value': x['value']} if x['type'] == 'inp' else
		 		{'type': x['type'], 'addr': x['addr'], 'value': x['value']}for x in sourcecell]


		# Merge it into the cell at left.
		mergecell.extend(mergesource)


	########################################################
	def _CloseANDCells(self, anchor, closer):
		"""Fix up the series of collapsed column instructions to give them
		the correct type.
		Paramters: anchor (list) = The accumulated run of instructions.
			closer (string) = The cell value which terminated the run 
				of insructions.
		"""
		# The nature of the closure instruction determines how we terminate them.
		anchorsize = len(anchor)

		# We only have one instruction to handle.
		if anchorsize == 1:
			# OR
			if closer in ('branchtl', 'branchl'):
				anchor[0]['type'] = 'or'
			# AND
			elif closer == 'branchttr':
				anchor[0]['type'] = 'and'
			# STORE
			elif closer == 'branchttl':
				anchor[0]['type'] = 'store'

			else:
				# TODO: Handle this better.
				print('Error - unhandled anchor 1 case in CloseANDCells %s' % closer)
		# We have multiple instructions to handle.
		else:
			# Accumulate the branch.
			if closer in ('branchtl', 'branchl', 'branchttl'):
				# The first one has to be a store.
				if anchor[0]['type'] == 'inp':
					anchor[0]['type'] = 'store'
				# The rest will be and.
				for instr in anchor:
					if instr['type'] == 'inp':
						instr['type'] = 'and'

			# Append an ORSTORE of the closer indicates.
			if closer in ('branchtl', 'branchl'):
				anchor.append({'type': 'orstr', 'addr': [], 'value': 'orstr'})

		return anchor



	########################################################
	def _CollapseInputColumns(self, inpmatrix):
		"""This is used to help analyse the 2D input matrix. This scans through 
		the input matrix and collapses consecutive runs of adjacent (horizontally) 
		instructions to single cells. We also re-write the cells to classify them
		in more detail as to type. 
		"""

		# First, go through and merge adjacent instructions.
		collapsedmatrix = inpmatrix
		# Each row.
		for row in collapsedmatrix:
			# We will 'anchor' each column to the start of a new
			# run of instructions.
			anchor = None
			# Each collumn.
			cellcount = len(row)
			for cellcount in range(len(row)):

				cell = row[cellcount]

				# Classify the current cell.
				isinstr = (len(cell) > 1) or ((cell[0]['value'] not in self._StructureCells))

				# We are just starting a series of instructions.
				if isinstr and (anchor == None):
					anchor = cell

				# We are continuing a series of instructions.
				elif isinstr and (anchor != None):
					self._MergeANDMatrixCell(cell, anchor)
					row[cellcount] = [{'type': 'branch', 'value': 'hbar'}]

				# Ignore this, it's just a spacer.
				elif cell[0]['value'] == 'hbar':
					pass

				# We just ended a series of instructions.
				elif (not isinstr) and (anchor != None):
					self._CloseANDCells(anchor, cell[0]['value'])
					anchor = None

				# We are not working on a series of instructions.
				else:
					anchor = None


		# Eliminate columns which contain only padding.

		# This will keep track of the number of padding cells in each column.
		padding = [0] * len(collapsedmatrix[0])
		colcount = range(len(collapsedmatrix[0]))

		# Go through each row and column, and increment the padding
		# counter for that column if that cell contains a padding instruction.
		for row in collapsedmatrix:
			for col in colcount:
				if (row[col][0]['type'] == 'pad') or (row[col][0]['value'] == 'hbar'):
					padding[col] += 1


		# Check to see if any of the columns are just padding.
		rowcount = len(collapsedmatrix)
		if max(padding) >= rowcount:
			# Now go through the matrix and filter out padding columns.
			trimmedmatrix = []
			for row in collapsedmatrix:
				trimmedmatrix.append([cell[0] for cell in zip(row, padding) if cell[1] < rowcount])
		else:
			trimmedmatrix = collapsedmatrix		


		return trimmedmatrix


	########################################################
	def _RewriteORMatrixCell(self, sourcecell, mergecell):
		"""Reformat an instruction cell for its new location.
		Parameters: sourcecell (list) = The source cell.
			mergecell (list) = The cell which sourcecell is to be merged into.
		"""

		# Rewrite the source cell to make a copy. 
		sourceor = [{'type': x['type'], 'addr': x['addr'], 'value': x['value']} for x in sourcecell]
		
		# Merge it into the cell above.
		mergecell.extend(sourceor)



	########################################################
	def _AndStoreCloseBlock(self, cell):
		"""Close a block with an andstore instruction.
		"""
		cell.append({'type': 'andstr', 'addr' : [], 'value': 'andstr'})


	########################################################
	def _CollapseInputRows(self, matrix):
		""" This collapses adjacent linked rows into a single group.
		Rows are linked if they are connected by branches.
		"""
		# Go through the matrix in a reversed order. This effectively
		# turns the matrix "upside down" because it's easier this way. 
		rmatrix = list(reversed(matrix))

		# Number of rows in the matrix. We need to stop short of the top row however.
		maxrow = len(rmatrix) - 1
		rowtop = maxrow - 1

		# The first column needs special handling, because the left hand set
		# of branches are implied, rather than explicit.
		branchfix = 'branchl'
		for rownum in range(maxrow):
			row = rmatrix[rownum]

			# Is the next column the bottom end if a branch?
			# If so, move it "up" to the next row.
			if row[1][0]['value'] == 'branchl':
				# Add the instruction to the row above provided it is an instruction.
				if row[0][0]['value'] not in self._HStructureCells:
					self._RewriteORMatrixCell(rmatrix[rownum][0], rmatrix[rownum + 1][0])

				# For the top row, we need to fix it up with a horizontal wire rather
				# than a vertical branch.
				if rownum == rowtop:
					branchfix = 'hbar'
				# Fix up the branch.
				rmatrix[rownum + 1][1] = [{'type': 'branch', 'value': branchfix}]
				# Get rid of the old branch and instruction.
				rmatrix[rownum][0] = [{'type': 'pad', 'value': 'none'}]
				rmatrix[rownum][1] = [{'type': 'pad', 'value': 'none'}]

				

		# Now, handle the other columns.
		branchfixl = 'branchl'
		branchfixr = 'branchr'
		for rownum in range(maxrow):
			row = rmatrix[rownum]
			rowsize = len(row)

			# Go through the columns.
			leftisbranchr = False
			for colnum in range(1, rowsize - 1):
				rightisbranchl = row[colnum + 1][0]['value'] == 'branchl'
				leftisbranchr = row[colnum - 1][0]['value'] == 'branchr'

				if rightisbranchl and leftisbranchr:
					# Add the instruction to the row above.
					self._RewriteORMatrixCell(rmatrix[rownum][colnum], rmatrix[rownum + 1][colnum])

					# For the top row, we need to fix it up with a horizontal wire rather
					# than a veritcal branch.
					if rownum == rowtop:
						branchfixl = 'hbar'
						branchfixr = 'hbar'
						# Close the block with an ANDSTORE.
						self._AndStoreCloseBlock(rmatrix[rownum + 1][colnum])

					# Fix up the branch.
					rmatrix[rownum + 1][colnum + 1] = [{'type': 'branch', 'value': branchfixl}]
					rmatrix[rownum + 1][colnum - 1] = [{'type': 'branch', 'value': branchfixr}]

					# Get rid of the old branch and instruction.
					rmatrix[rownum][colnum] = [{'type': 'pad', 'value': 'none'}]
					rmatrix[rownum][colnum + 1] = [{'type': 'pad', 'value': 'none'}]
					rmatrix[rownum][colnum - 1] = [{'type': 'pad', 'value': 'none'}]
				

		collapsedmatrix = []
		# Go through the rows, and eliminate any which don't have any instructions.
		for rows in rmatrix:
			hasinstr = [x for x in rows if x[0]['value'] not in self._StructureCells]
			if len(hasinstr) > 0:
				collapsedmatrix.append(rows)


		# Restore the matrix back to the normal order before returning it.
		return list(reversed(collapsedmatrix))


	########################################################
	def _InpMatrixtoIL(self):
		"""Convert the 2D input matrix to IL.
		"""

		collapsedlist = self._InpMatrix
		# Limit the number of iterations we attempt.
		limitcounter = 0


		# Attempt to collapse the input matrix.
		while ((len(collapsedlist) > 1) or (len(collapsedlist[0]) > 1)) and limitcounter < 10:
			# Collapse consecutive instructions.
			collapsedlist = self._CollapseInputColumns(collapsedlist)
			# Collapse consecutive rows.
			collapsedlist = self._CollapseInputRows(collapsedlist)

			limitcounter += 1


		# Convert the matrix into IL.
		illist = []
		for instr in collapsedlist[0][0]:		# TODO: Convert this to a list compehension.
			params = ' '.join(instr['addr'])
			opcode = self._InstrDefs[instr['value']][instr['type']]
			illist.append('%s %s' % (opcode, params))


		return illist


	########################################################
	def _Inp1DMatrixtoIL(self, row):
		"""Convert a simple 1D input matrix to IL. This handles one row
		of a very simple rung with no branch instructions. 
		Parameters: row (integer) = The matrix row to extract, where 0 
		is the first row, 1 the second row, etc.
		"""

		# Filter out any horizontal bar elements.
		inpmatrix = [cell for cell in self._InpMatrix[row] if cell[0]['value'] not in self._HStructureCells]


		# This looks up the instruction, appends the parameters,
		# and then adds it to the list. The first cell must be
		# a STORE.
		illist = []
		cell = inpmatrix[0]
		illist.append('%s %s' % (self._InstrDefs[cell[0]['value']]['store'], 
						' '.join(cell[0]['addr'])))

		# Subsequent cells will be ANDs.
		subsequent = inpmatrix[1:]
		illist.extend(['%s %s' % (self._InstrDefs[cell[0]['value']]['and'], 
			' '.join(cell[0]['addr'])) for cell in subsequent])

		return illist


	########################################################
	def _Inp1DORMatrix(self):
		"""Convert a simple 1D matrix to IL where the instructions are
		all in a single column (OR). There must be exactly two matrix
		columns present.
		"""


		# Check to see that the beginning and ending branches are correct.
		branches = [row[1][0]['value'] for row in self._InpMatrix]
		if (branches[0] != 'branchttl') or (branches[-1] != 'branchl'):
			print('Bad start or end branch %s' % branches)	# TODO: Needs better handling.
		
		# Check the intermediate branches (if there are any).
		if len(branches) > 2:
			interbranch = branches[1:-2]
			badbranches = [branch for branch in interbranch if branch != 'branchtl']
			if len(badbranches) > 0:
				print('Bad branch instruction %s' % badbranches)	# TODO: Needs better handling.

		illist = []
		# Get the contact instructions. Drop empty rows.
		instr = [(row[0][0]['value'], row[0][0]['addr']) for row in self._InpMatrix 
						if row[0][0]['value'] not in self._HStructureCells]


		# Look up the instruction, append the parameters, 
		# and then add it to the list. 

		# The first cell must be a STORE.
		firstinstr = instr[0]
		illist.append('%s %s' % (self._InstrDefs[firstinstr[0]]['store'], 
						' '.join(firstinstr[1])))

		# Subsequent cells will be ORs.
		subsequent = instr[1:]
		illist.extend(['%s %s' % (self._InstrDefs[cell[0]]['or'], ' '.join(cell[1])) for cell in subsequent])


		return illist


	########################################################
	def _FindInpMatrixType(self, matrix):
		"""Classify the input matrix type into different catgories. 
		This lets use handle simple cases separately.
		Parameters: matrix (list) = The input matrix.
		Returns: (string) = A string code indicating the matrix type.
		"""
		# Check if there are no inputs at all.
		if len(self._InpMatrix) == 0:
			return 'noinpmatrix'

		# Check to see if it is a simple 1D row of ANDs.
		if len(self._InpMatrix) == 1:
			return 'andmatrix'

		# Now check to see if it is a simple 1D column of ORs.
		# At this point we are assuming it isn't a simple 1D row.

		# Find the length of the rows which are not exactly 2 columns wide.
		matrixlen = [len(x) for x in matrix if len(x) != 2]

		# This should be a 1D OR matrix.
		if len(matrixlen) == 0:
			return 'ormatrix'

		# At least one row has only one instruction. This isn't
		# possible if it's more than a single row.
		if min(matrixlen) < 2:
			return 'badmatrix'

		# This is a complex 2D matrix.
		if max(matrixlen) > 2:
			return 'complexmatrix'



	########################################################
	def GetILDataSingle(self):
		"""Return the rung IL data that we created from the matrix.
		The rung is expected to contain outputs of only the "single" logic
		input type. Inputs may contain branches.
		Return (string) = A single block of text containing the entire
			set of source code representing the rung matrix.
		"""
		# Classify the matrix items.
		self._ClassifyMatrix()
		# Make the inputs into a 2D matrix.
		self._Make2DInputMatrix()

		ilsource = []

		# Check to see what sort of matrix we are dealing with.
		inpmatrixtype = self._FindInpMatrixType(self._InpMatrix)

		# A simple case in one row. 
		if inpmatrixtype == 'andmatrix':
			# Add the inputs to the IL source for the rung.
			ilsource.extend(self._Inp1DMatrixtoIL(0))

		# A simple case in one column.
		elif inpmatrixtype == 'ormatrix':
			ilsource.extend(self._Inp1DORMatrix())
		
		# No inputs at all.
		elif inpmatrixtype == 'noinpmatrix':
			pass

		else:
			ilsource.extend(self._InpMatrixtoIL())

		# This looks up the instruction, appends the parameters,
		# and then adds it to the source list.
		ilsource.extend(['%s %s' % (self._InstrDefs[cell['value']]['outp1'], 
					' '.join(cell['addr'])) for cell in self._Outputs])

		# Convert the list of instructions to a single string
		# and return the resulting block of source code.
		return '%s\n' % '\n'.join(ilsource)



	########################################################
	def GetILDataDouble(self):
		"""Return the rung IL data that we created from the matrix.
		The rung is expected to contain only 1 output of the the "double"
		input type. There must be two logical input blocks and no 
		branch instructions.
		Return (string) = A single block of text containing the entire
			set of source code representing the rung matrix.
		"""
		# Classify the matrix items.
		self._ClassifyMatrix()
		# Make the inputs into a 2D matrix.
		self._Make2DInputMatrix()

		ilsource = []

		# Check to see if the matrix is valid. 
		if (len(self._InpMatrix) == 2):
			# Add the inputs to the IL source for the first row.
			ilsource.extend(self._Inp1DMatrixtoIL(0))
			# Add the inputs to the IL source for the second row.
			ilsource.extend(self._Inp1DMatrixtoIL(1))
		else:
			print('Error - Invalid number of rows: %s  for double rung.' % len(self._InpMatrix))


		# We can only have one output in this rung.
		if (len(self._Outputs) != 1):
			print('Error - invalid number of outputs in rung.')	# TODO: Need better error handling

		# This looks up the instruction, appends the parameters,
		# and then adds it to the list.
		cell = self._Outputs[0]
		ilsource.append('%s %s' % (self._InstrDefs[cell['value']]['outp2'], ' '.join(cell['addr'])))


		# Convert the list of instructions to a single string
		# and return the resulting block of source code.
		return '%s\n' % '\n'.join(ilsource)




	########################################################
	def GetILDataTriple(self):
		"""Return the rung IL data that we created from the matrix.
		The rung is expected to contain only 1 output of the the "triple"
		input type. There must be three logical input blocks and no 
		branch instructions.
		Return (string) = A single block of text containing the entire
			set of source code representing the rung matrix.
		"""
		# Classify the matrix items.
		self._ClassifyMatrix()
		# Make the inputs into a 2D matrix.
		self._Make2DInputMatrix()

		ilsource = []

		# Check to see if the matrix is valid. 
		if (len(self._InpMatrix) == 3):
			# Add the inputs to the IL source for the first row.
			ilsource.extend(self._Inp1DMatrixtoIL(0))
			# Add the inputs to the IL source for the second row.
			ilsource.extend(self._Inp1DMatrixtoIL(1))
			# Add the inputs to the IL source for the second row.
			ilsource.extend(self._Inp1DMatrixtoIL(2))
		else:
			print('Error - Invalid number of rows: %s  for triple rung.' % len(self._InpMatrix))


		# We can only have one output in this rung.
		if (len(self._Outputs) != 1):
			print('Error - invalid number of outputs in rung.')	# TODO: Need better error handling

		cell = self._Outputs[0]
		ilsource.append('%s %s' % (self._InstrDefs[cell['value']]['outp3'], ' '.join(cell['addr'])))


		# Convert the list of instructions to a single string
		# and return the resulting block of source code.
		return '%s\n' % '\n'.join(ilsource)


############################################################



############################################################
class SubrAnalyser:
	"""Convert the source code for a complete subroutine into IL source.
	The subroutine may consist of a mixture of raw ladder matrix and IL.
	"""


	########################################################
	def __init__(self, instrdeflist):
		"""Params: instrdeflist: (list) = The instruction definition list
				which defines the complete instruction set.
		"""
		# Categories of valid ladder symbols. These have the following meanings:
		# inp = Input (any kind). outp = Output (any kind). 
		# none = Should not appear in a ladder matrix.
		self._LadderSymCategory = {'and' : 'inp', 'or' : 'inp', 'store' : 'inp', 
				'andstr' : 'inp', 'orstr' : 'inp', 
				'for' : 'outp', 'next' : 'outp', 'output0' : 'outp', 
				'output1' : 'outp', 'output2' : 'outp', 'output3' : 'outp',
				'comment' : 'none', 'rung' : 'none', 'sbr' : 'none'}


		# Make the instruction set look-up table.
		self._InstrDefs = self._MakeInstrSet(instrdeflist)




	########################################################
	def _MakeInstrSet(self, instrdeflist):
		"""Convert the instruction definition list into a dictionary
		which lets us look up each ladder symbol directly.
		Parameters: instrdeflist (list) = The instruction definition list
			which defines the complete instruction set. 
		"""
		instrdefs = {}
		for instr in instrdeflist:
			# Check if the instruction is not already in the dictionary.
			# Keys must be unique.
			if instrdefs.get(instr['ladsymb']) == None:
				instrdefs[instr['ladsymb']] = {'category' : self._LadderSymCategory[instr['class']],
								'and' : None, 'or' : None, 'store' : None, 
								'andstr' : None, 'orstr' : None,
								'outp1' : None, 'outp2' : None, 'outp3' : None}

			# Now, fill in the appropriate opcodes. A ladder symbol can have more than
			# one opcode if it is an input. We also have to categorise the outputs 
			# according to the type of rung (single, double, triple) they are compatible with.
			# This should give us something that looks like the following: 
			# {'noc' : {'category' : 'inp', 'and' : 'AND', 'or' : 'OR', 
			#	'store' : 'STR', 'outp1' : None, 'outp2' : None, 'outp3' : None}, etc.
			laddef = instrdefs[instr['ladsymb']]
			# Instruction is an input in an AND matrix location.
			if instr['class'] == 'and':
				laddef['and'] = instr['opcode']
			# Instruction is an input in an OR matrix location.
			elif instr['class'] == 'or':
				laddef['or'] = instr['opcode']
			# Instruction is an input in a STORE matrix location.
			elif instr['class'] == 'store':
				laddef['store'] = instr['opcode']
			# Instruction is an input in an ANDSTR matrix location.
			elif instr['class'] == 'andstr':
				laddef['andstr'] = instr['opcode']
			# Instruction is an input in an ORSTR matrix location.
			elif instr['class'] == 'orstr':
				laddef['orstr'] = instr['opcode']
			# Instruction is an output compatible with a "single" rung.
			elif instr['class'] in ('output0', 'output1', 'for', 'next'):
				laddef['outp1'] = instr['opcode']
			# Instruction is an output compatible with a "double" rung.
			elif instr['class'] == 'output2':
				laddef['outp2'] = instr['opcode']
			# Instruction is an output compatible with a "triple" rung.
			elif instr['class'] == 'output3':
				laddef['outp3'] = instr['opcode']

			# These instructions are not directly in a ladder matrix. We just
			# drop these definitions.
			elif instr['class'] in ('comment', 'rung', 'sbr'):
				pass
			else:
				# We don't know what this instruction is.
				print('Unknown instruction class %s' % instr['class'])

		return instrdefs



	########################################################
	def DecodeSubroutine(self, subrmatrix):
		"""Decode a subroutine matrix from the client and convert
		it to IL.
		Parameters: subrmatrix (dict) = A dictionary containing
			the subroutine matrix data from the client.
		Returns: subroutinecomments (string) = Subroutine comments,
			runglist (list) = List of rungs.
		"""
		# The name of the subroutine.
		self._SubroutineName = subrmatrix['subrname']
		# The subroutine comments.
		self._SubrComments = subrmatrix['subrcomments']
		# The signature (checksum) of the subroutine.
		self._Signature = subrmatrix['signature']
		# The list of rung data.
		self._RungData = subrmatrix['subrdata']

		self._RungList = []

		# The rung number.
		rungnumber = 0

		# Convert each rung of data into the source IL list.
		for rung in self._RungData:
			# Auto-number the rungs.
			rungnumber += 1

			# See what sort of rung (il or ladder) this is.
			# This is an empty rung.
			if (rung['rungtype'] == 'empty'):
				ildata = []
			# Rung is IL.
			elif (rung['rungtype'] == 'il'):
				ildata = rung['ildata']
			# Rung is ladder with "single" outputs.
			elif (rung['rungtype'] == 'single'):
				self._Decoder = RungDisassembler(self._InstrDefs, rung['matrixdata'])
				ildata = self._Decoder.GetILDataSingle()
			# Rung is ladder with "double" outputs.
			elif (rung['rungtype'] == 'double'):
				self._Decoder = RungDisassembler(self._InstrDefs, rung['matrixdata'])
				ildata = self._Decoder.GetILDataDouble()
			# Rung is ladder with "triple" outputs.
			elif (rung['rungtype'] == 'triple'):
				self._Decoder = RungDisassembler(self._InstrDefs, rung['matrixdata'])
				ildata = self._Decoder.GetILDataTriple()
			# Rung type is unknown.
			else:
				print('Unknown rung type.')	# TODO: Need better error handling

			# Get the rest of the rung data.
			newrungdata = {'comment' : rung['comment'],
				'rungnumber' : rungnumber,
				'ildata' : ildata}

			# Add the rung to the list of rungs.
			self._RungList.append(newrungdata)
			
		return self._SubroutineName, self._SubrComments, self._RungList

############################################################


############################################################
"""Assemble the IL components into a complete subroutine.
"""

def AssembleSubr(subrname, subrcomments, ildata):
	"""Assemble the subroutine components into a list of 
	subroutine data.
	Parameters: subrname (string) = The subroutine name.
		subrcomments (list) = The subroutine comments.
		ildata (list) = The subroutine IL source.
	Returns (list) = The formatted subroutine IL, including subroutine name and comments.
	"""
	sbrblock = []
	# 'main' is not a subroutine.
	if subrname != 'main':
		sbrblock.append('%s %s' % (DLCkTemplates.InstrTypeLookup['sbr'], subrname))
	sbrblock.append('%s %s' % (DLCkTemplates.InstrTypeLookup['comment'], subrcomments))
	# We have to flatten the nested list.
	# TODO: Change the list flattening technique to use chain.
	sbrblock.extend(sum([il['ildata'] for il in ildata], []))
	return sbrblock



############################################################


