"""
UNIDAD 2: SOLUCIÓN NUMÉRICA DE ECUACIONES NO LINEALES
Método 3: Método de la Secante
"""

import sys
import os
import math
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.evaluador import evaluar_funcion
from utils.componentes_gui import TablaResultados, CanvasGraficador, ttk_seguro as ttk

ECUACIONES_CLASE_SECANTE = [
    ("exp(-x^2) - x", "0.0", "1.0"),
    ("x^3 - 2*x - 5", "2.0", "3.0"),
    ("cos(x) - x", "0.5", "1.0"),
    ("x^3 + 4*x^2 - 10", "1.0", "2.0"),
]


def secante(
    expr: str,
    x0: float,
    x1: float,
    tol: float = 1e-4,
    max_iter: int = 100
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    iteraciones = []
    x_ant = x0
    x_act = x1
    f_ant = evaluar_funcion(expr, x_ant)
    raiz = x1
    convergido = False

    for k in range(1, max_iter + 1):
        f_act = evaluar_funcion(expr, x_act)
        den = f_act - f_ant

        if abs(den) < 1e-15:
            raise ZeroDivisionError(f"División entre cero en iteración {k}: f(x_i) ≈ f(x_{{i-1}}).")

        x_sig = x_act - (f_act * (x_act - x_ant)) / den

        if abs(x_sig) > 1e-15:
            ea = abs((x_sig - x_act) / x_sig) * 100.0
        else:
            ea = abs(x_sig - x_act) * 100.0

        iteraciones.append({
            'iter': k,
            'x_ant': x_ant,
            'x_act': x_act,
            'f_ant': f_ant,
            'f_act': f_act,
            'x_sig': x_sig,
            'ea': ea
        })

        raiz = x_sig
        if abs(f_act) < 1e-15 or ea <= tol:
            convergido = True
            break

        x_ant = x_act
        f_ant = f_act
        x_act = x_sig

    resumen = {
        'raiz': raiz,
        'f_raiz': evaluar_funcion(expr, raiz),
        'iteraciones_totales': len(iteraciones),
        'convergido': convergido,
        'error_final': iteraciones[-1]['ea'] if iteraciones else 0.0
    }

    return iteraciones, resumen


def crear_vista_secante(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de la Secante", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de la Secante recibe dos valores iniciales (x0 y x1) y aproxima la derivada mediante la pendiente "
            "de la recta secante que une (x_{i-1}, f(x_{i-1})) con (x_i, f(x_i)), aplicando la fórmula: "
            "x_{i+1} = x_i - f(x_i)·(x_i - x_{i-1}) / (f(x_i) - f(x_{i-1}))."
        ),
        font=('Helvetica', 9),
        wraplength=1060,
        justify=tk.LEFT
    ).pack(anchor='w')

    panel_principal = ttk.PanedWindow(frame_principal, orient=tk.HORIZONTAL)
    panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

    frame_izq = ttk.Frame(panel_principal, padding=4)
    frame_der = ttk.Frame(panel_principal, padding=4)
    panel_principal.add(frame_izq, weight=1)
    panel_principal.add(frame_der, weight=2)

    f_in = ttk.LabelFrame(frame_izq, text="Datos de Entrada (Ecuación vista en clase)", padding=8)
    f_in.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(f_in, text="Ecuaciones de clase:").grid(row=0, column=0, sticky='w', pady=2)
    combo_eq = ttk.Combobox(
        f_in,
        values=[f"{eq} = 0" for eq, _, _ in ECUACIONES_CLASE_SECANTE],
        state='readonly',
        width=22
    )
    combo_eq.current(0)
    combo_eq.grid(row=0, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Función f(x):").grid(row=1, column=0, sticky='w', pady=2)
    entry_fx = ttk.Entry(f_in, width=22)
    entry_fx.insert(0, ECUACIONES_CLASE_SECANTE[0][0])
    entry_fx.grid(row=1, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Primer valor inicial x0:").grid(row=2, column=0, sticky='w', pady=2)
    entry_x0 = ttk.Entry(f_in, width=12)
    entry_x0.insert(0, ECUACIONES_CLASE_SECANTE[0][1])
    entry_x0.grid(row=2, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Segundo valor inicial x1:").grid(row=3, column=0, sticky='w', pady=2)
    entry_x1 = ttk.Entry(f_in, width=12)
    entry_x1.insert(0, ECUACIONES_CLASE_SECANTE[0][2])
    entry_x1.grid(row=3, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Tolerancia (%):").grid(row=4, column=0, sticky='w', pady=2)
    entry_tol = ttk.Entry(f_in, width=12)
    entry_tol.insert(0, "0.0001")
    entry_tol.grid(row=4, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Máx. Iteraciones:").grid(row=5, column=0, sticky='w', pady=2)
    entry_max = ttk.Entry(f_in, width=12)
    entry_max.insert(0, "50")
    entry_max.grid(row=5, column=1, sticky='w', pady=2, padx=4)

    f_btn = ttk.Frame(f_in)
    f_btn.grid(row=6, column=0, columnspan=2, pady=6)

    graficador = CanvasGraficador(frame_izq, ancho=360, alto=220)
    graficador.pack(fill=tk.BOTH, expand=True)

    tabla = TablaResultados(
        frame_der,
        columnas=["i", "xant", "xact", "fant", "fact", "xsig", "ea"],
        encabezados=["Iter", "x_{i-1}", "x_i", "f(x_{i-1})", "f(x_i)", "x_{i+1}", "Error (%)"],
        anchos=[48, 92, 92, 92, 92, 100, 90]
    )
    tabla.pack(fill=tk.BOTH, expand=True)

    f_res = ttk.LabelFrame(frame_principal, text="Solución Obtenida", padding=8)
    f_res.pack(fill=tk.X, padx=10, pady=4)
    lbl_res = ttk.Label(f_res, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_res.pack(anchor='w')

    def resolver():
        try:
            expr = entry_fx.get().strip()
            x0_val = float(entry_x0.get().strip())
            x1_val = float(entry_x1.get().strip())
            tol_val = float(entry_tol.get().strip())
            max_val = int(entry_max.get().strip())

            iteraciones, resumen = secante(expr, x0_val, x1_val, tol_val, max_val)
            tabla.limpiar()

            for it in iteraciones:
                tabla.agregar_fila((
                    str(it['iter']),
                    f"{it['x_ant']:.6f}",
                    f"{it['x_act']:.6f}",
                    f"{it['f_ant']:.6f}",
                    f"{it['f_act']:.6f}",
                    f"{it['x_sig']:.6f}",
                    f"{it['ea']:.4f}%"
                ))

            raiz = resumen['raiz']
            f_raiz = resumen['f_raiz']
            lbl_res.config(
                text=f"Solución de la ecuación f(x) = 0  -->  x = {raiz:.8f}   |   f(x) = {f_raiz:.4e}   |   "
                     f"Iteraciones: {resumen['iteraciones_totales']}   |   Error final: {resumen['error_final']:.5f}%"
            )

            graficador.graficar_funcion(
                expr,
                raiz - 2.5,
                raiz + 2.5,
                puntos_destacados=[(raiz, f_raiz, f" Raíz: {raiz:.4f}")]
            )
        except Exception as e:
            messagebox.showerror("Error en Método de la Secante", str(e))

    def seleccionar_ecuacion(_event=None):
        idx = combo_eq.current()
        if 0 <= idx < len(ECUACIONES_CLASE_SECANTE):
            eq, x0_def, x1_def = ECUACIONES_CLASE_SECANTE[idx]
            entry_fx.delete(0, tk.END)
            entry_fx.insert(0, eq)
            entry_x0.delete(0, tk.END)
            entry_x0.insert(0, x0_def)
            entry_x1.delete(0, tk.END)
            entry_x1.insert(0, x1_def)
            resolver()

    combo_eq.bind("<<ComboboxSelected>>", seleccionar_ecuacion)

    ttk.Button(f_btn, text="Calcular Solución", command=resolver).pack(side=tk.LEFT, padx=4)
    ttk.Button(f_btn, text="Restablecer Ejemplo", command=seleccionar_ecuacion).pack(side=tk.LEFT, padx=4)

    resolver()
    return frame_principal


crear_vista_tema2_4 = crear_vista_secante
