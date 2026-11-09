"""
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
"""
from pathlib import Path

import numpy as np
import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

FILES = {
    "letter": DATA_DIR / "historical_requests_letter.csv.gz",
    "web": DATA_DIR / "historical_requests_web.csv.gz",
}

DEADLINE = 15


def _load_channel(channel: str, path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates().reset_index(drop=True)
    df["channel"] = channel
    return df


def _load_data() -> pd.DataFrame:
    df = pd.concat(
        [_load_channel(channel, path) for channel, path in FILES.items()],
        ignore_index=True,
    )

    df["in_date"] = pd.to_datetime(df["in_date"])
    df["out_date"] = pd.to_datetime(df["out_date"])

    df["answered"] = df["out_date"].notna()
    df["year"] = df["in_date"].dt.year

    # Días calendario: diferencia entre respuesta y entrada
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days

    # Días hábiles: lunes a viernes posteriores a la entrada, hasta la
    # respuesta incluida -> intervalo [in_date + 1, out_date + 1)
    df["business_days"] = np.nan
    answered = df["answered"]
    start = (df.loc[answered, "in_date"] + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    end = (df.loc[answered, "out_date"] + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    df.loc[answered, "business_days"] = np.busday_count(start, end)

    df["on_time"] = df["answered"] & (df["business_days"] <= DEADLINE)
    return df


def _counts(group: pd.DataFrame) -> pd.Series:
    requests = len(group)
    answered = int(group["answered"].sum())
    return pd.Series(
        {
            "requests": requests,
            "answered": answered,
            "pending": requests - answered,
            "median_business_days": group.loc[group["answered"], "business_days"].median(),
            "on_time_rate": group["on_time"].sum() / requests,
        }
    )


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = _load_data()

    # 1. Resumen por canal, en orden alfabético
    channel_summary = (
        df.groupby("channel").apply(_counts, include_groups=False).reset_index()
    )
    channel_summary = channel_summary.sort_values("channel").reset_index(drop=True)
    for col in ["requests", "answered", "pending"]:
        channel_summary[col] = channel_summary[col].astype(int)
    channel_summary = channel_summary[
        ["channel", "requests", "answered", "pending", "median_business_days", "on_time_rate"]
    ]

    # 2. Resumen por año y canal
    yearly_summary = (
        df.groupby(["year", "channel"]).apply(_counts, include_groups=False).reset_index()
    )
    yearly_summary = yearly_summary.sort_values(["year", "channel"]).reset_index(drop=True)
    for col in ["requests", "pending"]:
        yearly_summary[col] = yearly_summary[col].astype(int)
    yearly_summary = yearly_summary[["year", "channel", "requests", "pending", "on_time_rate"]]

    # 3. Resumen por día de entrada (lunes a domingo), canales juntos
    df["weekday_number"] = df["in_date"].dt.dayofweek
    day_order = df.groupby("day_name")["weekday_number"].agg(lambda s: s.mode().iloc[0])

    answered = df[df["answered"]]
    entry_day_summary = pd.DataFrame(
        {
            "requests": df.groupby("day_name").size(),
            "median_calendar_days": answered.groupby("day_name")["calendar_days"].median(),
            "median_business_days": answered.groupby("day_name")["business_days"].median(),
        }
    )
    entry_day_summary = entry_day_summary.loc[day_order.sort_values().index]
    entry_day_summary = entry_day_summary.rename_axis("day_name").reset_index()
    entry_day_summary["requests"] = entry_day_summary["requests"].astype(int)
    entry_day_summary = entry_day_summary[
        ["day_name", "requests", "median_calendar_days", "median_business_days"]
    ]

    # Guardar archivos
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    channel_summary.to_csv(SUBMISSION_DIR / "channel_summary.csv", index=False)
    yearly_summary.to_csv(SUBMISSION_DIR / "yearly_summary.csv", index=False)
    entry_day_summary.to_csv(SUBMISSION_DIR / "entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary