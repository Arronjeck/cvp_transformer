#!/usr/bin/env python

import os
from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from chat.chat_model import get_chat_chain
from langserve import add_routes

from document import DOCMGTER,DOCVECTOR

UPLOAD_STORE_DIR="data"

##FastAPI是一个基于Python的Web框架，用于构建高性能、可扩展的API。它提供了一种简单、直观的方式来定义API端点，以及处理HTTP请求和响应。
app = FastAPI(
  title="cvp transformer server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

## 接口1
@app.post('/uploadfile/')
async def upload_file(upfiles: List[UploadFile] = File(...)):
    try:
        for ufile in upfiles:
            file_name = ufile.filename
            file_path = os.path.join(UPLOAD_STORE_DIR, file_name)
            
            # 确保上传目录存在
            if not os.path.exists(UPLOAD_STORE_DIR):
                os.makedirs(UPLOAD_STORE_DIR)
            
            with open(file_path, "wb") as f:
                content = await ufile.read()
                f.write(content)
        # 返回成功响应
        return JSONResponse({'status': 'success', 'message': 'File uploaded successfully.'})
    except Exception as e:
        # 返回失败响应
        return JSONResponse({'status': 'error', 'message': 'Failed to upload file.'}, status=500)

## 接口2
add_routes( 
           app, 
           get_chat_chain(DOCVECTOR.get_retriever()),
           path="/chatwithvector"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=1233)