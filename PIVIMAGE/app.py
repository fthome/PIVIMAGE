# -*-coding:Utf-8 -*

'''
	Une interface graphique pour réaliser du pointage image par image
	sur plusieurs videos (initialement deux, mais facilement extensible à n).

	Cette interface est conçue pour analyser le mouvement d'un véhicule
		Soit avec une caméra fixée au véhicule
		Soit avec une caméra fixée sur la route (ou la table si miniature)

	Exemple : www.pierron/chariot_pour_la_mecanique.html

	Usage :
		import PIVIMAGE
		App = PIVIMAGE.App("Mon application")
		App.run()

'''

try: #Python 3
	import tkinter
	from tkinter import messagebox as tkMessageBox
	from tkinter import filedialog as tkFileDialog
except: # Python 2
	import Tkinter as tkinter
	import tkMessageBox
	import tkFileDialog

import pathlib, os
#import jsonpickle
import json
import funcy
import clipboard

from piencoder import *
from pivideo import *
from datas import *
from version import __version__

class App(object):
	'''Une application PIVIMAGE
		PIerron
		VIdeos
		Multiples
		iMAge par image
	'''
	images_path = pathlib.Path("./PIVIMAGE/images")
	vitesse_max = 15

	def __init__(self, name="PIVIMAGE"):
		'''Initialisation
			name		:	Nom de l'application
		'''
		print("Création App instance",self)
		self.window = tkinter.Tk()
		self.name = name
		self.init()
		self.set_title()

		#LES BOUTONS A GAUCHE
		self.button_barre = PiButtonsBarre(self.window, borderwidth  = 2,relief = 'groove', direction = tkinter.VERTICAL)
		self.button_barre.grid(column = 0)
		self.button_mesure = tkinter.Button(self.button_barre, text = "Mesure", command = self.bt_ruler)
		self.button_barre.add(self.button_mesure)
		self.button_capture = tkinter.Button(self.button_barre, text = "Mode Capture", command = self.bt_capture_datas)
		self.button_barre.add(self.button_capture)
		self.button_rubber = tkinter.Button(self.button_barre, text = "Supp points", command = self.bt_rubber)
		self.button_barre.add(self.button_rubber)
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Supp tous les points", command = self.bt_rubber_all))
		self.vitesse = tkinter.IntVar(value=10)
		self.button_barre.add(tkinter.Scale(self.button_barre, label = "Vitesse de lecture", from_ = 1, to_ = App.vitesse_max, resolution = 1, orient = 'horizontal', length = 150, variable = self.vitesse))

		#LES VIDEOS
		self.videos = []
		self.videos.append(Pivideo(self.window, app=self, datas_pos = 0))
		self.videos[0].grid( column = 1, row = 0, padx = 10, pady = 10)
		self.videos.append(Pivideo(self.window, app=self, datas_pos = 1))
		self.videos[1].grid( column = 1, row =1, padx = 10, pady = 10)

		#LES DONNES
		self.window.update_idletasks()
		height = 0
		for video in self.videos:
			height += video.winfo_height()
		pady = self.videos[0].title.winfo_reqheight() + 10
		self.datas = PiDatas(self.window,5,col_names = ["Temps (ms)","X1","Y1","X2","Y2"], height = height)
		self.datas.grid(column=2, row = 0, padx = 10, pady = pady, rowspan = 2, sticky = 'nw')

		#LES MENUS
		mainmenu = tkinter.Menu(self.window)
		self.window['menu'] = mainmenu

		menuFichier = tkinter.Menu(mainmenu,tearoff =0)
		menuFichier.add_command(label = "Nouveau projet", command = self.menu_new_project)
		menuFichier.add_command(label = "Ouvrir projet", command = self.menu_open_project)
		menuFichier.add_command(label = "Sauve projet", command = self.menu_save_project)
		menuFichier.add_command(label = "Sauve sous projet", command = self.menu_save_as_project)
		menuFichier.add_command(label = "Exporter...", command = self.menu_export)
		menuFichier.add_command(label = "Quitter", command = self.menu_quitter)
		mainmenu.add_cascade(label = "Fichier", menu = menuFichier)

		menuEdition = tkinter.Menu(mainmenu,tearoff =0)
		menuEdition.add_command(label = "Copier les valeurs", command = self.menu_copy_datas)
		mainmenu.add_cascade(label = "Edition", menu = menuEdition)

		menuVideo = tkinter.Menu(mainmenu,tearoff =0)
		menuVideo.add_command(label = "Ouvrir video 1", command = self.menu_open_video1)
		menuVideo.add_command(label = "Ouvrir video 2", command = self.menu_open_video2)
		menuVideo.add_command(label = "Informations", command = self.menu_informations)
		mainmenu.add_cascade(label = "Video", menu = menuVideo)

		menuAide = tkinter.Menu(mainmenu,tearoff =0)
		menuAide.add_command(label = "A propos", command = self.menu_about)
		mainmenu.add_cascade(label = "Aide", menu = menuAide)


	def run(self):
		'''Main : run forever
		'''
		self._lecture()
		self.window.mainloop()

	def init(self):
		self.project_file = None
		self.capture = None #None si pas de capture, sinon, l'index de la vidéo à capturer
		self.mode = None # None | 'capture' | 'rubber'

	def reinit(self):
		for video in self.videos:
			video.reinit()
		self.datas.delete()
		self.stop_mode()
		self.init()
		self.set_title()

	def set_title(self):
		name = None
		if self.project_file:
			name = pathlib.Path(self.project_file).name
		self.window.title(self.name + " - " + (name or "Nouveau projet"))


	def _lecture(self):
		'''Lecture des videos si en mode "play"
		'''
		for video in self.videos:
			if video.mode == "play":
				video.update_video()
		self.window.after((App.vitesse_max - self.vitesse.get())*20 + 2, self._lecture)

	def bt_ruler(self):
		'''Demande de mesurer une distance pour calibrer
		'''
		print("Mesurer...")
		self.stop_mode()
		self.mode = 'mesure'

	def bt_capture_datas(self):
		'''Lance le mode capture de points
		'''
		if self.capture!=None:
			self.stop_mode()
		else:
			self.stop_mode()
			init = True
			if not self.datas.is_empty():
				reponse = tkMessageBox.askyesnocancel("Capture","Voulez vous supprimer la capture précédente?")
				if reponse is None:
					return None
				if reponse :
					for video in self.videos:
						video.delete_marques()
					self.datas.delete()
				else:
					init = False
			if init:
				for video in self.videos:
					if video.video:
						video.offset = video.get_time()
			self.capture = 0
			self.mode = 'capture'
			self.button_capture.config(relief = "sunken")
			self.videos[0].move_mouse_at_last_capture()

	def stop_mode(self):
		''' Arrêt le mode en cours ('capture' | 'rubber')
		'''
		if self.mode == 'capture':
			self.capture = None
			self.mode = None
			self.button_capture.config(relief = "raised")
		elif self.mode =='rubber':
			for video in self.videos:
				for marque in video.marques.itervalues():
					video.canvas.tag_bind(marque.id, '<Button-1>', None)
			self.button_rubber.config(relief = "raised")
		for video in self.videos:
				video.canvas.config(cursor = "")
		self.mode = None

	def bt_rubber(self):
		'''Pass en mode gommage
		'''
		if self.mode != 'rubber':
			self.stop_mode()
			self.mode = 'rubber'
			self.button_rubber.config(relief = "sunken")
			for video in self.videos:
				for marque in video.marques.itervalues():
					video.canvas.tag_bind(marque.id, '<Button-1>', self.delete_marque)
		else:
			self.stop_mode()

	def delete_marque(self, event):
		'''Supprime la marque liée à event
		'''
		video = event.widget._nametowidget(event.widget.winfo_parent())
		id = event.widget.find_closest(event.x, event.y)[0]
		video.delete_marques(id=id)

	def bt_rubber_all(self):
		'''Supprime toutes les marques
		'''
		for video in self.videos:
			video.delete_marques()
		self.datas.delete()

	def menu_new_project(self):
		'''Nouveau projet
		'''
		if self.is_started():
			if tkMessageBox.askokcancel("Nouveau projet","Créer un nouveau projet sans sauvegarder le précédent?"):
				self.reinit()


	def menu_open_project(self):
		'''Ouvrir projet
		'''
		if not self.is_started() or tkMessageBox.askokcancel("Ouvrir un projet","Ouvrir un projet sans sauvegarder le précédent?"):
			name, path = self.get_name_path()
			file = tkFileDialog.askopenfilename(title = "Ouvrir un projet", defaultextension=".piv", filetypes = [("Projet PIVIMAGE","*.piv")], initialfile = name , initialdir = path)
			if file:
				with open(file, 'r') as f:
					self.load_json(json.loads(f.read()))
					f.close()

	def menu_save_project(self):
		'''Sauve projet
		'''
		if self.project_file:
			print("save_project %s"%self.project_file)
			#jsonpickle.set_preferred_backend('json')
			#jsonpickle.set_encoder_options('json', indent = 4)
			with open(self.project_file, 'w') as f:
				#f.write(jsonpickle.encode(self))
				f.write(json.dumps(self,cls = PiEncoder, indent = 4))
				f.close()
		else:
			self.menu_save_as_project()

	def menu_save_as_project(self):
		'''Sauve as projet
		'''
		name, path = self.get_name_path()
		file = tkFileDialog.asksaveasfilename(title = "Sauvegarder le projet sous...", defaultextension=".piv", filetypes = [("Projet PIVIMAGE","*.piv")], initialfile = name , initialdir = path)
		if file:
			self.project_file = file
			self.menu_save_project()

	def load_json(self, state):
		'''Load state into App object
			qui contient  ['videos', 'datas']
		'''
		for i, video_state in enumerate(state['videos']):
			if video_state['filename']:
				self.videos[i].load_json(video_state)
		self.datas.load_json(state['datas'])
		self.init()
		self.set_title()

	def to_json(self):
		''' Pour sérialiser (sauvegardes)
		'''
		return funcy.project(self.__dict__, ['videos', 'datas'])

	def get_name_path(self):
		'''Renvoie un tuple avec nom et path à sauvegarder ou ouvrir
		'''
		if self.project_file:
			return pathlib.Path(self.project_file).name, pathlib.Path(self.project_file).path
		else:
			return "MonProjet.piv", os.path.expanduser('~')

	def is_started(self):
		''' Renvoie True si le projet est débuté (existance d'au moins une video ouverte)
		'''
		for video in self.videos:
			if video.video:
				return True
		return False

	def menu_export(self):
		'''Export données
		'''
		print("menu_export")

	def menu_quitter(self):
		'''Quitter
		'''
		if tkMessageBox.askokcancel("Quitter PIVIMAGE", "Voullez vous vraiment quitter?"):
			self.window.destroy()

	def menu_copy_datas(self):
		'''Copy data to clipboard
		'''
		clipboard.copy(str(self.datas))

	def menu_open_video1(self):
		'''Ouvre video1
		'''
		self.videos[0].bt_open_video()

	def menu_open_video2(self):
		'''Ouvre video2
		'''
		self.videos[1].bt_open_video()


	def menu_informations(self):
		'''Information sur les videos
		'''
		txt = u""
		i = 1
		for video in self.videos:
			txt += u"Information Vidéo%s :\n"%i
			txt += "%s\n"%video.video
			i += 1
		tkMessageBox.showinfo(u"Informations vidéos", txt)

	def menu_about(self):
		'''A propos
		'''
		tkMessageBox.showinfo("A propos de ", "PIVIMAGE version %s"%__version__)
