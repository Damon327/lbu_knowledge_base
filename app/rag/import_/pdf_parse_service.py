#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：pdf_parse_service.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 11:58 
"""
from pathlib import Path
from typing import Tuple

from app.process.import_.agent.state import ImportGraphState
from app.shared.runtime.logger import logger, PROJECT_ROOT


def step1_validate_paths(state) -> Tuple[Path,Path]:
    #1 获取pdf_path local_dir
    pdf_path = state.get("pdf_path")
    local_dir = state.get("local_dir")

    #2 进行校验
    if not pdf_path:
        logger.error(f"{pdf_path}为空，无法获取pdf文件，无法继续业务")
        raise ValueError(f"{pdf_path}为空，无法获取pdf文件，无法继续业务")

    if not local_dir:
        logger.warning(f"{local_dir}为空，创建默认文件夹")
        #怎创建
        local_dir = PROJECT_ROOT / "output"
    #3 转Path
    pdf_path_obj = Path(pdf_path)
    local_dir_obj = Path(local_dir)

    #4 再次校验是否真实存在
    if not pdf_path_obj.exists():
        logger.error(f"{pdf_path}不存在对应的文件,业务无法继续!!")
        raise FileNotFoundError(f"{pdf_path}不存在对应的文件,业务无法继续!!")

    # 再次校验
    if not local_dir_obj.exists():
        logger.warning(f"进行pdf转化md,local_dir值:{local_dir_obj},但是没有对应文件夹! 我们自行创建!!")
        # parents 自动创建多层文件夹  例如: x/x/x/x  -> True会自动创建 x  x   x  x
        # exist_ok = True 当存在的时候不会创建也不会报错!
        local_dir_obj.mkdir(parents=True, exist_ok=True)

    #5 返回
    return pdf_path_obj,local_dir_obj


def step2_upload_and_poll(pdf_path_obj):
    # upload_pdf_and_poll(pdf_path_obj: Path) -> str
    #        1. 校验 MinerU 配置是否完整
    #        2. 调用 `/file-urls/batch` 申请上传地址与 `batch_id`
    #        3. 使用 `Session(trust_env=False)` 上传 PDF 文件
    #        4. 根据 `batch_id` 轮询任务状态
    #        5. 若任务成功，返回 `full_zip_url`
    #        6. 若任务失败或超时，抛出异常

    pass


def step3_download_and_extract(zip_url, local_dir_obj, pdf_path_obj):
    pass


def parse_pdf_to_markdown(state: ImportGraphState) -> ImportGraphState:
    """
    PDF 解析服务：
    1. 调用 MinerU
    2. 下载并解压解析结果
    3. 获取 Markdown 路径和正文内容
    4. 回写 md_path / md_content / local_dir
    """

    #校验pdf和输出地址
    pdf_path_obj,local_dir_obj = step1_validate_paths(state)
    
    #上传文件
    zip_url = step2_upload_and_poll(pdf_path_obj)
    
    #下载文件和解压
    md_path_obj = step3_download_and_extract(zip_url, local_dir_obj, pdf_path_obj)

    return state