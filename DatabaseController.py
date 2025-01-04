import sqlite3
from Student import Student
from Subject import Subject
from os.path import exists

class DatabaseController():

	# Creates a connection to the database
	def __init__(self, db_path:str):
		# Checks if the database file already exists
		if exists(db_path):
			self.conn = sqlite3.connect(db_path)
		else:
			# If the database file does not exist, then it also initialises the database
			self.conn = sqlite3.connect(db_path)
			self.create_db()
			
	# Inputs a 2D list of type [[integer, value1, ...], [integer, value2, ...], ...], then returns the list ordered by the integer values 
	def merge_sort(arr:list, asc=True):
		# If the length of the list is less than or equal to 1, then the list is already sorted and can be returned immediately
		if len(arr) <= 1:
			return arr
		
		# Finds the midpoint index of the list and splits the main list into two sublists, which are then sorted separately
		midpoint = len(arr)//2
		left = DatabaseController.merge_sort(arr[:midpoint], asc)
		right = DatabaseController.merge_sort(arr[midpoint:], asc)

		# Creates a new empty list
		new_arr = []

		# Runs the while loop while both lists contain at least 1 item
		while len(left) > 0 and len(right) > 0:

			# Finds whether the value in the left list is greater than the value in the right list
			if left[0][0] > right[0][0]:

				# If this value is greater, then checks if the algorithm needs to sort the list in ascending order
				if asc:
					# If it does, then the lower value is appended to the list, and removed from the list it was originally from
					new_arr.append(right.pop(0))
				else:
					# Otherwise, the greater value is appended to the list, and removed from the list it was originally from
					new_arr.append(left.pop(0))
			
			# Otherwise, if the value in the right list is greater than the value in the left list
			elif right[0][0] > left[0][0]:

				# Checks again if the algorithm needs to sort the list in ascending order
				if asc:
					# If it does, then the lower value is appended to the list, and removed from the list it was originally from
					new_arr.append(left.pop(0))
				else:
					# Otherwise, the greater value is appended to the list, and removed from the list it was originally from
					new_arr.append(right.pop(0))

			# Finally, if the two values are equal, then it does not matter which list the next value is taken from. Hence, the algorithm just takes the value from the right list
			else:
				new_arr.append(right.pop(0))

		# If there are still values left in the left list, then these values are appended sequentially to the list
		if len(left) > 0:
			new_arr += left
		
		# Otherwise, if there are still values left in the right list, then these values are appended sequentially to the list
		else:
			new_arr += right
		
		# Finally, returns the sorted list
		return new_arr
	
	# Inputs a query and returns the output in a utilisable format
	def execute(self, query:str):
		return [row for row in self.conn.execute(query)]
	
	# Inputs a StudentID and deletes the appropriate record in the Student table
	def delete_Student(self, studentID):
		query = f"DELETE FROM Student WHERE StudentID={studentID};"
		self.execute(query)
		self.commit()

	# Inputs a StudentID and deletes all of the appropriate records in the SubjectStudentLink table
	def delete_SubjectStudent_for_StudentID(self, studentID):
		query = f"DELETE FROM SubjectStudentLink WHERE StudentID={studentID};"
		self.execute(query)
		self.commit()

	# Inputs a SubjectID and deletes the appropriate record in the Subject table
	def delete_Subject(self, subjectID):
		query = f"DELETE FROM Subject WHERE SubjectID={subjectID};"
		self.execute(query)
		self.commit()

	# Inputs a SubjectID and deletes all of the appropriate records in the SubjectStudentLink table
	def delete_SubjectStudent_for_SubjectID(self, subjectID):
		query = f"DELETE FROM SubjectStudentLink WHERE SubjectID={subjectID};"
		self.execute(query)
		self.commit()

	# Inputs a SubjectID and deletes the all of the appropriate records in the Constraints table
	def delete_Subject_Constraints(self, subjectID):
		query = f"DELETE FROM Constraints WHERE SubjectID={subjectID};"
		self.execute(query)
		self.commit()

	# Resets all of the Constraints for a specific Subject, and replaces these with the new values inputted
	def reset_Subject_Constraints(self, newConstraints: dict, subjectID):
		self.delete_Subject_Constraints(subjectID)
		for constraintTypeID in newConstraints.keys():
			query = f"INSERT INTO Constraints(ConstraintTypeID, ConstraintDetail, SubjectID) VALUES({constraintTypeID}, {newConstraints[constraintTypeID]}, {subjectID});"
			self.execute(query)
			self.commit()
	
	# Inputs a Population name, PopulationID and a timestamp, and updates the appropriate record in the Population table
	def update_Population_Name(self, populationID, populationName, lastModified):
		query = f"UPDATE Population SET PopulationName=\"{populationName}\", LastModified=\"{lastModified}\"  WHERE PopulationID={populationID};"
		self.execute(query)
		self.commit()
	
	# Inputs the Population options, PopulationID and a timestamp, and updates the appropriate record in the Population table
	def update_Population_Options(self, populationID, options, lastModified):
		query = f"UPDATE Population SET Options=\"{options}\", LastModified=\"{lastModified}\"  WHERE PopulationID={populationID};"
		self.execute(query)
		self.commit()

	# Inputs Population details, creates a new Population record and returns the PopulationID of that record
	def add_new_Population(self, populationName, options, LastModified):
		query = f"""INSERT INTO Population(PopulationName, Options, LastModified)
		VALUES(\"{populationName}\", {options}, \"{LastModified}\");"""
		self.execute(query)
		self.commit()

		query = f"""SELECT PopulationID FROM Population
		WHERE PopulationName=\"{populationName}\";"""
		data = self.execute(query)
		return data[0][0]
	
	# Inputs a PopulationID and returns the details of the Population in the format [PopulationName, Options, LastModified]
	def get_Population_details(self, populationID):
		query = f"SELECT PopulationName, Options, LastModified FROM Population WHERE PopulationID={populationID};"
		return self.execute(query)[0]

	# Returns details of all the Populations stored in the database, sorted by their ID, in the format [PopulationID, Name]
	def get_all_Populations(self):
		query = "SELECT PopulationID, PopulationName FROM Population;"
		return DatabaseController.merge_sort(self.execute(query))

	# Inputs a Subject name, creates a new Subject and returns the SubjectID
	def add_new_Subject(self, subjectName):
		query = f"""INSERT INTO Subject(SubjectName)
		VALUES(\"{subjectName}\");"""
		self.execute(query)
		self.commit()

		query = f"""SELECT SubjectID FROM Subject
		WHERE SubjectName=\"{subjectName}\";"""
		data = self.execute(query)
		return data[0][0]
	
	# Inputs a SubjectID and a StudentID, and creates the corresponding record in the SubjectStudentLink table
	def add_new_SubjectStudent(self, subjectID, studentID):
		query = f"""INSERT INTO SubjectStudentLink
		VALUES({subjectID},{studentID});"""
		self.execute(query)
		self.commit()
	
	# Inputs a Student class, creates a new Student record and returns the StudentID of that record
	def add_new_Student(self, student:Student, populationID):
		query = f"""INSERT INTO Student(StudentFirstName, StudentSurname, PopulationID)
		VALUES(\"{student.get_Student_Firstname()}\",\"{student.get_Student_Surname()}\",{populationID});"""
		self.execute(query)
		self.commit()

		query = f"""SELECT StudentID FROM Student
		WHERE StudentFirstName=\"{student.get_Student_Firstname()}\"
		AND StudentSurname=\"{student.get_Student_Surname()}\"
		AND PopulationID={populationID};"""
		data = self.execute(query)
		return data[0][0]
	
	# Inputs a SubjectName and returns its SubjectID
	def get_SubjectID(self, subjectName:str):
		query = f"""
		SELECT SubjectID FROM Subject
		WHERE SubjectName = \"{subjectName}\";"""
		data = self.execute(query)
		return int(data[0][0])
	
	# Inputs a SubjectID and PopulationID, creates a new Block record and returns the BlockID of that record
	def add_new_Block(self, subjectID, populationID):
		query = f"INSERT INTO Block(SubjectID, PopulationID, PatternID, BlockNumber)\nVALUES({subjectID}, {populationID}, 0, -1);"
		self.execute(query)
		self.commit()
		
		query = f"SELECT BlockID FROM Block\nWHERE SubjectID={subjectID} AND PopulationID={populationID}\nORDER BY BlockID DESC\nLIMIT 1;"
		return self.execute(query)[0][0]

	# Inputs Student details and returns the StudentID of the corresponding record
	def get_StudentID(self, firstName, surname, populationID):
		query = f"""
		SELECT StudentID FROM Student
		WHERE StudentFirstName = \"{firstName}\"
		AND StudentSurname = \"{surname}\"
		AND PopulationID = {populationID};"""
		data = self.execute(query)
		return int(data[0][0])

	# Inputs a SubjectID and returns the constraints for that Subject in the format [value, id]
	def get_Subject_Constraints(self, subjectID):
		query = f"SELECT ConstraintDetail, ConstraintTypeID FROM Constraints\nWHERE SubjectID = {subjectID}\nORDER BY ConstraintTypeID ASC;"
		return  self.execute(query)

	# Inputs a SubjectID and returns the Subject name of that record
	def get_Subject_Name_From_SubjectID(self, subjectID):
		query = f"SELECT SubjectName FROM Subject WHERE SubjectID={subjectID};"
		return self.execute(query)[0][0]

	# Returns a list of [SubjectID, SubjectName] from database, sorted by the SubjectID
	def get_all_Subjects(self):
		query = "SELECT SubjectID, SubjectName FROM Subject WHERE SubjectID != 0;"
		return DatabaseController.merge_sort(self.execute(query))
	
	# Inputs a Subject class, and updates the corresponding records in the Subject and Constraints tables
	def update_Subject(self, subject:Subject):
		# Updates the Subject Name
		query = f"""
		UPDATE Subject
		SET SubjectName=\"{subject.get_Subject_Name()}\"
		WHERE SubjectID={subject.get_SubjectID()};"""
		self.execute(query)
		self.commit()

		# Deletes old constraint and adds new constraint
		query = f"DELETE FROM Constraints WHERE SubjectID={subject.get_SubjectID()};"
		self.execute(query)
		self.commit()

		query = f"INSERT INTO Constraints(ConstraintTypeID, ConstraintDetail, SubjectID) VALUES(1, {subject.get_max_Blocks()}, {subject.get_SubjectID()});"
		self.execute(query)
		self.commit()

	# Inputs a Student class, and updates the corresponding records in the Student and SubjectStudentLink tables
	def update_Student(self, student:Student):
		# Gets the Student's personal details from class and updates the values stored in the Student table
		query = f"""
		UPDATE Student
		SET StudentFirstName=\"{student.get_Student_Firstname()}\", StudentSurname=\"{student.get_Student_Surname()}\"
		WHERE Student.StudentID={student.get_StudentID()};"""
		self.execute(query)
		self.commit()

		# Deletes all records in the SubjectStudentLink table that correspond to this Student
		query = f"DELETE FROM SubjectStudentLink WHERE StudentID={student.get_StudentID()};"
		self.execute(query)
		self.commit()

		# Loops through all of the Subjects that the Student studies
		for subject in student.get_Student_Subjects():
			# Gets the SubjectID and StudentID, and adds this as a record to the SubjectStudentLink table
			query = f"""
			INSERT INTO SubjectStudentLink (SubjectID, StudentID)
			VALUES ({subject.get_SubjectID()}, {student.get_StudentID()});"""
			self.execute(query)
			self.commit()
	
	# Gets all of the types of Constraints and returns them in the format [ID, type]
	def get_Constraint_Types(self):
		query = "SELECT ConstraintTypeID, ConstraintType FROM ConstraintType;"
		return self.execute(query)

	# Gets all of the Students belonging to a Population and returns them in the format [ID, FirstName, Surname], sorted by the StudentID
	def get_Students_in_Population(self, populationID):
		query = f"SELECT StudentID, StudentFirstName, StudentSurname FROM Student WHERE PopulationID={populationID};"
		data = DatabaseController.merge_sort(self.execute(query))
		return data

	# Inputs a PopulationID and gets all of the unique Subjects that are being studied by Student in that Population, returning them in the format [ID, Name], sorted by the SubjectID
	def get_Subjects_in_Population(self, populationID):
		query = f"""
		SELECT DISTINCT Subject.SubjectID, Subject.SubjectName FROM Student
		INNER JOIN SubjectStudentLink ON SubjectStudentLink.StudentID=Student.StudentID
		INNER JOIN Subject ON SubjectStudentLink.SubjectID=Subject.SubjectID
		WHERE Student.PopulationID={populationID};"""
		data = self.execute(query)
		return DatabaseController.merge_sort(data)
	
	# Inputs a PopulationID and gets all of the data stored in the SubjectStudentLink table corresponding to Students in that Population. Data is returned in the format [StudentID, Subject1_ID, Subject2_ID, ...]
	def get_Subject_Student_data_from_Population(self, populationID):
		# Query that gets all of the records in the SubjectStudentLink table corresponding to Students in the population, returning the StudentID and the SubjectID
		query = f"""
		SELECT Student.StudentID, Subject.SubjectID FROM Student
		INNER JOIN SubjectStudentLink ON SubjectStudentLink.StudentID=Student.StudentID
		INNER JOIN Subject ON SubjectStudentLink.SubjectID=Subject.SubjectID
		WHERE Student.PopulationID={populationID};"""

		# Orders the data from the previous query by StudentID, so that records corresponding to the same Student are contiguous in the list
		data = DatabaseController.merge_sort(self.execute(query))

		# Stores all of the SubjectStudent data in the form of a 2D list
		subjectStudentData = []

		# Stores the StudentID of the previous record
		currentStudentID = -1

		# Loops through every record fetched from the database
		while data:
			record = data.pop(0)
			# Checks if the StudentID of the current record is the same as the StudentID of the previous record
			if record[0] == currentStudentID:
				# If it is, then the SubjectID of the record can be appended to the last list in the 2D list
				subjectStudentData[-1].append(record[1])

			else:
				# Otherwise, a new list is appended to the 2D list, containing the StudentID and the SubjectID
				subjectStudentData.append([record[0], record[1]])

				# The currentStudent variable is set to the new StudentID
				currentStudentID = record[0]
		
		# Returns the 2D list
		return subjectStudentData
	
	# Inputs Pattern details, creates a new Pattern record and returns the PatternID of that record
	def add_new_Pattern(self, patternName, lastModified, populationID):
		query = f"INSERT INTO Pattern(PatternName, LastModified, PopulationID) VALUES (\"{patternName}\", \"{lastModified}\", {populationID});"
		self.execute(query)
		self.commit()

		query = f"SELECT PatternID FROM Pattern WHERE PatternName = \"{patternName}\" and LastModified = \"{lastModified}\" AND PopulationID = {populationID} LIMIT 1;"
		return self.execute(query)[0][0]

	# Inputs a PopulationID, and gets all the records from the Pattern table which were modified after the Population was last modified. Returns a list of all of the PatternIDs for these records
	def get_valid_Patterns_for_Population(self, populationID):
		query = f"""
		SELECT Pattern.PatternID FROM Pattern
		INNER JOIN Population ON Population.PopulationID=Pattern.PopulationID
		WHERE Pattern.PopulationID={populationID}
			AND Population.LastModified <= Pattern.LastModified
		ORDER BY Pattern.PatternName ASC;"""
		return self.execute(query)
	
	# Inputs a PatternID and returns the PatternName of the corresponding record from the Pattern table
	def get_Pattern_Name_from_PatternID(self, patternID):
		query = f"SELECT PatternName FROM Pattern WHERE PatternID={patternID};"
		return self.execute(query)[0][0]

	# Inputs a PatternID and returns the timestamp that the corresponding record from the Pattern table was last modified
	def get_Last_Modified_from_PatternID(self, patternID):
		query = f"SELECT LastModified FROM Pattern WHERE PatternID={patternID};"
		return self.execute(query)[0][0]

	# Inputs a PatternID and a timestamp, and updates the corresponding record from the Pattern table
	def set_Last_Modified_from_PatternID(self, patternID, lastModified):
		query = f"UPDATE Pattern SET LastModified=\"{lastModified}\" WHERE PatternID={patternID};"
		self.execute(query)
		self.commit()

	# Inputs a PatternID and deletes the corresponding record in the Pattern table
	def delete_Pattern(self, patternID):
		query = f"DELETE FROM Pattern WHERE PatternID={patternID};"
		self.execute(query)
		self.commit()

	# Inputs a PatternID and deletes all the corresponding records in the Block table
	def delete_Blocks_in_Pattern(self, patternID):
		query = f"DELETE FROM Block WHERE PatternID={patternID};"
		self.execute(query)
		self.commit()
	
	# Inputs a BlockID and deletes the corresponding record in the Block table
	def delete_Block(self, blockID):
		query = f"DELETE FROM Block WHERE BlockID={blockID};"
		self.execute(query)
		self.commit()

	# Inputs a BlockID and returns the SubjectID of the corresponding record
	def get_Block_Details_from_BlockID(self, blockID):
		query = f"SELECT SubjectID, PatternID, BlockNumber FROM Block WHERE BlockID={blockID};"
		return self.execute(query)[0]

	# Inputs a PopulationID and gets all the corresponding records in the Block table. Returns the BlockID of each record.
	def get_Blocks_in_Population(self, populationID):
		query = f"SELECT BlockID FROM Block WHERE PopulationID={populationID};"
		return [row[0] for row in DatabaseController.merge_sort(self.execute(query))]

	# Inputs a BlockID and SubjectID, and updates the SubjectID of the corresponding record in the Block table
	def update_SubjectID_for_Block(self, blockID, subjectID):
		query = f"UPDATE Block SET SubjectID = {subjectID} WHERE BlockID = {blockID};"
		self.execute(query)
		self.commit()

	# Inputs a BlockID and BlockNumbers, and updates the BlockNumber of the corresponding record in the Block table
	def update_Block_Number_for_Block(self, blockID, blockNumber):
		query = f"UPDATE Block SET BlockNumber={blockNumber} WHERE BlockID={blockID};"
		self.execute(query)
		self.commit()
	
	# Inputs a BlockID and PatternID, and updates the PatternID of the corresponding record in the Block table
	def update_PatternID_for_Block(self, blockID, patternID):
		query = f"UPDATE Block SET PatternID={patternID} WHERE BlockID={blockID};"
		self.execute(query)
		self.commit()

	# Gets the name of the Pattern that was automatically created by the blocking algorithm most recently
	def get_last_created_Pattern_Name(self):
		query = "SELECT PatternName FROM Pattern WHERE PatternName LIKE \"GeneratedPattern[1-9]%\" ORDER BY PatternName DESC LIMIT 1;"
		return self.execute(query)

	# Commits all changes made to the database in the previous query
	def commit(self):
		self.conn.commit()
	
	# Stores and runs all of the queries required to initialise the database
	def create_db(self):
		# Queries that create the tables in the database
		CREATE_QUERIES=[
		"""CREATE TABLE "Population"(
			"PopulationID" INTEGER NOT NULL,
			"PopulationName" TEXT NOT NULL,
			"LastModified" TEXT NOT NULL,
			"Options" INTEGER NOT NULL,
			PRIMARY KEY ("PopulationID" AUTOINCREMENT)
		);""","""
		CREATE TABLE "Student"(
			"StudentID" INTEGER NOT NULL,
			"StudentFirstName" TEXT NOT NULL,
			"StudentSurname" TEXT NOT NULL,
			"PopulationID" INTEGER NOT NULL,
			PRIMARY KEY ("StudentID" AUTOINCREMENT),
			FOREIGN KEY ("PopulationID") REFERENCES "Population"("PopulationID")
		);""","""
		CREATE TABLE "Subject"(
			"SubjectID" INTEGER NOT NULL,
			"SubjectName" TEXT NOT NULL,
			PRIMARY KEY ("SubjectID" AUTOINCREMENT)
		);""","""
		CREATE TABLE "SubjectStudentLink"(
			"SubjectID" INTEGER NOT NULL,
			"StudentID" INTEGER NOT NULL,
			PRIMARY KEY ("SubjectID", "StudentID"),
			FOREIGN KEY ("SubjectID") REFERENCES "Subject"("SubjectID"),
			FOREIGN KEY ("StudentID") REFERENCES "Student"("StudentID")
		);""","""
		CREATE TABLE "ConstraintType"(
			"ConstraintTypeID" INTEGER NOT NULL,
			"ConstraintType" TEXT NOT NULL,
			PRIMARY KEY ("ConstraintTypeID" AUTOINCREMENT)
		);""","""
		CREATE TABLE "Constraints"(
			"ConstraintID" INTEGER NOT NULL,
			"ConstraintTypeID" INTEGER NOT NULL,
			"ConstraintDetail" INTEGER NOT NULL,
			"SubjectID" INTEGER NOT NULL,
			PRIMARY KEY ("ConstraintID" AUTOINCREMENT),
			FOREIGN KEY ("ConstraintTypeID") REFERENCES "ConstraintType"("ConstraintTypeID"),
			FOREIGN KEY ("SubjectID") REFERENCES "Subject"("SubjectID")
		);""","""
		CREATE TABLE "Block"(
			"BlockID" INTEGER NOT NULL,
			"SubjectID" INTEGER NOT NULL,
			"PopulationID" INTEGER NOT NULL,
			"PatternID" INTEGER NOT NULL,
			"BlockNumber" INTEGER NOT NULL,
			PRIMARY KEY ("BlockID" AUTOINCREMENT),
			FOREIGN KEY ("SubjectID") REFERENCES "Subject"("SubjectID"),
			FOREIGN KEY ("PopulationID") REFERENCES "Population"("PopulationID"),
			FOREIGN KEY ("PatternID") REFERENCES "Pattern"("PatternID")
		);""","""
		CREATE TABLE "Pattern"(
			"PatternID" INTEGER NOT NULL,
			"PatternName" TEXT NOT NULL,
			"PopulationID" INTEGER NOT NULL,
			"LastModified" TEXT NOT NULL,
			PRIMARY KEY ("PatternID" AUTOINCREMENT),
			FOREIGN KEY ("PopulationID") REFERENCES "Population"("PopulationID")
		);"""]
		for query in CREATE_QUERIES:
			self.execute(query)
			self.commit()
		
		# Queries that add null/dummy data to the database
		ADD_DATA_QUERIES = [
			"INSERT INTO ConstraintType(ConstraintType) VALUES(\"Number of Blocks\");",
			"INSERT INTO Population VALUES (0, \"UNASSIGNED\", \"UNASSIGNED\", 0);",
			"INSERT INTO Pattern VALUES (0, \"UNASSIGNED\", 0, \"UNASSIGNED\");",
			"INSERT INTO Subject VALUES (0, \"UNASSIGNED\");"]
		for query in ADD_DATA_QUERIES:
			self.execute(query)
			self.commit()

