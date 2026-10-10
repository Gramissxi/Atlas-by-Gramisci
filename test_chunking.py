from services.fragmentacion import dividir_texto_en_fragmentos
from services.lector_pdf import leer_pdf


texto = leer_pdf(
    "data/documentos/calculo/Modelo de examen - C1.pdf"
)

fragmentos = dividir_texto_en_fragmentos(texto)

print(f"Cantidad de fragmentos: {len(fragmentos)}")
print("\nPrimer fragmento:\n")
print(fragmentos[0])
