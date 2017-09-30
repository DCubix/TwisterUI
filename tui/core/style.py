import json
from bge import logic
from tui.draw.renderer import NinePatch
from tui.draw.texture import ImageTexture
from .font import Font

class Style:

	__cache = {}

	def __init__(self, styleFile=None):
		self.textures = {}
		self.font = None
		self.text_color = (0.0, 0.0, 0.0)
		self.disabled_text_color = (0.5, 0.5, 0.5)

		if styleFile is not None:
			self.load(styleFile)

	def load(self, styleFile):
		sfile = {}
		with open(styleFile) as fp:
			sfile = json.load(fp)
		
		if "font" in sfile:
			self.font = Font(logic.expandPath(sfile["font"]))
		else:
			self.font = Font()

		if "text_color" in sfile:
			self.text_color = sfile["text_color"]
		
		if "disabled_text_color" in sfile:
			self.disabled_text_color = sfile["disabled_text_color"]
		
		if "regions" not in sfile or "image" not in sfile:
			raise Exception("Invalid Style file.")
		
		img = ImageTexture(logic.expandPath(sfile["image"]))

		for name, np in sfile["regions"].items():
			if name in self.textures:
				continue
			region = np[0]
			lp, rp, bp, tp = np[1]
			self.textures[name] = NinePatch(img, lp, rp, bp, tp, region)
