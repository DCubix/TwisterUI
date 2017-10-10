"""
File: widgets/button.py
Description: The good ol' Button
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from .label import *
from tui.core.events import *

class Button(Label):
	"""
	Button
	Attributes:
		click_listeners: Click event listeners. Append them to this list.
	"""
	def __init__(self, text=""):
		super().__init__(text=text)
		self.click_listeners = []
		self.text_align = (ALIGN_CENTER | ALIGN_MIDDLE)

		self.clicked = False
		self.hovered = False
		self.auto_size = False

	def render(self, renderer):
		if self.style is None:
			return
		n = None
		if self.enabled:
			if not self.hovered and not self.clicked:
				n = self.style.textures["Button_normal"]
			elif self.hovered and not self.clicked:
				n = self.style.textures["Button_hover"]
			elif self.hovered and self.clicked:
				n = self.style.textures["Button_click"]
		else:
			n = self.style.textures["Button_disabled"]
		if n is not None:
			bp = self.get_corrected_bounds_no_intersect().packed()
			renderer.nine_patch_object(n, *bp)
		super().render(renderer)
	
	def handle_events(self, event):
		if event.get_type() == EVENT_TYPE_MOUSE_BUTTON:
			if self.get_corrected_bounds().has_point(event.x, event.y) and self.enabled:
				if event.status:
					self.clicked = True
				else:
					if self.clicked:
						self.clicked = False
						for listener in self.click_listeners:
							listener(self, event)
			else:
				self.clicked = False
				self.hovered = False
		elif event.get_type() == EVENT_TYPE_MOUSE_MOTION:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				self.hovered = True
			else:
				self.clicked = False
				self.hovered = False
		return super().handle_events(event)