# Mi Rincón de Guías – cómo agregar guías

1. Dentro de la carpeta `guias/` crea una carpeta con el nombre de la guía (ej. `Mis Primeros Trazos Divertidos`).
2. Mete ahí **las imágenes** de la guía (portada y páginas, `.jpg`/`.png`, ideal de unos 800 px de ancho) y **un archivo `.txt`** así. Las imágenes forman el carrusel en orden alfabético del nombre: `001_portada.jpg`, `002_pagina_1.jpg`, etc. El carrusel rota solo cada segundo (`rota:1000` en `index.html`) y el cliente puede deslizarlo o tocar los puntos:

```
titulo: Mis Primeros Trazos Divertidos
descripcion: Cuaderno de caligrafía para niños de 3 a 5 años...
precio digital: 250
precio impresa: 450
```
   - Si una guía solo existe en un formato, deja el otro precio fuera.
   - Al subir los cambios a GitHub, el catálogo se actualiza solo (tarda ~1 minuto).
   - Sin GitHub Actions: ejecuta `python3 generar_catalogo.py` y sube también `guias.js`.

## Publicar en GitHub Pages
Sube todo el contenido a un repositorio → **Settings → Pages → Deploy from a branch → main / (root)**.
Cambia el WhatsApp o la moneda en `index.html`, línea `const CFG={...}`.
