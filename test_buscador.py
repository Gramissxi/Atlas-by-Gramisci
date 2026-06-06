from services.buscador import buscar_chunks

resultados = buscar_chunks(
    "Taylor"
)

for resultado in resultados:

    print("\n=================\n")

    print(resultado)