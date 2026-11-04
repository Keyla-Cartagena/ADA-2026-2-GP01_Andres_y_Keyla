"""
Prueba de la heurística de búsqueda sin GPU.

Ejecuta las funciones del notebook notebooks/01_busqueda.ipynb contra un oráculo
sintético cuya mejor configuración se conoce de antemano, y comprueba las
propiedades que el manual técnico atribuye al algoritmo.

Uso, desde la raíz del repositorio:

    python pruebas/prueba_busqueda_simulada.py
"""

import json
import random
import time
import zlib
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOTEBOOK = RAIZ / "notebooks" / "01_busqueda.ipynb"
RANURAS = ["rol", "estrategia", "formato", "estilo", "cierre"]

# Configuración óptima del oráculo sintético (no tiene relación con el catálogo real).
OPTIMA = {"rol": 3, "estrategia": 6, "formato": 1, "estilo": 4, "cierre": 7}


class ResultadoSintetico:
    def __init__(self, precision, trazas, n):
        self.precision, self.trazas, self.n = precision, trazas, n


class OraculoSintetico:
    """Cada ranura distinta de la óptima hace fallar un subconjunto fijo de instancias.

    El resultado es determinista: depende solo de la configuración y del id de la
    instancia, igual que el oráculo real con temperatura 0.0.
    """

    def __init__(self):
        self.consultas = 0

    def evaluar(self, config, instancias, semilla=1):
        self.consultas += 1
        malas = [r for r in RANURAS if config[r] != OPTIMA[r]]
        trazas = []
        for x in instancias:
            for r in malas:
                h = zlib.crc32(f"{x['id']}|{r}|{config[r]}".encode())
                if h % 100 < 30:
                    trazas.append({"id": x["id"], "violo": f"familia_{r}",
                                   "salida": "respuesta sintética " * 20})
                    break
        return ResultadoSintetico(1 - len(trazas) / len(instancias), trazas, len(instancias))


def celdas_de_codigo():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    fuentes = []
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = c["source"] if isinstance(c["source"], str) else "".join(c["source"])
        fuentes.append(src)
    return fuentes


def ejecutar_busqueda():
    oraculo = OraculoSintetico()
    entorno = {
        "oraculo": oraculo, "INSTANCIAS": [{"id": i} for i in range(100)],
        "RANURAS": RANURAS, "OPCIONES": {r: list(range(8)) for r in RANURAS},
        "CATALOGO": {r: [f"opción {i}" for i in range(8)] for r in RANURAS},
        "SEMILLA": 1, "MAX_PASADAS": 3, "N_REINICIOS": 3, "UMBRAL_PODA": 3,
        "CONTEXTOS_PODA": 2, "MIN_VIVAS": 4, "TEMPERATURA": 0.0, "curva": lambda h: None,
        "random": random, "time": time, "Counter": Counter,
    }
    marcas = ("def evaluar_registrada", "def podar", "iniciales = [")
    for src in celdas_de_codigo():
        if any(m in src for m in marcas):
            exec(compile(src, str(NOTEBOOK), "exec"), entorno)
    return entorno, oraculo


def main():
    e, oraculo = ejecutar_busqueda()
    mejor = {r: e["MEJOR_CONFIG"][r] for r in RANURAS}
    claves = [tuple(f["config"][r] for r in RANURAS) for f in e["registro"]]

    comprobaciones = [
        ("encuentra la configuración óptima del oráculo sintético", mejor == OPTIMA),
        ("la precisión reportada es 100 %", e["MEJOR_PRECISION"] == 1.0),
        ("ninguna configuración se consulta dos veces", len(claves) == len(set(claves))),
        ("cada consulta nueva queda en el registro", len(claves) == oraculo.consultas),
        ("ningún reinicio termina por debajo de su punto inicial",
         all(r["precision"] >= e["memo"][e["clave"](r["inicial"])]["precision"]
             for r in e["reinicios"])),
        ("toda ranura conserva al menos MIN_VIVAS opciones",
         all(len(v) >= e["MIN_VIVAS"] for v in e["vivas"].values())),
        ("toda poda se apoya en derrotas en al menos CONTEXTOS_PODA vecindarios",
         all(len({tuple(x["vecindario"]) for x in p["evidencia"]}) >= e["CONTEXTOS_PODA"]
             for p in e["podas"])),
        ("cada derrota tiene una pérdida neta de al menos UMBRAL_PODA instancias",
         all(len(x["instancias_perdidas"]) - len(x["instancias_ganadas"]) >= e["UMBRAL_PODA"]
             for p in e["podas"] for x in p["evidencia"])),
        ("las consultas no superan la cota R(1 + I·m·K) = 363",
         oraculo.consultas <= 3 * (1 + 3 * 5 * 8)),
    ]
    fallidas = 0
    for texto, ok in comprobaciones:
        print(("OK    " if ok else "FALLA ") + texto)
        fallidas += not ok
    print(f"\nconsultas al oráculo: {oraculo.consultas} · podas: {len(e['podas'])}")
    raise SystemExit(1 if fallidas else 0)


if __name__ == "__main__":
    main()
