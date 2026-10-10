from services.repositorio_conocimiento import guardar_fragmento_conocimiento


guardar_fragmento_conocimiento(
    materia="calculo",
    documento="prueba.pdf",
    numero_fragmento=1,
    contenido="Este es un fragmento de prueba",
    incrustacion=[0.0] * 768,
)

print("Fragmento insertado correctamente")
