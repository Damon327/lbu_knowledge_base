#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：01_env_test.py.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/5/29 20:22 
"""

import os
from dotenv import load_dotenv

load_dotenv(
    override=True
)

print(os.environ.get("BGE_M3_PATH"))
# load_dotenv(override=True) → 输出 dotenv_val（.env覆盖系统）






