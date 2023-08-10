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


# class subseaData:

# 	val_names = ["ID", "TMPR", "PRES", "HEAD"]

# 	def __init__(self):
# 		self.val_dict = {}

# 		for entry in self.val_names:
# 			self.val_dict[entry] = 0

# 	def assign(self, val_name, value):
# 		for entry in self.val_names:
# 			if val_name == entry:
# 				self.val_dict[entry] = value
# 				return True
# 		return False

# 	def read(self, val_name):
# 		for entry in self.val_names:
# 			if val_name == entry:
# 				return self.val_dict[entry] 
# 		return 0

# 	def printclass(self):
# 		for entry in self.val_names:
# 			print(entry)
# 			print(self.val_dict[entry])
# 			print("------")


# class inputData:

# 	#change this class so that you can access each instruction by name

# 	val_names = ["JOYX", "JOYY", "VERT_DN", "VERT_UP", "ROT_CCW", "ROT_CW", "S_TOG", "L_TOG", "CAM_UP", "CAM_DN"]

# 	val_dict = {
# 		"JOYX" 	 : None,	
# 		"JOYY" 	 : None,	
# 		"VERT_DN"  : None,       
# 		"VERT_UP"  : None,       
# 		"ROT_CCW"  : None,       
# 		"ROT_CW"   : None,
# 		"S_TOG"    : None,    
# 		"L_TOG"    : None,               
# 		"CAM_UP"   : None,
# 		"CAM_DN"   : None
# 	}


# 	def __init__(self, joyX = 0, joyY = 0, rotate = 0, depth = 0, light_toggle = None, sample_toggle = None, cam_tilt = None):
		
# 		self.joyX = joyX
# 		self.joyY = joyY
# 		self.rotate = rotate
# 		self.depth = depth 
# 		self.light_toggle = light_toggle 
# 		self.sample_toggle = sample_toggle 
# 		self.cam_tilt = cam_tilt 

