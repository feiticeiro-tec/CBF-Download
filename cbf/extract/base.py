import re
import PyPDF2
from io import BytesIO
from datetime import datetime


class CBFExtratBase:
    def __init__(self, datetime=True) -> None:
        self.datetime = datetime

    def colect_time(self, row, match, format, time=False):
        """COLETA O DATETIME DE UMA LINHA"""
        data = re.search(match, row).group()
        if self.datetime:
            value = datetime.strptime(data, format)
            if time:
                return value.time()
            return value
        else:
            return data

    def bytes_pdf_to_text(self, pdf_bytes):
        """CONVERTE O BYTES DE UM PDF EM TEXTO"""
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        number_of_pages = len(reader.pages)
        text = ""
        for page_index in range(0, number_of_pages):
            page = reader.pages[page_index]
            text += page.extract_text()
            text += "\n"
        return text
