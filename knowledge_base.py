import os.path
from datetime import datetime
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
import config
import hashlib
import  json


#此模块提供md5功能，避免重复处理
#json转str str再转成md5
#以及添加进向量数据库
def check_md5(md5_str: str):
    """检查传入的md5字符串是否已经被处理过了
        return False(md5未处理过)  True(已经处理过，已有记录）
    """
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    #如果目标文件夹不存在则新建并创建
    # if进入表示文件不存在，那肯定没有处理过这个md5了

    else:
        for line in open(config.md5_path, 'r', encoding='utf-8'):
            line = line.strip() #line.strip() 的作用是移除字符串开头和结尾的空白字符（包括空格、制表符 \t、换行符 \n、回车符 \r 等）。
            if line == md5_str:
                return True
            # 遍历文件中的每一行，并判断是否与传入的md5字符串相等
        return   False

def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str + '\n')


def get_string_md5(input_str: str, encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""
    # 将字符串转换为字节数组
    str_bytes = input_str.encode(encoding=encoding)
    # 创建md5对象
    md5_obj = hashlib.md5()
    # 更新内容（传入即将要转换的字节数组）
    md5_obj.update(str_bytes)
    # 获取md5的十六进制字符串
    md5_hex = md5_obj.hexdigest()

    return md5_hex

def json_to_str(json_data, ensure_ascii=False, sort_keys=True):
    # 1. 将 JSON 对象转换成规范的字符串
    # sort_keys=True 保证键的顺序一致，避免 {'a':1,'b':2} 和 {'b':2,'a':1} 生成不同的 MD5
    json_str = json.dumps(
        json_data,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        separators=(',', ':')  # 去除多余空格，让字符串更紧凑
    )
    return json_str


class KnowledgeBaseService(object):


    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,     # 数据库的表名
            embedding_function=DashScopeEmbeddings(model=config.embedding_LLM),
            persist_directory=config.persist_directory,     # 数据库本地存储文件夹
        )     # 向量存储的实例 Chroma向量库对象

        self.spliter = config.splitter


    def upload_by_str(self, data: str,file):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            print("⚠️  已处理过该数据")
            return 0
        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
            print("添加成功")
        else:
            knowledge_chunks = [data]
            print("添加成功")

        metadata = {
            "operator": "Iris",
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas = [metadata for _ in knowledge_chunks]
        )
        save_md5(md5_hex)
        return 1


    def serch_docs(self, query):#检索向量数据库
        serch_result = self.chroma.similarity_search(query, k=config.k_number)
        return  serch_result



