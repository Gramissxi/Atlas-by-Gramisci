from services.perfil_usuario import (
    cargar_perfil,
    guardar_perfil
)


def actualizar_progreso(
    tema_actual,
    paso_actual,
    avance_porcentaje
):

    perfil = cargar_perfil()

    perfil["tema_actual"] = tema_actual
    perfil["paso_actual"] = paso_actual
    perfil["avance_porcentaje"] = avance_porcentaje

    guardar_perfil(perfil)


def obtener_progreso():

    perfil = cargar_perfil()

    return {
        "tema_actual": perfil["tema_actual"],
        "paso_actual": perfil["paso_actual"],
        "avance_porcentaje": perfil["avance_porcentaje"]
    }