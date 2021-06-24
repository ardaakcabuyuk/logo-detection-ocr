from logo_detection_tool.predict import Detector, Recognizer
from ocr_tool.ocr import OCR

ocr = OCR('logos/Capture.png')
text = ocr.extract_key_words()
print(text)
