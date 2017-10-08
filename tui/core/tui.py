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

		self.__keys_down = {}

	def refresh(self, widget_list=None):
		if widget_list is None:
			widget_list = self.widgets
		for w in widget_list:
			w.style = self.global_style
			if hasattr(w, "children"):
				self.refresh(w.children)

	def set_focus(self, widget):
		if self.focused == widget:
			return
		if self.focused is not None:
			self.focused.focused = False
			self.event_handler.send(FocusEvent(self.focused.focused))
		if widget is not None:
			widget.focused = True
			self.event_handler.send(FocusEvent(widget.focused))
		self.focused = widget

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
		self.event_handler.bind(widget, EVENT_TYPE_TEXT)
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
				b.y -= 1
				b.h += 1
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

		## Modifiers
		mods = []
		for ev in [events.LEFTSHIFTKEY, events.RIGHTSHIFTKEY, events.LEFTALTKEY, events.RIGHTALTKEY,	events.LEFTCTRLKEY, events.RIGHTCTRLKEY]:
			if logic.keyboard.inputs[ev].active:
				mods.append(ev)

		mx, my, on_screen = self.output.get_mouse_position()
		mbe = MouseButtonEvent(0, 0, mx, my)
		for e in mouse_button_events:
			mbe.modifiers = mods
			mbe.button = e
			if logic.mouse.inputs[e].activated and on_screen:
				mbe.status = True
				self.event_handler.send(mbe)
			elif logic.mouse.inputs[e].released and on_screen:
				mbe.status = False
				self.event_handler.send(mbe)

		## Mouse motion event
		if on_screen:
			mme = MouseMotionEvent(mx, my, mx - self.px, my - self.py)
			self.event_handler.send(mme)

		## Mouse wheel events
		if on_screen:
			delta = 0
			if logic.mouse.inputs[events.WHEELUPMOUSE].activated:
				delta = 1
			elif logic.mouse.inputs[events.WHEELDOWNMOUSE].activated:
				delta = -1
			if abs(delta) > 0:
				self.event_handler.send(ScrollEvent(delta))

		self.px = mx
		self.py = my

		## Key events
		for i in range(0, 256):
			shift = logic.keyboard.inputs[events.LEFTSHIFTKEY].active or \
					logic.keyboard.inputs[events.RIGHTSHIFTKEY].active
			try:
				# Text Event
				if logic.keyboard.inputs[i].activated:
					c = events.EventToCharacter(i, shift)
					if len(c) > 0:
						self.event_handler.send(TextEvent(c))
				
				# Key Event
				if logic.keyboard.inputs[i].activated:
					self.event_handler.send(KeyEvent(i, mods, True))
					self.__keys_down[i] = True
				else:
					if self.__keys_down[i] == True:
						self.event_handler.send(KeyEvent(i, mods, False))
						self.__keys_down[i] = False
			except KeyError:
				continue

	@property
	def x_scaling(self):
		return self.output.width / self.virtual_width

	@property
	def y_scaling(self):
		return self.output.height / self.virtual_height

	@property
	def virtual_aspect(self):
		return self.virtual_width / self.virtual_height