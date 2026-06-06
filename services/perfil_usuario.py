import json


RUTA_PERFIL = "data/perfiles/usuario.json"


def cargar_perfil():

    with open(
        RUTA_PERFIL,
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)


def guardar_perfil(perfil):

    with open(
        RUTA_PERFIL,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            perfil,
            archivo,
            ensure_ascii=False,
            indent=4
        )