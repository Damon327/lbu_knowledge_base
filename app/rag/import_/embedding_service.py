#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：embedding_service.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 12:14 
"""
from app.process.import_.agent.state import ImportGraphState


def generate_chunk_embeddings(state: ImportGraphState) -> ImportGraphState:
    """
    向量化服务：
    1. 读取 chunks
    2. 生成 dense_vector / sparse_vector
    3. 将向量结果补充回 chunks
    """
    return state