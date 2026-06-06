from pathlib import Path


RUTA_DOCUMENTOS = Path("data/documentos")


def listar_documentos():

    documentos = []

    for archivo in RUTA_DOCUMENTOS.rglob("*"):

        if archivo.is_file():

            documentos.append(
                {
                    "nombre": archivo.name,
                    "ruta": str(archivo),
                    "extension": archivo.suffix
                }
            )

    return documentos