#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：pdf_parse_service.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 11:58 
"""
from app.process.import_.agent.state import ImportGraphState


def parse_pdf_to_markdown(state: ImportGraphState) -> ImportGraphState:
    """
    PDF 解析服务：
    1. 调用 MinerU
    2. 下载并解压解析结果
    3. 获取 Markdown 路径和正文内容
    4. 回写 md_path / md_content / local_dir
    """
    return state