import unittest
from unittest.mock import patch
from services.generacion_equilibrada_aulas import generar_equilibrado


class FakeDB:
    pass


class TestGeneracionEquilibrada(unittest.TestCase):
    def test_tres_documentos_cinco_preguntas(self):
        llamadas = []

        def recuperar_falso(db, aula_id, texto, limite, documentos_ids):
            doc_id = documentos_ids[0]
            return [{"documento_id":doc_id,"nombre":f"PDF {doc_id}","pagina":1,"texto":"Contenido suficiente"}]

        def generar_falso(fragmentos, cantidad, dificultad, formato):
            doc_id = fragmentos[0]["documento_id"]
            llamadas.append((doc_id,cantidad,formato))
            return [f"PDF {doc_id} {formato} {n}" for n in range(cantidad)]

        with patch("services.generacion_equilibrada_aulas.recuperar", side_effect=recuperar_falso), \
             patch("services.generacion_equilibrada_aulas.generar_preguntas", side_effect=generar_falso):
            preguntas, fuentes = generar_equilibrado(FakeDB(),1,[11,22,33],5,"media","multiple")
        self.assertEqual([p.split()[1] for p in preguntas],["11","22","33","11","22"])
        self.assertEqual(llamadas,[(11,2,"multiple"),(22,2,"multiple"),(33,1,"multiple")])
        self.assertEqual({f["documento_id"] for f in fuentes},{11,22,33})

    def test_mixto_global_alternado(self):
        def recuperar_falso(db,aula_id,texto,limite,documentos_ids):
            return [{"documento_id":documentos_ids[0],"nombre":"Doc","pagina":2,"texto":"material"}]
        def generar_falso(fragmentos,cantidad,dificultad,formato):
            doc_id=fragmentos[0]["documento_id"]
            return [f"{doc_id}:{formato}:{i}" for i in range(cantidad)]
        with patch("services.generacion_equilibrada_aulas.recuperar",side_effect=recuperar_falso), \
             patch("services.generacion_equilibrada_aulas.generar_preguntas",side_effect=generar_falso):
            preguntas,_=generar_equilibrado(FakeDB(),1,[11,22,33],5,"media","mixto")
        self.assertEqual([p.split(":")[1] for p in preguntas],["multiple","desarrollo","multiple","desarrollo","multiple"])

    def test_mas_documentos_que_preguntas(self):
        with self.assertRaises(ValueError):
            generar_equilibrado(FakeDB(),1,[1,2,3,4],3,"media","multiple")


if __name__=="__main__":
    unittest.main()
