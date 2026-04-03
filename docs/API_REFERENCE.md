# API Reference

Documentacion operativa del servicio `Images Service Rescue` basada en el codigo actual.

## Resumen

- Base URL productiva actual: `https://docs-service.unidev.site`
- Documentacion interactiva: `GET /docs`
- Esquema OpenAPI: `GET /openapi.json`
- Documentacion alternativa: `GET /redoc`
- Healthcheck: `GET /`
- Archivos publicos: `GET /static/images/{folder}/{filename}`

## Como se manejan los errores

El servicio no define `exception_handler` personalizados ni middleware propio de errores. Todo el manejo cae en dos capas:

- FastAPI/Pydantic para errores de validacion y parametros mal formados.
- `HTTPException` lanzadas desde `StorageService` para reglas de negocio y almacenamiento.

Formas de respuesta de error:

- Errores de negocio:
```json
{
  "detail": "Folder 'reportes' not found."
}
```

- Errores de validacion:
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "name"],
      "msg": "String should match pattern '^[\\w-]+$'",
      "input": "mi carpeta"
    }
  ]
}
```

## Reglas globales

- `folder_name` debe tener entre 1 y 50 caracteres.
- `filename` base debe tener entre 1 y 120 caracteres.
- Tanto `folder_name` como `filename` solo aceptan letras, numeros, `_` y `-`.
- El archivo subido debe traer extension real; el backend conserva la extension original.
- Extensiones permitidas segun `.env`: `jpg`, `jpeg`, `png`, `pdf`, `docx`, `xlsx`.
- No hay proteccion contra sobreescritura en `POST /upload`: si ya existe un archivo con el mismo nombre final, se reemplaza.
- Las rutas publicas de archivos se sirven bajo `/static`.

## Endpoints

### `GET /`

Healthcheck simple del servicio.

Respuesta `200`:
```json
{
  "status": "ok"
}
```

Errores esperados:

- No define errores de negocio propios.

### `POST /folders`

Crea una carpeta fisica dentro de `static/images`.

Body:
```json
{
  "name": "reportes"
}
```

Respuesta `201`:
```json
{
  "message": "Folder created",
  "folder": "reportes",
  "path": "/static/images/reportes"
}
```

Errores:

- `409 Conflict`: la carpeta ya existe.
- `422 Unprocessable Entity`: nombre ausente, demasiado largo o con caracteres no permitidos.

Detalles reales:

- `Folder 'reportes' already exists.`
- Validacion por patron: `^[\\w-]+$`

### `GET /folders`

Lista las carpetas disponibles bajo `static/images`.

Respuesta `200`:
```json
[
  "reportes",
  "facturas"
]
```

Errores esperados:

- No define errores de negocio propios.

### `GET /folders/{folder_name}/files`

Lista los archivos de una carpeta y genera la URL publica de cada uno.

Ejemplo:
`GET /folders/reportes/files`

Respuesta `200`:
```json
[
  {
    "folder": "reportes",
    "filename": "incidente_2024.pdf",
    "url": "https://docs-service.unidev.site/static/images/reportes/incidente_2024.pdf"
  }
]
```

Errores:

- `404 Not Found`: la carpeta no existe.
- `422 Unprocessable Entity`: `folder_name` invalido.

Detalle real:

- `Folder 'reportes' not found.`

### `DELETE /folders/{folder_name}`

Elimina una carpeta completa y todo su contenido.

Ejemplo:
`DELETE /folders/reportes`

Respuesta `200`:
```json
{
  "message": "Folder deleted",
  "folder": "reportes"
}
```

Errores:

- `404 Not Found`: la carpeta no existe.
- `422 Unprocessable Entity`: `folder_name` invalido.

Detalle real:

- `Folder 'reportes' not found.`

### `DELETE /folders/{folder_name}/files/{filename}`

Elimina un archivo buscando por nombre base, sin extension.

Ejemplo:
`DELETE /folders/reportes/files/incidente_2024`

Respuesta `200`:
```json
{
  "message": "File deleted",
  "folder": "reportes",
  "filename": "incidente_2024.pdf"
}
```

Errores:

- `404 Not Found`: la carpeta no existe.
- `404 Not Found`: no existe ningun archivo con ese nombre base.
- `409 Conflict`: existen varias extensiones con el mismo nombre base y el backend no puede decidir cual borrar.
- `422 Unprocessable Entity`: `folder_name` o `filename` invalidos.

Detalles reales:

- `Folder 'reportes' not found.`
- `File 'incidente_2024' not found in folder 'reportes'.`
- `Multiple files share that name. Remove duplicates manually or include the extension.`

### `POST /upload`

Sube un archivo multipart y lo guarda como `static/images/{folder}/{filename}{extension_original}`.

Campos `multipart/form-data`:

- `folder`: nombre de la carpeta destino.
- `filename`: nombre base sin extension.
- `file`: archivo binario.

Ejemplo `curl`:
```bash
curl -X POST https://docs-service.unidev.site/upload \
  -F "folder=reportes" \
  -F "filename=incidente_2024" \
  -F "file=@/ruta/al/archivo.pdf"
```

Respuesta `201`:
```json
{
  "message": "File uploaded",
  "folder": "reportes",
  "filename": "incidente_2024.pdf",
  "url": "https://docs-service.unidev.site/static/images/reportes/incidente_2024.pdf"
}
```

Errores:

- `404 Not Found`: la carpeta no existe.
- `400 Bad Request`: ruta de carpeta invalida.
- `400 Bad Request`: el archivo no trae extension.
- `400 Bad Request`: nombre base vacio despues del procesamiento.
- `415 Unsupported Media Type`: extension no permitida.
- `422 Unprocessable Entity`: falta algun campo del formulario o `folder` / `filename` no pasan validacion.

Detalles reales:

- `Folder 'reportes' not found.`
- `Invalid folder path.`
- `Uploaded file must include an extension.`
- `Filename is required.`
- `Extension 'EXE' is not allowed. Allowed: docx, jpeg, jpg, pdf, png, xlsx.`

Comportamiento relevante:

- El backend usa la extension original del archivo subido.
- Si subes `file=@foto.png` con `filename=avatar`, el archivo final sera `avatar.png`.
- Si ya existe `avatar.png`, se sobrescribe sin devolver `409`.

## Endpoints publicos de archivos

### `GET /static/images/{folder}/{filename}`

Sirve el archivo tal como quedo almacenado.

Ejemplo:
`GET /static/images/reportes/incidente_2024.pdf`

Respuestas:

- `200 OK`: archivo encontrado.
- `404 Not Found`: archivo o carpeta inexistente.

Notas:

- La URL se construye desde `PUBLIC_BASE_URL` si esta definida; hoy vale `https://docs-service.unidev.site`.
- Para archivos `.apk`, el servicio intercepta la respuesta y muestra una pagina HTML de descarga.
- Si agregas `?raw=1` a un `.apk`, devuelve el archivo con `Content-Disposition: attachment`.

## CORS actual

Configuracion tomada de `ImagesService/.env`:

- `ALLOW_ORIGINS=https://docs-service.unidev.site`
- `ALLOW_METHODS=GET,POST,OPTIONS`
- `ALLOW_HEADERS=Authorization,Content-Type`

Implicaciones:

- Navegadores permitiran llamadas CORS solo desde `https://docs-service.unidev.site`.
- El backend implementa `DELETE /folders/...`, pero ese metodo no esta habilitado en CORS ahora mismo. Desde backend-server o `curl` funciona; desde navegador cross-origin puede bloquearse.

## Endpoints realmente expuestos

Estos son los endpoints visibles segun el codigo actual:

- `GET /`
- `GET /docs`
- `GET /redoc`
- `GET /openapi.json`
- `POST /folders`
- `GET /folders`
- `GET /folders/{folder_name}/files`
- `DELETE /folders/{folder_name}`
- `DELETE /folders/{folder_name}/files/{filename}`
- `POST /upload`
- `GET /static/*`
