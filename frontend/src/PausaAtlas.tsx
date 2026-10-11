import { useEffect, useRef, useState } from "react";
import { Brain, Paintbrush, Puzzle, RotateCcw } from "lucide-react";

type Etapa = "primaria" | "secundaria";
type Reto = {pregunta:string; opciones:[string,string,string]; correcta:number; explicacion:string};
type Par = {concepto:string; definicion:string};
type Banco = {preguntas:Reto[]; parejas:Par[]};

const contenidos:Record<string,Banco> = {
  p1:{preguntas:[
    {pregunta:"¿Cuánto es 6 + 3?",opciones:["8","9","10"],correcta:1,explicacion:"6 y 3 más forman 9."},
    {pregunta:"¿Cuál es una vocal?",opciones:["M","A","T"],correcta:1,explicacion:"A es una de las cinco vocales."},
    {pregunta:"¿Cuántos lados tiene un triángulo?",opciones:["3","4","5"],correcta:0,explicacion:"Un triángulo tiene tres lados."}],
    parejas:[{concepto:"Sol",definicion:"Estrella"},{concepto:"Perro",definicion:"Animal"},{concepto:"Rojo",definicion:"Color"}]},
  p2:{preguntas:[
    {pregunta:"¿Cuánto es 8 × 4?",opciones:["32","24","36"],correcta:0,explicacion:"8 + 8 + 8 + 8 = 32."},
    {pregunta:"¿Qué palabra es un sustantivo?",opciones:["Correr","Árbol","Rápido"],correcta:1,explicacion:"Árbol nombra un ser vivo."},
    {pregunta:"¿Qué fracción representa la mitad?",opciones:["1/4","2/3","1/2"],correcta:2,explicacion:"Una parte de dos partes iguales es 1/2."}],
    parejas:[{concepto:"1/2",definicion:"Mitad"},{concepto:"Verbo",definicion:"Acción"},{concepto:"Cuadrado",definicion:"4 lados iguales"}]},
  p3:{preguntas:[
    {pregunta:"¿Cuánto es el 25 % de 100?",opciones:["25","50","75"],correcta:0,explicacion:"25 % significa 25 de cada 100."},
    {pregunta:"¿Cuál de estos es un número primo?",opciones:["9","11","15"],correcta:1,explicacion:"11 solo tiene como divisores a 1 y 11."},
    {pregunta:"¿Cuál es el sujeto en «Los chicos leen»?",opciones:["Leen","Los chicos","Ninguno"],correcta:1,explicacion:"Los chicos indica quién realiza la acción."}],
    parejas:[{concepto:"25 %",definicion:"Un cuarto"},{concepto:"Ecosistema",definicion:"Seres y entorno"},{concepto:"Sujeto",definicion:"Quién realiza la acción"}]},
  s1:{preguntas:[
    {pregunta:"Si 2x + 3 = 11, ¿cuánto vale x?",opciones:["3","4","7"],correcta:1,explicacion:"Restás 3 y dividís entre 2: x = 4."},
    {pregunta:"¿Cuál es una fuente histórica primaria?",opciones:["Carta de época","Manual actual","Novela moderna"],correcta:0,explicacion:"Una carta de época es un testimonio de su tiempo."},
    {pregunta:"¿Qué órgano realiza el intercambio de gases?",opciones:["Estómago","Pulmones","Hígado"],correcta:1,explicacion:"El intercambio de oxígeno y dióxido de carbono ocurre en los pulmones."}],
    parejas:[{concepto:"Incógnita",definicion:"Valor por hallar"},{concepto:"Fuente primaria",definicion:"Testimonio directo"},{concepto:"Célula",definicion:"Unidad de vida"}]},
  s2:{preguntas:[
    {pregunta:"¿Cuánto es la pendiente entre (0,1) y (2,5)?",opciones:["2","4","1"],correcta:0,explicacion:"(5 - 1) / (2 - 0) = 2."},
    {pregunta:"¿Qué representa una aceleración?",opciones:["Cambio de velocidad","Distancia total","Masa"],correcta:0,explicacion:"La aceleración mide el cambio de velocidad por unidad de tiempo."},
    {pregunta:"¿Cuál de estas expresiones es una función lineal?",opciones:["y = 3x + 2","y = x²","y = 1/x"],correcta:0,explicacion:"y = 3x + 2 es afín, de grado uno."}],
    parejas:[{concepto:"Pendiente",definicion:"Cambio de y sobre x"},{concepto:"Aceleración",definicion:"Cambio de velocidad"},{concepto:"Hipótesis",definicion:"Explicación a comprobar"}]},
  s3:{preguntas:[
    {pregunta:"Si f(x) = x², ¿cuánto vale f(3)?",opciones:["6","9","3"],correcta:1,explicacion:"f(3) = 3 × 3 = 9."},
    {pregunta:"¿Cuál es el pH neutro aproximado a 25 °C?",opciones:["3","7","11"],correcta:1,explicacion:"En agua pura a 25 °C, pH cercano a 7 es neutro."},
    {pregunta:"¿Qué mide la mediana?",opciones:["Valor central ordenado","Valor más frecuente","Suma de valores"],correcta:0,explicacion:"Es el valor central de los datos ordenados."}],
    parejas:[{concepto:"Mediana",definicion:"Dato central"},{concepto:"Derivada",definicion:"Tasa de cambio"},{concepto:"pH",definicion:"Acidez o basicidad"}]}
};

function nivelDe(etapa:Etapa,grado:string):string {
  const numero=Number((grado||"").match(/\d+/)?.[0]||"0");
  if(etapa==="primaria")return numero<=2&&numero>0?"p1":numero<=4&&numero>0?"p2":"p3";
  return numero<=2&&numero>0?"s1":numero<=4&&numero>0?"s2":"s3";
}

function barajar<T,>(lista:T[]):T[]{
  const nueva=[...lista];
  for(let i=nueva.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[nueva[i],nueva[j]]=[nueva[j],nueva[i]];}
  return nueva;
}

function JuegoPreguntas({banco}:{banco:Banco}){
  const [indice,setIndice]=useState(0);
  const [respuesta,setRespuesta]=useState<number|null>(null);
  const [puntos,setPuntos]=useState(0);
  const pregunta=banco.preguntas[indice];
  const terminado=indice>=banco.preguntas.length;
  return <div className="atlas-juego-cuerpo">
    <p className="atlas-juego-subtitulo">Preguntados · {Math.min(indice+1,banco.preguntas.length)} de {banco.preguntas.length} · {puntos} puntos</p>
    {terminado?<><h3>¡Terminaste!</h3><p>Lograste {puntos} de {banco.preguntas.length} respuestas correctas.</p><button className="atlas-boton" onClick={()=>{setIndice(0);setRespuesta(null);setPuntos(0);}}>Volver a jugar</button></>:<>
      <h3>{pregunta.pregunta}</h3>
      <div className="atlas-juego-opciones">{pregunta.opciones.map((op,i)=><button key={op} disabled={respuesta!==null} className={respuesta!==null&&i===pregunta.correcta?"correcta":respuesta===i?"incorrecta":""} onClick={()=>{setRespuesta(i);if(i===pregunta.correcta)setPuntos(p=>p+1);}}>{op}</button>)}</div>
      {respuesta!==null&&<div className="atlas-juego-explicacion" role="status"><strong>{respuesta===pregunta.correcta?"¡Correcto!":"A seguir practicando."}</strong><p>{pregunta.explicacion}</p><button className="atlas-boton" onClick={()=>{setIndice(i=>i+1);setRespuesta(null);}}>Siguiente</button></div>}
    </>}
  </div>;
}

type Tarjeta={id:string;par:number;texto:string};
function JuegoMemoria({banco}:{banco:Banco}){
  const [cartas,setCartas]=useState<Tarjeta[]>(()=>barajar(banco.parejas.flatMap((p,i)=>[{id:"c"+i,par:i,texto:p.concepto},{id:"d"+i,par:i,texto:p.definicion}])));
  const [visibles,setVisibles]=useState<string[]>([]);
  const [resueltas,setResueltas]=useState<number[]>([]);
  const [intentos,setIntentos]=useState(0);
  const [bloqueado,setBloqueado]=useState(false);
  const tiempo=useRef<ReturnType<typeof setTimeout>|null>(null);
  useEffect(()=>()=>{if(tiempo.current)clearTimeout(tiempo.current);},[]);
  function elegir(c:Tarjeta){
    if(bloqueado||visibles.includes(c.id)||resueltas.includes(c.par))return;
    if(!visibles.length){setVisibles([c.id]);return;}
    const primera=cartas.find(x=>x.id===visibles[0]);
    setIntentos(n=>n+1);
    if(primera&&primera.par===c.par){setResueltas(prev=>[...prev,c.par]);setVisibles([]);}
    else{setVisibles([visibles[0],c.id]);setBloqueado(true);tiempo.current=setTimeout(()=>{setVisibles([]);setBloqueado(false);},950);}
  }
  function reiniciar(){if(tiempo.current)clearTimeout(tiempo.current);setCartas(barajar(banco.parejas.flatMap((p,i)=>[{id:"c"+i,par:i,texto:p.concepto},{id:"d"+i,par:i,texto:p.definicion}])));setVisibles([]);setResueltas([]);setIntentos(0);setBloqueado(false);}
  return <div className="atlas-juego-cuerpo"><p className="atlas-juego-subtitulo">Memoria · {resueltas.length}/{banco.parejas.length} parejas · {intentos} intentos</p><p>Encontrá cada concepto y su definición.</p><div className="atlas-memoria-grid">{cartas.map(c=><button key={c.id} disabled={resueltas.includes(c.par)} className={resueltas.includes(c.par)?"resuelta":""} onClick={()=>elegir(c)}>{visibles.includes(c.id)||resueltas.includes(c.par)?c.texto:"?"}</button>)}</div>{resueltas.length===banco.parejas.length&&<p>¡Encontraste todas las parejas!</p>}<button className="atlas-enlace" onClick={reiniciar}><RotateCcw size={15}/> Mezclar otra vez</button></div>;
}

function Lienzo(){
  const canvas=useRef<HTMLCanvasElement|null>(null);
  const pintando=useRef(false);
  const [color,setColor]=useState("#176b5b");
  const [grosor,setGrosor]=useState(5);
  function ubicacion(e:React.PointerEvent<HTMLCanvasElement>){
    const c=canvas.current!;
    const rect=c.getBoundingClientRect();
    return {x:(e.clientX-rect.left)*c.width/rect.width,y:(e.clientY-rect.top)*c.height/rect.height};
  }
  function comenzar(e:React.PointerEvent<HTMLCanvasElement>){
    const c=canvas.current!,ctx=c.getContext("2d");if(!ctx)return;
    e.currentTarget.setPointerCapture(e.pointerId);pintando.current=true;
    const p=ubicacion(e);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(p.x+0.1,p.y);ctx.strokeStyle=color;ctx.lineWidth=grosor;ctx.lineCap="round";ctx.lineJoin="round";ctx.stroke();
  }
  function mover(e:React.PointerEvent<HTMLCanvasElement>){if(!pintando.current)return;const ctx=canvas.current?.getContext("2d");if(!ctx)return;const p=ubicacion(e);ctx.lineTo(p.x,p.y);ctx.stroke();}
  function limpiar(){const c=canvas.current;if(c)c.getContext("2d")?.clearRect(0,0,c.width,c.height);}
  function guardar(){const c=canvas.current;if(!c)return;const exportado=document.createElement("canvas");exportado.width=c.width;exportado.height=c.height;const ctx=exportado.getContext("2d");if(!ctx)return;ctx.fillStyle="#ffffff";ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(c,0,0);const a=document.createElement("a");a.download="mi-dibujo-atlas.png";a.href=exportado.toDataURL("image/png");a.click();}
  return <div className="atlas-juego-cuerpo"><p className="atlas-juego-subtitulo">Mi rincón de dibujo · libre y sin conexión</p><p>Podés dibujar con mouse, dedo o lápiz táctil. El dibujo queda en esta pantalla hasta que lo guardes o cierres.</p><div className="atlas-pintura-herramientas"><label>Color <input aria-label="Color del lápiz" type="color" value={color} onChange={e=>setColor(e.target.value)}/></label><label>Trazo <input aria-label="Grosor del trazo" type="range" min="2" max="22" value={grosor} onChange={e=>setGrosor(Number(e.target.value))}/></label><button className="atlas-enlace" onClick={limpiar}>Borrar dibujo</button><button className="atlas-boton" onClick={guardar}>Guardar PNG</button></div><canvas ref={canvas} width={760} height={410} className="atlas-lienzo" aria-label="Lienzo para dibujar" onPointerDown={comenzar} onPointerMove={mover} onPointerUp={()=>pintando.current=false} onPointerCancel={()=>pintando.current=false}/></div>;
}

export default function PausaAtlas({etapa,grado="",materia=""}:{etapa:Etapa;grado?:string;materia?:string}){
  const [juego,setJuego]=useState<"preguntas"|"memoria"|"dibujo">("preguntas");
  const banco=contenidos[nivelDe(etapa,grado)];
  return <section className="atlas-desafios-nuevos">
    <p className="atlas-juego-subtitulo">{materia?materia+" · ":""}{etapa==="primaria"?"Primaria":"Secundaria"}{grado?" · "+grado:""}</p>
    <h2>Elegí un desafío</h2>
    <p>Estos juegos traen contenidos generales orientativos según el año. Se ejecutan en tu navegador, sin Ollama ni Internet durante la partida. Todavía no se generan a partir de los PDF.</p>
    <div className="atlas-juegos-menu">
      <button className={juego==="preguntas"?"seleccionado":""} onClick={()=>setJuego("preguntas")}><Brain size={19}/> Preguntados</button>
      <button className={juego==="memoria"?"seleccionado":""} onClick={()=>setJuego("memoria")}><Puzzle size={19}/> Memoria</button>
      <button className={juego==="dibujo"?"seleccionado":""} onClick={()=>setJuego("dibujo")}><Paintbrush size={19}/> Dibujar</button>
    </div>
    <div className="atlas-juego-panel" key={juego+"-"+etapa+"-"+grado}>{juego==="preguntas"?<JuegoPreguntas banco={banco}/>:juego==="memoria"?<JuegoMemoria banco={banco}/>:<Lienzo/>}</div>
  </section>;
}
