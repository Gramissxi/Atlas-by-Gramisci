"""Fragmentación estructurada opcional para documentos escolares.

No reemplaza automáticamente el fragmentador existente. Mantiene juntas
las oraciones y los párrafos cuando el tamaño lo permite, sin embeddings,
base de datos ni conexión a Internet.
"""
import re


def _unidades(texto):
    """Separar párrafos y, si hace falta, oraciones extensas."""
    for parrafo in re.split(r"\n\s*\n", texto.strip()):
        parrafo = re.sub(r"[ \t\n]+", " ", parrafo).strip()
        if not parrafo:
            continue
        # Los límites de oración son heurísticos; abreviaturas pueden fallar.
        for oracion in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ0-9¿¡])", parrafo):
            oracion = oracion.strip()
            if oracion:
                yield oracion


def fragmentar_estructurado(texto, max_caracteres=900, solapamiento=0):
    """Generar fragmentos ordenados. Nunca omitir contenido por ser extenso.

    max_caracteres es un límite estricto. Las oraciones demasiado extensas
    se cortan por palabras cuando es posible; palabras individuales enormes
    se dividen como último recurso. solapamiento=0 evita texto duplicado.
    """
    if max_caracteres <= 0:
        raise ValueError("max_caracteres debe ser positivo")
    if solapamiento < 0 or solapamiento >= max_caracteres:
        raise ValueError("solapamiento debe estar entre 0 y max_caracteres - 1")
    if not texto or not texto.strip():
        return []

    partes = []
    for unidad in _unidades(texto):
        if len(unidad) <= max_caracteres:
            partes.append(unidad)
            continue
        palabras = unidad.split()
        actual = ""
        for palabra in palabras:
            if len(palabra) > max_caracteres:
                if actual:
                    partes.append(actual)
                    actual = ""
                partes.extend(palabra[i:i + max_caracteres] for i in range(0, len(palabra), max_caracteres))
            elif len(actual) + len(palabra) + (1 if actual else 0) <= max_caracteres:
                actual = (actual + " " + palabra).strip()
            else:
                partes.append(actual)
                actual = palabra
        if actual:
            partes.append(actual)

    fragmentos = []
    actual = ""
    for parte in partes:
        candidato = f"{actual} {parte}".strip() if actual else parte
        if len(candidato) <= max_caracteres:
            actual = candidato
        else:
            if actual:
                fragmentos.append(actual)
            actual = parte
    if actual:
        fragmentos.append(actual)

    if not solapamiento or len(fragmentos) < 2:
        return fragmentos

    # Solapamiento textual acotado sin superar nunca max_caracteres.
    salida = [fragmentos[0]]
    for fragmento in fragmentos[1:]:
        espacio = max_caracteres - len(fragmento) - 1
        prefijo = salida[-1][-min(solapamiento, max(0, espacio)):] if espacio > 0 else ""
        salida.append((prefijo + " " + fragmento).strip() if prefijo else fragmento)
    return salida
