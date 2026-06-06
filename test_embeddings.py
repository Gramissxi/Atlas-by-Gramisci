from services.lector_pdf import leer_pdf
from services.chunking import dividir_texto
from services.embeddings import generar_embedding


texto = leer_pdf(
    "data/documentos/calculo/Modelo de examen - C1.pdf"
)

chunks = dividir_texto(texto)

embedding = generar_embedding(
    chunks[0]
)

print(
    f"Dimensión embedding: {len(embedding)}"
)

print(
    embedding[:10]
)