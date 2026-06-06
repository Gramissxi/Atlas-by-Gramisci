from pypdf import PdfReader


def leer_pdf(ruta_pdf):

    texto = ""

    reader = PdfReader(ruta_pdf)

    for pagina in reader.pages:

        contenido = pagina.extract_text()

        if contenido:
            texto += contenido + "\n"

    return texto