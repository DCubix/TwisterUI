"""
File: core/tui.py
Description: User interface management and logic
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from bge import render, logic, events, types
from tui.draw import Viewport, ObjectTexture, Renderer
from .style import Style
from .events import *

class TUI:
	"""
	Main UI handling system.
	Attributes:
		virtual_width: Virtual width of the GUI.
		virtual_height: Virtual height of the GUI.
		event_handler: Event handler object.
		renderer: Renderer object.
		widgets: List of widgets.
		focused: Currently focused widget.
		global_style: Main style file for all the widgets. (Use refresh() to apply changes).
	"""
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
		"""
		Refresh all the widgets recursively to apply changed to the
		global style.
		Args:
			widget_list: List of widgets to apply the global style to.
		"""
		if widget_list is None:
			widget_list = self.widgets
		for w in widget_list:
			w.style = self.global_style
			if hasattr(w, "children"):
				self.refresh(w.children)

	def set_focus(self, widget):
		"""
		Set the specified widget (if valid) to focused
		and blurs the previous widget. See: Widget.request_focus()
		Args:
			widget: A widget or None.
		"""
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
		"""
		Adds a new widget to the system.
		Args:
			widget: A valid not-yet-added widget.
		"""
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

	@property
	def output(self):
		"""Gets/Sets the output method used by this system."""
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
		"""X aspect ratio between the output width and the virtual width."""
		return self.output.width / self.virtual_width

	@property
	def y_scaling(self):
		"""Y aspect ratio between the output height and the virtual height."""
		return self.output.height / self.virtual_height

	@property
	def virtual_aspect(self):
		"""Virtual aspect ratio."""
		return self.virtual_width / self.virtual_height

	@staticmethod
	def __tui_render():
		if not hasattr(logic, "tuis"):
			return
		for scene, tui in logic.tuis.items():
			tui.render()

	@staticmethod
	def main_loop():
		"""Update all the systems registered."""
		if not hasattr(logic, "tuis"):
			return
		for scene, tui in logic.tuis.items():
			tui.update()

	@staticmethod
	def get_tui(obj, styleFile, width=1280, height=720, resolution=1):
		"""Gets or creates a system from an object or a scene."""
		if not isinstance(obj, types.KX_Scene) and not isinstance(obj, types.KX_GameObject):
			raise ValueError("Object must be a KX_Scene or a KX_GameObject.")
			return
		if not hasattr(logic, "tuis"):
			logic.tuis = {}
			logic.tui_scenes = []

		scene = None
		w = width * resolution
		h = height * resolution
		if isinstance(obj, types.KX_Scene):
			scene = obj
			output = Viewport(w, h)
		else:
			scene = obj.scene
			output = ObjectTexture(obj, w, h)
		if obj not in logic.tuis:
			if styleFile is None:
				raise ValueError("Style file must not be None.")
				return
			logic.tuis[obj] = TUI(styleFile, output, width, height)
			if scene not in logic.tui_scenes:
				scene.post_draw.append(TUI.__tui_render)
				logic.tui_scenes.append(scene)
		return logic.tuis[obj]