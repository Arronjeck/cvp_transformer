# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.vectorstores import VectorStoreRetriever
from .chatglm3_model import ChatGLM36B

def get_llm_model(model_name):
    if model_name == "chatglm3":
        return ChatGLM36B(model_name="/root/autodl-tmp/model/chatglm3-6b")
    elif model_name == "openai":
        return ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo")
    else:
        return ChatOpenAI(model_name=model_name)

# 一次对话的chain（可扩展为任意工作内容的chain）
def get_chat_chain(vector_retriever : VectorStoreRetriever):
    # 创建对话链chain LCEL
    return ConversationalRetrievalChain.from_llm(
        llm=get_llm_model("chatglm3"), # chat 模型
        retriever=vector_retriever,
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True) # 用于缓存或者保存对话历史记录的对象
    )