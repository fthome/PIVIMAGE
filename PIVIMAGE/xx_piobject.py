# -*-coding:Utf-8 -*

class PiObject(object):
	'''Classe abstraite qui ajoute les mécanismes de sérialisation json
	'''
	def save_json(self):
		'''Renvoi un dict décrivant l'application au format json
		'''
		state = self.__getstate__()
		for k, val in state.iteritems():
			if hasattr(val,'save_json'):
				state[k]=val.save_json()
		return state