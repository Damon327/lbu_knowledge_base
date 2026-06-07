#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：entry_service.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 11:57 
"""
from pathlib import Path

from app.process.import_.agent.state import ImportGraphState
from app.shared.runtime.logger import logger

def resolve_input_file(state: ImportGraphState) -> ImportGraphState:
    """
    入口识别服务：
    1. 校验 local_file_path
    2. 识别文件类型（PDF / Markdown）
    3. 回写 is_pdf_read_enabled / is_md_read_enabled
    4. 回写 pdf_path / md_path / file_title
    """
    #获取state的local_file_path
    local_file_path = state.get("local_file_path")

    #非空校验,如果是空文件，直接抛出异常
    if not local_file_path:
        logger.error(f"{local_file_path}为空，无法继续业务")
        raise FileNotFoundError(f"{local_file_path}为空，无法继续业务")

    #判断
    if local_file_path.endswith(".md"):
        #改写状态
        state['is_md_read_enabled'] = True
        state['md_path'] = local_file_path
    elif local_file_path.endswith(".pdf"):
        #改写状态
        state['is_pdf_read_enabled'] = True
        state['pdf_path'] = True
    else:
        logger.info(f"{local_file_path}既不是md文件也不是pdf文件，暂无法处理")
        return state

    #统一修改file_title
    state['file_title'] = Path(local_file_path).stem     #  xxxx
    #state['file_title'] = Path(local_file_path).name    xxxx.md
    #state['file_title'] = Path(local_file_path).suffix  .md

    return state