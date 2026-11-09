"""
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
"""

import os

import numpy as np
import pandas as pd

DATA_FILE = "data/superstore_orders.csv.gz"
OUTPUT_DIR = "submission"

BAND_LABELS = ["0%", "1%-5%", "6%-10%", "más de 10%"]


def _load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, sep=";", decimal=",", compression="gzip")
    df["is_loss"] = df["Profit"] < 0
    df["loss_amount"] = np.where(df["is_loss"], -df["Profit"], 0.0)
    return df


def _discount_band(discount: pd.Series) -> pd.Series:
    return pd.cut(
        discount,
        bins=[-np.inf, 0, 0.05, 0.10, np.inf],
        labels=BAND_LABELS,
        right=True,
    )


def _metrics(group: pd.DataFrame) -> pd.Series:
    lines = len(group)
    sales = group["Sales"].sum()
    profit = group["Profit"].sum()
    loss_lines = int(group["is_loss"].sum())
    return pd.Series(
        {
            "lines": lines,
            "orders": group["Order ID"].nunique(),
            "sales": sales,
            "profit": profit,
            "profit_margin": profit / sales if sales else np.nan,
            "loss_lines": loss_lines,
            "loss_line_rate": loss_lines / lines if lines else np.nan,
            "lost_profit": group["loss_amount"].sum(),
        }
    )


def _round(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["sales", "profit", "lost_profit"]:
        if col in df:
            df[col] = df[col].round(4)
    for col in ["profit_margin", "loss_line_rate"]:
        if col in df:
            df[col] = df[col].round(4)
    for col in ["lines", "orders", "loss_lines"]:
        if col in df:
            df[col] = df[col].astype(int)
    return df


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = _load_data()

    # 1. Resumen general
    summary = _metrics(df).to_frame().T
    summary = summary[
        [
            "lines",
            "orders",
            "sales",
            "profit",
            "profit_margin",
            "loss_lines",
            "loss_line_rate",
            "lost_profit",
        ]
    ]
    summary = _round(summary).reset_index(drop=True)

    # 2. Resumen por rango de descuento
    df["discount_band"] = _discount_band(df["Discount"])
    discount = (
        df.groupby("discount_band", observed=False)
        .apply(_metrics, include_groups=False)
        .reindex(BAND_LABELS)
        .reset_index()
    )
    discount = discount[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]
    discount = _round(discount)

    # 3. Segmentos prioritarios (segmento x categoría)
    segments = (
        df.groupby(["Customer Segment", "Product Category"])
        .apply(_metrics, include_groups=False)
        .reset_index()
    )
    segments = segments[segments["lines"] >= 100]
    segments = segments.sort_values("lost_profit", ascending=False).head(5)
    segments = segments[
        [
            "Customer Segment",
            "Product Category",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "lost_profit",
        ]
    ]
    segments = _round(segments).reset_index(drop=True)

    # Guardar archivos
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary.to_csv(f"{OUTPUT_DIR}/profitability_summary.csv", index=False)
    discount.to_csv(f"{OUTPUT_DIR}/discount_summary.csv", index=False)
    segments.to_csv(f"{OUTPUT_DIR}/priority_segments.csv", index=False)

    return summary, discount, segments
