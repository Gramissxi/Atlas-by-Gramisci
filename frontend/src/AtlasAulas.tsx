import { useState, type FormEvent, type ReactNode } from "react";
import { BookOpen, GraduationCap, LogOut, Upload, Users, ClipboardList, ChevronDown, ChevronUp, LayoutDashboard, FolderOpen, Sparkles, ArrowRight, FileText, Menu, X, Clock3, CheckCircle2, PlayCircle } from "lucide-react";
import PausaAtlas from "./PausaAtlas";
import "./atlas-inicio.css";

type Rol = "docente" | "alumno";
type Usuario = { id: number; nombre: string; rol: Rol };
type Documento = { id: number; nombre: string; paginas: number };
type Aula = { id: number; nombre: string; materia: string; codigo?: string; documentos: Documento[] };
type Resultado = { documento_id: number; nombre: string; pagina: number; texto: string };
const API = "/atlas-api";

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
  const [seguimiento,setSeguimiento] = useState<{evaluacion_id:number;titulo:string;aula_id:number;aula_nombre:string;materia:string;alumno_id:number;alumno:string;entregado_en:string|null;nota:number|null;comentario:string|null}[]>([]);
  const [filtroEvaluacion,setFiltroEvaluacion] = useState<number|null>(null);
  const [corregir,setCorregir] = useState<{evaluacion_id:number;alumno_id:number;alumno:string;preguntas:string[];respuestas:string[]}|null>(null);
  const [nota,setNota] = useState("");
  const [comentario,setComentario] = useState("");
  const [evaluaciones,setEvaluaciones] = useState<{id:number;aula_id:number;titulo:string;estado:string;aula_nombre:string;materia:string;entregada?:number;nota?:number|null;comentario?:string|null;corregido_en?:string|null}[]>([]);
  const [tituloEvaluacion,setTituloEvaluacion] = useState("");
  const [preguntasEvaluacion,setPreguntasEvaluacion] = useState([""]);
  const [cantidadGeneracion,setCantidadGeneracion] = useState(5);
  const [dificultadGeneracion,setDificultadGeneracion] = useState("media");
  const [formatoGeneracion,setFormatoGeneracion] = useState("mixto");
  const [avisosVistos,setAvisosVistos] = useState<number[]>([]);
  const [evaluacionAbierta,setEvaluacionAbierta] = useState<{id:number;titulo:string;preguntas:string[]}|null>(null);
  const [respuestasAlumno,setRespuestasAlumno] = useState<string[]>([]);
  const [nombreAula,setNombreAula] = useState("");
  const [materia,setMateria] = useState("");
  const [codigo,setCodigo] = useState("");
  const [seleccion,setSeleccion] = useState<number|null>(null);
  const [archivo,setArchivo] = useState<File|null>(null);
  const [pregunta,setPregunta] = useState("");
  const [menuAbierto,setMenuAbierto] = useState(false);
  const [documentosElegidos,setDocumentosElegidos] = useState<number[]>([]);
  const [fuentesAbiertas,setFuentesAbiertas] = useState<number[]>([]);
  const [vistaDocente,setVistaDocente] = useState<"inicio"|"clases"|"biblioteca"|"evaluaciones"|"seguimiento">("inicio");
  const [resultados,setResultados] = useState<Resultado[]>([]);
  const [respuestaTutor,setRespuestaTutor] = useState("");
  const [modoTutor,setModoTutor] = useState("");
  const [metricasTutor,setMetricasTutor] = useState<{segundos_generacion?:number;tokens_generados?:number;truncada?:boolean}|null>(null);
  const [estado,setEstado] = useState("");
  const [ocupado,setOcupado] = useState(false);
  const [etapa,setEtapa] = useState<"primaria"|"secundaria">("primaria");
  const [pausa,setPausa] = useState(false);
  const [vistaAlumno,setVistaAlumno] = useState<"inicio"|"clases"|"tutor"|"practicar"|"actividades"|"pausa">("inicio");

  async function llamar(path:string, body?:object, autenticacion=token) {
    const respuesta = await fetch(API+path,{
      method:body?"POST":"GET",
      headers:{"Content-Type":"application/json",...(autenticacion?{"Authorization":"Bearer "+autenticacion}:{})},
      ...(body?{body:JSON.stringify(body)}:{})
    });
    const cuerpo=await respuesta.text();
    let datos: { [key:string]: any };
    try { datos=cuerpo?JSON.parse(cuerpo) as { [key:string]: any }:{}; }
    catch {throw new Error("El servidor devolvió una respuesta no válida. Revisá la terminal de api_aulas.py.");}
    if(!respuesta.ok) throw new Error(typeof datos.error==="string"?datos.error:"Error de servidor ("+respuesta.status+"). Revisá api_aulas.py.");
    if(!cuerpo) throw new Error("El servidor no devolvió datos. Revisá api_aulas.py.");
    return datos;
  }
  async function actualizar(t=token) {
    const datos=await llamar("/api/aulas/lista",undefined,t);
    setAulas(datos.aulas);
    const listado=await llamar("/api/aulas/evaluaciones",undefined,t);
    setEvaluaciones(listado.evaluaciones);
    if(usuario?.rol==="docente"){
      const datosSeguimiento=await llamar("/api/aulas/seguimiento",undefined,t);
      setSeguimiento(datosSeguimiento.seguimiento);
    }
    setSeleccion(actual=>datos.aulas.some((a:Aula)=>a.id===actual)?actual:(datos.aulas[0]?.id??null));
  }
  // Se mantiene el acceso en memoria durante esta sesión del navegador.
  async function autenticar(e:FormEvent) {
    e.preventDefault();setOcupado(true);setEstado("");
    try{
      if(modo==="crear"){
        await llamar("/api/aulas/registro",{nombre,usuario:login,clave,rol,clave_docente:claveDocente},"");
        setModo("ingresar");setEstado("Cuenta creada. Ahora podés ingresar.");
      }else{
        const datos=await llamar("/api/aulas/login",{usuario:login,clave},"");
        setToken(datos.token);setUsuario(datos.usuario);
        await actualizar(datos.token);
        if(datos.usuario.rol==="docente"){const seg=await llamar("/api/aulas/seguimiento",undefined,datos.token);setSeguimiento(seg.seguimiento);}
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
  async function preguntar(e:FormEvent){
    e.preventDefault();
    if(seleccion===null)return;
    setOcupado(true);setEstado("");setResultados([]);setFuentesAbiertas([]);setRespuestaTutor("");setModoTutor("");setMetricasTutor(null);
    try{const respuesta=await llamar("/api/aulas/consultar",{aula_id:seleccion,pregunta,documentos_ids:documentosElegidos.length?documentosElegidos:aula?.documentos.map(d=>d.id)});setResultados(respuesta.resultados);setRespuestaTutor(respuesta.respuesta || "");setModoTutor(respuesta.modo || "");setMetricasTutor({segundos_generacion:respuesta.segundos_generacion,tokens_generados:respuesta.tokens_generados,truncada:respuesta.truncada});
      if(!respuesta.resultados.length)setEstado(respuesta.detalle || "No encontré coincidencias. Probá con un término del documento.");
    }catch(e){setEstado(e instanceof Error?e.message:"Error al consultar")}
    finally{setOcupado(false)}
  }
  async function salir() {
    try{await llamar("/api/aulas/salir",{});}catch{/* Cierre local aunque el servidor ya esté desconectado */}
    setUsuario(null);setToken("");setAulas([]);setResultados([]);setRespuestaTutor("");setSeleccion(null);setDocumentosElegidos([]);setEvaluaciones([]);setSeguimiento([]);setAvisosVistos([]);setEvaluacionAbierta(null);setCorregir(null);
  }

  const aula=aulas.find(a=>a.id===seleccion);
  if(!usuario) return <div className="atlas-nuevo atlas-primaria"><main className="atlas-contenido atlas-acceso">
    <section className="atlas-pagina">
      <span className="atlas-sobrelinea"><GraduationCap size={19}/> Atlas · Plataforma educativa</span>
      <h1>{modo==="ingresar"?"Bienvenido a Atlas":"Crear una cuenta"}</h1>
      <p>Entrá a tu espacio para estudiar o enseñar. Esta es una versión de pruebas, no apta todavía para datos reales de menores.</p>
      <div className="atlas-selector-materias">
        <button className={rol==="alumno"?"elegida":""} onClick={()=>setRol("alumno")}>Soy alumno/a</button>
        <button className={rol==="docente"?"elegida":""} onClick={()=>setRol("docente")}>Soy docente</button>
      </div>
      <form className="atlas-caja atlas-formulario" onSubmit={autenticar}>
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

  async function generarConIA(){
    if(!aula || !aula.documentos.length) throw new Error("Elegí una clase con PDF");
    const ids=documentosElegidos.length?documentosElegidos:aula.documentos.map(d=>d.id);
    const data=await llamar("/api/aulas/evaluaciones/generar",{aula_id:aula.id,documentos_ids:ids,cantidad:cantidadGeneracion,dificultad:dificultadGeneracion,formato:formatoGeneracion});
    if(!Array.isArray(data.preguntas)||!data.preguntas.length)throw new Error("La IA no devolvió preguntas válidas");
    setPreguntasEvaluacion(data.preguntas);
  }
  async function crearBorrador() {
    if(!aula)throw new Error("Seleccioná una clase");
    const ids=documentosElegidos.length?documentosElegidos:aula.documentos.map(d=>d.id);
    const preguntas=preguntasEvaluacion.map(p=>p.trim()).filter(Boolean);
    if(!preguntas.length)throw new Error("Agregá una pregunta");
    await llamar("/api/aulas/evaluaciones/crear",{aula_id:aula.id,titulo:tituloEvaluacion,documentos_ids:ids,preguntas});
    setTituloEvaluacion("");setPreguntasEvaluacion([""]);
  }
  async function abrirEvaluacion(id:number) {
    setOcupado(true);setEstado("");
    try {const datos=await llamar("/api/aulas/evaluaciones/ver",{evaluacion_id:id});setEvaluacionAbierta(datos.evaluacion);setRespuestasAlumno(datos.evaluacion.preguntas.map(()=>''));setVistaAlumno("actividades");}
    catch(e){setEstado(e instanceof Error?e.message:"No se pudo abrir la actividad")}
    finally{setOcupado(false)}
  }
  async function abrirCorreccion(evaluacion_id:number,alumno_id:number,alumno:string){
    setOcupado(true);setEstado("");
    try {const datos=await llamar("/api/aulas/evaluaciones/respuestas",{evaluacion_id,alumno_id});setCorregir({evaluacion_id,alumno_id,alumno,preguntas:datos.preguntas,respuestas:datos.respuestas});}
    catch(e){setEstado(e instanceof Error?e.message:"No se pudo recuperar la entrega")}
    finally{setOcupado(false)}
  }
  const pendientes=evaluaciones.filter(e=>!e.entregada);
  const correccionesNuevas=evaluaciones.filter(e=>e.entregada&&e.nota!==null&&e.nota!==undefined&&!avisosVistos.includes(e.id));
  const vista = usuario.rol==="docente"?vistaDocente:vistaAlumno;
  const navegar=(v:string)=>{setMenuAbierto(false); if(usuario.rol==="docente")setVistaDocente(v as typeof vistaDocente);else setVistaAlumno(v as typeof vistaAlumno);setEstado("");};
  const seleccionarAula=(id:number)=>{setSeleccion(id);setDocumentosElegidos([]);setResultados([]);setRespuestaTutor("");};
  const elegirDocumento=(id:number,marcado:boolean)=>{
    if(!aula)return;
    const actuales=documentosElegidos.length?documentosElegidos:aula.documentos.map(d=>d.id);
    const nuevos=marcado?[...new Set([...actuales,id])]:actuales.filter(x=>x!==id);
    if(!nuevos.length)return;
    setDocumentosElegidos(nuevos.length===aula.documentos.length?[]:nuevos);
  };
  const selectorDocumentos=()=>!aula?.documentos.length?<p>Esta clase todavía no tiene documentos.</p>:<div className="atlas-v2-documents">
    <div className="atlas-v2-row-between"><strong>Elegí los materiales</strong><button className="atlas-v2-link" onClick={()=>setDocumentosElegidos([])}>Seleccionar todos</button></div>
    {aula.documentos.map(d=><label key={d.id} className="atlas-v2-doc-option"><input type="checkbox" checked={!documentosElegidos.length||documentosElegidos.includes(d.id)} onChange={e=>elegirDocumento(d.id,e.target.checked)}/><FileText size={18}/><span><strong>{d.nombre}</strong><small>{d.paginas} páginas</small></span></label>)}
    <small>{documentosElegidos.length?documentosElegidos.length+" documentos seleccionados":"Todos los documentos seleccionados"}</small>
  </div>;
  const elegirClase=()=> <div className="atlas-v2-course-select"><label htmlFor="atlas-clase">Materia / clase</label><select id="atlas-clase" value={seleccion??""} onChange={e=>seleccionarAula(Number(e.target.value))}>{aulas.map(a=><option key={a.id} value={a.id}>{a.materia} · {a.nombre}</option>)}</select></div>;
  const tarjeta=(titulo:string,descripcion:string,icono:ReactNode,v:string,tono:string)=> <button className={"atlas-v2-action "+tono} onClick={()=>navegar(v)}>{icono}<strong>{titulo}</strong><span>{descripcion}</span><ArrowRight size={17}/></button>;
  const secciones=usuario.rol==="docente"?[
    ["inicio","Inicio",<LayoutDashboard size={19}/>],["clases","Mis clases",<Users size={19}/>],["biblioteca","Biblioteca",<FolderOpen size={19}/>],["evaluaciones","Evaluaciones",<ClipboardList size={19}/>],["seguimiento","Seguimiento",<CheckCircle2 size={19}/>]
  ]:[["inicio","Inicio",<LayoutDashboard size={19}/>],["clases","Mis materias",<BookOpen size={19}/>],["tutor","Tutor Atlas",<Sparkles size={19}/>],["practicar","Practicar",<ClipboardList size={19}/>],["actividades","Mis actividades",<CheckCircle2 size={19}/>],["pausa","Pausa y desafíos",<PlayCircle size={19}/>]];
  return <div className="atlas-v2">
    <header className="atlas-v2-mobile-header"><button aria-label="Abrir menú" onClick={()=>setMenuAbierto(true)}><Menu/></button><strong>✦ Atlas</strong><span>{usuario.nombre}</span></header>
    <aside className={"atlas-v2-sidebar "+(menuAbierto?"atlas-v2-sidebar-open":"")}>
      <div className="atlas-v2-brand"><span className="atlas-v2-brand-icon"><GraduationCap size={24}/></span><div><strong>Atlas</strong><small>Aprendemos juntos</small></div><button aria-label="Cerrar menú" className="atlas-v2-close" onClick={()=>setMenuAbierto(false)}><X size={20}/></button></div>
      <div className="atlas-v2-sidebar-label">MENÚ PRINCIPAL</div>
      <nav aria-label="Secciones de Atlas">{secciones.map(([id,label,icono])=><button key={id as string} className={vista===id?"activo":""} onClick={()=>navegar(id as string)}>{icono}{label}{usuario.rol==="alumno"&&id==="actividades"&&(pendientes.length+correccionesNuevas.length)>0&&<span className="atlas-v2-count">{(pendientes.length+correccionesNuevas.length)>99?"99+":pendientes.length+correccionesNuevas.length}</span>}</button>)}</nav>
      <div className="atlas-v2-sidebar-bottom"><div className="atlas-v2-user"><span>{usuario.nombre.slice(0,1).toUpperCase()}</span><div><strong>{usuario.nombre}</strong><small>{usuario.rol==="docente"?"Docente":"Estudiante"}</small></div></div><button onClick={()=>void salir()}><LogOut size={18}/> Cerrar sesión</button></div>
    </aside>
    {menuAbierto&&<button className="atlas-v2-scrim" onClick={()=>setMenuAbierto(false)} aria-label="Cerrar menú"/>}
    <main className="atlas-v2-main">
      <div className="atlas-v2-top"><span>Atlas / {usuario.rol==="docente"?"Espacio docente":"Espacio estudiante"} / {String(secciones.find(x=>x[0]===vista)?.[1]??"Inicio")}</span><span className="atlas-v2-status">● Prototipo local</span></div>
      {estado&&<div className="atlas-v2-alert" role="status">{estado}</div>}
      {vista==="inicio"&&<>
        <section className="atlas-v2-hero"><div><small>{usuario.rol==="docente"?"TU ESPACIO DE ENSEÑANZA":"TU ESPACIO PARA APRENDER"}</small><h1>{usuario.rol==="docente"?"¡Hola, "+usuario.nombre+"! 👋":"¡Hola, "+usuario.nombre+"! 👋"}</h1><p>{usuario.rol==="docente"?"Organizá tus clases, compartí materiales y acompañá el aprendizaje.":"¿Qué vamos a aprender hoy? Tus materias y tu tutor te esperan."}</p><button onClick={()=>navegar(usuario.rol==="docente"?"biblioteca":"clases")}>{usuario.rol==="docente"?"Ver biblioteca":"Explorar materias"} <ArrowRight size={18}/></button></div><div className="atlas-v2-hero-art" aria-hidden="true"><span>📚</span><span>✏️</span><span>🌱</span></div></section>
        <div className="atlas-v2-heading"><div><h2>{usuario.rol==="docente"?"Tu panel de trabajo":"¿Qué te gustaría hacer?"}</h2><p>Elegí una opción para continuar</p></div></div>
        <div className="atlas-v2-actions">{usuario.rol==="docente"?<>
          {tarjeta("Mis clases","Creá y administrá cursos",<Users size={27}/>,"clases","atlas-v2-purple")}
          {tarjeta("Biblioteca","Subí documentos de tus materias",<FolderOpen size={27}/>,"biblioteca","atlas-v2-blue")}
          {tarjeta("Evaluaciones","Prepará evaluaciones por PDF",<ClipboardList size={27}/>,"evaluaciones","atlas-v2-peach")}
          {tarjeta("Seguimiento","Espacio de seguimiento futuro",<CheckCircle2 size={27}/>,"seguimiento","atlas-v2-green")}
        </>:<>
          {tarjeta("Mis materias","Clases y materiales disponibles",<BookOpen size={27}/>,"clases","atlas-v2-purple")}
          {tarjeta("Tutor Atlas","Preguntá usando tus apuntes",<Sparkles size={27}/>,"tutor","atlas-v2-blue")}
          {tarjeta("Practicar","Prepará tus simulacros",<ClipboardList size={27}/>,"practicar","atlas-v2-peach")}
          {tarjeta("Pausa y desafíos","Jugá y aprendé a tu ritmo",<PlayCircle size={27}/>,"pausa","atlas-v2-green")}
        </>}</div>
        {usuario.rol==="alumno"&&correccionesNuevas.length>0&&<section className="atlas-v2-card atlas-v2-pendientes"><div className="atlas-v2-row-between"><h2>¡Tenés evaluaciones corregidas!</h2><button className="atlas-v2-link" onClick={()=>{setAvisosVistos(evaluaciones.filter(e=>e.nota!==null&&e.nota!==undefined).map(e=>e.id));navegar("actividades");}}>Ver notas →</button></div>{correccionesNuevas.map(e=><p key={e.id}><strong>{e.titulo}</strong> · Nota: {e.nota}/10</p>)}</section>}
        {usuario.rol==="alumno"&&<section className="atlas-v2-card atlas-v2-pendientes"><div className="atlas-v2-row-between"><h2>Actividades pendientes {pendientes.length>0?"("+pendientes.length+")":""}</h2><button className="atlas-v2-link" onClick={()=>navegar("actividades")}>Ver todas →</button></div>{pendientes.length?pendientes.slice(0,3).map(e=><button className="atlas-v2-task" key={e.id} onClick={()=>void abrirEvaluacion(e.id)}><ClipboardList size={19}/><span><strong>{e.titulo}</strong><small>{e.materia} · {e.aula_nombre}</small></span><ArrowRight size={17}/></button>):<p>No tenés evaluaciones pendientes. ¡Podés practicar por tu cuenta!</p>}</section>}
        <div className="atlas-v2-heading"><h2>{usuario.rol==="docente"?"Clases que administrás":"Mis materias"}</h2><button className="atlas-v2-link" onClick={()=>navegar("clases")}>Ver todas →</button></div>
        <div className="atlas-v2-courses">{aulas.length?aulas.map((a,i)=><button className={"atlas-v2-course "+["atlas-v2-purple","atlas-v2-blue","atlas-v2-green","atlas-v2-peach"][i%4]} key={a.id} onClick={()=>{seleccionarAula(a.id);navegar(usuario.rol==="docente"?"biblioteca":"tutor");}}><BookOpen size={25}/><strong>{a.materia}</strong><span>{a.nombre}</span><small>{a.documentos.length} documentos · Explorar →</small></button>):<div className="atlas-v2-empty">Todavía no hay clases. {usuario.rol==="docente"?"Creá una desde Mis clases.":"Pedile el código a tu docente."}</div>}</div>
      </>}
      {vista==="clases"&&<>
        <div className="atlas-v2-page-title"><small>{usuario.rol==="docente"?"ADMINISTRACIÓN":"MIS MATERIAS"}</small><h1>{usuario.rol==="docente"?"Mis clases":"Mis materias"}</h1><p>{usuario.rol==="docente"?"Creá clases y compartí su código de acceso.":"Unite con un código y explorá tus materias."}</p></div>
        <div className="atlas-v2-two">
          <section className="atlas-v2-card"><h2>{usuario.rol==="docente"?"Crear una clase":"Unirme a una clase"}</h2>
            {usuario.rol==="docente"?<form onSubmit={e=>{e.preventDefault();void ejecutar(()=>llamar("/api/aulas/crear",{nombre:nombreAula,materia}),"Clase creada correctamente.");}}><label>Nombre del curso<input required value={nombreAula} onChange={e=>setNombreAula(e.target.value)} placeholder="Ej.: 6.º B"/></label><label>Materia<input required value={materia} onChange={e=>setMateria(e.target.value)} placeholder="Ej.: Matemática"/></label><button className="atlas-v2-primary" disabled={ocupado}>Crear clase</button></form>:<form onSubmit={e=>{e.preventDefault();void ejecutar(()=>llamar("/api/aulas/unirse",{codigo}),"Te uniste a la clase.");}}><label>Código de invitación<input required maxLength={20} value={codigo} onChange={e=>setCodigo(e.target.value.toUpperCase())} placeholder="A1B2C3D4"/></label><button className="atlas-v2-primary" disabled={ocupado}>Unirme</button></form>}
          </section>
          <section className="atlas-v2-card"><h2>Clases disponibles</h2><div className="atlas-v2-classes">{aulas.map(a=><button key={a.id} onClick={()=>{seleccionarAula(a.id);navegar(usuario.rol==="docente"?"biblioteca":"tutor");}}><BookOpen size={20}/><span><strong>{a.materia}</strong><small>{a.nombre} · {a.documentos.length} PDF{usuario.rol==="docente"?" · Código "+a.codigo:""}</small></span><ArrowRight size={18}/></button>)}</div>{!aulas.length&&<p>Aún no tenés clases.</p>}</section>
        </div>
      </>}
      {vista==="biblioteca"&&usuario.rol==="docente"&&<>
        <div className="atlas-v2-page-title"><small>MATERIALES DEL CURSO</small><h1>Biblioteca</h1><p>Publicá PDF para que tus alumnos puedan consultarlos desde el tutor.</p></div>
        {aulas.length>0&&elegirClase()}
        <div className="atlas-v2-two">
          <section className="atlas-v2-card"><h2>Documentos publicados</h2>{aula?.documentos.length?aula.documentos.map(d=><div className="atlas-v2-file" key={d.id}><FileText size={23}/><span><strong>{d.nombre}</strong><small>{d.paginas} páginas</small></span></div>):<p>Todavía no hay documentos en esta clase.</p>}</section>
          <section className="atlas-v2-card"><h2>Subir un PDF</h2><p>Solo los docentes pueden publicar documentos. Tamaño máximo: 10 MB.</p><input type="file" accept=".pdf,application/pdf" onChange={e=>setArchivo(e.target.files?.[0]||null)}/><button className="atlas-v2-primary" disabled={!archivo||ocupado||!aula} onClick={()=>void ejecutar(subir,"PDF publicado e indexado.")}><Upload size={17}/> Publicar documento</button><p className="atlas-v2-note">Los originales todavía no se almacenan para descarga; esta función está pendiente.</p></section>
        </div>
      </>}
      {vista==="tutor"&&usuario.rol==="alumno"&&<>
        <div className="atlas-v2-page-title"><small>ASISTENTE EDUCATIVO</small><h1><Sparkles size={30}/> Tutor Atlas</h1><p>Preguntá sobre uno, varios o todos los documentos publicados por tu docente.</p></div>
        {aulas.length>0&&elegirClase()}
        <div className="atlas-v2-tutor-grid"><section className="atlas-v2-card"><h2><FolderOpen size={20}/> Materiales para consultar</h2>{selectorDocumentos()}<div className="atlas-v2-note">Los PDF originales no están disponibles para descarga todavía.</div></section>
        <section className="atlas-v2-card atlas-v2-chat"><h2><Sparkles size={21}/> Preguntale a Atlas</h2><div className="atlas-v2-answer">{respuestaTutor?<><strong>Atlas responde</strong><p>{respuestaTutor}</p>{metricasTutor?.truncada&&<small>La respuesta puede estar incompleta.</small>}{typeof metricasTutor?.segundos_generacion==="number"&&<small>IA local · {metricasTutor.segundos_generacion} s · {metricasTutor.tokens_generados??0} tokens</small>}{modoTutor==="ollama_local"&&<small>Verificá la respuesta con sus fuentes.</small>}</>:<><div className="atlas-v2-answer-icon"><Sparkles size={24}/></div><strong>¡Hola! Soy Atlas ✨</strong><p>Podés preguntarme cualquier tema incluido en los materiales de tu clase.</p></>}</div>
          {resultados.length>0&&<div className="atlas-v2-sources"><h3>Fuentes de la respuesta</h3>{resultados.map((r,i)=><article key={i}><button type="button" aria-expanded={fuentesAbiertas.includes(i)} onClick={()=>setFuentesAbiertas(prev=>prev.includes(i)?prev.filter(x=>x!==i):[...prev,i])}><FileText size={16}/><span>{r.nombre} · Pág. {r.pagina}</span>{fuentesAbiertas.includes(i)?<ChevronUp size={17}/>:<ChevronDown size={17}/>}</button>{fuentesAbiertas.includes(i)&&<p>{r.texto}</p>}</article>)}</div>}
          <form className="atlas-v2-question" onSubmit={e=>void preguntar(e)}><input aria-label="Escribí tu pregunta" value={pregunta} onChange={e=>setPregunta(e.target.value)} placeholder="Escribí tu pregunta..." required/><button disabled={ocupado||!pregunta.trim()||!aula?.documentos.length}>{ocupado?"Pensando...":"Preguntar →"}</button></form></section></div>
      </>}
      {(vista==="practicar"&&usuario.rol==="alumno"||vista==="evaluaciones"&&usuario.rol==="docente")&&<>
        <div className="atlas-v2-page-title"><small>{usuario.rol==="alumno"?"APRENDÉ A TU RITMO":"ORGANIZACIÓN DOCENTE"}</small><h1><ClipboardList size={29}/>{usuario.rol==="alumno"?"Mis simulacros":"Crear evaluación"}</h1><p>{usuario.rol==="alumno"?"Elegí los documentos sobre los que querés practicar.":"Prepará una evaluación de un PDF, varios o todos; revisala antes de publicarla."}</p></div>
        {aulas.length>0&&elegirClase()}
        <div className="atlas-v2-two"><section className="atlas-v2-card"><h2>Paso 1 · Elegí los materiales</h2>{selectorDocumentos()}</section>
        <section className="atlas-v2-card"><h2>Paso 2 · Configurá la actividad</h2><label>Cantidad de preguntas<select value={cantidadGeneracion} onChange={e=>setCantidadGeneracion(Number(e.target.value))}><option value={5}>5 preguntas</option><option value={10}>10 preguntas</option></select></label><label>Dificultad<select value={dificultadGeneracion} onChange={e=>setDificultadGeneracion(e.target.value)}><option value="basica">Básica</option><option value="media">Intermedia</option><option value="avanzada">Avanzada</option></select></label><label>Formato<select value={formatoGeneracion} onChange={e=>setFormatoGeneracion(e.target.value)}><option value="mixto">Mixto</option><option value="multiple">Opción múltiple</option><option value="desarrollo">Desarrollo</option></select></label><div className="atlas-v2-info"><Clock3 size={19}/><span>{usuario.rol==="alumno"?"Los simulacros personales tendrán corrección y explicaciones.":"Los borradores requerirán revisión docente antes de publicarse."}</span></div>{usuario.rol==="docente"?<div className="atlas-v2-eval-editor"><h3>Paso 3 · Revisá las preguntas</h3><button className="atlas-v2-primary" disabled={ocupado||!aula?.documentos.length} onClick={()=>void ejecutar(generarConIA,"Atlas propuso preguntas. Revisalas y editalas antes de guardar.")}><Sparkles size={17}/> Generar borrador con IA</button><label>Título de la evaluación<input value={tituloEvaluacion} maxLength={120} onChange={e=>setTituloEvaluacion(e.target.value)} placeholder="Ej.: Evaluación de Teoría de la Información"/></label>{preguntasEvaluacion.map((q,i)=><label key={i}>Pregunta {i+1}<textarea rows={2} value={q} onChange={e=>setPreguntasEvaluacion(prev=>prev.map((v,j)=>j===i?e.target.value:v))} placeholder="Escribí el enunciado que verá el alumno"/></label>)}<button className="atlas-v2-link" disabled={preguntasEvaluacion.length>=30} onClick={()=>setPreguntasEvaluacion(prev=>[...prev,""])}>+ Agregar pregunta</button><button className="atlas-v2-primary" disabled={!tituloEvaluacion.trim()||!aula?.documentos.length||ocupado||!preguntasEvaluacion.some(x=>x.trim().length>=8)} onClick={()=>void ejecutar(crearBorrador,"Borrador guardado. Revisalo abajo antes de publicar.")}>Guardar borrador</button><p className="atlas-v2-note">Las preguntas propuestas por IA son borradores. Revisalas y editalas antes de guardar y publicar.</p></div>:<p className="atlas-v2-note">Los simulacros personales generativos se incorporarán en otra etapa.</p>}</section></div>
      </>}
      {vista==="actividades"&&usuario.rol==="alumno"&&<>
        <div className="atlas-v2-page-title"><small>ACTIVIDADES DEL DOCENTE</small><h1>Mis actividades</h1><p>Las evaluaciones publicadas por tus docentes aparecen aquí.</p></div>
        <div className="atlas-v2-row-between"><p>Las notas y comentarios quedan disponibles después de la corrección docente.</p><button className="atlas-v2-link" onClick={()=>setAvisosVistos(evaluaciones.filter(e=>e.nota!==null&&e.nota!==undefined).map(e=>e.id))}>Marcar avisos como vistos</button></div>
        <section className="atlas-v2-card"><h2>Evaluaciones asignadas</h2>{evaluaciones.length?evaluaciones.map(e=><button key={e.id} className="atlas-v2-task" disabled={!!e.entregada} onClick={()=>void abrirEvaluacion(e.id)}><ClipboardList size={20}/><span><strong>{e.titulo}</strong><small>{e.materia} · {e.aula_nombre} · {e.entregada?(e.nota!==null&&e.nota!==undefined?"Corregida · Nota "+e.nota+"/10":"Entregada · Sin corregir"):"Pendiente"}</small></span>{e.entregada&&e.nota!==null&&e.nota!==undefined&&<span className="atlas-v2-graded">Nota {e.nota}/10{e.comentario&&<small>Devolución: {e.comentario}</small>}</span>}{!e.entregada&&<ArrowRight size={18}/>}</button>):<p>Todavía no hay actividades asignadas.</p>}</section>
        {evaluacionAbierta&&<section className="atlas-v2-card atlas-v2-eval-open"><h2>{evaluacionAbierta.titulo}</h2><p>Respondé y entregá cuando termines. No hay corrección automática en esta versión.</p>{evaluacionAbierta.preguntas.map((q,i)=><label key={i}>{i+1}. {q}<textarea rows={3} value={respuestasAlumno[i]??""} onChange={e=>setRespuestasAlumno(old=>old.map((v,j)=>j===i?e.target.value:v))}/></label>)}<button className="atlas-v2-primary" disabled={ocupado} onClick={()=>void ejecutar(async()=>{await llamar("/api/aulas/evaluaciones/entregar",{evaluacion_id:evaluacionAbierta.id,respuestas:respuestasAlumno});setEvaluacionAbierta(null);},"Evaluación entregada correctamente.")}>Entregar evaluación</button></section>}
      </>}
      {vista==="evaluaciones"&&usuario.rol==="docente"&&<section className="atlas-v2-card atlas-v2-eval-list"><h2>Evaluaciones creadas</h2>{evaluaciones.length?evaluaciones.map(e=><div className="atlas-v2-task" key={e.id}><ClipboardList size={20}/><span><strong>{e.titulo}</strong><small>{e.materia} · {e.aula_nombre} · {e.estado==="publicada"?"Publicada":"Borrador"}</small></span>{e.estado==="borrador"&&<button className="atlas-v2-primary" disabled={ocupado} onClick={()=>void ejecutar(()=>llamar("/api/aulas/evaluaciones/publicar",{evaluacion_id:e.id}),"Evaluación publicada. Ya aparece en Mis actividades del alumnado.")}>Publicar</button>}</div>):<p>Todavía no creaste evaluaciones.</p>}</section>}
      {vista==="seguimiento"&&usuario.rol==="docente"&&<>
        <div className="atlas-v2-page-title"><small>DOCENTES</small><h1>Seguimiento</h1><p>Entregas y notas reales por clase y evaluación.</p></div>
        {aulas.length>0&&elegirClase()}
        <section className="atlas-v2-card"><h2>Evaluaciones publicadas</h2><label>Evaluación<select value={filtroEvaluacion??""} onChange={e=>setFiltroEvaluacion(e.target.value?Number(e.target.value):null)}><option value="">Todas las evaluaciones</option>{evaluaciones.filter(e=>e.aula_id===seleccion&&e.estado==="publicada").map(e=><option key={e.id} value={e.id}>{e.titulo}</option>)}</select></label>
        <div className="atlas-v2-tracking"><div><strong>{seguimiento.filter(r=>r.aula_id===seleccion&&(filtroEvaluacion===null||r.evaluacion_id===filtroEvaluacion)).length}</strong><small>Asignaciones</small></div><div><strong>{seguimiento.filter(r=>r.aula_id===seleccion&&(filtroEvaluacion===null||r.evaluacion_id===filtroEvaluacion)&&r.entregado_en).length}</strong><small>Entregadas</small></div><div><strong>{seguimiento.filter(r=>r.aula_id===seleccion&&(filtroEvaluacion===null||r.evaluacion_id===filtroEvaluacion)&&!r.entregado_en).length}</strong><small>Pendientes</small></div></div>
        {seguimiento.filter(r=>r.aula_id===seleccion&&(filtroEvaluacion===null||r.evaluacion_id===filtroEvaluacion)).map((r,i)=><div className="atlas-v2-task" key={r.evaluacion_id+"-"+r.alumno_id}><Users size={19}/><span><strong>{r.alumno}</strong><small>{r.titulo} · {!r.entregado_en?"Pendiente":r.nota===null?"Entregada · Sin corregir":"Corregida · Nota "+r.nota}</small></span>{r.entregado_en&&<button className="atlas-v2-primary" onClick={()=>{setNota(r.nota===null?"":String(r.nota));setComentario(r.comentario??"");void abrirCorreccion(r.evaluacion_id,r.alumno_id,r.alumno);}}>Revisar</button>}</div>)}
        {!seguimiento.some(r=>r.aula_id===seleccion&&(filtroEvaluacion===null||r.evaluacion_id===filtroEvaluacion))&&<p>Sin asignaciones publicadas o estudiantes inscritos en esta selección.</p>}</section>
        {corregir&&<section className="atlas-v2-card atlas-v2-eval-open"><h2>Corregir · {corregir.alumno}</h2>{corregir.preguntas.map((p,i)=><div key={i}><strong>{i+1}. {p}</strong><p>{corregir.respuestas[i]||"(Sin respuesta)"}</p></div>)}<label>Nota (0 a 10)<input type="number" min="0" max="10" step="0.5" value={nota} onChange={e=>setNota(e.target.value)}/></label><label>Comentario docente<textarea value={comentario} maxLength={1000} rows={3} onChange={e=>setComentario(e.target.value)}/></label><button className="atlas-v2-primary" disabled={ocupado||nota.trim()===""||!Number.isFinite(Number(nota))||Number(nota)<0||Number(nota)>10} onClick={()=>void ejecutar(async()=>{await llamar("/api/aulas/evaluaciones/corregir",{evaluacion_id:corregir.evaluacion_id,alumno_id:corregir.alumno_id,nota:Number(nota),comentario});setCorregir(null);},"Calificación registrada.")}>Guardar nota</button></section>}
      </>}
      {vista==="pausa"&&usuario.rol==="alumno"&&<><div className="atlas-v2-page-title"><small>APRENDER JUGANDO</small><h1>Pausa y desafíos</h1><p>Un momento para practicar con juegos y actividades cortas.</p></div><div className="atlas-v2-card"><button className="atlas-v2-primary" onClick={()=>setPausa(!pausa)}>{pausa?"Cerrar actividades":"Abrir desafíos"}</button>{pausa&&<><div className="atlas-v2-options"><button onClick={()=>setEtapa("primaria")}>Primaria</button><button onClick={()=>setEtapa("secundaria")}>Secundaria</button></div><PausaAtlas etapa={etapa}/></>}</div></>}
      <footer className="atlas-v2-footer">Atlas · Prototipo local · No apto todavía para datos reales de menores · Sin sincronización offline</footer>
    </main>
  </div>;
}
