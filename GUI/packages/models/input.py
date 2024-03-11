# file: input.py
# description: create the Data class which is used to store topside commands and subsea data

class Data:

	def __init__(self, val_names):
		self.val_dict = {}
		self.val_names = val_names

		for entry in self.val_names:
			self.val_dict[entry] = None

	def assign(self, val_name, value):
		if val_name in self.val_names:
			self.val_dict[val_name] = value
			return True
		else:
			return False

		#old way:
		# for entry in self.val_names:
		# 	if val_name == entry:
		# 		self.val_dict[entry] = value
		# 		return True
		# return False

	def read(self, val_name):
		if val_name in self.val_names:
			return self.val_dict[val_name]
		else:
			print("UNABLE TO FIND VALUE FOR " + str(val_name))
			return 0
		
		#old way
		# for entry in self.val_names:
		# 	if val_name == entry:
		# 		return self.val_dict[entry] 
		# return 0

	def printclass(self):
		for entry in self.val_names:
			print(entry)
			print(self.val_dict[entry])
			print("------")

