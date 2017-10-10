"""
File: core/widget.py
Description: Base widget
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

from tui.draw.rect import Rect
from .events import EventSubscriber, EVENT_TYPE_MOUSE_BUTTON, EVENT_STATUS_AVAILABLE, EVENT_STATUS_CONSUMED

class Widget(EventSubscriber):
	"""
	Base widget.
	A visible event subscriber.
	Attributes:
		parent: Parent widget (container).
		bounds: Position and Size (x, y, width, height).
		visible: Visibility status.
		focused: Focus status.
		auto_size: Automatic size calculation.
		margin: Margin between this and the next widget.
		style: Visual style of the widget.
		id: Identification for this widget.
		layout_args: Arguments for the container (parent) layout.
		tui: GUI system.
	"""
	def __init__(self):
		super().__init__()

		self.parent = None

		self.bounds = Rect(0, 0, 50, 50)
		self.visible = True
		self.focused = False
		self.auto_size = False
		self.margin = [2, 2, 2, 2]
		self.style = None
		self.id = ""
		self.layout_args = -1

		self.tui = None

	@property
	def enabled(self):
		"""
		Get/Set the state of the widget.
		Whether or not it can listen to events sent by the event handler.
		"""
		pe = True
		if self.parent is not None:
			pe = self.parent.enabled
		return pe and self.var_enabled

	@enabled.setter
	def enabled(self, e):
		self.var_enabled = e

	def request_focus(self):
		"""Call the GUI manager out for attention."""
		self.tui.set_focus(self)

	def get_transformed_bounds_no_intersect(self):
		"""
		Returns:
			The transformed (parent + this) bounds without parent intersection.
		"""
		rect = Rect(0, 0, 0, 0)
		if self.parent is not None:
			rect = self.parent.get_transformed_bounds_no_intersect()
		return Rect(self.bounds.x + rect.x, self.bounds.y + rect.y, self.bounds.w, self.bounds.h)

	def get_transformed_bounds(self):
		"""
		Returns:
			The transformed (parent + this) bounds with parent intersection.
		"""
		bounds = self.get_transformed_bounds_no_intersect()
		if self.parent is not None:
			bounds = self.get_transformed_bounds_no_intersect().intersect(
				self.parent.get_transformed_bounds_no_intersect()
			)
		return bounds

	def get_corrected_bounds_no_intersect(self):
		"""
		Returns:
			The corrected ((parent + this) * xyscaling) bounds without parent intersection.
		"""
		return self.get_transformed_bounds_no_intersect().transform(self.tui.x_scaling, self.tui.y_scaling)

	def get_corrected_bounds(self):
		"""
		Returns:
			The corrected ((parent + this) * xyscaling) bounds with parent intersection.
		"""
		return self.get_transformed_bounds().transform(self.tui.x_scaling, self.tui.y_scaling)

	def set_size(self, w, h):
		"""
		Sets the size of the widget.
		Args:
			w: The new width.
			h: The new height.
		"""
		self.bounds.w = w
		self.bounds.h = h
	
	def get_preferred_size(self):
		"""Gets the preferred size of the widget."""
		return (self.bounds.w, self.bounds.h)

	def render(self, renderer):
		pass
	
	def update(self):
		self.set_size(*self.get_preferred_size())

	def handle_events(self, event):
		if event.get_type() == EVENT_TYPE_MOUSE_BUTTON and self.enabled and self.visible:
			if self.get_corrected_bounds().has_point(event.x, event.y) and event.status:
				self.request_focus()
				return EVENT_STATUS_CONSUMED
		return EVENT_STATUS_AVAILABLE
