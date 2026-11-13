"""
Script de prueba integral para verificar los 10 métodos solicitados por el profesor:
- Unidad 2: Bisección, Newton y Secante
- Unidad 3: Gauss-Jordan, Gauss-Seidel y Jacobi
- Unidad 4: Doolittle y Crout
- Unidad 5: Potencia y Potencia Inversa
"""

from unidad2_raices.tema2_1_biseccion import biseccion
from unidad2_raices.tema2_3_newton import newton_raphson
from unidad2_raices.tema2_4_secante import secante

from unidad3_sistemas.tema3_2_gauss_jordan import gauss_jordan
from unidad3_sistemas.tema3_4_gauss_seidel import metodo_gauss_seidel
from unidad3_sistemas.tema3_4_jacobi import metodo_jacobi

from unidad4_factorizacion.tema4_3_doolittle import factorizacion_doolittle
from unidad4_factorizacion.tema4_4_crout import factorizacion_crout

from unidad5_eigen.tema5_1_potencia import metodo_potencia_maximo
from unidad5_eigen.tema5_2_potencia_inversa import metodo_potencia_inversa


def probar_todo():
    print("Verificando los 10 métodos del proyecto...")

    # --- UNIDAD 2 ---
    # 1. Bisección (con intervalo y con un solo valor inicial)
    _, res_bis = biseccion("x^3 - 2*x - 5", 2.0, 3.0, 1e-5, 100)
    assert abs(res_bis["raiz"] - 2.094551) < 1e-3, "Fallo en Bisección con intervalo"
    _, res_bis_auto = biseccion("x^3 - 2*x - 5", 2.0, None, 1e-5, 100)
    assert abs(res_bis_auto["raiz"] - 2.094551) < 1e-3, "Fallo en Bisección con valor inicial único"

    # 2. Newton
    _, res_newt = newton_raphson("cos(x) - x", 1.0, "-sin(x) - 1", 1e-5, 50)
    assert abs(res_newt["raiz"] - 0.739085) < 1e-4, "Fallo en Newton"

    # 3. Secante
    _, res_sec = secante("exp(-x^2) - x", 0.0, 1.0, 1e-5, 50)
    assert abs(res_sec["raiz"] - 0.652918) < 1e-4, "Fallo en Secante"
    print("✔ Unidad 2 (Bisección, Newton y Secante) verificada.")

    # --- UNIDAD 3 ---
    # 4. Gauss-Jordan
    A3 = [[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]]
    b3 = [8.0, -11.0, -3.0]
    x_gj, _ = gauss_jordan(A3, b3)
    assert abs(x_gj[0] - 2.0) < 1e-6 and abs(x_gj[1] - 3.0) < 1e-6 and abs(x_gj[2] + 1.0) < 1e-6, "Fallo en Gauss-Jordan"

    # 5. Gauss-Seidel
    A_dom = [[10.0, 2.0, -1.0], [-2.0, 10.0, 1.0], [1.0, -2.0, 10.0]]
    b_dom = [7.0, 8.0, 6.0]
    _, x_gs, conv_gs = metodo_gauss_seidel(A_dom, b_dom, tol=1e-6, max_iter=100)
    assert conv_gs, "Fallo en Gauss-Seidel"

    # 6. Jacobi
    _, x_jac, conv_jac = metodo_jacobi(A_dom, b_dom, tol=1e-6, max_iter=100)
    assert conv_jac and abs(x_jac[0] - x_gs[0]) < 1e-4, "Fallo en Jacobi"
    print("✔ Unidad 3 (Gauss-Jordan, Gauss-Seidel y Jacobi) verificada.")

    # --- UNIDAD 4 ---
    A4 = [[2.0, -1.0, -2.0], [-4.0, 6.0, 3.0], [-4.0, -2.0, 8.0]]
    b4 = [-1.0, 13.0, -6.0]
    # 7. Doolittle
    _, _, x_doo, _ = factorizacion_doolittle(A4, b4)
    assert abs(x_doo[0] - 2.0) < 1e-5 and abs(x_doo[1] - 3.0) < 1e-5 and abs(x_doo[2] - 1.0) < 1e-5, "Fallo en Doolittle"

    # 8. Crout
    _, _, x_crout, _ = factorizacion_crout(A4, b4)
    assert abs(x_crout[0] - 2.0) < 1e-5 and abs(x_crout[1] - 3.0) < 1e-5 and abs(x_crout[2] - 1.0) < 1e-5, "Fallo en Crout"
    print("✔ Unidad 4 (Doolittle y Crout) verificada.")

    # --- UNIDAD 5 ---
    A5 = [[4.0, 1.0, 2.0], [1.0, 2.0, 0.0], [2.0, 0.0, 5.0]]
    # 9. Potencia (Valor propio máximo)
    lam_max, vec_max, _, _ = metodo_potencia_maximo(A5, tol=1e-6, max_iter=200)
    assert abs(lam_max - 6.645751) < 1e-3 and abs(max(vec_max, key=abs)) == 1.0, f"Fallo en Potencia: {lam_max}"

    # 10. Potencia Inversa (Valor propio mínimo)
    lam_min, vec_min, _, _ = metodo_potencia_inversa(A5, tol=1e-6, max_iter=200)
    assert abs(lam_min - 1.354248) < 1e-3 and abs(max(vec_min, key=abs)) == 1.0, f"Fallo en Potencia Inversa: {lam_min}"
    print("✔ Unidad 5 (Potencia y Potencia Inversa) verificada.")

    print("\n========================================================")
    print("¡TODOS LOS 10 MÉTODOS REQUERIDOS PASARON EXITOSAMENTE!")
    print("========================================================")


if __name__ == "__main__":
    probar_todo()
