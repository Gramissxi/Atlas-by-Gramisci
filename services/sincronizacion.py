import httpx


def hay_conexion_disponible(url_prueba="https://www.wikipedia.org", segundos=3):
    try:
        respuesta = httpx.get(url_prueba, timeout=segundos)
        return respuesta.status_code < 500
    except httpx.HTTPError:
        return False


def describir_modo_atlas(conexion_disponible):
    if conexion_disponible:
        return {
            "modo": "atlas_expandido",
            "descripcion": (
                "Atlas usa la biblioteca local y puede complementar rutas "
                "con fuentes externas curadas."
            ),
        }

    return {
        "modo": "biblioteca_local",
        "descripcion": (
            "Atlas funciona sin internet usando documentos, busqueda local, "
            "incrustaciones y progreso del usuario."
        ),
    }
