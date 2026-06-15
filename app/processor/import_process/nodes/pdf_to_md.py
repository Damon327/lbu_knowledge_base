#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：pdf_to_md.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/13 13:31 
"""
import os
import subprocess
from pathlib import Path

from app.processor.import_process.base import BaseNode, T
from app.processor.import_process.exceptions import FileProcessingError, PdfConversionError
from app.processor.import_process.state import ImportGraphState


class PdfToMd(BaseNode):
    def process(self, state: ImportGraphState) -> ImportGraphState:

        #1、校验参数
        pdf_path_obj,file_dir_obj = self.execute_validate(state)

        #2、调用pdf解析库解析pdf文件
        process_code = self.execute_mineru(pdf_path_obj, file_dir_obj)

        #判断
        if process_code != 0:
            raise PdfConversionError("pdf解析失败")

        #返回md_path的路径
        md_path = self.get_md_path(file_dir_obj, file_dir_obj)

        #返回state
        state['md_path'] = md_path
        return state


    #判断文件路径是否存在
    def execute_validate(self, state):
        #1、验证pdf的路径
        pdf_path = state.get("pdf_path")
        pdf_path_obj = Path("pdf_path")

        if not pdf_path_obj.exists():
            raise FileProcessingError("pdf文件不存在")

        #2、验证pdf的目录
        file_dir = state.get("file_dir")
        if not file_dir:
            file_dir  = pdf_path_obj.parent
        file_dir_obj = Path(file_dir)

        return pdf_path_obj, file_dir_obj

    #调用pdf解析库解析pdf文件
    def execute_mineru(self, import_file_path, file_dir):
        self.log_step("开始解析pdf文件")

        # 命令行方式调用本地转换
        # 设置环境变量
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        os.environ["HF_HOME"]= r"D:\dev"
        os.environ["MODELSCOPE_CACHE"] = r"D:\dev"

        # 构建执行客户端命令
        # mineru
        # -p "D:\6W100-整本手册.pdf"
        # -o "D:\mineru"
        # --source local
        # --device cpu
        # --backend pipeline
        # --batch-size 1
        # --no-auto-download
        cmd = [
            "mineru","-p",
            str(import_file_path),
            "-o",str(file_dir),
            "--source","local"
            "--device","cpu",
            "--backend","pipeline",
            "--batch-size","1",
            "--no-auto-download"
        ]

        # 执行cmd构建命令，创建子进程执行
        proc = subprocess.Popen(
            args=cmd, # 执行命令构建列表
            stdout=subprocess.PIPE,  # 正常执行过程（日志）
            stderr=subprocess.STDOUT, # 错误信息
            errors="replace",  # ignore   replace
            text=True, # 文本形式
            bufsize=1
        )
        # 输出stdout=subprocess.PIPE,每行日志
        for line in proc.stdout:
            self.log_step(f"执行MinerU日志: {line}")

        # 等待子进程操作完成, 返回0成功
        process_code = proc.wait()
        if process_code == 0:
            self.logger.info("执行mineru成功了!!!")
        else:
            self.logger.error("执行mineru失败了...")
        return process_code


    def get_md_path(self, pdf_path_obj, file_dir_obj):
        file_name = pdf_path_obj.stem
        md_path_obj = file_dir_obj / file_name / "auto" / f"{file_name}.md"
        return str(md_path_obj)


if __name__ == '__main__':
    pass