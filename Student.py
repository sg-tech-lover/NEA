class Student():
	# Inputs the Block details, and sets the Block's attributes
	def __init__(self, studentFirstname, studentSurname):
		self.__studentID = None
		self.__studentFirstname = studentFirstname
		self.__studentSurname = studentSurname
		self.__subjects = []
	
	# Inputs a Subject, and adds it to the StudentSubjects attribute
	def add_to_Student_Subjects(self, subject):
		self.__subjects.append(subject)
	
	# Getters for the Student's attributes
	def get_Student_Firstname(self):
		return self.__studentFirstname
	
	def get_Student_Subjects(self):
		return self.__subjects	
	
	def get_StudentID(self):
		return self.__studentID
	
	def get_Student_Surname(self):
		return self.__studentSurname

	# Setters for the Student's attributes
	def set_Student_Firstname(self, studentFirstname):
		self.__studentFirstname = studentFirstname
	
	def set_StudentID(self, studentID):
		self.__studentID = studentID

	def set_Student_Surname(self, studentSurname):
		self.__studentSurname = studentSurname
	
	def set_Student_Subjects(self, subjects):
		self.__subjects = subjects
	

