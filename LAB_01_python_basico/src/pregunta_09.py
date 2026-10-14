import gzip


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """
    
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        key_counts = {}
        for line in file:
            metrics = line.split("\t")[4].strip().split(",")
            for metric in metrics:
                key = metric.split(":")[0]
                key_counts[key] = key_counts.get(key, 0) + 1
    return dict(sorted(key_counts.items()))

    raise NotImplementedError
