from services.buscador import buscar_hibrido


resultados = buscar_hibrido("Taylor")

for resultado in resultados:
    print("\n=================\n")
    print(resultado)
