import { useEffect, useState } from "react";
import { BookOpen, GraduationCap, LogOut, Upload, Users } from "lucide-react";
import PausaAtlas from "./PausaAtlas";
import "./atlas-inicio.css";

type Rol = "docente" | "alumno";
type Usuario = { id: number; nombre: string; rol: Rol };
type Documento = { id: number; nombre: string; paginas: number };
type Aula = { id: number; nombre: string; materia: string; codigo?: string; documentos: Documento[] };
type Resultado = { nombre: string; pagina: number; texto: string };
const API = `http://${window.location.hostname}:8770`;

export default function AtlasAulas() {
  const [modo,setModo] = useState<"ingresar"|"crear">("ingresar");
  const [rol,setRol] = useState<Rol>("alumno");
  const [usuario,setUsuario] = useState<Usuario|null>(null);
  const [token,setToken] = useState("");
  const [nombre,setNombre] = useState("");
  const [login,setLogin] = useState("");
  const [clave,setClave] = useState("");
  const [claveDocente,setClaveDocente] = useState("");
  const [aulas,setAulas] = useState<Aula[]>([]);
  const [nombreAula,setNombreAula] = useState("");
  const [materia,setMateria] = useState("");
  const [codigo,setCodigo] = useState("");
  const [seleccion,setSeleccion] = useState<number|null>(null);
  const [archivo,setArchivo] = useState<File|null>(null);
  const [pregunta,setPregunta] = useState("");
  const [resultados,setResultados] = useState<Resultado[]>([]);
  const [estado,setEstado] = useState("");
  const [ocupado,setOcupado] = useState(false);
  const [etapa,setEtapa] = useState<"primaria"|"secundaria">("primaria");
  const [pausa,setPausa] = useState(false);

  async function llamar(path:string, body?:object, autenticacion=token) {
    const respuesta = await fetch(API+path,{
      method:body?"POST":"GET",
      headers:{"Content-Type":"application/json",...(autenticacion?{"Authorization":"Bearer "+autenticacion}:{})},
      ...(body?{body:JSON.stringify(body)}:{})
    });
    const datos=await respuesta.json();
    if(!respuesta.ok) throw new Error(datos.error || "No se pudo completar la solicitud");
    return datos;
  }
  async function actualizar(t=token) {
    const datos=await llamar("/api/aulas/lista",undefined,t);
    setAulas(datos.aulas);
    setSeleccion(actual=>datos.aulas.some((a:Aula)=>a.id===actual)?actual:(datos.aulas[0]?.id??null));
  }
  // Se mantiene el acceso en memoria durante esta sesión del navegador.
  async function autenticar(e:React.FormEvent) {
    e.preventDefault();setOcupado(true);setEstado("");
    try{
      if(modo==="crear"){
        await llamar("/api/aulas/registro",{nombre,usuario:login,clave,rol,clave_docente:claveDocente},"");
        setModo("ingresar");setEstado("Cuenta creada. Ahora podés ingresar.");
      }else{
        const datos=await llamar("/api/aulas/login",{usuario:login,clave},"");
        setToken(datos.token);setUsuario(datos.usuario);
        await actualizar(datos.token);
      }
    }catch(e){setEstado(e instanceof Error?e.message:"Error de conexión. ¿Está ejecutándose api_aulas.py?")}
    finally{setOcupado(false)}
  }
  async function ejecutar(accion:()=>Promise<unknown>,mensaje:string) {
    setOcupado(true);setEstado("");
    try { await accion();setEstado(mensaje);await actualizar(); }
    catch(e){setEstado(e instanceof Error?e.message:"Error")}
    finally{setOcupado(false)}
  }
  async function subir() {
    if(!archivo || seleccion===null) throw new Error("Elegí clase y PDF");
    if(archivo.size>10*1024*1024)throw new Error("PDF mayor a 10 MB");
    const base64=await new Promise<string>((resolve,reject)=>{
      const fr=new FileReader();fr.onload=()=>resolve(String(fr.result).split(",")[1]||"");
      fr.onerror=()=>reject(new Error("No se pudo leer el PDF"));fr.readAsDataURL(archivo);
    });
    await llamar("/api/aulas/subir",{aula_id:seleccion,nombre:archivo.name,base64});
    setArchivo(null);
  }
  async function preguntar(e:React.FormEvent){
    e.preventDefault();
    if(seleccion===null)return;
    setOcupado(true);setEstado("");setResultados([]);
    try{const respuesta=await llamar("/api/aulas/consultar",{aula_id:seleccion,pregunta});setResultados(respuesta.resultados);
      if(!respuesta.resultados.length)setEstado("No encontré fragmentos con esas palabras en el material de esta clase.");
    }catch(e){setEstado(e instanceof Error?e.message:"Error al consultar")}
    finally{setOcupado(false)}
  }
  async function salir() {
    try{await llamar("/api/aulas/salir",{});}catch{/* Cierre local aunque el servidor ya esté desconectado */}
    setUsuario(null);setToken("");setAulas([]);setResultados([]);setSeleccion(null);
  }

  const aula=aulas.find(a=>a.id===seleccion);
  if(!usuario) return <div className="atlas-nuevo atlas-primaria"><main className="atlas-contenido" style={{maxWidth:660,margin:"auto"}}>
    <section className="atlas-pagina">
      <span className="atlas-sobrelinea"><GraduationCap size={19}/> Atlas · Plataforma educativa</span>
      <h1>{modo==="ingresar"?"Bienvenido a Atlas":"Crear una cuenta"}</h1>
      <p>Entrá a tu espacio para estudiar o enseñar. Esta es una versión de pruebas, no apta todavía para datos reales de menores.</p>
      <div className="atlas-selector-materias">
        <button className={rol==="alumno"?"elegida":""} onClick={()=>setRol("alumno")}>Soy alumno/a</button>
        <button className={rol==="docente"?"elegida":""} onClick={()=>setRol("docente")}>Soy docente</button>
      </div>
      <form className="atlas-caja" onSubmit={autenticar}>
        {modo==="crear"&&<><label htmlFor="nombre">Nombre</label><input id="nombre" required maxLength={80} value={nombre} onChange={e=>setNombre(e.target.value)}/></>}
        <label htmlFor="usuario">Usuario</label>
        <input id="usuario" required value={login} onChange={e=>setLogin(e.target.value)} autoComplete="username"/>
        <label htmlFor="clave">Contraseña</label>
        <input id="clave" type="password" required minLength={modo==="crear"?10:1} value={clave} onChange={e=>setClave(e.target.value)} autoComplete={modo==="crear"?"new-password":"current-password"}/>
        {modo==="crear"&&rol==="docente"&&<><label htmlFor="claveDocente">Clave de habilitación docente</label><input id="claveDocente" type="password" required value={claveDocente} onChange={e=>setClaveDocente(e.target.value)}/></>}
        <button className="atlas-boton" disabled={ocupado} type="submit">{modo==="ingresar"?"Ingresar":"Crear cuenta"}</button>
      </form>
      <button className="atlas-enlace" onClick={()=>{setModo(modo==="ingresar"?"crear":"ingresar");setEstado("");}}>
        {modo==="ingresar"?"¿No tenés cuenta? Registrarte":"¿Ya tenés cuenta? Ingresar"}
      </button>
      <p role="status">{estado}</p>
    </section>
  </main></div>;

  return <div className="atlas-nuevo atlas-primaria">
    <header className="atlas-barra-movil"><strong>✦ Atlas</strong></header>
    <aside className="atlas-lateral">
      <div className="atlas-logo"><GraduationCap/><strong>Atlas</strong></div>
      <nav aria-label="Navegación"><button className="activo"><BookOpen size={18}/>{usuario.rol==="docente"?"Mis clases":"Mis materias"}</button></nav>
      <div className="atlas-lateral-pie"><span>{usuario.nombre} · {usuario.rol}</span><button onClick={()=>void salir()}><LogOut size={17}/> Cerrar sesión</button></div>
    </aside>
    <main className="atlas-contenido">
      <div className="atlas-cabecera"><span className="atlas-etiqueta"><GraduationCap size={16}/> Espacio {usuario.rol}</span><button className="atlas-enlace" onClick={()=>void salir()}>Salir</button></div>
      <section className="atlas-pagina">
        <h1>{usuario.rol==="docente"?"Panel docente":"Mis clases"}</h1>
        <p>{usuario.rol==="docente"?"Creá clases, compartí el código e incorporá documentos. Solo tu cuenta puede publicar materiales en tus clases.":"Ingresá el código que te dio tu docente y consultá los materiales de tu clase."}</p>
        {usuario.rol==="docente" ? <form className="atlas-caja" onSubmit={e=>{e.preventDefault();void ejecutar(()=>llamar("/api/aulas/crear",{nombre:nombreAula,materia}),"Clase creada. Compartí su código con tus estudiantes.");}}>
          <h2>Crear clase</h2><label htmlFor="n-aula">Nombre del curso</label><input id="n-aula" required value={nombreAula} onChange={e=>setNombreAula(e.target.value)} placeholder="Ej.: 5.º A"/>
          <label htmlFor="m-aula">Materia</label><input id="m-aula" required value={materia} onChange={e=>setMateria(e.target.value)} placeholder="Ej.: Ciencias Naturales"/>
          <button className="atlas-boton" disabled={ocupado} type="submit">Crear clase y código</button>
        </form> : <form className="atlas-caja" onSubmit={e=>{e.preventDefault();void ejecutar(()=>llamar("/api/aulas/unirse",{codigo}),"Ya te incorporaste a la clase.");}}>
          <h2><Users size={20}/> Unirme a una clase</h2><label htmlFor="codigo-clase">Código de clase</label>
          <input id="codigo-clase" value={codigo} onChange={e=>setCodigo(e.target.value.toUpperCase())} maxLength={20} required placeholder="Ej.: A1B2C3D4"/>
          <button className="atlas-boton" disabled={ocupado} type="submit">Unirme</button>
        </form>}
        <p role="status">{estado}</p>
        <div className="atlas-caja" style={{marginTop:20}}>
          <h2>{usuario.rol==="docente"?"Clases que administrás":"Clases a las que pertenecés"}</h2>
          {!aulas.length?<p>Todavía no hay clases.</p>:<div className="atlas-selector-materias">{aulas.map(a=><button key={a.id} className={seleccion===a.id?"elegida":""} onClick={()=>{setSeleccion(a.id);setResultados([]);setEstado("");}}>{a.nombre} · {a.materia}</button>)}</div>}
        </div>
        {aula&&<div className="atlas-caja" style={{marginTop:18}}>
          <h2>{aula.nombre} · {aula.materia}</h2>
          {usuario.rol==="docente"&&<p><strong>Código de invitación:</strong> <code>{aula.codigo}</code></p>}
          <h3>Material de la clase</h3>
          {!aula.documentos.length?<p>Todavía no hay documentos publicados.</p>:<ul>{aula.documentos.map(d=><li key={d.id}>{d.nombre} · {d.paginas} páginas</li>)}</ul>}
          {usuario.rol==="docente"&&<div style={{marginTop:18}}>
            <h3><Upload size={18}/> Subir PDF para esta clase</h3><input type="file" accept=".pdf,application/pdf" onChange={e=>setArchivo(e.target.files?.[0]||null)}/>
            <button className="atlas-boton" disabled={!archivo||ocupado} onClick={()=>void ejecutar(subir,"PDF indexado y disponible para esta clase.")}>Publicar documento</button>
          </div>}
          {usuario.rol==="alumno"&&<><h3>Preguntale a Atlas</h3>
            <form onSubmit={e=>void preguntar(e)}><label htmlFor="pregunta-aula">Tu pregunta</label><div className="atlas-pregunta">
              <input id="pregunta-aula" value={pregunta} onChange={e=>setPregunta(e.target.value)} required placeholder="¿Qué significa este concepto?"/>
              <button disabled={!pregunta.trim()||ocupado||!aula.documentos.length} type="submit">Consultar</button>
            </div></form>
            {resultados.length>0&&<div aria-live="polite"><h3>Fragmentos encontrados</h3>{resultados.map((r,i)=><article className="atlas-aviso" style={{marginTop:12}} key={i}><strong>{r.nombre} · página {r.pagina}</strong><p>{r.texto}</p></article>)}</div>}
          </>}
        </div>}
        {usuario.rol==="alumno"&&<div className="atlas-caja" style={{marginTop:18}}>
          <button className="atlas-enlace" onClick={()=>setPausa(!pausa)}>{pausa?"Cerrar desafíos":"Pausa y desafíos"}</button>
          {pausa&&<><div className="atlas-selector-materias"><button onClick={()=>setEtapa("primaria")}>Primaria</button><button onClick={()=>setEtapa("secundaria")}>Secundaria</button></div><PausaAtlas etapa={etapa}/></>}
        </div>}
      </section>
      <footer className="atlas-pie">Atlas · Prototipo local con cuentas y aulas · Sin sincronización offline todavía</footer>
    </main>
  </div>;
}
