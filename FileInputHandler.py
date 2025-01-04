from os.path import exists

# Class that handles importing data from a user-selected file
class FileInputHandler():
	# Defines the file extensions supported by the class
	ACCEPTED_EXTENSIONS = ["txt", "csv"]
	def __init__(self):
		pass

	# Inputs the file path of a file, and returns the file extension
	def get_extension(self, file_path:str):
		for index in range(len(file_path)-1, -1, -1):
			if file_path[index] == ".":
				return file_path[index+1:]

	# Inputs the file path of a file, and returns whether or not the file is valid
	def check_valid_file(self, file_path:str):
		if not exists(file_path):
			raise Exception("Error. File not found.")
		file_extension = self.get_extension(file_path)
		if not(file_extension in FileInputHandler.ACCEPTED_EXTENSIONS):
			raise Exception("Error. Invalid file type - please convert the file to one of the following: " + ", ".join(FileInputHandler.ACCEPTED_EXTENSIONS))
	
	# Inputs a file path and imports it, returning the data correctly formatted
	def import_new_Population(self, file_path:str):
		population = []
		subjects = set()
		# Checks if the file paths is valid
		self.check_valid_file(file_path)

		# Opens the file
		with open(file_path, "r") as file:
			for line in file:
				# Each line will have the following format: Firstname, Surname, Subject1, Subject2, ...
				student = line.strip().split(",")
				population.append(student)
				for subject in student[2:]:
					if subject:
						subjects.add(subject)
		
		# Returns the formatted data
		return subjects, population

