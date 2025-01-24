# app/utils/image_processing.py
import cv2
import numpy as np
from PIL import Image
import pytesseract
from ..core.config import get_settings

settings = get_settings()
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

def enhance_text_recognition(image: Image.Image) -> str:
    img = np.array(image)
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    img = cv2.medianBlur(img, 3)
    img = cv2.equalizeHist(img)
    
    processed_image = Image.fromarray(img)
    return pytesseract.image_to_string(
        processed_image,
        config=r'--oem 3 --psm 6 -l spa'
    )
