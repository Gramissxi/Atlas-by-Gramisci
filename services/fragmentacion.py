def dividir_texto_en_fragmentos(
    texto,
    tamano_fragmento=1000,
    solapamiento=150,
):
    if tamano_fragmento <= 0:
        raise ValueError("El tamano del fragmento debe ser mayor a cero.")

    if solapamiento < 0:
        raise ValueError("El solapamiento no puede ser negativo.")

    if solapamiento >= tamano_fragmento:
        raise ValueError(
            "El solapamiento debe ser menor al tamano del fragmento."
        )

    texto = texto.strip()

    if not texto:
        return []

    fragmentos = []
    posicion = 0
    avance = tamano_fragmento - solapamiento

    while posicion < len(texto):
        fragmento = texto[posicion:posicion + tamano_fragmento].strip()

        if fragmento:
            fragmentos.append(fragmento)

        posicion += avance

    return fragmentos
