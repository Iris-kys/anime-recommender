from pprint import pformat
import requests
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from typing import Dict, List, Optional, Any
from collections import defaultdict
import os
"""
该模块的核心作用是从bangumi的本地文件夹获取数据并合并
"""
import json

class BangumiDataLoader:
    def __init__(self, data_dir: str):
        """
        初始化数据加载器

        参数:
            data_dir: 存放所有 .jsonlines 文件的目录
        """
        self.data_dir = data_dir

        # 存储所有数据的字典
        self.subjects = {}  # id -> 条目详情
        self.characters = {}  # id -> 角色详情
        self.persons = {}  # id -> 人员详情
        self.episodes = defaultdict(list)  # subject_id -> [单集列表]

        # 关联关系
        self.subject_characters = defaultdict(list)  # subject_id -> [角色信息(含角色详情)]
        self.subject_persons = defaultdict(list)  # subject_id -> [人员信息(含人员详情)]
        self.subject_relations = defaultdict(list)  # subject_id -> [关联条目]
        self.person_characters = defaultdict(list)  # person_id -> [配音角色]

    def load_all(self):
        """加载所有文件"""
        print("开始加载数据...")

        # 1. 先加载主表
        self._load_subjects()
        self._load_characters()
        self._load_persons()

        # 2. 加载关联表
        self._load_subject_characters()
        self._load_subject_persons()
        self._load_subject_relations()
        self._load_person_characters()

        # 3. 加载附属表
        self._load_episodes()

        print(f"✅ 加载完成！")
        print(f"   - 条目: {len(self.subjects)}")
        print(f"   - 角色: {len(self.characters)}")
        print(f"   - 人员: {len(self.persons)}")
        print(f"   - 单集: {sum(len(e) for e in self.episodes.values())}")

    def _load_subjects(self):
        """加载条目信息"""
        file_path = os.path.join(self.data_dir, 'subject.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                self.subjects[data['id']] = data
        print(f"📚 已加载 {len(self.subjects)} 个条目")

    def _load_characters(self):
        """加载角色信息"""
        file_path = os.path.join(self.data_dir, 'character.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                self.characters[data['id']] = data
        print(f"👤 已加载 {len(self.characters)} 个角色")

    def _load_persons(self):
        """加载人员信息"""
        file_path = os.path.join(self.data_dir, 'person.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                self.persons[data['id']] = data
        print(f"🎭 已加载 {len(self.persons)} 个人员")

    def _load_subject_characters(self):
        """加载条目-角色关联"""
        file_path = os.path.join(self.data_dir, 'subject-characters.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                rel = json.loads(line.strip())
                subject_id = rel['subject_id']
                character_id = rel['character_id']

                # 获取完整的角色信息
                character = self.characters.get(character_id, {})
                if character:
                    # 合并关联信息（如角色类型）
                    char_info = {
                        **character,
                        'role_type': rel.get('role_type', ''),
                        'role_name': rel.get('role_name', ''),
                    }
                    self.subject_characters[subject_id].append(char_info)

        total = sum(len(v) for v in self.subject_characters.values())
        print(f"🔗 已加载 {total} 个条目-角色关联")

    def _load_subject_persons(self):
        """加载条目-人员关联"""
        file_path = os.path.join(self.data_dir, 'subject-persons.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                rel = json.loads(line.strip())
                subject_id = rel['subject_id']
                person_id = rel['person_id']

                # 获取完整的人员信息
                person = self.persons.get(person_id, {})
                if person:
                    # 合并职位信息
                    person_info = {
                        **person,
                        'position': rel.get('position', ''),
                        'relation': rel.get('relation', ''),
                    }
                    self.subject_persons[subject_id].append(person_info)

        total = sum(len(v) for v in self.subject_persons.values())
        print(f"🔗 已加载 {total} 个条目-人员关联")

    def _load_subject_relations(self):
        """加载条目关系"""
        file_path = os.path.join(self.data_dir, 'subject-relations.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                rel = json.loads(line.strip())
                subject_id = rel['subject_id']
                self.subject_relations[subject_id].append(rel)

        total = sum(len(v) for v in self.subject_relations.values())
        print(f"🔄 已加载 {total} 个条目关系")

    def _load_person_characters(self):
        """加载人员-角色关联（声优配音角色）"""
        file_path = os.path.join(self.data_dir, 'person-characters.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                rel = json.loads(line.strip())
                person_id = rel['person_id']
                character_id = rel['character_id']

                character = self.characters.get(character_id, {})
                if character:
                    char_info = {
                        **character,
                        'subject_id': rel.get('subject_id'),  # 哪个作品里的这个角色
                    }
                    self.person_characters[person_id].append(char_info)

        total = sum(len(v) for v in self.person_characters.values())
        print(f"🎤 已加载 {total} 个人员-角色关联")

    def _load_episodes(self):
        """加载单集信息"""
        file_path = os.path.join(self.data_dir, 'episode.jsonlines')
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                ep = json.loads(line.strip())
                subject_id = ep['subject_id']
                self.episodes[subject_id].append(ep)

        total = sum(len(v) for v in self.episodes.values())
        print(f"📺 已加载 {total} 个单集")

    def get_complete_subject(self, subject_id: int) -> Optional[Dict]:
        """
        获取一个条目的完整信息（包含角色、人员、单集、关联条目）
        """
        subject = self.subjects.get(subject_id)
        if not subject:
            return None

        return {
            **subject,
            'characters': self.subject_characters.get(subject_id, []),
            'persons': self.subject_persons.get(subject_id, []),
            'episodes': self.episodes.get(subject_id, []),
            'relations': self.subject_relations.get(subject_id, []),
        }

    def format_subject_for_vector(self, subject_id: int) -> Optional[str]:
        """
        将条目的完整信息格式化为适合存入向量库的文本
        """
        subject = self.get_complete_subject(subject_id)
        if not subject:
            return None

        content_parts = []

        # 基本信息
        title = subject.get('name_cn') or subject.get('name', '未知标题')
        content_parts.append(f"【标题】{title}")

        # 简介
        summary = subject.get('summary', '')
        if summary:
            content_parts.append(f"【剧情简介】{summary}")

        # 标签
        tags = subject.get('tags', [])
        if tags:
            tag_names = [t.get('name') for t in tags if t.get('name')]
            content_parts.append(f"【作品标签】{'、'.join(tag_names[:20])}")

        # 评分
        rating = subject.get('rating', {})
        if rating.get('score'):
            content_parts.append(f"【用户评分】{rating['score']}分 (共{rating.get('total', 0)}人评价)")

        # 主要角色
        characters = subject.get('characters', [])
        if characters:
            char_list = []
            for c in characters[:8]:  # 取前8个主要角色
                char_name = c.get('name_cn') or c.get('name', '未知')
                role = c.get('role_name', '')
                if role:
                    char_list.append(f"{char_name}({role})")
                else:
                    char_list.append(char_name)
            content_parts.append(f"【主要角色】{'、'.join(char_list)}")

        # 主要制作人员
        persons = subject.get('persons', [])
        if persons:
            person_list = []
            for p in persons[:8]:  # 取前8个主要人员
                person_name = p.get('name_cn') or p.get('name', '未知')
                relation = p.get('relation', '制作人员')
                person_list.append(f"{person_name}({relation})")
            content_parts.append(f"【主要制作人员】{'、'.join(person_list)}")

        # 单集信息（只取前几集作为样例）
        episodes = subject.get('episodes', [])
        if episodes:
            ep_list = []
            for ep in episodes[:5]:  # 只显示前5集
                ep_list.append(f"第{ep.get('ep', '?')}集: {ep.get('name_cn') or ep.get('name', '')}")
            if ep_list:
                content_parts.append(f"【单集预览】{' | '.join(ep_list)}")

        return "\n\n".join(content_parts)






# 使用方法
