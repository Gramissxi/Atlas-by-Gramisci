from services.fragmentacion import dividir_texto_en_fragmentos


def dividir_texto(texto, tamano_chunk=1000):
    return dividir_texto_en_fragmentos(
        texto,
        tamano_fragmento=tamano_chunk,
        solapamiento=0,
    )
