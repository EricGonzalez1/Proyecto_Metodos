"""
Componentes Gráficos 100% Puros en Tkinter (Sin ttk ni NSView nativos defectuosos en macOS Tk 8.5)
Garantiza compatibilidad total y colores de alto contraste en macOS (Modo Oscuro y Claro), Windows y Linux.
"""

import os
import sys
import ctypes
import math
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Tuple

# Silenciar advertencia de deprecación de Tk en macOS
os.environ["TK_SILENCE_DEPRECATION"] = "1"

# Referencias globales para evitar que el recolector de basura libere los callbacks C de ctypes
_REFS_PARCHE_MACOS = []
_PARCHE_MACOS_INSTALADO = False


def instalar_parche_render_macos_tk85():
    """
    Corrige el bug de ventana vacía/negra de Apple Tcl/Tk 8.5.9 en macOS modernos (Big Sur a macOS 27+).
    En Tk 8.5.9, -[TKContentView generateExposeEvents:] aborta si [[NSRunLoop currentRunLoop] currentMode] != nil,
    postergando el dibujo fuera de -[TKContentView drawRect:] mediante [view lockFocusIfCanDraw], lo cual
    está deshabilitado en vistas layer-backed de macOS moderno.
    Este parche procesa sincrónicamente los eventos Expose/Idle de Tcl dentro de drawRect: y redirige
    lockFocusIfCanDraw fuera de drawRect: hacia [view setNeedsDisplay:YES].
    """
    global _PARCHE_MACOS_INSTALADO
    if _PARCHE_MACOS_INSTALADO or sys.platform != "darwin":
        return
    if getattr(tk, "TkVersion", 8.6) > 8.5:
        return

    try:
        libtcl = ctypes.CDLL("/System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl")
        objc = ctypes.CDLL("/usr/lib/libobjc.A.dylib")

        libtcl.Tcl_DoOneEvent.argtypes = [ctypes.c_int]
        libtcl.Tcl_DoOneEvent.restype = ctypes.c_int

        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        objc.class_getInstanceMethod.restype = ctypes.c_void_p
        objc.class_getInstanceMethod.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        objc.method_getImplementation.restype = ctypes.c_void_p
        objc.method_getImplementation.argtypes = [ctypes.c_void_p]
        objc.method_setImplementation.restype = ctypes.c_void_p
        objc.method_setImplementation.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        objc.class_addMethod.restype = ctypes.c_bool
        objc.class_addMethod.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p
        ]

        cls_tk_view = objc.objc_getClass(b"TKContentView")
        cls_ns_view = objc.objc_getClass(b"NSView")
        if not cls_tk_view or not cls_ns_view:
            return

        sel_focus = objc.sel_registerName(b"focusView")
        sel_needs = objc.sel_registerName(b"setNeedsDisplay:")
        sel_draw = objc.sel_registerName(b"drawRect:")
        sel_lock = objc.sel_registerName(b"lockFocusIfCanDraw")

        msg_id = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )(("objc_msgSend", objc))
        msg_void_bool = ctypes.CFUNCTYPE(
            None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool
        )(("objc_msgSend", objc))

        m_draw = objc.class_getInstanceMethod(cls_tk_view, sel_draw)
        if not m_draw:
            return

        DRAW_FUNC = ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
        )
        orig_draw_ptr = objc.method_getImplementation(m_draw)
        orig_draw = DRAW_FUNC(orig_draw_ptr)

        en_draw = False

        def _fixed_draw_rect(self_ptr, _cmd, x, y, w, h):
            nonlocal en_draw
            orig_draw(self_ptr, _cmd, x, y, w, h)
            if en_draw:
                return
            en_draw = True
            try:
                # TCL_WINDOW_EVENTS (0x04) | TCL_IDLE_EVENTS (0x20) | TCL_DONT_WAIT (0x02)
                for _ in range(500):
                    if not libtcl.Tcl_DoOneEvent(0x04 | 0x20 | 0x02):
                        break
            finally:
                en_draw = False

        LOCK_FUNC = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def _custom_lock_focus(self_ptr, _cmd):
            focus = msg_id(cls_ns_view, sel_focus)
            if focus != self_ptr:
                msg_void_bool(self_ptr, sel_needs, True)
                return False
            return True

        c_fixed_draw = DRAW_FUNC(_fixed_draw_rect)
        c_custom_lock = LOCK_FUNC(_custom_lock_focus)

        objc.method_setImplementation(m_draw, ctypes.cast(c_fixed_draw, ctypes.c_void_p))
        if not objc.class_addMethod(
            cls_tk_view, sel_lock, ctypes.cast(c_custom_lock, ctypes.c_void_p), b"c@:"
        ):
            m_lock = objc.class_getInstanceMethod(cls_tk_view, sel_lock)
            if m_lock:
                objc.method_setImplementation(m_lock, ctypes.cast(c_custom_lock, ctypes.c_void_p))

        _REFS_PARCHE_MACOS.extend([
            libtcl, objc, msg_id, msg_void_bool, orig_draw, c_fixed_draw, c_custom_lock
        ])
        _PARCHE_MACOS_INSTALADO = True
    except Exception:
        pass


def configurar_dpi_windows():
    """Activa el escalado nítido High-DPI en Windows 10/11."""
    if not sys.platform.startswith("win"):
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# Activar parche en macOS o DPI en Windows automáticamente al importar componentes_gui
configurar_dpi_windows()
instalar_parche_render_macos_tk85()

from utils.evaluador import evaluar_funcion

# Paleta de colores de alto contraste (Modo Claro Forzado para legibilidad perfecta)
COLOR_BG_APP = "#F1F5F9"       # Gris azulado muy claro para el fondo general
COLOR_BG_PANEL = "#FFFFFF"     # Blanco puro para paneles y tarjetas
COLOR_TEXTO = "#0F172A"        # Azul pizarra casi negro para todo el texto
COLOR_PRIMARIO = "#1E3A8A"     # Azul marino institucional
COLOR_BOTON = "#1D4ED8"        # Azul intenso para botones
COLOR_BOTON_HOVER = "#2563EB"  # Azul brillante al pasar el mouse
COLOR_TAB_INACTIVA = "#CBD5E1" # Gris claro para pestañas inactivas
COLOR_BORDE = "#94A3B8"        # Gris medio para bordes


def _obtener_bg_padre(parent, default=COLOR_BG_PANEL) -> str:
    try:
        bg = parent.cget("bg")
        if bg and not bg.startswith("system"):
            return bg
    except Exception:
        pass
    return default


def _extraer_padding(kwargs: dict) -> Tuple[int, int]:
    pad = kwargs.pop("padding", None)
    if pad is None:
        return 0, 0
    if isinstance(pad, int):
        return pad, pad
    if isinstance(pad, (tuple, list)):
        if len(pad) == 1:
            return pad[0], pad[0]
        elif len(pad) >= 2:
            return pad[0], pad[1]
    return 0, 0


class PureFrame(tk.Frame):
    """Reemplazo directo de ttk.Frame con color de fondo explícito."""
    def __init__(self, parent=None, **kwargs):
        px, py = _extraer_padding(kwargs)
        bg = kwargs.pop("bg", kwargs.pop("background", _obtener_bg_padre(parent, COLOR_BG_APP)))
        if px and "padx" not in kwargs:
            kwargs["padx"] = px
        if py and "pady" not in kwargs:
            kwargs["pady"] = py
        super().__init__(parent, bg=bg, **kwargs)


class PureLabelFrame(tk.LabelFrame):
    """Reemplazo directo de ttk.LabelFrame con fondo blanco y título azul marino."""
    def __init__(self, parent=None, **kwargs):
        px, py = _extraer_padding(kwargs)
        if not px:
            px = 8
        if not py:
            py = 6
        bg = kwargs.pop("bg", kwargs.pop("background", COLOR_BG_PANEL))
        fg = kwargs.pop("fg", kwargs.pop("foreground", COLOR_PRIMARIO))
        font = kwargs.pop("font", ("Helvetica", 10, "bold"))
        super().__init__(
            parent,
            bg=bg,
            fg=fg,
            font=font,
            padx=px,
            pady=py,
            bd=1,
            relief=tk.SOLID,
            **kwargs
        )


class PureLabel(tk.Label):
    """Reemplazo directo de ttk.Label con contraste garantizado."""
    def __init__(self, parent=None, **kwargs):
        fg = kwargs.pop("foreground", kwargs.pop("fg", COLOR_TEXTO))
        bg = kwargs.pop("background", kwargs.pop("bg", _obtener_bg_padre(parent, COLOR_BG_PANEL)))
        font = kwargs.pop("font", ("Helvetica", 10))
        super().__init__(parent, bg=bg, fg=fg, font=font, **kwargs)

    def config(self, **kwargs):
        if "foreground" in kwargs:
            kwargs["fg"] = kwargs.pop("foreground")
        if "background" in kwargs:
            kwargs["bg"] = kwargs.pop("background")
        super().config(**kwargs)

    configure = config


class PureButton(tk.Label):
    """
    Botón dibujado mediante tk.Label para evitar el bug de NSButton en macOS Dark Mode
    (donde tk.Button y ttk.Button muestran texto blanco sobre fondo blanco).
    """
    def __init__(self, parent=None, text="", command=None, **kwargs):
        kwargs.pop("padding", None)
        self._command = command
        self._bg_normal = kwargs.pop("bg", COLOR_BOTON)
        self._bg_hover = COLOR_BOTON_HOVER
        fg = kwargs.pop("fg", kwargs.pop("foreground", "#FFFFFF"))
        font = kwargs.pop("font", ("Helvetica", 10, "bold"))

        super().__init__(
            parent,
            text=text,
            bg=self._bg_normal,
            fg=fg,
            font=font,
            padx=12,
            pady=5,
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            **kwargs
        )
        self.bind("<Button-1>", self._al_hacer_clic)
        self.bind("<Enter>", lambda e: super(PureButton, self).config(bg=self._bg_hover))
        self.bind("<Leave>", lambda e: super(PureButton, self).config(bg=self._bg_normal))

    def _al_hacer_clic(self, event=None):
        if self._command:
            self._command()

    def config(self, **kwargs):
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "foreground" in kwargs:
            kwargs["fg"] = kwargs.pop("foreground")
        super().config(**kwargs)

    configure = config


class PureEntry(tk.Entry):
    """Campo de texto con fondo blanco, texto oscuro y cursor visible en macOS."""
    def __init__(self, parent=None, **kwargs):
        font = kwargs.pop("font", ("Helvetica", 10))
        super().__init__(
            parent,
            bg="#FFFFFF",
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            selectbackground="#BFDBFE",
            selectforeground=COLOR_TEXTO,
            font=font,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
            highlightcolor=COLOR_BOTON,
            **kwargs
        )


class PureSpinbox(tk.Frame):
    """
    Selector numérico puro en tk (sin NSStepper de Cocoa que falla en Tk 8.5).
    Soporta .get(), .set(), .delete(), .insert() y botones - / +.
    """
    def __init__(self, parent=None, from_=1, to=10, width=5, command=None, **kwargs):
        super().__init__(parent, bg=_obtener_bg_padre(parent))
        self._from = int(from_)
        self._to = int(to)
        self._command = command

        self.entry = PureEntry(self, width=width, justify="center")
        self.entry.pack(side=tk.LEFT)

        btn_menos = tk.Label(
            self, text=" − ", bg="#E2E8F0", fg=COLOR_TEXTO,
            font=("Helvetica", 9, "bold"), relief=tk.RAISED, bd=1, cursor="hand2"
        )
        btn_menos.pack(side=tk.LEFT, padx=(2, 0))
        btn_menos.bind("<Button-1>", lambda e: self._ajustar(-1))

        btn_mas = tk.Label(
            self, text=" + ", bg="#E2E8F0", fg=COLOR_TEXTO,
            font=("Helvetica", 9, "bold"), relief=tk.RAISED, bd=1, cursor="hand2"
        )
        btn_mas.pack(side=tk.LEFT, padx=(2, 0))
        btn_mas.bind("<Button-1>", lambda e: self._ajustar(1))

        self.set(self._from)

    def _ajustar(self, delta: int):
        try:
            val = int(self.entry.get())
        except ValueError:
            val = self._from
        nuevo = max(self._from, min(self._to, val + delta))
        self.set(nuevo)
        if self._command:
            self._command()

    def get(self) -> str:
        return self.entry.get()

    def set(self, valor):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(valor))

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, s):
        self.entry.insert(index, s)

    def bind(self, sequence=None, func=None, add=None):
        self.entry.bind(sequence, func, add)


class PureCombobox(tk.Frame):
    """
    Selector desplegable puro en tk (sin NSPopUpButton de Cocoa).
    Abre un menú emergente al hacer clic.
    """
    def __init__(self, parent=None, values=None, state="readonly", width=20, **kwargs):
        super().__init__(parent, bg=_obtener_bg_padre(parent))
        self._values = list(values) if values else []
        self._valor_actual = self._values[0] if self._values else ""

        self._lbl = tk.Label(
            self,
            text=f"{self._valor_actual}  ▼",
            width=width,
            bg="#FFFFFF",
            fg=COLOR_TEXTO,
            font=("Helvetica", 10),
            relief=tk.SOLID,
            bd=1,
            padx=6,
            pady=3,
            anchor="w",
            cursor="hand2"
        )
        self._lbl.pack(fill=tk.X)
        self._lbl.bind("<Button-1>", self._mostrar_menu)

    def _mostrar_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        for val in self._values:
            menu.add_command(label=str(val), command=lambda v=val: self._seleccionar_item(v))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _seleccionar_item(self, valor: str):
        self.set(valor)
        try:
            self.event_generate("<<ComboboxSelected>>")
        except Exception:
            pass

    def get(self) -> str:
        return self._valor_actual

    def set(self, valor: str):
        self._valor_actual = str(valor)
        self._lbl.config(text=f"{self._valor_actual}  ▼")

    def current(self, index: int = None):
        if index is not None and 0 <= index < len(self._values):
            self.set(self._values[index])
        return self._values.index(self._valor_actual) if self._valor_actual in self._values else -1


class PurePanedWindow(tk.Frame):
    """Contenedor dividido horizontal o verticalmente usando Grid puro."""
    def __init__(self, parent=None, orient=tk.HORIZONTAL, **kwargs):
        super().__init__(parent, bg=_obtener_bg_padre(parent, COLOR_BG_APP))
        self._orient = orient
        self._count = 0
        self.grid_rowconfigure(0, weight=1)

    def add(self, child, weight=1):
        if self._orient == tk.HORIZONTAL:
            self.grid_columnconfigure(self._count, weight=weight)
            child.grid(row=0, column=self._count, sticky="nsew", padx=4, pady=2)
        else:
            self.grid_rowconfigure(self._count, weight=weight)
            self.grid_columnconfigure(0, weight=1)
            child.grid(row=self._count, column=0, sticky="nsew", padx=2, pady=4)
        self._count += 1


class PureNotebook(tk.Frame):
    """
    Cuaderno de pestañas 100% dibujado en tk puro (sin NSTabView de Cocoa).
    Muestra únicamente la pestaña activa evitando que Tk 8.5 encime vistas ocultas.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, bg=COLOR_BG_APP)
        self.barra_tabs = tk.Frame(self, bg="#CBD5E1", padx=4, pady=4)
        self.barra_tabs.pack(side=tk.TOP, fill=tk.X)

        self.contenedor = tk.Frame(self, bg=COLOR_BG_PANEL, bd=1, relief=tk.SOLID)
        self.contenedor.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._tabs = []  # Lista de dicts: {'frame': widget, 'btn': label_btn, 'text': str}
        self._indice_actual = -1

    def add(self, child, text="Pestaña"):
        idx = len(self._tabs)
        btn = tk.Label(
            self.barra_tabs,
            text=f"  {text.strip()}  ",
            font=("Helvetica", 10, "bold"),
            padx=8,
            pady=5,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1
        )
        btn.pack(side=tk.LEFT, padx=2, pady=1)
        btn.bind("<Button-1>", lambda e, i=idx: self.select(i))

        self._tabs.append({"frame": child, "btn": btn, "text": text})

        if self._indice_actual == -1:
            self.select(0)
        else:
            self._actualizar_estilos()

    def select(self, index: int = None):
        if index is None:
            return self._indice_actual
        if not (0 <= index < len(self._tabs)):
            return

        # Ocultar pestaña anterior
        if 0 <= self._indice_actual < len(self._tabs):
            self._tabs[self._indice_actual]["frame"].pack_forget()

        self._indice_actual = index
        frame_activo = self._tabs[index]["frame"]
        frame_activo.pack(in_=self.contenedor, fill=tk.BOTH, expand=True)
        self._actualizar_estilos()

    def _actualizar_estilos(self):
        for i, item in enumerate(self._tabs):
            if i == self._indice_actual:
                item["btn"].config(bg=COLOR_PRIMARIO, fg="#FFFFFF", relief=tk.SUNKEN)
            else:
                item["btn"].config(bg="#E2E8F0", fg=COLOR_TEXTO, relief=tk.RAISED)

    def tabs(self):
        return tuple(str(t["frame"]) for t in self._tabs)


class CompatTTK:
    """Espacio de nombres compatible con 'ttk' pero respaldado por widgets tk puros."""
    Frame = PureFrame
    LabelFrame = PureLabelFrame
    Label = PureLabel
    Button = PureButton
    Entry = PureEntry
    Spinbox = PureSpinbox
    Combobox = PureCombobox
    PanedWindow = PurePanedWindow
    Notebook = PureNotebook


# Instancia global que reemplaza a tkinter.ttk sin ningún bug de Cocoa
ttk_seguro = CompatTTK()


class TablaResultados(PureFrame):
    """
    Tabla de resultados construida en tk.Text + encabezados tk.Label (Cero NSScroller / Treeview).
    Funciona perfectamente en macOS Tk 8.5 sin barras flotantes y con scroll de trackpad/rueda.
    """

    def __init__(self, parent, columnas: List[str], encabezados: List[str], anchos: Optional[List[int]] = None):
        super().__init__(parent, bg=COLOR_BG_PANEL)
        self.columnas = columnas
        self.encabezados = encabezados
        # Convertir anchos en píxeles a ancho aproximado en caracteres monoespaciados
        self.anchos_chars = []
        for i in range(len(columnas)):
            px = anchos[i] if (anchos and i < len(anchos)) else 110
            chars = max(8, int(px / 7.5))
            self.anchos_chars.append(chars)

        # Barra superior con título y botones de desplazamiento
        barra_top = tk.Frame(self, bg=COLOR_PRIMARIO, padx=6, pady=4)
        barra_top.pack(fill=tk.X)

        linea_encabezado = self._formatear_fila(encabezados)
        self.lbl_header = tk.Label(
            barra_top,
            text=linea_encabezado,
            bg=COLOR_PRIMARIO,
            fg="#FFFFFF",
            font=("Courier", 10, "bold"),
            anchor="w",
            justify="left"
        )
        self.lbl_header.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botones compactos para subir/bajar por si no usa rueda de ratón
        btn_up = tk.Label(barra_top, text=" ▲ ", bg="#3B82F6", fg="#FFFFFF", font=("Helvetica", 8, "bold"), cursor="hand2")
        btn_up.pack(side=tk.RIGHT, padx=2)
        btn_up.bind("<Button-1>", lambda e: self.txt.yview_scroll(-4, "units"))

        btn_dn = tk.Label(barra_top, text=" ▼ ", bg="#3B82F6", fg="#FFFFFF", font=("Helvetica", 8, "bold"), cursor="hand2")
        btn_dn.pack(side=tk.RIGHT, padx=2)
        btn_dn.bind("<Button-1>", lambda e: self.txt.yview_scroll(4, "units"))

        # Área de filas con tk.Text puro
        self.txt = tk.Text(
            self,
            height=12,
            bg="#FFFFFF",
            fg=COLOR_TEXTO,
            font=("Courier", 10),
            wrap="none",
            relief=tk.SOLID,
            bd=1,
            padx=6,
            pady=4,
            highlightthickness=0
        )
        self.txt.pack(fill=tk.BOTH, expand=True)
        self.txt.tag_configure("par", background="#F8FAFC", foreground=COLOR_TEXTO)
        self.txt.tag_configure("impar", background="#FFFFFF", foreground=COLOR_TEXTO)
        self.txt.bind("<MouseWheel>", self._on_mousewheel)
        self.txt.bind("<Button-4>", lambda e: self.txt.yview_scroll(-3, "units"))
        self.txt.bind("<Button-5>", lambda e: self.txt.yview_scroll(3, "units"))
        self._num_filas = 0

    def _on_mousewheel(self, event):
        if sys.platform.startswith("win"):
            pasos = int(-1 * (event.delta / 120))
        elif sys.platform == "darwin":
            pasos = int(-1 * event.delta)
        else:
            pasos = -1 if event.delta > 0 else 1
        self.txt.yview_scroll(pasos if pasos != 0 else -1, "units")
        return "break"

    def _formatear_fila(self, valores: Tuple) -> str:
        celdas = []
        for i, val in enumerate(valores):
            ancho = self.anchos_chars[i] if i < len(self.anchos_chars) else 14
            texto = str(val)
            if len(texto) > ancho - 1:
                texto = texto[:ancho - 1]
            celdas.append(texto.center(ancho))
        return "│".join(celdas)

    def limpiar(self):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        self._num_filas = 0

    def agregar_fila(self, valores: tuple):
        self.txt.config(state=tk.NORMAL)
        linea = self._formatear_fila(valores) + "\n"
        tag = "par" if self._num_filas % 2 == 0 else "impar"
        self.txt.insert(tk.END, linea, tag)
        self._num_filas += 1


class EditorMatriz(PureLabelFrame):
    """
    Editor dinámico de matrices n x n o sistemas lineales [A | b]
    100% compatible con macOS Dark Mode y Tk 8.5.
    """

    def __init__(self, parent, titulo: str = "Matriz / Sistema", n_inicial: int = 3, con_vector_b: bool = True):
        super().__init__(parent, text=titulo, padding=10)
        self.con_vector_b = con_vector_b
        self.n = n_inicial
        self.entries_A: List[List[PureEntry]] = []
        self.entries_b: List[PureEntry] = []

        barra_n = PureFrame(self, bg=COLOR_BG_PANEL)
        barra_n.pack(fill=tk.X, pady=(0, 8))

        PureLabel(barra_n, text="Dimensión (n):", font=('Helvetica', 10, 'bold'), bg=COLOR_BG_PANEL).pack(side=tk.LEFT, padx=(0, 6))
        self.spin_n = PureSpinbox(barra_n, from_=2, to=8, width=4, command=self._cambiar_dimension)
        self.spin_n.set(self.n)
        self.spin_n.pack(side=tk.LEFT, padx=(0, 10))
        self.spin_n.bind('<Return>', lambda e: self._cambiar_dimension())

        PureButton(barra_n, text="Actualizar Tamaño", command=self._cambiar_dimension).pack(side=tk.LEFT)

        self.grid_frame = PureFrame(self, bg=COLOR_BG_PANEL)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        self._construir_cuadricula()

    def _cambiar_dimension(self):
        try:
            val = int(self.spin_n.get())
            if 2 <= val <= 8:
                self.n = val
                self._construir_cuadricula()
            else:
                messagebox.showwarning("Dimensión", "La dimensión debe ser un entero entre 2 y 8.")
                self.spin_n.set(self.n)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número entero válido para n.")

    def _construir_cuadricula(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.entries_A = []
        self.entries_b = []

        for j in range(self.n):
            lbl = PureLabel(self.grid_frame, text=f"x{j+1}", font=('Helvetica', 9, 'bold'), bg=COLOR_BG_PANEL)
            lbl.grid(row=0, column=j, padx=3, pady=2)

        if self.con_vector_b:
            lbl_b = PureLabel(self.grid_frame, text="|  b", font=('Helvetica', 9, 'bold'), foreground=COLOR_PRIMARIO, bg=COLOR_BG_PANEL)
            lbl_b.grid(row=0, column=self.n, padx=6, pady=2)

        for i in range(self.n):
            fila_entries = []
            for j in range(self.n):
                e = PureEntry(self.grid_frame, width=8, justify='center')
                e.insert(0, "1.0" if i == j else "0.0")
                e.grid(row=i + 1, column=j, padx=3, pady=3)
                fila_entries.append(e)
            self.entries_A.append(fila_entries)

            if self.con_vector_b:
                eb = PureEntry(self.grid_frame, width=8, justify='center')
                eb.insert(0, "1.0")
                eb.grid(row=i + 1, column=self.n, padx=(10, 3), pady=3)
                self.entries_b.append(eb)

    def obtener_matriz(self) -> List[List[float]]:
        A = []
        for i in range(self.n):
            fila = []
            for j in range(self.n):
                val_str = self.entries_A[i][j].get().strip()
                try:
                    fila.append(float(val_str))
                except ValueError:
                    raise ValueError(f"Valor no numérico en la celda A[{i+1},{j+1}]: '{val_str}'")
            A.append(fila)
        return A

    def obtener_vector_b(self) -> List[float]:
        if not self.con_vector_b:
            return []
        b = []
        for i in range(self.n):
            val_str = self.entries_b[i].get().strip()
            try:
                b.append(float(val_str))
            except ValueError:
                raise ValueError(f"Valor no numérico en el término independiente b[{i+1}]: '{val_str}'")
        return b

    def cargar_datos(self, A: List[List[float]], b: Optional[List[float]] = None):
        nuevo_n = len(A)
        self.n = nuevo_n
        self.spin_n.set(nuevo_n)
        self._construir_cuadricula()

        for i in range(self.n):
            for j in range(self.n):
                self.entries_A[i][j].delete(0, tk.END)
                self.entries_A[i][j].insert(0, f"{A[i][j]:.4g}")
            if self.con_vector_b and b is not None and i < len(b):
                self.entries_b[i].delete(0, tk.END)
                self.entries_b[i].insert(0, f"{b[i]:.4g}")

    def limpiar(self):
        for i in range(self.n):
            for j in range(self.n):
                self.entries_A[i][j].delete(0, tk.END)
                self.entries_A[i][j].insert(0, "0.0")
            if self.con_vector_b:
                self.entries_b[i].delete(0, tk.END)
                self.entries_b[i].insert(0, "0.0")


class CanvasGraficador(PureFrame):
    """Graficador 2D nativo en tk.Canvas."""

    def __init__(self, parent, ancho: int = 420, alto: int = 260):
        super().__init__(parent, bg=COLOR_BG_PANEL)
        self.ancho = ancho
        self.alto = alto

        self.canvas = tk.Canvas(
            self,
            width=ancho,
            height=alto,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground=COLOR_BORDE
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.dibujar_mensaje("Ingresa una función y haz clic en 'Resolver' para ver la gráfica")

    def dibujar_mensaje(self, mensaje: str):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.ancho / 2, self.alto / 2,
            text=mensaje,
            fill="#64748B",
            font=('Helvetica', 10, 'italic'),
            width=self.ancho - 40,
            justify='center'
        )

    def graficar_funcion(
        self,
        expr: str,
        x_min: float,
        x_max: float,
        puntos_destacados: Optional[List[Tuple[float, float, str]]] = None
    ):
        self.canvas.delete("all")
        if x_min >= x_max:
            x_min, x_max = x_min - 2, x_max + 2

        margen = 38
        w = self.ancho - 2 * margen
        h = self.alto - 2 * margen

        n_puntos = 250
        dx = (x_max - x_min) / n_puntos
        xs = [x_min + i * dx for i in range(n_puntos + 1)]
        ys = []
        valid_points = []

        for x in xs:
            try:
                y = evaluar_funcion(expr, x)
                if not math.isnan(y) and not math.isinf(y) and abs(y) < 1e7:
                    ys.append(y)
                    valid_points.append((x, y))
                else:
                    valid_points.append((x, None))
            except Exception:
                valid_points.append((x, None))

        if not ys:
            self.dibujar_mensaje("No fue posible evaluar la función en este intervalo.")
            return

        y_min = min(ys)
        y_max = max(ys)

        if y_min > 0:
            y_min = 0.0
        if y_max < 0:
            y_max = 0.0
        if abs(y_max - y_min) < 1e-6:
            y_max += 1.0
            y_min -= 1.0

        rango_y = y_max - y_min
        y_min -= 0.1 * rango_y
        y_max += 0.1 * rango_y
        rango_y = y_max - y_min

        def to_px(x_val):
            return margen + ((x_val - x_min) / (x_max - x_min)) * w

        def to_py(y_val):
            return (self.alto - margen) - ((y_val - y_min) / rango_y) * h

        # 1. Cuadrícula
        n_lineas_x = 6
        for i in range(n_lineas_x + 1):
            gx = x_min + i * (x_max - x_min) / n_lineas_x
            px = to_px(gx)
            self.canvas.create_line(px, margen, px, self.alto - margen, fill="#E2E8F0")
            self.canvas.create_text(px, self.alto - margen + 12, text=f"{gx:.2g}", fill="#475569", font=('Helvetica', 8))

        n_lineas_y = 5
        for i in range(n_lineas_y + 1):
            gy = y_min + i * rango_y / n_lineas_y
            py = to_py(gy)
            self.canvas.create_line(margen, py, self.ancho - margen, py, fill="#E2E8F0")
            self.canvas.create_text(margen - 18, py, text=f"{gy:.2g}", fill="#475569", font=('Helvetica', 8))

        # 2. Ejes X e Y
        if y_min <= 0 <= y_max:
            py0 = to_py(0)
            self.canvas.create_line(margen - 4, py0, self.ancho - margen + 4, py0, fill="#0F172A", width=2)
            self.canvas.create_text(self.ancho - margen + 12, py0, text="X", fill="#0F172A", font=('Helvetica', 9, 'bold'))

        if x_min <= 0 <= x_max:
            px0 = to_px(0)
            self.canvas.create_line(px0, margen - 4, px0, self.alto - margen + 4, fill="#0F172A", width=2)
            self.canvas.create_text(px0, margen - 10, text="Y", fill="#0F172A", font=('Helvetica', 9, 'bold'))

        # 3. Curva f(x)
        segmento = []
        for x, y in valid_points:
            if y is not None:
                px = to_px(x)
                py = to_py(y)
                py_clamped = max(margen, min(self.alto - margen, py))
                segmento.append((px, py_clamped))
            else:
                if len(segmento) >= 2:
                    coords = [coord for pt in segmento for coord in pt]
                    self.canvas.create_line(coords, fill="#1D4ED8", width=2, smooth=True)
                segmento = []

        if len(segmento) >= 2:
            coords = [coord for pt in segmento for coord in pt]
            self.canvas.create_line(coords, fill="#1D4ED8", width=2, smooth=True)

        # 4. Puntos destacados
        if puntos_destacados:
            for px_val, py_val, label in puntos_destacados:
                cx = to_px(px_val)
                cy = to_py(py_val)
                r = 5
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#DC2626", outline="#991B1B", width=2)
                self.canvas.create_text(cx + 8, cy - 10, text=label, fill="#991B1B", font=('Helvetica', 9, 'bold'), anchor='w')
