import type { ChangeEvent, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Brain,
  CheckCircle2,
  ClipboardCheck,
  Cloud,
  Database,
  FileText,
  FolderOpen,
  Gauge,
  GraduationCap,
  HardDrive,
  LibraryBig,
  ListChecks,
  MessageSquare,
  PlayCircle,
  RefreshCw,
  Route,
  Search,
  Server,
  Upload,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { Boton } from "./componentes/ui/boton";
import { Campo } from "./componentes/ui/campo";
import { Insignia } from "./componentes/ui/insignia";
import { CuerpoPanel, EncabezadoPanel, Panel } from "./componentes/ui/panel";
import {
  type Documento,
  type EstadoPractica,
  type Materia,
  type NivelDocumento,
  type PracticaDocumento,
  type SeccionDocumento,
  documentos as documentosSemilla,
  materias as materiasSemilla,
  practicas as practicasSemilla,
  resultadosBusqueda,
  seccionesDetectadas,
} from "./datos/semilla";
import { combinarClases } from "./lib/utilidades";

const CLAVE_DOCUMENTOS = "atlas.documentos";

const navegacion = [
  { id: "biblioteca", etiqueta: "Biblioteca", icono: LibraryBig },
  { id: "materias", etiqueta: "Materias", icono: BookOpen },
  { id: "documentos", etiqueta: "Documentos", icono: FileText },
  { id: "rutas", etiqueta: "Rutas", icono: Route },
  { id: "progreso", etiqueta: "Progreso", icono: Gauge },
];

const titulos: Record<string, string> = {
  biblioteca: "Biblioteca local",
  materias: "Estudio del documento",
  documentos: "Documentos",
  rutas: "Ruta de aprendizaje",
  progreso: "Progreso",
};

function obtenerDocumentosIniciales() {
  const guardados = window.localStorage.getItem(CLAVE_DOCUMENTOS);

  if (!guardados) {
    return documentosSemilla;
  }

  try {
    return JSON.parse(guardados) as Documento[];
  } catch {
    return documentosSemilla;
  }
}

function etiquetaNivel(nivel: NivelDocumento) {
  const etiquetas: Record<NivelDocumento, string> = {
    1: "Nivel 1: comprension basica",
    2: "Nivel 2: aplicacion",
    3: "Nivel 3: evaluacion integradora / defensa",
  };

  return etiquetas[nivel];
}

function clasificarResultado(score: number | null) {
  if (score === null) {
    return "sin score";
  }

  if (score < 60) {
    return "no aprobado";
  }

  if (score < 75) {
    return "aprobado justo";
  }

  if (score < 90) {
    return "aprobado comodo";
  }

  return "excelente";
}

function calcularEstadoSeccion(
  practica: PracticaDocumento | undefined,
  actividad: ActividadSeccion | undefined,
): EstadoSeccion {
  if (practica?.score !== null && practica?.score !== undefined) {
    if (practica.score < 60) {
      return "NECESITA_REPASO";
    }

    if (practica.score >= 90) {
      return "DOMINADA";
    }

    return "APROBADA";
  }

  if (practica?.estado === "NECESITA_REPASO") {
    return "NECESITA_REPASO";
  }

  if (practica?.estado === "EN_CURSO" || actividad?.practicaIniciada) {
    return "PRACTICANDO";
  }

  if (actividad?.fragmentosLeidos || actividad?.consultas) {
    return "EN_ESTUDIO";
  }

  return "PENDIENTE";
}

function estadoPracticaDe(seccion: SeccionDocumento, practica?: PracticaDocumento): EstadoPractica {
  if (!practica || seccion.fragment_ids.length === 0) {
    return "SIN_GENERAR";
  }

  return practica.estado;
}

function pesoEstado(estado: EstadoSeccion) {
  const pesos: Record<EstadoSeccion, number> = {
    PENDIENTE: 0,
    EN_ESTUDIO: 25,
    PRACTICANDO: 45,
    NECESITA_REPASO: 40,
    APROBADA: 78,
    DOMINADA: 100,
  };

  return pesos[estado];
}

function varianteEstadoSeccion(estado: EstadoSeccion) {
  if (estado === "DOMINADA" || estado === "APROBADA") {
    return "local";
  }

  if (estado === "EN_ESTUDIO" || estado === "PRACTICANDO") {
    return "internet";
  }

  if (estado === "NECESITA_REPASO") {
    return "alerta";
  }

  return "neutro";
}

function varianteEstadoDocumento(estado: Documento["estado"]) {
  if (estado === "indexado") {
    return "local";
  }

  if (estado === "error") {
    return "alerta";
  }

  return "neutro";
}

function textoEstadoDocumento(estado: Documento["estado"]) {
  if (estado === "indexado") {
    return "Indexado";
  }

  if (estado === "error") {
    return "Error";
  }

  return "Pendiente";
}

function salidaPorResultado(score: number | null) {
  const clasificacion = clasificarResultado(score);

  if (score === null) {
    return "Todavia no hay evaluacion final para esta seccion.";
  }

  if (score < 60) {
    return "No aprueba: Atlas recomienda repasar esta seccion antes de avanzar.";
  }

  if (score < 75) {
    return "Aprueba justo: puede continuar, pero la seccion queda marcada como debil.";
  }

  if (score < 90) {
    return "Aprueba comodo: puede avanzar normalmente.";
  }

  return `Excelente: seccion dominada (${clasificacion}).`;
}

function calcularProgresoDocumento(secciones: SeccionCalculada[]) {
  if (secciones.length === 0) {
    return 0;
  }

  const total = secciones.reduce((suma, seccion) => suma + pesoEstado(seccion.estado), 0);
  return Math.round(total / secciones.length);
}


function convertirTextoEnLineas(texto?: string) {
  return (texto ?? "")
    .split("\n")
    .map((linea) => linea.trim())
    .filter(Boolean)
    .slice(0, 8);
}

function describirFragmentos(fragmentos?: FragmentoApi[]) {
  return (fragmentos ?? []).slice(0, 5).map((fragmento) => {
    const numero = fragmento.numero_fragmento ?? "?";
    const contenido = fragmento.contenido?.trim() || "Fragmento sin texto visible.";
    return `Fragmento ${numero}: ${contenido.slice(0, 220)}`;
  });
}

async function pedirApiEstudioLocal(
  ruta: "fragmentos" | "consultar" | "practica",
  cuerpo: Record<string, unknown>,
) {
  const respuesta = await fetch(`http://127.0.0.1:8765/api/estudio/${ruta}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cuerpo),
  });

  const datos = (await respuesta.json()) as RespuestaApiEstudio;

  if (!respuesta.ok) {
    throw new Error(datos.detalle ?? datos.error ?? "No respondio la API local de Atlas");
  }

  return datos;
}
function App() {
  const documentosIniciales = useMemo(() => obtenerDocumentosIniciales(), []);
  const [seccionActiva, setSeccionActiva] = useState("materias");
  const [consulta, setConsulta] = useState("");
  const [documentosLocales, setDocumentosLocales] = useState<Documento[]>(documentosIniciales);
  const [documentoActivoId, setDocumentoActivoId] = useState(documentosIniciales[0]?.id ?? 0);
  const [modeloActivo, setModeloActivo] = useState<ModeloIA>("ollama-local");
  const [practicasLocales, setPracticasLocales] = useState<PracticaDocumento[]>(practicasSemilla);
  const [actividadSecciones, setActividadSecciones] = useState<Record<number, ActividadSeccion>>({});
  const [salidaTrabajo, setSalidaTrabajo] = useState<SalidaTrabajo | null>(null);
  const selectorArchivosRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    window.localStorage.setItem(CLAVE_DOCUMENTOS, JSON.stringify(documentosLocales));
  }, [documentosLocales]);

  const documentoActivo = useMemo(() => {
    return documentosLocales.find((documento) => documento.id === documentoActivoId) ?? documentosLocales[0] ?? null;
  }, [documentoActivoId, documentosLocales]);

  const seccionesDocumento = useMemo(() => {
    if (!documentoActivo) {
      return [];
    }

    return seccionesDetectadas.filter((seccion) => seccion.document_id === documentoActivo.id);
  }, [documentoActivo]);

  const seccionesCalculadas = useMemo(() => {
    return seccionesDocumento.map((seccion) => {
      const practica = practicasLocales.find((item) => item.section_id === seccion.id);
      const actividad = actividadSecciones[seccion.id];
      const estado = calcularEstadoSeccion(practica, actividad);
      const estadoPractica = estadoPracticaDe(seccion, practica);

      return {
        ...seccion,
        practica,
        actividad,
        estado,
        estadoPractica,
        clasificacion: clasificarResultado(practica?.score ?? null),
      };
    });
  }, [actividadSecciones, practicasLocales, seccionesDocumento]);

  const progresoDocumento = calcularProgresoDocumento(seccionesCalculadas);

  const materiaActiva = documentoActivo?.materia ?? "Sin materia";

  const materias = useMemo<Materia[]>(() => {
    return materiasSemilla.map((materia) => ({
      ...materia,
      documentos: documentosLocales.filter((documento) => documento.materia === materia.nombre).length,
      progreso: materia.nombre === materiaActiva ? progresoDocumento : materia.progreso,
    }));
  }, [documentosLocales, materiaActiva, progresoDocumento]);

  const resultadosFiltrados = useMemo(() => {
    const texto = consulta.trim().toLowerCase();

    if (!texto) {
      return resultadosBusqueda;
    }

    return resultadosBusqueda.filter((resultado) => {
      return [resultado.titulo, resultado.materia, resultado.fragmento, resultado.coincidencia]
        .join(" ")
        .toLowerCase()
        .includes(texto);
    });
  }, [consulta]);

  const documentosFiltrados = useMemo(() => {
    const texto = consulta.trim().toLowerCase();

    if (!texto) {
      return documentosLocales;
    }

    return documentosLocales.filter((documento) => {
      return [documento.titulo, documento.materia, documento.tipo, documento.estado]
        .join(" ")
        .toLowerCase()
        .includes(texto);
    });
  }, [consulta, documentosLocales]);

  function seleccionarDocumento(documentoId: number) {
    setDocumentoActivoId(documentoId);
    setSalidaTrabajo(null);
    setSeccionActiva("materias");
  }

  function seleccionarArchivos(evento: ChangeEvent<HTMLInputElement>) {
    const archivos = Array.from(evento.target.files ?? []);

    if (archivos.length === 0) {
      return;
    }

    const siguienteId = Math.max(0, ...documentosLocales.map((documento) => documento.id)) + 1;
    const materiaDestino = documentoActivo?.materia ?? materiasSemilla[0]?.nombre ?? "General";
    const nuevosDocumentos = archivos.map((archivo, indice) => ({
      id: siguienteId + indice,
      titulo: archivo.name,
      materia: materiaDestino,
      tipo: archivo.name.split(".").pop()?.toUpperCase() || "ARCHIVO",
      paginas: 0,
      estado: "pendiente" as const,
    }));

    setDocumentosLocales((actuales) => [...nuevosDocumentos, ...actuales]);
    setDocumentoActivoId(nuevosDocumentos[0].id);
    setSalidaTrabajo(null);
    setSeccionActiva("materias");
    evento.target.value = "";
  }

  function eliminarDocumento(documentoId: number) {
    const documento = documentosLocales.find((item) => item.id === documentoId);

    if (!documento) {
      return;
    }

    const confirmar = window.confirm(`Eliminar ${documento.titulo} de la biblioteca local?`);

    if (!confirmar) {
      return;
    }

    const restantes = documentosLocales.filter((item) => item.id !== documentoId);
    setDocumentosLocales(restantes);
    setDocumentoActivoId(restantes[0]?.id ?? 0);
    setSalidaTrabajo(null);
  }

  function restaurarDemo() {
    setDocumentosLocales(documentosSemilla);
    setDocumentoActivoId(documentosSemilla[0]?.id ?? 0);
    setPracticasLocales(practicasSemilla);
    setActividadSecciones({});
    setSalidaTrabajo(null);
    setSeccionActiva("materias");
  }

  function registrarActividad(sectionId: number, tipo: keyof ActividadSeccion) {
    setActividadSecciones((actual) => ({
      ...actual,
      [sectionId]: {
        ...actual[sectionId],
        [tipo]: (actual[sectionId]?.[tipo] ?? 0) + 1,
      },
    }));
  }

  async function estudiarSeccion(seccion: SeccionCalculada) {
    if (!documentoActivo) {
      return;
    }

    registrarActividad(seccion.id, "fragmentosLeidos");
    setSalidaTrabajo({
      tipo: "estudio",
      titulo: "Buscando fragmentos locales",
      seccion: seccion.titulo,
      detalle: "Atlas esta consultando la API local para priorizar fragmentos reales del documento activo.",
      metadatos: [
        { etiqueta: "document_id", valor: String(documentoActivo.id) },
        { etiqueta: "section_id", valor: String(seccion.id) },
        { etiqueta: "fragment_ids", valor: seccion.fragment_ids.join(", ") || "sin fragmentos" },
      ],
    });

    try {
      const datos = await pedirApiEstudioLocal("fragmentos", {
        documento: documentoActivo.titulo,
        materia: documentoActivo.materia,
        paso_ruta: seccion.titulo,
        document_id: documentoActivo.id,
        section_id: seccion.id,
        fragment_ids: seccion.fragment_ids,
        modelo: modeloActivo,
        difficulty_level: seccion.nivel,
      });
      const lineasRespuesta = convertirTextoEnLineas(datos.respuesta);
      const fragmentos = describirFragmentos(datos.fragmentos);

      setSalidaTrabajo({
        tipo: "estudio",
        titulo: "Fragmentos de estudio",
        seccion: seccion.titulo,
        detalle:
          fragmentos.length > 0
            ? "Atlas encontro fragmentos locales y los ordeno para estudiar esta seccion."
            : "Todavia no hay fragmentos indexados para esta seccion.",
        elementos: [...lineasRespuesta, ...fragmentos],
        metadatos: [
          { etiqueta: "document_id", valor: String(documentoActivo.id) },
          { etiqueta: "section_id", valor: String(seccion.id) },
          { etiqueta: "fragment_ids", valor: seccion.fragment_ids.join(", ") || "sin fragmentos" },
        ],
      });
    } catch (error) {
      setSalidaTrabajo({
        tipo: "estudio",
        titulo: "No se pudo leer desde la API local",
        seccion: seccion.titulo,
        detalle: error instanceof Error ? error.message : "La API local de Atlas no respondio.",
        elementos: [
          seccion.fragment_ids.length > 0
            ? `La seccion tiene ${seccion.fragment_ids.length} fragmentos previstos, pero falta conectarlos al indice local.`
            : "Todavia no hay fragmentos indexados para esta seccion.",
        ],
      });
    }
  }

  async function consultarSeccion(seccion: SeccionCalculada) {
    if (!documentoActivo) {
      return;
    }

    registrarActividad(seccion.id, "consultas");
    const pregunta = `Explica la seccion "${seccion.titulo}" usando solo el documento activo. Si faltan fragmentos, decilo sin inventar.`;

    setSalidaTrabajo({
      tipo: "consulta",
      titulo: modeloActivo === "ollama-local" ? "Consultando Ollama local" : "Consultando IA online",
      seccion: seccion.titulo,
      detalle: "El chat queda asociado al documento activo, la seccion y el modelo elegido.",
      metadatos: [
        { etiqueta: "document_id", valor: String(documentoActivo.id) },
        { etiqueta: "section_id", valor: String(seccion.id) },
        { etiqueta: "model_used", valor: modeloActivo },
      ],
    });

    try {
      const datos = await pedirApiEstudioLocal("consultar", {
        documento: documentoActivo.titulo,
        materia: documentoActivo.materia,
        paso_ruta: seccion.titulo,
        pregunta,
        modelo: modeloActivo,
        document_id: documentoActivo.id,
        section_id: seccion.id,
        fragment_ids: seccion.fragment_ids,
      });
      const lineasRespuesta = convertirTextoEnLineas(datos.respuesta);
      const fragmentos = describirFragmentos(datos.fragmentos);

      setSalidaTrabajo({
        tipo: "consulta",
        titulo: modeloActivo === "ollama-local" ? "Respuesta de Ollama local" : "Respuesta de IA online",
        seccion: seccion.titulo,
        detalle: datos.respuesta ?? "La consulta no devolvio texto.",
        elementos: fragmentos.length > 0 ? fragmentos : lineasRespuesta,
        metadatos: [
          { etiqueta: "document_id", valor: String(documentoActivo.id) },
          { etiqueta: "section_id", valor: String(seccion.id) },
          { etiqueta: "model_used", valor: modeloActivo },
          { etiqueta: "fragment_ids", valor: seccion.fragment_ids.join(", ") || "sin fragmentos" },
        ],
      });
    } catch (error) {
      setSalidaTrabajo({
        tipo: "consulta",
        titulo: modeloActivo === "api-online" ? "IA online no configurada" : "Consulta local no disponible",
        seccion: seccion.titulo,
        detalle:
          error instanceof Error
            ? error.message
            : "No se pudo consultar el modelo seleccionado.",
        elementos: [
          modeloActivo === "api-online"
            ? "La opcion online queda preparada para cuando haya una API externa configurada."
            : "Revisa que api_atlas.py y Ollama esten activos para responder con contexto local.",
        ],
      });
    }
  }

  async function iniciarPractica(seccion: SeccionCalculada) {
    if (!documentoActivo) {
      return;
    }

    if (seccion.fragment_ids.length === 0) {
      setSalidaTrabajo({
        tipo: "practica",
        titulo: "Practica no generada",
        seccion: seccion.titulo,
        detalle: "Todavia no hay practica generada para esta seccion.",
        elementos: ["Atlas necesita fragmentos reales del documento antes de generar practica."],
      });
      return;
    }

    setSalidaTrabajo({
      tipo: "practica",
      titulo: "Generando practica local",
      seccion: seccion.titulo,
      detalle: "Atlas intenta generar practica con Ollama usando fragmentos reales del indice local.",
      metadatos: [
        { etiqueta: "document_id", valor: String(documentoActivo.id) },
        { etiqueta: "section_id", valor: String(seccion.id) },
        { etiqueta: "fragment_ids", valor: seccion.fragment_ids.join(", ") },
        { etiqueta: "model_used", valor: modeloActivo },
        { etiqueta: "difficulty_level", valor: String(seccion.nivel) },
      ],
    });

    try {
      const datos = await pedirApiEstudioLocal("practica", {
        documento: documentoActivo.titulo,
        materia: documentoActivo.materia,
        paso_ruta: seccion.titulo,
        document_id: documentoActivo.id,
        section_id: seccion.id,
        fragment_ids: seccion.fragment_ids,
        modelo: modeloActivo,
        difficulty_level: seccion.nivel,
      });

      if (datos.estado === "SIN_GENERAR" || !datos.fragmentos || datos.fragmentos.length === 0) {
        setSalidaTrabajo({
          tipo: "practica",
          titulo: "Practica no generada",
          seccion: seccion.titulo,
          detalle: "Todavia no hay practica generada para esta seccion.",
          elementos: ["No se encontraron fragmentos reales en el indice local para construir preguntas."],
        });
        return;
      }

      const preguntas = datos.questions && datos.questions.length > 0 ? datos.questions : convertirTextoEnLineas(datos.respuesta);
      const nuevaPractica: PracticaDocumento = {
        id: Date.now(),
        document_id: documentoActivo.id,
        section_id: seccion.id,
        fragment_ids:
          datos.fragment_ids && datos.fragment_ids.length > 0
            ? datos.fragment_ids
            : datos.fragmentos
                .map((fragmento) => Number(fragmento.fragment_id ?? fragmento.numero_fragmento))
                .filter((numero) => Number.isFinite(numero)),
        model_used: datos.model_used === "api-online" ? "api-online" : "ollama-local",
        difficulty_level: seccion.nivel,
        questions: preguntas,
        answers: [],
        score: null,
        estado: "EN_CURSO",
      };

      setPracticasLocales((actuales) => [
        nuevaPractica,
        ...actuales.filter(
          (practica) => practica.document_id !== documentoActivo.id || practica.section_id !== seccion.id,
        ),
      ]);
      registrarActividad(seccion.id, "practicaIniciada");
      setSalidaTrabajo({
        tipo: "practica",
        titulo: "Practica generada desde fragmentos",
        seccion: seccion.titulo,
        detalle: "La practica quedo asociada al documento activo, seccion, fragmentos y modelo usado.",
        elementos: preguntas.length > 0 ? preguntas : [datos.respuesta ?? "Practica generada sin preguntas legibles."],
        metadatos: [
          { etiqueta: "document_id", valor: String(nuevaPractica.document_id) },
          { etiqueta: "section_id", valor: String(nuevaPractica.section_id) },
          { etiqueta: "fragment_ids", valor: nuevaPractica.fragment_ids.join(", ") || "sin ids" },
          { etiqueta: "model_used", valor: nuevaPractica.model_used },
          { etiqueta: "difficulty_level", valor: String(nuevaPractica.difficulty_level) },
          { etiqueta: "score", valor: "sin score" },
        ],
      });
    } catch (error) {
      setSalidaTrabajo({
        tipo: "practica",
        titulo: "Practica no generada",
        seccion: seccion.titulo,
        detalle: "Todavia no hay practica generada para esta seccion.",
        elementos: [
          error instanceof Error
            ? error.message
            : "No se pudo generar practica desde la API local.",
        ],
      });
    }
  }

  function evaluarSeccion(seccion: SeccionCalculada) {
    registrarActividad(seccion.id, "evaluaciones");
    setSalidaTrabajo({
      tipo: "evaluacion",
      titulo: "Resultado de evaluacion",
      seccion: seccion.titulo,
      detalle: salidaPorResultado(seccion.practica?.score ?? null),
    });
  }

  function reindexarDocumento() {
    setSalidaTrabajo({
      tipo: "sistema",
      titulo: "Reindexacion pendiente",
      seccion: documentoActivo?.titulo ?? "Documento",
      detalle: "Esta accion queda preparada para conectar extraccion, fragmentacion, pgvector y busqueda full-text.",
    });
  }

  function cambiarModeloRapido() {
    setModeloActivo((actual) => (actual === "ollama-local" ? "api-online" : "ollama-local"));
  }

  return (
    <div className="min-h-screen bg-fondo text-texto">
      <input
        ref={selectorArchivosRef}
        accept=".pdf,.txt,.md,.doc,.docx"
        className="hidden"
        multiple
        onChange={seleccionarArchivos}
        type="file"
      />

      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[224px_minmax(0,1fr)_340px]">
        <aside className="border-b border-borde bg-[#f7f8f4] lg:border-b-0 lg:border-r">
          <div className="flex h-full flex-col">
            <div className="border-b border-borde px-4 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primario text-primarioTexto">
                  <GraduationCap className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <h1 className="text-lg font-bold leading-6">Atlas</h1>
                  <p className="text-xs font-medium text-apagado">Biblioteca tecnica local</p>
                </div>
              </div>
            </div>

            <nav className="grid gap-1 p-3 sm:grid-cols-5 lg:block lg:space-y-1">
              {navegacion.map((item) => {
                const Icono = item.icono;
                const activo = seccionActiva === item.id;

                return (
                  <button
                    key={item.id}
                    className={combinarClases(
                      "flex h-10 items-center gap-3 rounded-md px-3 text-left text-sm font-semibold transition-colors",
                      activo
                        ? "bg-[#dfe9e6] text-[#0f4b50]"
                        : "text-[#34423a] hover:bg-[#e8eee8]",
                    )}
                    onClick={() => setSeccionActiva(item.id)}
                    type="button"
                  >
                    <Icono className="h-4 w-4 shrink-0" aria-hidden="true" />
                    <span className="truncate">{item.etiqueta}</span>
                  </button>
                );
              })}
            </nav>

            <div className="mt-auto border-t border-borde p-3">
              <div className="rounded-md border border-[#cbd8cf] bg-white p-3">
                <div className="flex items-center gap-2 text-sm font-bold text-[#183f39]">
                  <HardDrive className="h-4 w-4" aria-hidden="true" />
                  Modo escuela
                </div>
                <p className="mt-2 text-xs leading-5 text-apagado">
                  Funciona primero con biblioteca local y sincroniza cuando haya conexion.
                </p>
              </div>
            </div>
          </div>
        </aside>

        <main className="min-w-0 p-4 lg:p-5">
          <header className="mb-4 flex flex-col gap-3 border-b border-borde pb-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h2 className="text-2xl font-bold leading-8">{titulos[seccionActiva]}</h2>
              <p className="text-sm font-medium text-apagado">
                Rutas generadas desde documentos, consultas con IA y dominio calculado por evidencias.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Insignia variante="local">
                <WifiOff className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
                Local primero
              </Insignia>
              <Insignia variante="alerta">
                <RefreshCw className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
                Sync pendiente
              </Insignia>
            </div>
          </header>

          <section className="mb-4 grid gap-3 xl:grid-cols-[minmax(0,1fr)_180px]">
            <div className="relative">
              <Search
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-apagado"
                aria-hidden="true"
              />
              <Campo
                aria-label="Buscar en Atlas"
                className="pl-10"
                onChange={(evento) => setConsulta(evento.target.value)}
                placeholder="Buscar conceptos, documentos o dudas"
                value={consulta}
              />
            </div>
            <Boton className="w-full" variante="primario">
              <Search className="h-4 w-4" aria-hidden="true" />
              Buscar
            </Boton>
          </section>

          {seccionActiva === "documentos" ? (
            <VistaDocumentos
              documentoActivo={documentoActivo}
              documentos={documentosFiltrados}
              seleccionarDocumento={seleccionarDocumento}
              eliminarDocumento={eliminarDocumento}
              restaurarDemo={restaurarDemo}
              subirDocumentos={() => selectorArchivosRef.current?.click()}
            />
          ) : seccionActiva === "biblioteca" ? (
            <VistaBiblioteca
              materias={materias}
              resultadosFiltrados={resultadosFiltrados}
              abrirDocumento={(titulo) => {
                const documento = documentosLocales.find((item) => item.titulo === titulo);
                if (documento) seleccionarDocumento(documento.id);
              }}
            />
          ) : seccionActiva === "progreso" ? (
            <VistaProgreso
              documentoActivo={documentoActivo}
              secciones={seccionesCalculadas}
              progresoDocumento={progresoDocumento}
            />
          ) : (
            <PantallaEstudio
              documentoActivo={documentoActivo}
              materiaActiva={materiaActiva}
              secciones={seccionesCalculadas}
              progresoDocumento={progresoDocumento}
              salidaTrabajo={salidaTrabajo}
              cerrarSalida={() => setSalidaTrabajo(null)}
              estudiarSeccion={estudiarSeccion}
              consultarSeccion={consultarSeccion}
              iniciarPractica={iniciarPractica}
              evaluarSeccion={evaluarSeccion}
            />
          )}
        </main>

        <PanelContexto
          documentoActivo={documentoActivo}
          documentos={documentosLocales}
          modeloActivo={modeloActivo}
          progresoDocumento={progresoDocumento}
          seleccionarDocumento={seleccionarDocumento}
          setModeloActivo={setModeloActivo}
          subirDocumentos={() => selectorArchivosRef.current?.click()}
          reindexarDocumento={reindexarDocumento}
          cambiarModeloRapido={cambiarModeloRapido}
        />
      </div>
    </div>
  );
}

type PantallaEstudioProps = {
  documentoActivo: Documento | null;
  materiaActiva: string;
  secciones: SeccionCalculada[];
  progresoDocumento: number;
  salidaTrabajo: SalidaTrabajo | null;
  cerrarSalida: () => void;
  estudiarSeccion: (seccion: SeccionCalculada) => void;
  consultarSeccion: (seccion: SeccionCalculada) => void;
  iniciarPractica: (seccion: SeccionCalculada) => void;
  evaluarSeccion: (seccion: SeccionCalculada) => void;
};

function PantallaEstudio({
  documentoActivo,
  materiaActiva,
  secciones,
  progresoDocumento,
  salidaTrabajo,
  cerrarSalida,
  estudiarSeccion,
  consultarSeccion,
  iniciarPractica,
  evaluarSeccion,
}: PantallaEstudioProps) {
  if (!documentoActivo) {
    return (
      <div className="rounded-md border border-dashed border-borde bg-white p-8 text-center">
        <FileText className="mx-auto mb-3 h-10 w-10 text-apagado" aria-hidden="true" />
        <p className="text-base font-bold">No hay documento activo</p>
        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-apagado">
          Selecciona un documento desde el panel derecho para construir su ruta de aprendizaje.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <section className="rounded-md border border-borde bg-white p-4">
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_230px] xl:items-center">
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-normal text-apagado">Materia activa</p>
            <h3 className="mt-1 text-2xl font-bold leading-8">{materiaActiva}</h3>
            <p className="mt-2 text-sm leading-6 text-apagado">
              Biblioteca tecnica local con ruta de aprendizaje generada desde el documento seleccionado.
            </p>
          </div>
          <div className="rounded-md border border-borde bg-[#fbfcfa] p-3">
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-bold uppercase tracking-normal text-apagado">Dominio estimado</span>
              <span className="text-lg font-bold">{progresoDocumento}%</span>
            </div>
            <div className="mt-3 h-2 rounded-full bg-[#e3e8e2]">
              <div className="h-2 rounded-full bg-secundario" style={{ width: `${progresoDocumento}%` }} />
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-md border border-borde bg-[#fbfcfa] p-4">
        <p className="text-xs font-bold uppercase tracking-normal text-apagado">Documento activo</p>
        <div className="mt-2 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0">
            <h4 className="truncate text-xl font-bold leading-7">{documentoActivo.titulo}</h4>
            <p className="mt-1 text-sm text-apagado">
              {documentoActivo.tipo} - {documentoActivo.paginas || "sin"} paginas - {textoEstadoDocumento(documentoActivo.estado)}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Insignia variante="neutro">Nivel 1</Insignia>
            <Insignia variante="neutro">Nivel 2</Insignia>
            <Insignia variante="neutro">Nivel 3</Insignia>
          </div>
        </div>
      </section>

      {salidaTrabajo ? <SalidaTrabajoPanel salida={salidaTrabajo} cerrar={cerrarSalida} /> : null}

      <section className="space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-normal text-apagado">Ruta de aprendizaje del documento</p>
            <h3 className="mt-1 text-lg font-bold">Secciones detectadas</h3>
          </div>
          <p className="text-sm font-medium text-apagado">Estudiar - consultar - practicar - evaluar</p>
        </div>

        {secciones.length === 0 ? (
          <div className="rounded-md border border-dashed border-borde bg-white p-6 text-center">
            <Route className="mx-auto mb-3 h-9 w-9 text-apagado" aria-hidden="true" />
            <p className="text-sm font-bold">Todavia no hay secciones detectadas</p>
            <p className="mt-1 text-sm text-apagado">
              Indexa el documento para que Atlas pueda construir una ruta desde fragmentos reales.
            </p>
          </div>
        ) : (
          secciones.map((seccion, indice) => (
            <BloqueSeccion
              key={seccion.id}
              indice={indice}
              seccion={seccion}
              estudiarSeccion={estudiarSeccion}
              consultarSeccion={consultarSeccion}
              iniciarPractica={iniciarPractica}
              evaluarSeccion={evaluarSeccion}
            />
          ))
        )}
      </section>
    </div>
  );
}

type BloqueSeccionProps = {
  indice: number;
  seccion: SeccionCalculada;
  estudiarSeccion: (seccion: SeccionCalculada) => void;
  consultarSeccion: (seccion: SeccionCalculada) => void;
  iniciarPractica: (seccion: SeccionCalculada) => void;
  evaluarSeccion: (seccion: SeccionCalculada) => void;
};

function BloqueSeccion({
  indice,
  seccion,
  estudiarSeccion,
  consultarSeccion,
  iniciarPractica,
  evaluarSeccion,
}: BloqueSeccionProps) {
  const score = seccion.practica?.score ?? null;

  return (
    <article className="rounded-md border border-borde bg-white p-4">
      <div className="grid gap-4 xl:grid-cols-[42px_minmax(0,1fr)_210px] xl:items-start">
        <div
          className={combinarClases(
            "flex h-10 w-10 items-center justify-center rounded-md border text-sm font-bold",
            seccion.estado === "DOMINADA" && "border-[#496d3d] bg-[#dfead8] text-[#1f3b18]",
            seccion.estado === "APROBADA" && "border-[#6b7f55] bg-[#edf4e7] text-[#29441f]",
            seccion.estado === "PRACTICANDO" && "border-[#67889b] bg-[#e8f1f4] text-[#193f4d]",
            seccion.estado === "EN_ESTUDIO" && "border-[#0f5f66] bg-[#e8f1f4] text-[#0f4b50]",
            seccion.estado === "NECESITA_REPASO" && "border-[#d6a743] bg-[#fff4d8] text-[#6d4c00]",
            seccion.estado === "PENDIENTE" && "border-borde bg-[#f3f4f2] text-apagado",
          )}
        >
          {seccion.estado === "DOMINADA" ? <CheckCircle2 className="h-5 w-5" aria-hidden="true" /> : indice + 1}
        </div>

        <div className="min-w-0">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <h4 className="text-base font-bold leading-6">{seccion.titulo}</h4>
            <Insignia variante={varianteEstadoSeccion(seccion.estado)}>{seccion.estado}</Insignia>
          </div>
          <p className="mt-2 text-sm leading-6 text-apagado">{seccion.descripcion}</p>

          <div className="mt-3 grid gap-2 md:grid-cols-3">
            <DatoMini etiqueta="Nivel" valor={etiquetaNivel(seccion.nivel).replace("Nivel ", "N")} />
            <DatoMini etiqueta="Fragmentos" valor={String(seccion.fragment_ids.length)} />
            <DatoMini etiqueta="Practica" valor={seccion.estadoPractica} />
          </div>

          <div className="mt-3 rounded-md border border-[#d7ded8] bg-[#fbfcfa] p-3">
            <p className="text-xs font-bold uppercase tracking-normal text-[#496056]">Evidencia y resultado</p>
            <p className="mt-1 text-sm leading-5 text-[#34423a]">
              {seccion.estadoPractica === "SIN_GENERAR"
                ? "Todavia no hay practica generada para esta seccion."
                : `Score: ${score ?? "sin cerrar"} - ${clasificarResultado(score)}. ${salidaPorResultado(score)}`}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 xl:grid-cols-1">
          <Boton onClick={() => estudiarSeccion(seccion)} tamano="chico" variante="secundario">
            <BookOpen className="h-3.5 w-3.5" aria-hidden="true" />
            Estudiar
          </Boton>
          <Boton onClick={() => consultarSeccion(seccion)} tamano="chico" variante="fantasma">
            <MessageSquare className="h-3.5 w-3.5" aria-hidden="true" />
            Consultar
          </Boton>
          <Boton onClick={() => iniciarPractica(seccion)} tamano="chico" variante="fantasma">
            <PlayCircle className="h-3.5 w-3.5" aria-hidden="true" />
            Iniciar practica
          </Boton>
          <Boton onClick={() => evaluarSeccion(seccion)} tamano="chico" variante="fantasma">
            <ClipboardCheck className="h-3.5 w-3.5" aria-hidden="true" />
            Evaluar
          </Boton>
        </div>
      </div>
    </article>
  );
}

type PanelContextoProps = {
  documentoActivo: Documento | null;
  documentos: Documento[];
  modeloActivo: ModeloIA;
  progresoDocumento: number;
  seleccionarDocumento: (documentoId: number) => void;
  setModeloActivo: (modelo: ModeloIA) => void;
  subirDocumentos: () => void;
  reindexarDocumento: () => void;
  cambiarModeloRapido: () => void;
};

function PanelContexto({
  documentoActivo,
  documentos,
  modeloActivo,
  progresoDocumento,
  seleccionarDocumento,
  setModeloActivo,
  subirDocumentos,
  reindexarDocumento,
  cambiarModeloRapido,
}: PanelContextoProps) {
  return (
    <aside className="border-t border-borde bg-[#f7f8f4] p-4 lg:border-l lg:border-t-0 lg:p-5">
      <div className="space-y-4">
        <Panel>
          <EncabezadoPanel>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Documento activo</h3>
              <p className="text-xs text-apagado">Selector de contexto</p>
            </div>
            <FileText className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
          </EncabezadoPanel>
          <CuerpoPanel className="space-y-3">
            <select
              className="h-10 w-full rounded-md border border-borde bg-white px-3 text-sm font-semibold outline-none focus:border-[#0f5f66] focus:ring-2 focus:ring-[#c8dbd9]"
              onChange={(evento) => seleccionarDocumento(Number(evento.target.value))}
              value={documentoActivo?.id ?? ""}
            >
              {documentos.map((documento) => (
                <option key={documento.id} value={documento.id}>
                  {documento.titulo}
                </option>
              ))}
            </select>

            {documentoActivo ? (
              <div className="rounded-md border border-[#cbd8cf] bg-[#fbfcfa] p-3">
                <p className="line-clamp-2 text-sm font-bold leading-5">{documentoActivo.titulo}</p>
                <p className="mt-1 text-xs font-semibold text-apagado">{documentoActivo.materia}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Insignia variante={varianteEstadoDocumento(documentoActivo.estado)}>
                    {textoEstadoDocumento(documentoActivo.estado)}
                  </Insignia>
                  <Insignia variante="neutro">{documentoActivo.tipo}</Insignia>
                </div>
              </div>
            ) : null}
          </CuerpoPanel>
        </Panel>

        <Panel>
          <EncabezadoPanel>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Modelo disponible</h3>
              <p className="text-xs text-apagado">Chat asociado al documento</p>
            </div>
            <Brain className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
          </EncabezadoPanel>
          <CuerpoPanel className="space-y-2">
            <button
              className={combinarClases(
                "flex w-full items-center justify-between rounded-md border p-3 text-left text-sm font-bold",
                modeloActivo === "ollama-local" ? "border-[#0f5f66] bg-[#e8f1f4]" : "border-borde bg-white",
              )}
              onClick={() => setModeloActivo("ollama-local")}
              type="button"
            >
              <span className="flex items-center gap-2">
                <Server className="h-4 w-4" aria-hidden="true" />
                Ollama local
              </span>
              <Insignia variante="local">Offline</Insignia>
            </button>
            <button
              className={combinarClases(
                "flex w-full items-center justify-between rounded-md border p-3 text-left text-sm font-bold",
                modeloActivo === "api-online" ? "border-[#0f5f66] bg-[#e8f1f4]" : "border-borde bg-white",
              )}
              onClick={() => setModeloActivo("api-online")}
              type="button"
            >
              <span className="flex items-center gap-2">
                <Wifi className="h-4 w-4" aria-hidden="true" />
                IA online
              </span>
              <Insignia variante="alerta">Si hay internet</Insignia>
            </button>
          </CuerpoPanel>
        </Panel>

        <Panel>
          <EncabezadoPanel>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Estado local / sync</h3>
              <p className="text-xs text-apagado">Servicios de Atlas</p>
            </div>
            <Cloud className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
          </EncabezadoPanel>
          <CuerpoPanel className="space-y-3">
            <EstadoSistema
              icono={<HardDrive className="h-4 w-4" aria-hidden="true" />}
              titulo="Biblioteca local"
              detalle="Disponible"
              estado="correcto"
            />
            <EstadoSistema
              icono={<Database className="h-4 w-4" aria-hidden="true" />}
              titulo="Indice local"
              detalle="PostgreSQL + pgvector"
              estado="alerta"
            />
            <EstadoSistema
              icono={<WifiOff className="h-4 w-4" aria-hidden="true" />}
              titulo="Sincronizacion"
              detalle="Pendiente"
              estado="neutro"
            />
          </CuerpoPanel>
        </Panel>

        <Panel>
          <EncabezadoPanel>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Progreso calculado</h3>
              <p className="text-xs text-apagado">Documento activo</p>
            </div>
            <Gauge className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
          </EncabezadoPanel>
          <CuerpoPanel>
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-bold uppercase tracking-normal text-apagado">Dominio</span>
              <span className="text-lg font-bold">{progresoDocumento}%</span>
            </div>
            <div className="mt-3 h-2 rounded-full bg-[#e3e8e2]">
              <div className="h-2 rounded-full bg-secundario" style={{ width: `${progresoDocumento}%` }} />
            </div>
          </CuerpoPanel>
        </Panel>

        <Panel>
          <EncabezadoPanel>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Acciones secundarias</h3>
              <p className="text-xs text-apagado">Gestion del material</p>
            </div>
            <ListChecks className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
          </EncabezadoPanel>
          <CuerpoPanel className="grid gap-2">
            <Boton className="w-full" onClick={subirDocumentos}>
              <Upload className="h-4 w-4" aria-hidden="true" />
              Subir documento
            </Boton>
            <Boton className="w-full" onClick={reindexarDocumento} variante="fantasma">
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              Reindexar
            </Boton>
            <Boton className="w-full" onClick={cambiarModeloRapido} variante="fantasma">
              <Brain className="h-4 w-4" aria-hidden="true" />
              Cambiar modelo
            </Boton>
          </CuerpoPanel>
        </Panel>
      </div>
    </aside>
  );
}

type VistaBibliotecaProps = {
  materias: Materia[];
  resultadosFiltrados: typeof resultadosBusqueda;
  abrirDocumento: (titulo: string) => void;
};

function VistaBiblioteca({ materias, resultadosFiltrados, abrirDocumento }: VistaBibliotecaProps) {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(300px,0.8fr)]">
      <Panel className="min-w-0">
        <EncabezadoPanel>
          <div>
            <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Busqueda local</h3>
            <p className="text-xs text-apagado">Texto completo y semantica</p>
          </div>
          <Insignia variante="neutro">{resultadosFiltrados.length}</Insignia>
        </EncabezadoPanel>
        <CuerpoPanel className="space-y-3">
          {resultadosFiltrados.map((resultado) => (
            <article key={resultado.id} className="rounded-md border border-borde bg-[#fbfcfa] p-3">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <h4 className="truncate text-sm font-bold text-[#17241d]">{resultado.titulo}</h4>
                  <p className="mt-1 text-xs font-medium text-apagado">
                    {resultado.materia}
                    {resultado.pagina > 0 ? ` - pagina ${resultado.pagina}` : ""}
                  </p>
                </div>
                <Insignia variante={resultado.fuente === "local" ? "local" : "internet"}>
                  {resultado.fuente === "local" ? "Local" : "Internet"}
                </Insignia>
              </div>
              <p className="mt-3 text-sm leading-6 text-[#26332c]">{resultado.fragmento}</p>
              <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-semibold text-[#496056]">{resultado.coincidencia}</span>
                <Boton onClick={() => abrirDocumento(resultado.titulo)} variante="fantasma" tamano="chico">
                  Abrir fuente
                  <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                </Boton>
              </div>
            </article>
          ))}
        </CuerpoPanel>
      </Panel>

      <Panel>
        <EncabezadoPanel>
          <div>
            <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Materias</h3>
            <p className="text-xs text-apagado">Biblioteca tecnica</p>
          </div>
          <BookOpen className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
        </EncabezadoPanel>
        <CuerpoPanel className="space-y-3">
          {materias.map((materia) => (
            <article key={materia.id} className="rounded-md border border-borde bg-white p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h4 className="truncate text-sm font-bold">{materia.nombre}</h4>
                  <p className="mt-1 text-xs text-apagado">{materia.documentos} documentos</p>
                </div>
                <Insignia variante={materia.estado === "local" ? "local" : "alerta"}>
                  {materia.estado === "local" ? "Local" : "Actualizable"}
                </Insignia>
              </div>
              <div className="mt-3 h-2 rounded-full bg-[#e3e8e2]">
                <div className="h-2 rounded-full bg-secundario" style={{ width: `${materia.progreso}%` }} />
              </div>
            </article>
          ))}
        </CuerpoPanel>
      </Panel>
    </div>
  );
}

type VistaDocumentosProps = {
  documentoActivo: Documento | null;
  documentos: Documento[];
  seleccionarDocumento: (documentoId: number) => void;
  eliminarDocumento: (documentoId: number) => void;
  restaurarDemo: () => void;
  subirDocumentos: () => void;
};

function VistaDocumentos({
  documentoActivo,
  documentos,
  seleccionarDocumento,
  eliminarDocumento,
  restaurarDemo,
  subirDocumentos,
}: VistaDocumentosProps) {
  return (
    <Panel className="min-w-0">
      <EncabezadoPanel>
        <div>
          <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Documentos locales</h3>
          <p className="text-xs text-apagado">Carga, seleccion y estado de indexacion</p>
        </div>
        <div className="flex gap-2">
          <Boton onClick={subirDocumentos} tamano="chico">
            <Upload className="h-3.5 w-3.5" aria-hidden="true" />
            Subir
          </Boton>
          <Boton onClick={restaurarDemo} tamano="chico" variante="fantasma">
            Demo
          </Boton>
        </div>
      </EncabezadoPanel>
      <CuerpoPanel className="space-y-2">
        {documentos.map((documento) => (
          <article
            key={documento.id}
            className={combinarClases(
              "rounded-md border bg-white p-3",
              documentoActivo?.id === documento.id ? "border-[#0f5f66]" : "border-borde",
            )}
          >
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
              <div className="min-w-0">
                <h4 className="truncate text-sm font-bold">{documento.titulo}</h4>
                <p className="mt-1 text-xs font-medium text-apagado">
                  {documento.materia} - {documento.tipo} - {documento.paginas || "sin"} pag.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Insignia variante={varianteEstadoDocumento(documento.estado)}>
                  {textoEstadoDocumento(documento.estado)}
                </Insignia>
                <Boton onClick={() => seleccionarDocumento(documento.id)} tamano="chico" variante="fantasma">
                  <FolderOpen className="h-3.5 w-3.5" aria-hidden="true" />
                  Abrir
                </Boton>
                <Boton onClick={() => eliminarDocumento(documento.id)} tamano="chico" variante="peligro">
                  <X className="h-3.5 w-3.5" aria-hidden="true" />
                  Quitar
                </Boton>
              </div>
            </div>
          </article>
        ))}
      </CuerpoPanel>
    </Panel>
  );
}

type VistaProgresoProps = {
  documentoActivo: Documento | null;
  secciones: SeccionCalculada[];
  progresoDocumento: number;
};

function VistaProgreso({ documentoActivo, secciones, progresoDocumento }: VistaProgresoProps) {
  return (
    <Panel>
      <EncabezadoPanel>
        <div>
          <h3 className="text-sm font-bold uppercase tracking-normal text-[#29362f]">Dominio del documento</h3>
          <p className="text-xs text-apagado">Calculado desde practica, evaluacion y repaso</p>
        </div>
        <Gauge className="h-4 w-4 text-[#4c6258]" aria-hidden="true" />
      </EncabezadoPanel>
      <CuerpoPanel className="space-y-3">
        <div className="rounded-md border border-borde bg-[#fbfcfa] p-4">
          <h4 className="text-base font-bold">{documentoActivo?.titulo ?? "Sin documento"}</h4>
          <p className="mt-1 text-sm text-apagado">{progresoDocumento}% de dominio estimado</p>
        </div>
        {secciones.map((seccion) => (
          <div key={seccion.id} className="rounded-md border border-borde bg-white p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-bold">{seccion.titulo}</p>
              <Insignia variante={varianteEstadoSeccion(seccion.estado)}>{seccion.estado}</Insignia>
            </div>
            <p className="mt-1 text-xs text-apagado">
              {clasificarResultado(seccion.practica?.score ?? null)} - practica {seccion.estadoPractica}
            </p>
          </div>
        ))}
      </CuerpoPanel>
    </Panel>
  );
}

function SalidaTrabajoPanel({ salida, cerrar }: { salida: SalidaTrabajo; cerrar: () => void }) {
  return (
    <div className="rounded-md border border-[#cbd8cf] bg-[#fbfcfa] p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-normal text-apagado">{salida.tipo}</p>
          <h4 className="mt-1 text-sm font-bold">{salida.titulo}</h4>
          <p className="mt-1 text-xs font-semibold text-[#496056]">{salida.seccion}</p>
        </div>
        <button className="rounded-md p-1 hover:bg-[#e7ede8]" onClick={cerrar} type="button">
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
      <p className="mt-3 rounded-md border border-borde bg-white p-3 text-sm leading-6 text-[#26332c]">
        {salida.detalle}
      </p>
      {salida.elementos && salida.elementos.length > 0 ? (
        <div className="mt-3 space-y-2">
          {salida.elementos.map((elemento, indice) => (
            <div key={`${salida.tipo}-${indice}`} className="rounded-md border border-borde bg-white p-2 text-xs leading-5 text-[#26332c]">
              <span className="font-bold">{indice + 1}. </span>
              {elemento}
            </div>
          ))}
        </div>
      ) : null}
      {salida.metadatos && salida.metadatos.length > 0 ? (
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          {salida.metadatos.map((item) => (
            <DatoMini key={`${item.etiqueta}-${item.valor}`} etiqueta={item.etiqueta} valor={item.valor} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

type PropiedadesDatoMini = {
  etiqueta: string;
  valor: string;
};

function DatoMini({ etiqueta, valor }: PropiedadesDatoMini) {
  return (
    <div className="rounded-md border border-borde bg-[#f8faf7] px-2 py-2">
      <div className="truncate text-base font-bold text-texto">{valor}</div>
      <div className="text-[11px] font-semibold uppercase tracking-normal text-apagado">
        {etiqueta}
      </div>
    </div>
  );
}

type EstadoSistemaProps = {
  icono: ReactNode;
  titulo: string;
  detalle: string;
  estado: "correcto" | "alerta" | "neutro";
};

function EstadoSistema({ icono, titulo, detalle, estado }: EstadoSistemaProps) {
  return (
    <div className="flex items-center gap-3 rounded-md border border-borde bg-white p-3">
      <div
        className={combinarClases(
          "flex h-9 w-9 shrink-0 items-center justify-center rounded-md border",
          estado === "correcto" && "border-[#6b7f55] bg-[#edf4e7] text-[#29441f]",
          estado === "alerta" && "border-[#d6a743] bg-[#fff4d8] text-[#6d4c00]",
          estado === "neutro" && "border-borde bg-[#f3f4f2] text-[#475049]",
        )}
      >
        {icono}
      </div>
      <div className="min-w-0">
        <p className="truncate text-sm font-bold">{titulo}</p>
        <p className="mt-1 truncate text-xs font-semibold text-apagado">{detalle}</p>
      </div>
    </div>
  );
}

type ModeloIA = "ollama-local" | "api-online";
type EstadoSeccion = "PENDIENTE" | "EN_ESTUDIO" | "PRACTICANDO" | "NECESITA_REPASO" | "APROBADA" | "DOMINADA";

type ActividadSeccion = {
  fragmentosLeidos?: number;
  consultas?: number;
  practicaIniciada?: number;
  evaluaciones?: number;
};

type SeccionCalculada = SeccionDocumento & {
  practica?: PracticaDocumento;
  actividad?: ActividadSeccion;
  estado: EstadoSeccion;
  estadoPractica: EstadoPractica;
  clasificacion: string;
};

type SalidaTrabajo = {
  tipo: "estudio" | "consulta" | "practica" | "evaluacion" | "sistema";
  titulo: string;
  seccion: string;
  detalle: string;
  elementos?: string[];
  metadatos?: Array<{ etiqueta: string; valor: string }>;
};

type FragmentoApi = {
  materia?: string;
  documento?: string;
  numero_fragmento?: number;
  contenido?: string;
  document_id?: number;
  section_id?: number;
  fragment_id?: number;
};

type RespuestaApiEstudio = {
  respuesta?: string;
  estado?: EstadoPractica;
  fragmentos?: FragmentoApi[];
  fragment_ids?: number[];
  questions?: string[];
  answers?: string[];
  score?: number | null;
  model_used?: "ollama-local" | "api-online";
  difficulty_level?: NivelDocumento;
  error?: string;
  detalle?: string;
};

export default App;





