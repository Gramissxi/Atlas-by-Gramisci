from services.cliente_ollama import consultar_modelo


class CuradorRuta:
    def ejecutar(self, objetivo_usuario):
        prompt = f"""
Eres el agente Curador de Ruta de Atlas.

Atlas es una Encarta moderna offline-first: primero usa la biblioteca local del
estudiante y, cuando hay internet, complementa con fuentes externas curadas.

Objetivo del estudiante:

{objetivo_usuario}

Debes devolver:

1. Objetivo detectado.
2. Habilidades necesarias.
3. Orden recomendado de aprendizaje.
4. Proyectos sugeridos.
5. Brechas de conocimiento.
6. Que informacion conviene buscar en la biblioteca local.
7. Que informacion podria complementarse con internet cuando este disponible.

No generes cronogramas ni planes semanales.
Responde siempre en espanol.
"""

        return consultar_modelo(prompt)
