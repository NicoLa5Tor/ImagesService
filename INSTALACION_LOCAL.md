# Instalacion local de ImagesService

## Que es

Servicio FastAPI para crear carpetas, subir imagenes y servir archivos estaticos desde `static/images`.

## Requisitos

- Python 3.11+
- pip
- virtualenv recomendado

## Archivo `.env`

Crea `ImagesService/.env` con algo como esto:

```env
PROJECT_NAME=Images Service
API_VERSION=1.0.0
STATIC_DIR=static
IMAGES_SUBDIR=images

ALLOW_ORIGINS=http://localhost:5050,http://localhost:4200,http://localhost:8081
ALLOW_METHODS=GET,POST,DELETE,OPTIONS
ALLOW_HEADERS=*

ALLOWED_EXTENSIONS=jpg,jpeg,png,webp,apk
PUBLIC_BASE_URL=http://localhost:8000

UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_RELOAD=true
```

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar en local

Opcion 1, usando el entrypoint Python:

```bash
python main.py
```

Opcion 2, usando Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Abrir:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/`

## Docker

```bash
docker compose up --build
```

Nota: el `docker-compose.yml` de este proyecto usa una red externa llamada `unidev_app-unidev`. Para correrlo aislado en local simple, suele ser mas facil usar Python directo.

## Dependencias que espera

- Ninguna obligatoria para arrancar
- El backend de UniDev puede consumirlo via `APP_DOCUMENT_STORAGE_BASE_URL=http://localhost:8000`

## Problemas comunes

- Si no aparecen URLs publicas correctas, revisa `PUBLIC_BASE_URL`.
- Si el backend no puede subir archivos, revisa CORS y que el puerto coincida con `APP_DOCUMENT_STORAGE_BASE_URL`.
