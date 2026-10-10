from services.configuracion import obtener_configuracion


RUTA_DOCUMENTOS = obtener_configuracion().ruta_documentos


def listar_documentos():
    documentos = []

    for ruta_documento in RUTA_DOCUMENTOS.rglob("*"):
        if ruta_documento.is_file():
            documentos.append(
                {
                    "nombre": ruta_documento.name,
                    "ruta": str(ruta_documento),
                    "extension": ruta_documento.suffix,
                }
            )

    return documentos
