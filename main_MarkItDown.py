from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn
import logging
import io
from markitdown import MarkItDown, FileConversionException, UnsupportedFormatException
import os

# Cargar las variables desde el archivo .env
from dotenv import load_dotenv
load_dotenv()

# Acceder a las variables de entorno
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI(title="File Upload API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == USER and form_data.password == PASSWORD:
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    try:
        content = await file.read()

        diagnostic_messages = []
        markdown_content = None

        if file.content_type == 'application/pdf' or file.filename.endswith('.pdf'):
            try:
                markitdown = MarkItDown()
                result = markitdown.convert_stream(io.BytesIO(content))
                markdown_content = result.text_content
                diagnostic_messages.append("PDF convertido exitosamente a Markdown con MarkItDown")
            except (FileConversionException, UnsupportedFormatException) as e:
                diagnostic_messages.append(f"MarkItDown: Error al convertir PDF a Markdown: {str(e)}")
            except Exception as e:
                diagnostic_messages.append(f"MarkItDown: Error inesperado al convertir PDF a Markdown: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return {
            "status": "success",
            "message": "File processed successfully",
            "file_details": {
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type,
                "markdown_content": markdown_content.strip() if markdown_content else None,
                "diagnostic_messages": diagnostic_messages,
            },
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.get("/")
async def root():
    return {"message": "File Upload API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
