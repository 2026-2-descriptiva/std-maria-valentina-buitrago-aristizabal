import gzip


def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        letter_counts = {}
        for line in file:
            letter = line.split("\t")[0]
            letter_counts[letter] = letter_counts.get(letter, 0) + 1

    return sorted(letter_counts.items())

    raise NotImplementedError
