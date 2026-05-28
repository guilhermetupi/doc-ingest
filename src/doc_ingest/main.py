from fastapi import FastAPI

from doc_ingest.routes.document import document_router

app = FastAPI()

app.include_router(document_router)