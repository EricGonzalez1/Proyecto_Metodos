"""
Módulo de Álgebra Lineal Numérica (100% Python Estándar)
Provee operaciones matriciales fundamentales y resolución de sistemas triangulares
sin requerir NumPy ni bibliotecas externas.
"""

import math
from typing import List, Tuple

Matriz = List[List[float]]
Vector = List[float]


def crear_matriz(filas: int, columnas: int, valor: float = 0.0) -> Matriz:
    """Crea una matriz de dimensiones filas x columnas inicializada con 'valor'."""
    return [[float(valor) for _ in range(columnas)] for _ in range(filas)]


def matriz_identidad(n: int) -> Matriz:
    """Retorna una matriz identidad de tamaño n x n."""
    I = crear_matriz(n, n, 0.0)
    for i in range(n):
        I[i][i] = 1.0
    return I


def copiar_matriz(A: Matriz) -> Matriz:
    """Retorna una copia profunda de la matriz A."""
    return [list(fila) for fila in A]


def copiar_vector(v: Vector) -> Vector:
    """Retorna una copia del vector v."""
    return list(v)


def transponer(A: Matriz) -> Matriz:
    """Retorna la matriz transpuesta A^T."""
    filas = len(A)
    columnas = len(A[0]) if filas > 0 else 0
    return [[A[i][j] for i in range(filas)] for j in range(columnas)]


def multiplicar_matrices(A: Matriz, B: Matriz) -> Matriz:
    """Multiplica dos matrices A (m x p) y B (p x n)."""
    m = len(A)
    p = len(A[0])
    p2 = len(B)
    n = len(B[0])
    if p != p2:
        raise ValueError(f"Dimensiones incompatibles para multiplicación: ({m}x{p}) y ({p2}x{n})")

    C = crear_matriz(m, n, 0.0)
    for i in range(m):
        for k in range(p):
            aik = A[i][k]
            for j in range(n):
                C[i][j] += aik * B[k][j]
    return C


def multiplicar_matriz_vector(A: Matriz, v: Vector) -> Vector:
    """Multiplica una matriz A (m x n) por un vector columna v (n)."""
    m = len(A)
    n = len(A[0])
    if len(v) != n:
        raise ValueError(f"Dimensiones incompatibles: Matriz ({m}x{n}) y Vector ({len(v)})")

    res = [0.0] * m
    for i in range(m):
        res[i] = sum(A[i][j] * v[j] for j in range(n))
    return res


def producto_punto(u: Vector, v: Vector) -> float:
    """Calcula el producto escalar u . v."""
    if len(u) != len(v):
        raise ValueError("Los vectores deben tener la misma dimensión.")
    return sum(a * b for a, b in zip(u, v))


def norma_euclidiana(v: Vector) -> float:
    """Norma L2 de un vector."""
    return math.sqrt(sum(x ** 2 for x in v))


def norma_infinito(v: Vector) -> float:
    """Norma infinito (máximo valor absoluto) de un vector."""
    if not v:
        return 0.0
    return max(abs(x) for x in v)


def norma_infinito_matriz(A: Matriz) -> float:
    """Norma fila máxima ||A||_inf."""
    return max(sum(abs(val) for val in fila) for fila in A)


def sustitucion_adelante(L: Matriz, b: Vector, unos_diagonal: bool = False) -> Vector:
    """
    Resuelve el sistema triangular inferior L * y = b.
    Si 'unos_diagonal' es True, asume que L[i][i] = 1 (como en Doolittle).
    """
    n = len(L)
    y = [0.0] * n
    for i in range(n):
        suma = sum(L[i][j] * y[j] for j in range(i))
        if unos_diagonal:
            y[i] = b[i] - suma
        else:
            if abs(L[i][i]) < 1e-15:
                raise ZeroDivisionError(f"Elemento diagonal nulo en L[{i}][{i}] durante sustitución hacia adelante.")
            y[i] = (b[i] - suma) / L[i][i]
    return y


def sustitucion_atras(U: Matriz, y: Vector, unos_diagonal: bool = False) -> Vector:
    """
    Resuelve el sistema triangular superior U * x = y.
    Si 'unos_diagonal' es True, asume que U[i][i] = 1 (como en Crout).
    """
    n = len(U)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        suma = sum(U[i][j] * x[j] for j in range(i + 1, n))
        if unos_diagonal:
            x[i] = y[i] - suma
        else:
            if abs(U[i][i]) < 1e-15:
                raise ZeroDivisionError(f"Elemento diagonal nulo en U[{i}][{i}] durante sustitución hacia atrás.")
            x[i] = (y[i] - suma) / U[i][i]
    return x


def determinante(A: Matriz) -> float:
    """Calcula el determinante de una matriz n x n mediante eliminación Gaussiana con pivoteo parcial."""
    n = len(A)
    M = copiar_matriz(A)
    det = 1.0

    for i in range(n):
        # Pivoteo parcial
        max_fila = i
        max_val = abs(M[i][i])
        for k in range(i + 1, n):
            if abs(M[k][i]) > max_val:
                max_val = abs(M[k][i])
                max_fila = k

        if max_val < 1e-15:
            return 0.0

        if max_fila != i:
            M[i], M[max_fila] = M[max_fila], M[i]
            det = -det

        pivote = M[i][i]
        det *= pivote

        for k in range(i + 1, n):
            factor = M[k][i] / pivote
            for j in range(i, n):
                M[k][j] -= factor * M[i][j]

    return det


def inversa_gauss_jordan(A: Matriz) -> Tuple[Matriz, List[str]]:
    """
    Calcula la matriz inversa A^(-1) mediante Gauss-Jordan con la matriz aumentada [A | I].
    Retorna la inversa y un registro paso a paso.
    """
    n = len(A)
    pasos: List[str] = []

    # Construir matriz aumentada [A | I]
    aug: Matriz = [A[i] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    pasos.append(f"Matriz aumentada inicial [A | I] de tamaño {n}x{2*n}.")

    for i in range(n):
        # Buscar pivote máximo en la columna i
        max_fila = i
        max_val = abs(aug[i][i])
        for k in range(i + 1, n):
            if abs(aug[k][i]) > max_val:
                max_val = abs(aug[k][i])
                max_fila = k

        if max_val < 1e-15:
            raise ValueError(f"La matriz es singular o casi singular; no tiene inversa única (columna {i+1}).")

        if max_fila != i:
            aug[i], aug[max_fila] = aug[max_fila], aug[i]
            pasos.append(f"Fila {i+1} intercambiada con Fila {max_fila+1} (Pivote = {max_val:.6g}).")

        pivote = aug[i][i]
        # Normalizar fila i
        for j in range(2 * n):
            aug[i][j] /= pivote
        pasos.append(f"Fila {i+1} dividida por el pivote {pivote:.6g}.")

        # Hacer ceros en las demás filas de la columna i
        for k in range(n):
            if k != i:
                factor = aug[k][i]
                if abs(factor) > 1e-15:
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]
                    pasos.append(f"Fila {k+1} = Fila {k+1} - ({factor:.6g}) * Fila {i+1}.")

    # Extraer la matriz inversa de la mitad derecha
    inversa: Matriz = [[aug[i][j + n] for j in range(n)] for i in range(n)]
    pasos.append("Inversión Gauss-Jordan completada con éxito.")
    return inversa, pasos
