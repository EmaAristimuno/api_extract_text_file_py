# app/services/qr_extractor.py
from qreader import QReader
import numpy as np
from PIL import Image
import io
from pdf2image import convert_from_bytes
from typing import Tuple, List, Optional

class QRExtractor:
    def __init__(self):
        self.qreader = QReader()

    def extract_from_image(self, image_bytes: bytes) -> Tuple[str, List[str]]:
        diagnostic_messages = []
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            decoded_texts = self.qreader.detect_and_decode(image=image_np)
            
            decoded_texts = [text for text in decoded_texts if text]
            
            if decoded_texts:
                diagnostic_messages.append("Código(s) QR extraído(s) exitosamente con QReader")
                return "\n".join(decoded_texts), diagnostic_messages
            else:
                diagnostic_messages.append("No se encontraron códigos QR en la imagen")
                return "", diagnostic_messages
        except Exception as e:
            diagnostic_messages.append(f"Error procesando imagen para extraer QR: {str(e)}")
            return "", diagnostic_messages
        

    def extract_from_pdf(self, pdf_bytes: bytes) -> Tuple[Optional[str], List[str]]:
        diagnostic_messages = []
        try:
            # Convertir solo la primera página del PDF a imagen
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
            diagnostic_messages.append(f"Convertida la primera página a imagen para buscar códigos QR")
            
            for i, image in enumerate(images):
                image_buffer = io.BytesIO()
                image.save(image_buffer, format="PNG")
                image_buffer.seek(0)
                
                qr_content, qr_messages = self.extract_from_image(image_buffer.read())
                diagnostic_messages.extend(qr_messages)
                
                if qr_content and qr_content.strip():
                    diagnostic_messages.append(f"Código QR encontrado en la primera página")
                    return qr_content, diagnostic_messages
            
            diagnostic_messages.append("No se encontraron códigos QR en la primera página del PDF")
            return None, diagnostic_messages
        except Exception as e:
            diagnostic_messages.append(f"Error al procesar el PDF para buscar QR: {str(e)}")
            return None, diagnostic_messages
