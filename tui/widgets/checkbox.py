"""
File: widgets/checkbox.py
Description: True or False
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from .label import *
from tui.core import EVENT_STATUS_CONSUMED, EVENT_STATUS_AVAILABLE, EVENT_TYPE_MOUSE_BUTTON
from tui.draw import Rect

class CheckBox(Label):
	"""
	Check box.
	Attributes:
		change_listeners: Change event listener list.
		checked: Check status.
	"""
	def __init__(self, text=""):
		super().__init__(text=text, text_align=(ALIGN_LEFT | ALIGN_MIDDLE))

		self.change_listeners = []
		self.__checked = False
		self.clicked = False
		self.auto_size = True

	@property
	def checked(self):
		return self.__checked

	@checked.setter
	def checked(self, c):
		if c != self.__checked:
			prev = self.__checked
			self.__checked = c
			for cl in self.change_listeners:
				cl(self, prev)

	def render(self, renderer):
		pl = self.padding[0] * self.tui.x_scaling
		pr = self.padding[1] * self.tui.x_scaling
		pb = self.padding[2] * self.tui.y_scaling
		pt = self.padding[3] * self.tui.y_scaling
		if self.style is not None:
			cb = None
			cm = None
			if self.enabled:
				cb = self.style.textures["CheckBox_normal"]
				if self.checked:
					cm = self.style.textures["CheckBox_Mark_normal"]
			else:
				cb = self.style.textures["CheckBox_disabled"]
				if self.checked:
					cm = self.style.textures["CheckBox_Mark_disabled"]
			if cb:
				fid = self.style.font.id if self.font is None else self.font.id
				w, h = renderer.text_size(
					fid,
					self.text,
					self.font_size
				)
				sz = max(w, h)
				isz = max(cb.width, cb.height)
				ratio = sz / isz
				iw = min(cb.width * ratio, cb.width)
				ih = min(cb.height * ratio, cb.height)
				
				self.pref_size = (w + iw, h)

				nbounds = self.get_corrected_bounds_no_intersect()
				bounds = self.get_corrected_bounds_no_intersect()
				bounds.x += iw
				bounds.w -= iw * 2
				iy = bounds.h / 2 - ih / 2

				cbounds = Rect(nbounds.x + 1, nbounds.y + iy, iw, ih)
				renderer.nine_patch_object(cb, *cbounds.packed())
				if self.checked:
					renderer.nine_patch_object(cm, *cbounds.packed())

				x = bounds.x
				y = bounds.y

				if (self.text_align & ALIGN_CENTER) == ALIGN_CENTER:
					x += bounds.w / 2 - w / 2
				elif (self.text_align & ALIGN_RIGHT) == ALIGN_RIGHT:
					x += (bounds.w - w) - pr
				elif (self.text_align & ALIGN_LEFT) == ALIGN_LEFT:
					x += pl

				if (self.text_align & ALIGN_MIDDLE) == ALIGN_MIDDLE:
					y += (bounds.h / 2 - h / 2)
				elif (self.text_align & ALIGN_BOTTOM) == ALIGN_BOTTOM:
					y += (bounds.h - h) - pb
				elif (self.text_align & ALIGN_TOP) == ALIGN_TOP:
					y += pt

				color = self.style.text_color if self.enabled else self.style.disabled_text_color
				renderer.end()
				
				renderer.text(
					fid,
					self.text,
					x, y,
					color,
					self.font_size
				)
				renderer.begin()

	def handle_events(self, event):
		if event.get_type() == EVENT_TYPE_MOUSE_BUTTON:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				if event.status:
					self.clicked = True
				else:
					if self.clicked:
						self.clicked = False
						self.checked = not self.checked
		return super().handle_events(event)