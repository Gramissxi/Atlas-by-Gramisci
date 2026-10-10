def _consultar_modelo_local(prompt):
    try:
        from services.cliente_ollama import consultar_modelo
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Falta instalar o activar el entorno con el paquete ollama. Ejecuta pip install -r requirements.txt."
        ) from error

    return consultar_modelo(prompt)



def _normalizar_ids(fragment_ids):
    if fragment_ids is None:
        return []

    if isinstance(fragment_ids, (str, int)):
        fragment_ids = [fragment_ids]

    ids = []
    for valor in fragment_ids:
        try:
            ids.append(int(valor))
        except (TypeError, ValueError):
            continue

    return ids



def _normalizar_fragmento(resultado):
    if isinstance(resultado, dict):
        return {
            "materia": resultado.get("materia", ""),
            "documento": resultado.get("documento", ""),
            "numero_fragmento": resultado.get("numero_fragmento", 0),
            "contenido": resultado.get("contenido", ""),
            "document_id": resultado.get("document_id"),
            "section_id": resultado.get("section_id"),
            "fragment_id": resultado.get("fragment_id", resultado.get("numero_fragmento", 0)),
            "titulo": resultado.get("titulo", ""),
            "fuente": resultado.get("fuente", "postgresql"),
        }

    return {
        "materia": resultado[0] if len(resultado) > 0 else "",
        "documento": resultado[1] if len(resultado) > 1 else "",
        "numero_fragmento": resultado[2] if len(resultado) > 2 else 0,
        "contenido": resultado[3] if len(resultado) > 3 else "",
        "document_id": None,
        "section_id": None,
        "fragment_id": resultado[2] if len(resultado) > 2 else 0,
        "titulo": "",
        "fuente": "postgresql",
    }



def _buscar_fragmentos_mock(document_id, section_id, fragment_ids, limite):
    from services.fragmentos_mock import buscar_fragmentos_mock

    return buscar_fragmentos_mock(
        document_id=document_id,
        section_id=section_id,
        fragment_ids=fragment_ids,
        limite=limite,
    )



def obtener_fragmentos_documento(
    documento,
    materia,
    paso_ruta,
    limite=5,
    document_id=None,
    section_id=None,
    fragment_ids=None,
):
    ids = _normalizar_ids(fragment_ids)

    if ids:
        return _buscar_fragmentos_mock(
            document_id=document_id,
            section_id=section_id,
            fragment_ids=ids,
            limite=limite,
        )

    consulta = f"{materia} {documento} {paso_ruta}"

    from services.buscador import buscar_hibrido

    resultados = buscar_hibrido(consulta, limite=limite * 2)
    fragmentos = [_normalizar_fragmento(resultado) for resultado in resultados]
    documento_normalizado = documento.lower()

    propios = [
        fragmento
        for fragmento in fragmentos
        if documento_normalizado in fragmento["documento"].lower()
    ]

    return (propios or fragmentos)[:limite]



def _texto_fragmentos(fragmentos):
    return "\n\n".join(
        f"Fragmento {item['numero_fragmento']} ({item['documento']}):\n{item['contenido']}"
        for item in fragmentos
    )



def _ids_fragmentos(fragmentos):
    return [
        int(item.get("fragment_id") or item.get("numero_fragmento"))
        for item in fragmentos
        if item.get("fragment_id") or item.get("numero_fragmento")
    ]



def _mensaje_fragmentos_no_encontrados(fragment_ids):
    ids = _normalizar_ids(fragment_ids)

    if ids:
        return (
            "No se encontraron fragmentos locales para los fragment_ids enviados: "
            f"{', '.join(str(item) for item in ids)}. Revisa document_id, section_id o la fuente mock local."
        )

    return "Todavia no hay fragmentos indexados para esta seccion."



def _respuesta_estudio_local(documento, materia, paso_ruta, fragmentos):
    ids = ", ".join(str(item) for item in _ids_fragmentos(fragmentos))
    return (
        f"Atlas encontro fragmentos locales del documento {documento} para la seccion {paso_ruta}. "
        "Primero lee el recorrido general del pipeline y despues identifica cada responsabilidad: "
        "ingesta, validacion, transformacion, almacenamiento y exposicion. "
        f"Fragmentos usados: {ids}."
    )



def _respuesta_consulta_local(documento, materia, paso_ruta, pregunta, fragmentos):
    ids = ", ".join(str(item) for item in _ids_fragmentos(fragmentos))
    resumen = " ".join(item["contenido"] for item in fragmentos)
    resumen = resumen[:650].rstrip()
    return (
        f"Con los fragmentos locales del documento {documento}, la seccion {paso_ruta} describe "
        "el pipeline como una cadena de etapas con responsabilidades separadas. "
        f"Respuesta a la consulta: {resumen}. "
        f"Fragmentos usados: {ids}."
    )



def _preguntas_practica(fragmentos):
    ids = ", ".join(str(item) for item in _ids_fragmentos(fragmentos))
    return [
        f"Explica el recorrido de los datos en el pipeline usando los fragmentos {ids}.",
        "Identifica que responsabilidad cumple cada etapa: ingesta, validacion, transformacion, almacenamiento y exposicion.",
        "Dado un lote con campos obligatorios ausentes, indica en que etapa deberia detectarse y que evidencia quedaria registrada.",
        "Describe por que separar responsabilidades ayuda a mantener y corregir el pipeline.",
        "Criterio de autocorreccion: la respuesta debe mencionar flujo, controles de calidad y destino de consumo sin agregar fuentes externas.",
    ]



def _respuesta_practica_local(fragmentos):
    return "\n".join(_preguntas_practica(fragmentos))



def _son_fragmentos_mock(fragmentos):
    return bool(fragmentos) and all(
        item.get("fuente") == "mock-local" for item in fragmentos
    )



def _consultar_o_generar_respuesta(prompt, respuesta_local):
    try:
        return _consultar_modelo_local(prompt)
    except Exception:
        return respuesta_local



def ver_fragmentos_con_ollama(
    documento,
    materia,
    paso_ruta,
    limite=5,
    document_id=None,
    section_id=None,
    fragment_ids=None,
):
    fragmentos = obtener_fragmentos_documento(
        documento=documento,
        materia=materia,
        paso_ruta=paso_ruta,
        limite=limite,
        document_id=document_id,
        section_id=section_id,
        fragment_ids=fragment_ids,
    )

    if not fragmentos:
        return {
            "documento": documento,
            "materia": materia,
            "paso_ruta": paso_ruta,
            "fragmentos": [],
            "respuesta": _mensaje_fragmentos_no_encontrados(fragment_ids),
            "estado": "SIN_FRAGMENTOS",
        }

    texto_fragmentos = _texto_fragmentos(fragmentos)

    prompt = f"""
Eres Atlas, un asistente educativo offline-first para estudiantes.

Trabajas sin internet y solo podes usar material local ya cargado.

Documento: {documento}
Materia: {materia}
Paso de estudio: {paso_ruta}

Fragmentos locales disponibles:

{texto_fragmentos}

Tarea:
1. Selecciona los fragmentos mas utiles para este paso.
2. Explica por que sirven.
3. Sugiere que deberia mirar primero el estudiante.
4. Si faltan fragmentos, dilo claramente sin inventar informacion.

Responde en espanol, breve y accionable.
"""

    return {
        "documento": documento,
        "materia": materia,
        "paso_ruta": paso_ruta,
        "fragmentos": fragmentos,
        "fragment_ids": _ids_fragmentos(fragmentos),
        "respuesta": _respuesta_estudio_local(documento, materia, paso_ruta, fragmentos)
        if _son_fragmentos_mock(fragmentos)
        else _consultar_o_generar_respuesta(
            prompt,
            _respuesta_estudio_local(documento, materia, paso_ruta, fragmentos),
        ),
    }



def crear_practica_con_ollama(
    documento,
    materia,
    paso_ruta,
    limite=5,
    document_id=None,
    section_id=None,
    fragment_ids=None,
    modelo="ollama-local",
    dificultad=None,
):
    fragmentos = obtener_fragmentos_documento(
        documento=documento,
        materia=materia,
        paso_ruta=paso_ruta,
        limite=limite,
        document_id=document_id,
        section_id=section_id,
        fragment_ids=fragment_ids,
    )

    if not fragmentos:
        return {
            "documento": documento,
            "materia": materia,
            "paso_ruta": paso_ruta,
            "fragmentos": [],
            "respuesta": _mensaje_fragmentos_no_encontrados(fragment_ids),
            "estado": "SIN_GENERAR",
        }

    texto_fragmentos = _texto_fragmentos(fragmentos)
    preguntas = _preguntas_practica(fragmentos)

    prompt = f"""
Eres Atlas, un generador de practica offline para estudiantes.

Usa solamente el documento local y los fragmentos disponibles. No uses internet.

Documento: {documento}
Materia: {materia}
Paso de estudio: {paso_ruta}

Fragmentos locales:

{texto_fragmentos}

Genera una practica breve con:
1. 3 preguntas de comprension.
2. 2 ejercicios aplicados.
3. 1 consigna para explicar con palabras propias.
4. Criterios simples para autocorregirse.

Si no hay fragmentos suficientes, explica que falta indexar mas contenido y no inventes ejercicios genericos.
Responde en espanol.
"""

    return {
        "documento": documento,
        "materia": materia,
        "paso_ruta": paso_ruta,
        "document_id": document_id,
        "section_id": section_id,
        "fragmentos": fragmentos,
        "fragment_ids": _ids_fragmentos(fragmentos),
        "questions": preguntas,
        "answers": ["" for _ in preguntas],
        "score": None,
        "model_used": modelo,
        "difficulty_level": dificultad,
        "respuesta": _respuesta_practica_local(fragmentos)
        if _son_fragmentos_mock(fragmentos)
        else _consultar_o_generar_respuesta(
            prompt,
            _respuesta_practica_local(fragmentos),
        ),
        "estado": "GENERADA",
    }



def consultar_documento_con_ollama(
    documento,
    materia,
    paso_ruta,
    pregunta,
    limite=5,
    document_id=None,
    section_id=None,
    fragment_ids=None,
):
    fragmentos = obtener_fragmentos_documento(
        documento=documento,
        materia=materia,
        paso_ruta=paso_ruta,
        limite=limite,
        document_id=document_id,
        section_id=section_id,
        fragment_ids=fragment_ids,
    )

    if not fragmentos:
        return {
            "documento": documento,
            "materia": materia,
            "paso_ruta": paso_ruta,
            "pregunta": pregunta,
            "fragmentos": [],
            "respuesta": _mensaje_fragmentos_no_encontrados(fragment_ids),
        }

    texto_fragmentos = _texto_fragmentos(fragmentos)

    prompt = f"""
Eres Atlas, un chat educativo asociado a un documento tecnico local.

Reglas:
- Responde solo con los fragmentos locales provistos.
- Si los fragmentos no alcanzan, dilo claramente.
- No inventes bibliografia ni contenido externo.

Documento: {documento}
Materia: {materia}
Seccion de ruta: {paso_ruta}
Pregunta del estudiante: {pregunta}

Fragmentos locales:

{texto_fragmentos}

Responde en espanol, claro y breve. Incluye que fragmentos usaste cuando sea posible.
"""

    return {
        "documento": documento,
        "materia": materia,
        "paso_ruta": paso_ruta,
        "pregunta": pregunta,
        "fragmentos": fragmentos,
        "fragment_ids": _ids_fragmentos(fragmentos),
        "respuesta": _respuesta_consulta_local(documento, materia, paso_ruta, pregunta, fragmentos)
        if _son_fragmentos_mock(fragmentos)
        else _consultar_o_generar_respuesta(
            prompt,
            _respuesta_consulta_local(documento, materia, paso_ruta, pregunta, fragmentos),
        ),
    }

