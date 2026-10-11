import unittest
import json
from io import BytesIO
from unittest.mock import patch
from services.generacion_equilibrada_aulas import generar_equilibrado, clave_pregunta
from services.generador_evaluaciones_aulas import generar_preguntas, _generar_lote


class FakeDB:
    def execute(self, *args):
        return []


class TestGeneracionEquilibrada(unittest.TestCase):
    def test_claves_diferencian_preguntas_y_omiten_alternativas(self):
        primera = "¿Qué es la entropía? A) Uno B) Dos C) Tres D) Cuatro"
        segunda = "¿Cuál es la unidad del decibel?"
        repetida = "¿QUÉ ES LA ENTROPÍA? A) Cinco B) Seis C) Siete D) Ocho"
        self.assertNotEqual(clave_pregunta(primera), clave_pregunta(segunda))
        self.assertEqual(clave_pregunta(primera), clave_pregunta(repetida))
        self.assertTrue(clave_pregunta(segunda))

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

    def test_duplicate_question_retried_once(self):
        llamadas=[]
        def recuperar_falso(db,aula_id,texto,limite,documentos_ids):
            return [{"documento_id":documentos_ids[0],"nombre":"Doc","pagina":2,"texto":"material"}]
        def generar_falso(fragmentos,cantidad,dificultad,formato,modelo=None,excluir=None):
            doc=fragmentos[0]["documento_id"]
            llamadas.append((doc,excluir))
            if excluir:
                return ["¿Qué es una señal?"]
            if doc==11:
                return ["¿Qué es la entropía?"]
            return ["¿Qué es la entropía?"]
        with patch("services.generacion_equilibrada_aulas.recuperar",side_effect=recuperar_falso), \
             patch("services.generacion_equilibrada_aulas.generar_preguntas",side_effect=generar_falso):
            preguntas,_=generar_equilibrado(FakeDB(),1,[11,22],2,"media","desarrollo")
        self.assertEqual(preguntas,["¿Qué es la entropía?","¿Qué es una señal?"])
        self.assertEqual(len(llamadas),3)

    def test_lote_invalido_se_divide_en_generaciones_unitarias(self):
        llamadas=[]
        def simulacion(fragmentos,cantidad,dificultad,formato,modelo=None,excluir=None):
            llamadas.append(cantidad)
            if cantidad>1:
                raise ValueError("La IA devolvió una pregunta en vez de dos")
            return ["¿Qué es una señal?" if excluir else "¿Qué es la entropía?"]
        with patch("services.generador_evaluaciones_aulas._generar_lote",side_effect=simulacion):
            preguntas=generar_preguntas([{"nombre":"Doc","pagina":1,"texto":"Texto"}],2,"media","desarrollo")
        self.assertEqual(llamadas,[2,1,1])
        self.assertEqual(len(preguntas),2)
        self.assertNotEqual(preguntas[0],preguntas[1])

    def test_modelo_devuelve_cinco_cuando_se_pide_una(self):
        items=[{"enunciado":f"¿Qué ocurre con la señal número {i}?","opciones":["Uno","Dos","Tres","Cuatro"]} for i in range(5)]
        contenido=json.dumps({"message":{"content":json.dumps({"preguntas":items})},"eval_count":80,"done_reason":"stop"}).encode("utf-8")
        class Respuesta:
            def __enter__(self):
                return BytesIO(contenido)
            def __exit__(self,*args):
                return False
        fuentes=[{"nombre":"PDF de señales","pagina":3,"texto":"Conceptos de señales y telecomunicaciones"}]
        with patch("services.generador_evaluaciones_aulas.urlopen",return_value=Respuesta()):
            preguntas=_generar_lote(fuentes,1,"media","multiple")
        self.assertEqual(len(preguntas),1)
        self.assertIn("A) Uno",preguntas[0])
        self.assertIn("\nB) Dos",preguntas[0])

    def test_mas_documentos_que_preguntas(self):
        with self.assertRaises(ValueError):
            generar_equilibrado(FakeDB(),1,[1,2,3,4],3,"media","multiple")


if __name__=="__main__":
    unittest.main()
