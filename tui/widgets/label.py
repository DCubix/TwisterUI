"""
File: widgets/label.py
Description: A string on the screen
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from tui.core import Widget

ALIGN_LEFT = 2
ALIGN_CENTER = 4
ALIGN_RIGHT = 8
ALIGN_TOP = 16
ALIGN_MIDDLE = 32
ALIGN_BOTTOM = 64

class Label(Widget):
	"""
	Label.
	Attributes:
		text: Text, any string.
		text_align: Text alignment. Bit flags.
			- ALIGN_LEFT (x)
			- ALIGN_CENTER (x)
			- ALIGN_RIGHT (x)
			- ALIGN_TOP (y)
			- ALIGN_MIDDLE (y)
			- ALIGN_BOTTOM (y)
		image: Icon image.
		image_align: Image alignment. One of the above (x) ones.
		font: Custom font.
		font_size: Custom font size.
		padding: Text padding. [left, right, bottom, top]
	"""
	def __init__(self, text="", text_align=(ALIGN_LEFT | ALIGN_MIDDLE), image_align=ALIGN_CENTER, image=None):
		super().__init__()
		self.text = text
		self.text_align = text_align
		self.image = image
		self.image_align = image_align
		self.font_size = 8.0
		self.font = None
		self.padding = [4, 4, 4, 4]

		self.bounds.set_value(0, 0, 190, 32)

		self.pref_size = (0, 0)
		self.auto_size = True

	def get_preferred_size(self):
		if self.style is None:
			return super().get_preferred_size()
		if self.auto_size:
			return self.pref_size
		return super().get_preferred_size()

	def render(self, renderer):
		pl = self.padding[0] * self.tui.x_scaling
		pr = self.padding[1] * self.tui.x_scaling
		pb = self.padding[2] * self.tui.y_scaling
		pt = self.padding[3] * self.tui.y_scaling
		if self.style is not None and len(self.text) > 0:
			w, h = renderer.text_size(
				self.style.font.id,
				self.text,
				self.tui.virtual_aspect,
				self.tui.x_scaling, self.tui.y_scaling,
				self.font_size
			)
			self.pref_size = (w, h)
			bounds = self.get_corrected_bounds()
			color = self.style.text_color if self.enabled else self.style.disabled_text_color

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

			renderer.end() ## We need to end the rendering in order
						   ## to draw the text with BLF, because it doesn't like
						   ## VAOs...
			fid = self.style.font.id if self.font is None else self.font.id
			renderer.text(
				fid,
				self.text,
				x, y,
				color,
				self.tui.virtual_aspect,
				self.tui.x_scaling, self.tui.y_scaling,
				self.font_size
			)
			renderer.begin()
		if self.image is not None:
			bounds = self.get_corrected_bounds_no_intersect()
			ix = bounds.x
			sz = min(bounds.w, bounds.h)
			isz = max(self.image.width, self.image.height)
			ratio = sz / isz
			iw = min(self.image.width * ratio, self.image.width)
			ih = min(self.image.height * ratio, self.image.height)

			if self.image_align == ALIGN_CENTER:
				ix += bounds.w / 2 - iw / 2
			elif self.image_align == ALIGN_RIGHT:
				ix += (bounds.w - iw) - pr
			elif self.image_align == ALIGN_LEFT:
				ix += pl
			renderer.draw(self.image, ix, bounds.y + (bounds.h / 2 - ih / 2), iw, ih, gray=(not self.enabled))
