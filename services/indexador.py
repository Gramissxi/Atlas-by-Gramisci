from pathlib import Path

from services.lector_pdf import leer_pdf
from services.chunking import dividir_texto
from services.embeddings import generar_embedding
from services.vector_store import insertar_chunk


def indexar_pdf(
    ruta_pdf,
    materia
):

    print(f"\nIndexando: {ruta_pdf}")

    texto = leer_pdf(ruta_pdf)

    chunks = dividir_texto(texto)

    print(
        f"Chunks generados: {len(chunks)}"
    )

    archivo = Path(ruta_pdf).name

    for numero_chunk, chunk in enumerate(
        chunks,
        start=1
    ):

        embedding = generar_embedding(
            chunk
        )

        insertar_chunk(
            materia=materia,
            archivo=archivo,
            numero_chunk=numero_chunk,
            contenido=chunk,
            embedding=embedding
        )

        print(
            f"Chunk {numero_chunk} guardado"
        )

    print(
        f"\nDocumento indexado correctamente: {archivo}"
    )