import os
import shutil
import codecs
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pypdf

import langchain.text_splitter
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.notebook import NotebookLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class DocumentVectorStore:
    def __init__(self, store_path:str='cache/vctordb', chunk_size: int = 1000, chunk_overlap: int = 200):
        logging.info("Initializing VectorStore...")
        self.store_path = store_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding = HuggingFaceEmbeddings()
        self.file_types_loaders: Dict[str, type] = {
        '.ipynb': NotebookLoader,
        '.md': UnstructuredMarkdownLoader,
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.jpg': UnstructuredImageLoader,
        '.asciidoc': TextLoader,
        '.pptx': UnstructuredPowerPointLoader,        
        '.docx': UnstructuredWordDocumentLoader,
        '.xlsx': UnstructuredExcelLoader,
        '.xml': UnstructuredXMLLoader,
        '.json': JSONLoader,
        '.csv': CSVLoader,
        }
        
        if self.load_db():
            logging.info("VectorStore loaded successfully.")
        else:
            logging.info("VectorStore not found. Creating a new one...")
            self.vector_store = Chroma(embedding_function=self.embedding, persist_directory=store_path)
        
    # 定义析构函数
    def __del__(self):
        self.vector_store.persist()
        logging.info("VectorStore closed.")
        
    def __is_utf8__(file_path: str) -> bool:
        try:
            with codecs.open(file_path, encoding='utf-8', errors='strict') as f:
                for _ in f:
                    pass
            return True
        except UnicodeDecodeError:
            return False
        
    def __split_documents__(self, documents):
        text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        return text_splitter.split_documents(documents)

    # 添加文件向量数据库
    def add_document(self, file_path: str = "data\\aaa.txt"):
        logging.info(f"Add file {file_path} to vector")
        # Split filename into base name and extension
        base_name, extension = os.path.splitext(file_path)
        
        # 判断 extension 是否在 file_types_loaders 的 key 中存在
        doc_loader = self.file_types_loaders.get(extension)
        if loader == None:
            logging.warning(f"Not support file the type of {file_path}")
            return
        
        # If it's a PDF file, check if it's encrypted
        if extension == '.pdf':
            with open(file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                if pdf_reader.is_encrypted:
                    logging.warning(f"The pdf file {file_path} has encrypted")
                    return
        elif extension == '.txt' or extension == '.asciidoc':
            if not self.__is_utf8__(file_path):
                logging.warning(f"Skipping non-UTF-8 file {file_path}")
                return
        
        file_path.replace('\\', '/')
        
        if extension == '.ipynb':
            loader = doc_loader(path=file_path, include_outputs=False, remove_newline=True)
        elif extension == '.txt':
            loader = doc_loader(file_path=file_path, encoding="utf-8")
        elif extension == '.asciidoc':
            loader = doc_loader(file_path=file_path, encoding="utf-8")
        else:
            loader = doc_loader(file_path)
        
        logging.info(f"Loading file {file_path}...")
        documents = loader.load()
        docs = self.__split_documents__(documents)
        if len(docs) > 0:
            self.vector_store.add_documents(docs)
            logging.info(f"File {file_path} store to vector successfully.")
            
    # 查询文件向量数据库
    def query_document(self, query: str):
        logging.info(f"Query document with query: {query}")
        results = self.vector_store.search(query, top_k=10)
        logging.info(f"Query result: {results}")
        return results
        
    # 更新文件向量数据库
    def update_document(self, file_path: str):
        logging.info(f"Update file {file_path} in vector")
        # Split filename into base name and extension
        base_name, extension = os.path.splitext(file_path)
        # 判断 extension 是否在 file_types_loaders 的 key 中存在
        doc_loader = self.file_types_loaders.get(extension)
        if doc_loader == None:
            logging.warning(f"Not support file the type of {file_path}")
            return
        file_path.replace('\\', '/')
        if extension == '.ipynb':
            loader = doc_loader(path=file_path, include_outputs=False, remove_newline=True)
        elif extension == '.txt' or extension == '.asciidoc':
            loader = doc_loader(file_path=file_path, encoding="utf-8")
        else:
            loader = doc_loader(file_path)
        logging.info(f"Loading file {file_path}...")
        documents = loader.load()
        docs = self.__split_documents__(documents)
        if len(docs) > 0:
            self.vector_store.update_documents(docs)
            logging.info(f"File {file_path} update in vector successfully.")
    
    # 删除文件向量数据库
    def delete_document(self, file_path: str):
        logging.info(f"Delete file {file_path} from vector")
        self.vector_store.delete(ids=[file_path])
        logging.info(f"File {file_path} delete from vector successfully.")
            
    # 加载本地向量数据库
    def load_db(self) -> bool:
        db_dir = Path(self.store_path)        
        if db_dir.exists():
            logging.info(f"Local vector db path {self.store_path} found, load data")
            self.vector_store = Chroma(persist_directory=str(db_dir), embedding_function=self.embedding)
            return True
        return False
    
    
# 使用DocumentVectorStore的样例
def sample():
    local_db = DocumentVectorStore()
    local_db.add_document('data\\本地知识库.pdf')
    ret = local_db.query_document('who is xuan jie?')
    print(ret)
    
sample()