#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：state.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/1 14:22

    第一步是完成state.py
    state是langgraph的状态，最重要的概念之一，数据护照;
    State（状态）就是整个系统的共享内存。它贯穿了从文件上传、解析、切块到向量入库的全生命周期。


    state定义了在langgraph的工作流中，所有的数据长什么样子，以及包含了什么信息
        就像在厨房处理一条鱼，要经过很多道工序，每道工序这条鱼的状态也不一样。刚开始没洗，然后洗完了，切块，烹饪等等...

---------------------------------------------------------------------------------------------------------

企业开发中生产场景：
想象一下，你的系统正在高并发处理 1000 个 PDF 上传请求。
    场景 A（你的写法）： 如果某个节点只是想把新的切片追加到 chunks 里，
                        但因为你没配置 Reducer，直接把之前的切片全覆盖了，导致最后存入数据库的内容残缺不全。

    场景 B（企业规范）： 引入 LangGraph 的 Annotated 和 reducer。
                        当节点返回 {"chunks": [new_chunk]} 时，框架会自动将其合并到现有的列表中，保证数据的完整性和线程安全。

---------------------------------------------------------------------------------------------------------

面试场景题：
    面试题 1： “在 LangGraph 中，如果一个节点返回了 {'count': 5}，而当前 State 中 count 已经是 10 了，会发生什么？如果你想让两个节点的输出累加而不是覆盖，应该怎么做？”

    满分回答思路： 默认情况下，LangGraph 会使用 LastValue 策略，即新值 5 会直接覆盖旧值 10。
    如果想要累加（例如记录日志或收集切片），需要在定义 State 时，使用 typing_extensions.Annotated 配合 operator.add
    或自定义的 reducer 函数。例如：chunks: Annotated[list, operator.add]。



    面试题 2： “为什么在定义 LangGraph 的 State 时，推荐使用 Pydantic BaseModel 而不是 TypedDict？”

    满分回答思路： 虽然 TypedDict 够用，但 Pydantic 提供了强大的运行时数据验证能力。
    在企业级应用中，确保流入工作流的数据格式绝对正确至关重要（比如校验 task_id 是否符合 UUID 规范）。
    Pydantic 可以在数据进入 State 的第一时间拦截非法数据，防止脏数据污染整个下游流程。

"""
import copy
import json
from copy import deepcopy
from typing import TypedDict

from app.shared.runtime.logger import logger


class ImportGraphState(TypedDict):

    #任务状态追踪
    task_id: str #流程的身份标识

    #文件状态判断
    is_md_read_enabled: bool #标记，给路由函数决定下一跳
    is_pdf_read_enabled: bool  #标记，给路由函数决定下一跳

    #地址路径内容
    local_file_path: str #存储要解析文件的地址 pdf md   -》原始食材放在哪里（原始的pdf路径）
    local_dir: str #存储生成的md的文件  pdf -> md
    md_path: str  #专门存储md地址 =》 半成品放在哪里（转成md文件路径）-》告诉下游 markdown 文件在哪里
    pdf_path: str #专门存储pdf地址，原件备份路径， -〉PDF 解析入口文件
    file_title: str #菜名：文件名是什么？   xxx.pdf

    #文本和切块
    md_content: str #读取md的内容,用于切片
    item_name: str # 模型识别的一个文档对应的主体
    chunks: str ## 存储切块内容 切好的小段。此处有疑问为何不用Annotated[List[str],operator.add]  - reducer规约期
    #    chunks: Annotated[List[str], operator.add]


    #---数据库相关---
    embeddings_content: list # 存储带有向量的切块内容

# 每当有一个新任务开始，比如用户上传了一个新的PDF，我们就拿一个新的state来装数据
default_state: ImportGraphState = {
    "task_id": "",
    "is_pdf_read_enabled": False,
    "is_md_read_enabled": False,
    "local_dir":"",
    "local_file_path": "",
    "pdf_path": "",
    "md_path": "",
    "file_title": "",
    "md_content": "",
    "chunks": [],
    "item_name": "",
    "embeddings_content": [],
}


# 在企业级开发中，通常不需要手动封装 create_default_state。
# 初始化状态直接在调用 graph.invoke(initial_state) 时传入字典即可。
# 这样既减少了冗余代码，也避免了深拷贝带来的性能损耗。
def create_default_state(**overrides) -> ImportGraphState:
    """
    创建默认状态，支持覆盖
    """
    copy_state = copy.deepcopy(default_state)
    copy_state.update(overrides)
    return copy_state

#返回一个全新的state，避免污染全局
def get_default_state() -> ImportGraphState:
    return copy.deepcopy(default_state)

if __name__ == '__main__':
    state_new = create_default_state(task_id="task001")
    logger.info(f"测试复制方法：\n{json.dumps(state_new, ensure_ascii= False,indent=4)}")

    state_new1 = get_default_state()
    logger.info(f"测试复制方法：\n{json.dumps(state_new1, ensure_ascii=False, indent=4)}")

"""
    json.dumps : python对象 转为字符串 s=string 变成字符串
    json.dump： python对象 转为 文件存在硬盘 不带s，成文件
    
    json.loads： 把字符串转为json
    json.load ： 把文件转为json
    
    把字典变成字符串打印，你就用过json.dumps
    把字典变成文件.json ，就用json.dump

"""























