"""
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "sales.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"
CSV_FILE = SUBMISSION_DIR / "cohort_retention.csv"
PNG_FILE = SUBMISSION_DIR / "cohort_retention_heatmap.png"


def _load_orders() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, usecols=["CustomerID", "OrderDate"])
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df = df.dropna(subset=["CustomerID", "OrderDate"])
    df["order_period"] = df["OrderDate"].dt.to_period("M")
    df["cohort_period"] = df.groupby("CustomerID")["order_period"].transform("min")
    df["period_index"] = (
        (df["order_period"].dt.year - df["cohort_period"].dt.year) * 12
        + (df["order_period"].dt.month - df["cohort_period"].dt.month)
    )
    return df


def _build_table(df: pd.DataFrame) -> pd.DataFrame:
    table = (
        df.groupby(["cohort_period", "period_index"])["CustomerID"]
        .nunique()
        .reset_index(name="active_customers")
    )
    sizes = table[table["period_index"] == 0][["cohort_period", "active_customers"]]
    sizes = sizes.rename(columns={"active_customers": "cohort_size"})
    table = table.merge(sizes, on="cohort_period", how="left")
    table["retention_rate"] = table["active_customers"] / table["cohort_size"]
    table = table.sort_values(["cohort_period", "period_index"]).reset_index(drop=True)
    table["cohort_month"] = table["cohort_period"].dt.strftime("%Y-%m")
    return table


def _retention_matrix(table: pd.DataFrame, last_period) -> pd.DataFrame:
    matrix = table.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    max_index = int(table["period_index"].max())
    matrix = matrix.reindex(columns=range(max_index + 1))

    # Dentro de la ventana observable, la ausencia de compras sí es 0;
    # fuera de ella el valor queda vacío (NaN).
    cohorts = table.drop_duplicates("cohort_month").set_index("cohort_month")[
        "cohort_period"
    ]
    for cohort_month, cohort_period in cohorts.items():
        observable = (
            (last_period.year - cohort_period.year) * 12
            + (last_period.month - cohort_period.month)
        )
        for col in matrix.columns:
            if col <= observable and pd.isna(matrix.loc[cohort_month, col]):
                matrix.loc[cohort_month, col] = 0.0
    return matrix


def _plot_heatmap(matrix: pd.DataFrame) -> None:
    values = matrix.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(values)

    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad(color="white")

    fig, ax = plt.subplots(figsize=(1.0 * len(matrix.columns) + 3, 0.6 * len(matrix) + 2))
    image = ax.imshow(masked, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if np.isnan(value):
                continue
            color = "white" if value > 0.5 else "black"
            ax.text(j, i, f"{value:.0%}", ha="center", va="center", color=color, fontsize=9)

    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_xlabel("Meses desde la primera compra (period_index)")
    ax.set_ylabel("Cohorte (mes de primera compra)")
    ax.set_title("Retención de clientes por cohorte")

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))

    fig.tight_layout()
    fig.savefig(PNG_FILE, dpi=150)
    plt.close(fig)


def build_cohort_analysis() -> pd.DataFrame:
    orders = _load_orders()
    table = _build_table(orders)

    result = table[
        ["cohort_month", "period_index", "active_customers", "cohort_size", "retention_rate"]
    ].copy()

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(CSV_FILE, index=False)

    matrix = _retention_matrix(table, last_period=orders["order_period"].max())
    _plot_heatmap(matrix)

    return result