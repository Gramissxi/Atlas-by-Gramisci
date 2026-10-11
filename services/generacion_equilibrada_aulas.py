"""Generación equilibrada por PDF: cada documento aporta preguntas y fuentes propias."""
from services.generador_evaluaciones_aulas import generar_preguntas
from services.recuperacion_aulas import recuperar


def generar_equilibrado(db, aula_id, ids, cantidad, dificultad, formato):
    """Devuelve preguntas en orden y sus fuentes, sin mezclar PDFs en un prompt.

    Distribuye posiciones de modo circular (5 preguntas / 3 PDF => 2,2,1).
    Para formato mixto mantiene el patrón global: múltiple, desarrollo, ...
    """
    if len(ids) > cantidad:
        raise ValueError("Hay más PDF seleccionados que preguntas. Elegí más preguntas o menos archivos para incluir al menos una pregunta de cada uno.")
    posiciones = {doc_id: [] for doc_id in ids}
    for posicion in range(cantidad):
        posiciones[ids[posicion % len(ids)]].append(posicion)
    resultado = [None] * cantidad
    fuentes_usadas = []
    for doc_id in ids:
        ubicaciones = posiciones[doc_id]
        if not ubicaciones:
            continue
        fragmentos = recuperar(
            db, aula_id,
            "conceptos definiciones ejemplos ejercicios teoría contenidos procesos características",
            limite=7, documentos_ids=[doc_id]
        )
        if not fragmentos:
            fragmentos = [dict(f) for f in db.execute(
                """SELECT d.id AS documento_id,d.nombre,f.pagina,f.texto
                   FROM fragmentos f JOIN documentos d ON d.id=CAST(f.documento_id AS INTEGER)
                   WHERE d.id=? AND f.aula_id=? AND length(trim(f.texto))>=50
                   ORDER BY f.pagina LIMIT 7""", (doc_id, aula_id)
            )]
        if not fragmentos:
            raise ValueError("Uno de los PDF seleccionados no tiene texto suficiente. Revisá ese documento antes de generar.")
        fuentes_usadas.extend({
            "documento_id": f["documento_id"],
            "nombre": f["nombre"],
            "pagina": f["pagina"]
        } for f in fragmentos)
        if formato == "mixto":
            por_tipo = {
                "multiple": [i for i in ubicaciones if i % 2 == 0],
                "desarrollo": [i for i in ubicaciones if i % 2 == 1]
            }
        else:
            por_tipo = {formato: ubicaciones}
        for tipo, indices in por_tipo.items():
            if not indices:
                continue
            generadas = generar_preguntas(fragmentos, len(indices), dificultad, tipo)
            if len(generadas) != len(indices):
                raise ValueError("Ollama no generó la cantidad necesaria para uno de los documentos")
            for pos, pregunta in zip(indices, generadas):
                resultado[pos] = pregunta
    if any(not isinstance(p, str) or not p.strip() for p in resultado):
        raise ValueError("El simulacro quedó incompleto; intentá generar nuevamente")
    return resultado, fuentes_usadas
