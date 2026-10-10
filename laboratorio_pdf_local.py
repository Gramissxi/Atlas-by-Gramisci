"""Atlas: laboratorio local de PDF y recuperación offline.

Ejecutar desde la raíz del proyecto:
    pip install pypdf
    python laboratorio_pdf_local.py
Abrir http://127.0.0.1:8766

Solo para pruebas locales. Sin autenticación, no apto para uso escolar real.
"""
import json
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader
from services.fragmentacion_estructurada import fragmentar_estructurado

HOST, PORT = "127.0.0.1", 8766
MAX_PDF_BYTES = 12 * 1024 * 1024
DATABASE = Path("data/laboratorio_rag.sqlite3")
DB_LOCK = threading.Lock()

HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas · Laboratorio RAG</title>
<style>
body{font:16px system-ui,sans-serif;background:#f4f7f8;color:#152b32;margin:0}
main{max-width:800px;margin:36px auto;padding:22px}
header{background:#163b4a;color:#fff;padding:22px;border-radius:14px}h1{margin:0}
section{background:#fff;padding:22px;border:1px solid #dbe4e8;border-radius:12px;margin:18px 0}
button{background:#176875;color:white;border:0;border-radius:8px;padding:11px 17px;cursor:pointer}
input[type=text]{width:95%;padding:12px;border:1px solid #9eb3bb;border-radius:8px;margin:10px 0}
li{margin:16px 0}small,.nota{color:#4c6471}pre{white-space:pre-wrap}
</style></head><body><main>
<header><h1>✦ Atlas · Laboratorio de documentos</h1><p>PDF → texto → índice local → búsqueda con páginas</p></header>
<section><h2>1. Cargar PDF</h2><p>Solo archivos PDF con texto seleccionable. Máximo 12 MB.</p>
<input type="file" id="pdf" accept="application/pdf,.pdf"> <button id="cargar">Indexar PDF</button>
<p id="estado" role="status"></p></section>
<section><h2>2. Preguntar al documento</h2>
<label for="pregunta">Tu pregunta</label>
<input id="pregunta" type="text" placeholder="Por ejemplo: ¿qué es el ruido térmico?">
<button id="buscar">Buscar</button><p id="info" role="status"></p><ol id="resultados"></ol>
<p class="nota">Esta primera versión recupera fragmentos originales; todavía no genera explicaciones con IA.</p></section>
</main><script>
const e=id=>document.getElementById(id);
async function request(url,options){const r=await fetch(url,options);const d=await r.json();if(!r.ok)throw new Error(d.error||"Error de solicitud");return d}
e("cargar").onclick=async()=>{const f=e("pdf").files[0];if(!f)return e("estado").textContent="Seleccioná un archivo";
e("estado").textContent="Indexando, esperá...";
try{const d=await request("/api/documento",{method:"POST",headers:{"Content-Type":"application/pdf","X-Atlas-Filename":encodeURIComponent(f.name)},body:f});e("estado").textContent="Indexado: "+d.documento+" · "+d.paginas+" páginas · "+d.fragmentos+" fragmentos";}
catch(err){e("estado").textContent=err.message}};
e("buscar").onclick=async()=>{const q=e("pregunta").value.trim();if(!q)return;
e("resultados").replaceChildren();e("info").textContent="Buscando...";
try{const d=await request("/api/buscar",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pregunta:q})});
e("info").textContent=d.documento+": "+d.resultados.length+" fragmentos recuperados";
for(const item of d.resultados){const li=document.createElement("li");const h=document.createElement("strong");h.textContent="Página "+item.pagina;
const p=document.createElement("p");p.textContent=item.texto;li.append(h,p);e("resultados").append(li)}
}catch(err){e("info").textContent=err.message}};
e("pregunta").addEventListener("keydown",ev=>{if(ev.key==="Enter")e("buscar").click()});
</script></body></html>"""


def conectar():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.execute("CREATE TABLE IF NOT EXISTS documentos (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL)")
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fragmentos USING fts5(document_id UNINDEXED, pagina UNINDEXED, texto, tokenize='unicode61 remove_diacritics 2')")
    return conn


def limpiar_pregunta(pregunta):
    # Evita interpretar operadores avanzados de MATCH enviados por el navegador.
    tokens = re.findall(r"[^\W_]+", pregunta.casefold(), re.UNICODE)
    stop = {"que","como","cual","cuales","cuanto","cuantos","es","son","los","las","la","el","de","del","a","y","en","un","una","por","para","se","su","me","explica","sobre","segun","con"}
    return [token for token in tokens if len(token) > 1 and token not in stop][:15]


class API(BaseHTTPRequestHandler):
    def responder(self, contenido, codigo=200, tipo="application/json; charset=utf-8"):
        datos = contenido if isinstance(contenido, bytes) else json.dumps(contenido, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path == "/":
            return self.responder(HTML.encode("utf-8"), tipo="text/html; charset=utf-8")
        self.responder({"error":"Ruta inexistente"}, 404)

    def do_POST(self):
        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            if longitud < 1 or longitud > MAX_PDF_BYTES:
                raise ValueError("Solicitud vacía o demasiado grande (máximo 12 MB)")
            if self.path == "/api/documento":
                if self.headers.get("Content-Type", "").split(";")[0] != "application/pdf":
                    raise ValueError("El archivo debe ser PDF")
                datos = self.rfile.read(longitud)
                if not datos.startswith(b"%PDF-"):
                    raise ValueError("El archivo no contiene un encabezado PDF válido")
                from urllib.parse import unquote
                nombre = Path(unquote(self.headers.get("X-Atlas-Filename", "documento.pdf"))).name[:120]
                if not nombre.lower().endswith(".pdf"):
                    nombre += ".pdf"
                reader = PdfReader(BytesIO(datos))
                if len(reader.pages) > 500:
                    raise ValueError("Máximo 500 páginas en este laboratorio")
                fragmentos = []
                for pagina, hoja in enumerate(reader.pages, 1):
                    texto = hoja.extract_text() or ""
                    for fragmento in fragmentar_estructurado(texto):
                        fragmentos.append((pagina,fragmento))
                if not fragmentos:
                    raise ValueError("El PDF no contiene texto extraíble; necesitaríamos OCR")
                with DB_LOCK, conectar() as db:
                    db.execute("DELETE FROM fragmentos")
                    db.execute("DELETE FROM documentos")
                    id_doc = db.execute("INSERT INTO documentos (nombre) VALUES (?)",(nombre,)).lastrowid
                    db.executemany("INSERT INTO fragmentos(document_id,pagina,texto) VALUES (?,?,?)",((id_doc,p,t) for p,t in fragmentos))
                return self.responder({"documento":nombre,"paginas":len(reader.pages),"fragmentos":len(fragmentos)})
            if self.path == "/api/buscar":
                carga = json.loads(self.rfile.read(longitud))
                pregunta = carga.get("pregunta","")
                if not isinstance(pregunta,str) or len(pregunta) > 500:
                    raise ValueError("Pregunta inválida")
                tokens = limpiar_pregunta(pregunta)
                if not tokens:
                    raise ValueError("Escribí una pregunta más específica")
                # OR mantiene resultados ante vocabulario parcial; ranking bm25 ordena.
                expresion = " OR ".join('"'+t+'"' for t in tokens)
                with DB_LOCK, conectar() as db:
                    doc = db.execute("SELECT nombre FROM documentos LIMIT 1").fetchone()
                    if not doc:
                        raise ValueError("Primero indexá un documento")
                    filas = db.execute("SELECT pagina,texto FROM fragmentos WHERE fragmentos MATCH ? ORDER BY bm25(fragmentos) LIMIT 5",(expresion,)).fetchall()
                return self.responder({"documento":doc[0],"resultados":[{"pagina":p,"texto":t} for p,t in filas]})
            return self.responder({"error":"Ruta inexistente"},404)
        except (ValueError, json.JSONDecodeError) as e:
            self.responder({"error":str(e)},400)
        except Exception as e:
            # No mostrar detalles internos al navegador; registrar en terminal.
            print("Error local:",repr(e))
            self.responder({"error":"No se pudo procesar el documento"},500)


if __name__ == "__main__":
    print(f"Atlas laboratorio local: http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), API).serve_forever()
