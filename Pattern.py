class Pattern():
	# Inputs the Pattern details, and sets the Pattern's attributes
	def __init__(self, patternID, patternName, blocks, pattern, lastModified):
		self.__pattern = pattern
		self.__patternID = patternID
		self.__patternName = patternName
		self.__blocks = blocks
		self.__lastModified = lastModified
	
	# Getters for the Pattern's attributes
	def get_PatternID(self):
		return self.__patternID
	
	def get_Pattern(self):
		return self.__pattern
	
	def get_Blocks(self):
		return self.__blocks

	def get_Pattern_Name(self):
		return self.__patternName
	
	def get_Last_Modified(self):
		return self.__lastModified
	
	# Inputs a Block and adds it to the correct column in self.__pattern
	def add_Block_to_Pattern(self, block):
		self.__pattern[block.get_Block_Number()].append(block)
	
	# Inputs a BlockID, and removes the corresponding Block from self.__pattern
	def remove_Block_from_Pattern(self, blockID):
		for column in self.__pattern:
			for block in column:
				if block.get_BlockID() == blockID:
					column.remove(block)
					return
	
	# Setters for the Block's attributes
	def set_Pattern(self, newPattern):
		self.__pattern = newPattern

	def set_Blocks(self, newBlocks):
		self.__blocks = newBlocks
	
	def set_Pattern_Name(self, patternName):
		self.__patternName = patternName
	
	def set_Last_Modified(self, lastModified):
		self.__lastModified = lastModified


