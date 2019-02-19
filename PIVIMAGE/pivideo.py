# coding: utf8
from __future__ import unicode_literals
'''
	Frame tkinter :
		- Une video
		- Une barre de bouton de navigation
		- Le systeme de pointage

	Usage :
		videos.append(Pivideo(self.window, app=self, datas_pos = 0))
'''

try: #Python 2
	import Tkinter as tkinter
	import tkMessageBox
	import tkFileDialog
	import tkSimpleDialog
except: # Python 3
	import tkinter
	from tkinter import messagebox as tkMessageBox
	from tkinter import filedialog as tkFileDialog
	from tkinter import simpledialog as tkSimpleDialog

import ttk
import funcy
import pathlib
import PIL.Image, PIL.ImageTk
import sys
import math
import logging

#from piobject import * #Pourquoi PiObject TODO
from buttons import *
from videocapture import *
from marque import *


class Pivideo(tkinter.Frame):
	'''Un widget comprenant
		- Une video (=canevas avec image qui change)
		- Une barre de boutons (navigation images)
	'''
	nb_pivideo = 0 # Nb d'instances
	types_coordonnes = ["Cartesien","Polaire"]

	def __init__(self, parent, app, name = None, datas_pos=0, size = 0.25):
		'''Initialisation
			app			:	parent
			name
			datas_pos	:	position des données recoltées dans le tableau de données
		'''
		tkinter.Frame.__init__(self, parent)
		self.app = app
		self.datas_pos = datas_pos
		Pivideo.nb_pivideo +=1
		self.init()
		self.name = name or self.name
		self.marques = {}
		self.last_capture = None
		self.line_mesure = None
		self.size = size
		#TITRE
		self.title = tkinter.Label(self, text=self.name)
		self.title.grid()
		#VIDEO
		self.canvas = tkinter.Canvas(self, borderwidth  = 5,relief = 'groove')
		self.canvas.grid()
		self.canvas.bind("<ButtonRelease-1>", self.click_canvas)
		#PROGRESS BAR
		self.progress = tkinter.IntVar()
		self.progress_bar=ttk.Progressbar(self, orient = tkinter.HORIZONTAL, mode = "determinate", variable = self.progress)
		self.progress_bar.grid()
		self.progress_bar.bind('<ButtonRelease-1>',self.click_progress_bar)
		#BARRE DE BUTTONS
		self.button_barre = PiButtonsBarre(self, borderwidth  = 2,relief = 'groove')
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Ouvrir", command = self.bt_open_video))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "pause", command = self.bt_pause))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "play", command = self.bt_play))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "image/image", command = self.bt_image_plus))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "début", command = self.bt_goto_start))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Supp début", command = self.bt_trim_start))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Supp fin", command = self.bt_trim_end))
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Fermer", command = self.bt_close_video))
		self.button_barre.grid(sticky = 'nw', padx = 10, pady = 10)
		self.coordonnes = tkinter.StringVar(value=Pivideo.types_coordonnes[0])
		for coordonnes in Pivideo.types_coordonnes:
			self.button_barre.add(tkinter.Radiobutton(self.button_barre, variable = self.coordonnes, text=coordonnes,value = coordonnes, command = self.on_coordonnes_change))
		self.centre = None
		self.centre_lines = None

		#Echelle
		self.scale = tkinter.StringVar()
		self.set_ratio_px_mm(1)# Nb de mm par pixel
		self.scale_label = tkinter.Label(self, textvariable = self.scale)
		self.scale_label.grid()
		self.set_size(size)

	def set_size(self, size):
		'''Resize the widget
		'''
		self.canvas.config(width=self.winfo_screenwidth()*size, height = self.winfo_screenheight()*size)
		self.progress_bar.config(length = self.winfo_screenwidth()*size)
		self.size = size

	def __repr__(self):
		return "PiVideo %s"%self.name

	def init(self):
		'''initialise ou réinitialise les variables
		'''
		self.name = "Video%s"%self.nb_pivideo
		self.mode = "stop"
		self.filename = None
		self.start_frame = 0
		self.offset = 0
		self.end_frame = None
		self.photo = None
		self.image = None
		self.video = None

	def reinit(self):
		'''réinitialise tous
		'''
		self.delete_marques()
		self.init()
		self.title.config(text=self.name)
		self.canvas.delete("image")
		self.progress.set(0)


	def open_video(self, filename):
		'''Ouvre un fichier video et affiche la première image
		'''
		if filename:
			self.filename = filename
		else:
			filename = self.filename
		try:
			self.video = PiVideoCapture(filename)
			self.canvas.config(width= int((float(self.canvas['height']) * self.video.width) / self.video.height))
			self.update_video()
			self.title.config(text=pathlib.Path(filename.encode(sys.getfilesystemencoding())).name)
			self.update_progress_bar()
			for video in self.app.videos[1:]:
				if video.video and self.app.videos[0].video.get_virtual_fps() > video.video.get_virtual_fps():
					tkMessageBox.showwarning("Video","Attention, la video principale doit avoir le nombre d'images par secondes le plus petit de toutes les videos. Le mode capture risque d'être faussé. Inversez les videos.")
		except ValueError as e:
			logging.error(str(e))
			tkMessageBox.showerror("Ouvrir videos", "Impossible d'ouvrir le fichier.")
			self.video = None

	def update_video(self):
		'''Met à jour l'affichage de la video (avec le frame suivant)
		'''
		ret, frame = self.video.get_frame()
		if ret and (not self.end_frame or self.video.get_frame_no() < self.end_frame):
			self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame).resize((self.canvas.winfo_width(), self.canvas.winfo_height())))
			image_to_delete = self.image
			self.image = self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW, tags = "image")
			self.canvas.delete(image_to_delete)
			try:
				self.canvas.tag_lower("image","marques")
			except: # Si pas encore de marques
				pass
			try:
				self.canvas.tag_lower("image","coordonnes")
			except: # Si pas de centre
				pass
			self.update_progress_bar()
		else:
			self.mode = "stop"
			self.video.stop()

	def get_time(self, frame_no = None):
		'''Renvoie la duree entre un frame_no et le début de la video.
			Si frame_no est omis, le frame en cours est pris
		'''
		if self.start_frame:
			return self.video.get_time(frame_no) - self.video.get_time(self.start_frame)
		else:
			return self.video.get_time(frame_no)

	def get_relative_time(self, frame_no =None):
		''' renvoie la durée entre un frame_no et le début de la capture
		'''
		return self.get_time(frame_no) - self.offset

	def bt_open_video(self):
		'''Ouvre une boite de dialogue pour selectionner fichier et ouvre la video
		'''
		file = tkFileDialog.askopenfilename(title = "Selectionner la vidéo à ouvrir",initialdir = self.app.path)
		if file:
			self.open_video(file)
			self.app.path = pathlib.Path(file.encode(sys.getfilesystemencoding())).parent

	def bt_close_video(self):
		'''Ferme la video et redimensionne les autres videos
		'''
		self.app.close_video(self)

	def update_progress_bar(self):
		'''Met à jour la barre de progression
		'''
		self.progress_bar.config(maximum = (self.end_frame or self.video.frame_count) - self.start_frame)
		self.progress.set(self.video.get_frame_no() - self.start_frame)


	def bt_pause(self):
		''' Met en pause la video
		'''
		self.mode = "pause"

	def bt_play(self):
		''' Play the video
		'''
		if self.video:
			self.mode = "play"
			self.update_video()

	def bt_image_plus(self):
		'''Avance d'une image
		'''
		if self.video:
			self.mode = "pause"
			self.update_video()

	def bt_goto_start(self):
		'''Stop la video et reviens au début
		'''
		self.mode = "stop"
		if self.start_frame == 0:
			self.video.stop()
		else:
			self.app.window.config(cursor="wait")
			self.video.goto_frame(self.start_frame - 1)
			self.app.window.config(cursor="")
		self.update_video()


	def bt_trim_start(self):
		'''Definit la positionn actuelle comme étant le début de la video
		'''
		frame_no = self.video.get_frame_no()
		if frame_no == self.start_frame:
			if tkMessageBox.askokcancel("Définition du début de la video", "Réinitialiser le début de la vidéo?"):
				frame_no = 0
		self.start_frame = frame_no
		self.update_progress_bar()

	def bt_trim_end(self):
		'''Definit la positionn actuelle comme étant la fin de la video
		'''
		frame_no = self.video.get_frame_no()
		if frame_no == self.start_frame:
			if tkMessageBox.askokcancel("Définition de la fin de la video", "Réinitialiser la fin de la vidéo?"):
				frame_no = None
		self.end_frame = frame_no
		self.update_progress_bar()

	def click_progress_bar(self, evt):
		''' Gestionnaire d'evenement click sur progress_bar
			Déplace la vidéo vers le point clické
		'''
		if self.video:
			self.progress_bar.config(cursor="wait")
			self.video.goto_frame(int(self.start_frame + float(evt.x) / evt.widget.winfo_width() * ((self.end_frame or self.video.frame_count)-self.start_frame)))
			self.app.window.config(cursor="")
			self.update_video()
			self.progress_bar.config(cursor="")

	def click_canvas(self, evt):
		''' Gestionnaire d'evenement click sur la video
			Si mode enregistrement,
				- enregistre la position du point
				- trace un point
			Si mode mesure,
				-
				-
		'''
		# MODE CAPTURE
		if self.app.capture != None and self.app.videos[self.app.capture] == self and self.video:
			#Ajoute les données au tableau
			frame_time = int(round(self.get_relative_time()))
			self.app.datas.add(frame_time, [0,0]*self.datas_pos + self.get_coordonnes(evt))
			#Ajoute une marques
			self.marques[frame_time]=Marque(self, evt.x, evt.y)
			self.last_capture = (evt.x, evt.y)
			# Avance d'un frame (dans le fps de la video maitre)
			if self.datas_pos != 0: # Si pas video maitre : on avance jusque la frame précédente correspondant au temps de la video 0
				self.video.goto_time(self.app.videos[0].get_relative_time() + self.offset + ( self.video.get_time(self.start_frame) if self.start_frame else 0) - 1000.0 / self.video.get_virtual_fps())
			self.update_video()
			#rend active la PiVideo suivante qui a une video ouverte
			self.app.capture +=1
			self.app.capture %=len(self.app.videos)
			while not self.app.videos[self.app.capture].video:
				self.app.capture +=1
				self.app.capture %=len(self.app.videos)
			self.canvas.config(cursor = "")
			self.app.videos[self.app.capture].move_mouse_at_last_capture()
		# MODE MESURE
		if self.app.mode == 'mesure':
			if not self.line_mesure:
				#1er point de la mesure
				self.line_mesure = self.canvas.create_line(evt.x, evt.y,evt.x+1,evt.y+1, arrow = 'both')
				self.canvas.bind('<Motion>', self.on_motion_mesure)
				#TODO : faire bind sur echap pour annuler le mode
			else:
				#2nd point de la mesure
				[x0,y0,x1,y1] = self.canvas.coords(self.line_mesure)
				distance_px = ((x0-x1)**2 + (y0-y1)**2)**0.5
				distance_mm = tkSimpleDialog.askfloat("Convertir des pixels en mm", "La distance mesurée est de %d pixels.\n Quelle est la distance réelle en mm?"%distance_px, minvalue = 0)
				if distance_mm:
					self.set_ratio_px_mm( distance_mm / distance_px)
				self.app.stop_mode()
		#MODE SELECTION CENTRE COORDONNES POLAIRE
		if self.app.mode == 'centre' and self.coordonnes.get() == Pivideo.types_coordonnes[1]:
			self.centre = (evt.x, evt.y)
			self.draw_coordonnes()
			self.app.datas.change_datas(self.datas_pos, callback = self.to_polar, col_names = self.get_col_names())
			self.app.stop_mode()
			self.canvas.config(cursor = "")


	def stop_mesure(self):
		''' Sort du mode mesure
		'''
		self.canvas.unbind('<Motion>')
		self.canvas.delete(self.line_mesure)
		self.line_mesure = None

	def on_motion_mesure(self, evt):
		''' Pour le mode mesure, déplace la flèche selon la souris
		'''
		if self.line_mesure:
			coords = self.canvas.coords(self.line_mesure)[0:2]
			coords += [evt.x,evt.y]
			self.canvas.coords(self.line_mesure, *coords)

	def move_mouse_at_last_capture(self):
		'''Déplace la souris à l'emplacement de la dernière capture
		et change le curseur en "main"
		'''
		if self.last_capture:
			self.canvas.event_generate('<Motion>', warp=True, x=self.last_capture[0], y=self.last_capture[1])
		self.canvas.config(cursor = "tcross")

	def delete_marques(self, frame_time = None, id = None):
		'''Supprimer des marques
			frame_time 		:		Si None		: supprime toutes les marques
									Si valeur	: supprime 1 marque
									Si list		: supprime la liste
			id				:		numero d'item
		'''
		if id:
			frame_time = self.get_frame_time_marque(id)
		if frame_time is None:
			marques = self.marques.keys()
		elif not isinstance(frame_time ,list):
				marques = [frame_time]
		for frame in marques:
			#self.canvas.delete(self.marques[frame])
			self.marques.pop(frame)
			self.app.datas.delete(frame,self.datas_pos)
		self.last_capture = None

	def get_frame_time_marque(self, id):
		''' Renvoie le frame_time d'une marque selon son id
		'''
		for frame_time, marque in self.marques.iteritems():
			if marque.id == id:
				return frame_time

	def to_json(self):
		''' Pour sérialiser (sauvegardes)
		'''
		return funcy.project(self.__dict__, ['datas_pos', 'name', 'marques','filename','start_frame', 'offset', 'end_frame', 'ratio_px_mm','centre'])

	def load_json(self, state):
		'''Load state into App object
			qui contient  ['datas_pos', 'name', 'marques','filename','start_frame', 'offset', 'end_frame', 'ratio_px_mm']
		'''
		self.datas_pos = state['datas_pos']
		self.name = state['name']
		self.delete_marques()
		for frame_time, marque in state['marques'].iteritems():
			self.marques[frame_time] = Marque(self, marque['x'], marque['y'])
		self.filename = state['filename']
		self.start_frame = state['start_frame']
		self.offset = state['offset']
		self.end_frame = state['end_frame']
		self.set_ratio_px_mm(state['ratio_px_mm'])
		self.open_video(self.filename)
		self.bt_goto_start()
		self.centre = state['centre']
		self.centre_lines=[]
		if self.centre:
			self.coordonnes.set(Pivideo.types_coordonnes[1])
			self.app.mode = 'centre'
			self.draw_coordonnes()


	def set_ratio_px_mm(self, ratio_px_mm):
		'''Update the scale label
		'''
		self.ratio_px_mm = ratio_px_mm
		self.scale.set("Echelle : 1 pixel = %f mm"%(self.ratio_px_mm))

	def on_coordonnes_change(self):
		'''Au changement de coordonnés (cartesien - polaire)
		'''
		if self.coordonnes.get() == Pivideo.types_coordonnes[1]: # Si Polaire
			if tkMessageBox.askokcancel("Coordonnées polaires", "Pointer le centre du système de coordonnées."):
				self.app.stop_mode()
				self.app.mode = 'centre'
				self.canvas.config(cursor = "crosshair ")
			else:
				self.coordonnes.set(Pivideo.types_coordonnes[0])
		else: # Si coordonnés cartesien
			#if self.app.datas.is_empty() or tkMessageBox.askokcancel("Coordonnées cartésiens", "Attention les captures précédentes seront effacées."):
			self.app.datas.change_datas(self.datas_pos, callback = self.to_cartesien, col_names = self.get_col_names())
			self.centre = None
			self.draw_coordonnes()

	def to_cartesien(self, r, a):
		'''Convert polar to cartesien
		'''
		return (r*math.cos(a) + self.centre[0]*self.ratio_px_mm, r*math.sin(a) + self.centre[1]*self.ratio_px_mm)

	def to_polar(self, x, y):
		'''Convert cartesion to polar
		'''
		x = x - self.centre[0]*self.ratio_px_mm
		y = y - self.centre[1]*self.ratio_px_mm
		return [(x*x+y*y)**0.5,math.atan2(y,x)*180/math.pi]


	def draw_coordonnes(self):
		'''Dessine (ou detruit) les lignes de coordonnes
		'''
		if self.centre_lines:
			for line in self.centre_lines:
				self.canvas.delete(line)
		self.centre_lines=[]
		if self.centre:
			self.centre_lines.append(self.canvas.create_line(self.centre[0],0,self.centre[0],self.canvas.winfo_reqheight(),tags = "coordonnes"))
			self.centre_lines.append(self.canvas.create_line(0,self.centre[1],self.canvas.winfo_reqwidth(),self.centre[1],tags = "coordonnes"))

	def get_col_names(self):
		'''Renvoie un tuple de 2 composé du nom des colonnes de données
		'''
		indice = str(self.datas_pos+1)
		if self.coordonnes.get()==Pivideo.types_coordonnes[1]: # Si Polaire
			return "R" + indice, "A" + indice
		else:
			return "X" + indice, "Y" + indice

	def get_coordonnes(self, evt):
		''' Retourne une list [x,y] ou [r,angle] mis à l'echele
		'''
		if self.coordonnes.get() == Pivideo.types_coordonnes[0]:#Cartesien
			return [evt.x*self.ratio_px_mm,(self.canvas.winfo_reqheight()-evt.y)*self.ratio_px_mm]
		else:
			x = (evt.x - self.centre[0])*self.ratio_px_mm
			y = -(evt.y - self.centre[1])*self.ratio_px_mm
			return [(x*x+y*y)**0.5,math.atan2(y,x)*180/math.pi]
