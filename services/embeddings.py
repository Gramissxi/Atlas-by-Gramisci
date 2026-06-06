import ollama


def generar_embedding(texto):

    respuesta = ollama.embeddings(
        model="nomic-embed-text",
        prompt=texto
    )

    return respuesta["embedding"]