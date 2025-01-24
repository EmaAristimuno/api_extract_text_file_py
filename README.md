# Guía para Instalar un Entorno Virtual en Python con FastAPI

Este documento te guiará paso a paso para configurar un entorno virtual en Python y utilizar FastAPI para desarrollar una api/web.

## Requisitos Previos

- **Python**: Asegúrate de tener Python instalado en tu sistema. Puedes verificar la instalación ejecutando `python --version` o `py --version` en tu terminal.

## Paso 1: Crear un Entorno Virtual

1. **Navega al Directorio del Proyecto**: Abre una terminal y dirígete al directorio donde deseas crear tu proyecto.

2. **Crear el Entorno Virtual**: Ejecuta el siguiente comando para crear un entorno virtual llamado `.venv`:

   ```bash
   py -3 -m venv .venv


## Paso 2: Activar el Entorno Virtual
 Para activar el entorno virtual, ejecuta el siguiente comando dependiendo de tu sistema operativo:

**Windows:

`.venv\Scripts\activate`

**macOS/Linux:

`source .venv/bin/activate`

## Paso 3: Instalar Dependencias
 Con el entorno virtual activado, instala FastAPI y otras dependencias necesarias:

`pip install fastapi python-multipart uvicorn PyPDF2`

## Paso 4: Ejecutar la Aplicación
Crea un archivo main.py en el directorio de tu proyecto y añade el código necesario para tu aplicación FastAPI.

Ejecutar la Aplicación: Para iniciar la aplicación, ejecuta el siguiente comando:

`py main.py`

Esto iniciará un servidor local, y podrás acceder a tu aplicación FastAPI en http://127.0.0.1:8000.

## Paso 5: Desactivar el Entorno Virtual
Cuando hayas terminado de trabajar en tu proyecto, puedes desactivar el entorno virtual ejecutando:

`deactivate`