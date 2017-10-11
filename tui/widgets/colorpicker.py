"""
File: widgets/colorpicker.py
Description: Many colors
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

import colorsys
import math
from tui.core import Widget
from tui.core.events import *
from bge import events as BGE_Events

class ColorPicker(Widget):
	"""
	Color picker.
	Attributes:
		hue: Color Hue.
		saturation: Color Saturation.
		value: Color value/lightness/brightness.
	"""
	def __init__(self, color=(1.0, 1.0, 1.0)):
		super().__init__()
		self.padding = 6

		self.bounds.set_value(0, 0, 70, 70)

		self.clicked = False
		
		self.__hue = 0 # 0 to 1
		self.__saturation = 1
		self.__value = 1

		self.color_listeners = []

		hsv = colorsys.rgb_to_hsv(*color)
		self.hue = hsv[0]
		self.saturation = hsv[1]
		self.value = hsv[2]

	@property
	def color(self):
		return colorsys.hsv_to_rgb(self.__hue, self.__saturation, self.__value)

	@color.setter
	def color(self, v):
		hsv = colorsys.rgb_to_hsv(*v)
		self.__hue = hsv[0] # 0 to 1
		self.__saturation = hsv[1]
		self.__value = hsv[2]

	@property
	def hue(self):
		return self.__hue

	@hue.setter
	def hue(self, v):
		if v != self.__hue:
			prev = self.__hue
			self.__hue = v
			for cl in self.color_listeners:
				cl(self, [prev, self.__saturation, self.__value])

	@property
	def saturation(self):
		return self.__saturation

	@saturation.setter
	def saturation(self, v):
		if v != self.__saturation:
			prev = self.__saturation
			self.__saturation = v
			for cl in self.color_listeners:
				cl(self, [self.__hue, prev, self.__value])

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, v):
		if v != self.__value:
			prev = self.__value
			self.__value = v
			for cl in self.color_listeners:
				cl(self, [self.__hue, self.__saturation, prev])

	def render(self, renderer):
		b = self.get_corrected_bounds_no_intersect()
		if self.style is not None:
			renderer.nine_patch_object(self.style.textures["Panel"], *b.packed())

		sz = min(b.w, b.h) - self.padding * 2
		hsz = sz/2
		x = b.x + b.w/2
		y = b.y + b.h/2
		renderer.color_wheel(x, y, hsz, gray=(not self.enabled), value=self.__value)

		cur = self.style.textures["Dot"]
		cw = cur.width / self.tui.virtual_aspect
		ch = cur.height / self.tui.virtual_aspect
		h = self.__hue * (math.pi * 2.0)
		v = min(1.0, max(self.__saturation, 0.0))
		hszv = hsz * v
		cx = x + (math.cos(h) * hszv)
		cy = y + (math.sin(h) * hszv)
		renderer.nine_patch_object(cur, cx - cw/2, cy - ch/2, cw, ch, gray=(not self.enabled))
		super().render(renderer)

	def __update_hue(self, x, y):
		b = self.get_corrected_bounds_no_intersect()
		sz = min(b.w, b.h) - self.padding * 2
		hsz = sz/2
		cx = b.x + b.w/2
		cy = b.y + b.h/2
		dx = x - cx
		dy = y - cy
		dist = math.sqrt(dx * dx + dy * dy)
		angle_deg = math.degrees(math.atan2(dy, dx))
		angle = (angle_deg + 360) % 360
		self.saturation = min(1.0, max(dist / hsz, 0.0))
		self.hue = angle / 360

	def handle_events(self, event):
		if event.get_type() == EVENT_TYPE_MOUSE_BUTTON:
			if self.get_corrected_bounds().has_point(event.x, event.y) and event.button == BGE_Events.LEFTMOUSE:
				self.clicked = True
				self.__update_hue(event.x, event.y)
			else:
				self.clicked = False
			if not event.status or event.button != BGE_Events.LEFTMOUSE:
				self.clicked = False
		elif event.get_type() == EVENT_TYPE_MOUSE_MOTION:
			if self.clicked and self.get_corrected_bounds().has_point(event.x, event.y):
				self.__update_hue(event.x, event.y)
			else:
				self.clicked = False
		return super().handle_events(event)