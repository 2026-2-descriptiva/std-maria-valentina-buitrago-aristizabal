import gzip


def pregunta_10():
    """
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """
    
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        result = []
        for line in file:
            letter = line.split("\t")[0]
            codes_count = len(line.split("\t")[3].strip().split(","))
            metrics_count = len(line.split("\t")[4].strip().split(","))
            result.append((letter, codes_count, metrics_count))
    return result

    raise NotImplementedError
