from DatabaseController import DatabaseController
from FileInputHandler import FileInputHandler
from Subject import Subject
from Student import Student
from Population import Population
from Block import Block
from Pattern import Pattern
from PriorityQueue import PriorityQueue
from copy import deepcopy
from random import randint

class BackEnd():

	# Constant that specifies how many times the program will try to generate a Pattern
	GENERATOR_LOOPS = 5

	# Inputs a path to the database, and creates the connection
	def __init__(self, dbPath):
		self.dbController = DatabaseController(dbPath)
		self.population = None

	# Inputs a list, and returns a shuffled copy of it
	def shuffle(arr:list):
		# Copies the list
		temp = deepcopy(arr)
		newArr = []
		
		# Runs while elements are still in the copy of the list
		while temp:
			# Get a random index from the list
			index = randint(0, len(temp)-1)
			# Adds the corresponding value to the shuffled list
			newArr.append(temp[index])
			# Removes the added value from the copy of the list
			temp.remove(temp[index])
		
		# Returns the shuffled list
		return newArr

	# Inputs a PatternName, then creates a new Pattern (both as a class and as a record in the database)
	def create_blank_Pattern(self, patternName):
		lastModified = self.get_current_time()
		patternID = self.dbController.add_new_Pattern(patternName, lastModified, self.population.get_PopulationID())
		pattern = Pattern(patternID, patternName, [], [[] for i in range(self.population.get_Options())], lastModified)
		self.population.set_Patterns(self.population.get_Patterns() + [pattern], self.population.get_Last_Modified())
		return patternID

	# Inputs a BlockID and a PatternID, and removes the specified Block instance from the specified Pattern instance, and tells the database to remove the appropriate record
	def delete_Block(self, blockID, patternID):
		self.dbController.delete_Block(blockID)
		for pattern in self.population.get_Patterns():
			if pattern.get_PatternID() == patternID:
				pattern.remove_Block_from_Pattern(blockID)
	
	# Inputs a BlockID, SubjectID and PatternID, then updates the corresponding Block instance and database record with the new SubjectID. 
	def update_Block_using_SubjectID(self, blockID, subjectID, patternID):
		for pattern in self.population.get_Patterns():
			if pattern.get_PatternID() == patternID:
				break
		for column in pattern.get_Pattern():
			for block in column:
				if block.get_BlockID() == blockID:
					block.set_SubjectID(subjectID)
					lastModified = self.get_current_time()
					pattern.set_Last_Modified(lastModified)
					self.dbController.update_SubjectID_for_Block(blockID, subjectID)
					self.dbController.set_Last_Modified_from_PatternID(pattern.get_PatternID(), lastModified)
					return

	# Inputs a BlockID, SubjectName and PatternID, then updates the corresponding Block instance and database record with the correct SubjectID for that Subject.
	def update_Block(self, blockID, subjectName, patternID):
		for subject in self.population.get_Subjects():
			if subject.get_Subject_Name() == subjectName:
				break

		self.update_Block_using_SubjectID(blockID, subject.get_SubjectID(), patternID)

	# Inputs a PatternID and index (BlockNumber), then creates a new blank Block record and instance with those parameters.
	def create_blank_Block(self, patternID, index):
		# Adds the new record to the database, and updates it with the correct details
		blockID = self.dbController.add_new_Block(0, self.population.get_PopulationID())
		self.dbController.update_Block_Number_for_Block(blockID, index)
		self.dbController.update_PatternID_for_Block(blockID, patternID)

		# Creates the new Block instance and updates it with the correct details
		block = Block(0, blockID, self.population.get_PopulationID())
		block.set_Block_Number(index)

		for pattern in self.population.get_Patterns():
			if pattern.get_PatternID() == patternID:
				break
		
		# Adds the new Block instance to the correct Pattern instance
		pattern.add_Block_to_Pattern(block)
		return blockID

	# Inputs a list and returns a generator object that yields every possible permutation of that list
	def permutations(self, arr):
		pool = tuple(arr)
		n = len(pool)
		# Creates a list of indices (that are used to refer back to the values in the array)
		indices = list(range(n))

		# Creates a list of possible values for each position on the list (e.g. position 0 can have 9 values, position 1 can have 8 values etc.)
		cycles = list(range(n, 0, -1))
		
		# Returns the first possible ordering of the list
		yield tuple(pool[i] for i in indices[:n])
		while n:

			# Loops backwards through the cycles list
			for i in reversed(range(n)):

				# Decrements the appropriate cycles value by 1
				cycles[i] -= 1

				# If it is zero, then all of the possible values for this particular index have been exhausted
				if cycles[i] == 0:
					# Shuffles the indices (that have been used for the tail of the list) by one
					indices[i:] = indices[i+1:] + indices[i:i+1]
					# Returns the value in cycles back to its original value (so that the loop can continue again)
					cycles[i] = n - i

				# If it is not zero, then swap the indices specified to generate the "next item" in the possible orderings
				else:
					j = cycles[i]
					indices[i], indices[-j] = indices[-j], indices[i]

					# Yields the next item
					yield tuple(pool[i] for i in indices[:n])
					break
			
			# No more permutations are possible
			else:
				return

	# Inputs a PatternID and runs a test on it, returning the result of the test
	def test_Pattern_using_PatternID(self, patternID):
		for pattern in self.population.get_Patterns():
			if pattern.get_PatternID() == patternID:
				break
		
		# Formats the pattern to be in terms of SubjectIDs so that the test_Pattern function can deal with it properly
		blockPattern = pattern.get_Pattern()
		for column in range(len(blockPattern)):
			for block in range(len(blockPattern[column])):
				blockPattern[column][block] = blockPattern[column][block].get_SubjectID()
		
		return self.test_Pattern(blockPattern)

	# Inputs a pattern in the format [[Subject1_ID, Subject2_ID, ...], [Subject1ID, ....], ...] and returns how many Students are satisfied with the pattern, along with the Subject combinations that haven't been satisfied
	def test_Pattern(self, blockPattern):
		# Sets all the variables to their initial values
		studentsSatisfied = 0
		totalStudents = len(self.population.get_Students())

		# Stores the Subject combinations that have already worked/failed
		subjectCombinationsSatisfied = []
		subjectCombinationsNotSatisfied = []

		# Loops through every Student in the Population
		for student in self.population.get_Students():

			# Gets a list of the SubjectIDs of the Subjects the Student wants to study, sorted by SubjectID
			subjects = sorted([subject.get_SubjectID() for subject in student.get_Student_Subjects()])

			# Checks if this combination has been seen already. If it has, then edit the respective variables
			if subjects in subjectCombinationsSatisfied:
				studentsSatisfied += 1
			elif subjects in subjectCombinationsNotSatisfied:
				continue

			# Otherwise, checks if the current combination is satisfied
			else:
				# If this Student wants to study less than the maximum number of Subjects, then this adds the dummy SubjectID of 0 to the Student's current Subjects 
				while len(subjects) < self.population.get_Options():
					subjects = [0] + subjects

				# Creates a pattern template, which is a copy of the pattern with all SubjectIDs not corresponding to the Student removed
				patternTemplate = []
				for column in blockPattern:
					# Adds the dummy SubjectID to each column. Uses a set to ensure no repeats in each column
					patternTemplate.append(set([0]))
					for subjectID in column:
						if subjectID in subjects:
							patternTemplate[-1].add(subjectID)
				
				# Loops through all the possible permutations of the Student's Subjects
				for permutation in self.permutations(subjects):
					valid = True
					
					# Checks if the current permutation is valid.
					for index in range(len(permutation)):

						# If any of the permutations values isn't in the current column, then this permutation isn't valid
						if not(permutation[index] in patternTemplate[index]):
							valid = False
							break
					
					# If the current permutations didn't fail, then this Student's Subjects must be valid and successful
					if valid:
						subjectCombinationsSatisfied.append(sorted([subject for subject in subjects if subject != 0]))
						studentsSatisfied += 1
						break
				
				# If none of the permutations were successful, then this Student's Subjects were not supported by the Pattern
				if not valid:
					subjectCombinationsNotSatisfied.append(sorted([subject for subject in subjects if subject != 0]))
		
		# Loops through each combination of Subjects that weren't satisfied and replaces each SubjectID with the correct SubjectName
		for index in range(len(subjectCombinationsNotSatisfied)):
			subjectCombinationsNotSatisfied[index] = [self.dbController.get_Subject_Name_From_SubjectID(subject) for subject in subjectCombinationsNotSatisfied[index]]

		# Returns the final test data
		return studentsSatisfied, totalStudents, subjectCombinationsNotSatisfied

	# Inputs a PatternID and deletes the appropriate records and instances corresponding to that Pattern
	def delete_Pattern(self, patternID):
		# Deletes the records in the database
		self.dbController.delete_Blocks_in_Pattern(patternID)
		self.dbController.delete_Pattern(patternID)

		# Removes the Pattern instance from the Population
		self.population.set_Patterns([pattern for pattern in self.population.get_Patterns() if pattern.get_PatternID() != patternID], self.population.get_Last_Modified())

	# Gets a list of all of the Patterns corresponding to the current Population selected. Returns a list of [PatternID, PatternName]
	def get_Patterns(self):
		patterns = self.population.get_Patterns()
		patternData = []

		# First checks if any Patterns exist
		if patterns == []:
			return patternData
		else:
			
			# If Patterns exist, then loops through all of the Patterns and adds the data formatted correctly to patternData
			for pattern in patterns:
				if pattern.get_Last_Modified() == sorted([pattern.get_Last_Modified(), self.population.get_Last_Modified()])[1]:
					patternData.append([pattern.get_PatternID(), pattern.get_Pattern_Name()])
			
			# Returns the list of Patterns
			return patternData

	# Inputs a Student's details, and creates the records and instances
	def add_new_Student(self, studentFirstName, studentSurname, choices):
		# Creates the Student instance
		student = Student(studentFirstName, studentSurname)
		newChoices = []

		# Loops through the SubjectIDs in choices and gets the appropriate Subject instances for the Student, updating the Student instance
		for choice in choices:
			for subject in self.population.get_Subjects():
				if subject.get_Subject_Name() == choice:
					newChoices.append(subject)
					break
		student.set_Student_Subjects(newChoices)

		# Creates the record in the database, and sets the StudentID of the instance
		studentID = self.dbController.add_new_Student(student, self.population.get_PopulationID())
		student.set_StudentID(studentID)

		# Adds the appropriate records in the database for the Student's choices
		for subject in newChoices:
			self.dbController.add_new_SubjectStudent(subject.get_SubjectID(), studentID)
		
		# Updates the LastModified fields in the Population instance and database
		lastModified = self.get_current_time()
		self.population.set_Students(self.population.get_Students() + [student], lastModified)
		self.dbController.update_Population_Name(self.population.get_PopulationID(), self.population.get_Population_Name(), self.population.get_Last_Modified())

	# Inputs a new SubjectName and constraints, and creates the new Subject in the database
	def add_new_Subject(self, subjectName: str, constraints: dict):
		subjectID = self.dbController.add_new_Subject(subjectName)
		self.dbController.reset_Subject_Constraints(constraints, subjectID)

	# Inputs a PatternID and returns all the data about the Pattern in the format [name, pattern], where pattern is in the format [[[Subject1Name, BlockID], [Subject2Name, BlockID], ...], [[Subject1Name, BlockID], [Subject3Name, BlockID], ...], ...]
	def get_Pattern(self, patternID):
		# Gets the correct Pattern instance
		for pattern in self.population.get_Patterns():
			if pattern.get_PatternID() == patternID:
				break

		# Stores the pattern data that will be returned at the end
		patternData = []

		# Loops through each column in the pattern
		for optionBlock in pattern.get_Pattern():

			# Adds an empty list to the pattern data
			patternData.append([])

			# Loops through every block in the column
			for block in optionBlock:
				# Initially sets SubjectName to an empty string, in case the Subject does not exist
				subjectName = ""

				# Loops through every Subject to check if the SubjectID matches
				for subject in self.population.get_Subjects():

					# If the SubjectID matches, then the SubjectName is fetched from the instance
					if subject.get_SubjectID() == block.get_SubjectID():
						subjectName = subject.get_Subject_Name()
						break
				
				# Adds the correct data to the last list in patternData
				patternData[-1].append((subjectName, block.get_BlockID()))
		
		# Returns the name and the pattern
		return pattern.get_Pattern_Name(), patternData

	# Inputs a PopulationName and maximum number of options, and creates the correct records
	def create_blank_Population(self, populationName: str, options: int):
		self.get_Population_from_db(self.dbController.add_new_Population(populationName, options, self.get_current_time()))

	# Gets details of all the Populations stored in the database in the format {Population1Name: {SubjectsNo: x, StudentNo: y}, Population1Name:{SubjectsNo: x, StudentNo: y}, ...}
	def get_Populations(self):
		# Gets all of Populations stored in the database
		populations = self.dbController.get_all_Populations()[1:]
		populationData = {}

		# Checks if any Populations exist in the database
		try:
			population = populations[0]

		# Runs if no Populations exist
		except BaseException:
			return populationData
	
		# If Populations exist, it loops through every Population and gets the details about each Population
		for population in populations:
			totalStudents = len(self.dbController.get_Students_in_Population(population[0]))
			totalSubjects = len(self.dbController.get_Subjects_in_Population(population[0]))

			# Adds the Population and its data to the dictionary
			populationData[population[1]] = {"Number of Students":totalStudents, "Number of Subjects being studied":totalSubjects, "ID":population[0]}
		
		# Returns the dictionary
		return populationData

	# Inputs a SubjectID, SubjectName and MaxBlocks, then updates the appropriate record and instance with the new values
	def edit_Subject_details(self, subjectID, subjectName, maxBlocks):
		# If a population has already been selected, then edit the Subject instance stored in the Population
		if self.population:
			for subject in self.population.get_Subjects():
				if subject.get_SubjectID() == subjectID:
					break
			subject.set_Subject_Name(subjectName)
			subject.set_max_Blocks(maxBlocks)
		
		# Otherwise, create a new Subject instance with the supplied data
		else:
			subject = Subject(subjectName, subjectID, maxBlocks)
		
		# Updates the appropriate record in the database
		self.dbController.update_Subject(subject)

	# Inputs a StudentID and new Student Details, then updates the appropriate record and instance with the new values
	def edit_Student_details(self, studentID, studentFirstName, studentSurname, choices):
		
		# Gets the correct Student instance
		for student in self.population.get_Students():
			if student.get_StudentID() == studentID:
				break
		
		# Updates the attributes of the Student instance
		student.set_Student_Firstname(studentFirstName)
		student.set_Student_Surname(studentSurname)

		# Loops through the new choices given to get the correct Subject instances
		newChoices = []
		for choice in choices:
			for subject in self.population.get_Subjects():
				if subject.get_Subject_Name() == choice:
					newChoices.append(subject)
					break
		
		# Updates the Student's Subjects
		student.set_Student_Subjects(newChoices)

		# Updates the appropriate records in the database
		self.dbController.update_Student(student)

		# Updates the Population instance and record with the new timestamp
		lastModified = self.get_current_time()
		self.population.set_Students(self.population.get_Students(), lastModified)
		self.dbController.update_Population_Name(self.population.get_PopulationID(), self.population.get_Population_Name(), self.population.get_Last_Modified())

	# Inputs a new PopulationName and updates the Population instance and record
	def set_new_Population_Name(self, populationName):
		lastModified = self.get_current_time()
		self.dbController.update_Population_Name(self.population.get_PopulationID(), populationName, lastModified)
		self.population.set_Population_Name(populationName, lastModified)

	# Inputs a new Population Options and updates the Population instance and record
	def set_new_Population_Options(self, options):
		lastModified = self.get_current_time()
		self.dbController.update_Population_Options(self.population.get_PopulationID(), options, lastModified)
		self.population.set_Options(options, lastModified)

	# Inputs a StudentID and deletes the appropriate instance and records from the database
	def delete_Student(self, studentID):
		self.dbController.delete_SubjectStudent_for_StudentID(studentID)
		self.dbController.delete_Student(studentID)
		self.dbController.update_Population_Name(self.population.get_PopulationID(), self.population.get_Population_Name(), self.get_current_time())
		self.get_Population_from_db(self.population.get_PopulationID())

	# Inputs a StudentID and deletes the appropriate instance and records from the datab
	def delete_Subject(self, subjectID):
		self.dbController.delete_Subject_Constraints(subjectID)
		self.dbController.delete_SubjectStudent_for_SubjectID(subjectID)
		self.dbController.delete_Subject(subjectID)
		self.get_Population_from_db(self.population.get_PopulationID())

	# Returns all of the Students and the subjects they chose in the format {Student1Name:[Student1ID, Subjects], Student2Name:[Student2ID, Subjects], ...}
	def get_all_Student_Choices(self):
		data = {}
		
		# Gets all of the Students in the Population
		students = self.population.get_Students()

		# Loops through all the students
		for student in students:

			# Gets the name and ID of the student, and creates the dictionary reference
			studentName = " ".join([student.get_Student_Firstname(), student.get_Student_Surname()])
			studentID = student.get_StudentID()
			data[studentName] = [studentID]
			
			# Loops through the Student's Subjects and adds them to the dictionary
			for subject in student.get_Student_Subjects():
				data[studentName].append(subject.get_Subject_Name())
		
		# Returns the dictionary
		return data

	# Returns all of the Constraints of every Subject in the format {Subject1Name:{ID:Subject1ID, Constraints}, ...}
	def get_all_SubjectConstraints(self):
		data = {}

		# Gets all of the Subjects in the database
		subjects = self.dbController.get_all_Subjects()
		constraintTypes = self.dbController.get_Constraint_Types()

		# Loops through every Subject
		for subject in subjects:
			
			# Sets the initial "ID" key in the Subject's dictionary
			subjectID = subject[0]
			subjectName = subject[1]
			data[subjectName] = {"ID":subjectID}

			# Loops through each constraint and add it to the dictionary
			subjectConstraints = self.dbController.get_Subject_Constraints(subjectID)
			for constraint in subjectConstraints:
				for constraintType in constraintTypes:
					if constraintType[0] == constraint[1]:
						data[subjectName][constraintType[1]] = constraint[0]
						break
		
		# Returns the final dictionary
		return data

	# Function to pad a short string (s) with a specified character (pad) to get it to a desired length.
	def pad_string(self, s, desired_length, pad, front=True):

		# Converts input into a string if it is not already a string
		s = str(s)

		# Stores the current length of the string
		current = len(s)

		# Checks if the string is less than the desired length
		while current < desired_length:
			if front:
				# If the front of the string needs to be padded, then the character is prepended to the string
				s = pad + s
			else:
				# Otherwise, the character is appended to the string
				s += pad
			# Either way, the length of the string has increased by 1, so current needs to be incremented
			current += 1
		
		# Returns the padded string
		return s

	# Function to return the current time in the correct format
	def get_current_time(self):
		# Imports the time module and gets the current time
		import time
		timestamp = time.gmtime()

		# Returns the current time in the format "YYYY-MM-DD HH:MM" using the pad_string() function and string concatenation
		return f"{self.pad_string(timestamp.tm_year, 4, '0')}-{self.pad_string(timestamp.tm_mon, 2, '0')}-{self.pad_string(timestamp.tm_mday, 2, '0')} {self.pad_string(timestamp.tm_hour, 2, '0')}:{self.pad_string(timestamp.tm_min, 2, '0')}"

	# Inputs a dict of subjectName:subjectID and returns a dict of form SubjectName:SubjectInstance
	def create_Subjects(self, subjects:dict):
		subjectClasses = {}
		for subjectName in subjects.keys():
			# Get Constraint values for this Subject
			try:
				maxBlocks = self.dbController.get_Subject_Constraints(subjects[subjectName])[0][0]
			
			# Runs if there were no constraint values for the Subject
			except BaseException:
				maxBlocks = None

			# Creates the Subject instance and adds it to the dictionary
			subjectClasses[subjectName] = Subject(subjectName, subjects[subjectName], maxBlocks)
		
		# Returns the dictionary
		return subjectClasses

	# Function that returns the Clash Table for the current Population, replacing the SubjectID keys with the corresponding SubjectName
	def get_Clash_Table(self):

		clashTable = self.create_Clash_Table()
		newClashTable = {}

		# Loops through every key in the Clash Table, and get the correspinding SubjectName
		for subject1ID in clashTable.keys():
			subject1Name = self.dbController.get_Subject_Name_From_SubjectID(subject1ID)
			newClashTable[subject1Name] = {}
			for subject2ID in clashTable[subject1ID].keys():
				subject2Name = self.dbController.get_Subject_Name_From_SubjectID(subject2ID)
				
				# Creates the record in the new Clash Table
				newClashTable[subject1Name][subject2Name] = clashTable[subject1ID][subject2ID]
		
		# Returns the new Clash Table
		return newClashTable

	# Function that returns the Clash Table for the current Population
	def create_Clash_Table(self):
		# Gets a list of all the Subjects in the Population
		subjects = self.dbController.get_all_Subjects()

		# Creates an empty 2D dictionary to store the Clash Table
		clashTable = {}
		for subject1 in subjects:
			clashTable[subject1[0]] = {}
			for subject2 in subjects:
				clashTable[subject1[0]][subject2[0]] = 0
		
		# Gets a 2D array summarising all the relationships stored in the SubjectStudentLink database corresponding to the populationID
		subjectData = self.dbController.get_Subject_Student_data_from_Population(self.population.get_PopulationID())

		# Loops through every array of Subjects
		for studentSubjects in subjectData:
			for subject1 in range(1, len(studentSubjects)):
				clashTable[studentSubjects[subject1]][studentSubjects[subject1]] += 1
				for subject2 in range(subject1+1, len(studentSubjects)):
					clashTable[studentSubjects[subject1]][studentSubjects[subject2]] += 1
					clashTable[studentSubjects[subject2]][studentSubjects[subject1]] += 1
		
		return clashTable

	# Inputs the current Pattern, Clash Table and details about a state (the Block and the column that it would be added to) and returns the number of clashes placing it would cause
	def calculate_clashes(self, currentPattern, block, column, clashTable):
		column = currentPattern[column]
		clashes = 0

		# Loops through each Block already in the column, adding the number of Students who would study for this Block and the Block being added
		for existingBlock in column:
			clashes += clashTable[existingBlock.get_SubjectID()][block.get_SubjectID()]
		
		# Returns the total number of clashes
		return clashes

	# Inputs a Pattern and a list of Blocks, then returns a list of all of the posssible states
	def generate_states(self, currentPattern, blocks, clashTable):
		states = []

		# Loops through each Block and attempts to place that Block in each column of the Pattern
		for block in blocks:
			for column in range(0,len(currentPattern)):

				# Gets the clashes of this state, and appends the state to the list of states
				clashes = self.calculate_clashes(currentPattern, block, column, clashTable)

				# Each state is in the format [clashes, [length of the column the Block is being added to, [column, Block]]]
				states.append([clashes, [len(currentPattern[column]),[column, block]]])

		# Returns the list of states
		return states

	# Function to return the best Block Pattern with the current Clash Table and Blocks
	def generate_best_Block_Pattern(self, clashTable, blocks, currentPattern=[[],[],[]]):

		# Gets a list of the all the possible states, and puts them in a Priority Queue so that the states with the least clashes are retrieved first
		currentStates = PriorityQueue(queue=self.generate_states(currentPattern, blocks, clashTable))

		# Finds the number of clashes of the state at the front of the queue
		fewestClashes = currentStates.peek()[0]

		# This is a Priority Queue storing all of the states that have the same amount of clashes as the first state. This will order the items in the opposite order (i.e. descending number)
		favourableStates = PriorityQueue(queue=[],asc=False)

		# Adds each state with the fewest clashes to the favourableStates Priority Queue, which will now order the states by decreasing column length. This is to favour states that will add Blocks to columns with more Blocks already in them.
		while not(currentStates.is_empty()) and currentStates.peek()[0] == fewestClashes:
			favourableStates.enqueue(currentStates.dequeue()[1])

		# If the fewest number of clashes is zero, then it doesn't matter which state is chosen, so only the first state is kept
		if fewestClashes == 0:
			favourableStates = PriorityQueue(queue=[favourableStates.dequeue()])

		# A Priority Queue that stores all of the Patterns found in the loop below
		bestSubPatterns = PriorityQueue(queue=[])

		# Loops through each state, and tries adding it to the pattern
		while not(favourableStates.is_empty()):
			currentState = favourableStates.dequeue()
			column = currentState[1][0]
			block = currentState[1][1]

			subPattern = deepcopy(currentPattern)
			subPattern[column].append(block)

			# Creates the new Block list
			newBlocks = deepcopy(blocks)
			for index in range(len(newBlocks)):
				if block.get_BlockID() == newBlocks[index].get_BlockID():
					newBlocks.remove(newBlocks[index])
					break

			# If there are no more Blocks to be added, then the best Pattern for this state is the current pattern
			if len(newBlocks) == 0:
				bestSubPattern = deepcopy(subPattern)
				totalClashes = fewestClashes
			
			# Otherwise, the function calls itself to see what the best Pattern is for the current state, gets the number of clashes in that Pattern
			else:
				previousBest = self.generate_best_Block_Pattern(clashTable, newBlocks, subPattern)
				totalClashes = previousBest[0]
				bestSubPattern = previousBest[1]
				totalClashes += fewestClashes

			# Adds the Pattern and the Clashes to the Priority Queue
			bestSubPatterns.enqueue([totalClashes, deepcopy(bestSubPattern)])
		
		# Returns the Pattern with the fewest number of clashes, along with that Pattern's clashes
		return bestSubPatterns.dequeue()

	# Subroutine to create a new Population in the database from a file given by the user
	def setup_new_Population_from_file(self, filePath, populationName, options):
		# List to store any new Subjects that have been created - this will be used to ask the user to input new SubjectConstraints
		subjectsAdded = []

		# Create Population
		lastModified = self.get_current_time()
		populationID = self.dbController.add_new_Population(populationName, options, lastModified)

		# Import data
		inputHandler = FileInputHandler()
		subjects, newPopulation = inputHandler.import_new_Population(filePath)

		# Get names of Subjects already in database
		try:
			currentSubjects = [i[1] for i in self.dbController.get_all_Subjects()]
		except BaseException:
			currentSubjects = []
		
		# Creates a dictionary in the format {SubjectName:SubjectID, ...}
		subjectIDs = {}
		for subject in subjects:
			if subject in currentSubjects:
				subjectIDs[subject] = self.dbController.get_SubjectID(subject)
			else:
				subjectIDs[subject] = self.dbController.add_new_Subject(subject)
				subjectsAdded.append([subject, subjectIDs[subject]])

		# Creates the Subject instances for each Subject found
		subjectClasses = self.create_Subjects(subjectIDs)

		# Add Student data, add StudentSubjects data
		for studentDetails in newPopulation:
			studentFirstname, studentSurname = studentDetails.pop(0), studentDetails.pop(0)
			studentID = self.dbController.add_new_Student(Student(studentFirstname, studentSurname), populationID)
			studentSubjects = []
			for subject in studentDetails:
				if subject:
					studentSubjects.append(subjectClasses[subject])
					self.dbController.add_new_SubjectStudent(studentSubjects[-1].get_SubjectID(),studentID)

		# Return the list of Subjects that were added to the database
		return subjectsAdded

	# Subroutine to get Student, Subject, Block details from db, given a Population ID
	def get_Population_from_db(self, populationID):

		# Configure new Population class, store in self.population
		populationDetails = self.dbController.get_Population_details(populationID)
		populationLastModified = populationDetails[2]
		self.population = Population(populationDetails[0], populationDetails[1], populationLastModified)
		self.population.set_PopulationID(populationID)

		# Get all Subjects
		subjectLookup = {}
		subjects = self.dbController.get_all_Subjects()
		for index in range(len(subjects)):
			subjectID = subjects[index][0]
			subjectName = subjects[index][1]
			constraints = self.dbController.get_Subject_Constraints(subjectID)
			try:
				maxBlocks = constraints[0][0]
			except BaseException:
				maxBlocks = None
			subjectLookup[subjectID] = Subject(subjectName, subjectID, maxBlocks)

		# Get all Students in population
		students = self.dbController.get_Students_in_Population(self.population.get_PopulationID())
		studentLookup = {}
		for index in range(len(students)):
			studentDetails = students[index]
			student = Student(studentDetails[1], studentDetails[2])
			student.set_StudentID(studentDetails[0])
			studentLookup[studentDetails[0]] = student

		# Get all StudentSubjects data, store choices in every Student
		subjectChoices = self.dbController.get_Subject_Student_data_from_Population(self.population.get_PopulationID())
		for subjectChoice in subjectChoices:
			studentID = subjectChoice[0]
			for subjectID in subjectChoice[1:]:
				studentLookup[studentID].add_to_Student_Subjects(subjectLookup[subjectID])
		
		# Get all Blocks in population
		blocks = self.dbController.get_Blocks_in_Population(self.population.get_PopulationID())
		for index in range(len(blocks)):
			blockID = blocks[index]
			subjectID, patternID, blockNumber = self.dbController.get_Block_Details_from_BlockID(blockID)
			block = Block(subjectID, blockID, self.population.get_PopulationID())
			block.set_PatternID(patternID)
			block.set_Block_Number(blockNumber)
			blocks[index] = block

		# Get all Patterns in population
		patterns = []
		patternIDs = self.dbController.get_valid_Patterns_for_Population(self.population.get_PopulationID())
		for pattern in patternIDs:
			patternID = pattern[0]
			patternName = self.dbController.get_Pattern_Name_from_PatternID(patternID)
			lastModified = self.dbController.get_Last_Modified_from_PatternID(patternID)
			blocksInPattern = [block for block in blocks if block.get_PatternID() == patternID]
			blockPattern = [[] for i in range(self.population.get_Options())]
			for block in blocksInPattern:
				blockPattern[block.get_Block_Number()].append(block)
			patterns.append(Pattern(patternID, patternName, blocksInPattern, blockPattern, lastModified))
		
		# Stores Students, Subjects and Patterns into self.population
		self.population.set_Students(list(studentLookup.values()), populationLastModified)
		self.population.set_Subjects(list(subjectLookup.values()), populationLastModified)
		self.population.set_Patterns(patterns, populationLastModified)

	# Inputs a SubjectName, creates a new Block for that Subject and returns it
	def create_Block(self, subjectName:str):
		for subject in self.population.get_Subjects():
			if subject.get_Subject_Name() == subjectName:
				break
		populationID = self.population.get_PopulationID()

		blockID = self.dbController.add_new_Block(subject.get_SubjectID(), populationID)

		return Block(subject.get_SubjectID(), blockID, populationID)

	# Implementation of the algorithm that creates the Blocks from the Subject Constraints
	def create_Blocks_from_SubjectConstraints(self, clashTable):
		blocks = []
		subjects = self.population.get_Subjects()
		for index in range(len(subjects)):
			currentSubject = subjects[index]
			totalStudents = clashTable[currentSubject.get_SubjectID()][currentSubject.get_SubjectID()]
			if totalStudents == 0:
				continue
			elif currentSubject.get_max_Blocks() != 0:
				for i in range(currentSubject.get_max_Blocks()):
					blocks.append(self.create_Block(currentSubject.get_Subject_Name()))
			else:
				numberOfBlocks, remainder = divmod(totalStudents,currentSubject.get_max_Students())
				if remainder > 0:
					numberOfBlocks += 1
				
				for i in range(numberOfBlocks):
					blocks.append(self.create_Block(currentSubject.get_Subject_Name()))
		
		return blocks

	# Function that is used to automatically create a Pattern Name for an automatically-generated Pattern
	def create_Pattern_Name(self):
		lastName = self.dbController.get_last_created_Pattern_Name()
		try:
			lastName = lastName[0][0]
			number = "".join([letter for letter in lastName if letter.isdigit()])
			return f"GeneratedPattern{int(number)+1}"
		except BaseException:
			return "GeneratedPattern1"

	# Function that is used to generate the best Pattern for the current Population
	def generate_Patterns(self, blocks):

		# Creates the Clash Table and initialises the variables used to compare Patterns generated
		clashTable = self.create_Clash_Table()
		bestStudentsSatisfied = None
		bestSubjectsNotSatisfied = None
		bestPattern = None

		# Runs the generate_best_Block_Pattern function multiple times, but shuffling the order of the Block list each time. This is because different Patterns can be generated based on the ordering of the list, so shuffling and running the algorithm again increases the likelihood of the best Pattern being generated
		for i in range(BackEnd.GENERATOR_LOOPS):
			clashes, blockPattern = self.generate_best_Block_Pattern(clashTable, BackEnd.shuffle(blocks), [[] for i in range(self.population.get_Options())])

			# Creates a version of the generated Pattern that can be used to check 
			blockPatternToTest = []
			for column in range(len(blockPattern)):
				blockPatternToTest.append([])
				for block in blockPattern[column]:
					blockPatternToTest[-1].append(block.get_SubjectID())
		
			# Tests the generated Pattern and gets the results of the test
			results = self.test_Pattern(blockPatternToTest)
			studentsSatisfied = results[0]
			subjectsNotSatisfied = len(results[2])

			# If this is the first Pattern generated, then this must be the best Pattern found so far
			if bestStudentsSatisfied == None:
				bestStudentsSatisfied = studentsSatisfied
				bestSubjectsNotSatisfied = subjectsNotSatisfied
				bestPattern = deepcopy(blockPattern)
			
			# Otherwise, check first if the number of Students satisfied has improved. If this has stayed constant, then the algorithm will prefer the Pattern that satisfies more Subject Choices.
			elif bestStudentsSatisfied < studentsSatisfied or (bestStudentsSatisfied == studentsSatisfied and bestSubjectsNotSatisfied > subjectsNotSatisfied):
				bestStudentsSatisfied = studentsSatisfied
				bestSubjectsNotSatisfied = subjectsNotSatisfied
				bestPattern = deepcopy(blockPattern)
		
		# Formats the best Pattern found in a format that can be used by the GUI screens
		pattern = []
		for column in bestPattern:
			pattern.append([])
			for block in column:
				pattern[-1].append(block.get_SubjectID())

		# Returns the formatted Pattern
		return pattern

