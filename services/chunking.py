def dividir_texto(
    texto,
    tamano_chunk=1000
):

    chunks = []

    for i in range(
        0,
        len(texto),
        tamano_chunk
    ):

        chunk = texto[
            i:i + tamano_chunk
        ]

        chunks.append(chunk)

    return chunks