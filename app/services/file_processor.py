# app/services/file_processor.py
from fastapi import UploadFile, HTTPException
from app.models.comprobante import Comprobante
from app.services.comprobante_data_extractor import ComprobanteDataExtractor
from app.services.text_extractor import TextExtractor
from app.services.qr_extractor import QRExtractor
from app.utils.logging import logger

class FileProcessor:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.qr_extractor = QRExtractor()
        self.comprobante_data_extractor = ComprobanteDataExtractor()

    async def process_file(self, file: UploadFile, extract_qr: bool = True) -> dict:
        try:
            content = await file.read()
            file_text = ""
            qr_content = None
            diagnostic_messages = []

            if file.content_type == 'application/pdf' or file.filename.endswith('.pdf'):
                file_text, pdf_diagnostics = self.text_extractor.process_pdf(content)
                if extract_qr:  # Solo extraer QR si extract_qr es True
                    qr_content, qr_diagnostics = self.qr_extractor.extract_from_pdf(content)
                    diagnostic_messages.extend(qr_diagnostics)
                diagnostic_messages.extend(pdf_diagnostics)
            
            elif file.content_type.startswith('image/'):
                if extract_qr:  # Solo extraer QR si extract_qr es True
                    qr_content, qr_diagnostics = self.qr_extractor.extract_from_image(content)
                    diagnostic_messages.extend(qr_diagnostics)
                    
                if not qr_content or not extract_qr:  # Si no se extrajo QR o no se desea extraer, procesar texto
                    file_text, text_diagnostics = self.text_extractor.process_image(content)
                    diagnostic_messages.extend(text_diagnostics)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")

            # Extraer datos del comprobante
            comprobante = self.comprobante_data_extractor.extract_comprobante_data(file_text)

            # Actualizar campos generales del comprobante
            comprobante.filename = file.filename
            comprobante.size = len(content)
            comprobante.content_type = file.content_type
            comprobante.qr_content = qr_content.strip() if qr_content else None
            comprobante.diagnostic_messages = diagnostic_messages

            return {
                "status": "success",
                "message": "File processed successfully",
                "comprobante": comprobante.dict()
            }
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))