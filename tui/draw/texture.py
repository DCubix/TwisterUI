from OpenGL import GL
from bge import texture as vtex
import numpy

from bgl import *

class Texture:
	def __init__(self, width, height, data=None, interp=GL_LINEAR):
		self.__bindCode = Buffer(GL_INT, 1)
		glGenTextures(1, self.__bindCode)
		self.bindCode = self.__bindCode[0]

		self.valid = True
		self.width = width
		self.height = height

		glBindTexture(GL_TEXTURE_2D, self.bindCode)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, interp)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, interp)
		GL.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
		glBindTexture(GL_TEXTURE_2D, 0)

	def bind(self, slot=0):
		glActiveTexture(GL_TEXTURE0 + slot)
		glBindTexture(GL_TEXTURE_2D, self.bindCode)
	
	def unbind(self):
		glBindTexture(GL_TEXTURE_2D, 0)

	def __del__(self):
		glDeleteTextures(1, self.__bindCode)

class ImageTexture(Texture):
	def __init__(self, fileName, interp=GL_LINEAR):
		img = vtex.ImageFFmpeg(fileName)
		img.scale = False
		img.flip = False
		data = img.image
		w, h = img.size

		super().__init__(w, h, numpy.array(data, dtype=numpy.uint8), interp)

		if not data:
			self.valid = False
			self.__del__()
			return

		img = None