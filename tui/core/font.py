import blf

class Font:
	def __init__(self, fileName=None):
		self.id = blf.load(fileName) if fileName is not None else 0
		self.size = 18.0