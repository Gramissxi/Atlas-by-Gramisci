import psycopg

from services.configuracion import obtener_configuracion


def obtener_conexion():
    configuracion = obtener_configuracion()

    return psycopg.connect(
        host=configuracion.servidor_base_datos,
        port=configuracion.puerto_base_datos,
        dbname=configuracion.nombre_base_datos,
        user=configuracion.usuario_base_datos,
        password=configuracion.clave_base_datos,
    )
