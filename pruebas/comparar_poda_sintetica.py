"""
Compara la búsqueda con y sin poda sobre el oráculo sintético.

Usa el mismo código del notebook notebooks/01_busqueda.ipynb (a través de
prueba_busqueda_simulada.py) con 50 configuraciones óptimas elegidas al azar.
La versión sin poda es el mismo código con un umbral de poda inalcanzable.

Uso, desde la raíz del repositorio:

    python pruebas/comparar_poda_sintetica.py
"""

import contextlib
import io
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prueba_busqueda_simulada as P  # noqa: E402

N_OPTIMOS = 50
SEMILLA_OPTIMOS = 2026


def correr(optima, reinicios, con_poda):
    P.OPTIMA.clear()
    P.OPTIMA.update(optima)
    oraculo = P.OraculoSintetico()
    entorno = {
        "oraculo": oraculo, "INSTANCIAS": [{"id": i} for i in range(100)],
        "RANURAS": P.RANURAS, "OPCIONES": {r: list(range(8)) for r in P.RANURAS},
        "CATALOGO": {r: [f"opción {i}" for i in range(8)] for r in P.RANURAS},
        "SEMILLA": 1, "MAX_PASADAS": 3, "N_REINICIOS": reinicios,
        "UMBRAL_PODA": 3 if con_poda else 10**9, "CONTEXTOS_PODA": 2, "MIN_VIVAS": 4,
        "TEMPERATURA": 0.0, "curva": lambda h: None,
        "random": random, "time": time, "Counter": Counter,
    }
    marcas = ("def evaluar_registrada", "def podar", "iniciales = [")
    with contextlib.redirect_stdout(io.StringIO()):
        for src in P.celdas_de_codigo():
            if any(m in src for m in marcas):
                exec(compile(src, str(P.NOTEBOOK), "exec"), entorno)
    return oraculo.consultas, entorno["MEJOR_PRECISION"] == 1.0


def main():
    rng = random.Random(SEMILLA_OPTIMOS)
    optimos = [{r: rng.randrange(8) for r in P.RANURAS} for _ in range(N_OPTIMOS)]
    print(f"{'variante':24} {'consultas (media)':>18} {'mín':>5} {'máx':>5} {'óptimo':>8}")
    for nombre, reinicios, con_poda in [("sin poda, 2 reinicios", 2, False),
                                        ("con poda, 2 reinicios", 2, True),
                                        ("sin poda, 3 reinicios", 3, False),
                                        ("con poda, 3 reinicios", 3, True)]:
        res = [correr(op, reinicios, con_poda) for op in optimos]
        q = [c for c, _ in res]
        print(f"{nombre:24} {sum(q) / len(q):18.1f} {min(q):5} {max(q):5} "
              f"{sum(ok for _, ok in res):5}/{N_OPTIMOS}")


if __name__ == "__main__":
    main()
