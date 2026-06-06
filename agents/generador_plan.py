from services.cliente_ollama import consultar_modelo


class GeneradorPlan:

    def ejecutar(
        self,
        objetivo_usuario,
        roadmap_generado,
        horas_por_semana
    ):

        prompt = f"""
Eres el agente Generador de Plan de Pocket Mentor AI.

Tu trabajo NO es decidir qué tecnologías aprender.

Tu trabajo es construir un cronograma realista utilizando:

OBJETIVO DEL USUARIO:
{objetivo_usuario}

ROADMAP DEFINIDO POR EL CURADOR:
{roadmap_generado}

HORAS DISPONIBLES:
{horas_por_semana} horas por semana

Debes generar:

1. Plan de 12 semanas.
2. Objetivos semanales.
3. Horas recomendadas por tema.
4. Actividades prácticas.
5. Proyecto final sugerido.

IMPORTANTE:

- No cambies el roadmap recibido.
- Organiza el aprendizaje progresivamente.
- Sé realista para la cantidad de horas disponible.
- Responde en español.
"""

        return consultar_modelo(prompt)