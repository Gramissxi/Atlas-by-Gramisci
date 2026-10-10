import ollama

from services.configuracion import obtener_configuracion


def generar_incrustacion(texto, modelo=None):
    configuracion = obtener_configuracion()
    modelo = modelo or configuracion.modelo_incrustaciones

    respuesta = ollama.embeddings(
        model=modelo,
        prompt=texto,
    )

    return respuesta["embedding"]
