import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConfiguracionAtlas:
    nombre_base_datos: str
    usuario_base_datos: str
    clave_base_datos: str
    servidor_base_datos: str
    puerto_base_datos: int
    modelo_chat: str
    modelo_incrustaciones: str
    ruta_documentos: Path
    ruta_perfil_usuario: Path


def obtener_configuracion():
    return ConfiguracionAtlas(
        nombre_base_datos=os.getenv("ATLAS_BD_NOMBRE", "atlas"),
        usuario_base_datos=os.getenv("ATLAS_BD_USUARIO", "atlas"),
        clave_base_datos=os.getenv("ATLAS_BD_CLAVE", "atlas"),
        servidor_base_datos=os.getenv("ATLAS_BD_SERVIDOR", "localhost"),
        puerto_base_datos=int(os.getenv("ATLAS_BD_PUERTO", "5432")),
        modelo_chat=os.getenv("ATLAS_MODELO_CHAT", "llama3.2:3b"),
        modelo_incrustaciones=os.getenv(
            "ATLAS_MODELO_INCRUSTACIONES",
            "nomic-embed-text",
        ),
        ruta_documentos=Path(
            os.getenv("ATLAS_RUTA_DOCUMENTOS", "data/documentos")
        ),
        ruta_perfil_usuario=Path(
            os.getenv("ATLAS_RUTA_PERFIL", "data/perfiles/usuario.json")
        ),
    )
