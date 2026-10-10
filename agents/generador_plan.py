from services.cliente_ollama import consultar_modelo


class GeneradorPlan:
    def ejecutar(
        self,
        objetivo_usuario,
        ruta_aprendizaje,
        horas_por_semana,
    ):
        prompt = f"""
Eres el agente Generador de Plan de Atlas.

Tu trabajo no es decidir que tecnologias aprender: tu trabajo es convertir una
ruta de aprendizaje ya curada en un plan realista.

Objetivo del usuario:
{objetivo_usuario}

Ruta de aprendizaje definida:
{ruta_aprendizaje}

Horas disponibles:
{horas_por_semana} horas por semana

Debes generar:

1. Plan de 12 semanas.
2. Objetivos semanales.
3. Horas recomendadas por tema.
4. Actividades practicas.
5. Proyecto final sugerido.
6. Recursos locales que Atlas deberia priorizar.

Importante:

- No cambies la ruta recibida.
- Organiza el aprendizaje progresivamente.
- Se realista para la cantidad de horas disponible.
- Responde en espanol.
"""

        return consultar_modelo(prompt)
