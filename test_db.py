from services.base_datos import obtener_conexion

conn = obtener_conexion()

print("Conexión OK")

conn.close()