import os
import time
from datetime import datetime
from tinydb import TinyDB, Query

class DocumentManagement:
    def __init__(self, directory:str, db_path='cache/documents.json'):
        self.directory = directory
        self.db = TinyDB(db_path)
        self.query = Query()
        
    def __del__(self):
        self.db.close()

    def update_documents(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_info = os.stat(file_path)
                document = self.db.search(self.query.path == file_path)

                if not document:
                    self.db.insert({
                        'path': file_path,
                        'size': file_info.st_size,
                        'mtime': file_info.st_mtime,
                        'exist': True,
                        'history': [{'action': 'add','timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]                        
                    })
                elif file_info.st_mtime != document[0]['mtime'] or file_info.st_size != document[0]['size']:
                    self.db.update({
                        'size': file_info.st_size,
                        'mtime': file_info.st_mtime,
                        'exist': True,
                        'history': self.db.get(self.query.path == file_path)['history'] + [{'action': 'update', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
                    }, self.query.path == file_path)
                elif not document[0]['exist']:
                    self.db.update({
                        'size': file_info.st_size,
                        'mtime': file_info.st_mtime,
                        'exist': True,
                        'history': self.db.get(self.query.path == file_path)['history'] + [{'action': 'readd', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
                    }, self.query.path == file_path)
                    
        # 如果目录下文件已经删除，则记录文件删除状态
        for doc in self.db.all():
            if doc['exist'] and not os.path.exists(doc['path']):
                self.db.update({
                    'exist': False,
                    'history': doc['history'] + [{'action': 'delete', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
                }, self.query.path == doc['path'])   
                             
            # 检查history的记录条数，保留10条，其余的删除
            if len(doc['history']) > 10:
                self.db.update({
                    'history': doc['history'][-10:]
                }, self.query.path == doc['path'])
        
    
    # 定义文件更新历史记录函数
    def update_history(self, file_path, action):
        self.db.update({
            'history': self.db.get(self.query.path == file_path)['history'] + [{'action': action, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
        }, self.query.path == file_path)              
    
    def get_documents(self):
        return self.db.all()

    def close(self):
        self.db.close()

# Example usage
def example():
    doc_mgmt = DocumentManagement('data')
    doc_mgmt.update_documents()
    documents = doc_mgmt.get_documents()
    print(documents)
    
example()
