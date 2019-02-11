# coding: utf8
from __future__ import unicode_literals

'''
	Une interface graphique pour réaliser du pointage image par image
	sur plusieurs videos (initialement deux, mais facilement extensible à n).

	Cette interface est conçue pour analyser le mouvement d'un véhicule
		Soit avec une caméra fixée au véhicule
		Soit avec une caméra fixée sur la route (ou la table si miniature)

	Exemple : www.pierron/chariot_pour_la_mecanique.html
'''

import PIVIMAGE

App = PIVIMAGE.App()
App.run()
