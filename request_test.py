import os
import requests

def fastAPI_conversation(input:str):
    msg={'input': {'question': input}}
    url = "http://127.0.0.1:6006/chatwithvector/invoke/"
    response = requests.post(url, json=msg)
    return response.json()


def fastAPI_upload(file_path:str):
    url = "http://127.0.0.1:6006/uploadfile"
    upfile = open(file_path, "rb")
    files = {'upfiles': (upfile.name, upfile.read())}   
    response = requests.post(url, files=files)
    return response.json()

if __name__ == "__main__":
    # 打印当前路径
    #print(os.getcwd())
    #resp = fastAPI_upload('本地知识库.pdf')
    #print(resp)
    print(fastAPI_conversation('hello, who are you?'))