from pathlib import Path

from services.fragmentacion import dividir_texto_en_fragmentos
from services.incrustaciones import generar_incrustacion
from services.lector_pdf import leer_pdf
from services.repositorio_conocimiento import guardar_fragmento_conocimiento


def indexar_pdf(ruta_pdf, materia):
    print(f"\nIndexando documento: {ruta_pdf}")

    texto = leer_pdf(ruta_pdf)
    fragmentos = dividir_texto_en_fragmentos(texto)

    print(f"Fragmentos generados: {len(fragmentos)}")

    nombre_documento = Path(ruta_pdf).name

    for numero_fragmento, contenido_fragmento in enumerate(
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
        )

        print(f"Fragmento {numero_fragmento} guardado")

    print(f"\nDocumento indexado correctamente: {nombre_documento}")
