import json
from pathlib import Path

from app.processor.import_process.base import BaseNode, T, setup_logging
from app.processor.import_process.state import ImportGraphState


class EntryNode(BaseNode):

    def process(self, state: ImportGraphState) -> ImportGraphState:

        #打印日志
        self.log_step("步骤一","[检查文件类型]")

        #1、获取参数
        import_file_path = state.get("import_file_path")
        file_dir = state.get("file_dir")

        #2、判断文件后缀
        #2.1先转Path对象，方便拿后缀名
        import_file_path_obj = Path(import_file_path)

        if import_file_path_obj.suffix.lower() == ".pdf":
            self.log_step("pdf","[文件类型为pdf]")
            state["is_pdf_read_enabled"] = True
        elif import_file_path_obj.suffix.lower() == ".md":
            self.log_step("md","[文件类型为md]")
            state["is_md_read_enabled"] = True
        else:
            self.log_step("error","[文件类型错误]")


        #获取file_title
        state['file_title']  = import_file_path_obj.stem

        #3、返回state
        return state

if __name__ == '__main__':

    #日志初始化
    setup_logging()

    #构建字典数据
    entry_state={
        "file_dir": r"/Users/damon/PycharmProjects/lbu_knowledge_base/app/processor/import_process/import_temp_dir",
        "import_file_path": r"/Users/damon/PycharmProjects/lbu_knowledge_base/app/processor/import_process/import_temp_dir/hak180产品安全手册.pdf"
    }

    #EntryNode实例化
    entry_node = EntryNode()

    res = entry_node(entry_state)
    print(res)

    print(json.dumps(res,ensure_ascii=False,indent=4))








