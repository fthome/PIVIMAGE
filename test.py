import jsonpickle


class A(object):
	def __init__(self, name, b):
		print("Instanciation A(%s)"%name)
		self.name = name
		self.b = b
	def __str__(self):
		return "A(%s) : %s"%(self.name, self.b)
	
	def __setstate__(self,state):
		print("set_state(A) with state : ",state)
		self.__dict__ = state
		
	def __getstate__(self):
		print("__getstate__ for A")
		return self.__dict__

class B(object):
	def __init__(self, name):
		print("Instanciation B(%s)"%name)
		self.name = name
	def __str__(self):
		return "B(%s)"%self.name
	
	def __setstate__(self, state):
		print("set_state(B) with state : ",state)
		self.__dict__ = state

	def __getstate__(self):
		print("__getstate__ for B")
		return self.__dict__
	
	def __del__(self):
		print("Suppression de %s"%self)
		

def sauve(obj):
	jsonpickle.set_preferred_backend('json')
	jsonpickle.set_encoder_options('json', indent = 4)
	with open("test.json", 'w') as f:
		f.write(jsonpickle.encode(obj))
		f.close()

def restaure():
	with open("test.json", 'r') as f:
		return jsonpickle.decode(f.read())

b=B('b')
a=A('a',b)