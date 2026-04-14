from langchain_text_splitters import RecursiveCharacterTextSplitter


persist_directory="./Anime_chroma_db"#向量库数据保存位置
md5_path="./Anime_md5.text"#md5保存位置
collection_name = "Bangumi_Anime" #数据库表名
max_split_char_number = 100 #最长分割长度
embedding_LLM = "text-embedding-v3"#向量模型
chat_LLM = "qwen3-max"#聊天模型
k_number = 4 #搜索数量
HistoryFile = "./Chat_History"
session_id = "user123"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,    #截取长度
    chunk_overlap=50, #重叠文本数
    length_function=len, #使用Python自带的len函数做长度统计的依据
    separators=["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
)
# 分词器
