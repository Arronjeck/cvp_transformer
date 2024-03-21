
import shutil
from pathlib import Path
from .document_db import DOCMGTER
from .document_loader import DOCVECTOR


# Example usage
def doc_example():
    #DOCMGTER.update_documents()
    #documents = DOCMGTER.get_documents()
    #print(documents)
    #documents = DOCMGTER.search_file('data\\消失的她.txt')
    #print(documents)
    
    # 拷贝 data-back 下的 消失的她.txt 到 data 目录下
    shutil.copyfile('data-back\\消失的她.txt', 'data\\消失的她.txt')
    
    DOCMGTER.add_document('data\\消失的她.txt')
    #DOCMGTER.delete_file('data\\bbb.txt')
    
    