# import OS
import os
#from knowledge import DocumentCenter
from utils import LOGER, CONFIGER



# 判断main函数，打印 输出helloworld
if __name__ == "__main__":
    cfg = CONFIGER.get_config()
    openkey = cfg["keys"]["OPENAI_API_KEY"]    
    LOGER.debug(openkey)
    
    
    #docc = DocumentCenter()
    #docc.upload_file('aaa.txt')