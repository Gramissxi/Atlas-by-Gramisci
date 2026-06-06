from agents.orquestador import Orquestador
from agents.curador_ruta import CuradorRuta
from agents.generador_plan import GeneradorPlan
from agents.evaluador import Evaluador


def main():

    print("\n=== Pocket Mentor AI ===\n")

    consulta = input(
        "¿Cómo puedo ayudarte?\n\n"
    )

    orquestador = Orquestador()

    perfil = orquestador.obtener_contexto_usuario()

    print("\n=== PERFIL ACTUAL ===\n")
    print(perfil)

    intencion = orquestador.detectar_intencion(
        consulta
    )

    print(
        f"\n[ORQUESTADOR] Intención detectada: {intencion}\n"
    )

    # CURADOR
    if intencion == "curador":

        agente = CuradorRuta()

        respuesta = agente.ejecutar(
            consulta
        )

    # GENERADOR DE PLAN
    elif intencion == "generador":

        roadmap = input(
            "\nPegá tu roadmap:\n\n"
        )

        horas = input(
            "\nHoras por semana:\n\n"
        )

        agente = GeneradorPlan()

        respuesta = agente.ejecutar(
            consulta,
            roadmap,
            horas
        )

    # EVALUADOR
    elif intencion == "evaluador":

        roadmap = input(
            "\nPegá tu roadmap:\n\n"
        )

        plan = input(
            "\nPegá tu plan:\n\n"
        )

        agente = Evaluador()

        respuesta = agente.ejecutar(
            consulta,
            roadmap,
            plan
        )

    # CONTINUAR
    elif intencion == "continuar":

        respuesta = f"""
Objetivo actual: {perfil['objetivo']}

Tema actual: {perfil['tema_actual']}

Avance: {perfil['avance_porcentaje']}%

Habilidades registradas:
{', '.join(perfil['habilidades'])}

Evaluaciones realizadas:
{perfil['evaluaciones_realizadas']}
"""

    # FALLBACK
    else:

        respuesta = """
No pude identificar exactamente qué necesitás.

Probá con:
- Quiero convertirme en Data Engineer
- Generar un plan de estudio
- Quiero practicar SQL
- Seguimos
"""

    print("\n=== RESPUESTA ===\n")
    print(respuesta)


if __name__ == "__main__":
    main()