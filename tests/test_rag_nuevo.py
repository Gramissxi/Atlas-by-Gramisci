import unittest

from services.fragmentacion_estructurada import fragmentar_estructurado
from services.fusion_rankings import fusionar_por_rrf


class FragmentacionTests(unittest.TestCase):
    def test_vacio(self):
        self.assertEqual(fragmentar_estructurado(""), [])

    def test_no_corta_parrafo_corto(self):
        self.assertEqual(fragmentar_estructurado("Una oración. Otra oración.", 100), ["Una oración. Otra oración."])

    def test_limite_estricto(self):
        fragmentos = fragmentar_estructurado("Palabra " * 70, max_caracteres=50)
        self.assertTrue(fragmentos)
        self.assertTrue(all(len(f) <= 50 for f in fragmentos))

    def test_contenido_no_perdido(self):
        texto = "Fotosíntesis: las plantas usan luz. " * 12
        fragmentos = fragmentar_estructurado(texto, max_caracteres=85)
        self.assertEqual(" ".join(" ".join(fragmentos).split()), " ".join(texto.split()))

    def test_parametros(self):
        with self.assertRaises(ValueError):
            fragmentar_estructurado("abc", 0)


class FusionTests(unittest.TestCase):
    def test_documento_presente_en_dos_listas_subira(self):
        a = {"materia": "Ciencias", "documento": "a.pdf", "numero_fragmento": 1, "contenido": "uno"}
        b = {"materia": "Ciencias", "documento": "a.pdf", "numero_fragmento": 2, "contenido": "dos"}
        c = {"materia": "Ciencias", "documento": "a.pdf", "numero_fragmento": 3, "contenido": "tres"}
        resultado = fusionar_por_rrf([a, b], [c, b])
        self.assertEqual(resultado[0]["numero_fragmento"], 2)
        self.assertEqual(set(resultado[0]["fuentes"]), {"texto", "semantica"})

    def test_limite(self):
        a = {"materia": "M", "documento": "D", "numero_fragmento": 1}
        self.assertEqual(len(fusionar_por_rrf([a], [], limite=1)), 1)


if __name__ == "__main__":
    unittest.main()
