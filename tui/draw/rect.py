"""
File: draw/rect.py
Description: Rectangle
Author:	Diego Lopes (TwisterGE/DCubix) < diego95lopes@gmail.com >
"""

import sys

class Rect:
	def __init__(self, x=0, y=0, w=1, h=1):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def has_point(self, x, y):
		return x > self.x and \
				x < self.x + self.w and \
				y > self.y and \
				y < self.y + self.h

	def intersects(self, o):
		if not isinstance(o, Rect):
			return False
		return o.x < self.x + self.w and \
				o.x + o.w > self.x and \
				o.y < self.y + self.h and \
				o.y + o.h > self.y
	
	def intersect(self, r):
		tx1 = self.x
		ty1 = self.y
		rx1 = r.x
		ry1 = r.y
		tx2 = tx1; tx2 += self.w
		ty2 = ty1; ty2 += self.h
		rx2 = rx1; rx2 += r.w
		ry2 = ry1; ry2 += r.h
		if tx1 < rx1: tx1 = rx1
		if ty1 < ry1: ty1 = ry1
		if tx2 > rx2: tx2 = rx2
		if ty2 > ry2: ty2 = ry2
		tx2 -= tx1
		ty2 -= ty1
		if tx2 < (-sys.maxsize-1): tx2 = (-sys.maxsize-1)
		if ty2 < (-sys.maxsize-1): ty2 = (-sys.maxsize-1)
		return Rect(tx1, ty1, tx2, ty2)

	def transform(self, x, y):
		self.x = x * self.x
		self.y = y * self.y
		self.w = x * self.w
		self.h = y * self.h
		return self

	def set_value(self, x=0, y=0, w=1, h=1):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def packed(self):
		return (self.x, self.y, self.w, self.h)