import psycopg


def obtener_conexion():

    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="pocketmentor",
        user="celeste",
        password="celeste123"
    )