import os

import pandas as pd


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    df = pd.read_csv(
        "data/solicitudes_de_credito.csv.gz",
        sep=";",
        index_col=0,  # la primera columna es un índice que no pertenece a los datos
    )

    # 1. Campos de texto: minúsculas, "_" y "-" como espacios, sin espacios sobrantes
    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]
    for columna in columnas_texto:
        df[columna] = (
            df[columna]
            .str.lower()
            .str.replace("_", " ", regex=False)
            .str.replace("-", " ", regex=False)
            .str.split()
            .str.join(" ")
        )

    # 2. Estrato como entero (por ejemplo "02" -> 2)
    df["estrato"] = df["estrato"].astype(int)

    # 3. Monto: quitar "$", separadores de miles, espacios y decimales ".00"
    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(r"\.00$", "", regex=True)
        .astype(float)
        .astype(int)
    )

    # 4. Fechas: vienen como DD/MM/AAAA o AAAA/MM/DD; se unifican en AAAA-MM-DD
    fechas = pd.to_datetime(
        df["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce"
    )
    fechas = fechas.fillna(
        pd.to_datetime(df["fecha_de_beneficio"], format="%Y/%m/%d", errors="coerce")
    )
    df["fecha_de_beneficio"] = fechas.dt.strftime("%Y-%m-%d")

    # 5. Registros incompletos (se conservan los faltantes de comuna_ciudadano)
    columnas_obligatorias = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=columnas_obligatorias)

    # 6. Duplicados (después de normalizar, para detectar los que se veían distintos)
    df = df.drop_duplicates()

    os.makedirs("submission", exist_ok=True)
    df.to_csv("submission/solicitudes_de_credito.csv", sep=";", index=False)