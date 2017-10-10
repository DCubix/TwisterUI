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