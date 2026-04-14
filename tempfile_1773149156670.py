from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import bgmAPIuse
from openai import vector_stores
import config
import knowledge_base
from Agent项目.config import splitter
from langchain_core.documents import Document

kb_service = knowledge_base.KnowledgeBaseService()#创建实例
Anime = [1,8]

def Get_Vector(Object):  # json 转 str
   bgmAPIuse.get_subject(Object)
   temp = bgmAPIuse.get_subject(Object)
   docs = knowledge_base.json_to_str(temp)
   return docs

# ... existing code ...

for i in Anime:
    docs = Get_Vector(i)
    # 生成 MD5 并检查是否已处理
    md5_hex = knowledge_base.get_string_md5(docs)

    if knowledge_base.check_md5(md5_hex):
       print(f"动漫 ID {i} 的数据已存在，跳过处理")
       continue

    print(f"正在处理动漫 ID {i} 的数据...")

    # 分割文档
    chunks = splitter.split_text(docs)

    # 创建 Document 对象列表
    documents = []
    for chunk in chunks:
       doc = Document(
            page_content=chunk,
           metadata={
                "source": f"bangumi_anime_{i}",
                "anime_id": str(i)
            }
        )
       documents.append(doc)

    # 添加到向量库
    kb_service.chroma.add_documents(
       documents=documents,
        ids=[f"anime_{i}_chunk_{idx}" for idx in range(len(documents))]
    )

    # 保存 MD5 记录
    knowledge_base.save_md5(md5_hex)
    print(f"动漫 ID {i} 的数据已成功添加到向量库")

query = "你推荐什么动漫" #用户提问
serch_docs = kb_service.chroma.similarity_search(query, k=2) #从向量数据库检索 k 个相似数据
