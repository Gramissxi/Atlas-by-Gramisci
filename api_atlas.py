import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from services.estudio_documento import (
    consultar_documento_con_ollama,
    crear_practica_con_ollama,
    ver_fragmentos_con_ollama,
)
from services.metodologias_estudio import recargar_metodologias_si_hay_internet


class ManejadorAtlas(BaseHTTPRequestHandler):
    def _enviar_json(self, datos, estado=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        """Comprobacion liviana: no inicia Ollama ni consulta la base de datos."""
        if self.path == "/health":
            self._enviar_json({"estado": "ok", "servicio": "atlas-api"})
            return
        self._enviar_json({"error": "Ruta no encontrada"}, estado=404)

    def do_OPTIONS(self):
        self._enviar_json({"ok": True})

    def do_POST(self):
        longitud = int(self.headers.get("Content-Length", "0"))
        cuerpo = self.rfile.read(longitud).decode("utf-8") if longitud else "{}"

        try:
            datos = json.loads(cuerpo)
        except json.JSONDecodeError:
            self._enviar_json({"error": "JSON invalido"}, estado=400)
            return

        documento = datos.get("documento", "")
        materia = datos.get("materia", "")
        paso_ruta = datos.get("paso_ruta", "")
        pregunta = datos.get("pregunta", "")
        modelo = datos.get("modelo", "ollama-local")
        document_id = datos.get("document_id")
        section_id = datos.get("section_id")
        fragment_ids = datos.get("fragment_ids", [])
        dificultad = datos.get("difficulty_level")

        if isinstance(fragment_ids, (str, int)):
            fragment_ids = [fragment_ids]

        try:
            if self.path == "/api/estudio/fragmentos":
                respuesta = ver_fragmentos_con_ollama(
                    documento=documento,
                    materia=materia,
                    paso_ruta=paso_ruta,
                    document_id=document_id,
                    section_id=section_id,
                    fragment_ids=fragment_ids,
                )
                self._enviar_json(respuesta)
                return

            if self.path == "/api/estudio/consultar":
                if modelo != "ollama-local":
                    self._enviar_json(
                        {
                            "error": "Modelo online no configurado",
                            "detalle": "La consulta online queda preparada para cuando Atlas tenga una API externa configurada.",
                        },
                        estado=501,
                    )
                    return

                respuesta = consultar_documento_con_ollama(
                    documento=documento,
                    materia=materia,
                    paso_ruta=paso_ruta,
                    pregunta=pregunta,
                    document_id=document_id,
                    section_id=section_id,
                    fragment_ids=fragment_ids,
                )
                self._enviar_json(respuesta)
                return
            if self.path == "/api/estudio/practica":
                respuesta = crear_practica_con_ollama(
                    documento=documento,
                    materia=materia,
                    paso_ruta=paso_ruta,
                    document_id=document_id,
                    section_id=section_id,
                    fragment_ids=fragment_ids,
                    modelo=modelo,
                    dificultad=dificultad,
                )
                self._enviar_json(respuesta)
                return

            if self.path == "/api/metodologias/recargar":
                self._enviar_json(recargar_metodologias_si_hay_internet())
                return

            self._enviar_json({"error": "Ruta no encontrada"}, estado=404)

        except Exception as error:
            self._enviar_json(
                {
                    "error": "No se pudo completar la accion local",
                    "detalle": str(error),
                },
                estado=500,
            )


def ejecutar_api(host="127.0.0.1", puerto=8765):
    servidor = HTTPServer((host, puerto), ManejadorAtlas)
    print(f"Atlas API local escuchando en http://{host}:{puerto}")
    servidor.serve_forever()


if __name__ == "__main__":
    ejecutar_api()
