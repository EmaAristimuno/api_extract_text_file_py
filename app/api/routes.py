
# app/api/routes.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..core.security import create_access_token, get_current_user
from ..services.file_processor import FileProcessor
from ..core.config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == settings.USER and form_data.password == settings.PASSWORD:
        access_token = create_access_token({"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), 
    current_user: str = Depends(get_current_user),
    extract_qr: bool = True  # Parámetro opcional para extraer QR
):
    processor = FileProcessor()
    return await processor.process_file(file, extract_qr)
