CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS materias (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    dificultad TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documentos (
    id BIGSERIAL PRIMARY KEY,
    materia_id BIGINT REFERENCES materias(id) ON DELETE SET NULL,
    titulo TEXT NOT NULL,
    tipo_fuente TEXT NOT NULL DEFAULT 'pdf',
    uri_fuente TEXT,
    ruta_local TEXT,
    hash_archivo TEXT UNIQUE,
    idioma TEXT NOT NULL DEFAULT 'es',
    estado TEXT NOT NULL DEFAULT 'pendiente',
    metadatos JSONB NOT NULL DEFAULT '{}'::jsonb,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS paginas_documento (
    id BIGSERIAL PRIMARY KEY,
    documento_id BIGINT NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    numero_pagina INTEGER NOT NULL,
    contenido TEXT NOT NULL,
    metadatos JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (documento_id, numero_pagina)
);

CREATE TABLE IF NOT EXISTS fragmentos_documento (
    id BIGSERIAL PRIMARY KEY,
    documento_id BIGINT REFERENCES documentos(id) ON DELETE CASCADE,
    materia_id BIGINT REFERENCES materias(id) ON DELETE SET NULL,
    materia_legacy TEXT,
    documento_legacy TEXT,
    numero_fragmento INTEGER NOT NULL,
    pagina_inicio INTEGER,
    pagina_fin INTEGER,
    contenido TEXT NOT NULL,
    texto_busqueda TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('spanish', coalesce(contenido, ''))
    ) STORED,
    incrustacion VECTOR(768),
    metadatos JSONB NOT NULL DEFAULT '{}'::jsonb,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS conceptos (
    id BIGSERIAL PRIMARY KEY,
    materia_id BIGINT REFERENCES materias(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    dificultad TEXT,
    incrustacion VECTOR(768),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (materia_id, nombre)
);

CREATE TABLE IF NOT EXISTS fragmentos_conceptos (
    fragmento_id BIGINT NOT NULL REFERENCES fragmentos_documento(id) ON DELETE CASCADE,
    concepto_id BIGINT NOT NULL REFERENCES conceptos(id) ON DELETE CASCADE,
    confianza NUMERIC(4, 3) NOT NULL DEFAULT 0.500,
    PRIMARY KEY (fragmento_id, concepto_id)
);

CREATE TABLE IF NOT EXISTS rutas_aprendizaje (
    id BIGSERIAL PRIMARY KEY,
    materia_id BIGINT REFERENCES materias(id) ON DELETE SET NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    origen TEXT NOT NULL DEFAULT 'local',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pasos_ruta_aprendizaje (
    id BIGSERIAL PRIMARY KEY,
    ruta_id BIGINT NOT NULL REFERENCES rutas_aprendizaje(id) ON DELETE CASCADE,
    concepto_id BIGINT REFERENCES conceptos(id) ON DELETE SET NULL,
    posicion INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    minutos_estimados INTEGER,
    UNIQUE (ruta_id, posicion)
);

CREATE TABLE IF NOT EXISTS progreso_usuario (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    materia_id BIGINT REFERENCES materias(id) ON DELETE CASCADE,
    concepto_id BIGINT REFERENCES conceptos(id) ON DELETE CASCADE,
    estado TEXT NOT NULL DEFAULT 'sin_empezar',
    puntaje NUMERIC(5, 2),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (usuario_id, materia_id, concepto_id)
);

CREATE TABLE IF NOT EXISTS consultas_busqueda (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    consulta TEXT NOT NULL,
    modo TEXT NOT NULL DEFAULT 'hibrido',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fuentes_sincronizacion (
    id BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    url_base TEXT,
    habilitada BOOLEAN NOT NULL DEFAULT true,
    ultima_sincronizacion_en TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS trabajos_sincronizacion (
    id BIGSERIAL PRIMARY KEY,
    fuente_id BIGINT REFERENCES fuentes_sincronizacion(id) ON DELETE SET NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    iniciado_en TIMESTAMPTZ,
    finalizado_en TIMESTAMPTZ,
    error TEXT
);

CREATE TABLE IF NOT EXISTS eventos_sincronizacion (
    id BIGSERIAL PRIMARY KEY,
    tipo_entidad TEXT NOT NULL,
    entidad_id BIGINT,
    operacion TEXT NOT NULL,
    datos JSONB NOT NULL DEFAULT '{}'::jsonb,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documentos_materia
    ON documentos (materia_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_materia
    ON fragmentos_documento (materia_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_documento
    ON fragmentos_documento (documento_id);

CREATE INDEX IF NOT EXISTS idx_fragmentos_texto_busqueda
    ON fragmentos_documento USING GIN (texto_busqueda);

CREATE INDEX IF NOT EXISTS idx_fragmentos_incrustacion
    ON fragmentos_documento
    USING hnsw (incrustacion vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_conceptos_materia
    ON conceptos (materia_id);

CREATE INDEX IF NOT EXISTS idx_progreso_usuario_materia
    ON progreso_usuario (usuario_id, materia_id);
