# -*-coding:Utf-8 -*

import funcy

class Marque(object):
	'''Une marque représentant un point sur une video
	'''
	def __init__(self, parent, x,y):
		'''
			parent	:	une instance de Pivideo
			x,y		:	coordonnées
		'''
		self.parent = parent
		self.x = x
		self.y = y
		self.id = parent.canvas.create_bitmap(x,y,bitmap = "@marque.xbm", tags = "marques", foreground = "blue")

	def __del__(self):
		''' Destructeur
		'''
		self.parent.canvas.delete(self.id)

	def to_json(self):
		''' Pour sérialiser (sauvegardes)
		'''
		return funcy.project(self.__dict__, ['x','y'])

	def __repr__(self):
		return	"Marque sur %s at (%s,%s) with id %s"%(self.parent, self.x,,self.y, self.id)
