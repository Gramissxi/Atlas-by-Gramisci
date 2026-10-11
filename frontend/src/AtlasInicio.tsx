import { useState } from "react";
import { ArrowLeft, ArrowRight, BookOpen, Calculator, CheckCircle2, ClipboardList, FileText, GraduationCap, Leaf, MessageCircle, Settings, Sparkles, Upload, Users, Globe2, Menu, X } from "lucide-react";
import AppAnterior from "./App";
import PausaAtlas from "./PausaAtlas";
import TutorOfflineAtlas from "./TutorOfflineAtlas";
import "./atlas-inicio.css";

type Etapa = "primaria" | "secundaria";
type Pantalla = "inicio" | "materias" | "tutor" | "docente" | "pausa" | "anterior";
const materias = [
  { id: "mat", nombre: "Matemática", tema: "Fracciones y números", icono: Calculator, color: "azul" },
  { id: "nat", nombre: "Ciencias Naturales", tema: "Los seres vivos", icono: Leaf, color: "verde" },
  { id: "len", nombre: "Lengua", tema: "Lectura y escritura", icono: BookOpen, color: "naranja" },
  { id: "soc", nombre: "Ciencias Sociales", tema: "Nuestro entorno", icono: Globe2, color: "celeste" },
];

export default function AtlasInicio() {
  const [etapa, setEtapa] = useState<Etapa>("primaria");
  const [pantalla, setPantalla] = useState<Pantalla>("inicio");
  const [materia, setMateria] = useState("mat");
  const [menuAbierto, setMenuAbierto] = useState(false);
  if (pantalla === "anterior") {
    return <div><button className="atlas-volver" onClick={() => setPantalla("inicio")}><ArrowLeft size={17}/> Volver al nuevo Atlas</button><AppAnterior /></div>;
  }
  const actual = materias.find((m) => m.id === materia)!;
  function navegar(destino: Pantalla) { setPantalla(destino); setMenuAbierto(false); }
  const items = [
    { id: "inicio" as Pantalla, nombre: "Inicio", icono: GraduationCap },
    { id: "materias" as Pantalla, nombre: "Mis materias", icono: BookOpen },
    { id: "tutor" as Pantalla, nombre: "Tutor Atlas", icono: MessageCircle },
    { id: "pausa" as Pantalla, nombre: "Pausa y desafíos", icono: Sparkles },
    { id: "docente" as Pantalla, nombre: "Espacio docente", icono: Users },
  ];
  return <div className={`atlas-nuevo atlas-${etapa}`}>
    <a className="atlas-saltar" href="#contenido">Saltar al contenido</a>
    <header className="atlas-barra-movil"><button aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"} onClick={() => setMenuAbierto(!menuAbierto)}>{menuAbierto ? <X/> : <Menu/>}</button><strong>✦ Atlas</strong></header>
    <aside className={`atlas-lateral ${menuAbierto ? "atlas-abierto" : ""}`}>
      <div className="atlas-logo"><span className="atlas-logo-icono"><GraduationCap size={23}/></span><strong>Atlas</strong></div>
      <nav aria-label="Navegación principal">
        {items.map((item) => <button key={item.id} className={pantalla === item.id ? "activo" : ""} onClick={() => navegar(item.id)} aria-current={pantalla === item.id ? "page" : undefined}><item.icono size={18}/>{item.nombre}</button>)}
      </nav>
      <div className="atlas-lateral-pie"><span>Aprender a tu manera</span><button onClick={() => navegar("anterior")}><Settings size={17}/> Ver versión técnica</button></div>
    </aside>
    <main id="contenido" className="atlas-contenido">
      <div className="atlas-cabecera">
        <span className="atlas-etiqueta"><Sparkles size={15}/> Nueva experiencia Atlas</span>
        <div className="atlas-etapas" role="group" aria-label="Nivel educativo">
          <button className={etapa === "primaria" ? "seleccionado" : ""} aria-pressed={etapa === "primaria"} onClick={() => setEtapa("primaria")}>Primaria</button>
          <button className={etapa === "secundaria" ? "seleccionado" : ""} aria-pressed={etapa === "secundaria"} onClick={() => setEtapa("secundaria")}>Secundaria</button>
        </div>
      </div>
      {pantalla === "inicio" && <>
        <section className="atlas-hero"><div><span className="atlas-sobrelinea">{etapa === "primaria" ? "Tu espacio para descubrir" : "Tu espacio de aprendizaje"}</span><h1>{etapa === "primaria" ? "¡Hola! ¿Qué vamos a aprender hoy? 👋" : "Tu aprendizaje, a tu ritmo."}</h1><p>{etapa === "primaria" ? "Elegí una materia y empecemos a explorar juntos." : "Elegí una materia, repasá contenidos y practicá con el tutor educativo."}</p><button className="atlas-boton" onClick={() => navegar("materias")}>Explorar materias <ArrowRight size={17}/></button></div><div className="atlas-hero-dibujo" aria-hidden="true"><span>📚</span><span>✏️</span><span>🌱</span></div></section>
        <div className="atlas-titulo-seccion"><h2>Mis materias</h2><span>Contenido de demostración</span></div>
        <div className="atlas-tarjetas">{materias.map((m) => <button className={`atlas-materia atlas-${m.color}`} key={m.id} onClick={() => {setMateria(m.id);navegar("materias");}}><m.icono size={29}/><strong>{m.nombre}</strong><small>{m.tema}</small><span>Ver materia <ArrowRight size={14}/></span></button>)}</div>
        <div className="atlas-dos-columnas"><section className="atlas-caja"><div className="atlas-caja-icono"><ClipboardList/></div><h3>Continuá aprendiendo</h3><p>Elegí tu próxima actividad dentro de una materia.</p><button className="atlas-enlace" onClick={() => navegar("materias")}>Ver temas <ArrowRight size={16}/></button></section><section className="atlas-caja"><div className="atlas-caja-icono"><MessageCircle/></div><h3>Tu tutor Atlas</h3><p>Preguntá sobre una materia y estudiá paso a paso.</p><button className="atlas-enlace" onClick={() => navegar("tutor")}>Ir al tutor <ArrowRight size={16}/></button></section></div>
      </>}
      {pantalla === "materias" && <section className="atlas-pagina"><span className="atlas-sobrelinea">Mis materias</span><h1>Aprendé paso a paso</h1><p>Seleccioná una materia. Los temas escolares son ejemplos visuales; todavía no están conectados a cursos reales.</p><div className="atlas-selector-materias">{materias.map(m => <button key={m.id} className={materia === m.id ? "elegida" : ""} onClick={() => setMateria(m.id)}>{m.nombre}</button>)}</div><div className="atlas-leccion"><div className={`atlas-leccion-icono atlas-${actual.color}`}><actual.icono size={32}/></div><div><span className="atlas-sobrelinea">{etapa === "primaria" ? "Nivel primario" : "Nivel secundario"}</span><h2>{actual.nombre}</h2><p>{actual.tema}</p><div className="atlas-aviso">Las rutas se mostrarán cuando el docente cargue y apruebe los materiales.</div><button className="atlas-boton" onClick={() => navegar("tutor")}>Abrir tutor de esta materia <ArrowRight size={16}/></button></div></div></section>}
      {pantalla === "tutor" && <TutorOfflineAtlas/>}
      {pantalla === "pausa" && <PausaAtlas etapa={etapa}/>}
      {pantalla === "docente" && <section className="atlas-pagina"><span className="atlas-sobrelinea">Espacio docente · Vista preliminar</span><h1>Organizá tus clases</h1><p>Un lugar para preparar materiales y actividades que luego estarán disponibles para tus estudiantes.</p><div className="atlas-tarjetas-docente"><article><FileText/><h3>Materiales</h3><p>Subí PDFs y administrá los documentos de cada curso.</p></article><article><Sparkles/><h3>Rutas y actividades</h3><p>Generá propuestas y revisalas antes de publicarlas.</p></article><article><CheckCircle2/><h3>Seguimiento</h3><p>Consultá actividades completadas y temas a reforzar.</p></article></div><button className="atlas-boton" onClick={() => navegar("anterior")}><Upload size={17}/> Abrir herramientas actuales</button></section>}
      <footer className="atlas-pie">Atlas · Proyecto educativo gratuito · Vista preliminar sin datos reales de estudiantes</footer>
    </main>
  </div>;
}
