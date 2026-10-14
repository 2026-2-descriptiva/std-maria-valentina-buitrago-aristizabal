import gzip


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        value_letters = {}
        for line in file:
            letter, value = line.split("\t")[0], int(line.split("\t")[1])
            if value not in value_letters:
                value_letters[value] = {letter}
            else:
                value_letters[value].add(letter)

    return sorted([(k, sorted(v)) for k, v in value_letters.items()])

    raise NotImplementedError
