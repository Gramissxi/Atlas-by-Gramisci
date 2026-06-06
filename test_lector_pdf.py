from services.lector_pdf import leer_pdf

ruta = "data/documentos/calculo/Modelo de examen - C1.pdf"

texto = leer_pdf(ruta)

print(texto[:3000])