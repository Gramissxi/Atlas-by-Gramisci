"""Laboratorio local del RAG de Atlas: recuperación textual por página.

Uso:
  pip install pypdf scikit-learn
  python scripts/laboratorio_rag_pdf.py "ruta/al/documento.pdf"

No sube el PDF a Internet ni lo agrega al repositorio.
Es una línea base TF-IDF, NO mide embeddings, Ollama ni la API.
"""
import argparse

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.fragmentacion import dividir_texto_en_fragmentos
from services.fragmentacion_estructurada import fragmentar_estructurado

PREGUNTAS_SENALES = (
    ("simplex full duplex", 7),
    ("relación frecuencia periodo inversa", 17),
    ("capacidad canal Nyquist", 31),
    ("ruido térmico electrones", 37),
    ("amplitud onda azul ejercicio", 21),
)


def evaluar(ruta, preguntas=PREGUNTAS_SENALES):
    paginas = [pagina.extract_text() or "" for pagina in PdfReader(ruta).pages]
    print(f"Paginas: {len(paginas)} | con texto: {sum(bool(x.strip()) for x in paginas)}")
    for nombre, fragmentador in (
        ("Original", dividir_texto_en_fragmentos),
        ("Estructurado", fragmentar_estructurado),
    ):
        # Página por página: evita perder la referencia de origen.
        fragmentos = [
            (numero, fragmento)
            for numero, texto in enumerate(paginas, start=1)
            for fragmento in fragmentador(texto)
        ]
        print(f"\n{nombre}: {len(fragmentos)} fragmentos")
        if not fragmentos:
            continue
        vectorizador = TfidfVectorizer(
            strip_accents="unicode",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b\w+\b",
        )
        matriz = vectorizador.fit_transform([f[1] for f in fragmentos])
        primeros = 0
        top_cinco = 0
        for pregunta, pagina_esperada in preguntas:
            similitudes = cosine_similarity(
                vectorizador.transform([pregunta]), matriz
            )[0]
            orden = similitudes.argsort()[::-1][:5]
            paginas_encontradas = [fragmentos[i][0] for i in orden]
            primeros += paginas_encontradas[0] == pagina_esperada
            top_cinco += pagina_esperada in paginas_encontradas
            print(f"  {pregunta}: top 5 paginas={paginas_encontradas}; objetivo={pagina_esperada}")
        print(f"Top 1: {primeros}/{len(preguntas)} | Top 5: {top_cinco}/{len(preguntas)}")
    print("\nAviso: recuperar la pagina de un grafico NO significa comprender sus datos visuales.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", help="Ruta local del PDF de prueba")
    args = parser.parse_args()
    evaluar(args.pdf)
