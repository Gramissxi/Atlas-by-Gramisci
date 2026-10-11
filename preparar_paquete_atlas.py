"""Prepara en la PC central un paquete de consulta para Atlas Web.

Uso: python preparar_paquete_atlas.py archivo.pdf -o paquete-atlas.json
No requiere Ollama ni Internet. No incluye imágenes; solo texto extraíble.
"""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
from services.fragmentacion_estructurada import fragmentar_estructurado

def preparar(ruta, salida):
    lector = PdfReader(str(ruta))
    if len(lector.pages) > 500:
        raise ValueError("El laboratorio admite como máximo 500 páginas")
    fragmentos = [
        {"pagina": numero, "texto": bloque}
        for numero, pagina in enumerate(lector.pages, start=1)
        for bloque in fragmentar_estructurado(pagina.extract_text() or "")
    ]
    if not fragmentos:
        raise ValueError("No se extrajo texto del documento")
    paquete = {
        "formato": "atlas-offline-v1",
        "documento": Path(ruta).name,
        "paginas": len(lector.pages),
        "fragmentos": fragmentos,
    }
    destino = Path(salida)
    destino.write_text(json.dumps(paquete, ensure_ascii=False), encoding="utf-8")
    print(f"Preparado: {destino} | {len(fragmentos)} fragmentos | {destino.stat().st_size} bytes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("-o", "--salida", default="paquete-atlas.json")
    args = parser.parse_args()
    preparar(args.pdf, args.salida)
