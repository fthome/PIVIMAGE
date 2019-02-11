# coding: utf8
from __future__ import unicode_literals
'''
	Une barre de boutons (Frame tkinter)
'''

try:
	import tkinter
except:
	import Tkinter as tkinter

class PiButtonsBarre(tkinter.Frame):
	'''Une barre de boutons
	'''

	def __init__(self, parent, direction = tkinter.HORIZONTAL, **kwargs):
		'''Initialisation
			parent		:	tkinter parent
			app			:	main app
			direction	:	PiButtonsBarre.horizontal || PiButtonsBarre.vertical
		'''
		tkinter.Frame.__init__(self, parent, padx=5, **kwargs)
		self.direction = direction
		self.buttons = []


	def add(self, button):
		'''Ajoute un bouton
		'''
		self.buttons.append(button)
		if self.direction == tkinter.HORIZONTAL:
			button.grid(row = 0, column = len(self.buttons), padx = 5, pady = 5)
		else:
			button.grid(column = 0, row = len(self.buttons), padx = 5, pady = 5, sticky = 'nw')
