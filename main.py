import tkinter as tk
from tkinter import messagebox

def mensaje():
    messagebox.showinfo("Mensaje", "¡Hola! Has hecho clic en el botón.")

ventana = tk.Tk()
ventana.title("Mi primera ventana")
ventana.geometry("1470x956")

boton = tk.Button(ventana, text="Haz clic aquí", command=mensaje)
boton.pack()

ventana.mainloop()

