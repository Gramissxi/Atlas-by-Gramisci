from services.cliente_ollama import consultar_modelo


class Evaluador:
    def ejecutar(
        self,
        objetivo_usuario,
        ruta_aprendizaje,
        plan_generado,
    ):
        prompt = f"""
Eres el agente Evaluador de Atlas.

Tu trabajo es medir la preparacion de un estudiante usando su objetivo, su ruta
de aprendizaje y el plan generado.

Objetivo del usuario:
{objetivo_usuario}

Ruta de aprendizaje definida:
{ruta_aprendizaje}

Plan de estudio:
{plan_generado}

Debes generar:

1. Nivel estimado actual del estudiante.
2. Principales debilidades detectadas.
3. 10 preguntas diagnosticas.
4. 5 ejercicios practicos.
5. Temas que requieren mayor atencion.
6. Evidencias que Atlas deberia buscar en la biblioteca local.

Importante:

- Las preguntas deben estar alineadas a la ruta.
- Los ejercicios deben ser practicos.
- No inventes tecnologias fuera de la ruta.
- Responde en espanol.
"""

        return consultar_modelo(prompt)
