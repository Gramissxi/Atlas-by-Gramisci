from services.perfil_usuario import cargar_perfil


class Orquestador:
    def detectar_intencion(self, consulta):
        consulta = consulta.lower()

        if any(
            palabra in consulta
            for palabra in [
                "ruta",
                "aprender",
                "convertirme",
                "carrera",
                "camino",
            ]
        ):
            return "curador"

        if any(
            palabra in consulta
            for palabra in [
                "plan",
                "cronograma",
                "semanal",
            ]
        ):
            return "generador"

        if any(
            palabra in consulta
            for palabra in [
                "evaluar",
                "examen",
                "preguntas",
                "practicar",
            ]
        ):
            return "evaluador"

        if "seguimos" in consulta:
            return "continuar"

        return "curador"

    def obtener_contexto_usuario(self):
        return cargar_perfil()
