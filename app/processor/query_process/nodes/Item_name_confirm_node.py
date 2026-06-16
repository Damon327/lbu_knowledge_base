#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：Item_name_confirm_node.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/15 15:01 
"""
from app.processor.query_process.base import BaseNode, T
from app.processor.query_process.state import QueryGraphState


class ItemNameConfirmNode(BaseNode):



    def process(self, state: QueryGraphState) -> QueryGraphState:
        #1、获取原始问题

        #2、获取用户上下文
            #调用工具类方法，根据session_id获取最近10条会话记录，mangodb的工具类
            #把查询的历史会话列表拼接成字符串


        #3、根据用的问题，+ 上下文会话去调用大模型，提取商品的名称，约定好格式，json格式

        #4、根据商品名称查询向量数据库，得到稠密和稀疏向量
            #对 稠密和稀疏向量 的数据进行 评分对齐 ，返回两个列表
                #第一个列表confirmed：大于0.7的就放在confirmed里面
                #第二个列表options：再0.6和0.7之间的就放在options里面
            #返回

        #5、根据评分对齐的结果，进行更新state
                #判断 存在confirmed列表，则直接返回,否则options则给用户选，什么都没有，就提示当前问题无法识别


        return state
















