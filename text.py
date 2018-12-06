from Tkinter import *
 
root = Tk()

vsb = Scrollbar(root, orient=VERTICAL)
vsb.grid(row=0, column=1, sticky=N+S)


hsb = Scrollbar(root, orient=HORIZONTAL)
hsb.grid(row=1, column=0, sticky=E+W)


c = Canvas(root,yscrollcommand=vsb.set, xscrollcommand=hsb.set)
c.grid(row=0, column=0, sticky="news")


vsb.config(command=c.yview)
hsb.config(command=c.xview)


root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
fr = Frame(c)
#On ajoute des widgets :
for i in range(0,26):
    row=i/8
    col=i%8
    Button(fr, width=10,height=2,text="%s" %(chr(i+65))).grid(row=row, column=col)
c.create_window(0, 0,  window=fr)
fr.update_idletasks()
c.config(scrollregion=c.bbox("all"))
root.mainloop()