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

# Subir imagen
curl -X POST http://localhost:8000/upload \
     -F "folder=reportes" \
     -F "filename=incidente_2024" \
     -F "file=@/ruta/al/archivo.jpg"
```
La respuesta de subida incluye la URL pública (`url`) que podrás abrir directamente.

## Estilo y validaciones
- Nombres de carpetas permitidos: letras, números, `_` y `-`.
- `filename` no incluye extensión; el servicio reutiliza la del archivo subido y la valida con `ALLOWED_EXTENSIONS`.
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
El servicio publica `UVICORN_PORT` (8000 por defecto) y persiste las imágenes montando la carpeta local `static/`. En producción, actualiza `.env` o usa `docker compose --env-file` para inyectar configuraciones específicas (por ejemplo el archivo `.env.example.production`).

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
