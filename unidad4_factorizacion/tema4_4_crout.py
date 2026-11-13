"""
UNIDAD 4: FACTORIZACIÓN LU Y SUS APLICACIONES
Método 2: Método de Crout
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


def factorizacion_crout(A: Matriz, b: Vector = None) -> Tuple[Matriz, Matriz, Vector, List[str]]:
    n = len(A)
    L = crear_matriz(n, n, 0.0)
    U = matriz_identidad(n)
    pasos = []

    pasos.append(f"1. Factorización A = L · U por Crout (U con 1s en la diagonal principal):")

    for j in range(n):
        for i in range(j, n):
            suma = sum(L[i][k] * U[k][j] for k in range(j))
            L[i][j] = A[i][j] - suma
            pasos.append(f"   L[{i+1},{j+1}] = {A[i][j]:.4f} - ({suma:.4f}) = {L[i][j]:.6f}")

        if abs(L[j][j]) < 1e-15:
            raise ZeroDivisionError(f"Pivote diagonal nulo en L[{j+1},{j+1}] = 0.")

        for i in range(j + 1, n):
            suma = sum(L[j][k] * U[k][i] for k in range(j))
            U[j][i] = (A[j][i] - suma) / L[j][j]
            pasos.append(f"   U[{j+1},{i+1}] = ({A[j][i]:.4f} - ({suma:.4f})) / {L[j][j]:.4f} = {U[j][i]:.6f}")

    x = None
    if b is not None and len(b) == n:
        pasos.append("\n2. Sustitución hacia adelante (L · y = b):")
        y = sustitucion_adelante(L, b, unos_diagonal=False)
        for i, yi in enumerate(y, 1):
            pasos.append(f"   y{i} = {yi:.6f}")

        pasos.append("\n3. Sustitución hacia atrás (U · x = y con U[i][i] = 1):")
        x = sustitucion_atras(U, y, unos_diagonal=True)
        for i, xi in enumerate(x, 1):
            pasos.append(f"   x{i} = {xi:.6f}")

    return L, U, x, pasos


def crear_vista_crout(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Crout", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Crout resuelve un sistema de ecuaciones lineales A·x = b factorizando la matriz A en el producto "
            "de una matriz triangular inferior L y una matriz triangular superior U con unos en su diagonal principal (u_{ii} = 1). "
            "Una vez obtenidas L y U, se resuelve L·y = b hacia adelante y U·x = y hacia atrás para hallar la solución x."
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

    f_sol = ttk.LabelFrame(frame_principal, text="Solución del Sistema Lineal (Crout)", padding=8)
    f_sol.pack(fill=tk.X, padx=10, pady=4)
    lbl_sol = ttk.Label(f_sol, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_sol.pack(anchor='w')

    def resolver():
        try:
            A = editor.obtener_matriz()
            b = editor.obtener_vector_b()
            L, U, x, pasos = factorizacion_crout(A, b)

            txt_res.delete("1.0", tk.END)
            salida = (
                f"DESARROLLO PASO A PASO - MÉTODO DE CROUT (A = L · U)\n"
                f"{'='*72}\n"
                + "\n".join(pasos)
                + f"\n\n{'='*72}\nMATRIZ L (Triangular Inferior):\n"
            )
            for fila in L:
                salida += "  [ " + "  ".join(f"{val:10.4f}" for val in fila) + " ]\n"

            salida += f"\nMATRIZ U (Triangular Superior con diagonal de 1s):\n"
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
            messagebox.showerror("Error en Crout", str(e))

    def cargar_ejemplo():
        A = [
            [2.0, -1.0, -2.0],
            [-4.0, 6.0, 3.0],
            [-4.0, -2.0, 8.0]
        ]
        b = [-1.0, 13.0, -6.0]
        editor.cargar_datos(A, b)
        resolver()

    ttk.Button(f_acciones, text="Resolver por Crout", command=resolver).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Cargar Ejercicio de Clase (3x3)", command=cargar_ejemplo).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Limpiar Celdas", command=editor.limpiar).pack(side=tk.LEFT, padx=5)

    cargar_ejemplo()
    return frame_principal


crear_vista_tema4_4 = crear_vista_crout
