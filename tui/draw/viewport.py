from bge import logic, events
from OpenGL import GL
from .output import Output

class Viewport(Output):
	def __init__(self, width, height):
		super().__init__()
		self.width = width
		self.height = height

	def get_mouse_position(self):
		mx = logic.mouse.inputs[events.MOUSEX].values[-1]
		my = logic.mouse.inputs[events.MOUSEY].values[-1]
		return (mx, my)