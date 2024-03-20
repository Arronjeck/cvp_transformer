import os
import shutil
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
    
    def add_document(self, file_path:str )->bool:
        # 从file_path中获取文件名
        file_name = os.path.basename(file_path)
        file_info = os.stat(file_path)
        
        data_path = os.path.join(self.directory, file_name)
        document = self.db.search(self.query.path == data_path)
        if document is not None:
            if  not document[0]['exist'] or file_info.st_mtime != document[0]['mtime'] or file_info.st_size != document[0]['size']:
                # 拷贝文件 从 file_path 拷贝到 data_path
                shutil.copyfile(file_path, data_path)
                self.update_documents()
                return True
            else:
                return True        
        return False
    
    # 定义文件更新历史记录函数
    def update_history(self, file_path, action):
        self.db.update({
            'history': self.db.get(self.query.path == file_path)['history'] + [{'action': action, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
        }, self.query.path == file_path)              
    
    def get_documents(self):
        return self.db.all()
    
    # 查找文件
    def search_file(self, file_path):
        return self.db.search(lambda doc: file_path in doc['path'])
    
    # 删除文件
    def delete_file(self, file_path):
        if self.db.search(self.query.path == file_path):
            self.db.remove(self.query.path == file_path)
            return True
        else:
            return False

    def close(self):
        self.db.close()

DOCMGTER = DocumentManagement('data')

# Example usage
def example():
    DOCMGTER.update_documents()
    documents = DOCMGTER.get_documents()
    print(documents)
    documents = DOCMGTER.search_file('data\\消失的她.txt')
    print(documents)
    print(DOCMGTER.add_document('aaa.txt'))
    #DOCMGTER.delete_file('data\\bbb.txt')
    
#example()
