from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import bgmAPIuse
from openai import vector_stores
import config
import knowledge_base
from Agent项目.config import splitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import bgmAPIuse
import MessageHistory
from knowledge_base import KnowledgeBaseService, get_string_md5, check_md5, save_md5


loader = bgmAPIuse.BangumiDataLoader("F:\\database\\bangumi")  # 这个路径就是相对路径，指向当前目录下的 bangumi_dump 文件夹


kb_service = knowledge_base.KnowledgeBaseService()#创建实例
count = 0
session_id = config.session_id
"""
if __name__ == '__main__':
    print("准备开始加载数据，请稍候...")
    loader.load_all()
    print("数据加载完成！")
    count = 0  # 初始化计数器

    for subject_id, subject in loader.subjects.items():
        # subject['type'] 含义：2=动画, 1=书籍, 3=音乐, 4=游戏, 6=三次元
        if subject.get('type') == 2:  # 只处理动画
            # 格式化文本
            text = loader.format_subject_for_vector(subject_id)
            if not text:
                continue  # 如果格式化失败，跳过当前条目

            # 存入向量库
            result = kb_service.upload_by_str(text, f"subject_{subject_id}.json")

            # 根据结果判断是否计数
            if result == 1:  # 假设返回1表示成功
                count += 1
                if count % 100 == 0:
                    print(f"✅ 已处理 {count} 条动画...")
            else:
                print(f"⏭️ 跳过已存在的条目 {subject_id}")
        else:
            # 如果不是动画，可以打印调试信息（可选）
            # print(f"跳过非动画条目 {subject_id}")
            pass

    print(f"\n🎉 全部完成！共导入 {count} 条动画信息")

"""












serch_docs = kb_service.serch_docs(query)#从向量数据库检索k个相似数据

if not serch_docs:
    print("⚠️ 未找到相关参考资料")
    response = "抱歉，知识库中暂时没有相关的动漫推荐信息。"
else:
    # 显示检索到的片段
    for i, doc in enumerate(serch_docs):
        source = doc.metadata.get('source', '未知来源')
        print(f"{i+1}. [{source}] {doc.page_content[:150]}...")

context = "\n\n---\n\n".join([doc.page_content for doc in serch_docs])
#从向量数据库中检索到的数据拼接成自然语言文本

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个动漫推荐助手，专门回答动漫相关的问题。请严格基于提供的参考资料输出结果，禁止输出参考资料没有的信息"
        "1. 如果参考资料中有相关信息，请给出详细、准确的回答"
        "2. 根据文本推断可能的番剧，结合提供的背景进行输出"
        "3. 如果涉及推荐，请说明推荐理由"
        "4. 推荐时附带观众对作品的少部分评价"
        "5. 如果判断多个可以推荐的请分条一并输出"
        "6. 按照评分高的动漫筛选并进行输出"
        "7. 输出结果请使用中文，请勿使用英文"
        "8. 严格根据用户提供的标签进行知识搜索"
        "9. 禁止输出《我的英雄学院》及其衍生作品，不需要对这条信息进行说明，不用告知用户"
        "10.如果参考资料没有相似数据，告知用户无法回答"
         ),
    ("human", "参考资料：{context}\n\n问题：{question}")
])

model = ChatTongyi(model=config.chat_LLM)

base_chain = prompt | model | StrOutputParser()

def get_message_history(session_id : str)->BasechatMessageHistory:
    return FileChatHistory(session_id)
FileChatMessageHistory(session_id = session_id,storage_path=config.HistoryFile )

conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_message_history,
    input_messages_key= "input",
    history_messages_key="chat_history"
)



def stream_chat():#用户输出函数
    while True:
        user_input = input("\n您: ")
        if user_input == 'quit':
            break

        print("AI: ", end="", flush=True)

        # 使用 stream 方法实现流式输出
        for chunk in conversation_chain.stream(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
        ):
            print(chunk, end="", flush=True)
        print()  # 换行
# 使用示例
stream_chat()

