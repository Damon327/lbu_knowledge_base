#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：main_graph.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/2 21:58 
"""
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from app.process.import_.agent.state import ImportGraphState
from app.process.import_.agent.nodes.node_entry import node_entry
from app.process.import_.agent.nodes.node_pdf_to_md import node_pdf_to_md
from app.process.import_.agent.nodes.node_md_img import node_md_img
from app.process.import_.agent.nodes.node_document_split import node_document_split
from app.process.import_.agent.nodes.node_item_name_recognition import node_item_name_recognition
from app.process.import_.agent.nodes.node_bge_embedding import node_bge_embedding
from app.process.import_.agent.nodes.node_import_milvus import node_import_milvus

# 读取配置文件
load_dotenv()

# 构建builder
workflow = StateGraph(ImportGraphState)

# 添加节点
workflow.add_node("node_entry", node_entry)
workflow.add_node("node_pdf_to_md", node_pdf_to_md)
workflow.add_node("node_md_img", node_md_img)
workflow.add_node("node_document_split", node_document_split)
workflow.add_node("node_item_name_recognition", node_item_name_recognition)
workflow.add_node("node_bge_embedding", node_bge_embedding)
workflow.add_node("node_import_milvus", node_import_milvus)

# 添加边
workflow.set_entry_point("node_entry")


# 添加条件边，提供条件边函数
def condition_entry_to_pdf_to_md(state: ImportGraphState):
    if state.get("is_pdf_read_enabled"):
        return "node_pdf_to_md"
    elif state.get("is_md_read_enabled"):
        return "node_md_img"
    else:
        return END


workflow.add_conditional_edges(
    "node_entry",
    condition_entry_to_pdf_to_md,
    {
        "node_pdf_to_md": "node_pdf_to_md",
        "node_md_img": "node_md_img",
        END: END
    }
)

# 添加剩余的边

workflow.add_edge("node_pdf_to_md", "node_md_img")
workflow.add_edge("node_md_img", "node_document_split")
workflow.add_edge("node_document_split", "node_item_name_recognition")
workflow.add_edge("node_item_name_recognition", "node_bge_embedding")
workflow.add_edge("node_bge_embedding", "node_import_milvus")

# 5. 编译图对象
kb_import_app = workflow.compile()

if __name__ == '__main__':
    from app.shared.utils.path_util import PROJECT_ROOT
    import os
    from app.shared.runtime.logger import logger

    # 全流程测试：验证PDF导入→Milvus入库完整链路
    logger.info("===== 开始执行知识图谱导入全流程测试 =====")

    # 1. 构造测试文件路径（复用你项目的doc目录）
    test_pdf_name = os.path.join("doc", "hak180产品安全手册.pdf")
    test_pdf_path = os.path.join(PROJECT_ROOT, test_pdf_name)

    # 2. 构造输出目录（存放MD/图片等中间文件）
    test_output_dir = os.path.join(PROJECT_ROOT, "output")
    os.makedirs(test_output_dir, exist_ok=True)  # 不存在则创建

    # 3. 校验测试PDF文件是否存在
    if not os.path.exists(test_pdf_path):
        logger.error(f"全流程测试失败：测试PDF文件不存在，路径：{test_pdf_path}")
        logger.info("请检查文件路径，或手动将测试文件放入项目根目录的doc文件夹中")
    else:
        # 4. 构造测试状态（贴合实际业务入参，开启PDF解析开关）
        test_state = ImportGraphState({
            "task_id": "test_kg_import_workflow_001",  # 测试任务ID
            "local_file_path": test_pdf_path,  # 测试PDF文件路径
            "local_dir": test_output_dir,  # 中间文件输出目录
            "is_pdf_read_enabled": False,  # 开启PDF解析（核心开关）
            "is_md_read_enabled": False  # 关闭MD解析
        })
        try:
            logger.info(f"测试任务启动，PDF文件路径：{test_pdf_path}")
            logger.info(f"中间文件输出目录：{test_output_dir}")
            logger.info("开始执行全流程节点，依次执行：entry→pdf2md→md_img→split→item_name→embedding→milvus")

            # 5. 执行LangGraph全流程（流式执行，打印节点执行进度）
            final_state = kb_import_app.invoke(test_state)

            # 6. 全流程执行完成，结果预览和核心指标打印
            if final_state:
                logger.info(f"最终结果: {final_state}")
        except Exception as e:
            logger.exception(f"===== 全流程测试运行失败 =====")
    logger.info("===== 知识图谱导入全流程测试结束 =====")
