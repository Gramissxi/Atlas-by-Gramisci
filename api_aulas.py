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
    CREATE VIRTUAL TABLE IF NOT EXISTS fragmentos USING fts5(
        documento_id UNINDEXED, aula_id UNINDEXED, pagina UNINDEXED, texto,
        tokenize='unicode61 remove_diacritics 2'
    );
    """)
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
                        filas = db.execute("SELECT id,nombre,materia,codigo FROM aulas WHERE docente_id=? ORDER BY id DESC",(user["id"],)).fetchall()
                    else:
                        filas = db.execute("""SELECT a.id,a.nombre,a.materia FROM aulas a
                          JOIN inscripciones i ON i.aula_id=a.id
                          WHERE i.alumno_id=? ORDER BY a.id DESC""",(user["id"],)).fetchall()
                    aulas = [dict(row) for row in filas]
                    for aula in aulas:
                        aula["documentos"] = [dict(x) for x in db.execute("SELECT id,nombre,paginas FROM documentos WHERE aula_id=?",(aula["id"],))]
                return self.responder({"aulas":aulas})
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
                with LOCK, conexion() as db:
                    for _ in range(8):
                        codigo = secrets.token_hex(4).upper()
                        try:
                            db.execute("INSERT INTO aulas(docente_id,nombre,materia,codigo) VALUES (?,?,?,?)",(user["id"],nombre,materia,codigo))
                            break
                        except sqlite3.IntegrityError:
                            continue
                    else: raise ErrorUsuario("No se pudo generar código")
                return self.responder({"ok":True,"codigo":codigo},201)
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
                    db.executemany("INSERT INTO fragmentos(documento_id,aula_id,pagina,texto) VALUES (?,?,?,?)",
                            ((doc_id,aula_id,p,t) for p,t in fragmentos))
                return self.responder({"ok":True,"fragmentos":len(fragmentos)},201)
            if ruta == "/api/aulas/consultar":
                aula_id = int(datos.get("aula_id",0))
                pregunta = texto_corto(datos.get("pregunta"),400)
                tokens = terminos(pregunta)
                if not tokens:
                    raise ErrorUsuario("Escribí una pregunta más específica")
                expresion = " OR ".join('"'+t+'"' for t in tokens)
                with conexion() as db:
                    permiso_aula(db,user,aula_id)
                    # Consulta primero los fragmentos efectivamente asociados al aula.
                    # Esto permite distinguir índice vacío, coincidencias y errores.
                    total = db.execute(
                        "SELECT COUNT(*) FROM fragmentos WHERE aula_id=?",
                        (str(aula_id),)
                    ).fetchone()[0]
                    if not total:
                        return self.responder({
                            "resultados": [],
                            "estado": "SIN_INDICE",
                            "detalle": "Hay documentos publicados, pero no hay fragmentos indexados para esta clase. Es necesario reconstruir el índice."
                        })
                    # Evitar depender de coincidencias exactas de FTS en la primera
                    # versión del prototipo: puntaje lexical local con SQLite.
                    # Solo se buscan fragmentos del aula autorizada.
                    candidatos = db.execute("""SELECT d.nombre, f.pagina, f.texto
                        FROM fragmentos f
                        JOIN documentos d ON d.id=CAST(f.documento_id AS INTEGER)
                        WHERE f.aula_id=? LIMIT 20000""", (str(aula_id),)).fetchall()
                    import unicodedata
                    def normalizar(texto):
                        return "".join(c for c in unicodedata.normalize("NFKD", texto.casefold())
                            if not unicodedata.combining(c))
                    tokens_norm = list(dict.fromkeys(normalizar(t) for t in tokens))
                    ordenados = []
                    for candidato in candidatos:
                        contenido = normalizar(candidato["texto"])
                        presentes = sum(1 for t in tokens_norm if t in contenido)
                        if presentes:
                            ordenados.append((presentes, dict(candidato)))
                    ordenados.sort(key=lambda x: x[0], reverse=True)
                    filas = [r for _, r in ordenados[:5]]
                return self.responder({
                    "resultados": filas,
                    "estado": "OK" if filas else "SIN_COINCIDENCIAS",
                    "fragmentos_disponibles": total
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
