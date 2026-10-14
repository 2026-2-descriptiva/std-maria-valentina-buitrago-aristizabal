import gzip


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    import gzip
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        letter_sums = {}
        for line in file:
            letter, value = line.split("\t")[0], int(line.split("\t")[1])
            letter_sums[letter] = letter_sums.get(letter, 0) + value
    return sorted(letter_sums.items())

    raise NotImplementedError
