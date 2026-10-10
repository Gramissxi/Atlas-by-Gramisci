METODOLOGIAS_LOCALES = [
    {
        "nombre": "lectura guiada por objetivos",
        "uso": "entender para que sirve el documento antes de memorizar detalles",
    },
    {
        "nombre": "fragmentacion progresiva",
        "uso": "estudiar el material por bloques chicos y verificables",
    },
    {
        "nombre": "practica de recuperacion",
        "uso": "responder preguntas sin mirar y luego contrastar con el documento",
    },
    {
        "nombre": "deteccion de vacios",
        "uso": "marcar lo que el material no explica y complementarlo despues",
    },
]


def obtener_metodologias_locales():
    return METODOLOGIAS_LOCALES


def recargar_metodologias_si_hay_internet():
    try:
        from services.sincronizacion import hay_conexion_disponible
    except ModuleNotFoundError:
        return {
            "modo": "offline",
            "actualizado": False,
            "metodologias": METODOLOGIAS_LOCALES,
            "mensaje": (
                "Sin dependencias de conexion instaladas: Atlas usa "
                "metodologias locales guardadas."
            ),
        }

    if not hay_conexion_disponible():
        return {
            "modo": "offline",
            "actualizado": False,
            "metodologias": METODOLOGIAS_LOCALES,
            "mensaje": "Sin internet: Atlas usa metodologias locales guardadas.",
        }

    return {
        "modo": "online",
        "actualizado": False,
        "metodologias": METODOLOGIAS_LOCALES,
        "mensaje": (
            "Hay internet. Falta configurar fuentes curadas para comparar y "
            "actualizar metodologias sin reemplazar las locales automaticamente."
        ),
    }
