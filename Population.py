from Subject import Subject
from Student import Student
from Pattern import Pattern
from Block import Block

class Population():
	# Inputs the Population details, and sets the Population's attributes
	def __init__(self, populationName, options, lastModified):
		self.__populationID = None
		self.__populationName = populationName
		self.__students = []
		self.__subjects = []
		self.__patterns = []
		self.__lastModified = lastModified
		self.__options = options
	
	# Getters for the Population's attributes
	def get_Options(self):
		return self.__options

	def get_Patterns(self):
		return self.__patterns

	def get_Last_Modified(self):
		return self.__lastModified
	
	def get_PopulationID(self):
		return self.__populationID
	
	def get_Population_Name(self):
		return self.__populationName
	
	def get_Subjects(self):
		return self.__subjects
	
	def get_Students(self):
		return self.__students

	# Inputs either a list of Subject objects, or a singular Subject object, and adds this to the subjects attribute
	def add_to_Subjects(self, newSubjects):
		if type(newSubjects) is list:
			self.__subjects += newSubjects
		else:
			self.__subjects.append(newSubjects)
	
	# Setters for the Population's attributes
	def set_Options(self, options, lastModified):
		self.__options = options
		self.__lastModified = lastModified

	def set_PopulationID(self, populationID):
		self.__populationID = populationID
	
	def set_Students(self, students, lastModified):
		self.__students = students
		self.__lastModified = lastModified
	
	def set_Subjects(self, subjects, lastModified):
		self.__subjects = subjects
		self.__lastModified = lastModified
	
	def set_Patterns(self, patterns, lastModified):
		self.__patterns = patterns
		self.__lastModified = lastModified
	
	def set_Population_Name(self, populationName, lastModified):
		self.__populationName = populationName
		self.__lastModified = lastModified

