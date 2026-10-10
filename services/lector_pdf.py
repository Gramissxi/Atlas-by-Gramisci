from pypdf import PdfReader


def leer_pdf(ruta_pdf):

    texto = ""

    reader = PdfReader(ruta_pdf)

    for pagina in reader.pages:

        contenido = pagina.extract_text()

        if contenido:
            texto += contenido + "\n"

    return texto

def leer_pdf_por_paginas(ruta_pdf):
    """Devuelve (numero_pagina, texto) sin perder referencias de origen.

    Las paginas sin texto seleccionable permanecen en el documento, pero
    no producen fragmentos textuales. No aplica OCR a imagenes o graficos.
    """
    reader = PdfReader(ruta_pdf)
    return [
        (numero, pagina.extract_text() or "")
        for numero, pagina in enumerate(reader.pages, start=1)
    ]
