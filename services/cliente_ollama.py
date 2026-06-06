import ollama


def consultar_modelo(prompt, modelo="llama3.2:3b"):

    respuesta = ollama.chat(
        model=modelo,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return respuesta["message"]["content"]