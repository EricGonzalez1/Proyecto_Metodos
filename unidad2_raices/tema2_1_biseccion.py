"""
UNIDAD 2: SOLUCIÓN NUMÉRICA DE ECUACIONES NO LINEALES
Método 1: Método de Bisección
"""

    
import sys
import os
import math
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Tuple, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.evaluador import evaluar_funcion
from utils.componentes_gui import TablaResultados, CanvasGraficador, ttk_seguro as ttk

ECUACIONES_CLASE = [
    ("x^3 - 2*x - 5", "2.0", "3.0"),
    ("x^3 + 4*x^2 - 10", "1.0", "2.0"),
    ("cos(x) - x", "0.0", "1.0"),
    ("exp(-x) - x", "0.0", "1.0"),
]


def buscar_extremo_cambio_signo(expr: str, a: float) -> float:
    """
    Si el usuario ingresa únicamente un valor inicial x0 (o un extremo donde f(a)*f(b) > 0),
    busca automáticamente un segundo punto b cercano donde ocurra cambio de signo f(a)*f(b) <= 0.
    """
    fa = evaluar_funcion(expr, a)
    if abs(fa) < 1e-15:
        return a + 0.5
    for paso in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
        for signo in (1.0, -1.0):
            cand = a + signo * paso
            try:
                fc = evaluar_funcion(expr, cand)
                if fa * fc <= 0:
                    return cand
            except Exception:
                pass
    # Búsqueda más fina en [-10, 10]
    x_scan = -10.0
    while x_scan <= 10.0:
        try:
            fc = evaluar_funcion(expr, x_scan)
            if fa * fc <= 0 and abs(x_scan - a) > 1e-6:
                return x_scan
        except Exception:
            pass
        x_scan += 0.25
    raise ValueError(
        f"No se encontró cambio de signo alrededor del valor inicial {a}. "
        f"Ingresa un intervalo [a, b] donde f(a) y f(b) tengan signos opuestos."
    )


def biseccion(
    expr: str,
    a: float,
    b: Optional[float] = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if b is None or abs(b - a) < 1e-14:
        b = buscar_extremo_cambio_signo(expr, a)

    fa = evaluar_funcion(expr, a)
    fb = evaluar_funcion(expr, b)

    if fa * fb > 0:
        # Intentar localizar automáticamente b a partir del valor inicial a
        b = buscar_extremo_cambio_signo(expr, a)
        fb = evaluar_funcion(expr, b)

    if a > b:
        a, b = b, a
        fa, fb = fb, fa

    iteraciones = []
    xr_ant = None
    raiz = (a + b) / 2.0
    convergido = False
    a_ini, b_ini = a, b

    for k in range(1, max_iter + 1):
        xr = (a + b) / 2.0
        fxr = evaluar_funcion(expr, xr)

        if xr_ant is not None and abs(xr) > 1e-15:
            ea = abs((xr - xr_ant) / xr) * 100.0
        elif xr_ant is not None:
            ea = abs(xr - xr_ant) * 100.0
        else:
            ea = 100.0

        iteraciones.append({
            'iter': k,
            'a': a,
            'b': b,
            'xr': xr,
            'fa': fa,
            'fb': fb,
            'fxr': fxr,
            'ea': ea
        })

        if abs(fxr) < 1e-15 or (xr_ant is not None and ea <= tol):
            raiz = xr
            convergido = True
            break

        if fa * fxr < 0:
            b = xr
            fb = fxr
        else:
            a = xr
            fa = fxr

        xr_ant = xr
        raiz = xr

    resumen = {
        'raiz': raiz,
        'f_raiz': evaluar_funcion(expr, raiz),
        'iteraciones_totales': len(iteraciones),
        'convergido': convergido,
        'error_final': iteraciones[-1]['ea'] if iteraciones else 0.0,
        'a_usado': a_ini,
        'b_usado': b_ini
    }

    return iteraciones, resumen


def crear_vista_biseccion(parent) -> ttk.Frame:
    frame_principal = ttk.Frame(parent)

    # Breve explicación del método (Requisito del profesor)
    f_exp = ttk.LabelFrame(frame_principal, text="Breve Explicación del Método de Bisección", padding=8)
    f_exp.pack(fill=tk.X, padx=10, pady=(4, 4))
    ttk.Label(
        f_exp,
        text=(
            "El método de Bisección parte de una función continua f(x) y un valor/intervalo inicial donde ocurre un cambio de signo "
            "f(a)·f(b) < 0 (Teorema de Bolzano). En cada iteración calcula el punto medio xr = (a + b) / 2, evalúa f(xr) "
            "y selecciona la mitad del intervalo donde continúa el cambio de signo hasta converger a la raíz."
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

    # Parámetros de entrada
    f_in = ttk.LabelFrame(frame_izq, text="Datos de Entrada (Ecuación vista en clase)", padding=8)
    f_in.pack(fill=tk.X, pady=(0, 8))

    ttk.Label(f_in, text="Ecuaciones de clase:").grid(row=0, column=0, sticky='w', pady=2)
    combo_eq = ttk.Combobox(
        f_in,
        values=[f"{eq} = 0" for eq, _, _ in ECUACIONES_CLASE],
        state='readonly',
        width=22
    )
    combo_eq.current(0)
    combo_eq.grid(row=0, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Función f(x):").grid(row=1, column=0, sticky='w', pady=2)
    entry_fx = ttk.Entry(f_in, width=22)
    entry_fx.insert(0, ECUACIONES_CLASE[0][0])
    entry_fx.grid(row=1, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Valor inicial a (x0):").grid(row=2, column=0, sticky='w', pady=2)
    entry_a = ttk.Entry(f_in, width=12)
    entry_a.insert(0, ECUACIONES_CLASE[0][1])
    entry_a.grid(row=2, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Extremo b (o auto):").grid(row=3, column=0, sticky='w', pady=2)
    entry_b = ttk.Entry(f_in, width=12)
    entry_b.insert(0, ECUACIONES_CLASE[0][2])
    entry_b.grid(row=3, column=1, sticky='w', pady=2, padx=4)

    ttk.Label(f_in, text="Tolerancia (%):").grid(row=4, column=0, sticky='w', pady=2)
    entry_tol = ttk.Entry(f_in, width=12)
    entry_tol.insert(0, "0.001")
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
        columnas=["i", "a", "b", "xr", "fa", "fb", "fxr", "ea"],
        encabezados=["Iter", "a", "b", "x_r = (a+b)/2", "f(a)", "f(b)", "f(x_r)", "Error (%)"],
        anchos=[48, 88, 88, 105, 88, 88, 92, 90]
    )
    tabla.pack(fill=tk.BOTH, expand=True)

    f_res = ttk.LabelFrame(frame_principal, text="Solución Obtenida", padding=8)
    f_res.pack(fill=tk.X, padx=10, pady=4)
    lbl_res = ttk.Label(f_res, text="-", font=('Helvetica', 10, 'bold'), foreground='#0D47A1')
    lbl_res.pack(anchor='w')

    def resolver():
        try:
            expr = entry_fx.get().strip()
            a_val = float(entry_a.get().strip())
            b_str = entry_b.get().strip()
            b_val = float(b_str) if b_str else None
            tol_val = float(entry_tol.get().strip())
            max_val = int(entry_max.get().strip())

            iteraciones, resumen = biseccion(expr, a_val, b_val, tol_val, max_val)
            entry_b.delete(0, tk.END)
            entry_b.insert(0, f"{resumen['b_usado']:.4g}")

            tabla.limpiar()
            for it in iteraciones:
                tabla.agregar_fila((
                    str(it['iter']),
                    f"{it['a']:.6f}",
                    f"{it['b']:.6f}",
                    f"{it['xr']:.6f}",
                    f"{it['fa']:.6f}",
                    f"{it['fb']:.6f}",
                    f"{it['fxr']:.6f}",
                    f"{it['ea']:.4f}%"
                ))

            raiz = resumen['raiz']
            f_raiz = resumen['f_raiz']
            lbl_res.config(
                text=f"Solución de la ecuación f(x) = 0  -->  x = {raiz:.8f}   |   f(x) = {f_raiz:.4e}   |   "
                     f"Iteraciones: {resumen['iteraciones_totales']}   |   Error final: {resumen['error_final']:.5f}%"
            )

            a_u, b_u = resumen['a_usado'], resumen['b_usado']
            delta = max(abs(b_u - a_u), 1.0)
            graficador.graficar_funcion(
                expr,
                min(a_u, b_u) - 0.5 * delta,
                max(a_u, b_u) + 0.5 * delta,
                puntos_destacados=[(raiz, f_raiz, f" Raíz: {raiz:.4f}")]
            )
        except Exception as e:
            messagebox.showerror("Error en Bisección", str(e))

    def seleccionar_ecuacion(_event=None):
        idx = combo_eq.current()
        if 0 <= idx < len(ECUACIONES_CLASE):
            eq, a_def, b_def = ECUACIONES_CLASE[idx]
            entry_fx.delete(0, tk.END)
            entry_fx.insert(0, eq)
            entry_a.delete(0, tk.END)
            entry_a.insert(0, a_def)
            entry_b.delete(0, tk.END)
            entry_b.insert(0, b_def)
            resolver()

    combo_eq.bind("<<ComboboxSelected>>", seleccionar_ecuacion)

    ttk.Button(f_btn, text="Calcular Solución", command=resolver).pack(side=tk.LEFT, padx=4)
    ttk.Button(f_btn, text="Restablecer Ejemplo", command=seleccionar_ecuacion).pack(side=tk.LEFT, padx=4)

    resolver()
    return frame_principal


crear_vista_tema2_1 = crear_vista_biseccion
