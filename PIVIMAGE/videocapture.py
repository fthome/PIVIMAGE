# coding: utf8
from __future__ import unicode_literals

'''
	Base sur opencv2,
	Une video que l'on lit image par image

	Usage:
			video = PiVideoCapture(filename)
			ret, frame = video.get_frame()
			photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
			my_canvas.create_image(0, 0, image = photo, anchor = tkinter.NW, tags = "image")
'''
import cv2
import funcy
import sys
import logging

class PiVideoCapture(object):
	''' Une video
	'''
	props = ["CAP_PROP_POS_MSEC", "CAP_PROP_POS_FRAMES", "CAP_PROP_POS_AVI_RATIO", "CAP_PROP_FORMAT", "CAP_PROP_MODE"]

	def __init__(self, video_source=0):
		self.video_source = video_source
		self.frames = {}
		self.vid = None
		self.open()
		self.calc_real_fps()


	def open(self):
		'''Open the video source
		'''
		logging.info("Open video %s"%self.video_source)
		try: # Python 3
			self.vid = cv2.VideoCapture(self.video_source)
		except:
			try: # Python 2.7
				self.vid = cv2.VideoCapture(self.video_source.encode(sys.getfilesystemencoding()))
			except:
				pass
		if not self.vid or not self.vid.isOpened():
			raise ValueError("Unable to open video source", self.video_source)
		self.last_frame = None
		 # Get video source width and height and more
		self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.fps = self.vid.get(cv2.CAP_PROP_FPS)
		self.fourcc = self.vid.get(cv2.CAP_PROP_FOURCC)
		self.frame_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
		logging.info("%s Opened. Size : (%s,%s) - FPS : %s - Codec : %s - Nb of frames : %s"%(self.video_source, self.width, self.height, self.fps, self.fourcc, self.frame_count))
		self.virtual_frame_no = 0

	 # Release the video source when the object is destroyed
	def __del__(self):
		if self.vid and self.vid.isOpened():
			 self.vid.release()

	def __getstate__(self):
		''' Pour sérialiser (sauvegardes)
		'''
		return funcy.project(self.__dict__, ['video_source', 'frames', 'width','height','fps','fourcc','frame_count', 'virtual_frame_no'])
	def __set_state__(self, state):
		'''Pour désérialiser
		'''
		print("videocapture.__set_state__() : %s"%state)

	def __str__(self):
		'''Infos sur la video
		'''
		repr = u"Fichier : %s\n"%self.video_source #TODO : pb unicod
		repr += u"Dimensions : %s - %s pixels\n"%(self.width, self.height)
		repr += u"Codec (fourcc) : %s\n"%self.fourcc
		repr += u"FPS : %s\n"%self.fps
		repr += u"Nb de Frames : %s\n"%self.frame_count
		repr += u"FPS reél (images distinctes) : %s\n"%self.get_virtual_fps()
		repr += u"Durée : %s secondes\n"% (int(round(self.frame_count/self.fps)))
		return repr

	def get_frame(self):
		''' Lit un frame nouveau (et pas le suivant si duplication) et renvoie (ret, frame) ou ret = true si ok
		'''
		if self.vid.isOpened():
			same_image = True
			ret = True
			while same_image and ret:
				ret, frame = self.vid.read()
				try:
					b,g,r = cv2.split(cv2.subtract(frame, self.last_frame))
					same_image = cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0
				except:
					same_image = False
			if ret:
			# Return a boolean success flag and the current frame converted to BGR
				self.last_frame = frame
				self.virtual_frame_no +=1
				self.frames[self.get_frame_no()]=self.virtual_frame_no
				return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
			else:
				return (ret, None)
		else:
			return (False, None)

	def read_frame(self):
		''' Lit un frame nouveau et renvoie true si ok
		'''
		# OPTIMISER (gain 50%) POUR GOTO MAIS PAS UTILISABLE POUR COMPTER FRAMES
		if self.vid.isOpened():
			ret = self.vid.read()
			return ret
		else:
			return False

	def get_props(self):
		'''renvoie un dict avec les propriétés du frame en cours
		'''
		frame_props = {}
		for prop in self.props:
			frame_props[prop]=self.vid.get(getattr(cv2,prop))
		return frame_props

	def get_frame_no(self):
		'''renvoie ne n° de frame actif
		'''
		try:
			return self.get_props()["CAP_PROP_POS_FRAMES"]
		except:
			return 0

	def get_virtual_frame_no(self, frame_no = None):
		'''Renvoie le n° virtuel (images disctinctes) de frame actif ou celui correspondant au paramètre
		'''
		if frame_no is None:
			frame_no = self.get_frame_no()
		return self.frames[frame_no]

	def get_time(self, frame_no = None):
		'''Renvoie le temps entre le début de la video et le frame actuel ou passé en param
			en ms
		'''
		return 1000*self.get_virtual_frame_no(frame_no) / self.get_virtual_fps()

	def get_virtual_fps(self):
		'''Renvoie le FPS réel (images dupliquées déduites)
		'''
		return self.fps / self.ratio_fps

	def calc_real_fps(self, sample = 10, max_images = 50):
		'''Calcul le ratio du nombre d'images / le nombre d'images distinctes
			Principe : on cherche 10 images distinctes succesives avec le même nb d'image entre elles
		'''
		nb_images_distinctes_succesives = 0
		ratio_fps = 0
		while nb_images_distinctes_succesives <= sample and self.get_frame_no() < max_images:
			last_virtual_frame_no = self.get_frame_no()
			self.get_frame()
			if ratio_fps == self.get_frame_no() - last_virtual_frame_no:
				nb_images_distinctes_succesives+=1
			else:
				nb_images_distinctes_succesives = 0
				ratio_fps = self.get_frame_no() - last_virtual_frame_no
		self.stop()
		if self.get_frame_no() < max_images:
			self.ratio_fps = ratio_fps
		else:
			self.ratio_fps = self.get_frame_no() / self.virtual_frame_no

	def stop(self):
		'''Stop la video et reviens au début
		'''
		self.vid.release()
		self.open()

	def goto_frame(self, frame_no):
		'''Va au frame n° frame_no
			Si besoin referme le fichier et lit chaque frame jusqu'au bout
		'''
		if frame_no < self.get_frame_no():
			self.stop()
		ret = True
		while ret and self.get_frame_no()< frame_no:
			ret = self.get_frame()

	def goto_time(self, t):
		'''V au frame le plus proche du temps t
			t		:	temps (millisecondes)

		'''
		t = t - 1000.0 / self.get_virtual_fps() / 2
		ret = True
		while ret and self.get_time() < t:
			ret = self.get_frame()
