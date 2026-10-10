import ollama

from services.configuracion import obtener_configuracion


def consultar_modelo(prompt, modelo=None):
    configuracion = obtener_configuracion()
    modelo = modelo or configuracion.modelo_chat

    respuesta = ollama.chat(
        model=modelo,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return respuesta["message"]["content"]
