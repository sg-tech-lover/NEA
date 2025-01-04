class Subject():
	# Inputs the Subject details, and sets the Subject's attributes
	def __init__(self, name, ID, maxBlocks):
		self.__subjectName = name
		self.__subjectID = ID
		self.__maxBlocks = maxBlocks

	# Getters for the Subject's attributes
	def get_max_Blocks(self):
		return self.__maxBlocks
	
	def set_max_Blocks(self, maxBlocks):
		self.__maxBlocks = maxBlocks
	
	# Setters for the Subject's attributes
	def get_SubjectID(self):
		return self.__subjectID
	
	def get_Subject_Name(self):
		return self.__subjectName
	
	def set_Subject_Name(self, subjectName):
		self.__subjectName = subjectName

