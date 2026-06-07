#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：split_document.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 12:00 
"""
from app.process.import_.agent.state import ImportGraphState


def split_document(state: ImportGraphState) -> ImportGraphState:
    """
    文档切分服务：
    1. 按标题层级做一级粗切
    2. 对超长文本做二次细切
    3. 构造 chunks 列表
    4. 回写 chunks
    """
    return state