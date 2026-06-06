from services.base_datos import obtener_conexion

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
        "calculo",
        "prueba.pdf",
        1,
        "Este es un chunk de prueba",
        [0.0] * 768
    )
)

conn.commit()

print("Chunk insertado correctamente")

cur.close()
conn.close()