import gzip


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as file:
        letter_sums = {}
        for line in file:
            letter = line.split("\t")[0]
            metrics = line.split("\t")[4].strip().split(",")
            total_value = sum(int(metric.split(":")[1]) for metric in metrics)
            letter_sums[letter] = letter_sums.get(letter, 0) + total_value 
    return dict(sorted(letter_sums.items()))

    raise NotImplementedError
