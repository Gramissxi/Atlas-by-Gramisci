import { useEffect, useState } from "react";

type Fragmento = { pagina: number; texto: string };
type Paquete = { formato: "atlas-offline-v1"; documento: string; paginas: number; fragmentos: Fragmento[] };

const DB = "atlas-conocimiento-offline";
function guardar(paquete: Paquete): Promise<void> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore("paquetes");
    req.onerror = () => reject(req.error);
    req.onsuccess = () => {
      const db = req.result;
      const tx = db.transaction("paquetes", "readwrite");
      tx.objectStore("paquetes").put(paquete, "actual");
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error); };
    };
  });
}
function cargar(): Promise<Paquete | undefined> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore("paquetes");
    req.onerror = () => reject(req.error);
    req.onsuccess = () => {
      const db = req.result;
      const tx = db.transaction("paquetes", "readonly");
      const query = tx.objectStore("paquetes").get("actual");
      query.onsuccess = () => { resolve(query.result); db.close(); };
      query.onerror = () => { reject(query.error); db.close(); };
    };
  });
}
function normalizar(t: string): string[] {
  const comunes = new Set(["como","cual","cuales","que","los","las","una","uno","del","con","para","por","sobre","explica","este","esta","son","se","en","de","el","la","un"]);
  return (t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").match(/[a-z0-9ñ]+/g) || [])
    .filter(p => p.length > 2 && !comunes.has(p));
}
function buscar(paquete: Paquete, pregunta: string): Fragmento[] {
  const tokens = Array.from(new Set(normalizar(pregunta)));
  if (!tokens.length) return [];
  return paquete.fragmentos.map(f => {
    const palabras = new Set(normalizar(f.texto));
    const coincidencias = tokens.filter(t => palabras.has(t)).length;
    return { f, puntaje: coincidencias / Math.sqrt(Math.max(1,palabras.size)) };
  }).filter(x => x.puntaje > 0).sort((a,b) => b.puntaje - a.puntaje).slice(0,5).map(x => x.f);
}
export default function TutorOfflineAtlas() {
  const [paquete,setPaquete] = useState<Paquete | null>(null);
  const [pregunta,setPregunta] = useState("");
  const [resultados,setResultados] = useState<Fragmento[]>([]);
  const [estado,setEstado] = useState("Todavía no hay un paquete educativo importado en este navegador.");
  useEffect(() => { cargar().then(p => { if (p) { setPaquete(p); setEstado("Paquete guardado localmente y recuperado del dispositivo."); } }).catch(() => setEstado("No se pudo leer el almacenamiento local.")); },[]);
  async function importar(archivo?: File) {
    if (!archivo) return;
    if (archivo.size > 20 * 1024 * 1024) { setEstado("El paquete supera el límite experimental de 20 MB."); return; }
    try {
      const contenido: unknown = JSON.parse(await archivo.text());
      if (!contenido || typeof contenido !== "object") throw Error("Paquete inválido");
      const p = contenido as Partial<Paquete>;
      if (p.formato !== "atlas-offline-v1" || typeof p.documento !== "string" || !Array.isArray(p.fragmentos) || p.fragmentos.length > 20000 || !p.fragmentos.every(f => typeof f.texto === "string" && f.texto.length <= 2000 && Number.isInteger(f.pagina) && f.pagina > 0)) throw Error("Formato de paquete no válido");
      const validado = p as Paquete;
      await guardar(validado);
      setPaquete(validado);setResultados([]);setEstado("Paquete importado y guardado en este navegador.");
    } catch (e) {setEstado("No fue posible importar el paquete: " + (e instanceof Error ? e.message : "error desconocido"));}
  }
  return <section className="atlas-pagina atlas-pagina-chat">
    <span className="atlas-sobrelinea">Consulta de documentos · Modo offline experimental</span>
    <h1>Preguntale al material</h1>
    <p>Importá el paquete preparado por la computadora central. La búsqueda se realiza aquí mismo, sin contactar a Ollama, servidores ni Internet.</p>
    <div className="atlas-caja">
      <label htmlFor="paquete-atlas">Importar paquete educativo (.json)</label>
      <input id="paquete-atlas" type="file" accept=".json,application/json" onChange={e => void importar(e.target.files?.[0])} />
      <p role="status">{estado}</p>
      {paquete && <p><strong>Documento:</strong> {paquete.documento} · {paquete.paginas} páginas · {paquete.fragmentos.length} fragmentos.</p>}
    </div>
    <form onSubmit={e=>{e.preventDefault();setResultados(paquete ? buscar(paquete,pregunta) : []);}}>
      <label htmlFor="pregunta-offline">Pregunta</label>
      <div className="atlas-pregunta">
        <input id="pregunta-offline" value={pregunta} onChange={e=>setPregunta(e.target.value)} placeholder="Ej.: ¿Qué es el ruido térmico?" />
        <button type="submit" disabled={!paquete || !pregunta.trim()}>Buscar</button>
      </div>
    </form>
    {resultados.length>0 ? <div className="atlas-caja" aria-live="polite"><h2>Fragmentos relevantes</h2>{resultados.map((r,i)=><article key={i} style={{marginBottom:16}}><strong>Página {r.pagina}</strong><p>{r.texto}</p></article>)}</div> : paquete && pregunta && <p>Al buscar, aparecerán aquí los fragmentos coincidentes.</p>}
    <div className="atlas-aviso">Esta versión busca coincidencias de palabras y muestra fuentes. No genera respuestas nuevas ni comprende gráficos. Guardar el paquete no garantiza que la aplicación web abra sin red: eso requiere una instalación PWA con caché, que implementaremos y verificaremos por separado. El contenido importado no está autenticado; usá únicamente material de prueba.</div>
  </section>;
}
