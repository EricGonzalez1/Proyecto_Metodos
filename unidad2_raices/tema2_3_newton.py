"""
UNIDAD 2: SOLUCIÓN NUMÉRICA DE ECUACIONES NO LINEALES
Método 2: Método de Newton (Newton-Raphson)
"""

import sys
import os
import math
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Tuple, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.evaluador import evaluar_funcion, derivada_numerica
from utils.componentes_gui import TablaResultados, CanvasGraficador, ttk_seguro as ttk

ECUACIONES_CLASE_NEWTON = [
    ("cos(x) - x", "-sin(x) - 1", "1.0"),
    ("x^3 - 2*x - 5", "3*x^2 - 2", "2.0"),
    ("exp(-x) - x", "-exp(-x) - 1", "0.5"),
    ("x^3 + 4*x^2 - 10", "3*x^2 + 8*x", "1.5"),
]


def newton_raphson(
    expr: str,
    x0: float,
    expr_derivada: Optional[str] = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    iteraciones = []
    xi = x0
    raiz = x0
    convergido = False

    for k in range(1, max_iter + 1):
        f_xi = evaluar_funcion(expr, xi)

        if expr_derivada and expr_derivada.strip():
            df_xi = evaluar_funcion(expr_derivada.strip(), xi)
        else:
            df_xi = derivada_numerica(expr, xi)

        if abs(df_xi) < 1e-14:
            raise ZeroDivisionError(
                f"Derivada nula o casi nula en la iteración {k}: f'({xi:.6g}) = {df_xi:.4e}.\n"
                f"Prueba con otro valor inicial x0."
            )

        x_siguiente = xi - (f_xi / df_xi)

        if abs(x_siguiente) > 1e-15:
            ea = abs((x_siguiente - xi) / x_siguiente) * 100.0
        else:
            ea = abs(x_siguiente - xi) * 100.0

        iteraciones.append({
            'iter': k,
            'xi': xi,
            'f_xi': f_xi,
            'df_xi': df_xi,
            'x_sig': x_siguiente,
            'ea': ea
        })

        raiz = x_siguiente
        if abs(f_xi) < 1e-15 or ea <= tol:
            convergido = True
            break

        xi = x_siguiente

    resumen = {
        'raiz': raiz,
        'f_raiz': evaluar_funcion(expr, raiz),
        'iteraciones_totales': len(iteraciones),
        'convergido': convergido,
        'error_final': iteraciones[-1]['ea'] if iteraciones else 0.0
    }

    return iteraciones, resumen


def crear_vista_newton(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Newton", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Newton-Raphson es un método abierto que parte de un único valor inicial x0 y traza la recta tangente "
            "a la curva f(x) en cada iteración mediante la fórmula: x_{i+1} = x_i - f(x_i) / f'(x_i). Posee convergencia cuadrática "
            "cuando el valor inicial es cercano a la raíz."
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
        values=[f"{eq} = 0" for eq, _, _ in ECUACIONES_CLASE_NEWTON],
        state='readonly',
        width=22
    )
    combo_eq.current(0)
    combo_eq.grid(row=0, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Función f(x):").grid(row=1, column=0, sticky='w', pady=2)
    entry_fx = ttk.Entry(f_in, width=22)
    entry_fx.insert(0, ECUACIONES_CLASE_NEWTON[0][0])
    entry_fx.grid(row=1, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Derivada f'(x):").grid(row=2, column=0, sticky='w', pady=2)
    entry_dfx = ttk.Entry(f_in, width=22)
    entry_dfx.insert(0, ECUACIONES_CLASE_NEWTON[0][1])
    entry_dfx.grid(row=2, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Valor Inicial x0:").grid(row=3, column=0, sticky='w', pady=2)
    entry_x0 = ttk.Entry(f_in, width=12)
    entry_x0.insert(0, ECUACIONES_CLASE_NEWTON[0][2])
    entry_x0.grid(row=3, column=1, sticky='w', pady=2, padx=4)

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
        columnas=["i", "xi", "fxi", "dfxi", "xsig", "ea"],
        encabezados=["Iter", "x_i", "f(x_i)", "f'(x_i)", "x_{i+1}", "Error (%)"],
        anchos=[50, 105, 105, 105, 105, 95]
    )
    tabla.pack(fill=tk.BOTH, expand=True)

    f_res = ttk.LabelFrame(frame_principal, text="Solución Obtenida", padding=8)
    f_res.pack(fill=tk.X, padx=10, pady=4)
    lbl_res = ttk.Label(f_res, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_res.pack(anchor='w')

    def resolver():
        try:
            expr = entry_fx.get().strip()
            expr_df = entry_dfx.get().strip()
            x0_val = float(entry_x0.get().strip())
            tol_val = float(entry_tol.get().strip())
            max_val = int(entry_max.get().strip())

            iteraciones, resumen = newton_raphson(expr, x0_val, expr_df, tol_val, max_val)
            tabla.limpiar()

            for it in iteraciones:
                tabla.agregar_fila((
                    str(it['iter']),
                    f"{it['xi']:.6f}",
                    f"{it['f_xi']:.6f}",
                    f"{it['df_xi']:.6f}",
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
            messagebox.showerror("Error en Método de Newton", str(e))

    def seleccionar_ecuacion(_event=None):
        idx = combo_eq.current()
        if 0 <= idx < len(ECUACIONES_CLASE_NEWTON):
            eq, df_eq, x0_def = ECUACIONES_CLASE_NEWTON[idx]
            entry_fx.delete(0, tk.END)
            entry_fx.insert(0, eq)
            entry_dfx.delete(0, tk.END)
            entry_dfx.insert(0, df_eq)
            entry_x0.delete(0, tk.END)
            entry_x0.insert(0, x0_def)
            resolver()

    combo_eq.bind("<<ComboboxSelected>>", seleccionar_ecuacion)

    ttk.Button(f_btn, text="Calcular Solución", command=resolver).pack(side=tk.LEFT, padx=4)
    ttk.Button(f_btn, text="Restablecer Ejemplo", command=seleccionar_ecuacion).pack(side=tk.LEFT, padx=4)

    resolver()
    return frame_principal


crear_vista_tema2_3 = crear_vista_newton
