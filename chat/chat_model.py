# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.vectorstores import VectorStoreRetriever

# 一次对话的chain（可扩展为任意工作内容的chain）
def get_chat_chain(vector_retriever : VectorStoreRetriever):
    # 创建对话链chain LCEL
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo"), # chat 模型
        retriever=vector_retriever,
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True) # 用于缓存或者保存对话历史记录的对象
    )