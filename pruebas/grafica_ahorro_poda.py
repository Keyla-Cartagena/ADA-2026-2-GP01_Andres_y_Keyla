"""
Genera resultados/ahorro_poda.png: configuraciones evaluadas con y sin poda,
con los mismos dos reinicios, en los tres escenarios de la sección 7.5 del informe.

Las cifras son las de las tablas 12, 13 y 14 del informe:
- datos del curso: registro de la versión anterior (121 configuraciones distintas)
  y resultados/registro_busqueda.json (98 en los reinicios 1 y 2);
- datos propios: corridas de las dos versiones sobre datos de  prueba/datos_visibles_100.json;
- oráculo sintético: media de pruebas/comparar_poda_sintetica.py sobre 50 óptimos.

Uso, desde la raíz del repositorio:

    python pruebas/grafica_ahorro_poda.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "resultados" / "ahorro_poda.png"

ESCENARIOS = ["Datos del curso", "Datos propios", "Oráculo sintético\n(media de 50 óptimos)"]
SIN_PODA = [121, 149, 90.0]
CON_PODA = [98, 115, 76.4]

AZUL, NARANJA = "#2a78d6", "#eb6834"
SUPERFICIE, TINTA, TINTA_2, REJILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"


def etiqueta(v):
    return f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}".replace(".", ",")


def main():
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)

    ancho, hueco = 0.34, 0.02
    xs = range(len(ESCENARIOS))
    for x, a, b in zip(xs, SIN_PODA, CON_PODA):
        for dx, v, color in ((-(ancho + hueco) / 2, a, AZUL), ((ancho + hueco) / 2, b, NARANJA)):
            ax.bar(x + dx, v, ancho, color=color, edgecolor=SUPERFICIE, linewidth=1, zorder=3)
            ax.text(x + dx, v + 2, etiqueta(v), ha="center", va="bottom", fontsize=9, color=TINTA)
        ahorro = round(100 * (1 - b / a))
        ax.text(x, max(a, b) + 14, f"−{ahorro} %", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=TINTA_2)

    ax.set_xticks(list(xs), ESCENARIOS, fontsize=9, color=TINTA)
    ax.set_ylabel("Configuraciones evaluadas", fontsize=9, color=TINTA_2)
    ax.set_ylim(0, 180)
    ax.tick_params(axis="y", labelsize=8, colors=TINTA_2, length=0)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=REJILLA, linewidth=0.6, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(REJILLA)

    ax.bar(0, 0, color=AZUL, label="Sin poda")
    ax.bar(0, 0, color=NARANJA, label="Con poda guiada por trazas")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=9, ncol=2,
              labelcolor=TINTA, borderaxespad=0.2, handlelength=1.2)
    ax.set_title("Configuraciones evaluadas con los mismos dos reinicios",
                 fontsize=11, color=TINTA, loc="left", pad=26)
    fig.text(0.01, 0.01, "En los tres escenarios la poda llega al mismo resultado o a uno mejor.",
             fontsize=8, color=TINTA_2)

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    SALIDA.parent.mkdir(exist_ok=True)
    fig.savefig(SALIDA, facecolor=SUPERFICIE)
    print("guardada:", SALIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
