from services.base_datos import obtener_conexion
from services.embeddings import generar_embedding


def buscar_chunks(
    consulta,
    limite=3
):

    embedding = generar_embedding(
        consulta
    )

    conn = obtener_conexion()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            materia,
            archivo,
            numero_chunk,
            contenido
        FROM chunks_conocimiento
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (
            str(embedding),
            limite
        )
    )

    resultados = cur.fetchall()

    cur.close()
    conn.close()

    return resultados