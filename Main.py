from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from BackEnd import BackEnd
from functools import partial

import kivy

# Requires the kivy module that is running the GUI to be version 2.2.1 or more
kivy.require('2.2.1')

class MainMenu(Screen):
	# Class that creates the Main Menu screen
	
	# Function that switches the current screen to the Subject Data screen
	def subject_Button(self, instance):
		app.windowManager.current = "SubjectData"
		app.windowManager.transition.direction = "left"

	# Function that switches the current screen to the Populations screen
	def population_Button(self, instance):
		app.windowManager.current = "StudentPopulations"
		app.windowManager.transition.direction = "left"

	# Creates the layout of the Main Menu screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates a widget that can display other widgets in the form of a grid
		mainLayout = GridLayout(cols=1, spacing="36dp", padding="36dp")
		mainLayout.add_widget(Label(text="Main Menu"))

		# Creates widgets to store the buttons (so that the buttons are centred)
		subjectButtonLayout = GridLayout(cols=3)
		subjectButtonLayout.add_widget(Label())
		subjectButton = Button(text="Subject Data")
		subjectButton.bind(on_release=self.subject_Button)
		subjectButtonLayout.add_widget(subjectButton)
		subjectButtonLayout.add_widget(Label())

		populationButtonLayout = GridLayout(cols=3)
		populationButtonLayout.add_widget(Label())
		populationButton = Button(text="Student Populations")
		populationButton.bind(on_release=self.population_Button)
		populationButtonLayout.add_widget(populationButton)
		populationButtonLayout.add_widget(Label())

		# Adds the buttons to the main grid widget
		mainLayout.add_widget(subjectButtonLayout)
		mainLayout.add_widget(populationButtonLayout)

		# Adds the grid widget to the screen
		self.add_widget(mainLayout)

class ErrorInUserValues(GridLayout):
	# Generic class that is used to create an error message popup.

	# Closes the popup
	def close(self, instance):
		self.parent.parent.parent.dismiss()

	# Takes in an error message, and displays it in a grid widget along with a button to close the popup
	def __init__(self, errorMsg, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.add_widget(Label(text="WARNING", font_size="75dp"))
		self.add_widget(Label(text=errorMsg))
		closeButton = Button(text="Close")
		closeButton.bind(on_release=self.close)
		self.add_widget(closeButton)

class EditSubject(GridLayout):
	# Class that is used to create the popup to edit the details of a Subject

	# Called when the user wants to save the changes they've made
	def save_Changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the SubjectName field
		if self.newSubjectName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Subject name needs to be in the correct format. Currently, this field is empty."])
		if self.newSubjectName.text in [i[1] for i in backEnd.dbController.get_all_Subjects() if i[1] != self.subjectName]:
			validText = False
			errorMsg = "\n".join([errorMsg, "A Subject with that name already exists in the database."])
		if len(self.newSubjectName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "Subject names should have length less than or equal to 30 characters."])
		
		# Validates the maxBlocks field
		try:
			maxBlocks = int(self.newMaxBlocks.text)
			if maxBlocks <= 0:
				validText = False
				errorMsg = "\n".join([errorMsg, f"{self.constraints[1]} must be a positive integer."])
		except BaseException:
			validText = False
			errorMsg = "\n".join([errorMsg, f"{self.constraints[1]} must be an integer."])
		
		# If all the data is valid, then the new data is sent to backend and the current screen is updated
		if validText:
			backEnd.edit_Subject_details(self.subjectID, self.newSubjectName.text, maxBlocks)
			self.subjectScreen.on_enter()
			self.parent.parent.parent.dismiss()

		# Otherwise, shows new popup, telling user every error in their inputs 
		else:
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()


	# Takes in the SubjectID and the screen showing the Subjects
	def __init__(self, subjectID, subjectScreen, **kwargs):
		super().__init__(**kwargs)

		# Initialises variables used when data is submitted
		self.cols = 1

		self.subjectID = subjectID
		self.subjectScreen = subjectScreen
		self.subjectName = backEnd.dbController.get_Subject_Name_From_SubjectID(self.subjectID)

		# Creates the GUI screen, adding all of the widgets to the parent grid layout
		self.add_widget(Label(text=f"Editing Subject: {self.subjectName}"))

		mainLayout = GridLayout(cols=2)
		mainLayout.add_widget(Label(text="Name:"))

		# Creates layout responsible for showing the old SubjectName and getting the new SubjectName
		nameLayout = GridLayout(rows=2)
		nameLayout.add_widget(Label(text=self.subjectName))
		self.newSubjectName = TextInput(text=self.subjectName)
		nameLayout.add_widget(self.newSubjectName)

		mainLayout.add_widget(nameLayout)

		# Gets the constraints of the Subject and creates layout responsible for showing the old constraints and getting the new constraints
		self.constraints = backEnd.dbController.get_Constraint_Types()[0]

		try:
			maxBlocks = str(backEnd.dbController.get_Subject_Constraints(self.subjectID)[0][0])
		except BaseException:
			maxBlocks = ""

		mainLayout.add_widget(Label(text=self.constraints[1]))
		constraintLayout = GridLayout(rows=2)
		constraintLayout.add_widget(Label(text=maxBlocks))
		self.newMaxBlocks = TextInput(text=maxBlocks)
		constraintLayout.add_widget(self.newMaxBlocks)
		mainLayout.add_widget(constraintLayout)

		# Creates the button to save the changes made by the user
		saveChangesButton = Button(text="Save Changes")
		saveChangesButton.bind(on_release=self.save_Changes_Button)

		# Adds all of the widgets to the screen
		self.add_widget(mainLayout)
		self.add_widget(saveChangesButton)

class AddSubject(GridLayout):
	# Class that is used to create the popup to get the details of a new Subject

	# Called when the user wants to submit the new details for the new Subject
	def submit_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the SubjectName field
		if self.subjectName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Subject name needs to be in the correct format. Currently, this field is empty."])
		if self.subjectName.text in [i[1] for i in backEnd.dbController.get_all_Subjects()]:
			validText = False
			errorMsg = "\n".join([errorMsg, "A Subject with that name already exists in the database."])
		if len(self.subjectName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "Subject names should have length less than or equal to 30 characters."])
		
		# Validates the maxBlocks field
		try:
			maxBlocks = int(self.maxBlocks.text)
			if maxBlocks <= 0:
				validText = False
				errorMsg = "\n".join([errorMsg, f"{self.constraints[1]} must be a positive integer."])
		except BaseException:
			validText = False
			errorMsg = "\n".join([errorMsg, f"{self.constraints[1]} must be an integer."])

		# If all the data is valid, then the new data is sent to backend and the current screen is updated
		if validText:
			backEnd.add_new_Subject(self.subjectName.text, {int(self.constraints[0]):maxBlocks})
			self.subjectScreen.on_enter()
			self.parent.parent.parent.dismiss()
		# Otherwise, shows new popup, telling user every error in their inputs 
		else:
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

	# Takes in the screen showing the Subjects
	def __init__(self, subjectScreen, **kwargs):
		super().__init__(**kwargs)

		# Initialises variables used when data is submitted
		self.cols = 1
		self.subjectScreen = subjectScreen

		# Creates the GUI screen, adding all of the widgets to the parent grid layout
		newFieldsLayout = GridLayout(cols=2)
		self.subjectName = TextInput(multiline=False)
		self.constraints = backEnd.dbController.get_Constraint_Types()[0]
		self.maxBlocks = TextInput(multiline=False)

		newFieldsLayout.add_widget(Label(text="Name: "))
		newFieldsLayout.add_widget(self.subjectName)
		newFieldsLayout.add_widget(Label(text=self.constraints[1]))
		newFieldsLayout.add_widget(self.maxBlocks)

		# Creates the button to save the Subject made by the user
		submitButton = Button(text="Add to database")
		submitButton.bind(on_release=self.submit_Button)

		# Adds all of the widgets to the screen

		self.add_widget(Label(text="Add Subject"))
		self.add_widget(newFieldsLayout)
		self.add_widget(submitButton)

class DeleteSubject(GridLayout):
	# Class that is used to create the popup that confirms whether or not the user wants to delete the Subject from the database

	# Called if the user confirms their decision
	def confirm_Button(self, instance):
		
		# Deletes the Subject selected and refreshes the screen
		backEnd.delete_Subject(self.subjectID)
		self.subjectDataScreen.on_enter()
		self.parent.parent.parent.dismiss()
	
	# Cancels the operation and closes the popup
	def cancel_Button(self, instance):
		self.parent.parent.parent.dismiss()

	# Takes in the SubjectID and the screen showing the Subjects
	def __init__(self, subjectID, subjectDataScreen, **kwargs):
		super().__init__(**kwargs)

		# Initialises variables used when data is submitted
		self.cols = 1

		self.subjectID = subjectID
		self.subjectDataScreen = subjectDataScreen

		# Creates parent grid layout that will contain the buttons
		buttonLayout = GridLayout(cols=2, padding="10dp")

		# Creates the buttons and adds them to the parent gird
		confirmButton = Button(text="Confirm")
		confirmButton.bind(on_release=self.confirm_Button)
		cancelButton = Button(text="Cancel")
		cancelButton.bind(on_release=self.cancel_Button)

		buttonLayout.add_widget(confirmButton)
		buttonLayout.add_widget(cancelButton)

		# Adds all of the widgets to the screen
		self.add_widget(Label(text="WARNING", font_size="100dp"))
		self.add_widget(Label(text="You are about to delete a Subject from the database.\nPress confirm to continue with the action."))
		self.add_widget(buttonLayout)

class SubjectData(Screen):
	# Class that creates the Subject Data Menu screen

	# Called if the user wants to delete a Subject
	def delete_Subject_Button(self, instance, subjectID):
		popup = Popup(title="Delete Subject", content=DeleteSubject(subjectID, self), size_hint=(None, None), size=(1000, 1000))
		popup.open()
	
	# Called if the user wants to edit a Subject
	def edit_Subject_Button(self, instance, subjectID):
		popup = Popup(title="Edit Subject", content=EditSubject(subjectID, self), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "MainMenu"
		app.windowManager.transition.direction = "right"
	
	# Called if the user wants to add a new Subject
	def add_Subject_Button(self, instance):
		popup = Popup(title="Add Subject", content=AddSubject(self), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Creates the GUI screen
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(rows=2,size_hint_y=None)
		mainLayout.bind(minimum_height=mainLayout.setter("height"))

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(height=350,size_hint_y=None, cols=1, padding="12dp", spacing="24dp")
		topLayout.bind(minimum_height=topLayout.setter("height"))

		# Creates layouts for all of the Buttons (so that they are in the correct position) and creates the Buttons themselves
		returnButtonLayout = GridLayout(cols=5,size_hint_y=None)
		returnButtonLayout.bind(minimum_height=returnButtonLayout.setter("height"))
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButton = Button(text="Go Back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout.add_widget(returnButton)

		subjectButtonLayout = GridLayout(cols=5,size_hint_y=None)
		subjectButtonLayout.bind(minimum_height=subjectButtonLayout.setter("height"))
		subjectButtonLayout.add_widget(Label())
		subjectButtonLayout.add_widget(Label())
		addSubjectButton = Button(text="Add Subject")
		addSubjectButton.bind(on_release=self.add_Subject_Button)
		subjectButtonLayout.add_widget(addSubjectButton)
		subjectButtonLayout.add_widget(Label())
		subjectButtonLayout.add_widget(Label())

		# Adds the Buttons to the grid
		topLayout.add_widget(returnButtonLayout)
		topLayout.add_widget(Label(text="Subject Data Menu"))
		topLayout.add_widget(subjectButtonLayout)

		# Empty grid that will be used to show all of the Subjects and information relating to them
		self.subjectGrid = GridLayout(cols=3,spacing="20dp",size_hint_y=None)
		self.subjectGrid.bind(minimum_height=self.subjectGrid.setter("height"))

		# Adds all the widgets to their correct parents
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.subjectGrid)

		view.add_widget(mainLayout)

		self.add_widget(view)

	def on_enter(self, *args):
		super().on_enter(*args)
		
		# Gets all the data for each Subject
		subjectData = backEnd.get_all_SubjectConstraints()

		# Resets the grid for the Subjects
		self.subjectGrid.clear_widgets()
		self.subjectGrid.add_widget(Label(text="Name"))
		self.subjectGrid.add_widget(Label(text="Constraints"))
		self.subjectGrid.add_widget(Label(text=""))

		# Loops through each Subject in the data, and creates a row for that Subject
		for subjectName in subjectData.keys():
			constraintText = ""
			for constraintType in subjectData[subjectName].keys():
				if constraintType == "ID":
					continue
				constraintText = "\n".join([constraintText, f"{constraintType}: {subjectData[subjectName][constraintType]}"])
			self.subjectGrid.add_widget(Label(text=subjectName))
			self.subjectGrid.add_widget(Label(text=constraintText))

			# Creates Buttons used to edit/delete specific Subjects
			buttonGrid = GridLayout(rows=2, spacing="10dp",size_hint_y=None)
			editButton = Button(text="Edit", height="35dp")
			editButton.bind(on_release=partial(self.edit_Subject_Button, subjectID=subjectData[subjectName]["ID"]))
			buttonGrid.add_widget(editButton)
			deleteButton = Button(text="Delete", height="35dp")
			deleteButton.bind(on_release=partial(self.delete_Subject_Button, subjectID=subjectData[subjectName]["ID"]))
			buttonGrid.add_widget(deleteButton)
			self.subjectGrid.add_widget(buttonGrid)

class GetNewPopulationDetails(GridLayout):
	# Class used to create the popup to get the details of a new Population from the user

	# Called when the user wants to close the popup
	def close_Button(self, instance):
		self.parent.parent.parent.dismiss()

	# Called when the user wants to submit the new details for the new Population
	def submit_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the PopulationName field
		if self.newPopulationName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name needs to be in the correct format. Currently, this field is empty."])
		if len(self.newPopulationName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name should have length less than or equal to 30."])
		
		# Validates the PopulationOptions field
		try:
			options = int(self.newPopulationOptions.text)
			if options <= 0:
				validText = False
				errorMsg = "\n".join([errorMsg, "Options should be a positive integer."])
		except BaseException:
			validText = False
			errorMsg = "\n".join([errorMsg, "Options should be an integer."])

		# If any of the data is invalid, shows new popup, telling user every error in their inputs 
		if not validText:
			self.newPopulationName.text = ""
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

		# Otherwise, the new data is sent to backend and the current screen is updated
		else:
			backEnd.create_blank_Population(self.newPopulationName.text, options)
			self.parent.parent.parent.dismiss()
			app.windowManager.current = "ManualEditPopulation"
			app.windowManager.transition.direction = "left"

	# Creates the GUI screen for the popup
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		# Creates layouts for the different sections of the popup
		closeButton = Button(text="Close")
		closeButton.bind(on_release=self.close_Button)
		closeButtonLayout = GridLayout(cols=3)
		closeButtonLayout.add_widget(Label())
		closeButtonLayout.add_widget(Label())
		closeButtonLayout.add_widget(closeButton)

		populationDetailsInputLayout = GridLayout(cols=2)
		populationDetailsInputLayout.add_widget(Label(text="Population Name:"))
		self.newPopulationName = TextInput(text="", multiline=False)
		populationDetailsInputLayout.add_widget(self.newPopulationName)
		populationDetailsInputLayout.add_widget(Label(text="Maximum number of Subjects\nper Student:"))
		self.newPopulationOptions = TextInput(text="", multiline=False)
		populationDetailsInputLayout.add_widget(self.newPopulationOptions)
		submitButton = Button(text="Submit")
		submitButton.bind(on_release=self.submit_Button)

		# Adds the layouts to the parent grid
		self.add_widget(closeButtonLayout)
		self.add_widget(populationDetailsInputLayout)
		self.add_widget(submitButton)

class StudentPopulations(Screen):
	# Class that creates the Student Populations Menu screen

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "MainMenu"
		app.windowManager.transition.direction = "right"

	# Called if the user wants to load an existing Population from the database
	def load_existing_Button(self, instance):
		app.windowManager.current = "LoadExistingStudentPopulation"
		app.windowManager.transition.direction = "left"
	
	# Called if the user wants to load a Population from an external file
	def import_from_file_Button(self, instance):
		app.windowManager.current = "ImportPopulationFromFile"
		app.windowManager.transition.direction = "left"
	
	# Called if the user wants to create an empty Population and modify it themselves
	def manually_add_data_Button(self, instance):
		popup = Popup(title = "New Population Name", content=GetNewPopulationDetails(), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(rows=5, spacing="20dp", padding="12dp")

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(cols=1, size_hint_y=None,height=125)

		# Creates the layout that holds the return Button, and creates the return Button
		returnButtonLayout = GridLayout(cols=5)
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButton = Button(text="Go Back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout.add_widget(returnButton)

		topLayout.add_widget(returnButtonLayout)
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(Label(text="Student Populations Menu"))

		# Creating the layouts for the main Buttons in the screen
		loadExistingButtonLayout = GridLayout(cols=3)
		loadExistingButtonLayout.add_widget(Label())
		loadExistingButton = Button(text="Load existing Student Population")
		loadExistingButton.bind(on_release=self.load_existing_Button)
		loadExistingButtonLayout.add_widget(loadExistingButton)
		loadExistingButtonLayout.add_widget(Label())

		importFromFileButtonLayout = GridLayout(cols=3)
		importFromFileButtonLayout.add_widget(Label())
		importFromFileButton = Button(text="Import data from external file")
		importFromFileButton.bind(on_release=self.import_from_file_Button)
		importFromFileButtonLayout.add_widget(importFromFileButton)
		importFromFileButtonLayout.add_widget(Label())

		manuallyAddDataButtonLayout = GridLayout(cols=3)
		manuallyAddDataButtonLayout.add_widget(Label())
		self.manuallyAddDataButton = Button(text="Manually add data")
		self.manuallyAddDataButton.bind(on_release=self.manually_add_data_Button)
		manuallyAddDataButtonLayout.add_widget(self.manuallyAddDataButton)
		manuallyAddDataButtonLayout.add_widget(Label())

		# Adding the main Buttons to the grid
		mainLayout.add_widget(loadExistingButtonLayout)
		mainLayout.add_widget(importFromFileButtonLayout)
		mainLayout.add_widget(manuallyAddDataButtonLayout)

		# Adding the grid to the screen
		self.add_widget(mainLayout)
			
class NoPopulations(GridLayout):
	# Class that creates a popup that tells the user that no Populations exist in the database

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		self.parent.parent.parent.dismiss()
		app.windowManager.current = "StudentPopulations"
		app.windowManager.transition.direction = "right"

	# Creates the GUI screen
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Creates the layout for the return Button
		self.cols = 1
		returnButton = Button(text="Go Back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout = GridLayout(cols=3)
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(returnButton)
		returnButtonLayout.add_widget(Label())

		# Adds all of the widgets to the screen
		self.add_widget(Label(text="Error. No Populations exist in the database."))
		self.add_widget(Label(text="A Population must either be imported or created manually."))
		self.add_widget(returnButtonLayout)
		
class LoadExistingStudentPopulation(Screen):
	# Class that creates the Load Existing Population Menu screen

	# Called if the user wants to select a Population
	def select_Population_Button(self, instance, populationID):
		backEnd.get_Population_from_db(populationID)
		app.windowManager.current = "ManualEditPopulation"
		app.windowManager.transition.direction = "left"

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "StudentPopulations"
		app.windowManager.transition.direction = "right"

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(rows=2,size_hint_y=None)
		mainLayout.bind(minimum_height=mainLayout.setter("height"))

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(size_hint_y=None, height=350, cols=1,padding="12dp")
		topLayout.bind(minimum_height=topLayout.setter("height"))
		
		# Creates layouts for all of the Buttons (so that they are in the correct position) and creates the Buttons themselves
		returnButtonLayout = GridLayout(size_hint_y=None, cols=5)
		returnButtonLayout.bind(minimum_height=returnButtonLayout.setter("height"))
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		returnButton = Button(text="Go Back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout.add_widget(returnButton)
		
		# Adds the Buttons to the grid
		topLayout.add_widget(returnButtonLayout)
		topLayout.add_widget(Label(text="Population Select Menu"))
		topLayout.add_widget(Label())

		# Empty grid that will be used to show all of the Populations and information relating to them
		self.populationGrid = GridLayout(size_hint_y=None, cols=3, spacing="15dp", padding="15dp")
		self.populationGrid.bind(minimum_height=self.populationGrid.setter("height"))

		# Adds all the widgets to their correct parents
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.populationGrid)

		view.add_widget(mainLayout)

		self.add_widget(view)

	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Gets all the data for each Population
		populationData = backEnd.get_Populations()

		# Runs if there are not Populations in the database
		if populationData == {}:
			popup = Popup(title="No Populations", content=NoPopulations(), size_hint=(None, None), size=(1000, 1000))
			popup.open()
			return
		
		# Resets the grid for the Populations
		self.populationGrid.clear_widgets()
		self.populationGrid.add_widget(Label(text="Name", height="50dp", size_hint_y=None))
		self.populationGrid.add_widget(Label(text="Details", height="50dp", size_hint_y=None))
		self.populationGrid.add_widget(Label(text="", height="50dp", size_hint_y=None))

		# Loops through each Population in the data, and creates a row for that Population
		for populationName in populationData.keys():
			populationText = ""
			for detail in populationData[populationName].keys():
				if detail == "ID":
					continue
				populationText = "\n".join([populationText, f"{detail}: {populationData[populationName][detail]}"])
			self.populationGrid.add_widget(Label(text=populationName, height="50dp", size_hint_y=None))
			self.populationGrid.add_widget(Label(text=populationText, height="50dp", size_hint_y=None))

			# Creates Button used to edit specific Populations
			selectPopulationButton = Button(text=f"Select {populationName}", height="50dp", size_hint_y=None)
			selectPopulationButton.bind(on_release=partial(self.select_Population_Button, populationID=populationData[populationName]["ID"]))
			self.populationGrid.add_widget(selectPopulationButton)

class NewSubjectsAddedAlert(GridLayout):
	# Class used for creating the popup informing the user that new Subjects have been added to the database as a result of the Population being imported from a file

	# Called if the user confirms they have seen the popup
	def confirm_Button(self, instance):
		app.windowManager.current = "SubjectData"
		app.windowManager.transition.direction = "right"
		self.parent.parent.parent.dismiss()

	# Creates the GUI screen
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		# Creates all of the widgets and adds them to the parent grid
		self.add_widget(Label(text="WARNING", font_size="100dp"))
		self.add_widget(Label(text="New Subjects have been added to the database."))
		self.add_widget(Label(text="These must have Constraints added to them, otherwise the blocking algorithm will not work!"))
		confirmButton = Button(text="Confirm")
		confirmButton.bind(on_release=self.confirm_Button)
		self.add_widget(confirmButton)

class GetNewPopulationDetailsForFile(GridLayout):
	# Class that is used to create the popup the gets the Population details for a Population that had been imported from a file

	# Called when the user wanrs to submit the new details for the new Population
	def submit_button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the PopulationName field
		if self.newPopulationName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name needs to be in the correct format. Currently, this field is empty."])
		if len(self.newPopulationName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name should have length less than or equal to 30."])
		
		# Validates the PopulationOptions field
		try:
			choices = int(self.newPopulationChoice.text)
			if choices <= 0:
				validText = False
				errorMsg = "\n".join([errorMsg, "The maximum Subjects should be a positive integer."])
		except BaseException:
			validText = False
			errorMsg = "\n".join([errorMsg, "The maximum Subjects should be an integer."])

		# If any of the data is invalid, shows new popup, telling user every error in their inputs 
		if not validText:
			self.newPopulationName.text = ""
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

		# Otherwise, the new data is sent to backend and the current screen is updated
		else:
			# Tries to setup the new Population using the filepath given
			try:
				newSubjects = backEnd.setup_new_Population_from_file(self.filePath, self.newPopulationName.text, choices)
			
			# Runs if the filepath does not exist
			except Exception as err:
				popup = Popup(title="Error when accessing file!", content=Label(text=str(err), font_size="75dp"), size_hint=(None, None), size=(1000, 1000))
				popup.open()
				self.parent.parent.parent.dismiss()
				return
			
			# If Subject were created in this process, then the correct popup is displayed on the screen
			if newSubjects:
				popup = Popup(title="Alert - new Subjects added!", content=NewSubjectsAddedAlert(), size_hint=(None, None), size=(1000, 1000))
				popup.open()
			self.parent.parent.parent.dismiss()

	# Creates the GUI screen for the popup
	def __init__(self, filePath, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		# Creates the layout for the input fields, and adds the correct widgets to it
		inputFieldsLayout = GridLayout(cols=2)
		inputFieldsLayout.add_widget(Label(text="New Population Name:"))
		self.newPopulationName = TextInput(text="", multiline=False)
		self.filePath = filePath
		inputFieldsLayout.add_widget(self.newPopulationName)
		inputFieldsLayout.add_widget(Label(text="Max Subject per Student:"))
		self.newPopulationChoice = TextInput(text="", multiline=False)
		inputFieldsLayout.add_widget(self.newPopulationChoice)
		submitButton = Button(text="Submit")
		submitButton.bind(on_release=self.submit_button)

		# Adds the widgets to the screen
		self.add_widget(inputFieldsLayout)
		self.add_widget(submitButton)

class HelpImportFromFile(GridLayout):
	# Class that is used to create the popup showing how the user's file should be formatted

	# Called when the user wants to close the popup
	def close_Button(self, instance):
		self.parent.parent.parent.dismiss()

	# Creates the GUI screen for the popup
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		# Creates the layout for the button
		closeButton = Button(text="Close")
		closeButton.bind(on_release=self.close_Button)
		closeButtonLayout = GridLayout(cols=3)
		closeButtonLayout.add_widget(Label())
		closeButtonLayout.add_widget(closeButton)
		closeButtonLayout.add_widget(Label())

		# Adds the widgets to the parent grid
		self.add_widget(Label(text="Population Data should be in the following format:\nFirstName,Surname,Choice1,Choice2,Choice3,..."))
		self.add_widget(Label(text="As shown above, each Student should be on separate lines."))
		self.add_widget(Label(text="An example of how this might be done is as follows:"))
		self.add_widget(Label(text="""S1,S1,Further Maths,Maths,Physics,Chemistry
S2,S2,Maths,Art,Physics,Biology
S3,S3,Further Maths,Maths,Music,
S4,S4,Greek,Music,Art,Latin"""))
		self.add_widget(closeButtonLayout)

class ImportPopulationFromFile(Screen):
	# Class that creates the Import Population Menu screen

	# Called when the user wants help on how to format their file
	def help_Button(self, instance):
		popup = Popup(title="Import Help", content=HelpImportFromFile(), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "StudentPopulations"
		app.windowManager.transition.direction = "right"
	
	# Called if the user has inputted the filepath of the file they want to import
	def import_file(self, instance):

		# Runs only if the filepath field isn't empty
		if self.filePathInput.text:
			
			# Updates the screen
			app.windowManager.current = "StudentPopulations"
			app.windowManager.transition.direction = "left"

			# Creates a popup to get the Population Details
			popup = Popup(title="New Population Name", content=GetNewPopulationDetailsForFile(self.filePathInput.text), size_hint=(None, None), size=(1000, 1000))
			popup.open()
		self.filePathInput.text = ""

	# Creates the GUI for the screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates the main grid that displays all of the widgets
		mainLayout = GridLayout(rows=3, spacing="15dp", padding="15dp")

		# Creates the Buttons shown at the top of the page
		helpButtonLayout = GridLayout(rows=3)
		helpButton = Button(text="Help")
		helpButton.bind(on_release=self.help_Button)
		helpButtonLayout.add_widget(helpButton)
		helpButtonLayout.add_widget(Label())
		helpButtonLayout.add_widget(Label())

		returnButtonLayout = GridLayout(rows=3)
		returnButton = Button(text="Go back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout.add_widget(returnButton)
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())

		# Creates the grid that stores the widgets at the top of the screen
		topLayout = GridLayout(cols=5,spacing="15dp")
		topLayout.add_widget(helpButtonLayout)
		topLayout.add_widget(Label())
		topLayout.add_widget(Label(text="Enter full file path below:"))
		topLayout.add_widget(Label())
		topLayout.add_widget(returnButtonLayout)

		# Creates the grid that stores widgets responsible for getting the file path from the user
		filePathLayout = GridLayout(cols=4)
		filePathLayout.add_widget(Label())
		self.filePathInput = TextInput(multiline=False)
		filePathLayout.add_widget(self.filePathInput)
		importFileButton = Button(text="Import data")
		importFileButton.bind(on_release=self.import_file)
		filePathLayout.add_widget(importFileButton)
		filePathLayout.add_widget(Label())

		# Adds all of the widgets to the screen
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(filePathLayout)
		mainLayout.add_widget(Label())

		self.add_widget(mainLayout)

class EditPopulationName(GridLayout):
	# Class that is used to create the popup to change the name of the Population selected

	# Creates the GUI screen for the popup
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.add_widget(Label(text="Edit Population Name"))

		# Creates the grid that is used to place the widgets for the old PopulationName and the new PopulationName
		nameGrid = GridLayout(cols=2)

		nameGrid.add_widget(Label(text="Current Population Name:"))
		nameGrid.add_widget(Label(text=backEnd.population.get_Population_Name()))

		nameGrid.add_widget(Label(text="New Population Name:"))
		self.newName = TextInput(text=backEnd.population.get_Population_Name())
		nameGrid.add_widget(self.newName)

		# Adds the grid to the screen
		self.add_widget(nameGrid)

		# Creates the submit Button and adds it to the screen
		saveChangesButton = Button(text="Save changes")
		saveChangesButton.bind(on_release=self.save_changes_Button)
		self.add_widget(saveChangesButton)

	# Called when the user wants to save the changes thay have made to the PopulationName
	def save_changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the PopulationName field
		if self.newName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name needs to be in the correct format. Currently, this field is empty."])
		if len(self.newName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Population name should have length less than or equal to 30."])

		# If any of the data is invalid, shows new popup, telling user every error in their inputs 
		if not validText:
			self.newPopulationName.text = ""
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

		# Otherwise, the new data is sent to backend and the current screen is updated
		else:
			backEnd.set_new_Population_Name(self.newName.text)
			self.parent.parent.parent.dismiss()

class EditPopulationOptions(GridLayout):
	# Class that is used to create the popup to change the Options of the Population selected

	# Creates the GUI screen for the popup
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.add_widget(Label(text="Edit Population Options"))

		# Creates the grid that is used to place the widgets for the old PopulationOptions and the new PopulationOptions
		optionsGrid = GridLayout(cols=2)

		optionsGrid.add_widget(Label(text="Current Population Options:"))
		optionsGrid.add_widget(Label(text=str(backEnd.population.get_Options())))

		optionsGrid.add_widget(Label(text="New Population Options:"))
		self.newOptions = TextInput(text=str(backEnd.population.get_Options()))
		optionsGrid.add_widget(self.newOptions)

		# Adds the grid to the screen
		self.add_widget(optionsGrid)

		# Creates the submit Button and adds it to the screen
		saveChangesButton = Button(text="Save changes")
		saveChangesButton.bind(on_release=self.save_changes_Button)
		self.add_widget(saveChangesButton)

	# Called when the user wants to save the changes thay have made to the PopulationName
	def save_changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the PopulationName field
		try:
			options = int(self.newOptions.text)
			if options <= 0:
				validText = False
				errorMsg = "\n".join([errorMsg, "Options should be a positive integer."])
		except BaseException:
			validText = False
			errorMsg = "\n".join([errorMsg, "Options should be an integer."])

		# If any of the data is invalid, shows new popup, telling user every error in their inputs 
		if not validText:
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

		# Otherwise, the new data is sent to backend and the current screen is updated
		else:
			backEnd.set_new_Population_Options(int(self.newOptions.text))
			self.parent.parent.parent.dismiss()

class ChooseNewSubjectForStudent(GridLayout):
	# Class that is used to create the popup for the user to change a Subject that a Student is studying

	# Called when the user selects a Subject in the grid presented
	def subject_Button(self, instance, index, studentDetailsClass):
		studentDetailsClass.edit_choice(instance, index, self.parent.parent.parent)
		
	# Creates the GUI screen for the popup
	def __init__(self, studentDetailsClass, choiceIndex, subjects, **kwargs):
		super().__init__(**kwargs)

		self.cols = 3

		# Loops through every Subject in the database and adds a corresponding Button to the screen
		for subject in subjects:
			subjectButton = Button(text=subject)
			subjectButton.bind(on_release=partial(self.subject_Button, index=choiceIndex, studentDetailsClass=studentDetailsClass))
			self.add_widget(subjectButton)

class EditStudentDetails(FloatLayout):
	# Class that is used to create the popup to change any details of a Student in the Population

	# Called when the user updates one of the Student's choices
	def edit_choice(self, instance, index, popup):
		self.newChoices[index].text = instance.text
		popup.dismiss()

	# Creates the GUI screen for the popup
	def __init__(self, studentID, **kwargs):
		super().__init__(**kwargs)

		# Gets the old Student instance
		self.studentID = studentID

		for student in backEnd.population.get_Students():
			if self.studentID == student.get_StudentID():
				oldStudent = student
				break

		# Adds the title widget in the correct position on the screen
		self.add_widget(Label(text="Edit Student Details", size_hint=(1, 0.25), pos_hint={"x":0, "y":0.75}))

		# Creates the grid used to place all of the widgets
		mainLayout = GridLayout(cols=2, size_hint=(1, 0.5), pos_hint={"x":0, "y":0.25})

		# Adds a row in the main grid for each field of the Student entity
		mainLayout.add_widget(Label(text="First Name: "))
		dataInputLayout = GridLayout(rows=2)
		dataInputLayout.add_widget(Label(text=oldStudent.get_Student_Firstname()))
		self.newStudentFirstName = TextInput(text=oldStudent.get_Student_Firstname())
		dataInputLayout.add_widget(self.newStudentFirstName)
		mainLayout.add_widget(dataInputLayout)

		mainLayout.add_widget(Label(text="Surname: "))
		dataInputLayout = GridLayout(rows=2)
		dataInputLayout.add_widget(Label(text=oldStudent.get_Student_Surname()))
		self.newStudentSurname = TextInput(text=oldStudent.get_Student_Surname())
		dataInputLayout.add_widget(self.newStudentSurname)
		mainLayout.add_widget(dataInputLayout)

		# Gets the Student's old choices in a readable format
		oldChoices = [subject.get_Subject_Name() for subject in oldStudent.get_Student_Subjects()]
		
		while len(oldChoices) != backEnd.population.get_Options():
			oldChoices.append("")

		self.newChoices = []
		subjects =[""] + [subject.get_Subject_Name() for subject in backEnd.population.get_Subjects()]

		# Loops through all of the Student choices and adds them as a new row in the popup
		for i in range(backEnd.population.get_Options()):
			choicesPopup = Popup(title="Select new Subject", content=ChooseNewSubjectForStudent(self, i, subjects), size_hint=(None, None), size=(750, 750))
			mainLayout.add_widget(Label(text=f"Choice {i+1}: "))
			dataInputLayout = GridLayout(rows=2)
			dataInputLayout.add_widget(Label(text=oldChoices[i]))
			showDropdownButton = Button(text=oldChoices[i])
			showDropdownButton.bind(on_release=choicesPopup.open)
			self.newChoices.append(showDropdownButton)
			dataInputLayout.add_widget(self.newChoices[i])
			mainLayout.add_widget(dataInputLayout)
		
		# Creates the submit Button and adds it to the screen
		saveChangesButton = Button(text="Save Changes", size_hint=(1, 0.25), pos_hint={"x":0, "y":0})
		saveChangesButton.bind(on_release=self.save_changes_Button)
		self.add_widget(mainLayout)
		self.add_widget(saveChangesButton)

	# Called when the user wants to save the changes thay have made to the Student
	def save_changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the StudentFirstName field
		if self.newStudentFirstName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's first name needs to be non-empty."])
		if len(self.newStudentFirstName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's first name length needs to be less than or equal to 30 characters."])

		# Validates the StudentSurname field
		if self.newStudentSurname.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's surname needs to be non-empty."])
		if len(self.newStudentSurname.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's surname length needs to be less than or equal to 30 characters."])
		
		# If all the data is valid, then the new data is sent to backend
		if validText:
			backEnd.edit_Student_details(self.studentID, self.newStudentFirstName.text, self.newStudentSurname.text, [button.text for button in self.newChoices if button.text != ""])
			self.parent.parent.parent.dismiss()

		# Otherwise, shows new popup, telling user every error in their inputs 
		else:
			popup = Popup(title="Error", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

class DeleteStudent(GridLayout):
	# Class that creates a popup asking the user to confirm the deletion of a Student from the Population

	# Called when the user confirms they want to delete the Student
	def confirm_Button(self, instance):
		backEnd.delete_Student(self.studentID)
		self.editPopulationScreen.on_enter()
		self.parent.parent.parent.dismiss()
	
	# Called when the user cancels their decision
	def cancel_Button(self, instance):
		self.parent.parent.parent.dismiss()

	# Creates the GUI screen for the popup
	def __init__(self, studentID, editPopulationScreen, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.studentID = studentID
		self.editPopulationScreen = editPopulationScreen

		# Creates the Buttons and adds them to the button grid
		buttonLayout = GridLayout(cols=2, padding="10dp")
		confirmButton = Button(text="Confirm")
		confirmButton.bind(on_release=self.confirm_Button)
		cancelButton = Button(text="Cancel")
		cancelButton.bind(on_release=self.cancel_Button)

		buttonLayout.add_widget(confirmButton)
		buttonLayout.add_widget(cancelButton)

		# Adds all of the widgets to the screen
		self.add_widget(Label(text="WARNING", font_size="100dp"))
		self.add_widget(Label(text="You are about to delete a Student from the database.\nPress confirm to continue with the action."))
		self.add_widget(buttonLayout)

class AddStudent(FloatLayout):
	# Class that creates a popup, asking the user for details of the Student they would like to add

	# Called when the user wants to edit one of the Student's choices
	def edit_choice(self, instance, index, popup):
		self.newChoices[index].text = instance.text
		popup.dismiss()

	# Creates the GUI screen for the popup
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Adds the title widget in the correct position on the screen
		self.add_widget(Label(text="Add New Student", size_hint=(1, 0.25), pos_hint={"x":0, "y":0.75}))

		# Creates the grid used to place all of the widgets
		mainLayout = GridLayout(cols=2, size_hint=(1, 0.5), pos_hint={"x":0, "y":0.25})

		# Adds a row in the main grid for each field of the Student entity
		mainLayout.add_widget(Label(text="First Name: "))
		self.studentFirstName = TextInput(text="")
		mainLayout.add_widget(self.studentFirstName)

		mainLayout.add_widget(Label(text="Surname: "))
		self.studentSurname = TextInput(text="")
		mainLayout.add_widget(self.studentSurname)

		oldChoices = []
		
		for i in range(backEnd.population.get_Options()):
			oldChoices.append("")

		self.newChoices = []
		subjects =[""] + [subject.get_Subject_Name() for subject in backEnd.population.get_Subjects()]

		# Loops through all of the Student choices and adds them as a new row in the popup
		for i in range(backEnd.population.get_Options()):
			choicesPopup = Popup(title="Select new Subject", content=ChooseNewSubjectForStudent(self, i, subjects), size_hint=(None, None), size=(750, 750))
			mainLayout.add_widget(Label(text=f"Choice {i+1}: "))
			dataInputLayout = GridLayout(rows=2)
			dataInputLayout.add_widget(Label(text=oldChoices[i]))
			showDropdownButton = Button(text=oldChoices[i])
			showDropdownButton.bind(on_release=choicesPopup.open)
			self.newChoices.append(showDropdownButton)
			dataInputLayout.add_widget(self.newChoices[i])
			mainLayout.add_widget(dataInputLayout)
		
		# Creates the submit Button and adds it to the screen
		saveChangesButton = Button(text="Save Changes", size_hint=(1, 0.25), pos_hint={"x":0, "y":0})
		saveChangesButton.bind(on_release=self.save_changes_Button)
		self.add_widget(mainLayout)
		self.add_widget(saveChangesButton)

	# Called when the user wants to save the changes thay have made to the Student
	def save_changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the StudentFirstName field
		if self.studentFirstName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's first name needs to be non-empty."])
		if len(self.studentFirstName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's first name length needs to be less than or equal to 30 characters."])

		# Validates the StudentSurname field
		if self.studentSurname.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's surname needs to be non-empty."])
		if len(self.studentSurname.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Student's surname length needs to be less than or equal to 30 characters."])

		# If all the data is valid, then the new data is sent to backend
		if validText:
			backEnd.add_new_Student(self.studentFirstName.text, self.studentSurname.text, [button.text for button in self.newChoices if button.text != ""])
			self.parent.parent.parent.dismiss()

		# Otherwise, shows new popup, telling user every error in their inputs 
		else:
			popup = Popup(title="Error", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

class ManualEditPopulation(Screen):
	# Class that creates the Manual Edit Population screen

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "LoadExistingStudentPopulation"
		app.windowManager.transition.direction = "right"
	
	# Called if the user wants to go to the Clash Table screen
	def clash_table_Button(self, instance):
		app.windowManager.current = "ClashTable"
		app.windowManager.transition.direction = "left"
	
	# Called if the user wants to edit the name of the Population
	def edit_Population_name_Button(self, instance):
		self.popupWindow = Popup(title="Edit Population Name", content=EditPopulationName(), size_hint=(None, None), size=(1000,1000), on_dismiss=self.on_enter)
		self.popupWindow.open()
	
	# Called if the user wants to edit the number of Options of the Population
	def edit_Population_Options_Button(self, instance):
		self.popupWindow = Popup(title="Edit Population Options", content=EditPopulationOptions(), size_hint=(None, None), size=(1000,1000), on_dismiss=self.on_enter)
		self.popupWindow.open()

	# Called if the user wants to add a Student to the Population
	def add_Student_Button(self, instance):
		self.popupWindow = Popup(title="Add New Student", content=AddStudent(), size_hint=(None, None), size=(1000,1000), on_dismiss=self.on_enter)
		self.popupWindow.open()

	# Called if the user wants to edit the details of a Student in the Population
	def edit_Student_Button(self, instance, studentID):
		self.popupWindow = Popup(title="Edit Student Details", content=EditStudentDetails(studentID), size_hint=(None, None), size=(1000,1000), on_dismiss=self.on_enter)
		self.popupWindow.open()

	# Called if the user wants to delete a Student in the Population
	def delete_Student_Button(self, instance, studentID):
		popup = Popup(title="Delete Student", content=DeleteStudent(studentID, self), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1, size_hint_y=None)
		mainLayout.bind(minimum_height=mainLayout.setter("height"))

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(rows=1, size_hint_y=None, padding="10dp", spacing="15dp")
		topLayout.bind(minimum_height=topLayout.setter("height"))

		# Creates all of the widgets for the top half of the screen
		clashtableButton = Button(text="Clash Table")
		clashtableButton.bind(on_release=self.clash_table_Button)

		populationFieldNameLayout = GridLayout(cols=1, size_hint_y=None)
		populationFieldNameLayout.bind(minimum_height=populationFieldNameLayout.setter("height"))
		populationFieldNameLayout.add_widget(Label(text="Population Name:"))
		populationFieldNameLayout.add_widget(Label(text="Max Subjects per Student:"))

		populationLabelLayout = GridLayout(cols=1,size_hint_y=None)
		populationLabelLayout.bind(minimum_height=populationLabelLayout.setter("height"))
		self.populationLabel = Label()
		populationLabelLayout.add_widget(self.populationLabel)
		self.populationOptions = Label()
		populationLabelLayout.add_widget(self.populationOptions)

		editPopulationNameButton = Button(text="Edit")
		editPopulationNameButton.bind(on_release=self.edit_Population_name_Button)
		editPopulationOptionsButton = Button(text="Edit")
		editPopulationOptionsButton.bind(on_release=self.edit_Population_Options_Button)
		editPopulationDetailsButtonLayout = GridLayout(cols=1, size_hint_y=None)
		editPopulationDetailsButtonLayout.bind(minimum_height=editPopulationDetailsButtonLayout.setter("height"))
		editPopulationDetailsButtonLayout.add_widget(editPopulationNameButton)
		editPopulationDetailsButtonLayout.add_widget(editPopulationOptionsButton)

		returnButton = Button(text="Go back")
		returnButton.bind(on_release=self.return_Button)

		# Adds all of the widgets for the top half of the screen to the top grid widget
		topLayout.add_widget(clashtableButton)
		topLayout.add_widget(populationFieldNameLayout)
		topLayout.add_widget(populationLabelLayout)
		topLayout.add_widget(editPopulationDetailsButtonLayout)
		topLayout.add_widget(returnButton)

		# Creates the Button to add Students to the Population
		addStudentButtonLayout = GridLayout(cols=3, size_hint_y=None, spacing="15dp", padding="25dp")
		addStudentButtonLayout.bind(minimum_height=addStudentButtonLayout.setter("height"))
		paddingLayout = GridLayout(cols=1, size_hint_y=None)
		paddingLayout.bind(minimum_height=paddingLayout.setter("height"))
		paddingLayout.add_widget(Label())
		paddingLayout.add_widget(Label())
		paddingLayout.add_widget(Label())
		addStudentButtonLayout.add_widget(paddingLayout)
		addStudentButton = Button(text="Add Student")
		addStudentButton.bind(on_release=self.add_Student_Button)
		addStudentButtonLayout.add_widget(addStudentButton)
		addStudentButtonLayout.add_widget(Label())

		# Creates an empty grid that will store the details of all of the Students in the Population
		self.studentDetails = GridLayout(cols=1, spacing="50dp", size_hint_y=None, padding="15dp")
		self.studentDetails.bind(minimum_height=self.studentDetails.setter("height"))

		# Adds all of the widgets to the main grid widget
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(addStudentButtonLayout)
		mainLayout.add_widget(self.studentDetails)

		# Adds the widgets to the screen
		view.add_widget(mainLayout)

		self.add_widget(view)

	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Updates the text at the top of the screen to match the current Population
		self.populationLabel.text = backEnd.population.get_Population_Name()
		self.populationOptions.text = str(backEnd.population.get_Options())

		# Gets all of the Student data from the Population
		populationDetails = backEnd.get_all_Student_Choices()

		# Resets the grid for the Students
		self.studentDetails.clear_widgets()
		self.studentDetails.cols = backEnd.population.get_Options() + 2
		self.studentDetails.add_widget(Label(text="Name"))

		# Sets the columns of the grid
		for i in range(backEnd.population.get_Options()):
			self.studentDetails.add_widget(Label(text=f"Choice {i+1}"))
		self.studentDetails.add_widget(Label(text=""))

		# Loops through every Student in the Population, and adds their choices and the edit/delete buttons to the screen
		for student in populationDetails.keys():

			# Adds Student choices
			subjects = populationDetails[student][1:]
			self.studentDetails.add_widget(Label(text=student))
			for i in range(backEnd.population.get_Options()):
				try:
					self.studentDetails.add_widget(Label(text=subjects[i]))
				except BaseException:
					self.studentDetails.add_widget(Label())

			# Adds Buttons
			buttonGrid = GridLayout(cols=2, size_hint_y=None)
			buttonGrid.bind(minimum_height=buttonGrid.setter("height"))
			editButton = Button(text="Edit", height="50dp")
			editButton.bind(on_release=partial(self.edit_Student_Button, studentID=populationDetails[student][0]))
			buttonGrid.add_widget(editButton)
			deleteButton = Button(text="Delete", height="50dp")
			deleteButton.bind(on_release=partial(self.delete_Student_Button, studentID=populationDetails[student][0]))
			buttonGrid.add_widget(deleteButton)
			self.studentDetails.add_widget(buttonGrid)

class ClashTable(Screen):
	# Class that creates the Clash Table screen

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "ManualEditPopulation"
		app.windowManager.transition.direction = "right"
	
	# Called if the user wants to view the Patterns list
	def pattern_Button(self, instance):
		app.windowManager.current = "ViewPatternList"
		app.windowManager.transition.direction = "left"

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1,size_hint_y=None,padding="15dp")
		mainLayout.bind(minimum_height=mainLayout.setter("height"))
		
		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(rows=1,size_hint_y=None)
		topLayout.bind(minimum_height=topLayout.setter("height"))

		# Creates and adds widgets to the top half of the screen
		topLayout.add_widget(Label())
		topLayout.add_widget(Label(text="Clash Table:"))
		returnButton = Button(text="Go back")
		returnButton.bind(on_release=self.return_Button)
		topLayout.add_widget(returnButton)

		# Creates an empty grid to store the Clash Table
		self.clashGridHolder = GridLayout(rows=1,size_hint_y=None)
		self.clashGridHolder.bind(minimum_height=self.clashGridHolder.setter("height"))

		# Creates the grid layout that is responsible for creating the bottom half of the screen
		bottomLayout = GridLayout(cols=3,size_hint_y=None)
		bottomLayout.bind(minimum_height=bottomLayout.setter("height"))

		# Creates and adds widgets to the bottom half of the screen
		bottomLayout.add_widget(Label())
		patternButton = Button(text="View Patterns")
		patternButton.bind(on_release=self.pattern_Button)
		bottomLayout.add_widget(patternButton)
		bottomLayout.add_widget(Label())

		# Adds widgets to the main grid layout
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.clashGridHolder)
		mainLayout.add_widget(bottomLayout)

		# Adds widgets to the screen
		view.add_widget(mainLayout)

		self.add_widget(view)
	
	# Run whenever the user enters this screen
	def on_enter(self):
		
		# Gets the Clash Table
		clashTable = backEnd.get_Clash_Table()
		subjectNames = clashTable.keys()

		# Creates the table for the Clash Table
		clashGrid = GridLayout(rows=len(subjectNames)+1,size_hint_y=None, spacing="35dp", padding="20dp")
		clashGrid.bind(minimum_height=clashGrid.setter("height"))
		clashGrid.add_widget(Label(text=""))

		# Adds the columns to the table
		for subjectName in subjectNames:
			clashGrid.add_widget(Label(text=subjectName))

		# Loops through every element in the dictionary, adding it to the table
		for subject1 in subjectNames:
			clashGrid.add_widget(Label(text=subject1))
			for subject2 in subjectNames:
				clashGrid.add_widget(Label(text=str(clashTable[subject1][subject2])))
		
		# Adds the table to the grid layout
		self.clashGridHolder.clear_widgets()
		self.clashGridHolder.add_widget(clashGrid)

class ViewPatternList(Screen):
	# Class that creates the Pattern screen

	# Called if the user wants to create a new Pattern manually
	def create_new_Pattern_Button(self, instance):
		app.viewPatternScreen.newPattern = True
		app.windowManager.current = "EditPattern"
		app.windowManager.transition.direction = "left"

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "ClashTable"
		app.windowManager.transition.direction = "right"
	
	# Called if the user wants the program to automatically generate a Pattern
	def block_generate_Button(self, instance):
		app.windowManager.current = "BlockPatternGeneration"
		app.windowManager.transition.direction = "left"
	
	# Called if the user wants to delete a Pattern from the list
	def delete_Pattern_Button(self, instance, patternID):
		backEnd.delete_Pattern(patternID)
		self.on_enter()

	# Called if the user wants to view/edit a Pattern in the list
	def edit_Pattern_Button(self, instance, patternID):
		app.viewPatternScreen.patternID = patternID
		app.viewPatternScreen.newPattern = False
		app.windowManager.current = "EditPattern"
		app.windowManager.transition.direction = "left"

	# Creates the GUI
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1,size_hint_y=None,padding="15dp")
		mainLayout.bind(minimum_height=mainLayout.setter("height"))
		
		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(rows=1,size_hint_y=None)
		topLayout.bind(minimum_height=topLayout.setter("height"))

		# Creates layouts for all of the Buttons (so that they are in the correct position) and creates the Buttons themselves
		blockGenerateButton = Button(text="Auto-Generate Pattern")
		blockGenerateButton.bind(on_release=self.block_generate_Button)
		topLayout.add_widget(blockGenerateButton)

		createNewPatternButton = Button(text="Create New Pattern")
		createNewPatternButton.bind(on_release=self.create_new_Pattern_Button)

		middleWidgetLayout = GridLayout(cols=1, size_hint_y=None)
		middleWidgetLayout.bind(minimum_height=middleWidgetLayout.setter("height"))
		middleWidgetLayout.add_widget(Label(text="Patterns:"))
		middleWidgetLayout.add_widget(createNewPatternButton)

		# Adds the Buttons to the grid
		topLayout.add_widget(middleWidgetLayout)
		returnButton = Button(text="Go back")
		returnButton.bind(on_release=self.return_Button)
		topLayout.add_widget(returnButton)

		# Empty grid that will be used to show all of the Patterns and information relating to them
		self.patternGrid = GridLayout(cols=3, size_hint_y=None, padding="15dp", spacing="15dp")
		self.patternGrid.bind(minimum_height=self.patternGrid.setter("height"))

		# Adds all the widgets to their correct parents
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.patternGrid)

		view.add_widget(mainLayout)

		self.add_widget(view)
	
	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Gets all the data for each Pattern
		patternData = backEnd.get_Patterns()

		# Creates title widget for the Pattern grid
		nameLayout = GridLayout(cols=1, size_hint_y=None)
		nameLayout.bind(minimum_height=nameLayout.setter("height"))
		nameLayout.add_widget(Label())
		nameLayout.add_widget(Label(text="Name"))
		nameLayout.add_widget(Label())

		# Resets the grid for the Patterns
		self.patternGrid.clear_widgets()
		self.patternGrid.add_widget(Label())
		self.patternGrid.add_widget(nameLayout)
		self.patternGrid.add_widget(Label())

		# Loops through each Pattern in the data, and creates a row for that Pattern
		for pattern in patternData:
			id, name = pattern

			# Creates Button used to edit/delete specific Populations
			deleteButton = Button(text="Delete")
			deleteButton.bind(on_release=partial(self.delete_Pattern_Button, patternID=id))
			editButton = Button(text="Edit/View")
			editButton.bind(on_release=partial(self.edit_Pattern_Button, patternID=id))

			# Displays the Population Name in the correct format
			nameLayout = GridLayout(cols=1, size_hint_y=None)
			nameLayout.bind(minimum_height=nameLayout.setter("height"))
			nameLayout.add_widget(Label())
			nameLayout.add_widget(Label(text=name))
			nameLayout.add_widget(Label())

			# Adds widgets to the Pattern grid
			self.patternGrid.add_widget(deleteButton)
			self.patternGrid.add_widget(nameLayout)
			self.patternGrid.add_widget(editButton)

class ChooseNewSubjectForBlock(GridLayout):
	# Class that creates a popup that asks the user what Subject they would like to assign to a Block in the Pattern they are currently viewing

	# Called if the user clicks one of the Subject Buttons in the popup, updating the correct Block with the correct Subject
	def subject_Button(self, instance, blockID, viewPatternClass):
		if instance.text != "NONE":
			viewPatternClass.update_Block(blockID, instance.text)
		else:
			viewPatternClass.delete_Block(blockID)
		self.parent.parent.parent.dismiss()
		
	# Creates the GUI screen for the popup
	def __init__(self, viewPatternClass, blockID, subjects, **kwargs):
		super().__init__(**kwargs)

		self.cols = 3

		# Loops through each subject and creates a new Button on the screen
		for subject in subjects:
			subjectButton = Button(text=subject)
			subjectButton.bind(on_release=partial(self.subject_Button, blockID=blockID, viewPatternClass=viewPatternClass))
			self.add_widget(subjectButton)

class GetNewPatternName(GridLayout):
	# Class that creates a popup to get the PatternName for a new Pattern that the user created

	# Creates the GUI screen
	def __init__(self, viewPatternClass, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1
		self.viewPatternClass = viewPatternClass

		# Adds all of the widgets to the screen
		self.add_widget(Label(text="Pattern Name"))

		self.patternName = TextInput()

		self.add_widget(self.patternName)

		saveChangesButton = Button(text="Save changes")
		saveChangesButton.bind(on_release=self.save_changes_Button)
		self.add_widget(saveChangesButton)

	# Called when the user wants to submit the name for the new Pattern
	def save_changes_Button(self, instance):

		# Validates user input
		validText = True
		errorMsg = ""

		# Validates the PatternName field
		if self.patternName.text == "":
			validText = False
			errorMsg = "\n".join([errorMsg, "The Pattern name needs to be in the correct format. Currently, this field is empty."])
		if len(self.patternName.text) > 30:
			validText = False
			errorMsg = "\n".join([errorMsg, "The Pattern name should have length less than or equal to 30."])

		# If any of the data is invalid, shows new popup, telling user every error in their inputs 
		if not validText:
			self.newPopulationName.text = ""
			popup = Popup(title="ERROR", content=ErrorInUserValues(errorMsg), size_hint=(None, None), size=(750, 750))
			popup.open()

		# Otherwise, the new data is sent to backend and the current screen is updated
		else:
			patternID = backEnd.create_blank_Pattern(self.patternName.text)
			self.viewPatternClass.patternID = patternID
			self.viewPatternClass.patternLabel.text = self.patternName.text
			self.viewPatternClass.newPattern = False
			self.parent.parent.parent.dismiss()

class PatternTestResult(GridLayout):
	# Class that creates a popup to show the results when the current Pattern has been tested against the Population

	# Called when the user wants to close the popup
	def close_Button(self, instance):
		self.parent.parent.parent.dismiss()

	# Creates the GUI screen
	def __init__(self, results, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.add_widget(Label(text="Results:"))

		# Formats the results into different fields on the screen22
		resultsLayout = GridLayout(cols=2)
		resultsLayout.add_widget(Label(text="Students Satisfied:"))
		resultsLayout.add_widget(Label(text=f"{results[0]}/{results[1]}"))
		resultsLayout.add_widget(Label(text="Subject Combinations not satisfied:"))
		resultsLayout.add_widget(Label(text="\n".join([",".join(combination) for combination in results[2]])))

		# Creates the close Button
		closeButton = Button(text="Close")
		closeButton.bind(on_release=self.close_Button)

		# Adds widgets to the screen
		self.add_widget(resultsLayout)
		self.add_widget(closeButton)
		
class EditPattern(Screen):
	# Class that creates the Pattern Modification screen

	# Called if the user wants to test the current Pattern against the Population
	def test_Pattern_Button(self, instance):
		popup = Popup(title="Test Results", content=PatternTestResult(backEnd.test_Pattern_using_PatternID(self.patternID)), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Called if the user wants to delete a Block in the Pattern
	def delete_Block(self, blockID):
		backEnd.delete_Block(blockID, self.patternID)
		self.on_enter()

	# Called when the new Subject for a Block has been selected by the user
	def update_Block(self, blockID, subjectName):
		backEnd.update_Block(blockID, subjectName, self.patternID)
		self.on_enter()

	# Called if the user wants to add a new Block to the Pattern
	def block_add_Button(self, instance, index):
		blockID = backEnd.create_blank_Block(self.patternID, index)
		popup = Popup(title="Edit Block", content=ChooseNewSubjectForBlock(self, blockID, [subject.get_Subject_Name() for subject in backEnd.population.get_Subjects()] + ["NONE"]), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Called if the user wants to change the Subject assigned to a Block
	def block_edit_Button(self, instance, blockID):
		popup = Popup(title="Edit Block", content=ChooseNewSubjectForBlock(self, blockID, [subject.get_Subject_Name() for subject in backEnd.population.get_Subjects()] + ["NONE"]), size_hint=(None, None), size=(1000, 1000))
		popup.open()

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "ViewPatternList"
		app.windowManager.transition.direction = "right"

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Public variables that are changed by other Classes to let this Class know when the Pattern the user requested already exists, or is a new Pattern
		self.patternID = None

		self.newPattern = False

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1, size_hint_y=None, padding="15dp")
		mainLayout.bind(minimum_height=mainLayout.setter("height"))

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(cols=4, size_hint_y=None)
		topLayout.bind(minimum_height=topLayout.setter("height"))
		testPatternButton = Button(text="Test Pattern", size_hint_y=None)
		testPatternButton.bind(on_release=self.test_Pattern_Button)
		topLayout.add_widget(testPatternButton)
		topLayout.add_widget(Label(text="Pattern Name: ", size_hint_y=None))
		self.patternLabel = Label(text="", size_hint_y=None)
		topLayout.add_widget(self.patternLabel)
		returnButton = Button(text="Go back", size_hint_y=None)
		returnButton.bind(on_release=self.return_Button)
		topLayout.add_widget(returnButton)

		# Empty grid that will be used to show the Pattern selected by the user
		self.patternGridLayout = GridLayout(cols=1, size_hint_y=None, padding="20dp")
		self.patternGridLayout.bind(minimum_height=self.patternGridLayout.setter("height"))

		# Adds all the widgets to their correct parents
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.patternGridLayout)

		view.add_widget(mainLayout)

		self.add_widget(view)
	
	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Checks if this is a new Pattern, or if it already exists in the database
		if self.newPattern:

			# If it is new, then gets the PatternName from the user, then creates a blank template that the user can edit
			popup = Popup(title="Pattern Name", content=GetNewPatternName(self), size_hint=(None, None), size=(1000, 1000))
			popup.open()
		
		# Otherwise, the selected Pattern is fetched
		else:
			self.patternLabel.text, self.pattern = backEnd.get_Pattern(self.patternID)
		
		self.view_Pattern()

	# Function that renders the current Pattern selected onto the screen
	def view_Pattern(self):

		# Initialises the empty grid used to store the Pattern widgets
		patternGrid = GridLayout(cols=backEnd.population.get_Options()+1, size_hint_y=None, spacing="20dp")
		patternGrid.bind(minimum_height=patternGrid.setter("height"))
		patternGrid.add_widget(Label())
		for index in range(backEnd.population.get_Options()):
			patternGrid.add_widget(Label(text=str(index+1)))

		# Loop that continually adds rows to the Pattern grid until no more Blocks have been added. At this point, all the Blocks have been added to the screen.
			
		# Initialises variables responsible for repeating the loop
		blocksAdded = -1
		index = -1
		while blocksAdded != 0:
			index += 1
			blocksAdded = 0
			patternGrid.add_widget(Label(text=str(index+1)))

			# Loops through each of the columns in the Pattern
			for i in range(backEnd.population.get_Options()):
				
				# Tries to get the Block which is at the pattern[index] position of the column.
				try:
					blockEditButton = Button(text=self.pattern[i][index][0], size_hint_y=None)
					blockEditButton.bind(on_release=partial(self.block_edit_Button, blockID=self.pattern[i][index][1]))
					patternGrid.add_widget(blockEditButton)
					blocksAdded += 1
				
				# If this doesn't exist, then creates a blank Block and adds that to the screen instead
				except BaseException:
					blockAddButton = Button(text="[Add new Block]", size_hint_y=None)
					blockAddButton.bind(on_release=partial(self.block_add_Button, index=i))
					patternGrid.add_widget(blockAddButton)
		
		# Resets the widgets on the screen and adds the new Pattern grid to the screen
		self.patternGridLayout.clear_widgets()
		self.patternGridLayout.add_widget(patternGrid)

class GeneratedPatternTestResult(PatternTestResult):
	# Class that creates the popup to show the result when a Pattern generated by the program is tested against the Population

	# Inherits from the "PatternTestResult" class, since most of the functionality for these popups is the same

	# Called when the user wants to close the popup
	def close_Button(self, instance):
		self.parent.parent.parent.dismiss()

class GenerationScreen(Screen):
	# Class that shows the Pattern generated by the program

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "BlockPatternGeneration"
		app.windowManager.transition.direction = "right"
	
	# Called if the user wants to save the generated Pattern to the database
	def save_Pattern_Button(self, instance):

		# Creates a new Pattern with the same details as the generated Pattern, saving it to the database
		patternName = backEnd.create_Pattern_Name()
		patternID = backEnd.create_blank_Pattern(patternName)
		for column in range(len(self.bestPattern)):
			for subjectID in self.bestPattern[column]:
				blockID = backEnd.create_blank_Block(patternID, column)
				backEnd.update_Block_using_SubjectID(blockID, subjectID, patternID)
		
		# Changes the screen to the previous screen
		app.windowManager.current = "ViewPatternList"
		app.windowManager.transition.direction = "right"

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		self.blocks = []

		# Creates a scroll widget that will allow the user to scroll down the menu if there are too many Subjects to fit onto the screen
		view = ScrollView()

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1, size_hint_y=None, padding="15dp")
		mainLayout.bind(minimum_height=mainLayout.setter("height"))

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(cols=3, size_hint_y=None)
		topLayout.bind(minimum_height=topLayout.setter("height"))
		savePatternButton = Button(text="Save Pattern")
		savePatternButton.bind(on_release=self.save_Pattern_Button)
		topLayout.add_widget(savePatternButton)
		topLayout.add_widget(Label(text="Generated Pattern:", size_hint_y=None))
		returnButton = Button(text="Go back", size_hint_y=None)
		returnButton.bind(on_release=self.return_Button)
		topLayout.add_widget(returnButton)

		# Creates the empty grid to display the generated Pattern
		self.patternGridLayout = GridLayout(cols=1, size_hint_y=None, padding="20dp")
		self.patternGridLayout.bind(minimum_height=self.patternGridLayout.setter("height"))

		# Adds all the widgets to their correct parents
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.patternGridLayout)

		view.add_widget(mainLayout)

		self.add_widget(view)
	
	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Gets the best Pattern and creates a new Pattern in a easier-to-use format for the display code
		self.displayPattern = []
		self.bestPattern = backEnd.generate_Patterns(self.blocks)
		for column in self.bestPattern:
			self.displayPattern.append([])
			for subjectID in column:
				subjectName = backEnd.dbController.get_Subject_Name_From_SubjectID(subjectID)
				self.displayPattern[-1].append(subjectName)
		
		# Creates the empty table to display the Pattern
		patternGrid = GridLayout(cols=backEnd.population.get_Options()+1, size_hint_y=None)
		patternGrid.bind(minimum_height=patternGrid.setter("height"))
		
		patternGrid.add_widget(Label())

		for i in range(backEnd.population.get_Options()):
			patternGrid.add_widget(Label(text=str(i+1), size_hint_y=None))

		# Loop that continually adds rows to the Pattern grid until no more Blocks have been added. At this point, all the Blocks have been added to the screen.
			
		# Initialises variables responsible for repeating the loop
		blocksAdded = -1
		index = -1
		while blocksAdded != 0:
			index += 1
			blocksAdded = 0
			patternGrid.add_widget(Label(text=str(index+1)))

			# Loops through each of the columns in the Pattern
			for i in range(backEnd.population.get_Options()):

				# Tries to get the Block which is at the pattern[index] position of the column.
				try:
					patternGrid.add_widget(Label(text=self.displayPattern[i][index], size_hint_y=None))
					blocksAdded += 1

				# If this doesn't exist, then creates a blank Block and adds that to the screen instead
				except BaseException:
					patternGrid.add_widget(Label(size_hint_y=None))
		
		# Resets the widgets on the screen and adds the new Pattern grid to the screen
		self.patternGridLayout.clear_widgets()
		self.patternGridLayout.add_widget(patternGrid)
		
		# Creates a popup to show how successful the Pattern generated is
		popup = Popup(title="Test Results", content=GeneratedPatternTestResult(backEnd.test_Pattern(self.bestPattern)), size_hint=(None, None), size=(1000, 1000))
		popup.open()

class BlockPatternGeneration(Screen):
	# Class that creates the Block Pattern Generation screen

	# Called when the user wants the program to start generating Patterns
	def generation_Button(self, instance):
		app.generationScreen.blocks = self.blocks
		app.windowManager.current = "GenerationScreen"
		app.windowManager.transition.direction = "left"

	# Called if the user wants to return to the previous screen
	def return_Button(self, instance):
		app.windowManager.current = "ViewPatternList"
		app.windowManager.transition.direction = "right"

	# Creates the GUI screen
	def __init__(self, **kw):
		super().__init__(**kw)

		# Creates the main grid layout that will store all of the widgets
		mainLayout = GridLayout(cols=1)

		# Creates the grid layout that is responsible for creating the top half of the screen
		topLayout = GridLayout(cols=3)
		topLayout.add_widget(Label())
		topLayout.add_widget(Label(text="Block Pattern Generation"))
		returnButtonLayout = GridLayout(cols=1)
		returnButton = Button(text="Go back")
		returnButton.bind(on_release=self.return_Button)
		returnButtonLayout.add_widget(returnButton)
		returnButtonLayout.add_widget(Label())
		returnButtonLayout.add_widget(Label())
		topLayout.add_widget(returnButtonLayout)

		# Creates the empty middle grid that will store some details about the Pattern before it has been generated
		self.midLayout = GridLayout(cols=4)

		# Creates the bottom grid that stores the Button to start Pattern generation
		bottomLayout = GridLayout(cols=3)
		bottomLayout.add_widget(Label())
		generationButtonLayout = GridLayout(rows=3)
		generationButtonLayout.add_widget(Label())
		generationButton = Button(text="Start Generation")
		generationButton.bind(on_release=self.generation_Button)
		generationButtonLayout.add_widget(generationButton)
		generationButtonLayout.add_widget(Label())
		bottomLayout.add_widget(generationButtonLayout)
		bottomLayout.add_widget(Label())

		# Adds grids to the main grid
		mainLayout.add_widget(topLayout)
		mainLayout.add_widget(self.midLayout)
		mainLayout.add_widget(bottomLayout)

		# Adds the main grid to the screen
		self.add_widget(mainLayout)
	
	# Run whenever the user enters this screen
	def on_enter(self, *args):
		super().on_enter(*args)

		# Tries to create the list of Blocks that needs to be assigned to the Pattern
		try:
			self.blocks = backEnd.create_Blocks_from_SubjectConstraints(backEnd.create_Clash_Table())
		
		# If there is an error, then some of the Subjects haven't had constraints applied to them
		except BaseException:
			popup = Popup(title="Error", content=NewSubjectsAddedAlert(), size_hint=(None, None), size=(1000, 1000))
			popup.open()
			return

		# Gets the total number of Students to be fit in the Pattern
		totalStudents = len(backEnd.population.get_Students())
		
		# Shows the data on the screen
		self.midLayout.add_widget(Label())
		self.midLayout.add_widget(Label(text="Number of Blocks:"))
		self.midLayout.add_widget(Label(text=str(len(self.blocks))))
		self.midLayout.add_widget(Label())
		self.midLayout.add_widget(Label())
		self.midLayout.add_widget(Label(text="Number of Students:"))
		self.midLayout.add_widget(Label(text=str(totalStudents)))
		self.midLayout.add_widget(Label())

class BlockManagerApp(App):
	# Class used to manage the entire app and switching between different screens

	# Run when the app is opened
	def build(self):

		# Class that manages transitions between screens
		self.windowManager = ScreenManager()

		# All of the screens in the app are initialised with the correct names
		self.mainScreen = MainMenu(name="MainMenu")
		self.subjectScreen = SubjectData(name="SubjectData")
		self.populationScreen = StudentPopulations(name="StudentPopulations")
		self.loadExistingScreen = LoadExistingStudentPopulation(name="LoadExistingStudentPopulation")
		self.importPopulationScreen = ImportPopulationFromFile(name="ImportPopulationFromFile")
		self.manualEditPopulationScreen = ManualEditPopulation(name="ManualEditPopulation")
		self.clashtableScreen = ClashTable(name="ClashTable")
		self.viewPatternListScreen = ViewPatternList(name="ViewPatternList")
		self.viewPatternScreen = EditPattern(name="EditPattern")
		self.blockPatternGenerationScreen = BlockPatternGeneration(name="BlockPatternGeneration")
		self.generationScreen = GenerationScreen(name="GenerationScreen")

		# All of the screens are added to the ScreenManager instance
		self.windowManager.add_widget(self.mainScreen)
		self.windowManager.add_widget(self.subjectScreen)
		self.windowManager.add_widget(self.populationScreen)
		self.windowManager.add_widget(self.loadExistingScreen)
		self.windowManager.add_widget(self.importPopulationScreen)
		self.windowManager.add_widget(self.manualEditPopulationScreen)
		self.windowManager.add_widget(self.clashtableScreen)
		self.windowManager.add_widget(self.viewPatternListScreen)
		self.windowManager.add_widget(self.viewPatternScreen)
		self.windowManager.add_widget(self.blockPatternGenerationScreen)
		self.windowManager.add_widget(self.generationScreen)

		# The ScreenManager instance is returned, and the app is run
		return self.windowManager

# Runs only when this is the file being directly run
if __name__ == "__main__":
	
	# Initialises the backend
	dbPath = "StudentDB.db"
	backEnd = BackEnd(dbPath)

	# Initialises the app and runs it
	app = BlockManagerApp()
	app.run()
