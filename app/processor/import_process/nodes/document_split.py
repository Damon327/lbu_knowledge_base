#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：document_split.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/15 14:18 
"""
from app.processor.import_process.base import BaseNode
from app.processor.import_process.state import ImportGraphState


class DocumentSplit(BaseNode):
    def process(self,state:ImportGraphState) -> ImportGraphState:
        #1、获取参数，格式化标准




        """
        2、根据标题切分
        [{body:111,title:第一章}，{body:666,title:第2章}]

        3、对根据标题切分内容再处理
            #原则：如果每段的内容过长在进行切分
            1、如果内容内容 > 1000，用递归切分器切分 \n,\n\n,逗号，句号，感叹号
            2、如果内容内容 < 1000，直接返回

            同一个标题，
            3、如果每段内容太小，阈值每段最小是500，多个段内容合并，






        """


        return state