# coding: utf8
from __future__ import unicode_literals

import funcy
try: #Python 2
	import Tkinter as tkinter
except: # Python 3
	import tkinter

class Marque(object):
	'''Une marque représentant un point sur une video
	'''
	BITMAP = """
		#define marque_width 10
		#define marque_height 10
		static unsigned char marque_bits[] = {
		   0x01, 0x02, 0x02, 0x01, 0xb4, 0x00, 0x78, 0x00, 0xfc, 0x00, 0xfc, 0x00,
		   0x78, 0x00, 0xb4, 0x00, 0x02, 0x01, 0x01, 0x02 };
	"""
	bitmaps = [None]*8
	colors = ["blue", "red", "green", "cyan", "yellow", "magenta", "black", "white"]

	def __init__(self, parent, x,y, color = 0):
		'''
			parent	:	une instance de Pivideo
			x,y		:	coordonnées
		'''

		if not Marque.bitmaps[color]:
			Marque.bitmaps[color] = tkinter.BitmapImage(data=Marque.BITMAP,foreground=Marque.colors[color])
		self.parent = parent
		self.x = x
		self.y = y
		self.id = parent.canvas.create_image(x,y,image = Marque.bitmaps[color], tags = "marques")

	def __del__(self):
		''' Destructeur
		'''
		self.parent.canvas.delete(self.id)

	def to_json(self):
		''' Pour sérialiser (sauvegardes)
		'''
		return funcy.project(self.__dict__, ['x','y'])

	def __repr__(self):
		return	"Marque sur %s at (%s,%s) with id %s"%(self.parent, self.x,self.y, self.id)
