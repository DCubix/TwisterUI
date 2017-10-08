from bge import events as BGE_Events
from bge import logic as BGE_Logic
from tui.core import Widget
from tui.core import EVENT_STATUS_CONSUMED, EVENT_TYPE_KEY, EVENT_TYPE_TEXT, EVENT_TYPE_FOCUS, EVENT_TYPE_MOUSE_BUTTON, EVENT_TYPE_MOUSE_MOTION

class Edit(Widget):
	def __init__(self, text=""):
		super().__init__()
		self.text = text

		self.__mouse_x = -1
		self.__mouse_drag_x = 0
		self.__caret_x = 0
		self.__selection = -1
		self.__mouse_mod = None
		self.__textOffset = 3
		self.__glyphs = []
		self.__avg_height = 0.0
		self.__blink = True
		self.__blink_time = 0.0

		self.hovered = False
		self.clicked = False

		self.font_size = 10.0
		self.font = None
		self.editable = True
		self.masked = False
		self.mask = "*"

		self.bounds.set_value(0, 0, 190, 20)

	def update(self):
		self.__textOffset = 3
		if not self.focused:
			self.__selection = -1
			self.__caret_x = -1
		
		self.__blink_time += (1.0 / BGE_Logic.getLogicTicRate())
		if self.__blink_time >= 0.5:
			self.__blink = not self.__blink
			self.__blink_time = 0.0

	def __compute_glyph_positions(self, renderer, text):
		fid = self.style.font.id if self.font is None else self.font.id
		self.__glyphs = []
		for i in range(len(text)):
			txt = text[:i]
			tw, th = renderer.text_size(
				fid,
				txt,
				self.tui.virtual_aspect,
				self.tui.x_scaling, self.tui.y_scaling,
				self.font_size
			)
			self.__glyphs.append(tw)
			self.__avg_height = max(self.__avg_height, th)
		return len(self.__glyphs)

	def __position_to_cursor(self, posx, lastx, size):
		cursor_id = 0
		if size == 0:
			return cursor_id
		cx = self.__glyphs[cursor_id]
		for i in range(1, size):
			if abs(cx - posx) > abs(self.__glyphs[i] - posx):
				cursor_id = i
				cx = self.__glyphs[cursor_id]
		if abs(cx - posx) > abs(lastx - posx):
			cursor_id = size
		return cursor_id

	def __cursor_to_position(self, index, lastx, size):
		pos = 0
		if size == 0:
			return pos

		if index == size:
			pos = lastx
		else:
			pos = self.__glyphs[index]
		return pos

	def __update_cursor(self, lastx, size):
		if self.__mouse_x != -1:
			if self.__mouse_mod == BGE_Events.LEFTSHIFTKEY or self.__mouse_mod == BGE_Events.RIGHTSHIFTKEY:
				if self.__selection == -1:
					self.__selection = self.__caret_x
			else:
				self.__selection = -1
			self.__caret_x = self.__position_to_cursor(self.__mouse_x, lastx, size)
			self.__mouse_x = -1
		elif self.__mouse_drag_x != -1:
			if self.__selection == -1:
				self.__selection = self.__caret_x
			self.__caret_x = self.__position_to_cursor(self.__mouse_drag_x, lastx, size)
		else:
			if self.__caret_x < 0:
				self.__caret_x = size
		if self.__caret_x == self.__selection:
			self.__selection = -1

	def render(self, renderer):
		if self.style is not None:
			bounds = self.get_corrected_bounds()
			nbounds = self.get_corrected_bounds_no_intersect()

			n = None
			if self.enabled:
				if not self.hovered and not self.focused:
					n = self.style.textures["TextBox_normal"]
				elif self.hovered and not self.focused:
					n = self.style.textures["TextBox_hover"]
				else:
					n = self.style.textures["TextBox_click"]
			else:
				n = self.style.textures["TextBox_disabled"]

			if n:
				renderer.nine_patch_object(n, *nbounds.packed())
			
			tcolor = self.style.text_color if self.enabled else self.style.disabled_text_color

			text_x = nbounds.x
			nbounds.x += self.__textOffset

			fid = self.style.font.id if self.font is None else self.font.id
			mask = self.mask if len(self.mask) == 1 else self.mask[0]
			text = self.text if not self.masked else mask * len(self.text)
			tw, th = renderer.text_size(
				fid,
				text,
				self.tui.virtual_aspect,
				self.tui.x_scaling, self.tui.y_scaling,
				self.font_size
			)
			text_y = nbounds.y + (nbounds.h/2 - th/2)

			nglyphs = self.__compute_glyph_positions(renderer, text)
			self.__update_cursor(tw, nglyphs)

			prev_cpos = self.__caret_x - 1 if self.__caret_x > 0 else 0
			next_cpos = self.__caret_x + 1 if self.__caret_x < nglyphs else nglyphs
			prev_cx = nbounds.x + self.__cursor_to_position(prev_cpos, tw, nglyphs)
			next_cx = nbounds.x + self.__cursor_to_position(next_cpos, tw, nglyphs)

			clip_x = nbounds.x + 3
			clip_width = nbounds.w - 12
			
			if next_cx > clip_x + clip_width:
				self.__textOffset -= next_cx - (clip_x + clip_width) + 1
			if prev_cx < nbounds.x:
				self.__textOffset += nbounds.x - prev_cx + 1
			nbounds.x = int(text_x + self.__textOffset)

			renderer.end()
			renderer.text(
				fid,
				text,
				nbounds.x, text_y,
				tcolor,
				self.tui.virtual_aspect,
				self.tui.x_scaling, self.tui.y_scaling,
				self.font_size
			)
			renderer.begin()

			if self.__caret_x > -1:
				if self.__selection > -1:
					caret_x = self.__cursor_to_position(self.__caret_x, tw, nglyphs)
					sel_x = self.__cursor_to_position(self.__selection, tw, nglyphs)
					if caret_x > sel_x:
						tmp = sel_x
						sel_x = caret_x
						caret_x = tmp

					s = self.style.textures["TextBox_select"]
					if s:
						renderer.nine_patch_object(
							s,
							caret_x + nbounds.x,
							text_y,
							sel_x - caret_x,
							self.__avg_height
						)

			if self.__blink and self.focused and self.editable:
				_, oth = renderer.text_size(
					fid,
					self.text,
					self.tui.virtual_aspect,
					self.tui.x_scaling, self.tui.y_scaling,
					self.font_size
				)
				oth += 2
				otext_y = nbounds.y + (nbounds.h/2 - oth/2)
				caret_x = self.__cursor_to_position(self.__caret_x, tw, nglyphs)
				caret_x += nbounds.x
				tcol = tcolor if len(tcolor) == 4 else [*tcolor, 1.0]
				renderer.rectangle(caret_x, otext_y, 1 * self.tui.x_scaling, oth, color=tcol, wire=False)

	def __delete_selection(self):
		if self.__selection > -1:
			begin = self.__selection
			end = self.__caret_x

			if begin > end:
				tmp = begin
				begin = end
				end = tmp
			
			if begin == end-1:
				self.text = self.text[:begin] + self.text[begin+1:]
			else:
				self.text = self.text[:begin] + self.text[end:]
			
			self.__caret_x = begin
			self.__selection = -1
			return True
		return False

	def __copy_selection(self):
		pass

	def handle_events(self, event):
		nbounds = self.get_corrected_bounds_no_intersect()
		if event.get_type() == EVENT_TYPE_TEXT and self.focused and self.editable:
			self.text = self.text[:self.__caret_x] + event.character + self.text[self.__caret_x:]
			self.__delete_selection()
			self.__caret_x += 1
			self.__selection = -1
			self.__blink = True
		elif event.get_type() == EVENT_TYPE_KEY and self.focused and self.editable:
			# TODO Implement shortcuts for copying, pasting, selecting all, etc...
			if event.status:
				if event.key == BGE_Events.LEFTARROWKEY:
					self.__caret_x -= 1 if self.__caret_x > 0 else 0
					self.__selection = -1
				elif event.key == BGE_Events.RIGHTARROWKEY:
					self.__caret_x += 1 if self.__caret_x < len(self.text) else 0
					self.__selection = -1
				elif event.key == BGE_Events.HOMEKEY:
					self.__caret_x = 0
					self.__selection = -1
				elif event.key == BGE_Events.ENDKEY:
					self.__caret_x = len(self.text)
					self.__selection = -1
				elif event.key == BGE_Events.DELKEY:
					if not self.__delete_selection():
						if self.__caret_x < len(self.text):
							self.text = self.text[:self.__caret_x] + self.text[self.__caret_x+1:]
					else:
						self.__textOffset = 3
					self.__selection = -1
				elif event.key == BGE_Events.BACKSPACEKEY:
					if not self.__delete_selection():
						if self.__caret_x > 0:
							i = self.__caret_x-1
							self.text = self.text[:i] + self.text[i+1:]
							self.__caret_x -= 1
					else:
						self.__textOffset = 3
					self.__selection = -1
				self.__blink = True
		elif event.get_type() == EVENT_TYPE_MOUSE_BUTTON and self.editable:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				if event.status:
					self.__mouse_drag_x = -1
					self.__mouse_x = event.x - nbounds.x
					self.__mouse_mod = event.modifiers[0] if len(event.modifiers) > 0 else None
					self.__blink = True
					self.clicked = True
				else:
					if self.clicked:
						self.clicked = False
					self.__mouse_x = -1
					self.__mouse_drag_x = -1
			else:
				self.clicked = False
				self.__mouse_x = -1
			if not event.status:
				self.__mouse_x = -1
				self.__mouse_drag_x = -1
				self.clicked = False
				self.hovered = False
		elif event.get_type() == EVENT_TYPE_MOUSE_MOTION and self.editable:
			if self.get_corrected_bounds().has_point(event.x, event.y):
				if self.clicked:
					self.__mouse_drag_x = event.x - nbounds.x
				self.hovered = True
			else:
				self.hovered = False
				self.clicked = False
				self.__mouse_x = -1
				self.__mouse_drag_x = -1
		elif event.get_type() == EVENT_TYPE_FOCUS:
			self.__caret_x = 0
			self.hovered = False
			return EVENT_STATUS_CONSUMED
		return super().handle_events(event)