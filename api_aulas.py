"""Atlas Aulas: API de prototipo con roles y aislamiento por clase.

Ejecutar en el equipo central: python api_aulas.py
Docentes: definir ATLAS_CLAVE_ALTA_DOCENTE antes de crear su cuenta.
NO apto para producción con menores: falta HTTPS, auditoría, recuperación de cuentas,
aprobación institucional, políticas de retención y sincronización offline segura.
"""
import base64
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pypdf import PdfReader
from services.fragmentacion_estructurada import fragmentar_estructurado

DB = Path("data/atlas_aulas_demo.sqlite3")
LOCK = threading.Lock()
MAX_BODY = 16 * 1024 * 1024
MAX_PDF = 10 * 1024 * 1024
TOKENS = {}
HOST = os.getenv("ATLAS_AULAS_HOST", "127.0.0.1")
PORT = int(os.getenv("ATLAS_AULAS_PUERTO", "8770"))


def conexion():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE, rol TEXT NOT NULL CHECK(rol IN ('docente','alumno')),
        sal BLOB NOT NULL, clave BLOB NOT NULL
    );
    CREATE TABLE IF NOT EXISTS aulas (
        id INTEGER PRIMARY KEY, docente_id INTEGER NOT NULL REFERENCES usuarios(id),
        nombre TEXT NOT NULL, materia TEXT NOT NULL,
        codigo TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS inscripciones (
        aula_id INTEGER REFERENCES aulas(id), alumno_id INTEGER REFERENCES usuarios(id),
        PRIMARY KEY(aula_id,alumno_id)
    );
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY, aula_id INTEGER NOT NULL REFERENCES aulas(id),
        nombre TEXT NOT NULL, paginas INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS documentos_archivos (documento_id INTEGER PRIMARY KEY REFERENCES documentos(id), contenido BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS evaluaciones (id INTEGER PRIMARY KEY, aula_id INTEGER NOT NULL REFERENCES aulas(id), titulo TEXT NOT NULL, documentos_ids TEXT NOT NULL, preguntas TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'borrador' CHECK(estado IN ('borrador','publicada')), creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, publicado_en TEXT);
    CREATE TABLE IF NOT EXISTS entregas_evaluacion (evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id), alumno_id INTEGER NOT NULL REFERENCES usuarios(id), respuestas TEXT NOT NULL, entregado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(evaluacion_id,alumno_id));
    CREATE TABLE IF NOT EXISTS calificaciones (
      evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id),
      alumno_id INTEGER NOT NULL REFERENCES usuarios(id),
      nota REAL NOT NULL CHECK(nota >= 0 AND nota <= 10),
      comentario TEXT NOT NULL DEFAULT '',
      corregido_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY(evaluacion_id,alumno_id)
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS fragmentos USING fts5(
        documento_id UNINDEXED, aula_id UNINDEXED, pagina UNINDEXED, texto,
        tokenize='unicode61 remove_diacritics 2'
    );
    """)
    columnas={c["name"] for c in db.execute("PRAGMA table_info(aulas)")}
    if "nivel" not in columnas:db.execute("ALTER TABLE aulas ADD COLUMN nivel TEXT NOT NULL DEFAULT 'sin_definir'")
    if "grado" not in columnas:db.execute("ALTER TABLE aulas ADD COLUMN grado TEXT NOT NULL DEFAULT ''")
    return db


def hash_clave(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 240000)


def terminos(pregunta):
    comunes = {"que", "como", "cual", "cuales", "por", "para", "sobre", "los", "las", "una", "del", "con", "donde", "segun", "es", "son", "me", "explica", "el", "la", "un", "de", "en"}
    return [p for p in re.findall(r"[^\W_]+", pregunta.casefold()) if len(p) > 2 and p not in comunes][:14]


class ErrorUsuario(Exception):
    def __init__(self, mensaje, estado=400):
        super().__init__(mensaje)
        self.estado = estado


def texto_corto(v, maximo=100):
    if not isinstance(v, str) or not v.strip() or len(v.strip()) > maximo:
        raise ErrorUsuario("Campo obligatorio o demasiado largo")
    return v.strip()


def identidad(handler):
    header = handler.headers.get("Authorization", "")
    token = header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else ""
    user_id = TOKENS.get(token)
    if not user_id:
        raise ErrorUsuario("Sesión inválida: ingresá nuevamente", 401)
    with conexion() as db:
        usuario = db.execute("SELECT id,nombre,usuario,rol FROM usuarios WHERE id=?", (user_id,)).fetchone()
    if not usuario:
        raise ErrorUsuario("Usuario inexistente", 401)
    return dict(usuario)


def permiso_aula(db, user, aula_id, docente=False):
    aula = db.execute("SELECT * FROM aulas WHERE id=?", (aula_id,)).fetchone()
    if not aula:
        raise ErrorUsuario("Clase no encontrada", 404)
    if docente:
        permitido = user["rol"] == "docente" and aula["docente_id"] == user["id"]
    elif user["rol"] == "docente":
        permitido = aula["docente_id"] == user["id"]
    else:
        permitido = db.execute("SELECT 1 FROM inscripciones WHERE aula_id=? AND alumno_id=?", (aula_id,user["id"])).fetchone() is not None
    if not permitido:
        raise ErrorUsuario("No tenés acceso a esta clase", 403)
    return aula


class Handler(BaseHTTPRequestHandler):
    def responder(self, datos, status=200):
        body = json.dumps(datos, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        # end_headers ya agrega Access-Control-Allow-Origin una sola vez.
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def _origen(self):
        origen = self.headers.get("Origin","")
        # Prototipo con Vite en la misma máquina/red: otros orígenes no obtienen CORS.
        from urllib.parse import urlparse
        u = urlparse(origen)
        host = self.headers.get("Host","").split(":")[0]
        if u.scheme == "http" and u.port == 5173 and u.hostname in (host, "localhost", "127.0.0.1"):
            return origen
        return "null"

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", self._origen())
        super().end_headers()

    def do_GET(self):
        try:
            if self.path == "/api/aulas/health":
                return self.responder({"ok":True})
            user = identidad(self)
            if self.path == "/api/aulas/yo":
                return self.responder({"usuario":user})
            if self.path == "/api/aulas/lista":
                with conexion() as db:
                    if user["rol"] == "docente":
                        filas = db.execute("SELECT id,nombre,materia,codigo,nivel,grado FROM aulas WHERE docente_id=? ORDER BY id DESC",(user["id"],)).fetchall()
                    else:
                        filas = db.execute("""SELECT a.id,a.nombre,a.materia,a.nivel,a.grado FROM aulas a
                          JOIN inscripciones i ON i.aula_id=a.id
                          WHERE i.alumno_id=? ORDER BY a.id DESC""",(user["id"],)).fetchall()
                    aulas = [dict(row) for row in filas]
                    for aula in aulas:
                        aula["documentos"] = [dict(x) for x in db.execute("SELECT d.id,d.nombre,d.paginas,CASE WHEN f.documento_id IS NULL THEN 0 ELSE 1 END AS descargable FROM documentos d LEFT JOIN documentos_archivos f ON f.documento_id=d.id WHERE d.aula_id=?",(aula["id"],))]
                return self.responder({"aulas":aulas})
            if self.path == "/api/aulas/evaluaciones":
                with conexion() as db:
                    if user["rol"] == "docente":
                        filas=db.execute("""SELECT e.id,e.aula_id,e.titulo,e.estado,e.creado_en,e.publicado_en,a.nombre AS aula_nombre,a.materia FROM evaluaciones e JOIN aulas a ON a.id=e.aula_id WHERE a.docente_id=? ORDER BY e.id DESC""",(user["id"],)).fetchall()
                    else:
                        filas=db.execute("""SELECT e.id,e.aula_id,e.titulo,e.estado,e.creado_en,e.publicado_en,a.nombre AS aula_nombre,a.materia,CASE WHEN t.evaluacion_id IS NULL THEN 0 ELSE 1 END AS entregada,c.nota,c.comentario,c.corregido_en FROM evaluaciones e JOIN aulas a ON a.id=e.aula_id JOIN inscripciones i ON i.aula_id=a.id AND i.alumno_id=? LEFT JOIN entregas_evaluacion t ON t.evaluacion_id=e.id AND t.alumno_id=? LEFT JOIN calificaciones c ON c.evaluacion_id=e.id AND c.alumno_id=? WHERE e.estado='publicada' ORDER BY e.id DESC""",(user["id"],user["id"],user["id"])).fetchall()
                return self.responder({"evaluaciones":[dict(x) for x in filas]})
            if self.path == "/api/aulas/seguimiento":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes",403)
                with conexion() as db:
                    registros=db.execute("""SELECT e.id AS evaluacion_id,e.titulo,e.aula_id,a.nombre AS aula_nombre,a.materia,
                      u.id AS alumno_id,u.nombre AS alumno,
                      t.entregado_en,c.nota,c.comentario,c.corregido_en
                      FROM evaluaciones e JOIN aulas a ON a.id=e.aula_id
                      JOIN inscripciones i ON i.aula_id=e.aula_id
                      JOIN usuarios u ON u.id=i.alumno_id
                      LEFT JOIN entregas_evaluacion t ON t.evaluacion_id=e.id AND t.alumno_id=u.id
                      LEFT JOIN calificaciones c ON c.evaluacion_id=e.id AND c.alumno_id=u.id
                      WHERE a.docente_id=? AND e.estado='publicada'
                      ORDER BY a.nombre,e.id,u.nombre""",(user["id"],)).fetchall()
                return self.responder({"seguimiento":[dict(x) for x in registros]})
            raise ErrorUsuario("Ruta inexistente",404)
        except ErrorUsuario as e:
            self.responder({"error":str(e)}, e.estado)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length","0"))
            if n <= 0 or n > MAX_BODY:
                raise ErrorUsuario("Solicitud inválida o demasiado grande",413)
            datos = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(datos,dict):
                raise ErrorUsuario("Formato inválido")
            ruta = self.path
            if ruta == "/api/aulas/registro":
                rol = datos.get("rol")
                if rol not in ("docente","alumno"):
                    raise ErrorUsuario("Rol inválido")
                if rol == "docente":
                    secreto = os.getenv("ATLAS_CLAVE_ALTA_DOCENTE")
                    if not secreto or not hmac.compare_digest(str(datos.get("clave_docente","")),secreto):
                        raise ErrorUsuario("Alta docente no autorizada",403)
                nombre = texto_corto(datos.get("nombre"),80)
                login = texto_corto(datos.get("usuario"),60).lower()
                password = texto_corto(datos.get("clave"),150)
                if len(password) < 10:
                    raise ErrorUsuario("La contraseña debe tener al menos 10 caracteres")
                sal = os.urandom(16)
                with LOCK, conexion() as db:
                    try:
                        db.execute("INSERT INTO usuarios(nombre,usuario,rol,sal,clave) VALUES (?,?,?,?,?)",
                            (nombre,login,rol,sal,hash_clave(password,sal)))
                    except sqlite3.IntegrityError:
                        raise ErrorUsuario("Ese usuario ya existe",409)
                return self.responder({"ok":True},201)
            if ruta == "/api/aulas/login":
                login = texto_corto(datos.get("usuario"),60).lower()
                password = texto_corto(datos.get("clave"),150)
                with conexion() as db:
                    row = db.execute("SELECT * FROM usuarios WHERE usuario=?",(login,)).fetchone()
                if not row or not hmac.compare_digest(row["clave"],hash_clave(password,row["sal"])):
                    raise ErrorUsuario("Credenciales incorrectas",401)
                token = secrets.token_urlsafe(32)
                TOKENS[token] = row["id"]
                return self.responder({"token":token,"usuario":dict(id=row["id"],nombre=row["nombre"],rol=row["rol"])})
            user = identidad(self)
            if ruta == "/api/aulas/salir":
                token = self.headers.get("Authorization","").removeprefix("Bearer ").strip()
                TOKENS.pop(token,None)
                return self.responder({"ok":True})
            if ruta == "/api/aulas/crear":
                if user["rol"] != "docente":
                    raise ErrorUsuario("Solo docentes pueden crear clases",403)
                nombre = texto_corto(datos.get("nombre"),100)
                materia = texto_corto(datos.get("materia"),100)
                nivel=datos.get("nivel","sin_definir")
                grado=datos.get("grado","")
                if nivel not in ("primaria","secundaria"):raise ErrorUsuario("Elegí nivel educativo")
                if not isinstance(grado,str) or not 1<=len(grado.strip())<=40:raise ErrorUsuario("Indicá grado o año")
                with LOCK, conexion() as db:
                    for _ in range(8):
                        codigo = secrets.token_hex(4).upper()
                        try:
                            db.execute("INSERT INTO aulas(docente_id,nombre,materia,codigo,nivel,grado) VALUES (?,?,?,?,?,?)",(user["id"],nombre,materia,codigo,nivel,grado.strip()))
                            break
                        except sqlite3.IntegrityError:
                            continue
                    else: raise ErrorUsuario("No se pudo generar código")
                return self.responder({"ok":True,"codigo":codigo},201)
            if ruta == "/api/aulas/configurar":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden configurar clases",403)
                aula_id=int(datos.get("aula_id",0))
                nivel=datos.get("nivel")
                grado=datos.get("grado","")
                if nivel not in ("primaria","secundaria") or not isinstance(grado,str) or not 1<=len(grado.strip())<=40:raise ErrorUsuario("Indicá nivel y grado/año")
                with LOCK, conexion() as db:
                    permiso_aula(db,user,aula_id,docente=True)
                    db.execute("UPDATE aulas SET nivel=?,grado=? WHERE id=?",(nivel,grado.strip(),aula_id))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/unirse":
                if user["rol"] != "alumno":
                    raise ErrorUsuario("Solo alumnos pueden unirse",403)
                codigo = texto_corto(datos.get("codigo"),20).upper()
                with LOCK, conexion() as db:
                    aula = db.execute("SELECT id FROM aulas WHERE codigo=?",(codigo,)).fetchone()
                    if not aula:
                        raise ErrorUsuario("Código de clase inválido",404)
                    db.execute("INSERT OR IGNORE INTO inscripciones(aula_id,alumno_id) VALUES (?,?)",(aula["id"],user["id"]))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/subir":
                aula_id = int(datos.get("aula_id",0))
                if user["rol"] != "docente":
                    raise ErrorUsuario("Solo docentes pueden subir documentos",403)
                nombre = texto_corto(datos.get("nombre"),140)
                if not nombre.lower().endswith(".pdf"):
                    raise ErrorUsuario("Solo se aceptan PDF")
                encoded = datos.get("base64","")
                if not isinstance(encoded,str) or len(encoded) > MAX_PDF*4//3+20:
                    raise ErrorUsuario("PDF demasiado grande",413)
                contenido = base64.b64decode(encoded,validate=True)
                if len(contenido)>MAX_PDF or not contenido.startswith(b"%PDF-"):
                    raise ErrorUsuario("PDF inválido o mayor a 10 MB")
                with conexion() as db: permiso_aula(db,user,aula_id,docente=True)
                reader = PdfReader(io.BytesIO(contenido))
                if len(reader.pages)>500:
                    raise ErrorUsuario("Máximo 500 páginas")
                fragmentos = [(pagina,bloque) for pagina,hoja in enumerate(reader.pages,1)
                         for bloque in fragmentar_estructurado(hoja.extract_text() or "")]
                if not fragmentos:
                    raise ErrorUsuario("No hay texto extraíble en este PDF")
                with LOCK, conexion() as db:
                    permiso_aula(db,user,aula_id,docente=True)
                    doc_id = db.execute("INSERT INTO documentos(aula_id,nombre,paginas) VALUES (?,?,?)",(aula_id,nombre,len(reader.pages))).lastrowid
                    db.execute("INSERT INTO documentos_archivos(documento_id,contenido) VALUES (?,?)",(doc_id,contenido))
                    db.executemany("INSERT INTO fragmentos(documento_id,aula_id,pagina,texto) VALUES (?,?,?,?)",
                            ((doc_id,aula_id,p,t) for p,t in fragmentos))
                return self.responder({"ok":True,"fragmentos":len(fragmentos)},201)
            if ruta == "/api/aulas/documento/eliminar":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden eliminar PDF",403)
                documento_id=int(datos.get("documento_id",0))
                with LOCK, conexion() as db:
                    doc=db.execute("SELECT id,aula_id FROM documentos WHERE id=?",(documento_id,)).fetchone()
                    if not doc:raise ErrorUsuario("PDF inexistente",404)
                    permiso_aula(db,user,doc["aula_id"],docente=True)
                    evaluaciones=db.execute("SELECT id,titulo,documentos_ids FROM evaluaciones WHERE aula_id=?",(doc["aula_id"],)).fetchall()
                    dependencias=[e["titulo"] for e in evaluaciones if documento_id in json.loads(e["documentos_ids"])]
                    if dependencias:
                        raise ErrorUsuario("No se puede eliminar: este PDF está asociado a evaluaciones ("+", ".join(dependencias[:4])+"). Conservá el historial o eliminá primero los borradores que correspondan.",409)
                    db.execute("DELETE FROM fragmentos WHERE CAST(documento_id AS INTEGER)=? AND CAST(aula_id AS INTEGER)=?",(documento_id,doc["aula_id"]))
                    db.execute("DELETE FROM documentos_archivos WHERE documento_id=?",(documento_id,))
                    db.execute("DELETE FROM documentos WHERE id=?",(documento_id,))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/evaluaciones/eliminar-borrador":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden eliminar borradores",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                with LOCK, conexion() as db:
                    e=db.execute("SELECT aula_id,estado FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Borrador inexistente",404)
                    permiso_aula(db,user,e["aula_id"],docente=True)
                    if e["estado"]!="borrador":raise ErrorUsuario("No se pueden borrar evaluaciones publicadas con historial académico",409)
                    db.execute("DELETE FROM evaluaciones WHERE id=?",(evaluacion_id,))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/evaluaciones/pdf":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden descargar esta copia",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                with conexion() as db:
                    eva=db.execute("SELECT e.aula_id,e.titulo,e.preguntas,a.nombre AS curso,a.materia FROM evaluaciones e JOIN aulas a ON a.id=e.aula_id WHERE e.id=?",(evaluacion_id,)).fetchone()
                    if not eva:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,eva["aula_id"],docente=True)
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import A4
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.pdfbase.ttfonts import TTFont
                except ImportError:
                    raise ErrorUsuario("Falta instalar reportlab: pip install reportlab",503)
                # Unicode completo para español en una fuente TrueType del sistema.
                fuentes=[Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                         Path("C:/Windows/Fonts/arial.ttf")]
                fuente=next((f for f in fuentes if f.is_file()),None)
                if not fuente:raise ErrorUsuario("No se encontró una fuente compatible para crear el PDF",503)
                if "AtlasPDF" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("AtlasPDF",str(fuente)))
                salida=io.BytesIO()
                pagina=canvas.Canvas(salida,pagesize=A4)
                ancho,alto=A4
                y=alto-55
                def linea(texto,tamano=11,espacio=18):
                    nonlocal y
                    if y<70:
                        pagina.showPage();y=alto-55
                    pagina.setFont("AtlasPDF",tamano);pagina.drawString(48,y,texto);y-=espacio
                def envolver(cadena,maxancho=ancho-96):
                    palabras=str(cadena).split()
                    trozos=[];actual=""
                    for palabra in palabras:
                        nuevo=(actual+" "+palabra).strip()
                        if stringWidth(nuevo,"AtlasPDF",11)>maxancho and actual:
                            trozos.append(actual);actual=palabra
                        else:actual=nuevo
                    if actual:trozos.append(actual)
                    return trozos
                for texto,tam in [("Materia: "+eva["materia"]+"   |   Curso: "+eva["curso"],11),(eva["titulo"],16)]:
                    for fragmento in envolver(texto):linea(fragmento,tam,26)
                y-=12
                for i,pregunta in enumerate(json.loads(eva["preguntas"]),1):
                    for fragmento in envolver(str(i)+". "+pregunta):linea(fragmento)
                    y-=12
                pagina.save()
                return self.responder({"nombre":eva["titulo"]+".pdf","base64":base64.b64encode(salida.getvalue()).decode("ascii")})
            if ruta == "/api/aulas/documento":
                documento_id=int(datos.get("documento_id",0))
                with conexion() as db:
                    doc=db.execute("SELECT id,aula_id,nombre FROM documentos WHERE id=?",(documento_id,)).fetchone()
                    if not doc:raise ErrorUsuario("Documento inexistente",404)
                    permiso_aula(db,user,doc["aula_id"])
                    archivo=db.execute("SELECT contenido FROM documentos_archivos WHERE documento_id=?",(documento_id,)).fetchone()
                    if not archivo:raise ErrorUsuario("El PDF original no está guardado. Pedile al docente que lo vuelva a subir.",404)
                    return self.responder({"nombre":doc["nombre"],"base64":base64.b64encode(archivo["contenido"]).decode("ascii")})
            if ruta == "/api/aulas/practicar/revisar":
                if user["rol"]!="alumno":raise ErrorUsuario("Solo alumnos pueden revisar simulacros",403)
                aula_id=int(datos.get("aula_id",0))
                ids=datos.get("documentos_ids")
                preguntas=datos.get("preguntas")
                respuestas=datos.get("respuestas")
                if not isinstance(ids,list) or not ids or any(type(i) is not int for i in ids):
                    raise ErrorUsuario("Materiales inválidos")
                if not isinstance(preguntas,list) or not isinstance(respuestas,list) or not 1<=len(preguntas)<=15 or len(preguntas)!=len(respuestas) or any(not isinstance(x,str) or len(x)>1000 for x in preguntas+respuestas):
                    raise ErrorUsuario("Simulacro inválido")
                with conexion() as db:
                    permiso_aula(db,user,aula_id)
                    disponibles={r[0] for r in db.execute("SELECT id FROM documentos WHERE aula_id=?",(aula_id,))}
                    if not set(ids).issubset(disponibles):raise ErrorUsuario("Material fuera de clase",403)
                    from services.recuperacion_aulas import recuperar
                    fuentes=recuperar(db,aula_id,"definiciones conceptos ejercicios formulas contenidos",limite=8,documentos_ids=ids)
                if not fuentes:raise ErrorUsuario("No se encontró material para revisar")
                import urllib.request
                contexto="\\n".join(f["texto"][:800] for f in fuentes)
                pares="\\n".join(f"{i+1}. P: {p}\\nAlumno: {r}" for i,(p,r) in enumerate(zip(preguntas,respuestas)))
                solicitud={"model":os.getenv("ATLAS_MODELO_CHAT","llama3.2:3b"),"stream":False,
                    "options":{"temperature":0.1,"num_predict":650},
                    "messages":[{"role":"system","content":"Sos un tutor educativo. Compará respuestas con material de clase. No inventes ni afirmes certeza donde el texto no alcanza. Explicá brevemente qué repasar para cada respuesta. La devolución es orientativa, no una calificación oficial."},
                                {"role":"user","content":"FUENTES:\\n"+contexto+"\\nPREGUNTAS Y RESPUESTAS:\\n"+pares}]}
                req=urllib.request.Request(os.getenv("ATLAS_OLLAMA_URL","http://127.0.0.1:11434/api/chat"),json.dumps(solicitud).encode(),{"Content-Type":"application/json"})
                try:
                    with urllib.request.urlopen(req,timeout=120) as out:resultado=json.load(out)
                    devolucion=resultado.get("message",{}).get("content","").strip()
                except Exception:raise ErrorUsuario("No fue posible generar la devolución con Ollama",503)
                if not devolucion:raise ErrorUsuario("Ollama no devolvió una corrección",503)
                return self.responder({"devolucion":devolucion})
            if ruta == "/api/aulas/practicar/generar":
                if user["rol"]!="alumno":raise ErrorUsuario("Solo alumnos pueden crear simulacros personales",403)
                aula_id=int(datos.get("aula_id",0))
                ids=datos.get("documentos_ids")
                cantidad=datos.get("cantidad",5)
                dificultad=datos.get("dificultad","media")
                formato=datos.get("formato","mixto")
                if type(cantidad) is not int or cantidad not in (5,10,15):
                    raise ErrorUsuario("Elegí 5, 10 o 15 preguntas")
                if dificultad not in ("basica","media","avanzada") or formato not in ("mixto","multiple","desarrollo"):
                    raise ErrorUsuario("Configuración inválida")
                if not isinstance(ids,list) or not ids or len(ids)>100 or any(type(i) is not int or i<=0 for i in ids):
                    raise ErrorUsuario("Seleccioná documentos válidos")
                ids=list(dict.fromkeys(ids))
                with conexion() as db:
                    permiso_aula(db,user,aula_id)
                    disponibles={x[0] for x in db.execute("SELECT id FROM documentos WHERE aula_id=?",(aula_id,))}
                    if not set(ids).issubset(disponibles):raise ErrorUsuario("Documento fuera de tu clase",403)
                    from services.recuperacion_aulas import recuperar
                    fuentes=recuperar(db,aula_id,"conceptos definiciones ejemplos ejercicios teoría contenidos",limite=10,documentos_ids=ids)
                if not fuentes:raise ErrorUsuario("No se encontraron fragmentos para generar preguntas")
                from services.generador_evaluaciones_aulas import generar_preguntas
                try:preguntas=generar_preguntas(fuentes,cantidad,dificultad,formato)
                except ValueError as exc:raise ErrorUsuario(str(exc),503)
                return self.responder({"preguntas":preguntas})
            if ruta == "/api/aulas/evaluaciones/generar":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden generar evaluaciones",403)
                aula_id=int(datos.get("aula_id",0))
                ids=datos.get("documentos_ids")
                cantidad=datos.get("cantidad",5)
                dificultad=datos.get("dificultad","media")
                formato=datos.get("formato","mixto")
                if type(cantidad) is not int or not 1<=cantidad<=15:
                    raise ErrorUsuario("Seleccioná entre 1 y 10 preguntas por generación")
                if dificultad not in ("basica","media","avanzada") or formato not in ("mixto","multiple","desarrollo"):
                    raise ErrorUsuario("Configuración de evaluación inválida")
                if not isinstance(ids,list) or not ids or len(ids)>100 or any(type(i) is not int or i<=0 for i in ids):
                    raise ErrorUsuario("Seleccioná documentos válidos")
                ids=list(dict.fromkeys(ids))
                with conexion() as db:
                    permiso_aula(db,user,aula_id,docente=True)
                    existentes={x[0] for x in db.execute("SELECT id FROM documentos WHERE aula_id=?",(aula_id,))}
                    if not set(ids).issubset(existentes):raise ErrorUsuario("Documento fuera de la clase",403)
                    from services.recuperacion_aulas import recuperar
                    fuentes=recuperar(db,aula_id,"conceptos definiciones ejercicios ejemplos teoria informacion contenidos",limite=10,documentos_ids=ids)
                    if not fuentes:
                        fuentes=[dict(x) for x in db.execute(
                            "SELECT d.id AS documento_id,d.nombre,f.pagina,f.texto FROM fragmentos f JOIN documentos d ON d.id=CAST(f.documento_id AS INTEGER) WHERE f.aula_id=? AND d.id IN ("+
                            ",".join("?" for _ in ids)+") AND length(f.texto)>100 ORDER BY f.pagina LIMIT 10",
                            (aula_id,*ids))]
                if not fuentes:raise ErrorUsuario("Los PDF elegidos no contienen texto suficiente")
                from services.generador_evaluaciones_aulas import generar_preguntas
                try:preguntas=generar_preguntas(fuentes,cantidad,dificultad,formato)
                except ValueError as exc:raise ErrorUsuario(str(exc),503)
                return self.responder({"preguntas":preguntas,"fuentes":[{"documento_id":f["documento_id"],"nombre":f["nombre"],"pagina":f["pagina"]} for f in fuentes]})
            if ruta == "/api/aulas/evaluaciones/crear":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden crear evaluaciones",403)
                aula_id=int(datos.get("aula_id",0))
                titulo=texto_corto(datos.get("titulo"),120)
                ids=datos.get("documentos_ids")
                preguntas=datos.get("preguntas")
                if not isinstance(ids,list) or not ids or len(ids)>100 or any(type(x) is not int or x<=0 for x in ids):
                    raise ErrorUsuario("Seleccioná documentos válidos")
                ids=list(dict.fromkeys(ids))
                if not isinstance(preguntas,list) or not 1<=len(preguntas)<=30 or any(not isinstance(q,str) or not 8<=len(q.strip())<=500 for q in preguntas):
                    raise ErrorUsuario("Agregá preguntas válidas para revisar")
                with LOCK, conexion() as db:
                    permiso_aula(db,user,aula_id,docente=True)
                    existentes={x[0] for x in db.execute("SELECT id FROM documentos WHERE aula_id=?",(aula_id,))}
                    if not set(ids).issubset(existentes):raise ErrorUsuario("Documento fuera de la clase",403)
                    nuevo=db.execute("INSERT INTO evaluaciones(aula_id,titulo,documentos_ids,preguntas) VALUES (?,?,?,?)",(aula_id,titulo,json.dumps(ids),json.dumps([p.strip() for p in preguntas],ensure_ascii=False))).lastrowid
                return self.responder({"id":nuevo,"estado":"borrador"},201)
            if ruta == "/api/aulas/evaluaciones/publicar":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes pueden publicar",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                with LOCK, conexion() as db:
                    e=db.execute("SELECT aula_id,estado FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,e["aula_id"],docente=True)
                    if e["estado"]!="borrador":raise ErrorUsuario("Ya publicada")
                    db.execute("UPDATE evaluaciones SET estado='publicada',publicado_en=CURRENT_TIMESTAMP WHERE id=?",(evaluacion_id,))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/evaluaciones/ver":
                evaluacion_id=int(datos.get("evaluacion_id",0))
                with conexion() as db:
                    e=db.execute("SELECT * FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,e["aula_id"])
                    if user["rol"]=="alumno" and e["estado"]!="publicada":raise ErrorUsuario("No publicada",403)
                    resultado={"id":e["id"],"titulo":e["titulo"],"preguntas":json.loads(e["preguntas"]),"estado":e["estado"]}
                    if user["rol"]=="alumno":
                        entrega=db.execute("SELECT respuestas,entregado_en FROM entregas_evaluacion WHERE evaluacion_id=? AND alumno_id=?",(evaluacion_id,user["id"])).fetchone()
                        resultado["entregada"]=bool(entrega)
                        if entrega:
                            resultado["respuestas"]=json.loads(entrega["respuestas"])
                            resultado["entregado_en"]=entrega["entregado_en"]
                            calificacion=db.execute("SELECT nota,comentario,corregido_en FROM calificaciones WHERE evaluacion_id=? AND alumno_id=?",(evaluacion_id,user["id"])).fetchone()
                            resultado["calificacion"]=dict(calificacion) if calificacion else None
                    return self.responder({"evaluacion":resultado})
            if ruta == "/api/aulas/evaluaciones/corregir":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                alumno_id=int(datos.get("alumno_id",0))
                nota=datos.get("nota")
                if type(nota) not in (int,float) or not 0<=nota<=10:
                    raise ErrorUsuario("La nota debe ser numérica, entre 0 y 10")
                comentario=datos.get("comentario","")
                if not isinstance(comentario,str) or len(comentario)>3000:
                    raise ErrorUsuario("Comentario demasiado largo")
                with LOCK, conexion() as db:
                    e=db.execute("SELECT aula_id FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,e["aula_id"],docente=True)
                    entrega=db.execute("SELECT 1 FROM entregas_evaluacion WHERE evaluacion_id=? AND alumno_id=?",(evaluacion_id,alumno_id)).fetchone()
                    if not entrega:raise ErrorUsuario("El alumno no entregó esta evaluación",409)
                    db.execute("""INSERT INTO calificaciones(evaluacion_id,alumno_id,nota,comentario)
                    VALUES (?,?,?,?)
                    ON CONFLICT(evaluacion_id,alumno_id) DO UPDATE SET
                    nota=excluded.nota,comentario=excluded.comentario,corregido_en=CURRENT_TIMESTAMP""",
                    (evaluacion_id,alumno_id,nota,comentario.strip()))
                return self.responder({"ok":True})
            if ruta == "/api/aulas/evaluaciones/respuestas":
                if user["rol"]!="docente":raise ErrorUsuario("Solo docentes",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                alumno_id=int(datos.get("alumno_id",0))
                with conexion() as db:
                    e=db.execute("SELECT aula_id,preguntas FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,e["aula_id"],docente=True)
                    entrega=db.execute("SELECT respuestas FROM entregas_evaluacion WHERE evaluacion_id=? AND alumno_id=?",(evaluacion_id,alumno_id)).fetchone()
                    if not entrega:raise ErrorUsuario("Entrega inexistente",404)
                return self.responder({"preguntas":json.loads(e["preguntas"]),"respuestas":json.loads(entrega["respuestas"])})
            if ruta == "/api/aulas/evaluaciones/entregar":
                if user["rol"]!="alumno":raise ErrorUsuario("Solo estudiantes pueden entregar",403)
                evaluacion_id=int(datos.get("evaluacion_id",0))
                respuestas=datos.get("respuestas")
                with LOCK, conexion() as db:
                    e=db.execute("SELECT * FROM evaluaciones WHERE id=?",(evaluacion_id,)).fetchone()
                    if not e:raise ErrorUsuario("Evaluación inexistente",404)
                    permiso_aula(db,user,e["aula_id"])
                    if e["estado"]!="publicada":raise ErrorUsuario("No publicada",403)
                    if not isinstance(respuestas,list) or len(respuestas)!=len(json.loads(e["preguntas"])) or any(not isinstance(x,str) or len(x)>3000 for x in respuestas):raise ErrorUsuario("Respuestas inválidas")
                    try:db.execute("INSERT INTO entregas_evaluacion(evaluacion_id,alumno_id,respuestas) VALUES (?,?,?)",(evaluacion_id,user["id"],json.dumps(respuestas,ensure_ascii=False)))
                    except sqlite3.IntegrityError:raise ErrorUsuario("Ya entregada",409)
                return self.responder({"ok":True},201)
            if ruta == "/api/aulas/consultar":
                aula_id = int(datos.get("aula_id",0))
                pregunta = texto_corto(datos.get("pregunta"),400)
                ids_solicitados = datos.get("documentos_ids")
                if ids_solicitados is not None:
                    if (not isinstance(ids_solicitados,list) or not ids_solicitados
                        or len(ids_solicitados)>100 or any(type(x) is not int or x<=0 for x in ids_solicitados)):
                        raise ErrorUsuario("Seleccioná uno o más documentos válidos")
                    ids_solicitados = list(dict.fromkeys(ids_solicitados))
                tokens = terminos(pregunta)
                if not tokens:
                    raise ErrorUsuario("Escribí una pregunta más específica")
                expresion = " OR ".join('"'+t+'"' for t in tokens)
                inicio_recuperacion = time.perf_counter()
                with conexion() as db:
                    aula = permiso_aula(db,user,aula_id)
                    # Consulta primero los fragmentos efectivamente asociados al aula.
                    # Esto permite distinguir índice vacío, coincidencias y errores.
                    total = db.execute(
                        "SELECT COUNT(*) FROM fragmentos WHERE aula_id=?",
                        (aula_id,)
                    ).fetchone()[0]
                    if not total:
                        return self.responder({
                            "resultados": [],
                            "estado": "SIN_INDICE",
                            "detalle": "Hay documentos publicados, pero no hay fragmentos indexados para esta clase. Es necesario reconstruir el índice."
                        })
                    if ids_solicitados is not None:
                        disponibles = {r[0] for r in db.execute(
                            "SELECT id FROM documentos WHERE aula_id=?", (aula_id,))}
                        if not set(ids_solicitados).issubset(disponibles):
                            raise ErrorUsuario("Algún documento no pertenece a la clase",403)
                    from services.recuperacion_aulas import recuperar
                    filas = recuperar(db, aula_id, pregunta, limite=5, documentos_ids=ids_solicitados)
                segundos_recuperacion = round(time.perf_counter() - inicio_recuperacion, 3)
                from services.generador_rag_aulas import responder_con_documentos
                # La autorización se verificó antes de recuperar el contexto.
                generado = responder_con_documentos(pregunta, filas, materia=aula["materia"])
                return self.responder({
                    "resultados": filas,
                    "estado": "OK" if filas else "SIN_COINCIDENCIAS",
                    "fragmentos_disponibles": total,
                    "segundos_recuperacion": segundos_recuperacion,
                    **generado,
                })

            raise ErrorUsuario("Ruta inexistente",404)
        except ErrorUsuario as e:
            self.responder({"error":str(e)},e.estado)
        except (ValueError,TypeError,json.JSONDecodeError,UnicodeError,base64.binascii.Error):
            self.responder({"error":"Datos de solicitud inválidos"},400)
        except Exception as e:
            print("Error interno aulas:",repr(e))
            self.responder({"error":"Error interno"},500)


if __name__ == "__main__":
    print(f"Atlas Aulas · prototipo local en http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT),Handler).serve_forever()
