# File Upload API

Esta es una API desarrollada con FastAPI que permite a los usuarios subir archivos (PDFs e imágenes) para extraer texto y códigos QR. La API también incluye autenticación basada en tokens para proteger los endpoints.

## Características principales

- **Extracción de texto de PDFs**: Utiliza `pdfplumber` para extraer texto directamente de archivos PDF. Si falla, recurre a OCR (Reconocimiento Óptico de Caracteres) mediante `pytesseract` para extraer texto de las imágenes generadas a partir del PDF.
  
- **Extracción de texto de imágenes**: Utiliza OCR (`pytesseract`) para extraer texto de imágenes. Además, aplica técnicas de preprocesamiento de imágenes para mejorar la precisión del reconocimiento de texto.

- **Detección de códigos QR**: Utiliza la librería `QReader` para detectar y decodificar códigos QR en imágenes y PDFs.

- **Autenticación basada en tokens**: La API utiliza OAuth2 con contraseña para autenticar a los usuarios. Los usuarios deben proporcionar un nombre de usuario y contraseña válidos para obtener un token de acceso, que luego se utiliza para acceder a los endpoints protegidos.

## Requisitos

- Python 3.7 o superior.
- Tesseract OCR instalado en el sistema (ajustar la ruta en el código si es necesario).
- Dependencias listadas en `requirements.txt`.

## Instalación

1. Clona el repositorio:

   ```
   git clone https://github.com/EmaAristimuno/api_extract_text_file_py.git
   cd api_extract_text_file_py
   ```

## Crea un entorno virtual e instala las dependencias:

En Linux usa:
    `python -m venv venv`
    `source venv/bin/activate ` 

 En Windows usa: 
    `venv\Scripts\activate`

    luego

`pip install -r requirements.txt`

## Configura las variables de entorno:

Crea un archivo .env en la raíz del proyecto con las siguientes variables:

`
USER=tu_usuario
PASSWORD=tu_contraseña
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
`
## Ejecuta la aplicación:

    `
      uvicorn main:app --reload
    `   
o 
`
python main.py
`
    La API estará disponible en http://127.0.0.1:8000.
### Uso
Autenticación
Para acceder a los endpoints protegidos, primero debes autenticarte:

`
curl -X POST "http://127.0.0.1:8000/login" -d "username=tu_usuario&password=tu_contraseña"
`

Esto devolverá un token de acceso que debes incluir en las solicitudes subsiguientes como un encabezado Authorization.

## Subida de archivos
Puedes subir archivos PDF o imágenes para extraer texto y códigos QR:

`
curl -X POST "http://127.0.0.1:8000/upload/" -H "Authorization: Bearer tu_token" -F "file=@ruta/al/archivo.pdf"
`

La respuesta incluirá el texto extraído, cualquier código QR detectado y mensajes de diagnóstico.

### Endpoints
**POST /login**: Autentica al usuario y devuelve un token de acceso.

**POST /upload/**: Sube un archivo para extraer texto y códigos QR. Requiere autenticación.

**GET /**: Verifica que la API está en funcionamiento.

## Ejemplo de respuesta
`
{
  "status": "success",
  "message": "File processed successfully",
  "file_details": {
    "filename": "example.pdf",
    "size": 123456,
    "content_type": "application/pdf",
    "text_content": "Texto extraído del archivo...",
    "qr_content": "Contenido del código QR...",
    "diagnostic_messages": [
      "Texto extraído exitosamente con pdfplumber",
      "Código QR encontrado en la página 1"
    ]
  }
}
`