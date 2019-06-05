# coding: utf8
from __future__ import unicode_literals
from __future__ import absolute_import
from six import itervalues

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
import json
import funcy
import pyperclip as clipboard
import logging

from .piencoder import *
from .pivideo import *
from .datas import *
from .version import __version__

class App(object):
	'''Une application PIVIMAGE
		PIerron
		VIdeos
		Multiples
		iMAge par image
	'''
	images_path = pathlib.Path("./PIVIMAGE/images")
	vitesse_max = 15

	def __init__(self, name="PIVIMAGE", path = None):
		'''Initialisation
			name		:	Nom de l'application
		'''
		logging.debug("Création App instance %s"%self)
		self.window = tkinter.Tk()
		self.name = name
		self.init()
		self.set_title()
		if path:
			self.path = path
		else:
			self.path = os.path.expanduser('~')

		#LES BOUTONS A GAUCHE
		self.button_barre = PiButtonsBarre(self.window, borderwidth  = 2,relief = 'groove', direction = tkinter.VERTICAL)
		self.button_barre.grid(column = 0, row = 0)
		self.button_mesure = tkinter.Button(self.button_barre, text = "Echelle", command = self.bt_ruler)
		self.button_barre.add(self.button_mesure)
		self.button_capture = tkinter.Button(self.button_barre, text = "Mode Capture", command = self.bt_capture_datas)
		self.button_barre.add(self.button_capture)
		self.button_rubber = tkinter.Button(self.button_barre, text = "Supp points", command = self.bt_rubber)
		self.button_barre.add(self.button_rubber)
		self.button_barre.add(tkinter.Button(self.button_barre, text = "Supp tous les points", command = self.bt_rubber_all))
		self.vitesse = tkinter.IntVar(value=10)
		self.button_barre.add(tkinter.Scale(self.button_barre, label = "Vitesse de lecture", from_ = 1, to_ = App.vitesse_max, resolution = 1, orient = 'horizontal', length = 150, variable = self.vitesse))

		#LES VIDEOS
		self.video_frame = tkinter.Frame(self.window, borderwidth  = 2,relief = 'groove')
		self.video_frame.grid(column = 1, row = 0,rowspan = 2, sticky = tkinter.N)
		self.videos = []
		self.videos.append(Pivideo(self.video_frame, app=self, datas_pos = 0, size = 0.75))
		self.videos[0].grid( column = 0, row = 0, sticky  = tkinter.N, padx = 10, pady = 5)

		#LES DONNES
		nb_video = len(self.videos)
		self.window.update_idletasks()
		height = self.window.winfo_reqheight() - self.button_barre.winfo_reqheight() - 50
		pady = self.videos[0].title.winfo_reqheight() + 10
		self.datas = PiDatas(self.window,1,col_names = ["Tps(ms)"], height = height)
		self.datas.grid(column=0, row = 1, padx = 10, pady = pady, rowspan = 2)#, sticky = 'nw')
		for video in self.videos:
			self.datas.add_video(list(video.get_col_names()))

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
		menuVideo.add_command(label = "Ouvrir video...", command = self.menu_open_video)
		menuVideo.add_command(label = "Ajout video...", command = self.menu_ajout_video)
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

	def add_video(self):
		'''Add a new video and resize all of them
		'''
		nb_video = len(self.videos)+1
		if nb_video > 4:
			tkMessageBox.showerror("Ouvrir videos", "Impossible d'ajouter une 5ème video.")
		else:
			video = Pivideo(self.video_frame, app=self, datas_pos = nb_video-1)
			self.videos.append(video)
			self.resize_videos()
			self.datas.add_video(list(video.get_col_names()))

	def close_video(self, video, confirm = True):
		'''Ferme une video
		'''
		if (not confirm) or tkMessageBox.askokcancel("Fermer la vidéo","Voulez vous fermer la vidéo? S'il y a des données elles seront effacées."):
			self.datas.remove_video(video.datas_pos)
			self.videos.remove(video)
			video.destroy()
			self.resize_videos()

	def resize_videos(self):
		''' Redimensionne les videos (après un ajout ou une suppression)
		'''
		nb_video = len(self.videos)
		if nb_video == 1:
			size = 0.75
			nb_col = 1
			nb_lig = 1
		elif nb_video == 2:
			size = 0.33
			nb_col = 1
			nb_lig = 2
		elif nb_video in [3,4]:
			size = 0.33
			nb_col = 2
			nb_lig = 2
		for video in self.videos:
			video.set_size(size)
		for i, video in enumerate(self.videos):
			video.grid( column = i//nb_lig, row =i%nb_lig, sticky  = tkinter.N, padx = 10, pady = 5)

	def init_datas(self):
		''' Initialise (or re-init) datas
		'''
		for video in self.videos:
			video.delete_marques()
		try:
			self.datas.destroy()
		except:
			pass
		nb_video = len(self.videos)
		self.window.update_idletasks()
		height = self.window.winfo_reqheight() - self.button_barre.winfo_reqheight() - 50
		pady = self.videos[0].title.winfo_reqheight() + 10
		col_names = ["t(ms)"]
		for i in range(nb_video):
			col1, col2 = self.videos[i].get_col_names()
			col_names.append(col1+str(i+1))
			col_names.append(col2+str(i+1))
		self.datas = PiDatas(self.window,1+nb_video*2,col_names = col_names, height = height)
		self.datas.grid(column=0, row = 1, padx = 10, pady = pady, rowspan = 2)#, sticky = 'nw')


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
		if self.mode == "mesure":
			self.stop_mode()
		else:
			self.stop_mode()
			self.button_mesure.config(relief = "sunken")
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
				for marque in itervalues(video.marques):
					video.canvas.tag_bind(marque.id, '<Button-1>', None)
			self.button_rubber.config(relief = "raised")
		elif self.mode == 'mesure':
			self.button_mesure.config(relief = "raised")
			for video in self.videos:
				video.stop_mesure()
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
				for marque in itervalues(video.marques):
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
				self.path = pathlib.Path(file).parent

	def menu_save_project(self):
		'''Sauve projet
		'''
		if self.project_file:
			logging.info("save_project %s"%self.project_file)
			with open(self.project_file, 'w') as f:
				f.write(json.dumps(self, cls = PiEncoder, indent = 4))
				f.close()
		else:
			self.menu_save_as_project()

	def menu_save_as_project(self):
		'''Sauve as projet
		'''
		name, path = self.get_name_path()
		file = tkFileDialog.asksaveasfilename(title = "Sauvegarder le projet sous...", defaultextension=".piv", filetypes = [("Projet PIVIMAGE","*.piv")], initialfile = name , initialdir = utils.encode(path))
		if file:
			self.project_file = file
			self.menu_save_project()
			self.path = pathlib.Path(file).parent

	def load_json(self, state):
		'''Load state into App object
			qui contient  ['videos', 'datas']
		'''
		for i, video_state in enumerate(state['videos']):
			if len(self.videos) <= i:
				self.add_video() #Si besoin, ajoute une video
			if video_state['filename']:
				self.videos[i].load_json(video_state)
		while len(self.videos) > len(state['videos']):
			logging.debug("close %s"%self.videos[-1])
			self.close_video(self.videos[-1], confirm = False) #Si besoin, ferme video inutile
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
			return pathlib.Path(self.project_file).name, pathlib.Path(self.project_file).parent
		else:
			return "MonProjet.piv", self.path

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
		logging.info("menu_export : TODO")
		tkMessageBox.showinfo("Menu Export", "Pas encore implémenté... Utiliser l'option 'Copier les valeurs'")

	def menu_quitter(self):
		'''Quitter
		'''
		if tkMessageBox.askokcancel("Quitter PIVIMAGE", "Voulez vous vraiment quitter?"):
			self.window.destroy()

	def menu_copy_datas(self):
		'''Copy data to clipboard
		'''
		clipboard.copy(str(self.datas))

	def menu_ajout_video(self):
		'''Ajoute une nouvelle video
		'''
		if self.datas.is_empty() or tkMessageBox.askokcancel("Ajout d'une vidéo", "L'ajout d'une video va effacer les données. Voulez-vous continuer?"):
			self.add_video()

	def menu_open_video(self):
		''' Ouvre une videos'''
		for video in self.videos:
			if not video.video:
				video.bt_open_video()
				break

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
		tkMessageBox.showinfo("A propos de ", \
				"PIVIMAGE version %s\n"%__version__  + \
				"License : CeCILL version 2.1\n" + \
				"https://github.com/fthome/PIVIMAGE" \
				)
