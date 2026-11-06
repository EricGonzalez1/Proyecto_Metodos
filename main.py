import tkinter as tk
from tkinter import messagebox

import addPrueba

def mensaje():
    messagebox.showinfo("Mensaje", "¡Hola! Has hecho clic en el botón.")

ventana = tk.Tk()
ventana.title("Mi primera ventana")
ventana.geometry("1400x900")

boton = tk.Button(ventana, text="Haz clic aquí", command=addPrueba.saluda)
boton.pack()

ventana.mainloop()

# PROBANDO COMENTARIOS
# OTRO COMENTARIO  


