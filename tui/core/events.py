"""
File: core/events.py
Description: Event handling module
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

EVENT_STATUS_AVAILABLE = 0
EVENT_STATUS_CONSUMED = 1

EVENT_TYPE_MOUSE_BUTTON = 0
EVENT_TYPE_MOUSE_MOTION = 1
EVENT_TYPE_KEY = 2
EVENT_TYPE_FOCUS = 3
EVENT_TYPE_SCROLL = 4
EVENT_TYPE_TEXT = 5

class Event:
	"""Base Event class"""

	def get_type(self):
		"""
		Gets the type of the event.
		
		Returns:
			The type of the current event.
		"""
		pass

class EventSubscriber:
	"""
	Base event receiver.
	It's the base of all the Widgets.
	"""
	def __init__(self):
		self.var_enabled = True

	@property
	def enabled(self):
		"""
		Get/Set the state of the subscriber.
		Whether or not it can listen to events sent by the event handler.
		"""
		return self.var_enabled

	@enabled.setter
	def enabled(self, e):
		self.var_enabled = e

	def handle_events(self, event):
		"""Do whatever logic with the incoming event"""
		pass

class EventHandler:
	"""
	Main event processor.
	Sends events to all subscribers and register new subscribers.
	Attributes:
		subscribers: The event subscribers that will listen to the events sent by this event handler.
	"""
	def __init__(self):
		self.subscribers = {}
	
	def bind(self, subscriber, etype):
		"""
		Binds a subscriber to an event type.
		Args:
			subscriber: The subscriber of EventSubscriber type.
			etype: The event type.
		"""
		if etype in self.subscribers:
			self.subscribers[etype].append(subscriber)
		else:
			self.subscribers[etype] = []
			self.bind(subscriber, etype)

	def send(self, event):
		"""
		Sends a specific event to all the subscribers registered
		to that event.
		Args:
			event: The event to be sent.
		"""
		if event.get_type() not in self.subscribers:
			return
		for sub in self.subscribers[event.get_type()]:
			if sub.enabled and sub.handle_events(event) == EVENT_STATUS_CONSUMED:
				break

class FocusEvent(Event):
	"""
	Focus/Blur event.
	Raised when the widget gains or loses focus, i.e: Click in and out.
	Attributes:
		focused: Focused state.
	"""
	def __init__(self, status):
		self.focused = status

	def get_type(self):
		return EVENT_TYPE_FOCUS

class KeyEvent(Event):
	"""
	Keyboard event.
	Raised when any key is pressed.
	Attributes:
		key: The key code.
		modifiers: The list of modifiers. i.e: Shift, Alt...
		status: The activation status of the key.
	"""
	def __init__(self, key, mod, status):
		self.key = key
		self.modifiers = mod
		self.status = status

	def get_type(self):
		return EVENT_TYPE_KEY

class TextEvent(Event):
	"""
	Text event.
	Raised when typing text. Same as KeyEvent.
	Attributes:
		character: The currently typed character.
	"""
	def __init__(self, character):
		self.character = character
	
	def get_type(self):
		return EVENT_TYPE_TEXT

class MouseButtonEvent(Event):
	"""
	Mouse button event.
	Raised when any mouse button is pressed.
	Attributes:
		modifiers: The list of modifiers. i.e: Shift, Alt...
		button: The current mouse button.
		status: The button status.
		x: X coordinate in the virtual space.
		y: Y coordinate in the virtual space.
	"""
	def __init__(self, button, status, x, y):
		self.modifiers = []
		self.button = button
		self.status = status
		self.x = x
		self.y = y

	def get_type(self):
		return EVENT_TYPE_MOUSE_BUTTON

class MouseMotionEvent(Event):
	"""
	Mouse movement event.
	Raised when the mouse is moved.
	Attributes:
		x: X coordinate in the virtual space.
		y: Y coordinate in the virtual space.
		dx: Delta X coordinate between this and the last frame in the virtual space.
		dy: Delta Y coordinate between this and the last frame in the virtual space.
	"""
	def __init__(self, x, y, dx, dy):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

	def get_type(self):
		return EVENT_TYPE_MOUSE_MOTION

class ScrollEvent(Event):
	"""
	Scroll event.
	Raised when the mouse wheel is scrolled.
	Attributes:
		delta: Scroll value.
	"""
	def __init__(self, delta):
		self.delta = delta

	def get_type(self):
		return EVENT_TYPE_SCROLL