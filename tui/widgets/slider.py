from tui.core import Widget, EVENT_TYPE_SCROLL, EVENT_TYPE_MOUSE_BUTTON, EVENT_TYPE_MOUSE_MOTION, EVENT_STATUS_CONSUMED
from tui.draw import Rect

ORIENTATION_VERTICAL = 0
ORIENTATION_HORIZONTAL = 1

def roundPartial(value, resolution):
	return round(value / resolution) * resolution

class Range:
	def __init__(self, minimum=0, maximum=1):
		self.minimum = minimum
		self.maximum = maximum

	def clamp(self, value):
		return max(self.minimum, min(self.maximum, value))

	def normalized(self, value):
		return (self.clamp(value) - self.minimum) / (self.maximum - self.minimum)

	def unormalized(self, ratio):
		return self.clamp(ratio * self.delta + self.minimum)

	@property
	def delta(self):
		return abs(self.maximum - self.minimum)

class Slider(Widget):
	def __init__(self, minimum=0, maximum=100, step=10, rounded=False):
		super().__init__()
		self.range = Range(minimum, maximum)
		self.step = step
		self.rounded = rounded
		self.orientation = ORIENTATION_HORIZONTAL
		self.change_listeners = []

		self.clicked = False
		self.hover = False

		self.__value = 0
		self.__pos = 0
		self.__thumb = Rect(0, 0, 1, 1)

		self.bounds.set_value(0, 0, 120, 9)

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, v):
		if v != self.__value:
			prev = self.__value
			self.__value = v
			for cl in self.change_listeners:
				cl(self, prev)

	def __thumb_size(self):
		b = self.get_corrected_bounds_no_intersect()
		view_size = self.range.delta
		size = b.w if self.orientation == ORIENTATION_HORIZONTAL else b.h
		ret = (size * self.step / view_size)
		tt = self.style.textures["Slider_Thumb_normal"]
		tsize = tt.width+2 if self.orientation == ORIENTATION_HORIZONTAL else tt.height+2
		return ret if ret > tsize else tsize

	def __track_size(self):
		b = self.get_corrected_bounds_no_intersect()
		sz = b.w if self.orientation == ORIENTATION_HORIZONTAL else b.h
		return int(sz)

	def __update_slider(self, p):
		b = self.get_corrected_bounds()
		thumb = self.__thumb_size()
		track = self.__track_size()
		size = b.w if self.orientation == ORIENTATION_HORIZONTAL else b.h
		pos = b.x if self.orientation == ORIENTATION_HORIZONTAL else b.y

		trange = Range(thumb/2, track-thumb/2)
		cp = p - pos
		if cp <= 0:
			cp = 0
		elif cp >= track:
			cp = track

		cpos = cp

		ratio = trange.normalized(cp)
		val = self.range.unormalized(ratio)

		self.value = val if not self.rounded else roundPartial(val, self.step)

	def __update_val(self):
		self.__value = self.range.clamp(self.__value)
		thumb = self.__thumb_size()
		track = self.__track_size()
		trange = Range(thumb/2, track-thumb/2)
		ratio = self.range.normalized(self.__value)
		self.__pos = (ratio * trange.delta)

	def update(self):
		self.__update_val()

		b = self.get_corrected_bounds_no_intersect()
		if self.orientation == ORIENTATION_HORIZONTAL:
			self.__thumb.set_value(self.__pos + b.x, b.y, self.__thumb_size(), b.h)
		else:
			self.__thumb.set_value(b.x, self.__pos + b.y, b.w, self.__thumb_size())

	def render(self, renderer):
		if self.style is None:
			return
		t = None
		n = None
		if self.enabled:
			t = self.style.textures["Slider_Track_normal"]
			if not self.hover and not self.clicked:
				n = self.style.textures["Slider_Thumb_normal"]
			elif self.hover and not self.clicked:
				n = self.style.textures["Slider_Thumb_hover"]
			elif self.hover and self.clicked:
				n = self.style.textures["Slider_Thumb_click"]
		else:
			t = self.style.textures["Slider_Track_disabled"]
			n = self.style.textures["Slider_Thumb_disabled"]

		if t and n:
			b = self.get_corrected_bounds_no_intersect()
			renderer.nine_patch_object(t, *b.packed())
			renderer.nine_patch_object(n, *self.__thumb.packed())

	def handle_events(self, event):
		if event.get_type() == EVENT_TYPE_SCROLL and self.focused:
			if self.orientation == ORIENTATION_VERTICAL:
				self.value -= event.delta * self.step
			else:
				self.value += event.delta * self.step
			return EVENT_STATUS_CONSUMED
		elif event.get_type() == EVENT_TYPE_MOUSE_BUTTON:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				self.clicked = event.status
				if self.clicked:
					self.hover = True
					self.__update_slider(event.x if self.orientation == ORIENTATION_HORIZONTAL else event.y)
			else:
				self.clicked = False
			if not event.status:
				self.hover = False
				self.clicked = False
		elif event.get_type() == EVENT_TYPE_MOUSE_MOTION:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				self.hover = True
			else:
				if not self.clicked:
					self.hover = False
			if self.clicked:
				self.__update_slider(event.x if self.orientation == ORIENTATION_HORIZONTAL else event.y)
		return super().handle_events(event)