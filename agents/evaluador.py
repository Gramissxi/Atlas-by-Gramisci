from services.cliente_ollama import consultar_modelo


class Evaluador:

    def ejecutar(
        self,
        objetivo_usuario,
        roadmap_generado,
        plan_generado
    ):

        prompt = f"""
Eres el agente Evaluador de Pocket Mentor AI.

Tu trabajo es medir la preparación de un estudiante.

OBJETIVO DEL USUARIO:
{objetivo_usuario}

ROADMAP DEFINIDO:
{roadmap_generado}

PLAN DE ESTUDIO:
{plan_generado}

Debes generar:

1. Nivel estimado actual del estudiante.
2. Principales debilidades detectadas.
3. 10 preguntas diagnósticas.
4. 5 ejercicios prácticos.
5. Temas que requieren mayor atención.

IMPORTANTE:

- Las preguntas deben estar alineadas al roadmap.
- Los ejercicios deben ser prácticos.
- No inventes tecnologías fuera del roadmap.
- Responde en español.
"""

        return consultar_modelo(prompt)