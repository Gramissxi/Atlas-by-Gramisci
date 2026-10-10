"""Prueba aislada del indexador: no requiere base de datos ni Ollama."""
import sys
import types
import unittest
from unittest.mock import patch


class IndexadorTests(unittest.TestCase):
    def test_registra_pagina_correcta_y_omite_vacia(self):
        # Inyectar dependencias externas antes de importar el indexador.
        fake_incrustaciones = types.ModuleType("services.incrustaciones")
        fake_incrustaciones.generar_incrustacion = lambda texto: [0.1, 0.2]
        fake_repo = types.ModuleType("services.repositorio_conocimiento")
        registros = []
        fake_repo.guardar_fragmento_conocimiento = lambda **kwargs: registros.append(kwargs)
        with patch.dict(sys.modules, {
            "services.incrustaciones": fake_incrustaciones,
            "services.repositorio_conocimiento": fake_repo,
        }):
            import importlib
            sys.modules.pop("services.indexador", None)
            indexador = importlib.import_module("services.indexador")
            with patch.object(indexador, "leer_pdf_por_paginas", return_value=[
                (1, "La señal es periódica."),
                (2, ""),
                (3, "La frecuencia es la inversa del período."),
            ]):
                indexador.indexar_pdf("senales.pdf", "Telecomunicaciones")
        self.assertEqual([r["pagina_inicio"] for r in registros], [1, 3])
        self.assertEqual([r["pagina_fin"] for r in registros], [1, 3])
        self.assertEqual([r["numero_fragmento"] for r in registros], [1, 2])


if __name__ == "__main__":
    unittest.main()
