#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：mutli_search_rerank.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/16 21:00 
"""
from app.processor.query_process.base import BaseNode
from app.processor.query_process.state import QueryGraphState


class MultiSearchRerankNode(BaseNode):
    def process(self, state: QueryGraphState) -> QueryGraphState:
        #1、获取输入问题

        #2、获取融合数据，合并在一起
        #web搜索数据 + rrf融合数据

        #3、把输入数据 + 数据 传递Rerank模型，进行精排处理
        # 和输入问题语义相似度降序排列之后的列表


        #4、断崖式检测

        #5、更新state返回
        return state