"""
File: draw/output.py
Description: Render output manager and input handling
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from bge import types, logic, events, render
from OpenGL import GL
from .texture import Texture

from bgl import *

class Output:
	"""
	Output target for GUI rendering.
	Attributes:
		width: Output width.
		height: Output height.
	"""
	def __init__(self):
		self.width = 1
		self.height = 1

	def get_mouse_position(self):
		"""Gets the mouse position on this output."""
		return (0, 0)

	def bind(self):
		"""Binds this output for rendering."""
		pass
	
	def unbind(self):
		pass

class Viewport(Output):
	"""
	Viewport output.
	Outputs the rendering to the viewport.
	"""
	def __init__(self, width, height):
		super().__init__()
		self.width = width
		self.height = height

	def get_mouse_position(self):
		mx = logic.mouse.inputs[events.MOUSEX].values[-1]
		my = logic.mouse.inputs[events.MOUSEY].values[-1]
		return (mx, my, True)

class ObjectTexture(Output):
	"""
	Object output.
	Outputs the rendering to a textured object.
	Attributes:
		object: Target object.
		background: Clear color.
		ray_dist: Max. distance for clicking.
	"""
	def __init__(self, obj, width, height, ray_dist=20.0):
		super().__init__()
		self.object = obj
		self.width = width
		self.height = height
		self.background = (0.0, 0.0, 0.0, 0.0)
		self.ray_dist = ray_dist

		self.texture = Texture(width, height)

		self.bindCode = Buffer(GL_INT, 1)
		glGenFramebuffers(1, self.bindCode)
		glBindFramebuffer(GL_FRAMEBUFFER, self.bindCode[0])
		glFramebufferTexture2D(
			GL_FRAMEBUFFER,
			GL_COLOR_ATTACHMENT0,
			GL_TEXTURE_2D,
			self.texture.bindCode, 0
		)
		glBindFramebuffer(GL_FRAMEBUFFER, 0)

		VS = '''
		void main() {
			gl_Position = ftransform();
			gl_TexCoord[0] = gl_MultiTexCoord0;
		}
		'''

		FS = '''
		uniform sampler2D tex0;
		void main() {
			vec2 uv = gl_TexCoord[0].st;
			gl_FragColor = texture2D(tex0, uv);
		}
		'''

		mat = self.object.meshes[0].materials[0]
		shad = mat.getShader()
		if shad is not None:
			shad.setSource(VS, FS, True)

		self.__lx = 0
		self.__ly = 0

	def get_mouse_position(self):
		mx = logic.mouse.inputs[events.MOUSEX].values[-1] / render.getWindowWidth()
		my = logic.mouse.inputs[events.MOUSEY].values[-1] / render.getWindowHeight()
		cam = self.object.scene.active_camera
		svec = cam.getScreenVect(mx, my)
		camPos = cam.worldPosition
		z = self.ray_dist
		projectedPos = camPos - svec * z
		
		ob, _, _, _, uv = cam.rayCast(projectedPos, None, self.ray_dist, "", True, False, 2)
		if ob == self.object:
			mx = uv.x * self.width
			my = uv.y * self.height
			self.__lx = mx
			self.__ly = my
			return (int(mx), int(self.height - my), True)
		return (self.__lx, self.__ly, False)

	def bind(self):
		glBindFramebuffer(GL_FRAMEBUFFER, self.bindCode[0])
		glViewport(0, 0, self.width, self.height)
		glScissor(0, 0, self.width, self.height)
		glClearColor(*self.background)
		glClear(GL_COLOR_BUFFER_BIT)

	def unbind(self):
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		mat = self.object.meshes[0].materials[0]
		mat.textures[0].bindCode = self.texture.bindCode
		if mat.getShader() is not None:
			mat.getShader().setSampler("tex0", 0)


	def __del__(self):
		glDeleteFramebuffers(1, self.bindCode)
