class Block():
	# Inputs the Block details, and sets the Block's attributes
	def __init__(self, subjectID, blockID, populationID):
		self.__subjectID = subjectID
		self.__blockID = blockID
		self.__patternID = -1
		self.__blockNumber = -1
		self.__populationID = populationID
	
	# Getters for the Block's attributes
	def get_BlockID(self):
		return self.__blockID
	
	def get_SubjectID(self):
		return self.__subjectID
	
	def get_PatternID(self):
		return self.__patternID
	
	def get_Block_Number(self):
		return self.__blockNumber
	
	def get_PopulationID(self):
		return self.__populationID
	
	# Setters for the Block's attributes
	def set_BlockID(self, blockID):
		self.__blockID = blockID
	
	def set_SubjectID(self, subjectID):
		self.__subjectID = subjectID
	
	def set_PatternID(self, patternID):
		self.__patternID = patternID
	
	def set_Block_Number(self, blockNumber):
		self.__blockNumber = blockNumber
	
	def set_PopulationID(self, populationID):
		self.__populationID = populationID

