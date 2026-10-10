from services.repositorio_conocimiento import guardar_fragmento_conocimiento


def insertar_chunk(
    materia,
    archivo,
    numero_chunk,
    contenido,
    embedding,
):
    guardar_fragmento_conocimiento(
        materia=materia,
        documento=archivo,
        numero_fragmento=numero_chunk,
        contenido=contenido,
        incrustacion=embedding,
    )
