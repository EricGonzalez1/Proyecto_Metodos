# Proyecto de Métodos Numéricos (Multiplataforma: Windows, macOS y Linux)

Sistema interactivo en **Python + Tkinter** (100% biblioteca estándar, sin dependencias externas), estructurado conforme a las indicaciones generales del profesor.

---

## Estructura del Proyecto y Métodos Incluidos

```text
Proyecto_Metodos/
├── main.py                                    # Menú Principal, Menús Secundarios y control de salida
├── Proyecto_Metodos_Windows.pyw               # Ejecutable directo sin consola para Windows (doble clic)
├── Ejecutar_Proyecto_Windows.bat              # Lanzador directo por lotes para Windows (doble clic)
├── Crear_Ejecutable_Windows.bat               # Generador automático de Proyecto_Metodos.exe en Windows
├── Ejecutar_Proyecto.command                  # Ejecutable directo para macOS (doble clic)
├── Proyecto_Metodos.app/                      # Aplicación ejecutable nativa (.app) para macOS
├── Ejecutar_Proyecto_Linux.sh                 # Lanzador ejecutable para Linux
├── test_todos_metodos.py                      # Pruebas automáticas de los 10 métodos
├── utils/
│   ├── evaluador.py                           # Evaluador seguro de funciones no lineales y derivadas
│   ├── algebra_lineal.py                      # Operaciones matriciales y vectoriales
│   └── componentes_gui.py                     # Tablas, editor matricial, graficador 2D y soporte Windows/macOS/Linux
├── unidad2_raices/                            # Unidad 2: Bisección, Newton y Secante
│   ├── tema2_1_biseccion.py                   # Método de Bisección
│   ├── tema2_3_newton.py                      # Método de Newton (Newton-Raphson)
│   └── tema2_4_secante.py                     # Método de la Secante
├── unidad3_sistemas/                          # Unidad 3: Gauss-Jordan, Gauss-Seidel y Jacobi
│   ├── tema3_2_gauss_jordan.py                # Método de Gauss-Jordan
│   ├── tema3_4_gauss_seidel.py                # Método de Gauss-Seidel
│   └── tema3_4_jacobi.py                      # Método de Jacobi
├── unidad4_factorizacion/                     # Unidad 4: Doolittle y Crout
│   ├── tema4_3_doolittle.py                   # Método de Doolittle (A = L·U con L unitaria)
│   └── tema4_4_crout.py                       # Método de Crout (A = L·U con U unitaria)
└── unidad5_eigen/                             # Unidad 5: Potencia y Potencia Inversa
    ├── tema5_1_potencia.py                    # Método de la Potencia (Valor propio máximo y vector propio)
    └── tema5_2_potencia_inversa.py            # Método de la Potencia Inversa (Valor propio mínimo y vector propio)
```

---

## Cómo Ejecutar en cada Sistema Operativo

### En Windows
1. **Doble clic directo (sin consola):** Haz doble clic sobre `Ejecutar_Proyecto_Windows.bat` o `Proyecto_Metodos_Windows.pyw`.
2. **Para generar un archivo `.exe` autónomo (`Proyecto_Metodos.exe`):** Haz doble clic sobre `Crear_Ejecutable_Windows.bat` desde cualquier PC con Windows.
3. **Desde terminal (CMD / PowerShell):**
   ```cmd
   python main.py
   ```

### En macOS
1. **Doble clic directo:** Haz doble clic sobre `Proyecto_Metodos.app` o `Ejecutar_Proyecto.command`.
2. **Desde terminal:**
   ```bash
   python3 main.py
   ```

### En Linux
1. **Doble clic o terminal:**
   ```bash
   ./Ejecutar_Proyecto_Linux.sh
   ```
   o bien:
   ```bash
   python3 main.py
   ```
