import logging
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Extracts text from PDFs.
    Falls back to OCR if text extraction yields little results.
    """

    @staticmethod
    def extract_text(pdf_path: str, ocr_fallback: bool = True) -> str:
        text_content = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = "\n".join(text_content)

            # Heuristic: If text is excessively short implies scanned PDF
            if len(full_text.strip()) < 50 and ocr_fallback:
                logger.info(f"Low text content in {pdf_path}, falling back to OCR.")
                return PDFParser._ocr_extract(pdf_path)
            
            return full_text
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return ""

    @staticmethod
    def _ocr_extract(pdf_path: str) -> str:
        """
        Convert PDF pages to images and run Tesseract OCR.
        """
        try:
            images = convert_from_path(pdf_path)
            ocr_text = []
            for img in images:
                text = pytesseract.image_to_string(img)
                ocr_text.append(text)
            return "\n".join(ocr_text)
        except Exception as e:
            logger.error(f"OCR failed for {pdf_path}: {e}")
            return ""
