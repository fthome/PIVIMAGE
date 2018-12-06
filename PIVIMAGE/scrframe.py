#!/usr/bin/python
# -*- coding: utf-8 -*-

# Thanks : https://gist.github.com/EugeneBakin
# http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

try:
	import tkinter
except:
	import Tkinter as tkinter

from ttk import *



class VerticalScrolledFrame(tkinter.Frame):
	"""A pure Tkinter scrollable frame that actually works!
	* Use the 'interior' attribute to place widgets inside the scrollable frame
	* Construct and pack/place/grid normally
	* This frame only allows vertical scrolling

	"""
	def __init__(self, parent, height = None, *args, **kw):
		tkinter.Frame.__init__(self, parent, *args, **kw)            

		# create a canvas object and a vertical scrollbar for scrolling it
		vscrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
		vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.TRUE)
		canvas = tkinter.Canvas(self, bd=0, highlightthickness=0,
						yscrollcommand=vscrollbar.set, height = height)
		canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
		vscrollbar.config(command=canvas.yview)

		# reset the view
		canvas.xview_moveto(0)
		canvas.yview_moveto(0)

		# create a frame inside the canvas which will be scrolled with it
		self.interior = interior = Frame(canvas)
		interior_id = canvas.create_window(0, 0, window=interior,
										   anchor=tkinter.NW)

		# track changes to the canvas and frame width and sync them,
		# also updating the scrollbar
		def _configure_interior(event):
			# update the scrollbars to match the size of the inner frame
			size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
			canvas.config(scrollregion="0 0 %s %s" % size)
			if interior.winfo_reqwidth() != canvas.winfo_width():
				# update the canvas's width to fit the inner frame
				canvas.config(width=interior.winfo_reqwidth())
		interior.bind('<Configure>', _configure_interior)

		def _configure_canvas(event):
			if interior.winfo_reqwidth() != canvas.winfo_width():
				# update the inner frame's width to fill the canvas
				canvas.itemconfigure(interior_id, width=canvas.winfo_width())
		canvas.bind('<Configure>', _configure_canvas)


if __name__ == "__main__":

	class SampleApp(tkinter.Tk):
		def __init__(self, *args, **kwargs):
			root = tkinter.Tk.__init__(self, *args, **kwargs)


			self.frame = VerticalScrolledFrame(root)
			self.frame.pack()
			self.label = tkinter.Label(text="Shrink the window to activate the scrollbar.")
			self.label.pack()
			buttons = []
			for i in range(10):
				buttons.append(tkinter.Button(self.frame.interior, text="Button " + str(i)))
				buttons[-1].pack()

	app = SampleApp()
	app.mainloop()