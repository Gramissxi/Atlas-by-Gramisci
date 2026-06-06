from services.documentos import listar_documentos

documentos = listar_documentos()

for doc in documentos:

    print(doc)