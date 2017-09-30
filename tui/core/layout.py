from tui.widgets.panel import Panel

class Layout:
	def perform_layout(self, widget):
		pass
	
	def set_args(self, widget):
		pass

class StackLayout(Layout):
	def perform_layout(self, widget):
		if not isinstance(widget, Panel):
			return
		nexty = 0
		for w in widget.children:
			if not w.visible:
				continue
			w.set_size(widget.bounds.w - (w.margin[0]+w.margin[2]), w.bounds.h)

			nexty += w.margin[3]
			w.bounds.x = w.margin[0]
			w.bounds.y = nexty

			nexty += w.bounds.h

class FlowLayout(Layout):
	def perform_layout(self, widget):
		if not isinstance(widget, Panel):
			return
		nextx = 0
		nexty = 0

		for w in widget.children:
			if not w.visible:
				continue
			if w.auto_size:
				w.set_size(widget.bounds.w, w.bounds.h)

			nextx += w.margin[0]
			nexty += w.margin[3]
			w.bounds.x = nextx
			w.bounds.y = nexty

			nextx = 0
			nexty += w.bounds.h

BORDER_LAYOUT_POS_LEFT = 0
BORDER_LAYOUT_POS_RIGHT = 1
BORDER_LAYOUT_POS_BOTTOM = 2
BORDER_LAYOUT_POS_TOP = 3
BORDER_LAYOUT_POS_CENTER = 4

class BorderLayout(Layout):
	def __init__(self):
		self.left = None
		self.right = None
		self.bottom = None
		self.top = None
		self.center = None

	def get_child(self, arg):
		if arg == BORDER_LAYOUT_POS_LEFT:
			return self.left
		elif arg == BORDER_LAYOUT_POS_RIGHT:
			return self.right
		elif arg == BORDER_LAYOUT_POS_BOTTOM:
			return self.bottom
		elif arg == BORDER_LAYOUT_POS_TOP:
			return self.top
		elif arg == BORDER_LAYOUT_POS_CENTER:
			return self.center
		return None

	def perform_layout(self, widget):
		if not isinstance(widget, Panel):
			return
		bounds = widget.get_content_bounds()
		x0 = bounds.x
		y0 = bounds.y
		x1 = bounds.x + bounds.w
		y1 = bounds.y + bounds.h

		w = None
		margin = []
		w = self.get_child(BORDER_LAYOUT_POS_TOP)
		if w is not None:
			margin = w.margin
			w.bounds.x = margin[0] + x0
			w.bounds.y = margin[3] + y0
			w.set_size((x1 - x0) - (margin[0] + margin[1]), w.bounds.h)
			y0 += w.bounds.h + margin[3]

		w = self.get_child(BORDER_LAYOUT_POS_BOTTOM)
		if w is not None:
			margin = w.margin
			w.bounds.x = margin[0] + x0
			w.bounds.y = y1 - (w.bounds.h + margin[3])
			w.set_size((x1 - x0) - (margin[0] + margin[1]), w.bounds.h)
			y1 -= w.bounds.h + margin[2]

		w = self.get_child(BORDER_LAYOUT_POS_LEFT)
		if w is not None:
			margin = w.margin
			w.bounds.x = margin[0] + x0
			w.bounds.y = margin[3] + y0
			w.set_size(w.bounds.w, (y1 - y0) - (margin[2] + margin[3]))
			x0 += w.bounds.w + margin[1];

		w = self.get_child(BORDER_LAYOUT_POS_RIGHT)
		if w is not None:
			margin = w.margin
			w.bounds.x = x1 - (w.bounds.w + margin[2])
			w.bounds.y = margin[3] + y0
			w.set_size(w.bounds.w, (y1 - y0) - (margin[2] + margin[3]))
			x1 -= w.bounds.w + margin[0]
		
		w = self.get_child(BORDER_LAYOUT_POS_CENTER)
		if w is not None:
			margin = w.margin
			w.bounds.x = margin[0] + x0
			w.bounds.y = margin[3] + y0
			w.set_size((x1 - x0) - (margin[0] + margin[1]), (y1 - y0) - (margin[2] + margin[3]))

	def set_args(self, widget):
		arg = BORDER_LAYOUT_POS_CENTER
		if widget.layout_args != -1:
			arg = widget.layout_args
		
		if arg == BORDER_LAYOUT_POS_LEFT:
			self.left = widget
		elif arg == BORDER_LAYOUT_POS_RIGHT:
			self.right = widget
		elif arg == BORDER_LAYOUT_POS_BOTTOM:
			self.bottom = widget
		elif arg == BORDER_LAYOUT_POS_TOP:
			self.top = widget
		elif arg == BORDER_LAYOUT_POS_CENTER:
			self.center = widget
