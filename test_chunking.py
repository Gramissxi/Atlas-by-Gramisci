from services.lector_pdf import leer_pdf
from services.chunking import dividir_texto

texto = leer_pdf(
    "data/documentos/calculo/Modelo de examen - C1.pdf"
)

chunks = dividir_texto(texto)

print(
    f"Cantidad de chunks: {len(chunks)}"
)

print("\nPrimer chunk:\n")

print(chunks[0])