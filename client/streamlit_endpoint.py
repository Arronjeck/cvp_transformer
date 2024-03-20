import time
import requests
import streamlit as st

def app():
    # 初始化
    # session_state是Streamlit提供的用于存储会话状态的功能
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.set_page_config(page_title="企业级通用知识库", page_icon=":robot:")    
    st.header("企业级通用知识库")
    # 1. 提供用户输入文本框
    user_input = st.text_input("请输入你的提问: ")
    # 处理用户输入，并返回响应结果
    if user_input:
        #process_user_input(user_input)
        st.write(user_input)
    
    with st.sidebar:
        # 2. 设置子标题
        st.subheader("File Uploader")
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
                    # 延迟10秒
                    time.sleep(10)
                    # 调用https GET方法
                    response = requests.get(f"http://127.0.0.1:8501/search?query={user_input}")
                    st.write(response.text)
                    
                    # 4. 获取文档内容（文本）
                    # texts = extract_text_from_PDF(files)
                    # 5. 将获取到的文档内容进行切分
                    # content_chunks = split_content_into_chunks(texts)
                    # 6. 向量化并且存储数据
                    # embedding_model = get_openaiEmbedding_model()
                    # vector_store = save_chunks_into_vectorstore(content_chunks, embedding_model)
                    # 7. 创建对话chain
                    # st.session_state.conversation = get_chat_chain(vector_store)
                    pass
        
if __name__ == "__main__":
    app()