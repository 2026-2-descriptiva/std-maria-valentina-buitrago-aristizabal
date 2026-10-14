import gzip


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        month_counts = {}
        for line in file:
            date = line.split("\t")[2]
            month = date.split("-")[1]
            month_counts[month] = month_counts.get(month, 0) + 1

    return sorted(month_counts.items())

    raise NotImplementedError
