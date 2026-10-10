import json

from services.configuracion import obtener_configuracion


RUTA_PERFIL = obtener_configuracion().ruta_perfil_usuario


def cargar_perfil():
    with open(
        RUTA_PERFIL,
        "r",
        encoding="utf-8",
    ) as archivo_perfil:
        return json.load(archivo_perfil)


def guardar_perfil(perfil):
    with open(
        RUTA_PERFIL,
        "w",
        encoding="utf-8",
    ) as archivo_perfil:
        json.dump(
            perfil,
            archivo_perfil,
            ensure_ascii=False,
            indent=4,
        )
