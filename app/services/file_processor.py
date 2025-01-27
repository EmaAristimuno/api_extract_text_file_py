from ollama import chat, ChatResponse
from app.models.comprobante import Comprobante
from app.services.comprobante_data_extractor import ComprobanteDataExtractor
from app.services.text_extractor import TextExtractor
from app.services.qr_extractor import QRExtractor
from app.utils.logging import logger
from fastapi import UploadFile, HTTPException

class FileProcessor:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.qr_extractor = QRExtractor()
        self.comprobante_data_extractor = ComprobanteDataExtractor()

    async def process_file(self, file: UploadFile, extract_qr: bool = True, ollama_response: bool = False) -> dict:
        try:
            content = await file.read()
            file_text = ""
            qr_content = None
            diagnostic_messages = []

            # Procesamiento de PDF o imagen
            if file.content_type == 'application/pdf' or file.filename.endswith('.pdf'):
                file_text, pdf_diagnostics = self.text_extractor.process_pdf(content)
                if extract_qr:
                    qr_content, qr_diagnostics = self.qr_extractor.extract_from_pdf(content)
                    diagnostic_messages.extend(qr_diagnostics)
                diagnostic_messages.extend(pdf_diagnostics)
            
            elif file.content_type.startswith('image/'):
                if extract_qr:
                    qr_content, qr_diagnostics = self.qr_extractor.extract_from_image(content)
                    diagnostic_messages.extend(qr_diagnostics)
                    
                if not qr_content or not extract_qr:
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

            # Consultar a Ollama para obtener información adicional estructurada
            if ollama_response:
                ollama_response = self._query_ollama(file_text)
                comprobante.otros_datos_no_formateados["ollama_response"] = ollama_response

            return {
                "status": "success",
                "message": "File processed successfully",
                "comprobante": comprobante.dict()
            }
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _query_ollama(self, text: str) -> dict:
        """
        Realiza una consulta a Ollama utilizando el método chat para extraer información adicional.
        """
        try:
            # Prompt para Ollama
            messages = [
                {
                    'role': 'user',
                    'content': f"Extrae información estructurada del siguiente texto de un comprobante:\n{text}"
                }
            ]

            # Consulta al modelo especificado
            response: ChatResponse = chat(model="llama3.2", messages=messages)

            # Acceder al contenido de la respuesta
            return response['message']['content']  # Ajusta según el formato de la respuesta
        except Exception as e:
            logger.error(f"Error querying Ollama: {str(e)}")
            return {"error": str(e)}
