import json
import  os
from langchain_core.chat_history import BaseChatMessageHistory
import config
from typing import Sequence, List, Iterator
from langchain_core.messages import BaseMessage,messages_from_dict,messages_to_dict

class FileChatHistory(BaseChatMessageHistory):
    """文件夹存储用户对话记录，重启不丢失"""

    def __int__(self,session_id:str,storage_path:str = config.HistoryFile):
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = f"{storage_path}/{session_id}.json"
        #初始化内容

        os.makedirs(storage_path,exist_ok = True)
        #self.messages = self._load_message()
        #从数据库恢复之前的消息
        print(f"已加载会话{session_id}的历史记录，共{len(self.messages)}条消息")


    def lazy_load_message(self) -> Iterator[BaseMessage]:
        try:
            with open(self.file_path,'r',encoding = "utf-8") as f:
                for line in f:
                    line = line.strip()#删除不必要字符
                    if not line:
                        continue
                    data = json.loads(line)
                    # JSON → Python 类型转换规则：
                    # JSON对象 {}  → Python字典(dict)
                    # JSON数组 []  → Python列表(list)
                    # JSON字符串   → Python字符串(str)
                    # JSON数字     → Python整数(int)或浮点数(float)
                    # JSON true    → Python True
                    # JSON false   → Python False
                    # JSON null    → Python None

                    # messages_from_dict 期望的是列表，但这里 data 是单条消息的字典
                    # 需要将单条消息转换为 BaseMessage 对象
                    msg_list = messages_from_dict([data])
                    yield msg_list[0]
                    #用 messages_from_dict([data]) 得到列表，再取第一个


        except FileNotFoundError:
            return #文件不存在，返回空迭代器
        except json.JSONDecodeError:
            return #如果损坏科研选择跳过或者终止

    def append_message(self,message:BaseMessage):
        """追加一条消息到文件(JSONL格式)"""
        #把单条消息转化成可序列化的字典
        # message_to_dict 函数会返回一个字典，包含消息的属性，如 role, content, name 等
        data = message_to_dict([message])[0]
        with open(self.file_path,'a',encoding = 'utf-8') as f:
            f.write(json.dumps(data,ensure_ascii = False) + '\n')

    def clear_message(self):
        """清空文件"""
        self.messages = []
        with open(self.file_path,'w',encoding = 'utf-8') as f:
            f.write('')

        #用w方式覆盖文件，实现清空历史的功能
        print("消息已被清空")
    def has_history(self) -> bool:
        """检查是否有历史记录"""
        if os.path.exists(self.file_path):
            return True
        if os.path.getsize(self.file_path) == 0:
            #检查文件是否为空
            return False
        return  True



