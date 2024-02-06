# -*- coding: cp949 -*-
import PyPDF2, os

class Pdf2TextConverter:
    def __init__(self): pass
        
    def convert(self, pdfFilePath, outputPath):
        try:
            with open(outputPath, "w", encoding="utf-8") as file:
                pdf1 = PyPDF2.PdfReader(open(pdfFilePath, 'rb'))
                for page in pdf1.pages :
                    st = page.extract_text()
                    file.write(st)
                    
        except Exception as e:
            raise(e)

