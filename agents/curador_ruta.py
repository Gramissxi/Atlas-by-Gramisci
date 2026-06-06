from services.cliente_ollama import consultar_modelo


class CuradorRuta:

    def ejecutar(self, objetivo_usuario):

        prompt = f"""
Eres el agente Curador de Ruta de Aprendizaje de Pocket Mentor AI.

Tu función es ayudar a estudiantes a alcanzar objetivos tecnológicos.

Objetivo del estudiante:

{objetivo_usuario}

Debes devolver:

1. Objetivo detectado.
2. Habilidades necesarias.
3. Orden recomendado de aprendizaje.
4. Proyectos sugeridos.
5. Posibles brechas de conocimiento.

NO generes cronogramas ni planes semanales.

Tu única responsabilidad es definir:

- habilidades necesarias
- orden de aprendizaje
- brechas de conocimiento
- proyectos sugeridos

El cronograma será responsabilidad de otro agente.
Responde siempre en español.
"""

        return consultar_modelo(prompt)