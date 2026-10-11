"""Regresión: FTS5 preserva el tipo entero en columnas UNINDEXED.

Ejecutar: python -m unittest tests.test_filtro_aula_fts5 -v
"""
import sqlite3
import unittest


class FiltroAulaFTS5Tests(unittest.TestCase):
    def test_filtra_por_aula_con_entero(self):
        db = sqlite3.connect(":memory:")
        try:
            db.execute("CREATE VIRTUAL TABLE fragmentos USING fts5(aula_id UNINDEXED, texto)")
            db.execute("INSERT INTO fragmentos(aula_id,texto) VALUES (?,?)", (1, "La entropía mide información."))
            db.execute("INSERT INTO fragmentos(aula_id,texto) VALUES (?,?)", (2, "Documento de otra clase."))
            correcto = db.execute("SELECT count(*) FROM fragmentos WHERE aula_id=?", (1,)).fetchone()[0]
            erroneo = db.execute("SELECT count(*) FROM fragmentos WHERE aula_id=?", ("1",)).fetchone()[0]
            self.assertEqual(correcto, 1)
            self.assertEqual(erroneo, 0)
            busqueda = db.execute("SELECT texto FROM fragmentos WHERE aula_id=? AND fragmentos MATCH ?", (1, "entropía")).fetchall()
            self.assertEqual(len(busqueda), 1)
            ajeno = db.execute("SELECT texto FROM fragmentos WHERE aula_id=? AND fragmentos MATCH ?", (2, "entropía")).fetchall()
            self.assertEqual(ajeno, [])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
