from bge import types, logic, events, render
from OpenGL import GL
from .output import Output
from .texture import Texture

from bgl import *

class ObjectTexture(Output):
	def __init__(self, obj, width, height):
		super().__init__()
		self.object = obj
		self.width = width
		self.height = height
		self.background = (0.0, 0.0, 0.0, 0.0)

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
		z = 1000.0
		projectedPos = camPos - svec * z
		
		ob, _, _, _, uv = cam.rayCast(projectedPos, None, 0, "", True, False, 2)
		if ob == self.object:
			mx = uv.x * self.width
			my = uv.y * self.height
			self.__lx = mx
			self.__ly = my
			return (int(mx), self.height - int(my))
		return (self.__lx, self.__ly)

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
