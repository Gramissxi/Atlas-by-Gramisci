class ErrorPostgreSQL(RuntimeError):
    pass


try:
    import psycopg
except ModuleNotFoundError as error:
    raise ErrorPostgreSQL(
        "Error de conexión con PostgreSQL: falta instalar el paquete psycopg en el entorno Python activo."
    ) from error

from services.base_datos import obtener_conexion
from services.incrustaciones import generar_incrustacion


def _mensaje_error_postgresql(error):
    return f"Error de conexión con PostgreSQL: {error}"


def _cerrar_recursos(cursor=None, conexion=None):
    if cursor is not None:
        cursor.close()
    if conexion is not None:
        conexion.close()


def buscar_por_semantica(consulta, limite=5):
    incrustacion = generar_incrustacion(consulta)
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    COALESCE(m.nombre, fd.materia_legacy) AS materia,
                    COALESCE(d.titulo, fd.documento_legacy) AS documento,
                    fd.numero_fragmento,
                    fd.contenido,
                    1 - (fd.incrustacion <=> %s::vector) AS puntaje
                FROM fragmentos_documento fd
                LEFT JOIN materias m ON m.id = fd.materia_id
                LEFT JOIN documentos d ON d.id = fd.documento_id
                WHERE fd.incrustacion IS NOT NULL
                ORDER BY fd.incrustacion <=> %s::vector
                LIMIT %s
                """,
                (
                    str(incrustacion),
                    str(incrustacion),
                    limite,
                ),
            )
        except (psycopg.errors.UndefinedTable, psycopg.errors.UndefinedColumn):
            conexion.rollback()
            cursor.execute(
                """
                SELECT
                    materia,
                    archivo,
                    numero_chunk,
                    contenido,
                    1 - (embedding <=> %s::vector) AS puntaje
                FROM chunks_conocimiento
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    str(incrustacion),
                    str(incrustacion),
                    limite,
                ),
            )

        return cursor.fetchall()
    except psycopg.Error as error:
        raise ErrorPostgreSQL(_mensaje_error_postgresql(error)) from error
    finally:
        _cerrar_recursos(cursor, conexion)


def buscar_por_texto(consulta, limite=5):
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    COALESCE(m.nombre, fd.materia_legacy) AS materia,
                    COALESCE(d.titulo, fd.documento_legacy) AS documento,
                    fd.numero_fragmento,
                    fd.contenido,
                    ts_rank(fd.texto_busqueda, plainto_tsquery('spanish', %s)) AS puntaje
                FROM fragmentos_documento fd
                LEFT JOIN materias m ON m.id = fd.materia_id
                LEFT JOIN documentos d ON d.id = fd.documento_id
                WHERE fd.texto_busqueda @@ plainto_tsquery('spanish', %s)
                ORDER BY puntaje DESC
                LIMIT %s
                """,
                (
                    consulta,
                    consulta,
                    limite,
                ),
            )
        except (psycopg.errors.UndefinedTable, psycopg.errors.UndefinedColumn):
            conexion.rollback()
            cursor.execute(
                """
                SELECT
                    materia,
                    archivo,
                    numero_chunk,
                    contenido,
                    0.500 AS puntaje
                FROM chunks_conocimiento
                WHERE contenido ILIKE %s
                LIMIT %s
                """,
                (
                    f"%{consulta}%",
                    limite,
                ),
            )

        return cursor.fetchall()
    except psycopg.Error as error:
        raise ErrorPostgreSQL(_mensaje_error_postgresql(error)) from error
    finally:
        _cerrar_recursos(cursor, conexion)


def buscar_hibrido(consulta, limite=5):
    resultados = {}

    for resultado in buscar_por_texto(consulta, limite=limite):
        clave = (resultado[0], resultado[1], resultado[2])
        resultados[clave] = {
            "materia": resultado[0],
            "documento": resultado[1],
            "numero_fragmento": resultado[2],
            "contenido": resultado[3],
            "puntaje_texto": float(resultado[4]),
            "puntaje_semantico": 0.0,
        }

    for resultado in buscar_por_semantica(consulta, limite=limite):
        clave = (resultado[0], resultado[1], resultado[2])
        if clave not in resultados:
            resultados[clave] = {
                "materia": resultado[0],
                "documento": resultado[1],
                "numero_fragmento": resultado[2],
                "contenido": resultado[3],
                "puntaje_texto": 0.0,
                "puntaje_semantico": float(resultado[4]),
            }
        else:
            resultados[clave]["puntaje_semantico"] = float(resultado[4])

    ordenados = sorted(
        resultados.values(),
        key=lambda item: (
            item["puntaje_texto"] * 0.45
            + item["puntaje_semantico"] * 0.55
        ),
        reverse=True,
    )

    return ordenados[:limite]


def buscar_chunks(consulta, limite=3):
    return buscar_por_semantica(consulta, limite=limite)

