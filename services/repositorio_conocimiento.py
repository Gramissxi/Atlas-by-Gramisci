import psycopg

from services.base_datos import obtener_conexion


def guardar_fragmento_conocimiento(
    materia,
    documento,
    numero_fragmento,
    contenido,
    incrustacion,
    pagina_inicio=None,
    pagina_fin=None,
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO fragmentos_documento
            (
                materia_legacy,
                documento_legacy,
                numero_fragmento,
                pagina_inicio,
                pagina_fin,
                contenido,
                incrustacion
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::vector
            )
            """,
            (
                materia,
                documento,
                numero_fragmento,
                pagina_inicio,
                pagina_fin,
                contenido,
                str(incrustacion),
            ),
        )
    except (psycopg.errors.UndefinedTable, psycopg.errors.UndefinedColumn):
        conexion.rollback()
        cursor.execute(
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
                %s::vector
            )
            """,
            (
                materia,
                documento,
                numero_fragmento,
                contenido,
                str(incrustacion),
            ),
        )

    conexion.commit()
    cursor.close()
    conexion.close()
