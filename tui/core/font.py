"""
File: core/font.py
Description: Basic BLF wrapper
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

import blf

class Font:
	"""
	Simple Font class.
	Wraps BLF font loading.
	Attributes:
		id: Font ID (from BLF).
		size: Font size.
	"""
	def __init__(self, fileName=None):
		self.id = blf.load(fileName) if fileName is not None else 0
		self.size = 18.0

	def get_size(self, old_size, new_size):
		return Font.get_best_size(self.size, old_size, new_size)

	@staticmethod
	def get_best_size(font_size, old_size, new_size):
		return old_size * font_size / new_size
