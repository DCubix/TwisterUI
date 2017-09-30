from OpenGL import GL
from bgl import *

class Uniform:
	def __init__(self):
		self.location = -1
	
	def set_value(self, val):
		if isinstance(val, list) or isinstance(val, tuple):
			c = len(val)
			if   c == 1: glUniform1f(self.location, val[0])
			elif c == 2: glUniform2f(self.location, val[0], val[1])
			elif c == 3: glUniform3f(self.location, val[0], val[1], val[2])
			elif c == 4: glUniform4f(self.location, val[0], val[1], val[2], val[3])
			elif c == 9: glUniformMatrix3fv(self.location, 1, False, val)
			elif c == 16: glUniformMatrix4fv(self.location, 1, False, val)
		else:
			glUniform1f(self.location, val)
	
	def set_sampler(self, val):
		glUniform1i(self.location, val)

class ShaderProgram:
	def __init__(self):
		self.bindCode = glCreateProgram()
		self.__shaders = []
		self.valid = False

		self.__uniform = Uniform()
		self.__uniforms = {}
		self.__attributes = {}
	
	def add(self, src, stype):
		sh = glCreateShader(stype)
		glShaderSource(sh, src)
		glCompileShader(sh)

		if GL.glGetShaderiv(sh, GL_COMPILE_STATUS) != GL_TRUE:
			glDeleteShader(sh)
			print(GL.glGetShaderInfoLog(sh))
			self.valid = False
			return

		self.valid = True
		glAttachShader(self.bindCode, sh)
		self.__shaders.append(sh)

	def link(self):
		if not self.valid:
			return
		
		glLinkProgram(self.bindCode)

		if GL.glGetProgramiv(self.bindCode, GL_LINK_STATUS) != GL_TRUE:
			print(GL.glGetProgramInfoLog(self.bindCode))
			self.valid = False
		
		for sh in self.__shaders:
			glDeleteShader(sh)
		self.__shaders = []

	def bind(self):
		glUseProgram(self.bindCode)
	
	def unbind(self):
		glUseProgram(0)

	def get_uniform(self, uname):
		loc = self.get_uniform_location(uname)
		if loc != -1:
			self.__uniform.location = loc
			return self.__uniform
		print("Uniform not found. {}".format(uname))
		return None

	def get_uniform_location(self, uname):
		if uname not in self.__uniforms:
			loc = glGetUniformLocation(self.bindCode, uname)
			if loc != -1:
				self.__uniforms[uname] = loc
			else:
				return -1
		return self.__uniforms[uname]

	def get_attribute_location(self, aname):
		if aname not in self.__attributes:
			loc = glGetAttribLocation(self.bindCode, aname)
			if loc != -1:
				self.__attributes[aname] = loc
			else:
				return -1
		return self.__attributes[aname]

	def __del__(self):
		glDeleteProgram(self.bindCode)