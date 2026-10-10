from agents.curador_ruta import CuradorRuta
from agents.evaluador import Evaluador
from agents.generador_plan import GeneradorPlan
from agents.orquestador import Orquestador
from services.sincronizacion import describir_modo_atlas, hay_conexion_disponible


def main():
    print("\n=== Atlas ===\n")

    estado_modo = describir_modo_atlas(hay_conexion_disponible())
    print(f"Modo actual: {estado_modo['modo']}")
    print(estado_modo["descripcion"])

    consulta = input("\nComo puedo ayudarte?\n\n")

    orquestador = Orquestador()
    perfil = orquestador.obtener_contexto_usuario()

    print("\n=== PERFIL ACTUAL ===\n")
    print(perfil)

    intencion = orquestador.detectar_intencion(consulta)
    print(f"\n[ORQUESTADOR] Intencion detectada: {intencion}\n")

    if intencion == "curador":
        agente = CuradorRuta()
        respuesta = agente.ejecutar(consulta)

    elif intencion == "generador":
        ruta_aprendizaje = input("\nPega tu ruta de aprendizaje:\n\n")
        horas = input("\nHoras por semana:\n\n")

        agente = GeneradorPlan()
        respuesta = agente.ejecutar(
            consulta,
            ruta_aprendizaje,
            horas,
        )

    elif intencion == "evaluador":
        ruta_aprendizaje = input("\nPega tu ruta de aprendizaje:\n\n")
        plan = input("\nPega tu plan:\n\n")

        agente = Evaluador()
        respuesta = agente.ejecutar(
            consulta,
            ruta_aprendizaje,
            plan,
        )

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

    else:
        respuesta = """
No pude identificar exactamente que necesitas.

Proba con:
- Quiero convertirme en Data Engineer
- Generar un plan de estudio
- Quiero practicar SQL
- Seguimos
"""

    print("\n=== RESPUESTA ===\n")
    print(respuesta)


if __name__ == "__main__":
    main()
