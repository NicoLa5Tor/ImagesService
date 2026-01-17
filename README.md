# Images Service

Servicio FastAPI para gestionar carpetas e imágenes locales bajo `static/images`, pensado para integrarse con el ecosistema ECOES.

## Requisitos
- Python 3.11+
- pip y virtualenv (opcional pero recomendado)
- Docker y Docker Compose (para despliegue contenedorizado)

## Configuración local
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
Ajusta `.env` según tus necesidades (`ALLOWED_EXTENSIONS`, `UVICORN_PORT`, etc.).

## Comandos principales
```bash
# Ejecutar en modo desarrollo
uvicorn main:app --reload --port 8000

# Crear carpeta
curl -X POST http://localhost:8000/folders -H "Content-Type: application/json" -d '{"name":"reportes"}'

# Listar carpetas
curl http://localhost:8000/folders

# Listar archivos de una carpeta
curl http://localhost:8000/folders/reportes/files

# Subir imagen
curl -X POST http://localhost:8000/upload \
     -F "folder=reportes" \
     -F "filename=incidente_2024" \
     -F "file=@/ruta/al/archivo.jpg"

# Eliminar archivo (sin extensión)
curl -X DELETE http://localhost:8000/folders/reportes/files/incidente_2024


# Eliminar carpeta completa
curl -X DELETE http://localhost:8000/folders/reportes
```
La respuesta de subida incluye la URL pública (`url`) que podrás abrir directamente.

## Estilo y validaciones
- Nombres de carpetas permitidos: letras, números, `_` y `-`.
- `filename` no incluye extensión; el servicio reutiliza la del archivo subido y la valida con `ALLOWED_EXTENSIONS`.
- El listado de `/folders/<folder>/files` devuelve cada archivo con su nombre (incluida extensión) y la URL servible en `/static`.
- Para eliminar un archivo basta proporcionar el nombre base (`/folders/<folder>/files/<nombre>`); si existen varias extensiones con el mismo nombre, obtendrás un 409 de conflicto.
- Los ficheros se guardan en `static/images/<carpeta>/<filename>.<ext>` y se sirven desde `/static/...`.

## Despliegue con Docker
```bash
# Construir y levantar
docker compose up --build -d

# Ver logs
docker compose logs -f

# Detener
docker compose down
```
El contenedor escucha en `UVICORN_PORT` (8000 por defecto) y Docker Compose lo publica sólo en `127.0.0.1`, usando el mismo valor definido en tu `.env`. Las imágenes persisten gracias al volumen `./static:/app/static`.
Para entornos productivos puedes crear un `.env` específico o invocar `docker compose --env-file .env.example.production up` para ajustar host, puerto y extensiones permitidas.

## Estructura del proyecto
```
app/
  api/routes/        # Endpoints de carpetas y uploads
  core/              # Configuración y dependencias
  schemas/           # Modelos Pydantic
  services/          # Lógica de almacenamiento
static/images/       # Carpeta raíz para archivos gestionados
main.py              # Punto de entrada FastAPI
Dockerfile           # Imagen Uvicorn
```

## Próximos pasos sugeridos
- Añadir pruebas con `pytest` + `httpx` que cubran reglas de validación.
- Incorporar autenticación si el servicio se expone públicamente.
- Configurar un pipeline CI/CD que ejecute tests y actualice la imagen Docker.
