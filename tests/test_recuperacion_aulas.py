import sqlite3
import unittest
from services.recuperacion_aulas import recuperar

class RecuperacionAulasTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE documentos (id INTEGER PRIMARY KEY,nombre TEXT)")
        self.db.execute("INSERT INTO documentos VALUES (1,'Tema.pdf')")
        self.db.execute("INSERT INTO documentos VALUES (2,'Privado.pdf')")
        self.db.execute("CREATE VIRTUAL TABLE fragmentos USING fts5(documento_id UNINDEXED,aula_id UNINDEXED,pagina UNINDEXED,texto,tokenize='unicode61 remove_diacritics 2')")
        self.db.execute("INSERT INTO fragmentos VALUES (1,1,4,'La entropía mide la incertidumbre de una fuente.')")
        self.db.execute("INSERT INTO fragmentos VALUES (1,1,6,'La teoría de la información estudia los mensajes.')")
        self.db.execute("INSERT INTO fragmentos VALUES (2,2,8,'Dato secreto sobre entropía e información.')")

    def tearDown(self):
        self.db.close()

    def test_retorna_relevantes_del_aula(self):
        r = recuperar(self.db, 1, "¿Qué es la entropía?")
        self.assertTrue(r)
        self.assertEqual(r[0]["pagina"],4)
        self.assertTrue(all(item["nombre"]=="Tema.pdf" for item in r))

    def test_aislamiento_por_aula(self):
        r = recuperar(self.db, 1, "secreto entropía información")
        self.assertTrue(all("secreto" not in x["texto"] for x in r))

    def test_prioriza_definicion_sobre_temario(self):
        self.db.execute("INSERT INTO fragmentos VALUES (1,1,2,'Índice\\nCanal de comunicación\\nRuido\\nEmisor\\nReceptor\\nSeñal\\nCódigos')")
        self.db.execute("INSERT INTO fragmentos VALUES (1,1,31,'El canal de comunicación es el medio físico y lógico que conecta emisor y receptor.')")
        resultado = recuperar(self.db, 1, "¿Qué es el canal de comunicación?")
        self.assertTrue(resultado)
        self.assertEqual(resultado[0]["pagina"],31)

    def test_seleccion_de_un_documento(self):
        self.db.execute("INSERT INTO documentos VALUES (3,'Otra unidad.pdf')")
        self.db.execute("INSERT INTO fragmentos VALUES (3,1,15,'Entropía e información de otra unidad')")
        r = recuperar(self.db, 1, "entropia informacion", documentos_ids=[1])
        self.assertTrue(r)
        self.assertTrue(all(item["documento_id"] == 1 for item in r))
        self.assertTrue(all(item["nombre"] != "Otra unidad.pdf" for item in r))

    def test_sin_documentos(self):
        self.assertEqual(recuperar(self.db, 1, "entropia", documentos_ids=[]), [])

    def test_consulta_sencilla(self):
        r = recuperar(self.db, 1, "informacion")
        self.assertTrue(r)

if __name__=="__main__":
    unittest.main()
