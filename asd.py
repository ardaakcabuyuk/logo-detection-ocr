from ocr_tool.ocr import OCR

ocr = OCR('images/Capture.png')
text = ocr.extract()
print(text)
