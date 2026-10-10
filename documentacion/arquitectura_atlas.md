# Arquitectura de Atlas

Atlas funciona como una Encarta moderna offline-first. El sistema debe poder
generar rutas de aprendizaje sin internet usando documentos locales, y usar
internet solo para complementar informacion cuando haya conexion.

## Modulos

- `services.configuracion`: variables de entorno y rutas principales.
- `services.documentos`: descubrimiento de documentos locales.
- `services.lector_pdf`: extraccion de texto desde PDF.
- `services.fragmentacion`: division del texto en fragmentos indexables.
- `services.incrustaciones`: generacion local de vectores con Ollama.
- `services.repositorio_conocimiento`: escritura de fragmentos en PostgreSQL.
- `services.buscador`: busqueda full-text, semantica e hibrida.
- `services.sincronizacion`: deteccion de modo local o expandido.
- `agents.curador_ruta`: genera rutas de aprendizaje.
- `agents.generador_plan`: convierte rutas en planes semanales.
- `agents.evaluador`: diagnostica preparacion y brechas.
- `agents.curador_conocimiento`: extrae materias, temas y conceptos.

## Flujo de datos local

1. El usuario guarda documentos en `data/documentos`.
2. Atlas lee cada documento y extrae texto.
3. El texto se divide en fragmentos.
4. Cada fragmento obtiene una incrustacion local.
5. PostgreSQL guarda documentos, fragmentos, texto full-text y vectores.
6. El buscador combina coincidencia textual y similitud semantica.
7. Los agentes usan ese conocimiento para crear rutas, planes y evaluaciones.

## Flujo con internet

1. Atlas detecta conexion.
2. Consulta fuentes externas configuradas.
3. Resume y cura la informacion externa.
4. Marca origen, fecha y confianza.
5. Propone complementos para rutas locales.
6. Reindexa el material aprobado.

## Tablas principales

- `usuarios`
- `materias`
- `documentos`
- `paginas_documento`
- `fragmentos_documento`
- `conceptos`
- `fragmentos_conceptos`
- `rutas_aprendizaje`
- `pasos_ruta_aprendizaje`
- `progreso_usuario`
- `consultas_busqueda`
- `fuentes_sincronizacion`
- `trabajos_sincronizacion`
- `eventos_sincronizacion`
