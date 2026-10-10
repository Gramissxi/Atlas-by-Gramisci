import json
from pathlib import Path

from agents.curador_conocimiento import CuradorConocimiento
from services.lector_pdf import leer_pdf


class CrearMateria:
    def ejecutar(
        self,
        carpeta_documentos,
        carpeta_salida="data/materias",
    ):
        ruta_documentos = Path(carpeta_documentos)
        texto_total = ""

        for ruta_pdf in ruta_documentos.rglob("*.pdf"):
            print(f"Leyendo: {ruta_pdf.name}")
            texto_total += "\n\n"
            texto_total += leer_pdf(str(ruta_pdf))

        curador = CuradorConocimiento()
        metadatos = curador.ejecutar(texto_total)

        nombre_materia = (
            metadatos["materia"]
            .lower()
            .replace(" ", "_")
        )

        ruta_materia = Path(carpeta_salida) / nombre_materia
        ruta_materia.mkdir(parents=True, exist_ok=True)

        ruta_metadatos = ruta_materia / "metadatos.json"

        with open(
            ruta_metadatos,
            "w",
            encoding="utf-8",
        ) as archivo_metadatos:
            json.dump(
                metadatos,
                archivo_metadatos,
                ensure_ascii=False,
                indent=4,
            )

        print("\nMateria creada correctamente:")
        print(ruta_metadatos)

        return metadatos
