FRAGMENTOS_MOCK = [
    {
        "fragment_id": 2101,
        "numero_fragmento": 2101,
        "document_id": 2,
        "section_id": 201,
        "materia": "Ingenieria de Datos II",
        "documento": "IDD-II_Clase07_AFB.pdf",
        "titulo": "Modelo conceptual del pipeline",
        "contenido": (
            "Un pipeline de datos es una secuencia controlada de etapas que mueve datos desde "
            "una fuente hasta un destino de analisis o consumo. En el modelo conceptual se "
            "separan responsabilidades: ingesta, validacion, transformacion, almacenamiento y "
            "exposicion. La separacion permite entender donde entra el dato, donde se controla "
            "su calidad, donde cambia su forma y donde queda disponible para consultas o modelos."
        ),
    },
    {
        "fragment_id": 2102,
        "numero_fragmento": 2102,
        "document_id": 2,
        "section_id": 201,
        "materia": "Ingenieria de Datos II",
        "documento": "IDD-II_Clase07_AFB.pdf",
        "titulo": "Componentes y flujo del pipeline",
        "contenido": (
            "El flujo conceptual del pipeline comienza con fuentes operacionales, archivos, "
            "eventos o APIs. Luego una capa de ingesta registra los datos crudos y una capa de "
            "validacion detecta formatos invalidos, duplicados o campos obligatorios ausentes. "
            "Despues, la transformacion normaliza, enriquece y relaciona los datos antes de "
            "publicarlos en una zona preparada para analitica, tableros, servicios o aprendizaje automatico."
        ),
    },
]


def _a_entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _normalizar_ids(fragment_ids):
    ids = []

    if fragment_ids is None:
        return ids

    if isinstance(fragment_ids, (str, int)):
        fragment_ids = [fragment_ids]

    for valor in fragment_ids:
        numero = _a_entero(valor)
        if numero is not None:
            ids.append(numero)

    return ids


def normalizar_fragmento_mock(fragmento):
    return {
        "materia": fragmento["materia"],
        "documento": fragmento["documento"],
        "numero_fragmento": fragmento["numero_fragmento"],
        "contenido": fragmento["contenido"],
        "document_id": fragmento["document_id"],
        "section_id": fragmento["section_id"],
        "fragment_id": fragmento["fragment_id"],
        "titulo": fragmento["titulo"],
        "fuente": "mock-local",
    }


def buscar_fragmentos_mock(document_id=None, section_id=None, fragment_ids=None, limite=5):
    document_id = _a_entero(document_id)
    section_id = _a_entero(section_id)
    ids = set(_normalizar_ids(fragment_ids))
    encontrados = []

    for fragmento in FRAGMENTOS_MOCK:
        if ids and fragmento["fragment_id"] not in ids:
            continue

        if document_id is not None and fragmento["document_id"] != document_id:
            continue

        if section_id is not None and fragmento["section_id"] != section_id:
            continue

        encontrados.append(normalizar_fragmento_mock(fragmento))

    return encontrados[:limite]
