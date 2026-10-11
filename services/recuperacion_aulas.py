"""Recuperación documental de aulas con FTS5 + coincidencia léxica.

Ambas listas se fusionan con Reciprocal Rank Fusion. No son embeddings:
la recuperación semántica real se incorporará en una etapa posterior.
"""
import re
import unicodedata

STOP = {"que","como","cual","cuales","por","para","sobre","los","las","una","del","con","donde","segun","es","son","me","explica","el","la","un","de","en"}

def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto.casefold()) if not unicodedata.combining(c))

def palabras(pregunta):
    texto = normalizar(pregunta)
    return list(dict.fromkeys(p for p in re.findall(r"[^\W_]+",texto) if len(p)>2 and p not in STOP))[:14]

def recuperar(db, aula_id, pregunta, limite=5):
    tokens = palabras(pregunta)
    if not tokens:
        return []
    consulta = " OR ".join('"' + t + '"' for t in tokens)
    filas_fts = db.execute("""SELECT f.rowid, d.nombre, f.pagina, f.texto
        FROM fragmentos f JOIN documentos d ON d.id=CAST(f.documento_id AS INTEGER)
        WHERE f.aula_id=? AND fragmentos MATCH ?
        ORDER BY bm25(fragmentos) LIMIT 40""", (aula_id,consulta)).fetchall()

    # Búsqueda de respaldo acotada únicamente a la clase autorizada.
    # No se limita a los primeros 20.000 bloques del repositorio.
    filas = db.execute("""SELECT f.rowid, d.nombre, f.pagina, f.texto
        FROM fragmentos f JOIN documentos d ON d.id=CAST(f.documento_id AS INTEGER)
        WHERE f.aula_id=?""",(aula_id,)).fetchall()
    puntuados = []
    for fila in filas:
        texto = normalizar(fila["texto"])
        presentes = sum(1 for t in tokens if re.search(r"(?<!\w)"+re.escape(t)+r"(?!\w)",texto))
        if presentes:
            puntuados.append((presentes, fila))
    puntuados.sort(key=lambda x:x[0],reverse=True)
    fusion = {}
    for origen, lista in (("fts",filas_fts),("lexica",[x[1] for x in puntuados[:40]])):
        vistos = set()
        for posicion, fila in enumerate(lista, start=1):
            clave = fila["rowid"]
            if clave in vistos:continue
            vistos.add(clave)
            entrada = fusion.setdefault(clave,{"fila":fila,"puntaje":0,"metodos":[]})
            entrada["puntaje"] += 1/(60+posicion)
            entrada["metodos"].append(origen)
    # Penalización suave a índices de diapositivas, que suelen listar términos
    # sin definirlos. Heurística: requiere evaluación con PDFs reales.
    def puntuacion_final(item):
        texto = normalizar(item["fila"]["texto"])
        lineas = [x.strip() for x in texto.splitlines() if x.strip()]
        es_temario = ("indice" in texto[:100] or "temario" in texto[:100]
                     or (len(lineas) >= 5 and sum(len(x) < 65 for x in lineas) / len(lineas) > 0.8))
        return item["puntaje"] * (0.35 if es_temario else 1)
    ranking = sorted(fusion.values(),key=puntuacion_final,reverse=True)[:limite]
    return [
        {"nombre":x["fila"]["nombre"],"pagina":x["fila"]["pagina"],"texto":x["fila"]["texto"]}
        for x in ranking
    ]
