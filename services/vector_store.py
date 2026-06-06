from services.base_datos import (
    obtener_conexion
)


def insertar_chunk(
    materia,
    archivo,
    numero_chunk,
    contenido,
    embedding
):

    conn = obtener_conexion()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chunks_conocimiento
        (
            materia,
            archivo,
            numero_chunk,
            contenido,
            embedding
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            materia,
            archivo,
            numero_chunk,
            contenido,
            embedding
        )
    )

    conn.commit()

    cur.close()
    conn.close()