# Frontend de Atlas

Interfaz inicial de escritorio para Atlas, pensada para escuelas con equipos modestos.
Usa React, Vite, Tailwind y componentes propios inspirados en shadcn/ui.

## Comandos

```powershell
npm install
npm run dev
npm run build
```

La vista local queda en:

`http://127.0.0.1:5173/`

## Criterios visuales

- Pantalla util desde el inicio, sin landing.
- Layout de biblioteca, busqueda, ruta y estado local.
- Componentes sobrios y de alto contraste.
- Sin fondos pesados ni animaciones costosas.
- Preparado para integrarse luego en Tauri como app desktop.

## API local para Ollama

Para que `Ver fragmentos` y `Crear practica` usen Ollama local:

```powershell
cd C:\proy\Atlas-by-Gramisci
python api_atlas.py
```

La API escucha en:

`http://127.0.0.1:8765/`

Si la API no esta levantada, la interfaz muestra una salida provisoria local para no cortar el flujo.
