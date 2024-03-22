import requests
import logging
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from chat.chat_model import get_chat_chain
from document import DOCMGTER,DOCVECTOR


# AI template
bot_div_format = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://t4.ftcdn.net/jpg/02/10/96/95/360_F_210969565_cIHkcrIzRpWNZzq8eaQnYotG4pkHh0P9.jpg" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

# 用户template
user_div_format = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.pinimg.com/474x/be/3b/9b/be3b9b983cfea7c8aa64706203174fcf.jpg" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

def python_upload(upfile:UploadedFile):
    # 把 upfile 写到 data 目录下
    file_path = f"data/{upfile.name}"
    with open(file_path, "wb") as f:
        f.write(upfile.getbuffer())
    DOCMGTER.add_document(file_path)
    return "上传和解析成功！"

def fastAPI_upload(upfile:UploadedFile):
    url = "http://127.0.0.1:1233/uploadfile"
    files = {'upfiles': (upfile.name,upfile.read())}   
    response = requests.post(url, files=files)
    return response.json()

def app():
    # 初始化    
    st.set_page_config(page_title="企业级通用知识库", page_icon=":robot:")    
    st.header("企业级通用知识库")
    
    # session_state是Streamlit提供的用于存储会话状态的功能
    if "conversation" not in st.session_state:
        st.session_state.conversation = get_chat_chain(DOCVECTOR.get_retriever())
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    # 文件上传sidebar模块
    with st.sidebar:
        # 2. 设置子标题
        st.subheader("知识库管理")
        st.write("Upload a file to search for keywords.")
        # 3. 上传文档
        upfile = st.file_uploader("Choose a file", type=["txt", "pdf", "ipynb", "asciidoc"] ,
                                 accept_multiple_files=False)
        # 打印upfiles中的文件详细信息
        if upfile is not None:
            st.write("File Name:", upfile.name)
            st.write("File Type:", upfile.type)
            st.write("File Size:", upfile.size, "bytes")                
            if st.button("提交"):
                with st.spinner("请等待，处理中..."):
                    #python_upload(upfile)
                    resp = fastAPI_upload(upfile)
                    st.write(resp)
    
    # 基于知识库聊天模块
    user_input = st.text_input("请输入你的提问: ")
    # 处理用户输入，并返回响应结果
    if user_input:
        if st.session_state.conversation is not None:
            # 调用函数st.session_state.conversation，并把用户输入的内容作为一个问题传入，返回响应。
            logging.info(f'用户输入问题：{user_input}')
            # 改成调用 API
            response = st.session_state.conversation({'question': user_input})
            # session状态是Streamlit中的一个特性，允许在用户的多个请求之间保存数据。
            st.session_state.chat_history = response['chat_history']
            # 显示聊天记录
            # chat_history : 一个包含之前聊天记录的列表(一问一答的机制，所以单数是机器回答，双数是用户输入的问题)
            for i, message in enumerate(st.session_state.chat_history):
                if i % 2 == 0:
                    st.write(user_div_format.replace("{{MSG}}", message.content), unsafe_allow_html=True) # unsafe_allow_html=True表示允许HTML内容被渲染
                else:
                    st.write(bot_div_format.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:            
            st.write(user_input)
    
    
        
if __name__ == "__main__":
    app()