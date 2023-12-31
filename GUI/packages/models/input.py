# file: input.py
# description: create the Data class which is used to store topside commands and subsea data

class Data:

	def __init__(self, val_names):
		self.val_dict = {}
		self.init(val_names)

		for entry in self.val_names:
			self.val_dict[entry] = 0


	def init(self, val_names):
		self.val_names = val_names

	def assign(self, val_name, value):
		for entry in self.val_names:
			if val_name == entry:
				self.val_dict[entry] = value
				return True
		return False

	def read(self, val_name):
		for entry in self.val_names:
			if val_name == entry:
				return self.val_dict[entry] 
		return 0

	def printclass(self):
		for entry in self.val_names:
			print(entry)
			print(self.val_dict[entry])
			print("------")

