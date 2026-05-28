from abc import ABC, abstractmethod

from fastapi import UploadFile


class IFileTextParser(ABC):
    @abstractmethod
    async def parse(self, file: UploadFile) -> str:
        pass