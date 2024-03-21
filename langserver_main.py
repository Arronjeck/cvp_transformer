#!/usr/bin/env python

import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langserve import add_routes

##FastAPI是一个基于Python的Web框架，用于构建高性能、可扩展的API。它提供了一种简单、直观的方式来定义API端点，以及处理HTTP请求和响应。
app = FastAPI(
  title="cvp transformer server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

@app.post('/uploadfile/')
async def upload_file(file_name:str, file_buffer: memoryview):
    try:
        # 把 upfile 写到 data 目录下
        file_path = f"data/{file_name}"
        with open(file_path, "wb") as f:
            f.write(file_buffer)
        # 返回成功响应
        return JSONResponse({'status': 'success', 'message': 'File uploaded successfully.'})
    except Exception as e:
        # 返回失败响应
        return JSONResponse({'status': 'error', 'message': 'Failed to upload file.'}, status=500)

## 接口2
#add_routes( 
#           app, 
#           prompt | model,
#           path="/chatwithvector"
#)

if __name__ == "__main__":
    import uvicorn
    ## Python的web服务器
    uvicorn.run(app, host="localhost", port=9091)