import { useState } from "react";
import { ArrowRight, Heart, RefreshCw, Sparkles } from "lucide-react";

type Etapa = "primaria" | "secundaria";
type Animo = "bien" | "cansado" | "frustrado" | "sin-decir";

const mensajes: Record<Animo,string> = {
  bien: "¡Qué bueno! Si querés, probá un desafío cortito.",
  cansado: "Podemos ir despacio. Un descanso también ayuda a aprender.",
  frustrado: "Equivocarse es parte de aprender. Podemos intentar de otra manera.",
  "sin-decir": "No hace falta contar cómo te sentís para participar.",
};

const retos = {
  primaria: [
    { pregunta:"¿Cuánto es 7 + 5?", opciones:["11","12","13"], correcta:1, pista:"Podés partir de 7 y contar cinco más." },
    { pregunta:"¿Cuál de estas palabras es un sustantivo?", opciones:["Árbol","Correr","Rápido"], correcta:0, pista:"Pensá cuál nombra una cosa o ser." },
    { pregunta:"¿Cuántos lados tiene un triángulo?", opciones:["3","4","5"], correcta:0, pista:"Imaginá el dibujo de un triángulo." }
  ],
  secundaria: [
    { pregunta:"Si 3x + 2 = 14, ¿cuánto vale x?", opciones:["3","4","5"], correcta:1, pista:"Primero restá 2 a ambos lados y luego dividí por 3." },
    { pregunta:"¿Cuál es una fuente primaria en Historia?", opciones:["Un diario de época","Un resumen actual","Una novela histórica"], correcta:0, pista:"Buscá un testimonio producido en el período estudiado." },
    { pregunta:"¿Qué orgánulo realiza gran parte de la fotosíntesis?", opciones:["Cloroplasto","Núcleo","Ribosoma"], correcta:0, pista:"Su nombre está relacionado con la clorofila." }
  ],
};

export default function PausaAtlas({etapa}:{etapa:Etapa}) {
  const [animo,setAnimo] = useState<Animo>("sin-decir");
  const [indice,setIndice] = useState(0);
  const [opcion,setOpcion] = useState<number|null>(null);
  const [mostrarPista,setMostrarPista] = useState(false);
  const retosEtapa = retos[etapa];
  const reto = retosEtapa[indice % retosEtapa.length];
  const correcto = opcion === reto.correcta;
  function siguiente() {setIndice(i=>i+1);setOpcion(null);setMostrarPista(false);}
  return <section className="atlas-pagina atlas-bienestar" aria-labelledby="bienestar-titulo">
    <span className="atlas-sobrelinea"><Heart size={16}/> Un ratito para vos</span>
    <h1 id="bienestar-titulo">{etapa==="primaria"?"Aprendé jugando":"Tomate una pausa activa"}</h1>
    <p>{etapa==="primaria"?"Mini desafíos para practicar sin presión.":"Desafíos breves para cambiar de ritmo y volver a estudiar."} Todos se pueden resolver sin Internet.</p>
    <div className="atlas-caja" style={{marginTop:20}}>
      <h2 style={{fontSize:21,margin:"0 0 10px"}}>¿Cómo te sentís hoy? <span style={{fontSize:13,fontWeight:400}}>(opcional)</span></h2>
      <div className="atlas-selector-materias" role="group" aria-label="Elegí cómo te sentís">
        {([{id:"bien",label:"😊 Bien"},{id:"cansado",label:"😴 Con cansancio"},{id:"frustrado",label:"😕 Me cuesta hoy"},{id:"sin-decir",label:"Prefiero no decir"}] as const).map(a=><button key={a.id} aria-pressed={animo===a.id} className={animo===a.id?"elegida":""} onClick={()=>setAnimo(a.id)}>{a.label}</button>)}
      </div>
      <p aria-live="polite">{mensajes[animo]}</p>
      <p style={{fontSize:12,color:"#526c67"}}>Esta elección no se almacena ni se comparte con docentes.</p>
    </div>
    <div className="atlas-caja" style={{marginTop:18}}>
      <span className="atlas-sobrelinea"><Sparkles size={16}/> Minijuego de práctica · Demostración</span>
      <h2 style={{fontSize:23,margin:"12px 0"}}>{reto.pregunta}</h2>
      <div className="atlas-selector-materias" role="group" aria-label="Opciones del desafío">
        {reto.opciones.map((respuesta,i)=><button key={respuesta} className={opcion===i?"elegida":""} aria-pressed={opcion===i} onClick={()=>setOpcion(i)}>{respuesta}</button>)}
      </div>
      {opcion!==null && <p aria-live="polite">{correcto?"¡Bien resuelto! ¿Podés explicar cómo llegaste al resultado?":"Todavía no. Podés revisar la pregunta o pedir una pista."}</p>}
      {mostrarPista && <div className="atlas-aviso">{reto.pista}</div>}
      <div style={{display:"flex",gap:12,flexWrap:"wrap"}}>
        <button className="atlas-enlace" onClick={()=>setMostrarPista(true)}>Ver pista</button>
        <button className="atlas-boton" onClick={siguiente}>Otro desafío <ArrowRight size={16}/></button>
      </div>
    </div>
    <p style={{marginTop:18,fontSize:13,color:"#526c67"}}><RefreshCw size={14} style={{display:"inline",verticalAlign:"middle"}}/> Los desafíos son ejemplos locales; más adelante podrán reemplazarse por actividades aprobadas para cada curso.</p>
  </section>;
}
