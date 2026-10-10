from services.fragmentacion import dividir_texto_en_fragmentos
from services.incrustaciones import generar_incrustacion
from services.lector_pdf import leer_pdf


texto = leer_pdf(
    "data/documentos/calculo/Modelo de examen - C1.pdf"
)

fragmentos = dividir_texto_en_fragmentos(texto)
incrustacion = generar_incrustacion(fragmentos[0])

print(f"Dimension incrustacion: {len(incrustacion)}")
print(incrustacion[:10])
