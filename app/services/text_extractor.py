import io
from typing import Tuple, List
import pdfplumber
from pdf2image import convert_from_bytes
from ..utils.image_processing import enhance_text_recognition
from PIL import Image

class TextExtractor:
    def process_pdf(self, pdf_bytes: bytes) -> Tuple[str, List[str]]:
        diagnostic_messages = []
        extracted_text = []
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Procesar solo la primera página
                first_page = pdf.pages[0]
                text = first_page.extract_text(x_tolerance=3, y_tolerance=3)
                if text and text.strip():
                    extracted_text.append(text)
            
            if extracted_text:
                diagnostic_messages.append("Texto extraído exitosamente con pdfplumber (solo primera página)")
                return "\n".join(extracted_text), diagnostic_messages
                
            # Fall back to OCR si no se extrajo texto
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)  # Solo la primera página
            diagnostic_messages.append(f"Convertida la primera página a imagen para OCR")
            
            for i, image in enumerate(images):
                text = enhance_text_recognition(image)
                if text and text.strip():
                    extracted_text.append(f"--- Página {i+1} ---\n{text}")
                    
            if extracted_text:
                diagnostic_messages.append("Texto extraído exitosamente con OCR (solo primera página)")
            else:
                diagnostic_messages.append("OCR no pudo extraer texto de la primera página")
                
            return "\n".join(extracted_text), diagnostic_messages
            
        except Exception as e:
            diagnostic_messages.append(f"Error en proceso de extracción: {str(e)}")
            return "", diagnostic_messages

    def process_image(self, image_bytes: bytes) -> Tuple[str, List[str]]:
        diagnostic_messages = []
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = enhance_text_recognition(image)
            
            if text and text.strip():
                diagnostic_messages.append("Texto extraído exitosamente de la imagen usando OCR")
                return text, diagnostic_messages
            else:
                diagnostic_messages.append("No se pudo extraer texto de la imagen usando OCR")
                return "", diagnostic_messages
        except Exception as e:
            diagnostic_messages.append(f"Error procesando imagen usando OCR: {str(e)}")
            return "", diagnostic_messages
