"""
UNIDAD 3: SOLUCIÓN DE SISTEMAS DE ECUACIONES LINEALES
Método 1: Método de Gauss-Jordan
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.algebra_lineal import Matriz, Vector
from utils.componentes_gui import EditorMatriz, ttk_seguro as ttk


def gauss_jordan(A: Matriz, b: Vector) -> Tuple[Vector, List[str]]:
    """
    Resuelve un sistema de ecuaciones lineales A·x = b mediante el método de Gauss-Jordan,
    transformando la matriz aumentada [A | b] en la matriz identidad [I | x] paso a paso
    como en los ejercicios realizados en clase.
    """
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    pasos: List[str] = []

    pasos.append(f"Matriz aumentada inicial [A | b] ({n}x{n+1}):")
    for row in M:
        pasos.append("  [ " + "  ".join(f"{val:10.4f}" for val in row[:-1]) + f" | {row[-1]:10.4f} ]")

    for k in range(n):
        # Si el pivote diagonal es casi cero, intercambiar con una fila inferior con mayor valor absoluto
        if abs(M[k][k]) < 1e-12:
            max_fila = max(range(k, n), key=lambda i: abs(M[i][k]))
            if abs(M[max_fila][k]) < 1e-14:
                raise ValueError(f"El sistema no tiene solución única (pivote nulo en columna {k+1}).")
            M[k], M[max_fila] = M[max_fila], M[k]
            pasos.append(f"\n[Paso {k+1}] Intercambio de R{k+1} <-> R{max_fila+1} para evitar pivote nulo.")

        pivote = M[k][k]
        pasos.append(f"\n[Paso {k+1}] Normalizar R{k+1} --> R{k+1} = R{k+1} / ({pivote:.4f}):")
        for j in range(k, n + 1):
            M[k][j] /= pivote

        pasos.append(f"  Eliminación en columna {k+1} (hacer ceros arriba y abajo del pivote):")
        for i in range(n):
            if i != k:
                factor = M[i][k]
                if abs(factor) > 1e-15:
                    for j in range(k, n + 1):
                        M[i][j] -= factor * M[k][j]
                    pasos.append(f"    R{i+1} = R{i+1} - ({factor:.4f}) · R{k+1}")

        pasos.append(f"  Matriz aumentada después del Paso {k+1}:")
        for row in M:
            pasos.append("  [ " + "  ".join(f"{val:10.4f}" for val in row[:-1]) + f" | {row[-1]:10.4f} ]")

    x_final = [M[i][n] for i in range(n)]
    return x_final, pasos


# Alias para compatibilidad con pruebas existentes
gauss_jordan_pivoteo_total = gauss_jordan


def crear_vista_gauss_jordan(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Gauss-Jordan", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Gauss-Jordan es un método directo que transforma la matriz aumentada del sistema lineal [A | b] "
            "en una matriz diagonal unitaria (identidad) [I | x] mediante operaciones elementales por renglón: "
            "1) dividir el renglón pivote entre su elemento diagonal (R_k = R_k / a_{kk}) para obtener un 1, y "
            "2) hacer ceros todos los demás elementos de esa columna tanto arriba como abajo (R_i = R_i - a_{ik}·R_k)."
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

    f_sol = ttk.LabelFrame(frame_principal, text="Solución del Sistema Lineal (Gauss-Jordan)", padding=8)
    f_sol.pack(fill=tk.X, padx=10, pady=4)
    lbl_sol = ttk.Label(f_sol, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_sol.pack(anchor='w')

    def resolver():
        try:
            A = editor.obtener_matriz()
            b = editor.obtener_vector_b()
            x, pasos = gauss_jordan(A, b)

            txt_res.delete("1.0", tk.END)
            salida = (
                f"DESARROLLO PASO A PASO - MÉTODO DE GAUSS-JORDAN\n"
                f"{'='*72}\n"
                + "\n".join(pasos)
                + f"\n\n{'='*72}\nSOLUCIÓN DEL SISTEMA DE ECUACIONES:\n"
            )
            for i, xi in enumerate(x, 1):
                salida += f"  x{i} = {xi:.6f}\n"

            txt_res.insert(tk.END, salida)
            res_str = "   |   ".join(f"x{i+1} = {x[i]:.6f}" for i in range(len(x)))
            lbl_sol.config(text=f"Vector Solución:   {res_str}")
        except Exception as e:
            messagebox.showerror("Error en Gauss-Jordan", str(e))

    def cargar_ejemplo():
        A = [
            [2.0, 1.0, -1.0],
            [-3.0, -1.0, 2.0],
            [-2.0, 1.0, 2.0]
        ]
        b = [8.0, -11.0, -3.0]
        editor.cargar_datos(A, b)
        resolver()

    ttk.Button(f_acciones, text="Resolver por Gauss-Jordan", command=resolver).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Cargar Ejercicio de Clase (3x3)", command=cargar_ejemplo).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_acciones, text="Limpiar Celdas", command=editor.limpiar).pack(side=tk.LEFT, padx=5)

    cargar_ejemplo()
    return frame_principal


crear_vista_tema3_2_gj = crear_vista_gauss_jordan
