from ollama import chat, generate, ChatResponse
from app.models.comprobante import Comprobante
from app.services.comprobante_data_extractor import ComprobanteDataExtractor
from app.services.text_extractor import TextExtractor
from app.services.qr_extractor import QRExtractor
from app.utils.logging import logger
from fastapi import UploadFile, HTTPException
import time
from typing import Dict, Any, Optional

class FileProcessor:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.qr_extractor = QRExtractor()
        self.comprobante_data_extractor = ComprobanteDataExtractor()
        # Configuración por defecto para Ollama
        self.ollama_config = {
            "model": "llama3.2:1b",
            "options": {
                "num_predict": 600,     # Número máximo de tokens a generar
                "temperature": 0.5,     # Controla la aleatoriedad de las respuestas
                "top_p": 0.3           # Controla la diversidad del muestreo
            }
        }

    async def process_file(self, file: UploadFile, extract_qr: bool = True, ollama_response: bool = False) -> dict:
        """
        Procesa un archivo y extrae la información del comprobante.
        
        Args:
            file: Archivo a procesar
            extract_qr: Si se debe extraer información del código QR
            ollama_response: Si se debe consultar a Ollama para información adicional
        
        Returns:
            dict: Información procesada del comprobante
        """
        try:
            start_time = time.time()
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

            # Consultar a Ollama si es requerido
            if ollama_response and file_text:
                ollama_result = self._query_ollama(file_text)
                if "error" not in ollama_result:
                    comprobante.otros_datos_no_formateados["ollama_response"] = ollama_result

            # Agregar tiempo total de procesamiento
            total_time = round(time.time() - start_time, 2)
            
            return {
                "status": "success",
                "message": "File processed successfully",
                "processing_time": total_time,
                "comprobante": comprobante.dict()
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _query_ollama(self, text: str) -> Dict[str, Any]:
        """
        Realiza una consulta a Ollama para extraer información adicional.
        
        Args:
            text: Texto del comprobante
        
        Returns:
            Dict con la respuesta de Ollama y metadatos
        """
        start_time = time.time()
        
        try:
           # Crear un prompt directo para generate
            prompt = f"""
            Analiza el siguiente texto de comprobante y extrae TODOS los datos.
            
            Responde en formato JSON.
            
            Texto del comprobante:
            {text}
            """
            
            response = generate(
                model=self.ollama_config["model"],
                prompt=prompt,
                options=self.ollama_config["options"]
            )

            #logger.error(f"response ollama.generate: {str(response)}")
            
            processing_time = time.time() - start_time
            
            return {
                'content': response['response'],
                'model': self.ollama_config["model"],
                'time': round(processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error querying Ollama: {str(e)}")
            return {
                'error': str(e),
                'model': self.ollama_config["model"],
                'time': round(time.time() - start_time, 2)
            }