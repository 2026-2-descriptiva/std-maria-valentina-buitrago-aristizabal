import gzip

def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    letter_values = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        for line in file:
            columns = line.split("\t")
            letter, value = columns[0], int(columns[1])
            
            if letter not in letter_values:
                letter_values[letter] = (value, value)  # (max, min)
            else:
                current_max, current_min = letter_values[letter]
                letter_values[letter] = (max(current_max, value), min(current_min, value))

    return [(letter, max_val, min_val) for letter, (max_val, min_val) in sorted(letter_values.items())]

    raise NotImplementedError
