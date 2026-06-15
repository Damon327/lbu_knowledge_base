#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：chunks_embedding_node.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/15 14:01 
"""
from app.processor.import_process.base import BaseNode, T
from app.processor.import_process.state import ImportGraphState


class ChunksEmbeddingNode(BaseNode):
    def process(self, state: ImportGraphState) -> ImportGraphState:
        #1、参数校验，state里面chunks列表不能为空

        #2、chunks内容进行嵌入，转换稠密和稀疏向量
        #批量嵌入，每3段嵌入一次


        #3、更新数据


        return state