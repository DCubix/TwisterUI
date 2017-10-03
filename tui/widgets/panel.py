from tui.core import Widget
from tui.draw import Rect
from tui.core import EVENT_STATUS_CONSUMED, EVENT_STATUS_AVAILABLE

class Panel(Widget):
	def __init__(self, layout=None):
		super().__init__()

		self.children = []
		self.background = True
		self.layout = layout

	def get_content_bounds(self):
		return Rect(1, 1, self.bounds.w - 2, self.bounds.h - 2)

	def add(self, widget, layout_args=-1):
		widget.style = self.style
		if widget.parent == self:
			return self
		elif widget.parent is not None:
			widget.parent.children.remove(widget)
		
		widget.parent = self
		widget.tui = self.tui
		widget.layout_args = layout_args
		self.children.append(widget)
		return widget

	def update(self):
		for w in self.children:
			w.update()
			if self.layout is not None:
				self.layout.set_args(w)
		if self.layout is not None:
			self.layout.perform_layout(self)

	def render(self, renderer):
		if self.background and self.style is not None:
			n = self.style.textures["Panel"]
			renderer.nine_patch_object(n, *self.get_corrected_bounds_no_intersect().packed())
		for w in self.children:
			if w.visible:
				b = w.get_corrected_bounds()
				b.y -= 1
				b.h += 1
				renderer.clip_start(*b.packed())
				w.render(renderer)
				renderer.clip_end()

	def handle_events(self, event):
		for w in self.children:
			if w.enabled and w.visible and w.handle_events(event) == EVENT_STATUS_CONSUMED:
				return EVENT_STATUS_CONSUMED
		return super().handle_events(event)