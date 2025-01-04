from DatabaseController import DatabaseController as db

# Priority queue takes in a list with elements [priority, value] and creates a queue with the lower priority value at the start
class PriorityQueue():
	def __init__(self, queue=[], asc=True):
		self.__asc = asc
		self.__queue = queue
		self.__queue = db.merge_sort(self.__queue, self.__asc)
	
	# Adds an item to the end of the queue
	def enqueue(self, item):
		self.__queue.append(item)
		self.__queue = db.merge_sort(self.__queue, self.__asc)
	
	# Returns the value stored at the front of the queue
	def peek(self):
		return self.__queue[0]
	
	# Removes and returns the value stored at the front of the queue
	def dequeue(self):
		return self.__queue.pop(0)
	
	# Returns whether or not the queue is empty
	def is_empty(self):
		try:
			self.peek()
			return False
		except BaseException:
			return True
		

		