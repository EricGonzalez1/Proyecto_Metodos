"""
UNIDAD 5: CÁLCULO DE VALORES Y VECTORES PROPIOS
Método 1: Método de la Potencia (Valor Propio Máximo)
"""

import sys
import os
import math
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.algebra_lineal import Matriz, Vector, multiplicar_matriz_vector
from utils.componentes_gui import EditorMatriz, TablaResultados, ttk_seguro as ttk


def metodo_potencia_maximo(
    A: Matriz,
    x0: Vector = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> Tuple[float, Vector, List[dict], bool]:
    """
    Calcula el valor propio máximo (dominante) y su vector propio correspondiente
    normalizando respecto a la componente de mayor magnitud (norma infinito, como en clase).
    """
    n = len(A)
    x = [1.0] * n if x0 is None else list(x0)

    lambda_ant = 0.0
    iteraciones = []
    convergido = False

    for k in range(1, max_iter + 1):
        y = multiplicar_matriz_vector(A, x)

        # Componente de mayor valor absoluto (conservando su signo, como en los ejercicios de clase)
        idx_max = max(range(n), key=lambda i: abs(y[i]))
        c_max = y[idx_max]

        if abs(c_max) < 1e-15:
            raise ValueError(f"El vector propio colapsó a cero en la iteración {k}.")

        x_sig = [val / c_max for val in y]

        if k == 1:
            err_rel = 100.0
        else:
            err_lam = abs((c_max - lambda_ant) / c_max) * 100.0
            err_vec = max(abs(x_sig[i] - x[i]) for i in range(n)) * 100.0
            err_rel = max(err_lam, err_vec)

        iteraciones.append({
            'k': k,
            'y': list(y),
            'lambda': c_max,
            'vector': list(x_sig),
            'error': err_rel
        })

        if k > 1 and err_rel <= tol:
            convergido = True
            break

        lambda_ant = c_max
        x = x_sig

    lambda_final = iteraciones[-1]['lambda']
    vector_final = iteraciones[-1]['vector']
    return lambda_final, vector_final, iteraciones, convergido


def crear_vista_potencia(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de la Potencia", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de la Potencia es un procedimiento iterativo que recibe una matriz cuadrada A y un vector inicial x^(0) "
            "para determinar el valor propio de mayor magnitud (valor propio máximo λ_máx) y su vector propio asociado. "
            "En cada iteración se multiplica y^(k) = A·x^(k-1), se extrae como factor común la componente de mayor magnitud "
            "(λ^(k)) y se normaliza el vector x^(k) = y^(k) / λ^(k) hasta converger."
        ),
        font=('Helvetica', 9),
        wraplength=1060,
        justify=tk.LEFT
    ).pack(anchor='w')

    editor = EditorMatriz(frame_principal, titulo="Matriz Cuadrada A", n_inicial=3, con_vector_b=False)
    editor.pack(fill=tk.X, padx=10, pady=4)

    f_params = ttk.Frame(frame_principal)
    f_params.pack(fill=tk.X, padx=10, pady=4)

    ttk.Label(f_params, text="Tolerancia (%):").pack(side=tk.LEFT, padx=(5, 3))
    entry_tol = ttk.Entry(f_params, width=10)
    entry_tol.insert(0, "0.001")
    entry_tol.pack(side=tk.LEFT, padx=(0, 10))

    ttk.Label(f_params, text="Máx. Iteraciones:").pack(side=tk.LEFT, padx=(5, 3))
    entry_max = ttk.Entry(f_params, width=6)
    entry_max.insert(0, "50")
    entry_max.pack(side=tk.LEFT, padx=(0, 15))

    tabla = TablaResultados(
        frame_principal,
        columnas=["k", "y", "lambda", "vector", "error"],
        encabezados=[
            "Iter",
            "Producto y^(k) = A·x^(k-1)",
            "Valor Propio Máx (λ)",
            "Vector Propio Normalizado x^(k)",
            "Error (%)"
        ],
        anchos=[50, 230, 150, 240, 100]
    )
    tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

    f_res = ttk.LabelFrame(frame_principal, text="Resultado: Valor Propio Máximo y Vector Propio", padding=8)
    f_res.pack(fill=tk.X, padx=10, pady=4)
    lbl_res = ttk.Label(f_res, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_res.pack(anchor='w')

    def resolver():
        try:
            A = editor.obtener_matriz()
            tol = float(entry_tol.get().strip())
            max_it = int(entry_max.get().strip())

            lam, vec, iters, _ = metodo_potencia_maximo(A, tol=tol, max_iter=max_it)

            tabla.limpiar()
            for it in iters:
                y_str = "[ " + ", ".join(f"{v:.4f}" for v in it['y']) + " ]"
                vec_str = "[ " + ", ".join(f"{v:.5f}" for v in it['vector']) + " ]"
                tabla.agregar_fila((
                    str(it['k']),
                    y_str,
                    f"{it['lambda']:.6f}",
                    vec_str,
                    f"{it['error']:.4f}%"
                ))

            v_str = "[ " + ",  ".join(f"{v:.6f}" for v in vec) + " ]"
            lbl_res.config(
                text=f"Valor Propio Máximo (λ_máx) = {lam:.6f}     |     Iteraciones: {len(iters)}\n"
                     f"Vector Propio Correspondiente v = {v_str}"
            )
        except Exception as e:
            messagebox.showerror("Error en Método de la Potencia", str(e))

    def cargar_ejemplo():
        A = [
            [4.0, 1.0, 2.0],
            [1.0, 2.0, 0.0],
            [2.0, 0.0, 5.0]
        ]
        editor.cargar_datos(A)
        resolver()

    ttk.Button(f_params, text="Calcular Valor Propio Máximo", command=resolver).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_params, text="Cargar Ejercicio de Clase (3x3)", command=cargar_ejemplo).pack(side=tk.LEFT, padx=5)
    ttk.Button(f_params, text="Limpiar Celdas", command=editor.limpiar).pack(side=tk.LEFT, padx=5)

    cargar_ejemplo()
    return frame_principal
