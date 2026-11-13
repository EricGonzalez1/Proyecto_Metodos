"""
====================================================================
PROYECTO DE MÉTODOS NUMÉRICOS
Ambiente Gráfico en Python (Tkinter Estándar)
Estructura con Menú Principal, Menús Secundarios por Unidad,
Introducción en cada parte, Breve explicación en cada método,
y Salida exclusiva desde el Menú Principal.
====================================================================
"""

import os
import sys

# Silenciar advertencia de versión de Tk del sistema en macOS antes de importar tkinter
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import tkinter as tk
from tkinter import messagebox

# Configurar ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.componentes_gui import configurar_dpi_windows, instalar_parche_render_macos_tk85
configurar_dpi_windows()
instalar_parche_render_macos_tk85()

# Importar vistas de Unidad 2 (Bisección, Newton y Secante)
from unidad2_raices.tema2_1_biseccion import crear_vista_biseccion
from unidad2_raices.tema2_3_newton import crear_vista_newton
from unidad2_raices.tema2_4_secante import crear_vista_secante

# Importar vistas de Unidad 3 (Gauss-Jordan, Gauss-Seidel y Jacobi)
from unidad3_sistemas.tema3_2_gauss_jordan import crear_vista_gauss_jordan
from unidad3_sistemas.tema3_4_gauss_seidel import crear_vista_gauss_seidel
from unidad3_sistemas.tema3_4_jacobi import crear_vista_jacobi

# Importar vistas de Unidad 4 (Doolittle y Crout)
from unidad4_factorizacion.tema4_3_doolittle import crear_vista_doolittle
from unidad4_factorizacion.tema4_4_crout import crear_vista_crout

# Importar vistas de Unidad 5 (Potencia y Potencia Inversa)
from unidad5_eigen.tema5_1_potencia import crear_vista_potencia
from unidad5_eigen.tema5_2_potencia_inversa import crear_vista_potencia_inversa


# Catálogo oficial de Unidades y Métodos según las indicaciones del profesor
CATALOGO_UNIDADES = [
    {
        "numero": "Unidad 2",
        "titulo": "Unidad 2: Solución de Ecuaciones No Lineales",
        "subtitulo": "Métodos: Bisección, Newton y Secante",
        "introduccion": (
            "INTRODUCCIÓN A LA UNIDAD 2:\n"
            "En esta unidad se estudian los algoritmos numéricos para aproximar las raíces reales de una ecuación no lineal "
            "de una sola variable f(x) = 0. Se abordan tanto métodos cerrados (Bisección, que acota la raíz en un intervalo) "
            "como métodos abiertos (Newton y Secante, que utilizan rectas tangentes o secantes a partir de valores iniciales) "
            "generando la tabla de iteraciones para revisar la convergencia hacia la solución."
        ),
        "metodos": [
            ("Bisección", crear_vista_biseccion),
            ("Newton", crear_vista_newton),
            ("Secante", crear_vista_secante),
        ],
    },
    {
        "numero": "Unidad 3",
        "titulo": "Unidad 3: Solución de Sistemas de Ecuaciones Lineales",
        "subtitulo": "Métodos: Gauss-Jordan, Gauss-Seidel y Jacobi",
        "introduccion": (
            "INTRODUCCIÓN A LA UNIDAD 3:\n"
            "En esta unidad se resuelven sistemas de ecuaciones lineales de la forma A·x = b. Se implementa el método exacto "
            "de eliminación de Gauss-Jordan (que transforma la matriz aumentada [A | b] en la identidad [I | x]) y los métodos "
            "iterativos de Gauss-Seidel y Jacobi, los cuales aproximan el vector solución despejando las incógnitas de la diagonal principal."
        ),
        "metodos": [
            ("Gauss - Jordan", crear_vista_gauss_jordan),
            ("Gauss - Seidel", crear_vista_gauss_seidel),
            ("Jacobi", crear_vista_jacobi),
        ],
    },
    {
        "numero": "Unidad 4",
        "titulo": "Unidad 4: Factorización LU y sus Aplicaciones",
        "subtitulo": "Métodos: Doolittle y Crout",
        "introduccion": (
            "INTRODUCCIÓN A LA UNIDAD 4:\n"
            "La factorización LU descompone la matriz de coeficientes A en el producto de una matriz triangular inferior (L) "
            "y una matriz triangular superior (U), de modo que A·x = b se resuelve en dos etapas simples: sustitución hacia adelante "
            "(L·y = b) y sustitución hacia atrás (U·x = y). Se incluyen los métodos clásicos de Doolittle (diagonal de 1s en L) y Crout (diagonal de 1s en U)."
        ),
        "metodos": [
            ("Doolittle", crear_vista_doolittle),
            ("Crout", crear_vista_crout),
        ],
    },
    {
        "numero": "Unidad 5",
        "titulo": "Unidad 5: Cálculo de Valores y Vectores Propios",
        "subtitulo": "Métodos: Potencia y Potencia Inversa",
        "introduccion": (
            "INTRODUCCIÓN A LA UNIDAD 5:\n"
            "Los valores propios (λ) y vectores propios (v) de una matriz cuadrada A satisfacen la relación A·v = λ·v. "
            "En esta unidad se programan el método de la Potencia (para obtener el valor propio máximo y su vector propio correspondiente) "
            "y el método de la Potencia Inversa (para obtener el valor propio mínimo y su vector propio correspondiente)."
        ),
        "metodos": [
            ("Potencia (Valor Propio Máximo)", crear_vista_potencia),
            ("Potencia Inversa (Valor Propio Mínimo)", crear_vista_potencia_inversa),
        ],
    },
]


class AplicacionPrincipal:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Métodos Numéricos — Unidades 2, 3, 4 y 5")
        self._configurar_geometria_multiplataforma()
        self.root.configure(bg="#F1F5F9")

        # Forzar colores claros legibles
        self.root.option_add("*Text.background", "#FFFFFF")
        self.root.option_add("*Text.foreground", "#0F172A")
        self.root.option_add("*Entry.background", "#FFFFFF")
        self.root.option_add("*Entry.foreground", "#0F172A")

        # REGLA DEL PROFESOR: "La única forma de salir es con la opción de salir en el menú principal"
        self.en_menu_principal = True
        self.root.protocol("WM_DELETE_WINDOW", self._intento_cerrar_bloqueado)
        try:
            self.root.createcommand("::tk::mac::Quit", self._intento_cerrar_bloqueado)
        except Exception:
            pass
        self.root.bind_all("<Command-q>", self._atajo_salida_bloqueado)
        self.root.bind_all("<Control-q>", self._atajo_salida_bloqueado)
        self.root.bind_all("<Alt-F4>", self._atajo_salida_bloqueado)

        # Contenedor raíz donde se intercambia el Menú Principal y los Menús Secundarios
        self.contenedor_raiz = tk.Frame(self.root, bg="#F1F5F9")
        self.contenedor_raiz.pack(fill=tk.BOTH, expand=True)

        self._crear_barra_estado()
        self.mostrar_menu_principal()

    def _configurar_geometria_multiplataforma(self):
        """Ajusta y centra la ventana según la resolución disponible en Windows, macOS o Linux."""
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            ancho = min(1220, max(960, sw - 60))
            alto = min(820, max(660, sh - 80))
            pos_x = max(0, (sw - ancho) // 2)
            pos_y = max(0, (sh - alto) // 2 - 10)
            self.root.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
            self.root.minsize(min(960, ancho), min(640, alto))
        except Exception:
            self.root.geometry("1180x780")
            self.root.minsize(960, 640)
        try:
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(120, lambda: self.root.attributes("-topmost", False))
            self.root.focus_force()
        except Exception:
            pass

    def _atajo_salida_bloqueado(self, _event=None):
        self._intento_cerrar_bloqueado()
        return "break"

    def _intento_cerrar_bloqueado(self):
        """Impide cerrar con la 'X' o Cmd+Q para cumplir que solo se salga desde el Menú Principal."""
        messagebox.showwarning(
            "Salida Restringida",
            "Por indicación general del proyecto:\n\n"
            "«La única forma de salir es con la opción de salir en el menú principal».\n\n"
            "Dirígete al Menú Principal y presiona el botón 'Salir del Programa'."
        )

    def _salir_desde_menu_principal(self):
        """Única función autorizada para cerrar la aplicación (solo disponible en el Menú Principal)."""
        if not self.en_menu_principal:
            self._intento_cerrar_bloqueado()
            return
        if messagebox.askyesno(
            "Confirmar Salida",
            "¿Deseas salir del Sistema de Métodos Numéricos?"
        ):
            self.root.destroy()

    def _limpiar_contenedor_raiz(self):
        for child in self.contenedor_raiz.winfo_children():
            child.destroy()

    def mostrar_menu_principal(self):
        """Muestra la pantalla del Menú Principal con la Introducción General, las Unidades y la opción de Salir."""
        self.en_menu_principal = True
        self._limpiar_contenedor_raiz()

        # Encabezado institucional
        header = tk.Frame(self.contenedor_raiz, bg="#0F172A", padx=20, pady=14)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="PROYECTO FINAL DE MÉTODOS NUMÉRICOS — MENÚ PRINCIPAL",
            font=("Helvetica", 15, "bold"),
            bg="#0F172A",
            fg="#FFFFFF"
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Selecciona una Unidad para abrir su Menú Secundario y ejecutar los métodos correspondientes.",
            font=("Helvetica", 10),
            bg="#0F172A",
            fg="#CBD5E1"
        ).pack(anchor="w", pady=(3, 0))

        cuerpo = tk.Frame(self.contenedor_raiz, bg="#F1F5F9", padx=24, pady=14)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        # Introducción general del sistema (Requisito del profesor)
        marco_intro = tk.LabelFrame(
            cuerpo,
            text=" Introducción General al Sistema de Métodos Numéricos ",
            font=("Helvetica", 11, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            padx=14,
            pady=10,
            relief=tk.GROOVE,
            bd=2
        )
        marco_intro.pack(fill=tk.X, pady=(0, 14))

        texto_intro = (
            "Bienvenido al Sistema Interactivo de Métodos Numéricos. Los métodos numéricos son técnicas matemáticas mediante "
            "las cuales es posible formular problemas de manera que puedan resolverse usando operaciones aritméticas sistemáticas.\n\n"
            "Este sistema agrupa los métodos vistos en clase de acuerdo con el temario oficial de la materia:\n"
            "  • Unidad 2 (Ecuaciones No Lineales): Bisección, Newton y Secante.\n"
            "  • Unidad 3 (Sistemas de Ecuaciones Lineales): Gauss-Jordan, Gauss-Seidel y Jacobi.\n"
            "  • Unidad 4 (Factorización LU): Doolittle y Crout.\n"
            "  • Unidad 5 (Valores y Vectores Propios): Potencia y Potencia Inversa.\n\n"
            "En cada unidad encontrarás una introducción teórica, un menú secundario para elegir el método, una breve explicación "
            "de cada algoritmo y la tabla o desarrollo paso a paso como en los ejercicios realizados en el curso."
        )
        tk.Label(
            marco_intro,
            text=texto_intro,
            font=("Helvetica", 10),
            bg="#FFFFFF",
            fg="#0F172A",
            justify=tk.LEFT,
            wraplength=1120
        ).pack(anchor="w")

        # Cuadrícula de tarjetas para las 4 Unidades (Menús Secundarios)
        marco_unidades = tk.LabelFrame(
            cuerpo,
            text=" Menús Secundarios por Unidad del Temario ",
            font=("Helvetica", 11, "bold"),
            bg="#F1F5F9",
            fg="#0F172A",
            padx=12,
            pady=12,
            relief=tk.GROOVE,
            bd=2
        )
        marco_unidades.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

        for i in range(2):
            marco_unidades.columnconfigure(i, weight=1)
            marco_unidades.rowconfigure(i, weight=1)

        for idx, unidad in enumerate(CATALOGO_UNIDADES):
            fila = idx // 2
            col = idx % 2

            tarjeta = tk.Frame(
                marco_unidades,
                bg="#FFFFFF",
                padx=16,
                pady=12,
                relief=tk.RAISED,
                bd=2,
                highlightbackground="#94A3B8",
                highlightthickness=1
            )
            tarjeta.grid(row=fila, column=col, sticky="nsew", padx=8, pady=8)

            tk.Label(
                tarjeta,
                text=unidad["titulo"],
                font=("Helvetica", 12, "bold"),
                bg="#FFFFFF",
                fg="#1E3A8A"
            ).pack(anchor="w")

            tk.Label(
                tarjeta,
                text=unidad["subtitulo"],
                font=("Helvetica", 10, "bold"),
                bg="#FFFFFF",
                fg="#2563EB"
            ).pack(anchor="w", pady=(2, 6))

            lista_metodos = "  •  ".join(m[0] for m in unidad["metodos"])
            tk.Label(
                tarjeta,
                text=f"Métodos incluidos: {lista_metodos}",
                font=("Helvetica", 9),
                bg="#FFFFFF",
                fg="#334155"
            ).pack(anchor="w", pady=(0, 10))

            btn_abrir = tk.Label(
                tarjeta,
                text=f"  Abrir Menú Secundario de {unidad['numero']}  ➜  ",
                font=("Helvetica", 10, "bold"),
                bg="#1D4ED8",
                fg="#FFFFFF",
                padx=12,
                pady=7,
                cursor="hand2",
                relief=tk.RAISED,
                bd=1
            )
            btn_abrir.pack(anchor="w")
            btn_abrir.bind("<Button-1>", lambda _e, u=idx: self.mostrar_menu_unidad(u, 0))
            btn_abrir.bind("<Enter>", lambda _e, b=btn_abrir: b.config(bg="#2563EB"))
            btn_abrir.bind("<Leave>", lambda _e, b=btn_abrir: b.config(bg="#1D4ED8"))

        # Barra inferior del Menú Principal con la ÚNICA opción para salir del programa
        marco_salida = tk.Frame(cuerpo, bg="#FEE2E2", padx=16, pady=10, relief=tk.SOLID, bd=1)
        marco_salida.pack(fill=tk.X)

        tk.Label(
            marco_salida,
            text="Indicaciones del Sistema: La única forma de salir del programa es mediante el botón de la derecha en este Menú Principal.",
            font=("Helvetica", 10, "bold"),
            bg="#FEE2E2",
            fg="#991B1B"
        ).pack(side=tk.LEFT)

        btn_salir = tk.Label(
            marco_salida,
            text="  ✖  Salir del Programa (Menú Principal)  ",
            font=("Helvetica", 10, "bold"),
            bg="#DC2626",
            fg="#FFFFFF",
            padx=14,
            pady=7,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        btn_salir.pack(side=tk.RIGHT)
        btn_salir.bind("<Button-1>", lambda _e: self._salir_desde_menu_principal())
        btn_salir.bind("<Enter>", lambda _e: btn_salir.config(bg="#B91C1C"))
        btn_salir.bind("<Leave>", lambda _e: btn_salir.config(bg="#DC2626"))

        self.root.update_idletasks()

    def mostrar_menu_unidad(self, u_idx: int, m_idx: int = 0):
        """
        Muestra el Menú Secundario de la Unidad seleccionada:
        1. Barra superior con botón para regresar al Menú Principal (sin botón de salir directo).
        2. Introducción de la Unidad.
        3. Botones del Menú Secundario para elegir cada Método de la Unidad.
        4. Área interactiva del Método con su breve explicación, tabla de datos y solución.
        """
        self.en_menu_principal = False
        self._limpiar_contenedor_raiz()

        unidad = CATALOGO_UNIDADES[u_idx]

        # 1. Barra superior del Menú Secundario
        barra_sup = tk.Frame(self.contenedor_raiz, bg="#0F172A", padx=14, pady=8)
        barra_sup.pack(fill=tk.X)

        btn_volver = tk.Label(
            barra_sup,
            text="  ⬅  Volver al Menú Principal  ",
            font=("Helvetica", 10, "bold"),
            bg="#F59E0B",
            fg="#0F172A",
            padx=10,
            pady=5,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        btn_volver.pack(side=tk.LEFT, padx=(0, 14))
        btn_volver.bind("<Button-1>", lambda _e: self.mostrar_menu_principal())
        btn_volver.bind("<Enter>", lambda _e: btn_volver.config(bg="#FBBF24"))
        btn_volver.bind("<Leave>", lambda _e: btn_volver.config(bg="#F59E0B"))

        tk.Label(
            barra_sup,
            text=f"MENÚ SECUNDARIO  |  {unidad['titulo'].upper()}",
            font=("Helvetica", 12, "bold"),
            bg="#0F172A",
            fg="#FFFFFF"
        ).pack(side=tk.LEFT)

        # 2. Introducción de la Unidad
        marco_intro_u = tk.Frame(self.contenedor_raiz, bg="#EFF6FF", padx=14, pady=6, relief=tk.SOLID, bd=1)
        marco_intro_u.pack(fill=tk.X, padx=10, pady=(6, 4))
        tk.Label(
            marco_intro_u,
            text=unidad["introduccion"],
            font=("Helvetica", 9),
            bg="#EFF6FF",
            fg="#1E3A8A",
            justify=tk.LEFT,
            wraplength=1160
        ).pack(anchor="w")

        # 3. Barra de botones del Menú Secundario (Métodos de la Unidad)
        barra_metodos = tk.Frame(self.contenedor_raiz, bg="#CBD5E1", padx=10, pady=6)
        barra_metodos.pack(fill=tk.X, padx=10)

        tk.Label(
            barra_metodos,
            text="Selecciona el Método:",
            font=("Helvetica", 10, "bold"),
            bg="#CBD5E1",
            fg="#0F172A"
        ).pack(side=tk.LEFT, padx=(4, 10))

        for i, (nombre_metodo, _) in enumerate(unidad["metodos"]):
            es_activo = (i == m_idx)
            btn_m = tk.Label(
                barra_metodos,
                text=f"  {i+1}. {nombre_metodo}  ",
                font=("Helvetica", 10, "bold" if es_activo else "normal"),
                bg="#1E3A8A" if es_activo else "#FFFFFF",
                fg="#FFFFFF" if es_activo else "#0F172A",
                padx=12,
                pady=5,
                cursor="hand2",
                relief=tk.SUNKEN if es_activo else tk.RAISED,
                bd=2
            )
            btn_m.pack(side=tk.LEFT, padx=4)
            btn_m.bind("<Button-1>", lambda _e, ui=u_idx, mi=i: self.mostrar_menu_unidad(ui, mi))

        # 4. Contenedor del Método Seleccionado
        contenedor_metodo = tk.Frame(self.contenedor_raiz, bg="#F1F5F9")
        contenedor_metodo.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        _, creador_vista = unidad["metodos"][m_idx]
        vista_metodo = creador_vista(contenedor_metodo)
        vista_metodo.pack(fill=tk.BOTH, expand=True)

        self.root.update_idletasks()

    def _crear_barra_estado(self):
        barra = tk.Frame(self.root, bg="#E2E8F0", padx=12, pady=4)
        barra.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(
            barra,
            text="Proyecto de Métodos Numéricos  |  Unidades 2, 3, 4 y 5  |  Nota: Para salir del sistema utiliza exclusivamente la opción 'Salir del Programa' en el Menú Principal",
            font=("Helvetica", 9),
            bg="#E2E8F0",
            fg="#1E293B"
        ).pack(side=tk.LEFT)


def main():
    root = tk.Tk()
    AplicacionPrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
