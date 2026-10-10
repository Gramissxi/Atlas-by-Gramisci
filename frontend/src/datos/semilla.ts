export type Materia = {
  id: number;
  nombre: string;
  documentos: number;
  progreso: number;
  estado: "local" | "actualizable";
};

export type Documento = {
  id: number;
  titulo: string;
  materia: string;
  tipo: string;
  paginas: number;
  estado: "indexado" | "pendiente" | "error";
};

export type ResultadoBusqueda = {
  id: number;
  titulo: string;
  materia: string;
  pagina: number;
  fuente: "local" | "internet";
  fragmento: string;
  coincidencia: string;
};

export type NivelDocumento = 1 | 2 | 3;

export type SeccionDocumento = {
  id: number;
  document_id: number;
  titulo: string;
  descripcion: string;
  nivel: NivelDocumento;
  fragment_ids: number[];
};

export type EstadoPractica = "SIN_GENERAR" | "GENERADA" | "EN_CURSO" | "FINALIZADA" | "NECESITA_REPASO";

export type PracticaDocumento = {
  id: number;
  document_id: number;
  section_id: number;
  fragment_ids: number[];
  model_used: "ollama-local" | "api-online";
  difficulty_level: NivelDocumento;
  questions: string[];
  answers: string[];
  score: number | null;
  estado: EstadoPractica;
};

export const materias: Materia[] = [
  {
    id: 1,
    nombre: "Ingenieria de Datos II",
    documentos: 2,
    progreso: 42,
    estado: "local",
  },
  {
    id: 2,
    nombre: "Calculo",
    documentos: 1,
    progreso: 18,
    estado: "local",
  },
  {
    id: 3,
    nombre: "Programacion",
    documentos: 1,
    progreso: 64,
    estado: "actualizable",
  },
  {
    id: 4,
    nombre: "Probabilidad y Estadistica",
    documentos: 1,
    progreso: 9,
    estado: "local",
  },
];

export const documentos: Documento[] = [
  {
    id: 1,
    titulo: "IDD-II_Clase08_AFB.pdf",
    materia: "Ingenieria de Datos II",
    tipo: "PDF",
    paginas: 42,
    estado: "indexado",
  },
  {
    id: 2,
    titulo: "IDD-II_Clase07_AFB.pdf",
    materia: "Ingenieria de Datos II",
    tipo: "PDF",
    paginas: 39,
    estado: "indexado",
  },
  {
    id: 3,
    titulo: "Modelo de examen - C1.pdf",
    materia: "Calculo",
    tipo: "PDF",
    paginas: 8,
    estado: "indexado",
  },
  {
    id: 4,
    titulo: "Guia Problemas Estadistica General - UADE.pdf",
    materia: "Probabilidad y Estadistica",
    tipo: "PDF",
    paginas: 66,
    estado: "pendiente",
  },
  {
    id: 5,
    titulo: "Apunte estructuras de control.md",
    materia: "Programacion",
    tipo: "MD",
    paginas: 0,
    estado: "error",
  },
];

export const resultadosBusqueda: ResultadoBusqueda[] = [
  {
    id: 1,
    titulo: "Modelo de examen - C1.pdf",
    materia: "Calculo",
    pagina: 3,
    fuente: "local",
    coincidencia: "full-text + semantica",
    fragmento:
      "El resultado se obtiene aproximando el desarrollo y revisando el error esperado en el intervalo indicado.",
  },
  {
    id: 2,
    titulo: "IDD-II_Clase08_AFB.pdf",
    materia: "Ingenieria de Datos II",
    pagina: 18,
    fuente: "local",
    coincidencia: "semantica",
    fragmento:
      "La arquitectura de datos debe separar ingestion, almacenamiento, transformacion y consulta para sostener cambios futuros.",
  },
  {
    id: 3,
    titulo: "Documentacion externa sugerida",
    materia: "Programacion",
    pagina: 0,
    fuente: "internet",
    coincidencia: "pendiente de sincronizar",
    fragmento:
      "Cuando haya conexion, Atlas puede buscar ejemplos oficiales para reforzar ejercicios y completar vacios detectados.",
  },
];

export const seccionesDetectadas: SeccionDocumento[] = [
  {
    id: 101,
    document_id: 1,
    titulo: "Arquitectura de ingesta",
    descripcion: "Identificar fuentes, eventos, validaciones iniciales y responsabilidades de entrada de datos.",
    nivel: 1,
    fragment_ids: [1101, 1102, 1103],
  },
  {
    id: 102,
    document_id: 1,
    titulo: "Separacion almacenamiento-transformacion-consulta",
    descripcion: "Relacionar zonas de datos, transformaciones y superficies de consulta para sostener cambios.",
    nivel: 2,
    fragment_ids: [1110, 1111, 1112],
  },
  {
    id: 103,
    document_id: 1,
    titulo: "Defensa de decisiones tecnicas",
    descripcion: "Explicar por que una arquitectura elegida resuelve el caso y que riesgos deja abiertos.",
    nivel: 3,
    fragment_ids: [1120, 1121],
  },
  {
    id: 201,
    document_id: 2,
    titulo: "Modelo conceptual del pipeline",
    descripcion: "Reconocer componentes, dependencias y flujo general del proceso de datos.",
    nivel: 1,
    fragment_ids: [2101, 2102],
  },
  {
    id: 202,
    document_id: 2,
    titulo: "Aplicacion a un caso de clase",
    descripcion: "Usar el modelo del documento para resolver un escenario concreto de integracion.",
    nivel: 2,
    fragment_ids: [2110, 2111, 2112],
  },
  {
    id: 301,
    document_id: 3,
    titulo: "Comprension del enunciado",
    descripcion: "Separar datos, objetivos y restricciones antes de calcular.",
    nivel: 1,
    fragment_ids: [3101, 3102],
  },
  {
    id: 302,
    document_id: 3,
    titulo: "Aplicacion de procedimientos",
    descripcion: "Resolver ejercicios del modelo justificando formulas y pasos intermedios.",
    nivel: 2,
    fragment_ids: [3110, 3111],
  },
  {
    id: 401,
    document_id: 4,
    titulo: "Lectura inicial de guia",
    descripcion: "Esperando indexacion para detectar fragmentos y ejercicios reales.",
    nivel: 1,
    fragment_ids: [],
  },
];

export const practicas: PracticaDocumento[] = [
  {
    id: 5001,
    document_id: 1,
    section_id: 101,
    fragment_ids: [1101, 1102, 1103],
    model_used: "ollama-local",
    difficulty_level: 1,
    questions: ["Explica que valida la etapa de ingesta.", "Nombra dos riesgos de entrada."],
    answers: ["", ""],
    score: 92,
    estado: "FINALIZADA",
  },
  {
    id: 5002,
    document_id: 1,
    section_id: 102,
    fragment_ids: [1110, 1111, 1112],
    model_used: "ollama-local",
    difficulty_level: 2,
    questions: ["Relaciona almacenamiento y transformacion en el caso del documento."],
    answers: [""],
    score: 68,
    estado: "FINALIZADA",
  },
  {
    id: 5003,
    document_id: 2,
    section_id: 201,
    fragment_ids: [2101, 2102],
    model_used: "ollama-local",
    difficulty_level: 1,
    questions: ["Describe el flujo general del pipeline."],
    answers: [""],
    score: null,
    estado: "GENERADA",
  },
  {
    id: 5004,
    document_id: 3,
    section_id: 301,
    fragment_ids: [3101, 3102],
    model_used: "api-online",
    difficulty_level: 1,
    questions: ["Que pide el enunciado y que datos entrega?"],
    answers: [""],
    score: 54,
    estado: "NECESITA_REPASO",
  },
];
