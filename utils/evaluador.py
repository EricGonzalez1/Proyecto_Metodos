"""
Módulo de Evaluación Matemática Segura
Permite evaluar expresiones f(x) introducidas por el usuario sin dependencias externas.
Soporta funciones de la biblioteca estándar 'math' y realiza análisis numérico de derivadas.
"""

import math
import re

# Diccionario seguro de funciones y constantes matemáticas permitidas
MATH_SCOPE = {
    # Constantes
    'pi': math.pi,
    'e': math.e,
    # Funciones trigonométricas
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    # Funciones hiperbólicas
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    # Exponenciales y logarítmicas
    'exp': math.exp,
    'log': math.log,        # log natural
    'ln': math.log,         # alias común de log natural
    'log10': math.log10,
    'log2': math.log2,
    # Raíz y potencias
    'sqrt': math.sqrt,
    # Redondeo y valor absoluto
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
}


def sanitizar_expresion(expr: str) -> str:
    """
    Limpia y normaliza la expresión matemática ingresada por el usuario:
    - Convierte potencias '^' a '**'
    - Reemplaza 'ln(' por 'log('
    - Permite multiplicación implícita (ej. 2x -> 2*x, 3(x+1) -> 3*(x+1))
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("La expresión matemática no puede estar vacía.")

    # Reemplazo de potencia
    expr = expr.replace('^', '**')

    # Reemplazo de ln por log
    expr = re.sub(r'\bln\(', 'log(', expr)

    # Permitir número seguido de 'x' o '(' -> ej. 2x -> 2*x, 2( -> 2*(
    expr = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr)

    # Permitir 'x' seguido de '(' -> x( -> x*(
    expr = re.sub(r'([xX])(\()', r'\1*\2', expr)

    # Permitir ')' seguido de número, 'x' o '(' -> ej. )( -> )*(, )2 -> )*2
    expr = re.sub(r'(\))([\d[a-zA-Z\(])', r'\1*\2', expr)

    return expr


def evaluar_funcion(expr: str, x_val: float) -> float:
    """
    Evalúa f(x) en x = x_val de manera segura.
    """
    expr_limpia = sanitizar_expresion(expr)
    contexto = dict(MATH_SCOPE)
    contexto['x'] = float(x_val)
    contexto['X'] = float(x_val)

    try:
        # Se bloquean los builtins por seguridad
        resultado = eval(expr_limpia, {"__builtins__": {}}, contexto)
        return float(resultado)
    except ZeroDivisionError:
        raise ZeroDivisionError(f"División entre cero al evaluar en x = {x_val}")
    except ValueError as ve:
        raise ValueError(f"Error de dominio matemático en x = {x_val}: {ve}")
    except Exception as e:
        raise ValueError(f"Error al evaluar '{expr}' en x = {x_val}: {e}")


def derivada_numerica(expr: str, x_val: float, h: float = 1e-7) -> float:
    """
    Aproximación de la primera derivada f'(x) mediante diferencias centrales:
    f'(x) ≈ (f(x + h) - f(x - h)) / (2h)
    """
    f_adelante = evaluar_funcion(expr, x_val + h)
    f_atras = evaluar_funcion(expr, x_val - h)
    return (f_adelante - f_atras) / (2.0 * h)


def segunda_derivada_numerica(expr: str, x_val: float, h: float = 1e-5) -> float:
    """
    Aproximación de la segunda derivada f''(x) mediante diferencias centrales:
    f''(x) ≈ (f(x + h) - 2f(x) + f(x - h)) / (h^2)
    """
    f_adelante = evaluar_funcion(expr, x_val + h)
    f_centro = evaluar_funcion(expr, x_val)
    f_atras = evaluar_funcion(expr, x_val - h)
    return (f_adelante - 2.0 * f_centro + f_atras) / (h ** 2)
