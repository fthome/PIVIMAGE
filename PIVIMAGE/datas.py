# coding: utf8
from __future__ import unicode_literals
from __future__ import absolute_import
'''
	Un Frame tkinter
		qui représente des données classées sous forme de tableau

	Usage :
			datas = PiDatas(self.window,width=5,col_names = ["Temps (ms)","X1","Y1","X2","Y2"], height = height)
			datas.add(frame_time, [x1,y1,x2,y2,...])
			datas.delete(frame_time, video_index)
'''
try:
	import tkinter
except:
	import Tkinter as tkinter

from .scrframe import *
from .piencoder import *
import funcy
import logging

class PiDatas(VerticalScrolledFrame):
	'''Un tableau de données
	'''
	cell_format = {'relief' : 'groove', 'width' : 6}
	str_format = "%.2f"
	separateur = "," #TODO paramètrage

	def __init__(self, parent, width, col_names = [], height = None):
		'''Initialisation
			width		:	nb de colonnes (y compris l'index)
			col_names	:	tableau des noms de colonnes
		'''
		VerticalScrolledFrame.__init__(self, parent, height = height, relief = 'groove',borderwidth = 5)
		self.numberColumns = width
		self.col_names = col_names
		self.entetes = []
		for i in range(self.numberColumns):
			try:
				name = col_names[i]
			except IndexError:
				name = str(i)
			label = tkinter.Label(self.interior, text=name, **PiDatas.cell_format)
			label.grid(row = 0, column = i, padx = 0, pady = 0)
			self.entetes.append(label)
		self.lines = {} # {no_frame:[cellTemps, cellX1, cellY1, cellX2, cellY2, ...], ...}

	def is_empty(self):
		'''
		'''
		return not bool(self.lines)

	def remove_datas(self, datas_pos):
		'''Supprime 2 colonnes
		'''
		#Suppression des entetes
		for row in [datas_pos*2+2,datas_pos*2+1]:
			logging.debug("Remove colonne n° %s"%row)
			self.entetes[row].destroy()
			del self.entetes[row]
			self.col_names.pop(row)
		#Supression des Coordonnées
		self.delete(None, datas_pos)
		#
		self.numberColumns -=2

	def add_video(self, col_names=[]):
		'''Insert new rows for a video
			return : video_index
		'''
		logging.debug("Add video with col_names = %s"%col_names)
		for col in range(self.numberColumns, self.numberColumns + len(col_names)):
			logging.debug("Colonne index : %s"%col)
			try:
				name = col_names[col-self.numberColumns]
			except IndexError:
				name = str(col)
			self.col_names.append(name)
			logging.debug("Colonne name : %s"%name)
			label = tkinter.Label(self.interior, text=name, **PiDatas.cell_format)
			label.grid(row = 0, column = col, padx = 0, pady = 0)
			self.entetes.append(label)
			for frame_no in self.lines:
				logging.debug("Add capture for frame_no : %s"%frame_no)
				cell = tkinter.Label(self.interior, text = "-",**PiDatas.cell_format)
				label.grid(row = 0, column = col, padx = 0, pady = 0)
				self.lines[frame_no].append(cell)
		self.numberColumns += len(col_names)
		return (self.numberColumns - 1)/2


	def add(self, frame_time, data):
		'''Ajoute des données
			frame_time		:	Index du tableau
			data			:	Liste [x1,y1,x2,y2,...] ou [None, None, x2,y2,...]
		'''
		data = data + [None] * (self.numberColumns - len(data) - 1)
		if frame_time not in self.lines:
			self.lines[frame_time] = []
			cell = tkinter.Label(self.interior, text = str(frame_time),**PiDatas.cell_format)
			self.lines[frame_time].append(cell)
			cell.grid(row = len(self.lines)+1, column = 0, padx = 0, pady = 0)
			for j in range(self.numberColumns-1):
				if isinstance(data[j],int):
					text = str(data[j])
				elif isinstance(data[j],float):
					text = "%.1f"%data[j]
				else:
					text = data[j]
				cell = tkinter.Label(self.interior, text = text,**PiDatas.cell_format)
				self.lines[frame_time].append(cell)
				cell.grid(row = len(self.lines)+1, column = j+1, padx = 0, pady = 0)
		else:
			for j in range(len(data)):
				if data[j]:
					if isinstance(data[j],int):
						text = str(data[j])
					elif isinstance(data[j],float):
						text = PiDatas.str_format%data[j]
					else:
						text = data[j]
					self.lines[frame_time][j+1].config(text=text)

	def delete(self, frame_time = None, datas_pos = None):
		'''Delete une ou pls donnée
				frame_time		:	Si None => tous
									Si Int	=> 1
									Si list	=> la liste
		'''
		if frame_time is None:
			frames = list(self.lines.keys())
		elif not isinstance(frame_time,list):
			frames = [frame_time]
		else:
			frames = frame_time
		logging.debug("Données à détruire : %s"%frames)
		for frame in frames:
			if datas_pos is None:
				for cell in self.lines[frame]:
					if cell:
						cell.destroy()
				self.lines.pop(frame)
			else:
				for i in [datas_pos*2+1, datas_pos*2+2]:
					if self.lines[frame][i]:
						self.lines[frame][i].destroy()
						self.lines[frame][i]=None
				is_active = False
				for cell in self.lines[frame][1:]:
					if cell and cell["text"]!="-":
						is_active = True
				if not is_active:
					for cell in self.lines[frame]:
						if cell:
							cell.destroy()
					self.lines.pop(frame)

	def to_json(self):
		''' Pour sérialiser (sauvegardes)
		'''
		state = funcy.project(self.__dict__, ['numberColumns', 'col_names'])
		#Pour les données, on remplace les cellules par la valeur des cellules
		state['lines'] = {}
		for frame_time, line in self.lines.iteritems():
			state['lines'][frame_time] = []
			for cell in line[1:]:
				state['lines'][frame_time].append(cell["text"])
		return state

	def load_json(self, state):
		'''Load state into App object
			qui contient  ['numberColumns', 'col_names', 'lines'])
		'''
		self.numberColumns = state['numberColumns']
		self.col_names = state['col_names']
		for frame_time, line in state['lines'].iteritems():
			self.add(frame_time, line)


	def __str__(self):
		''' les données au format text pour envoie clipboard
		'''
		txt = u''
		for col_name in self.col_names:
			txt += col_name + u"\t"
		for frame_time in sorted(iter(self.lines)):
			txt += u"\n"
			for cell in self.lines[frame_time]:
				txt += str(cell.cget('text')).replace('.',self.separateur) + u"\t"
		return txt

	def change_datas(self, datas_pos, callback = None, col_names = []):
		'''Transforme les données
			datas_pos	:	0 pour la 1er video, 1 ...
			col_names	:	["Xn", "Yn"] ou ["Rn", "An"]
			callback	:	fonction avec deux arguments (X,Y), les données associés à datas_pos qui retourne un tuple
		'''
		logging.debug("Change datas n° %s with col_names = %s"%(datas_pos, col_names))
		index1 = datas_pos*2+1
		index2 = datas_pos*2+2
		#entetes
		#try:
		print(col_names)
		self.col_names[index1]=col_names[0]
		self.entetes[index1].config(text=col_names[0])
		self.col_names[index2]=col_names[1]
		self.entetes[index2].config(text=col_names[1])
		#except IndexError:
		#	pass
		#Données
		if callback:
			for frame_no in self.lines:
				line = self.lines[frame_no]
				val1, val2 = callback(float(line[index1].cget('text')),float(line[index2].cget('text')))
				line[index1].config(text=PiDatas.str_format%val1)
				line[index2].config(text=PiDatas.str_format%val2)
