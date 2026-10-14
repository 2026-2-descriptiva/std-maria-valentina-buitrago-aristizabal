import gzip

def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    
    metrics_values = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        for line in file:
            metrics = line.split("\t")[4].strip().split(",")
            for metric in metrics:
                key, value = metric.split(":")
                value = int(value)
                if key not in metrics_values:
                    metrics_values[key] = (value, value)  # (min, max)
                else:
                    current_min, current_max = metrics_values[key]
                    metrics_values[key] = (min(current_min, value), max(current_max, value))

    return [(key, min_val, max_val) for key, (min_val, max_val) in sorted(metrics_values.items())]

    raise NotImplementedError
