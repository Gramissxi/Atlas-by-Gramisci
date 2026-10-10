"""Fusión de rankings para recuperación híbrida, sin dependencias externas."""


def fusionar_por_rrf(resultados_texto, resultados_semanticos, limite=5, k=60):
    """Combina listas ordenadas de dicts con 'materia', 'documento' y
    'numero_fragmento'. No compara directamente puntajes de escalas distintas.

    Los permisos y filtros de documentos deben aplicarse ANTES de esta función.
    """
    if limite < 1 or k < 1:
        raise ValueError("limite y k deben ser positivos")
    combinados = {}
    for fuente, resultados in (("texto", resultados_texto), ("semantica", resultados_semanticos)):
        vistos = set()
        for posicion, item in enumerate(resultados, start=1):
            clave = (item["materia"], item["documento"], item["numero_fragmento"])
            if clave in vistos:
                continue
            vistos.add(clave)
            registro = combinados.setdefault(clave, {**item, "puntaje_rrf": 0.0, "fuentes": []})
            registro["puntaje_rrf"] += 1 / (k + posicion)
            registro["fuentes"].append(fuente)
    return sorted(combinados.values(), key=lambda x: x["puntaje_rrf"], reverse=True)[:limite]
