from pathlib import Path
from .document_db import DOCMGTER
from .document_loader import DOCVECTOR


class DocumentCenter:
    def __init__(self):
        DOCMGTER.update_documents()
        self.documents = DOCMGTER.get_documents()
        self.vector_retriever = DOCVECTOR.get_retriever()
       
    def upload_file(self, file_src:str)->bool:
        return DOCMGTER.add_document(file_src)
    
    
    