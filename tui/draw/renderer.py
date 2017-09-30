from OpenGL import GL
import numpy
import blf
from ctypes import c_void_p

from .shader import ShaderProgram
from .texture import Texture
from .viewport import Viewport

from bge import render
from bgl import *

class NinePatch:
	def __init__(self, texture, lp=0, rp=0, bp=0, tp=0, uv=(0, 0, 1, 1)):
		self.texture = texture
		self.margin_left = lp
		self.margin_right = rp
		self.margin_bottom = bp
		self.margin_top = tp
		self.uv = uv
	
	@property
	def width(self):
		return self.texture.width * self.uv[2]

	@property
	def height(self):
		return self.texture.height * self.uv[3]

class Sprite:
	def __init__(self, x, y, width, height, uv, color, tex):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.uv = uv
		self.color = color
		self.tex = tex

	def vertices(self):
		return [
			self.x, self.y, self.uv[0], self.uv[1], *self.color,
			self.x + self.width, self.y, self.uv[0]+self.uv[2], self.uv[1], *self.color,
			self.x + self.width, self.y + self.height, self.uv[0]+self.uv[2], self.uv[1]+self.uv[3], *self.color,
			self.x, self.y + self.height, self.uv[0], self.uv[1]+self.uv[3], *self.color,
		]

class Batch:
	def __init__(self, tex, off, ilen):
		self.tex = tex
		self.off = off
		self.ilen = ilen

class Renderer:
	def __init__(self, output):
		self.output = output

		self.__sprites = []
		self.__batches = []
		self.__clip_stack = []

		self.vao = Buffer(GL_INT, 1)
		glGenVertexArrays(1, self.vao)

		self.vbo = Buffer(GL_INT, 1)
		glGenBuffers(1, self.vbo)

		self.ibo = Buffer(GL_INT, 1)
		glGenBuffers(1, self.ibo)

		self.vbo_len = 0
		self.ibo_len = 0

		verts = Buffer(GL_FLOAT, 8, [
				0.0, 0.0,
				1.0, 0.0,
				1.0, 1.0,
				0.0, 1.0
		])
		inds = Buffer(GL_INT, 4, [0, 1, 3, 2])

		glBindVertexArray(self.vao[0])
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
		glBufferData(GL_ARRAY_BUFFER, 8 * 4, verts, GL_STATIC_DRAW)

		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo[0])
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, 16, inds, GL_STATIC_DRAW)

		glEnableVertexAttribArray(0)
		GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 8, None)

		glBindVertexArray(0)

		VS = """
		attribute vec2 v_position;
		varying vec2 vs_texCoord;
		uniform vec4 clipRect;
		uniform vec4 transform;
		void main() {
			vec2 fpos = transform.xy + (v_position * transform.zw);
			gl_Position = gl_ModelViewProjectionMatrix * vec4(fpos, 0.0, 1.0);
			vs_texCoord = clipRect.xy + (v_position * clipRect.zw);
		}
		"""

		FS = """
		varying vec2 vs_texCoord;
		uniform vec4 color;
		uniform sampler2D tex0;
		void main() {
			gl_FragColor = texture2D(tex0, vs_texCoord) * color;
		}
		"""

		self.shader = ShaderProgram()
		self.shader.add(VS, GL_VERTEX_SHADER)
		self.shader.add(FS, GL_FRAGMENT_SHADER)
		self.shader.link()

	def begin(self):
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		glDisable(GL_CULL_FACE)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.output.width, self.output.height, 0, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self.shader.bind()
		self.shader.get_uniform("tex0").set_sampler(0)
		glBindVertexArray(self.vao[0])

	def nine_patch_object(self, nine_patch, bx, by, bw, bh, color=(1, 1, 1, 1)):
		self.nine_patch(
			nine_patch.texture,
			bx, by, bw, bh,
			nine_patch.margin_left,
			nine_patch.margin_right,
			nine_patch.margin_bottom,
			nine_patch.margin_top,
			nine_patch.uv,
			color
		)

	def nine_patch(self, tex, bx, by, bw, bh,
					lp=0, rp=0, bp=0, tp=0,
					uv=(0, 0, 1, 1),
					color=(1, 1, 1, 1)):
		bx = int(bx)
		by = int(by)
		bw = int(bw)
		bh = int(bh)
		iw = tex.width
		ih = tex.height

		luv = lp / iw
		ruv = rp / iw
		buv = bp / ih
		tuv = tp / ih

		## Top Left
		if lp > 0 and tp > 0:
			self.draw(tex,
				bx, by, lp, tp,
				(uv[0], uv[1], luv, tuv),
				color
			)
		
		## Middle Left
		if lp > 0:
			self.draw(tex,
				bx, by + tp, lp, bh - (tp+bp),
				(uv[0], uv[1] + tuv, luv, uv[3] - (tuv+buv)),
				color
			)
		
		## Bottom Left
		if lp > 0 and bp > 0:
			self.draw(tex,
				bx, by + (bh - bp), lp, bp,
				(uv[0], uv[1] + (uv[3] - buv), luv, buv),
				color
			)
		
		## Top Center
		if tp > 0:
			self.draw(tex,
				bx + lp, by, bw - (lp+rp), tp,
				(uv[0] + luv, uv[1], uv[2] - (luv+ruv), tuv),
				color
			)

		## Middle Center
		self.draw(tex,
			bx + lp, by + tp, bw - (lp+rp), bh - (tp+bp),
			(uv[0] + luv, uv[1] + tuv, uv[2] - (luv+ruv), uv[3] - (tuv+buv)),
			color
		)
		
		## Bottom Center
		if bp > 0:
			self.draw(tex,
				bx + lp, by + (bh - bp), bw - (lp+rp), bp,
				(uv[0] + luv, uv[1] + (uv[3] - buv), uv[2] - (luv+ruv), buv),
				color
			)
		
		## Top Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by, rp, tp,
				(uv[0] + (uv[2] - ruv), uv[1], ruv, tuv),
				color
			)
		
		## Middle Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by + tp, rp, bh - (tp+bp),
				(uv[0] + (uv[2] - ruv), uv[1] + tuv, ruv, uv[3] - (tuv+buv)),
				color
			)
		
		## Bottom Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by + (bh - bp), rp, bp,
				(uv[0] + (uv[2] - ruv), uv[1] + (uv[3] - buv), ruv, buv),
				color
			)

	def draw(self, tex, x, y, w, h, uv=(0, 0, 1, 1), color=(1, 1, 1, 1)):
		tex.bind(0)
		self.shader.get_uniform("clipRect").set_value(uv)
		self.shader.get_uniform("transform").set_value((x, y, w, h))
		self.shader.get_uniform("color").set_value(color)
		GL.glDrawElements(GL_TRIANGLE_STRIP, 4, GL_UNSIGNED_INT, None)
		tex.unbind()

	def end(self):
		self.shader.unbind()
		glBindVertexArray(0)

	def clip_start(self, sx, sy, sw, sh):
		vp = GL.glGetIntegerv(GL_VIEWPORT)
		if len(self.__clip_stack) > 0:
			px, py, pw, ph = self.__clip_stack[-1]
			minx = max(px, sx)
			maxx = min(px + pw, sx + sw)
			if maxx - minx < 1:
				return False
			
			miny = max(py, sy)
			maxy = min(py + ph, sy + sh)
			if maxy - miny < 1:
				return False

			sx = minx
			sy = miny
			sw = maxx - minx
			sh = max(1, maxy - miny)
		else:
			glEnable(GL_SCISSOR_TEST)
		sx = vp[0] + sx
		sy = vp[1] + (self.output.height - sy - sh)
		self.__clip_stack.append((sx, sy, sw, sh))
		glScissor(int(sx), int(sy), int(sw), int(sh))
		return True

	def clip_end(self):
		if len(self.__clip_stack) > 0:
			self.__clip_stack.pop()
		if len(self.__clip_stack) > 0:
			sx, sy, sw, sh = self.__clip_stack[-1]
			glScissor(int(sx), int(sy), int(sw), int(sh))
		else:
			glScissor(0, 0, self.output.width, self.output.height)
			glDisable(GL_SCISSOR_TEST)

	def text(self, fid, text, x, y, color=(1.0, 1.0, 1.0), aspect=1.0, rx=1.0, ry=1.0, size=12.0):
		_, h = blf.dimensions(fid, text)
		blf.position(fid, int(x), int(-y), 0)
		blf.size(fid, int(size * max(rx, ry)), 72)
		blf.aspect(fid, aspect)

		glPushMatrix()
		
		glTranslatef(0, h, 0)
		glScalef(1, -1, 1)

		glColor3f(*color)
		blf.draw(fid, text)
		glPopMatrix()

	def text_size(self, fid, text, aspect=1.0, rx=1.0, ry=1.0, size=12.0):
		blf.size(fid, int(size * max(rx, ry)), 72)
		blf.aspect(fid, aspect)
		return blf.dimensions(fid, text)

	def __del__(self):
		glDeleteVertexArrays(1, self.vao)
		glDeleteBuffers(1, self.vbo)
		glDeleteBuffers(1, self.ibo)