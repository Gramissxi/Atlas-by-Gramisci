import json

from services.cliente_ollama import consultar_modelo


class CuradorConocimiento:
    def ejecutar(self, texto_documento):
        prompt = f"""
Eres un analista pedagogico de Atlas especializado en construir materias desde
material educativo local.

Analiza el siguiente material.

Debes identificar:

1. Nombre probable de la materia.
2. Temas principales.
3. Conceptos clave.
4. Orden recomendado de aprendizaje.
5. Posibles vacios que convendria complementar cuando haya internet.

Devuelve exclusivamente un JSON valido con este formato:

{{
    "materia": "",
    "temas": [],
    "conceptos": [],
    "ruta": [],
    "complementos_sugeridos": []
}}

Material:

{texto_documento}
"""

        respuesta = consultar_modelo(prompt)
        print("\nRESPUESTA MODELO:\n")
        print(respuesta)

        respuesta = respuesta.replace("```json", "")
        respuesta = respuesta.replace("```", "")
        respuesta = respuesta.strip()

        try:
            return json.loads(respuesta)
        except Exception:
            return {
                "materia": "Materia no detectada",
                "temas": [],
                "conceptos": [],
                "ruta": [],
                "complementos_sugeridos": [],
            }
