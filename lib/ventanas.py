
from tkinter import *
from tkinter.messagebox import showwarning



root = Tk()
root.title="ventana principal"



def msg():
    emergente = showwarning(title="PRINTER", message="He detectado este error")
    print(f"Estado de emergente --> {emergente}")

btn = Button(root, text="click", command=msg)
btn.pack()



root.mainloop()