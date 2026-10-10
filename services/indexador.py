from pathlib import Path

from services.fragmentacion_estructurada import fragmentar_estructurado
from services.incrustaciones import generar_incrustacion
from services.lector_pdf import leer_pdf_por_paginas
from services.repositorio_conocimiento import guardar_fragmento_conocimiento


def indexar_pdf(ruta_pdf, materia):
    print(f"\nIndexando documento: {ruta_pdf}")

    fragmentos = [
        (pagina, fragmento)
        for pagina, texto in leer_pdf_por_paginas(ruta_pdf)
        for fragmento in fragmentar_estructurado(texto)
    ]

    print(f"Fragmentos generados: {len(fragmentos)}")

    nombre_documento = Path(ruta_pdf).name

    for numero_fragmento, (pagina, contenido_fragmento) in enumerate(
        fragmentos,
        start=1,
    ):
        incrustacion = generar_incrustacion(contenido_fragmento)

        guardar_fragmento_conocimiento(
            materia=materia,
            documento=nombre_documento,
            numero_fragmento=numero_fragmento,
            contenido=contenido_fragmento,
            incrustacion=incrustacion,
            pagina_inicio=pagina,
            pagina_fin=pagina,
        )

        print(f"Fragmento {numero_fragmento} guardado")

    print(f"\nDocumento indexado correctamente: {nombre_documento}")
