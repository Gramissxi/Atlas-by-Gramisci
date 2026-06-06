from services.perfil_usuario import (
    cargar_perfil,
    guardar_perfil
)

perfil = cargar_perfil()

print(perfil)

perfil["objetivo"] = "Data Engineer"

guardar_perfil(perfil)

print("Perfil actualizado")