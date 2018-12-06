# -*-coding:Utf-8 -*
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

from scrframe import *
from piencoder import *
import funcy
	
class PiDatas(VerticalScrolledFrame): 
	'''Un tableau de données
	'''
	cell_format = {'relief' : 'groove', 'width' : 10}
	def __init__(self, parent, width, col_names = [], height = None): 
		'''Initialisation
			width		:	nb de colonnes (y compris l'index)
			col_names	:	tableau des noms de colonnes
		'''
		print("Création PiDatas instance", self)
		VerticalScrolledFrame.__init__(self, parent, height = height, relief = 'groove',borderwidth = 5)
		self.numberColumns = width 
		self.col_names = col_names
		for i in range(self.numberColumns):
			try:
				name = col_names[i]
			except IndexError:
				name = str(i)
			label = tkinter.Label(self.interior, text=name, **PiDatas.cell_format)
			label.grid(row = 0, column = i, padx = 0, pady = 0)
		self.lines = {} # {no_frame:[cellTemps, cellX1, cellY1, cellX2, cellY2, ...], ...}
		
	def is_empty(self):
		'''
		'''
		return not bool(self.lines)
	
	def add(self, frame_time, data):
		'''Ajoute des données
			frame_time		:	Index du tableau
			data			:	Liste [x1,y1,x2,y2,...] ou [None, None, x2,y2,...]
		'''
		data = data + ["-"] * (self.numberColumns - len(data) - 1)
		if frame_time not in self.lines:
			self.lines[frame_time] = []
			cell = tkinter.Label(self.interior, text = str(frame_time),**PiDatas.cell_format)
			self.lines[frame_time].append(cell)
			cell.grid(row = len(self.lines)+1, column = 0, padx = 0, pady = 0)
			for j in range(self.numberColumns-1): 
				cell = tkinter.Label(self.interior, text = str(data[j]),**PiDatas.cell_format) 
				self.lines[frame_time].append(cell)
				cell.grid(row = len(self.lines)+1, column = j+1, padx = 0, pady = 0)
		else:
			for j in range(len(data)):
				if data[j]:
					self.lines[frame_time][j+1].config(text=str(data[j]))
	
	def delete(self, frame_time = None, video_index = None):
		'''Delete une ou pls donnée
				frame_time		:	Si None => tous
									Si Int	=> 1
									Si list	=> la liste
		'''
		if frame_time is None:
			frames = self.lines.keys()
		elif not isinstance(frame_time,list):
			frames = [frame_time]
		else:
			frames = frame_time
		for frame in frames:
			if video_index is None:
				for cell in self.lines[frame]:
					if cell:
						cell.destroy()
				self.lines.pop(frame)
			else:
				self.lines[frame][video_index*2+1].destroy()
				self.lines[frame][video_index*2+2].destroy()
				self.lines[frame][video_index*2+1]=None
				self.lines[frame][video_index*2+2]=None
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
		''' les données au format text pour envoie clipboard par ex
		'''
		txt = ""
		for col_name in self.col_names:
			txt += col_name + "\t"
		for frame_time in sorted(self.lines.iterkeys()):
			txt += "\n"
			for cell in self.lines[frame_time]:
				txt += cell.cget('text') + "\t"
		return txt
	
	