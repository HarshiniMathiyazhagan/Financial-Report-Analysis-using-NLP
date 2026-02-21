import pdfplumber
import pytesseract
from PIL import Image
import re
import spacy
import io
import fitz  # PyMuPDF

class FinancialReportAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.patterns = self._get_patterns()

    def _get_patterns(self):
        return {
            'revenue': r'revenue(?:s)?[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)\s*(billion|million|thousand)?',
            'profit': r'(?:gross|operating|net)?\s+profit[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)\s*(billion|million|thousand)?',
            'net_income': r'net\s+income[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)\s*(billion|million|thousand)?',
            'total_assets': r'total\s+assets[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)\s*(billion|million|thousand)?',
            'total_liabilities': r'total\s+liabilities[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)\s*(billion|million|thousand)?',
            'earnings_per_share': r'earnings\s+per\s+share[^$\d]{0,20}(?:usd|\$)?\s*(\d[\d,\.]*)',
            'operating_margin': r'operating\s+margin[^%\d]{0,20}(\d+(?:\.\d+)?)\s*%',
            'return_on_equity': r'return\s+on\s+equity[^%\d]{0,20}(\d+(?:\.\d+)?)\s*%',
            'debt_to_equity': r'debt\s+to\s+equity[^:\d]{0,20}(\d+(?:\.\d+)?)',
        }

    def read_document(self, file_path):
        text = ""

        # Extract text using pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            text += f"\nError extracting text with pdfplumber: {str(e)}\n"

        # OCR on embedded images using PyMuPDF
        try:
            doc = fitz.open(file_path)
            for page in doc:
                image_list = page.get_images(full=True)
                for img in image_list:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    ocr_text = pytesseract.image_to_string(image)
                    text += "\n" + ocr_text
        except Exception as e:
            text += f"\nError extracting images with PyMuPDF: {str(e)}\n"

        return text

    def extract_financial_metrics(self, text):
        metrics = {key: None for key in self.patterns.keys()}

        for metric, pattern in self.patterns.items():
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                value_str = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else None
                value = self._normalize_value(value_str, unit)
                if value is not None:
                    metrics[metric] = value
                    break

        return metrics

    def _normalize_value(self, value_str, unit=None):
        try:
            value = float(value_str.replace(',', ''))
            multiplier = {
                'billion': 1e9,
                'million': 1e6,
                'thousand': 1e3
            }.get(unit, 1)
            return value * multiplier
        except:
            return None

    def summarize_text(self, text, max_sentences=5):
        doc = self.nlp(text)
        sentences = list(doc.sents)
        return ' '.join([str(s) for s in sentences[:max_sentences]])
