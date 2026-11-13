"""
UNIDAD 3: SOLUCIÓN DE SISTEMAS DE ECUACIONES LINEALES
Método 3: Método de Jacobi
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.algebra_lineal import Matriz, Vector, norma_infinito
from utils.componentes_gui import EditorMatriz, TablaResultados, ttk_seguro as ttk


def es_diagonalmente_dominante(A: Matriz) -> Tuple[bool, List[str]]:
    n = len(A)
    dominante = True
    mensajes = []
    for i in range(n):
        diag = abs(A[i][i])
        suma_otros = sum(abs(A[i][j]) for j in range(n) if j != i)
        if diag <= suma_otros:
            dominante = False
            mensajes.append(f"Fila {i+1}: |A[{i+1},{i+1}]| = {diag:.4g} <= {suma_otros:.4g}")
    return dominante, mensajes


def metodo_jacobi(
    A: Matriz,
    b: Vector,
    x0: Vector = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> Tuple[List[dict], Vector, bool]:
    n = len(A)
    for i in range(n):
        if abs(A[i][i]) < 1e-15:
            raise ZeroDivisionError(f"Elemento diagonal nulo en A[{i+1},{i+1}]. Reordena las ecuaciones.")

    x_ant = [0.0] * n if x0 is None else list(x0)
    iteraciones = []
    convergido = False
    x_act = list(x_ant)

    for k in range(1, max_iter + 1):
        x_act = [0.0] * n
        for i in range(n):
            suma = sum(A[i][j] * x_ant[j] for j in range(n) if j != i)
            x_act[i] = (b[i] - suma) / A[i][i]

        diff = [abs(x_act[i] - x_ant[i]) for i in range(n)]
        err = max(diff)
        norm_act = norma_infinito(x_act)
        err_rel = (err / norm_act) * 100.0 if norm_act > 1e-15 else err * 100.0

        iteraciones.append({
            'k': k,
            'x': list(x_act),
            'error_abs': err,
            'error_rel': err_rel
        })

        if err <= tol or err_rel <= tol:
            convergido = True
            break

        x_ant = list(x_act)

    return iteraciones, x_act, convergido


def crear_vista_jacobi(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Jacobi", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Jacobi es un método iterativo simultáneo para resolver sistemas lineales A·x = b. "
            "Se despeja cada incógnita x_i de la ecuación i-ésima: x_i^{(k+1)} = (b_i - sum_{j!=i} a_{ij}·x_j^{(k)}) / a_{ii}, "
            "calculando todo el nuevo vector usando únicamente los valores de la iteración anterior k."
        ),
        font=('Helvetica', 9),
        wraplength=1060,
        justify=tk.LEFT
    ).pack(anchor='w')

    editor = EditorMatriz(frame_principal, titulo="Sistema de Ecuaciones Lineales [ A | b ]", n_inicial=3, con_vector_b=True)
    editor.pack(fill=tk.X, padx=10, pady=4)

    f_params = ttk.Frame(frame_principal)
    f_params.pack(fill=tk.X, padx=10, pady=4)

    ttk.Label(f_params, text="Tolerancia:").pack(side=tk.LEFT, padx=(5, 3))
    entry_tol = ttk.Entry(f_params, width=10)
    entry_tol.insert(0, "0.0001")
    entry_tol.pack(side=tk.LEFT, padx=(0, 10))

    ttk.Label(f_params, text="Máx. Iteraciones:").pack(side=tk.LEFT, padx=(5, 3))
    entry_max = ttk.Entry(f_params, width=6)
    entry_max.insert(0, "50")
    entry_max.pack(side=tk.LEFT, padx=(0, 15))

    frame_tabla = ttk.Frame(frame_principal)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
    tabla_ref = [None]

    f_res = ttk.LabelFrame(frame_principal, text="Solución del Sistema Lineal (Jacobi)", padding=8)
    f_res.pack(fill=tk.X, padx=10, pady=4)
    lbl_res = ttk.Label(f_res, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_res.pack(anchor='w')

    def resolver():
        try:
            A = editor.obtener_matriz()
            b = editor.obtener_vector_b()
            tol = float(entry_tol.get().strip())
            max_it = int(entry_max.get().strip())
            n = len(A)

            es_dom, _ = es_diagonalmente_dominante(A)
            iteraciones, x_final, conv = metodo_jacobi(A, b, tol=tol, max_iter=max_it)

            if tabla_ref[0]:
                tabla_ref[0].destroy()

            cols = ["k"] + [f"x{i+1}" for i in range(n)] + ["error"]
            heads = ["Iter"] + [f"x_{i+1}" for i in range(n)] + ["Error Máx (%)"]
            anchos = [55] + [120] * n + [120]

            nueva_tabla = TablaResultados(frame_tabla, columnas=cols, encabezados=heads, anchos=anchos)
            nueva_tabla.pack(fill=tk.BOTH, expand=True)
            tabla_ref[0] = nueva_tabla

            fila_cero = ["0"] + [f"{0.0:.6f}" for _ in range(n)] + ["-"]
            nueva_tabla.agregar_fila(tuple(fila_cero))

            for it in iteraciones:
                fila_vals = [str(it['k'])] + [f"{val:.6f}" for val in it['x']] + [f"{it['error_rel']:.5f}%"]
                nueva_tabla.agregar_fila(tuple(fila_vals))

            dom_texto = "Matriz Diagonalmente Dominante" if es_dom else "Nota: Matriz no diagonalmente dominante"
            res_str = "   |   ".join(f"x{i+1} = {x_final[i]:.6f}" for i in range(n))
            lbl_res.config(
                text=f"Solución obtenida en {len(iteraciones)} iteraciones ({dom_texto}):\n{res_str}"
            )
        except Exception as e:
            messagebox.showerror("Error en Jacobi", str(e))

    def cargar_ejemplo():
        A = [
            [10.0, 2.0, -1.0],
            [-2.0, 10.0, 1.0],
            [1.0, -2.0, 10.0]
        ]
        b = [7.0, 8.0, 6.0]
        editor.cargar_datos(A, b)
        resolver()

    ttk.Button(f_params, text="Resolver por Jacobi", command=resolver).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_params, text="Cargar Ejercicio de Clase (3x3)", command=cargar_ejemplo).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_params, text="Limpiar Celdas", command=editor.limpiar).pack(side=tk.LEFT, padx=5)

    cargar_ejemplo()
    return frame_principal


crear_vista_tema3_4_jacobi = crear_vista_jacobi
