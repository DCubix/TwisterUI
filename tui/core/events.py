EVENT_STATUS_AVAILABLE = 0
EVENT_STATUS_CONSUMED = 1

EVENT_TYPE_MOUSE_BUTTON = 0
EVENT_TYPE_MOUSE_MOTION = 1
EVENT_TYPE_KEY = 2
EVENT_TYPE_FOCUS = 3
EVENT_TYPE_SCROLL = 4
EVENT_TYPE_TEXT = 5

class Event:
	def get_type(self):
		pass

class EventSubscriber:
	def __init__(self):
		self.var_enabled = True

	@property
	def enabled(self):
		return self.var_enabled

	@enabled.setter
	def enabled(self, e):
		self.var_enabled = e

	def handle_events(self, event):
		pass

class EventHandler:
	def __init__(self):
		self.subscribers = {}
	
	def bind(self, subscriber, etype):
		if etype in self.subscribers:
			self.subscribers[etype].append(subscriber)
		else:
			self.subscribers[etype] = []
			self.bind(subscriber, etype)

	def send(self, event):
		if event.get_type() not in self.subscribers:
			return
		for sub in self.subscribers[event.get_type()]:
			if sub.enabled and sub.handle_events(event) == EVENT_STATUS_CONSUMED:
				break

class FocusEvent(Event):
	def __init__(self, status):
		self.focused = status

	def get_type(self):
		return EVENT_TYPE_FOCUS

class KeyEvent(Event):
	def __init__(self, key, mod, status):
		self.key = key
		self.modifiers = mod
		self.status = status

	def get_type(self):
		return EVENT_TYPE_KEY

class TextEvent(Event):
	def __init__(self, character):
		self.character = character
	
	def get_type(self):
		return EVENT_TYPE_TEXT

class MouseButtonEvent(Event):
	def __init__(self, button, status, x, y):
		self.modifiers = []
		self.button = button
		self.status = status
		self.x = x
		self.y = y

	def get_type(self):
		return EVENT_TYPE_MOUSE_BUTTON

class MouseMotionEvent(Event):
	def __init__(self, x, y, dx, dy):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

	def get_type(self):
		return EVENT_TYPE_MOUSE_MOTION

class ScrollEvent(Event):
	def __init__(self, delta):
		self.delta = delta

	def get_type(self):
		return EVENT_TYPE_SCROLL