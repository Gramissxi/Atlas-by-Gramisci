import io
import json
import unittest
from unittest.mock import patch
from services.generador_rag_aulas import responder_con_documentos


class MockResponse:
    def __enter__(self):
        return io.BytesIO(json.dumps({"message":{"content":"La entropía mide incertidumbre (página 2)."}}).encode())
    def __exit__(self, *args):
        return False


class GeneradorTests(unittest.TestCase):
    def test_sin_fragmentos_no_llama_ollama(self):
        with patch("services.generador_rag_aulas.urlopen") as llamada:
            r = responder_con_documentos("¿Qué es entropía?", [])
            self.assertEqual(r["modo"], "sin_contexto")
            llamada.assert_not_called()

    def test_respuesta_con_fuente(self):
        fragmentos = [{"nombre":"Teoria.pdf","pagina":2,"texto":"La entropía mide incertidumbre."}]
        with patch("services.generador_rag_aulas.urlopen", return_value=MockResponse()) as llamada:
            r = responder_con_documentos("¿Qué es entropía?", fragmentos)
            self.assertEqual(r["modo"], "ollama_local")
            payload = json.loads(llamada.call_args.args[0].data)
            self.assertIn("Teoria.pdf", payload["messages"][1]["content"])
            self.assertIn("página 2", payload["messages"][1]["content"])

    def test_fallo_de_ollama_devuelve_fuentes_sin_generar(self):
        fragmentos = [{"nombre":"A.pdf","pagina":1,"texto":"Un texto"}]
        with patch("services.generador_rag_aulas.urlopen", side_effect=OSError("No disponible")):
            r = responder_con_documentos("Pregunta", fragmentos)
            self.assertEqual(r["modo"], "solo_fragmentos")


if __name__ == "__main__":
    unittest.main()
