import gzip
def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        value_letters = {}
        for line in file:
            letter, value = line.split("\t")[0], int(line.split("\t")[1])
            if value not in value_letters:
                value_letters[value] = [letter]
            else:
                value_letters[value].append(letter) 
    return sorted(value_letters.items())

    raise NotImplementedError
