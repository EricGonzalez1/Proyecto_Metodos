"""
Lanzador directo sin consola para Windows (.pyw).
En Windows, al hacer doble clic sobre este archivo se abre directamente
la interfaz gráfica con pythonw.exe sin mostrar ventana negra de símbolo del sistema.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from main import main

if __name__ == "__main__":
    main()
