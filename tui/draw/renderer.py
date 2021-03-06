"""
File: draw/renderer.py
Description: Rendering system
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from OpenGL import GL
import numpy
import blf
import math
import colorsys

from ctypes import c_void_p

from .shader import ShaderProgram
from .texture import Texture
from .output import Viewport
from tui.core.font import Font

from bge import render
from bgl import *

class NinePatch:
	"""
	9-Slice texture.
	Best alternative for high quality GUI.
	"""
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
	"""
	Advanced 2D Renderer.
	"""
	def __init__(self, tui):
		self.tui = tui
		self.output = tui.output

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
		inds = Buffer(GL_INT, 6, [0, 1, 2, 2, 3, 0])

		glBindVertexArray(self.vao[0])
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
		glBufferData(GL_ARRAY_BUFFER, 8 * 4, verts, GL_STATIC_DRAW)

		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo[0])
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, 6 * 4, inds, GL_STATIC_DRAW)

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
		uniform float gray;
		void main() {
			vec4 scol = texture2D(tex0, vs_texCoord);
			if (gray > 0.0) {
				scol.rgb = dot(scol.rgb, vec3(0.299, 0.587, 0.114));
			}
			gl_FragColor = scol * color;
		}
		"""

		self.shader = ShaderProgram()
		self.shader.add(VS, GL_VERTEX_SHADER)
		self.shader.add(FS, GL_FRAGMENT_SHADER)
		self.shader.link()

		self.__dtex = Texture(1, 1, numpy.array([255, 255, 255, 255], dtype=numpy.uint8))

	def begin(self):
		glEnable(GL_POLYGON_SMOOTH)
		glEnable(GL_LINE_SMOOTH)
		glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		glDisable(GL_CULL_FACE)
		glDisable(GL_LIGHTING)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.output.width, self.output.height, 0, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self.shader.bind()
		self.shader.get_uniform("tex0").set_sampler(0)
		glBindVertexArray(self.vao[0])

	def nine_patch_object(self, nine_patch, bx, by, bw, bh, color=(1, 1, 1, 1), gray=False):
		self.nine_patch(
			nine_patch.texture,
			bx, by, bw, bh,
			nine_patch.margin_left,
			nine_patch.margin_right,
			nine_patch.margin_bottom,
			nine_patch.margin_top,
			nine_patch.uv,
			color, gray
		)

	def nine_patch(self, tex, bx, by, bw, bh,
					lp=0, rp=0, bp=0, tp=0,
					uv=(0, 0, 1, 1),
					color=(1, 1, 1, 1),
					gray=False):
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
				color, gray
			)
		
		## Middle Left
		if lp > 0:
			self.draw(tex,
				bx, by + tp, lp, bh - (tp+bp),
				(uv[0], uv[1] + tuv, luv, uv[3] - (tuv+buv)),
				color, gray
			)
		
		## Bottom Left
		if lp > 0 and bp > 0:
			self.draw(tex,
				bx, by + (bh - bp), lp, bp,
				(uv[0], uv[1] + (uv[3] - buv), luv, buv),
				color, gray
			)
		
		## Top Center
		if tp > 0:
			self.draw(tex,
				bx + lp, by, bw - (lp+rp), tp,
				(uv[0] + luv, uv[1], uv[2] - (luv+ruv), tuv),
				color, gray
			)

		## Middle Center
		self.draw(tex,
			bx + lp, by + tp, bw - (lp+rp), bh - (tp+bp),
			(uv[0] + luv, uv[1] + tuv, uv[2] - (luv+ruv), uv[3] - (tuv+buv)),
			color, gray
		)
		
		## Bottom Center
		if bp > 0:
			self.draw(tex,
				bx + lp, by + (bh - bp), bw - (lp+rp), bp,
				(uv[0] + luv, uv[1] + (uv[3] - buv), uv[2] - (luv+ruv), buv),
				color, gray
			)
		
		## Top Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by, rp, tp,
				(uv[0] + (uv[2] - ruv), uv[1], ruv, tuv),
				color, gray
			)
		
		## Middle Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by + tp, rp, bh - (tp+bp),
				(uv[0] + (uv[2] - ruv), uv[1] + tuv, ruv, uv[3] - (tuv+buv)),
				color, gray
			)
		
		## Bottom Right
		if tp > 0 and rp > 0:
			self.draw(tex,
				bx + (bw - rp), by + (bh - bp), rp, bp,
				(uv[0] + (uv[2] - ruv), uv[1] + (uv[3] - buv), ruv, buv),
				color, gray
			)

	def color_wheel(self, x, y, radius, value=1.0, res=32, gray=False):
		self.end()
		px = 0
		py = 0
		steps = int(360 / res)
		fx = x
		fy = y

		glBegin(GL_TRIANGLE_FAN)
		glColor3f(*colorsys.hsv_to_rgb(0, 0, value))
		glVertex2f(fx + px, fy + py)
		for i in range(0, 360+steps, steps):
			rad = math.radians(i)
			px = math.cos(rad) * radius
			py = math.sin(rad) * radius
			col = [*colorsys.hsv_to_rgb(i / 360, 1.0, value)]
			if not gray:
				glColor3f(*col)
			else:
				g = (col[0] + col[1] + col[2]) / 3.0
				glColor3f(g, g, g)
			glVertex2f(fx + px, fy + py)
		glEnd()
		self.begin()

	def draw(self, tex, x, y, w, h, uv=(0, 0, 1, 1), color=(1, 1, 1, 1), gray=False):
		tex.bind(0)
		self.shader.get_uniform("clipRect").set_value(uv)
		self.shader.get_uniform("transform").set_value((x, y, w, h))
		self.shader.get_uniform("color").set_value(color)
		self.shader.get_uniform("gray").set_value(1 if gray else 0)
		GL.glDrawElements(GL_TRIANGLE_STRIP, 6, GL_UNSIGNED_INT, None)
		tex.unbind()

	def rectangle(self, x, y, w, h, color=(1, 1, 1, 1), wire=False):
		self.__dtex.bind(0)
		self.shader.get_uniform("clipRect").set_value((0, 0, 1, 1))
		self.shader.get_uniform("transform").set_value((x, y, w, h))
		self.shader.get_uniform("color").set_value(color)
		self.shader.get_uniform("gray").set_value(0)
		if wire:
			GL.glDrawElements(GL_LINE_LOOP, 6, GL_UNSIGNED_INT, None)
		else:
			GL.glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
		self.__dtex.unbind()

	def end(self):
		self.shader.unbind()
		glBindVertexArray(0)

	def clip_start(self, sx, sy, sw, sh):
		try:
			vp = GL.glGetIntegerv(GL_VIEWPORT)
		except:
			vp = [0, 0, render.getWindowWidth(), render.getWindowHeight()]
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

	def begin_text(self):
		glPushMatrix()
	
	def end_text(self):
		glPopMatrix()

	def text(self, fid, text, x, y, color=(1.0, 1.0, 1.0), size=12.0):
		blf.position(fid, int(x), int(-y), 0)
		blf.size(fid, self.font_size(size), self.font_dpi(size))
		_, h = blf.dimensions(fid, text)

		glPushMatrix()
		
		glTranslatef(0, h, 0)
		glScalef(1, -1, 1)

		glColor3f(*color)
		blf.draw(fid, text)
		glPopMatrix()

		return h

	def text_size(self, fid, text, size):
		blf.size(fid, self.font_size(size), self.font_dpi(size))
		return blf.dimensions(fid, text)

	def font_size(self, size):
		os = self.output.width
		ns = self.tui.virtual_width
		return int(Font.get_best_size(size, os, ns))

	def font_dpi(self, dsize):
		return 72

	def __del__(self):
		glDeleteVertexArrays(1, self.vao)
		glDeleteBuffers(1, self.vbo)
		glDeleteBuffers(1, self.ibo)