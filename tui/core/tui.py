from bge import render, logic, events
from tui.draw.renderer import Renderer
from tui.draw.viewport import Viewport
from .style import Style
from .events import *

class TUI:
	def __init__(self, styleFile, output=None, virtual_width=1280, virtual_height=720):
		self.__output = output if output is not None else Viewport(render.getWindowWidth(), render.getWindowHeight())

		self.virtual_width = virtual_width
		self.virtual_height = virtual_height

		self.event_handler = EventHandler()
		self.renderer = Renderer(self.__output)

		self.widgets = []
		self.focused = None

		self.global_style = Style(styleFile)

		self.px = 0
		self.py = 0

	def set_focus(self, widget):
		if self.focused == widget:
			return
		if self.focused is not None:
			self.focused.focused = False
			self.event_handler.send(FocusEvent(self.focused.focused))
		if widget is not None:
			widget.focused = True
			self.event_handler.send(FocusEvent(widget.focused))

	def add(self, widget):
		if widget in self.widgets:
			return widget

		widget.style = self.global_style
		widget.tui = self
		self.widgets.append(widget)
		self.event_handler.bind(widget, EVENT_TYPE_FOCUS)
		self.event_handler.bind(widget, EVENT_TYPE_KEY)
		self.event_handler.bind(widget, EVENT_TYPE_MOUSE_BUTTON)
		self.event_handler.bind(widget, EVENT_TYPE_MOUSE_MOTION)
		self.event_handler.bind(widget, EVENT_TYPE_SCROLL)
		return widget

	def reset(self):
		self.widgets = []

	@property
	def output(self):
		return self.__output

	@output.setter
	def output(self, v):
		self.__output = v
		self.renderer.output = self.__output

	def render(self):
		self.output.bind()
		self.renderer.begin()
		for w in self.widgets:
			if w.visible and w.parent is None:
				b = w.get_corrected_bounds()
				b.y -= 2
				b.h += 4
				self.renderer.clip_start(*b.packed())
				w.render(self.renderer)
				self.renderer.clip_end()
		self.renderer.end()
		self.output.unbind()

	def update(self):
		for w in self.widgets:
			if w.parent is None:
				w.update()

		## Mouse button event
		mouse_button_events = [
			events.LEFTMOUSE,
			events.MIDDLEMOUSE,
			events.RIGHTMOUSE
		]
		mx, my = self.output.get_mouse_position()
		mbe = MouseButtonEvent(0, 0, mx, my)
		for e in mouse_button_events:
			mbe.button = e
			if logic.mouse.inputs[e].activated:
				mbe.status = True
				self.event_handler.send(mbe)
			elif logic.mouse.inputs[e].released:
				mbe.status = False
				self.event_handler.send(mbe)

		## Mouse motion event
		mme = MouseMotionEvent(mx, my, mx - self.px, my - self.py)
		self.event_handler.send(mme)

		self.px = mx
		self.py = my

	@property
	def x_scaling(self):
		return self.output.width / self.virtual_width

	@property
	def y_scaling(self):
		return self.output.height / self.virtual_height

	@property
	def virtual_aspect(self):
		return self.virtual_width / self.virtual_height