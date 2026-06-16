#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：vector_search_node.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/15 15:54 
"""
from typer.cli import state

from app.processor.query_process.base import BaseNode, T
from app.processor.query_process.state import QueryGraphState


class VectorSearchNode(BaseNode):
    def process(self, state: QueryGraphState) -> QueryGraphState:
        # 1、参数校验，获取item_name，重写的问题
        item_name,rewritten_query = self.validate_param(state)

        # 2、对重写的问题进行向量化

        #3、构建item_name标量字段条件
        # item_name in ["xxx", "yyy"]

        #4、对item_name向量化

        #5、执行混合检索

        return state

    def validate_param(self, state):
        pass














