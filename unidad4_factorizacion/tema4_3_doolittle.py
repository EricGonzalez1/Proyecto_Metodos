"""
UNIDAD 4: FACTORIZACIÓN LU Y SUS APLICACIONES
Método 1: Método de Doolittle
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.algebra_lineal import (
    Matriz, Vector, crear_matriz, matriz_identidad,
    sustitucion_adelante, sustitucion_atras
)
from utils.componentes_gui import EditorMatriz, ttk_seguro as ttk


def factorizacion_doolittle(A: Matriz, b: Vector = None) -> Tuple[Matriz, Matriz, Vector, List[str]]:
    n = len(A)
    L = matriz_identidad(n)
    U = crear_matriz(n, n, 0.0)
    pasos = []

    pasos.append(f"1. Factorización A = L · U por Doolittle (L con 1s en la diagonal principal):")

    for i in range(n):
        for j in range(i, n):
            suma = sum(L[i][k] * U[k][j] for k in range(i))
            U[i][j] = A[i][j] - suma
            pasos.append(f"   U[{i+1},{j+1}] = {A[i][j]:.4f} - ({suma:.4f}) = {U[i][j]:.6f}")

        if abs(U[i][i]) < 1e-15:
            raise ZeroDivisionError(f"Pivote nulo en U[{i+1},{i+1}] = 0.")

        for j in range(i + 1, n):
            suma = sum(L[j][k] * U[k][i] for k in range(i))
            L[j][i] = (A[j][i] - suma) / U[i][i]
            pasos.append(f"   L[{j+1},{i+1}] = ({A[j][i]:.4f} - ({suma:.4f})) / {U[i][i]:.4f} = {L[j][i]:.6f}")

    x = None
    if b is not None and len(b) == n:
        pasos.append("\n2. Sustitución hacia adelante (L · y = b):")
        y = sustitucion_adelante(L, b, unos_diagonal=True)
        for i, yi in enumerate(y, 1):
            pasos.append(f"   y{i} = {yi:.6f}")

        pasos.append("\n3. Sustitución hacia atrás (U · x = y):")
        x = sustitucion_atras(U, y, unos_diagonal=False)
        for i, xi in enumerate(x, 1):
            pasos.append(f"   x{i} = {xi:.6f}")

    return L, U, x, pasos


def crear_vista_doolittle(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Doolittle", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Doolittle resuelve el sistema lineal A·x = b descomponiendo la matriz A en el producto de una "
            "matriz triangular inferior L (con 1s en su diagonal principal: l_{ii} = 1) y una matriz triangular superior U (A = L·U). "
            "Posteriormente se resuelve L·y = b por sustitución hacia adelante y U·x = y por sustitución hacia atrás."
        ),
        font=('Helvetica', 9),
        wraplength=1060,
        justify=tk.LEFT
    ).pack(anchor='w')

    editor = EditorMatriz(frame_principal, titulo="Sistema de Ecuaciones Lineales [ A | b ]", n_inicial=3, con_vector_b=True)
    editor.pack(fill=tk.X, padx=10, pady=4)

    f_acciones = ttk.Frame(frame_principal)
    f_acciones.pack(fill=tk.X, padx=10, pady=4)

    txt_res = tk.Text(
        frame_principal,
        height=13,
        font=('Courier', 10),
        wrap='word',
        bg="#FFFFFF",
        fg="#0F172A",
        relief=tk.SOLID,
        bd=1
    )
    txt_res.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

    f_sol = ttk.LabelFrame(frame_principal, text="Solución del Sistema Lineal (Doolittle)", padding=8)
    f_sol.pack(fill=tk.X, padx=10, pady=4)
    lbl_sol = ttk.Label(f_sol, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_sol.pack(anchor='w')

    def resolver():
        try:
            A = editor.obtener_matriz()
            b = editor.obtener_vector_b()
            L, U, x, pasos = factorizacion_doolittle(A, b)

            txt_res.delete("1.0", tk.END)
            salida = (
                f"DESARROLLO PASO A PASO - MÉTODO DE DOOLITTLE (A = L · U)\n"
                f"{'='*72}\n"
                + "\n".join(pasos)
                + f"\n\n{'='*72}\nMATRIZ L (Triangular Inferior con diagonal de 1s):\n"
            )
            for fila in L:
                salida += "  [ " + "  ".join(f"{val:10.4f}" for val in fila) + " ]\n"

            salida += f"\nMATRIZ U (Triangular Superior):\n"
            for fila in U:
                salida += "  [ " + "  ".join(f"{val:10.4f}" for val in fila) + " ]\n"

            if x is not None:
                salida += f"\nSOLUCIÓN FINAL DEL SISTEMA:\n"
                for i, xi in enumerate(x, 1):
                    salida += f"  x{i} = {xi:.6f}\n"
                res_str = "   |   ".join(f"x{i+1} = {x[i]:.6f}" for i in range(len(x)))
                lbl_sol.config(text=f"Vector Solución:   {res_str}")

            txt_res.insert(tk.END, salida)
        except Exception as e:
            messagebox.showerror("Error en Doolittle", str(e))

    def cargar_ejemplo():
        A = [
            [2.0, -1.0, -2.0],
            [-4.0, 6.0, 3.0],
            [-4.0, -2.0, 8.0]
        ]
        b = [-1.0, 13.0, -6.0]
        editor.cargar_datos(A, b)
        resolver()

    ttk.Button(f_acciones, text="Resolver por Doolittle", command=resolver).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Cargar Ejercicio de Clase (3x3)", command=cargar_ejemplo).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Limpiar Celdas", command=editor.limpiar).pack(side=tk.LEFT, padx=5)

    cargar_ejemplo()
    return frame_principal


crear_vista_tema4_3 = crear_vista_doolittle
