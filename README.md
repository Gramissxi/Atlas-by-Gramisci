# Atlas

Atlas es una biblioteca educativa offline-first: funciona con documentos locales,
busqueda full-text, busqueda semantica, rutas de aprendizaje y agentes
pedagogicos. Cuando hay internet, puede complementar la biblioteca con fuentes
externas curadas sin depender de ellas para funcionar.

## Modo local

En modo local Atlas usa:

- PDFs y materiales guardados en `data/documentos`.
- PostgreSQL como base de conocimiento.
- pgvector para busqueda semantica.
- Full-text search de PostgreSQL para busqueda literal.
- Ollama para chat e incrustaciones locales.
- Perfil y progreso del usuario.

## Modo expandido

Cuando hay conexion, Atlas puede consultar fuentes externas, resumirlas,
curarlas, comparar contra la biblioteca local y proponer mejoras a las rutas.
La informacion externa debe quedar marcada por origen y pasar por revision antes
de mezclarse con el conocimiento local.

## Esquema de datos

El esquema inicial esta en:

`base_de_datos/esquema_atlas.sql`

Incluye materias, documentos, paginas, fragmentos, conceptos, rutas de
aprendizaje, progreso, busquedas y sincronizacion.

## Variables de entorno

- `ATLAS_BD_NOMBRE`
- `ATLAS_BD_USUARIO`
- `ATLAS_BD_CLAVE`
- `ATLAS_BD_SERVIDOR`
- `ATLAS_BD_PUERTO`
- `ATLAS_MODELO_CHAT`
- `ATLAS_MODELO_INCRUSTACIONES`
- `ATLAS_RUTA_DOCUMENTOS`
- `ATLAS_RUTA_PERFIL`

## API local de estudio

Atlas incluye una API local sin dependencias extra para conectar la interfaz con Ollama:

```powershell
python api_atlas.py
```

Endpoints iniciales:

- `POST /api/estudio/fragmentos`
- `POST /api/estudio/practica`
- `POST /api/metodologias/recargar`

Estas funciones trabajan offline con documentos locales, PostgreSQL/pgvector cuando esten indexados y Ollama.
