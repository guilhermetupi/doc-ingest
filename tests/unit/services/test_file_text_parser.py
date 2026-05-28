import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile
from pypdf import PdfReader

from doc_ingest.services.file_text_parser import FileTextParser


@pytest.fixture
def parser():
    return FileTextParser()


class TestParseMarkdown:
    @pytest.mark.asyncio
    async def test_parse_markdown(self, parser):
        content = b"# Hello\n\nThis is markdown."
        file = UploadFile(
            filename="test.md",
            file=io.BytesIO(content),
            headers={"content-type": "text/markdown"},
        )

        result = await parser.parse(file)

        assert result == "# Hello\n\nThis is markdown."


class TestParsePdf:
    @pytest.mark.asyncio
    async def test_single_page(self, parser):
        with patch("doc_ingest.services.file_text_parser.PdfReader") as mock_reader_class:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Page 1 text"
            mock_reader = MagicMock(spec=PdfReader)
            mock_reader.pages = [mock_page]
            mock_reader_class.return_value = mock_reader

            content = b"fake pdf content"
            file = UploadFile(
                filename="test.pdf",
                file=io.BytesIO(content),
                headers={"content-type": "application/pdf"},
            )

            result = await parser.parse(file)

            assert result == "Page 1 text\n\n"
            mock_reader_class.assert_called_once()
            mock_page.extract_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_pages(self, parser):
        with patch("doc_ingest.services.file_text_parser.PdfReader") as mock_reader_class:
            pages = []
            for i in range(3):
                page = MagicMock()
                page.extract_text.return_value = f"Page {i + 1} text"
                pages.append(page)

            mock_reader = MagicMock(spec=PdfReader)
            mock_reader.pages = pages
            mock_reader_class.return_value = mock_reader

            content = b"fake multi-page pdf"
            file = UploadFile(
                filename="test.pdf",
                file=io.BytesIO(content),
                headers={"content-type": "application/pdf"},
            )

            result = await parser.parse(file)

            expected = "Page 1 text\n\nPage 2 text\n\nPage 3 text\n\n"
            assert result == expected
            assert len(pages) == 3
            for page in pages:
                page.extract_text.assert_called_once()
