import io

from PyPDF2 import PdfReader
from fastapi import UploadFile

from doc_ingest.services.interface.file_text_parser import IFileTextParser


class FileTextParser(IFileTextParser):
    async def parse(self, file: UploadFile) -> str:
        if file.content_type == 'application/pdf':
            return await self.__parse_pdf(file)

        return await self.__parse_md(file)

    async def __parse_md(self, file: UploadFile) -> str:
        content_bytes = await file.read()
        return content_bytes.decode('utf-8')


    async def __parse_pdf(self, file: UploadFile) -> str:
        content_bytes = await file.read()
        in_memory_file = io.BytesIO(content_bytes)

        reader = PdfReader(in_memory_file)
        text = ""
        for num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"{page_text}\n\n"
        return text
